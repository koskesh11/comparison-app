"""Run every enumerable guide difference against the player's live PoB setup."""

from __future__ import annotations

import copy
import json
import logging
import re
import time

import guide_lua
from api_errors import ApiError
from display import fmt_pct
from guide_check_avail import row_availability
from guide_check_eval import evaluate_options, lua_mb, models_not_applied, named_models
from guide_check_log import log_check
from guide_check_rank import rank_rows
from guide_check_result import assemble_row, build_result, carries_value, kpis
from guide_check_retest import evaluate_config, retest_zero_rows
from guide_check_why import breakdown, explain_row
from guide_diff import diff, tree_candidates
from guide_interactions import load_named_gap_patterns, interaction_for, vault_note_status
from pobhost import LuaError


class GuideLoadError(ApiError):
    status = 400
    kind = "InvalidRequest"


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _first_line(error: Exception) -> str:
    line = next((line.strip() for line in str(error).splitlines() if line.strip()),
                type(error).__name__)
    return re.sub(r"^.*?\.lua:\d+:\s*", "", line)


def _not_tested(row: dict, reason: str | None = None) -> dict:
    result = {**copy.deepcopy(row), "reason": reason or row.get("reason") or "Not testable",
              "chips": ["not tested"], "rank": None, "result": None}
    if MAGEBLOOD_NOTE in result["reason"]:
        result["vaultRefs"] = sorted({*result.get("vaultRefs", []), MAGEBLOOD_NOTE})
    return result


def _probe(engine) -> None:
    result = guide_lua.probe(engine)
    missing = [key for key in ("compareTab", "comparePowerBuilder", "compareEntry") if not result.get(key)]
    if missing:
        raise RuntimeError("Path of Building guide comparison is unavailable: " + ", ".join(missing))


def _load_pair(auditor, guide_path, guide_label: str) -> tuple[dict, dict, dict, list[dict], float, str | None]:
    engine = auditor.engine
    player = guide_lua.snapshot(engine, "player")
    node_power, node_error = [], None
    try:
        loaded = guide_lua.load_guide(engine, guide_path, guide_label)
        if not loaded.get("ok"):
            raise GuideLoadError("Couldn't read that build.")
        guide = guide_lua.snapshot(engine, "guide")
        candidates = tree_candidates(player, guide)
        info = guide_lua.tree_info(engine, candidates["ids"], candidates["removeIds"])
        differences = diff(player, guide, info)
        if any(row.get("category") == "tree-add" for row in differences["rows"]):
            try:
                node_power = guide_lua.guide_power(engine, ["treeNodes"])
            except Exception as error:
                node_error = "unavailable: " + _first_line(error)
                logging.exception("guide node-alone comparison failed")
        memory = lua_mb(engine)
        return player, guide, differences, node_power, memory, node_error
    finally:
        guide_lua.release_guide(engine)


def _items(snapshot: dict) -> dict[str, dict]:
    return {str(item.get("slot")): item for item in snapshot.get("items") or []}


def _node_alone(row: dict, powers: list[dict]) -> dict | None:
    info = row.get("info") or {}
    if row.get("category") != "tree-add" or (info.get("pathNodes") or 0) <= 0:
        return None
    ident = info.get("node") or (row.get("change") or {}).get("target")
    match = next((value for value in powers if value.get("nodeId") == ident), None)
    if not match:
        return None
    value = {"dpsPct": match.get("impactPercent") or 0,
             "pathDist": match.get("pathDist"), "source": "PoB Compare tab"}
    shown = ((row.get("result") or {}).get("delta") or {}).get("dpsPct")
    return value if fmt_pct(value["dpsPct"]) != fmt_pct(shown) else None


def _chosen_row(row: dict, change: dict) -> dict:
    result = copy.deepcopy(row)
    options = (row.get("info") or {}).get("options") or []
    if len(options) <= 1:
        result["change"] = change
        return result
    names = [str(value.get("replaced")) for value in options]
    added = (change.get("gem") or {}).get("name") or "support"
    label = str(row.get("label") or "")
    suffix = label[label.find(' in "'):] if ' in "' in label else ""
    result["label"] = f"Replace {change.get('replaced')} with {added}{suffix}"
    result["detail"] = f"Tested replacing each of: {', '.join(names)}; the best is shown."
    result["info"] = {**(result.get("info") or {}), "tested": len(options)}
    result["change"] = change
    return result


def _tested_row(auditor, row: dict, base_ctx: dict, player: dict, guide: dict,
                powers: list[dict], statuses: dict, gaps: list[dict]) -> dict:
    ctx, change = evaluate_options(auditor, row, base_ctx)
    row = _chosen_row(row, change)
    result, dims, breaks = build_result(auditor, base_ctx, ctx)
    availability = row_availability(auditor.obtainable, row)
    slot = (row.get("info") or {}).get("slot") or change.get("slot")
    player_item, guide_item = _items(player).get(str(slot)), _items(guide).get(str(slot))
    interaction = interaction_for(row, named_models(auditor, ctx), guide_item, player_item,
                                  gaps, statuses)
    values = breakdown(auditor, base_ctx, ctx)
    built = assemble_row(row, result, dims, breaks, availability, interaction, values, statuses,
                         auditor.obtainable.league, auditor.obtainable.cache_date)
    built["nodeAlone"] = _node_alone(built, powers)
    return built


def _state_unchanged(auditor, base_ctx: dict, before: dict) -> None:
    current = auditor.base_context()
    dims = auditor.dimensions(current, base_ctx)
    values = [dims.get("dps"), dims.get("ehp"), dims.get("physMaxHit"),
              (dims.get("manaTo") or 0) - (dims.get("manaFrom") or 0)]
    snapshot = guide_lua.snapshot(auditor.engine, "player")
    if any((value or 0) != 0 for value in values) or _canonical(snapshot) != _canonical(before):
        raise RuntimeError("player state changed during the check")


def _header(auditor, player: dict, guide: dict, label: str, banners: list[dict]) -> dict:
    player_class = player.get("ascendancy") or player.get("className")
    guide_class = guide.get("ascendancy") or guide.get("className")
    return {"playerName": player.get("label"), "guideName": label,
            "playerClass": player_class, "guideClass": guide_class,
            "playerMainSkill": player.get("mainSkill"), "guideMainSkill": guide.get("mainSkill"),
            "pobVersion": player.get("pobVersion"), "league": auditor.obtainable.league,
            "leagueDate": auditor.obtainable.cache_date, "points": player.get("points") or {},
            "scenario": auditor.scenario, "leaveOut": list(auditor.disabled_skills),
            "dpsStat": auditor.dps_key, "skippedDrafts": list(auditor.skipped),
            "sets": {"player": player.get("sets") or {}, "guide": guide.get("sets") or {}},
            "banners": banners}


def _test_rows(state: dict) -> None:
    progress = state["progress"]
    tester = getattr(progress, "testing", None)
    if callable(tester):
        tester(0, state["total"])
    for row in state["initial_not_tested"]:
        state["not_tested"].append(_not_tested(row))
        state["done"] += 1
        if callable(tester):
            tester(state["done"], state["total"])
    for row in state["rows"]:
        _test_one(state, row)
        if callable(tester):
            tester(state["done"], state["total"])


def _test_one(state: dict, row: dict) -> None:
    state["done"] += 1
    reason = (_granted_group_reason(row, state["player"]) or _alternate_set_reason(row)
              or _mageblood_reason(row, state["player"]))
    if reason:
        state["not_tested"].append(_not_tested(row, reason))
        return
    elapsed = state["clock"]() - state["start"]
    if state["limited"] or elapsed >= state["deadline"]:
        state["limited"] = True
        reason = f"Stopped at the time limit ({state['deadline']} s); not tested."
        state["not_tested"].append(_not_tested(row, reason))
        return
    try:
        built = _tested_row(state["auditor"], row, state["base_ctx"], state["player"],
                            state["guide"], state["powers"], state["statuses"], state["gaps"])
    except LuaError as error:
        reason = "Path of Building could not test this: " + _first_line(error)
        logging.exception("guide row could not be tested: %s", row.get("id"))
        state["not_tested"].append(_not_tested(row, reason))
        return
    destination = state["no_change"] if built.get("zeroNote") and not carries_value(built) else state["ranked"]
    destination.append(built)


def _granted_group_reason(row: dict, player: dict) -> str | None:
    changes = (row.get("info") or {}).get("options") or [row.get("change") or {}]
    gem_changes = [change for change in changes
                   if change.get("type") in {"gemLevel", "addSupport", "replaceSupport"}]
    if not gem_changes:
        return None
    groups = {group.get("index"): group for group in player.get("groups") or []}
    if any((groups.get(change.get("group")) or {}).get("source") is not None
           for change in gem_changes):
        return "This skill is granted by your passive tree or an item, so its gems can't be changed."
    return None


MAGEBLOOD_NOTE = "Mageblood flasks"
_MAGEBLOOD_LINE = "constantly apply their flask effects"


def wears_mageblood(player: dict) -> bool:
    """A belt line that keeps magic utility flasks on (Mageblood, also the Foulborn version)."""
    return any(_MAGEBLOOD_LINE in str(mod).casefold() for item in player.get("items") or []
               if item.get("slot") == "Belt" for mod in item.get("mods") or [])


def _mageblood_reason(row: dict, player: dict) -> str | None:
    """PoB re-adds the saved flasks under Mageblood, so a flask swap measures a phantom second flask."""
    if row.get("category") != "flask" or not wears_mageblood(player):
        return None
    return ("You wear Mageblood: Path of Building keeps your saved flasks on, so a flask change can't "
            f"be measured here (vault note: {MAGEBLOOD_NOTE}).")


def _gap_patterns(player: dict) -> list[dict]:
    """Vault gap patterns; the Mageblood flask lines only apply to a player who wears Mageblood."""
    wears = wears_mageblood(player)
    return [pattern for pattern in load_named_gap_patterns()
            if wears or not (pattern.get("note") == MAGEBLOOD_NOTE and pattern.get("slot") == "Flask")]


def _alternate_set_reason(row: dict) -> str | None:
    """Inactive weapon sets always measure 0 in PoB, so they are listed, not tested."""
    change = row.get("change") or {}
    items = change.get("changes") if change.get("type") == "compound" else [change]
    slots = [str(value.get("slot") or "") for value in items or [] if value.get("type") == "item"]
    if any(slot.endswith(" Swap") for slot in slots):
        return "Alternate weapon sets are not tested."
    return None


def _test_config(state: dict, rows: list[dict]) -> list[dict]:
    result, tester = [], getattr(state["progress"], "testing", None)
    for row in rows:
        if not row.get("change"):
            result.append(evaluate_config(state["auditor"], row, state["base_ctx"]))
            continue
        elapsed = state["clock"]() - state["start"]
        state["done"] += 1
        if state["limited"] or elapsed >= state["deadline"]:
            state["limited"] = True
            reason = f"Stopped at the time limit ({state['deadline']} s); not tested."
            result.append({**copy.deepcopy(row), "tickable": False,
                           "note": "Only if this applies to you in game.",
                           "result": None, "reason": reason})
        else:
            result.append(evaluate_config(state["auditor"], row, state["base_ctx"]))
        if callable(tester):
            tester(state["done"], state["total"])
    return result


def _explain(auditor, rows: list[dict], player: dict, guide: dict,
             clock, start: float, deadline: float) -> None:
    players, guides = _items(player), _items(guide)
    for row in rows:
        slot = (row.get("info") or {}).get("slot") or (row.get("change") or {}).get("slot")
        category = row.get("category", "")
        calls_pob = category.startswith("tree-") or category == "gem-level"
        can_call = not calls_pob or clock() - start < deadline
        row["why"] = explain_row(auditor, row, player, players.get(str(slot)),
                                 guides.get(str(slot)), can_call)
        if not can_call and category.startswith("tree-"):
            row["whySkipped"] = True


def _banners(auditor, differences: dict, limited: bool, untested: list[dict]) -> list[dict]:
    result = copy.deepcopy(differences["banners"])
    if not auditor.obtainable.gems:
        result.append({"kind": "leagueUnavailable",
                       "text": "League data unavailable - availability unknown. Nothing here is claimed obtainable.",
                       "data": {}})
    if limited:
        count = sum("time limit" in str(row.get("reason", "")) for row in untested)
        result.append({"kind": "timeLimit",
                       "text": f"Stopped at the time limit: {count} differences were not tested.",
                       "data": {"count": count}})
    return result


def _result_state(differences: dict, tested: int, untested: list[dict], config: list[dict]) -> str:
    if differences["identical"]:
        return "identical"
    if tested == 0 and (untested or config):
        return "nothingTestable"
    return "differences"


def _scenario_identical(auditor, differences: dict) -> bool:
    if differences["found"] != 0:
        return False
    controlled = set((auditor.scenarios[auditor.scenario].get("pob_config") or {}).keys())
    controlled.update(row.get("var") for row in auditor.conditional if row.get("applied"))
    variables = {fact.get("var") for row in differences["config"]
                 for fact in (row.get("info") or {}).get("vars") or []}
    return variables <= controlled


def _finish(auditor, guide_label: str, state: dict, differences: dict,
            config: list[dict], guide_mb: float, node_error: str | None,
            start: float, deadline_s: float, final: float) -> dict:
    player, guide = state["player"], state["guide"]
    ranked, sorts = rank_rows(state["ranked"])
    no_change = [{**row, "rank": None} for row in state["no_change"]]
    tested = len(ranked) + len(no_change)
    assert differences["found"] == tested + len(state["not_tested"])
    counts = {"found": differences["found"], "tested": tested,
              "notTested": len(state["not_tested"]), "noChange": len(no_change),
              "settings": len(config)}
    perf = {"seconds": final - start, "rowsTested": tested, "luaMB": lua_mb(auditor.engine),
            "luaMBGuideLoaded": guide_mb, "timeLimit": state["limited"],
            "deadlineSeconds": deadline_s}
    if node_error:
        perf["nodeAlone"] = node_error
    banners = _banners(auditor, differences, state["limited"], state["not_tested"])
    return {"state": _result_state(differences, tested, state["not_tested"], config),
            "header": _header(auditor, player, guide, guide_label, banners),
            "base": kpis(auditor, state["base_ctx"]), "rows": ranked, "noChange": no_change,
            "config": config, "notTested": state["not_tested"], "counts": counts,
            "sha": auditor.source_sha256, "playerPath": str(auditor.build_path),
            "perf": perf, "sorts": sorts, "kpiSources": auditor.kpi_sources(state["base_ctx"])}


def run_check(auditor, guide_xml_path, guide_label, progress=lambda label: None, deadline_s=90, *,
              clock=time.monotonic, job_id=None, source=None) -> dict:
    """Test every guide difference on the player build; vault Models are named, not applied (spec 5B)."""
    with models_not_applied(auditor):
        return _run_check(auditor, guide_xml_path, guide_label, progress, deadline_s, clock, job_id, source)


def _run_check(auditor, guide_xml_path, guide_label, progress, deadline_s, clock, job_id, source) -> dict:
    start = clock()
    progress("Loading both builds in Path of Building")
    _probe(auditor.engine)
    player, guide, differences, powers, guide_mb, node_error = _load_pair(
        auditor, guide_xml_path, guide_label)
    if _scenario_identical(auditor, differences):
        differences = {**differences, "config": [], "identical": True}
    base_ctx = auditor.base_context()
    testable_config = [row for row in differences["config"] if row.get("change")]
    state = {"auditor": auditor, "progress": progress, "clock": clock, "start": start,
             "deadline": deadline_s, "limited": False,
             "player": player, "guide": guide, "base_ctx": base_ctx, "powers": powers,
             "statuses": vault_note_status(), "gaps": _gap_patterns(player),
             "rows": differences["rows"], "initial_not_tested": differences["notTested"],
             "ranked": [], "no_change": [], "not_tested": [], "done": 0,
             "total": differences["found"] + len(testable_config)}
    progress("Testing differences")
    _test_rows(state)
    config = _test_config(state, differences["config"])
    zero_rows = [row for row in state["ranked"] + state["no_change"] if row.get("zeroNote")]
    if zero_rows and testable_config and not state["limited"]:
        elapsed = clock() - start
        if elapsed >= deadline_s:
            state["limited"] = True
        else:
            retest_zero_rows(auditor, zero_rows, testable_config)
    _state_unchanged(auditor, base_ctx, player)
    progress("Ranking and explaining")
    _explain(auditor, state["ranked"] + state["no_change"], player, guide,
             clock, start, deadline_s)
    final = clock()
    result = _finish(auditor, guide_label, state, differences, config, guide_mb,
                     node_error, start, deadline_s, final)
    _canonical(result)
    log_check(result, guide_xml_path, str(player.get("label") or ""), source=source, job_id=job_id,
              node_powers=powers)
    return result
