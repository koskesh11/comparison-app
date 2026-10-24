"""PoB-derived conditional and zero-result notes for guide rows."""

DOWNSIDE_WORDING = "unaffected by"
NEEDS_FLAGS = {
    "ElementalResistMaxIsHighestResistMax": "needs a raised maximum Elemental Resistance",
}


def _gem_ids(row: dict) -> list[str]:
    change = row.get("change") or {}
    if change.get("gems"):
        return [gem["gemId"] for gem in change["gems"] if gem.get("gemId")]
    gem = change.get("gem") or {}
    return [gem["gemId"]] if gem.get("gemId") else []


def _curse_note(auditor, row: dict) -> str | None:
    """Say the curse limit is used up only by PoB's own rule; anything it can't decide falls back to the neutral note."""
    if not row.get("zeroNote"):
        return None
    gem_ids = _gem_ids(row)
    if not gem_ids:
        return None
    state = auditor.call("curseStateJSON", {"gemIds": gem_ids})
    curses, marks = state.get("curse") or {}, state.get("mark") or {}
    limit, slots = state.get("limit") or 0, state.get("slots") or []
    if state.get("limitBypass") or any(marks.get(gem_id) is not False for gem_id in gem_ids):
        return None
    if all(curses.get(gem_id) is True for gem_id in gem_ids) and limit > 0 and len(slots) >= limit:
        names = ", ".join(slots)
        return (f"PoB shows no effect here: your curse limit ({limit}) is used up by "
                f"curses that count against it ({names}).")
    return None


def _guide_runs(guide: dict, name: str) -> bool:
    return any(group.get("enabled") is True and gem.get("enabled") is True
               and gem.get("name") == name
               for group in guide.get("groups") or [] for gem in group.get("gems") or [])


def _need_texts(parsed: list[dict] | dict, guide: dict) -> list[str]:
    """"needs X" only for a skill gem the player could add; generic buffs (Aura, Arcane Surge) and downside mods are skipped."""
    texts = []
    for value in parsed or []:
        if DOWNSIDE_WORDING in str(value.get("text") or "").lower():
            continue
        for condition in value.get("conditions") or []:
            label = condition.get("skill")
            if label and condition.get("on") is False:
                suffix = "; the guide runs it" if _guide_runs(guide, label) else ""
                texts.append(f"needs {label} (not in your build{suffix})")
        texts.extend(NEEDS_FLAGS[flag] for flag in value.get("flags") or []
                     if flag in NEEDS_FLAGS)
    return list(dict.fromkeys(texts))


def _conditional(auditor, row: dict, player_item: dict | None,
                 guide_item: dict | None, guide: dict) -> dict | None:
    if row.get("category") not in {"item", "flask", "jewel"} or row.get("conditional") is not None:
        return None
    old, new = (player_item or {}).get("mods") or [], (guide_item or {}).get("mods") or []
    added = [line for line in new if line not in old]
    if not added:
        return None
    texts = _need_texts(auditor.call("modNeedsJSON", {"lines": added}), guide)
    if not texts:
        return None
    return {"text": "; ".join(texts), "dpsPct": None, "ehpPct": None, "settings": []}


def apply_notes(auditor, row: dict, player_item: dict | None,
                guide_item: dict | None, guide: dict) -> dict:
    result = {}
    zero_note = _curse_note(auditor, row)
    conditional = _conditional(auditor, row, player_item, guide_item, guide)
    if zero_note:
        result["zeroNote"] = zero_note
    if conditional:
        result["conditional"] = conditional
    return result
