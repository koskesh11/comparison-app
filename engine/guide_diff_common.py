"""Shared constructors and names for guide snapshot diffs."""

import re

CATEGORY_ORDER = ["item", "flask", "jewel", "group-add", "support-add",
                  "support-replace", "gem-level", "tree-add", "tree-remove", "config"]
CLASS_START_TYPES = {"ClassStart", "AscendClassStart"}
OVERRIDE_REASON = "Tattoos and runegrafts aren't tested yet."


def validate_snapshot(snapshot: object) -> dict:
    """Return a supported snapshot or raise the public schema error."""
    if not isinstance(snapshot, dict) or snapshot.get("schema") != 1:
        raise ValueError("unsupported snapshot schema")
    return snapshot


def node_id(value: object) -> int | None:
    """Convert a node id to int when possible."""
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def item_name(item: dict | None) -> str:
    """Best available full name for item matching and signatures."""
    item = item or {}
    return str(item.get("name") or item.get("title") or item.get("base") or "item")


def display_name(item: dict | None) -> str:
    """Return the user-facing item name without the appended base type."""
    item = item or {}
    return str(item.get("title") or item.get("name") or item.get("base") or "item")


def clean_label(text: object) -> str:
    """Remove Path of Building colour markup and one trailing colon."""
    value = re.sub(r"\^x[0-9A-Fa-f]{6}|\^[0-9]", "", str(text or "")).strip()
    return value[:-1].rstrip() if value.endswith(":") else value


def node_name(node: dict | None, fallback: int | None = None) -> str:
    """Best available display name for a node."""
    return str((node or {}).get("name") or (f"Node {fallback}" if fallback is not None else "node"))


def override_facts(node: dict) -> dict | None:
    """Return normalized tattoo or runegraft facts when present."""
    override = node.get("override")
    if not isinstance(override, dict):
        return None
    raw_lines = override.get("lines")
    lines = [str(value) for value in raw_lines] if isinstance(raw_lines, list) else []
    return {"name": str(override.get("name") or "Tattoo"), "lines": lines,
            "plain": str(override.get("plain") or node_name(node))}


def classify_node(node: dict) -> str:
    """Classify a snapshot node in the specification's first-match order."""
    if node.get("type") in CLASS_START_TYPES:
        return "structural"
    if node.get("ascendancy") is not None:
        return "ascendancy"
    ident = node_id(node.get("id")) or 0
    if node.get("cluster") or ident >= 65536:
        return "cluster"
    if node.get("conquered"):
        return "conquered"
    if node.get("override") is not None:
        return "override"
    if node.get("socket") or node.get("type") == "Socket":
        return "socket"
    if node.get("type") == "Mastery":
        return "mastery"
    if node.get("modKeyEmpty"):
        return "no-stats"
    if node.get("type") not in (None, "Normal", "Notable", "Keystone"):
        return "unknown"
    return "testable"


def nodes_by_id(snapshot: dict) -> dict[int, dict]:
    """Return non-structural nodes keyed deterministically by integer id."""
    result = {}
    for value in snapshot.get("nodes") or []:
        if not isinstance(value, dict) or classify_node(value) == "structural":
            continue
        ident = node_id(value.get("id"))
        if ident is not None and ident not in result:
            result[ident] = value
    return result


def sorted_unique(values: list) -> list:
    """Deduplicate and sort touches by kind and semantic key."""
    found = {repr(value): value for value in values}

    def key(value: object) -> tuple:
        if not isinstance(value, dict):
            return ("", str(value))
        raw = value.get("key")
        parts = raw if isinstance(raw, list) else [raw]
        cooked = tuple((0, part) if isinstance(part, int) else (1, str(part).casefold())
                       for part in parts)
        return (str(value.get("kind") or ""), cooked)

    return sorted(found.values(), key=key)


def row(row_id: str, category: str, label: str, change: dict | None = None,
        touches: list[dict] | None = None, note: str | None = None,
        detail: str | None = None, flags: list[str] | None = None,
        vault_refs: list[str] | None = None, info: dict | None = None) -> dict:
    """Construct a complete, deterministic row."""
    touch_values = touches or []
    touch_values = sorted_unique(touch_values)
    return {"id": row_id, "category": category, "label": label, "change": change,
            "touches": touch_values, "note": note, "detail": detail,
            "flags": sorted(set(flags or []), key=str.casefold),
            "vaultRefs": sorted(set(vault_refs or []), key=str.casefold), "info": info or {}}


def not_tested(row_id: str, category: str, label: str, reason: str,
               touches: list[dict] | None = None, note: str | None = None,
               detail: str | None = None, flags: list[str] | None = None,
               info: dict | None = None) -> dict:
    """Construct a complete row which cannot be tested."""
    return {**row(row_id, category, label, None, touches, note, detail, flags, info=info),
            "reason": reason}


def info_node(tree_info: dict | None, ident: int) -> dict:
    """Look up tree information accepting integer or string keys."""
    nodes = (tree_info or {}).get("nodes") or {}
    value = nodes.get(ident, nodes.get(str(ident), {})) if isinstance(nodes, dict) else {}
    return value if isinstance(value, dict) else {}


def number(value: object) -> int:
    """Use zero for missing comparison numbers."""
    return value if isinstance(value, int) and not isinstance(value, bool) else 0
