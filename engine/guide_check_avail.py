"""League obtainability for guide-check rows."""

from obtainability import gem_key

_GEM_TYPES = {"addSupport", "replaceSupport", "addGroup", "gemLevel"}


def _gems(row: dict) -> list[dict]:
    change = row.get("change") or {}
    kind = change.get("type")
    if kind in {"addSupport", "replaceSupport"}:
        return [change.get("gem") or {}]
    if kind == "addGroup":
        return [gem for gem in change.get("gems") or [] if isinstance(gem, dict)]
    if kind == "gemLevel":
        return [{key: change.get(key) for key in ("name", "level", "quality", "qualityId")}]
    return []


def _one(obtainable, gem: dict) -> dict:
    name = str(gem.get("name") or "gem")
    if not obtainable.gems:
        return {"state": "unknown", "name": name, "reason": "league data unavailable"}
    quality_id = gem.get("qualityId")
    if quality_id not in (None, "Default"):
        return {"state": "unknown", "name": name,
                "reason": "alternate quality is not in the league data"}
    status = obtainable.status(name)
    if status["state"] == "denied":
        reason = status.get("reason") or f"not obtainable in {obtainable.league}"
        return {"state": "unobtainable", "name": name, "reason": reason,
                "note": status.get("note"), "since": status.get("since")}
    if status["state"] == "unlisted":
        return {"state": "unobtainable", "name": name,
                "reason": f"not seen in {obtainable.league} data"}
    level, quality = gem.get("level") or 0, gem.get("quality") or 0
    if level > 20 or quality > 20:
        variants = obtainable.gems.get(gem_key(name), [])
        if not any(value.level >= level and value.quality >= quality for value in variants):
            reason = f"level {level} / quality {quality}% not seen in {obtainable.league} data"
            return {"state": "unobtainable", "name": name, "reason": reason}
    return {"state": "obtainable", "name": name, "reason": "listed in league data"}


def _category(row: dict) -> str:
    category = row.get("category")
    if category:
        return category
    return "gem" if (row.get("change") or {}).get("type") in _GEM_TYPES else ""


def row_availability(obtainable, row: dict, *_args, **_kwargs) -> dict:
    """Return the worst availability state among gems changed by a row."""
    category = _category(row)
    if category in {"item", "flask", "jewel"}:
        return {"state": "notChecked", "text": "Item availability isn't checked.", "gems": []}
    if category in {"tree-add", "tree-remove"}:
        return {"state": "n/a", "text": "Not applicable.", "gems": []}
    gems = [_one(obtainable, gem) for gem in _gems(row)]
    if not gems:
        return {"state": "n/a", "text": "Not applicable.", "gems": []}
    order = {"obtainable": 0, "unknown": 1, "unobtainable": 2}
    state = max((gem["state"] for gem in gems), key=order.get)
    worst = next(gem for gem in gems if gem["state"] == state)
    if state == "obtainable":
        text = f"Obtainable in {obtainable.league}."
    elif state == "unknown":
        text = worst["reason"]
    else:
        text = worst["reason"]
    return {"state": state, "text": text, "gems": gems}
