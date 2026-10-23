"""Audit socketed gems that are denied or absent from the league cache."""

from costs import used_together
from display import fmt
from obtainability import Obtainability, gem_key
from pobhost import LuaError
from scoring import attack_names, skill_out, trigger_overshoot_why
import part_variants

TRIGGER_PREFIXES = ("cast on ", "cast when ", "cast while ")
OWN_BONUS = {"awakened cast on critical strike": "cooldown recovery"}
RATE_EPS = 1e-9


def _cache_text(value: str | None) -> str:
    return f"cache {value}" if value else "cache date unknown"


def flag_label(status: dict) -> str | None:
    state = status["state"]
    if state == "denied":
        return (f"Unobtainable since {status['since']}: {status['reason']} "
                f"(vault: {status['note']})")
    if state == "unlisted":
        cache = _cache_text(status.get("cacheDate"))
        return f"not listed on poe.ninja {status['league']} ({cache}), unverified"
    return None


def flagged_rows(gems: list[dict], obtainable: Obtainability) -> tuple[int, list[dict]]:
    checked = 0
    rows = []
    for gem in sorted(gems, key=lambda row: (row["group"], row["gemIndex"])):
        if gem["granted"]:
            continue
        checked += 1
        status = obtainable.status(gem["name"])
        label = flag_label(status)
        if label:
            rows.append({
                "group": gem["group"], "gemIndex": gem["gemIndex"], "groupLabel": gem["groupLabel"],
                "name": gem["name"], "level": gem["level"], "quality": gem["quality"],
                "state": status["state"], "label": label,
            })
    return checked, rows


def choose_replacement(name: str, obtainable: Obtainability) -> tuple[dict | None, str | None]:
    normal = obtainable.normal_version(name)
    if normal is None:
        return None, f"{name} has no normal version"
    best = obtainable.best_uncorrupted(normal)
    if best is None:
        cache = _cache_text(obtainable.cache_date)
        note = f"{normal} has no uncorrupted listing on poe.ninja {obtainable.league} ({cache})"
        return None, note
    return {"with": normal, "level": best.level, "quality": best.quality}, None


def _changed(before: float | None, after: float | None) -> bool:
    if before is None or after is None:
        return before is not after
    return abs(before - after) > RATE_EPS


def _rate(value: float | None) -> str:
    return "n/a" if value is None else fmt(value, 2) + "/s"


def trigger_why(base_ctx: dict, ctx: dict) -> list[str]:
    after = {}
    for row in used_together(ctx):
        if row["name"] not in after:
            after[row["name"]] = row
    lines, seen = [], set()
    for before in used_together(base_ctx):
        name = before["name"]
        if name in seen:
            continue
        seen.add(name)
        old, new = skill_out(before), skill_out(after.get(name, {}))
        rate_from, rate_to = old.get("SkillTriggerRate"), new.get("SkillTriggerRate")
        cap_from, cap_to = old.get("TriggerRateCap"), new.get("TriggerRateCap")
        if all(value is None for value in (rate_from, rate_to, cap_from, cap_to)):
            continue
        if not _changed(rate_from, rate_to) and not _changed(cap_from, cap_to):
            continue
        line = f"{name}: {_rate(rate_from)} -> {_rate(rate_to)}"
        if cap_from is not None or cap_to is not None:
            line += f", cap {_rate(cap_from)} -> {_rate(cap_to)}"
        source_to = new.get("EffectiveSourceRate")
        if rate_to is not None and cap_to is not None and source_to is not None:
            why = trigger_overshoot_why(rate_to, cap_to, source_to, attack_names(ctx))
            if why is not None:
                line += "; " + why
        lines.append(line)
    return lines


def removal_why(name: str) -> list[str]:
    key = gem_key(name)
    prefix_key = key.removeprefix("awakened ")
    if not prefix_key.startswith(TRIGGER_PREFIXES):
        return []
    example = f" (e.g. {OWN_BONUS[key]})" if key in OWN_BONUS else ""
    return [f"removes {name}'s own bonuses{example}"]


def swap_levels(obtainable: Obtainability) -> dict[str, dict]:
    levels = {}
    for key in sorted(obtainable.gems):
        best = obtainable.best_uncorrupted(key)
        if obtainable.gem_obtainable(key) and best is not None:
            levels[key] = {"level": best.level, "quality": best.quality}
    return levels


def skipped_count(result: dict) -> int:
    skipped = result.get("skipped", 0)
    if isinstance(skipped, list):
        return len(skipped)
    return int(skipped or 0)


def _item_lines(item: dict, fmt_dims) -> list[str]:
    tag = f"[{item['id']}]" if item["id"] is not None else "   "
    lines = [f"   {tag} group {item['group']} gem {item['gemIndex']}: "
             f"{item['name']} {item['level']}/{item['quality']}: {item['label']}"]
    replacement = item["replacement"]
    if replacement:
        lines.append(f"         -> {replacement['with']} {replacement['level']}/{replacement['quality']}: "
                     f"{fmt_dims(item['dims'])}")
        parts = part_variants.parts_text(item["dims"])
        if parts:
            lines.append("         " + parts)
    else:
        lines.append(f"         no replacement: {item['replacementNote']}")
    lines += [f"         why: {why}" for why in item["why"]]
    lines += [f"         !! breaks (shown, still offered: the current gem can't be obtained): {broken}"
              for broken in item["breaks"]]
    return lines


def alert_lines(section: dict, fmt_dims) -> list[str]:
    items = section["items"]
    if not items:
        return []
    lines = [f"!! {len(items)} unobtainable or unlisted gem(s) already in your build "
             f"({section['checked']} gems checked):"]
    for item in items:
        lines += _item_lines(item, fmt_dims)
    combined = section.get("combined")
    if combined:
        lines.append(f"   together {combined['ids']}: {fmt_dims(combined['dims'])}")
        parts = part_variants.parts_text(combined["dims"])
        if parts:
            lines.append("         " + parts)
        lines += [f"         why: {why}" for why in combined["why"]]
        lines += [f"         !! breaks (shown, still offered: the current gem can't be obtained): {broken}"
                  for broken in combined["breaks"]]
    return lines


def _request(auditor, replacements: list[dict]) -> dict:
    request = {"stats": auditor.keys, "replacements": replacements,
               "extraSkills": auditor.extra_request()}
    return {**request, "partVariants": True} if auditor.multi_part else request


def run_replacements(auditor, replacements: list[dict]) -> tuple[dict | None, dict[int, str]]:
    try:
        result = auditor.call("auditGemReplaceJSON", _request(auditor, replacements))
        return {**result, "indexes": list(range(len(replacements)))}, {}
    except LuaError:
        failures, survivors = {}, []
        for index, replacement in enumerate(replacements):
            try:
                auditor.call("auditGemReplaceJSON", _request(auditor, [replacement]))
                survivors.append(index)
            except LuaError as error:
                failures[index] = str(error)
        if not survivors:
            return None, failures
        remaining = [replacements[index] for index in survivors]
        result = auditor.call("auditGemReplaceJSON", _request(auditor, remaining))
        return {**result, "indexes": survivors}, failures


def _build_item(auditor, base_ctx: dict, row: dict, choice: dict | None, note: str | None,
                single: dict | None, failure: str | None) -> dict:
    replacement, item_id, dims = None, None, None
    why, broken = [], []
    if failure is not None:
        note = f"PoB cannot apply {choice['with']}: {failure}"
    elif single is not None:
        ctx = auditor.adjust(single["ctx"])
        dims = auditor.dimensions(ctx, base_ctx)
        why = trigger_why(base_ctx, ctx) + removal_why(row["name"])
        broken = auditor.breaks(ctx)
        replacement = {"with": single["with"], "level": single["level"], "quality": single["quality"]}
        change = {"type": "replaceGem", "group": row["group"], "gemIndex": row["gemIndex"],
                  "name": row["name"], **replacement}
        item_id = auditor.suggest(change)
        note = None
    return {**row, "replacement": replacement, "replacementNote": note, "id": item_id,
            "dims": dims, "why": why, "breaks": broken}


def _combined(auditor, base_ctx: dict, result: dict | None, items: list[dict]) -> dict | None:
    replaced = [item for item in items if item["replacement"] is not None]
    if len(replaced) < 2:
        return None
    ctx = auditor.adjust(result["combined"])
    why = trigger_why(base_ctx, ctx)
    for item in replaced:
        why += removal_why(item["name"])
    return {"ids": [item["id"] for item in replaced], "dims": auditor.dimensions(ctx, base_ctx),
            "why": why, "breaks": auditor.breaks(ctx)}


def check(auditor, base_ctx: dict) -> dict:
    checked, rows = flagged_rows(auditor.call("listGemsJSON"), auditor.obtainable)
    if not rows:
        return {"checked": checked, "items": [], "combined": None}
    choices = [choose_replacement(row["name"], auditor.obtainable) for row in rows]
    request_rows = [index for index, (choice, note) in enumerate(choices) if choice is not None]
    replacements = [{"group": rows[index]["group"], "gemIndex": rows[index]["gemIndex"],
                     "name": rows[index]["name"], **choices[index][0]} for index in request_rows]
    result, failures = run_replacements(auditor, replacements) if replacements else (None, {})
    singles = {} if result is None else {
        request_rows[index]: single for index, single in zip(result["indexes"], result["single"])
    }
    failed_rows = {request_rows[index]: message for index, message in failures.items()}
    items = [_build_item(auditor, base_ctx, row, choices[index][0], choices[index][1],
                         singles.get(index), failed_rows.get(index))
             for index, row in enumerate(rows)]
    return {"checked": checked, "items": items, "combined": _combined(auditor, base_ctx, result, items)}
