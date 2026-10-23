"""Validate, preview, and save combinations from a guide comparison report."""

from __future__ import annotations

import copy
import math
import re
from pathlib import Path

from api_errors import InvalidRequest
import display
import guide_lua
import optimize
from pobhost import LuaError
from scoring import change_pct

_PHASES = {"dealloc": 0, "alloc": 1, "item": 2, "gemLevel": 3, "level": 3,
           "replaceSupport": 4, "addSupport": 5, "addGroup": 6}
_REASONS = {"slot": "same slot", "group": "same skill", "gem": "same gem",
            "node": "one adds and one removes the same passive nodes"}
_METRICS = ("dps", "ehp", "manaMargin", "maxHit")


def rows_index(report: dict) -> dict[str, dict]:
    """Index the tickable sections of a report by stable row id."""
    return {row["id"]: row for section in ("rows", "noChange")
            for row in report.get(section) or []}


def _section_index(report: dict, section: str) -> dict[str, dict]:
    return {row.get("id"): row for row in report.get(section) or []}


def _row_error(row: dict, reason: str) -> InvalidRequest:
    return InvalidRequest(f"{row.get('label') or row.get('id')}: {reason}")


def resolve_ticks(report: dict, ids: list[str]) -> list[dict]:
    """Resolve validated ids into rows while preserving report order."""
    if not isinstance(ids, list) or not ids:
        raise InvalidRequest("ids must be a non-empty list")
    if len(ids) > 500:
        raise InvalidRequest("at most 500 ids may be applied")
    for value in ids:
        if not isinstance(value, str):
            raise InvalidRequest("every id must be a string")
        if len(value) > 200:
            raise InvalidRequest("ids may not exceed 200 characters")
    wanted = set(ids)
    config, untested = _section_index(report, "config"), _section_index(report, "notTested")
    for value in wanted:
        if value in config:
            raise _row_error(config[value], "settings the guide assumes are never applied")
        if value in untested:
            raise _row_error(untested[value], "not tested, so it can't be applied")
    indexed = rows_index(report)
    unknown = sorted(wanted - set(indexed))
    if unknown:
        raise InvalidRequest(f"unknown row id: {unknown[0]}")
    result = [row for section in ("rows", "noChange") for row in report.get(section) or []
              if row["id"] in wanted]
    locked = next((row for row in result if row.get("locked")), None)
    if locked:
        raise _row_error(locked, locked.get("lockReason") or "locked")
    return result


def _flatten(change: dict) -> list[dict]:
    if change.get("type") != "compound":
        return [copy.deepcopy(change)]
    return [simple for child in change.get("changes") or [] for simple in _flatten(child)]


def _path_plan(changes: list[dict]) -> list[dict]:
    kept, covered = [], set()
    for change in sorted(changes, key=lambda value: -len(value.get("nodes") or [])):
        if change.get("target") in covered:
            continue
        kept.append(change)
        covered.update(change.get("nodes") or [])
    return kept


def plan_changes(rows: list[dict]) -> list[dict]:
    """Flatten rows and return the stable mutation order expected by PoB."""
    simple = [change for row in rows for change in _flatten(row["change"])]
    paths = {kind: _path_plan([change for change in simple if change.get("type") == kind])
             for kind in ("dealloc", "alloc")}
    others = [change for change in simple if change.get("type") not in paths]
    items = sorted((change for change in others if change.get("type") == "item"),
                   key=lambda value: value.get("slot") or "")
    by_phase = paths["dealloc"] + paths["alloc"] + items
    for phase in range(3, 7):
        by_phase += [change for change in others if _PHASES.get(change.get("type")) == phase]
    return by_phase


def conflicts(rows: list[dict]) -> list[dict]:
    """Return pairwise conflicts phrased for the first row in each pair."""
    indexed = {row["id"]: row for row in rows}
    result, seen = [], set()
    for pair in optimize.conflict_pairs([(row["id"], row["change"]) for row in rows]):
        key = (pair["keys"], pair["kind"])
        if key in seen or pair["kind"] not in _REASONS:
            continue
        seen.add(key)
        left, right = pair["keys"]
        label = indexed[right].get("label") or right
        result.append({"ids": [left, right],
                       "message": f"Can't combine with {label} ({_REASONS[pair['kind']]})."})
    return result


def _number(value: object) -> float | int | None:
    return value if isinstance(value, (int, float)) and math.isfinite(value) else None


def _dimensions(auditor, ctx: dict) -> dict:
    out = auditor.main_out(ctx)
    return {"dps": _number(out.get(auditor.dps_key) or 0),
            "ehp": _number(out.get("TotalEHP") or 0),
            "manaMargin": _number(auditor.mana_margin(ctx)),
            "maxHit": _number(out.get("PhysicalMaximumHitTaken") or 0)}


def _combined(base: dict, after: dict) -> dict:
    base = {key: _number(value) for key, value in base.items()}
    after = {key: _number(value) for key, value in after.items()}
    pct = lambda key: (_number(change_pct(after[key], base[key]))
                       if after[key] is not None and base[key] is not None else None)
    mana = (after["manaMargin"] - base["manaMargin"]
            if after["manaMargin"] is not None and base["manaMargin"] is not None else None)
    return {"base": base, "after": after,
            "delta": {"dpsPct": pct("dps"), "ehpPct": pct("ehp"),
                      "manaMargin": _number(mana), "maxHit": pct("maxHit")}}


def _empty_result(rows: list[dict], found: list[dict], reason: str | None = None) -> dict:
    refused = {"reason": reason, "message": found[0]["message"]} if reason else None
    return {"ok": refused is None, "refused": refused, "conflicts": found,
            "ids": [row["id"] for row in rows], "combined": None,
            "points": None, "violations": []}


def _pob_message(error: Exception) -> str:
    first = next((line.strip() for line in str(error).splitlines() if line.strip()), "")
    detail = first.rsplit(": ", 1)[-1]
    return f"Path of Building did not accept this combination: {detail}"


def _run(auditor, rows: list[dict], want_xml: bool) -> tuple[dict, str | None]:
    found = conflicts(rows)
    if found:
        return _empty_result(rows, found, "conflict"), None
    engine = auditor.engine
    engine.load_build(auditor.build_path)
    auditor.load_audit_hooks(auditor.disabled_skills)
    base_ctx = auditor.evaluate()
    auditor.breaks(base_ctx)
    before = guide_lua.snapshot(engine, "player")["points"]
    name = f"{auditor.summary['buildName']} (guide check)"
    try:
        applied = guide_lua.apply_changes(engine, plan_changes(rows), auditor.keys, name,
                                          extra_skills=auditor.extra_request(), save=want_xml)
    except LuaError as error:
        if "did not accept" not in str(error):
            raise
        result = _empty_result(rows, [], None)
        result.update(ok=False, refused={"reason": "pob", "message": _pob_message(error)})
        return result, None
    ctx = auditor.adjust(applied["ctx"])
    after = guide_lua.snapshot(engine, "player")["points"]
    combined = _combined(_dimensions(auditor, base_ctx), _dimensions(auditor, ctx))
    over = after["used"] > after["available"] and after["used"] > before["used"]
    needs = after["used"] - after["available"] if over else 0
    points = {"before": before["used"], "after": after["used"], "available": after["available"],
              "over": over, "needs": needs}
    violations = auditor.breaks(ctx)
    refused = ({"reason": "budget", "message": f"needs {needs} more points; also tick a removal"} if over
               else {"reason": "rule", "message": "Breaks a rule: " + "; ".join(violations)}
               if violations else None)
    result = {"ok": refused is None, "refused": refused, "conflicts": [],
              "ids": [row["id"] for row in rows], "combined": combined,
              "points": points, "violations": violations}
    return result, applied.get("xml")


def predict(auditor, rows: list[dict]) -> dict:
    """Preview a row combination without serializing or writing the build."""
    return _run(auditor, rows, False)[0]


def _safe_name(value: object) -> str:
    name = re.sub(r"[^\w .()'-]", "", str(value or ""), flags=re.UNICODE).strip()[:80]
    name = re.sub(r"\.{2,}", ".", name).strip()
    return name or "Build"


def _reload_equal(predicted: dict, reloaded: dict) -> tuple[bool, list[str]]:
    diffs = []
    for key in _METRICS:
        left, right = predicted[key], reloaded[key]
        if left is None or right is None:
            if left != right:
                diffs.append(f"{key}: predicted {left}, reloaded {right}")
            continue
        raw = left == right or abs(left - right) <= 1e-6 * max(abs(left), abs(right))
        digits = 1 if key == "manaMargin" else 0
        if not raw or display.fmt(left, digits) != display.fmt(right, digits):
            diffs.append(f"{key}: predicted {left}, reloaded {right}")
    return not diffs, diffs


def _reload(auditor, path: Path, predicted: dict) -> dict:
    try:
        auditor.engine.load_build(path)
        auditor.load_audit_hooks(auditor.disabled_skills)
        reloaded = _dimensions(auditor, auditor.evaluate())
        equal, diffs = _reload_equal(predicted, reloaded)
        return {"checked": True, "equal": equal, "diffs": diffs, "error": None}
    except (LuaError, OSError, ValueError):
        return {"checked": True, "equal": False, "diffs": [], "error": "reload check failed"}


def save(auditor, rows: list[dict], out_dir: Path, force: bool = False) -> dict:
    """Run the preview path, save an accepted XML, and verify it after reload."""
    result, xml = _run(auditor, rows, True)
    allowed = result["refused"] is None or (force and result["refused"]["reason"] == "rule")
    result.update(saved=False, path=None, fileName=None, reload=None)
    if not allowed:
        return result
    name = _safe_name(auditor.summary.get("buildName")) + " (guide check)"
    path = optimize.save_xml(Path(out_dir), name, xml)
    reload = _reload(auditor, path, result["combined"]["after"])
    result.update(saved=True, path=str(path), fileName=path.name, reload=reload)
    return result


def not_applied(report: dict, applied_ids: list[str]) -> dict:
    """Count every report row excluded from a saved combination."""
    rows = [row for section in ("rows", "noChange") for row in report.get(section) or []]
    unobtainable = sum(row.get("locked", False) and "unobtainable" in (row.get("chips") or []) for row in rows)
    locked = sum(row.get("locked", False) and "unobtainable" not in (row.get("chips") or []) for row in rows)
    applied = set(applied_ids)
    unticked = sum(not row.get("locked", False) and row.get("id") not in applied for row in rows)
    result = {"config": len(report.get("config") or []), "notTested": len(report.get("notTested") or []),
              "unobtainable": unobtainable, "locked": locked, "unticked": unticked}
    return {**result, "total": sum(result.values())}
