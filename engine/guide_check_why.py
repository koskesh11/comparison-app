"""PoB-derived why lines and KPI-source breakdowns."""

from display import fmt_compact
from scoring import skill_pcts_text


def _source_map(rows: list[dict]) -> dict:
    result = {}
    for row in rows:
        if "label" in row:
            result[row["label"]] = row.get("value")
        for source in row.get("sources") or []:
            result[source["label"]] = source.get("value")
    return result


def breakdown(auditor, base_ctx: dict, ctx: dict) -> list[dict]:
    before, after = auditor.kpi_sources(base_ctx), auditor.kpi_sources(ctx)
    result = []
    for section in sorted(set(before) | set(after)):
        left = _source_map(before.get(section) or [])
        right = _source_map(after.get(section) or [])
        for label in sorted(set(left) | set(right)):
            if left.get(label) != right.get(label):
                result.append({"label": f"{section}: {label}",
                               "before": left.get(label), "after": right.get(label)})
    return result


def cheap_why(dims: dict) -> list[str]:
    text = skill_pcts_text(dims.get("skills") or [])
    return [f"PoB per-skill DPS: {text}"] if text else []


def tree_why(auditor, row: dict) -> list[str]:
    change = row.get("change") or {}
    request = {"removeIds": change.get("nodes") or [] if change.get("type") == "dealloc" else [],
               "addIds": change.get("nodes") or [] if change.get("type") == "alloc" else []}
    values = auditor.call("whyJSON", request)
    return [f"{value['type']} {value['stat']} {fmt_compact(value['from'])} -> "
            f"{fmt_compact(value['to'])} ({value['source']})" for value in values[:4]]


def gem_why(auditor, row: dict, player_snapshot: dict) -> list[str]:
    change = row.get("change") or {}
    group = next((value for value in player_snapshot.get("groups") or []
                  if value.get("index") == change.get("group")), {})
    gems = group.get("gems") or []
    index = (change.get("gemIndex") or 1) - 1
    old = gems[index] if 0 <= index < len(gems) else {}
    request = {"name": change.get("name"),
               "from": {"level": old.get("level"), "quality": old.get("quality")},
               "to": {"level": change.get("level"), "quality": change.get("quality")}}
    values = auditor.call("gemStatDiffJSON", request)
    return [f"{value.get('fromText') or value.get('stat')} -> "
            f"{value.get('toText') or value.get('stat')}" for value in values[:3]]


def item_why(row: dict, player_item: dict | None, guide_item: dict | None) -> list[str]:
    old, new = (player_item or {}).get("mods") or [], (guide_item or {}).get("mods") or []
    added = [f"+ {line}" for line in new if line not in old]
    removed = [f"- {line}" for line in old if line not in new]
    return (added + removed)[:4]


def explain_row(auditor, row: dict, player_snapshot: dict,
                player_item=None, guide_item=None, allow_call: bool = True) -> list[str]:
    lines = cheap_why(row.get("dims") or {})
    if allow_call and row.get("category", "").startswith("tree-"):
        lines = tree_why(auditor, row) + lines
    elif allow_call and row.get("category") == "gem-level":
        lines = gem_why(auditor, row, player_snapshot) + lines
    elif row.get("category") in {"item", "flask", "jewel"}:
        lines = item_why(row, player_item, guide_item) + lines
    if not lines and row.get("zeroNote") is None:
        lines = ["PoB: the change shows up in the totals only (no single modifier source)"]
    return lines[:4]
