"""Passive-tree rows for guide snapshot comparison."""

from guide_diff_common import (OVERRIDE_REASON, classify_node, info_node, node_id, node_name,
                               nodes_by_id, not_tested, override_facts, row)


def _ids(values: object, include: int, sort: bool = False) -> list[int]:
    found = []
    for value in values if isinstance(values, list) else []:
        ident = node_id(value)
        if ident is not None and ident not in found:
            found.append(ident)
    if include not in found:
        found.append(include)
    return sorted(found) if sort else found


def candidate_ids(player: dict, guide: dict) -> tuple[list[int], list[int]]:
    """Return guide-only and player-only testable allocation ids."""
    players, guides = nodes_by_id(player), nodes_by_id(guide)
    add = [ident for ident, value in guides.items()
           if ident not in players and classify_node(value) == "testable"]
    remove = [ident for ident, value in players.items()
              if ident not in guides and classify_node(value) == "testable"]
    return sorted(add), sorted(remove)


def _facts(tree_info: dict | None, ident: int, fallback: dict) -> dict:
    value = info_node(tree_info, ident)
    return {**fallback, **value}


def _alloc_row(ident: int, target: dict, guides: dict[int, dict], guide_only: set[int],
               tree_info: dict | None) -> tuple[dict, set[int]]:
    facts = _facts(tree_info, ident, target)
    path = _ids(facts.get("path"), ident)
    if not facts.get("path") or ident not in [node_id(value) for value in facts.get("path") or []]:
        label = f"Take {node_name(target, ident)}"
        return not_tested(f"tree-add:{ident}", "tree-add", label,
                          "no path to this node", info={"node": ident}), set()
    overridden = next((override_facts(guides[value]) for value in path
                       if value != ident and value in guide_only
                       and override_facts(guides[value]) is not None), None)
    if overridden:
        detail = f"path includes {overridden['name']} on {overridden['plain']}"
        return not_tested(f"tree-add:{ident}", "tree-add", f"Take {node_name(target, ident)}",
                          OVERRIDE_REASON, detail=detail, info={"node": ident}), set()
    extras = sorted({node_name(guides[value], value) for value in path
                     if value != ident and value in guide_only}, key=str.casefold)
    path_nodes = max(0, len(path) - 1)
    details = []
    if path_nodes:
        details.append(f"includes {path_nodes} path node" + ("" if path_nodes == 1 else "s"))
    if extras:
        details.append("also takes: " + ", ".join(extras))
    note = "Changed by your timeless jewel" if facts.get("conquered") else None
    flags = ["conquered-yours"] if facts.get("conquered") else []
    change = {"type": "alloc", "target": ident, "nodes": path}
    touches = [{"kind": "node", "key": value} for value in path]
    value = row(f"tree-add:{ident}", "tree-add", f"Take {node_name(target, ident)}", change,
                touches, note, "; ".join(details) or None, flags,
                info={"points": len(path), "pathNodes": path_nodes, "node": ident,
                      "nodeType": target.get("type"), "alsoTakes": extras})
    return value, set(path)


def _jewel_names(player: dict, depends: list[int]) -> list[str]:
    names = []
    for item in player.get("items") or []:
        if not isinstance(item, dict) or node_id(item.get("socketNode")) not in depends:
            continue
        names.append(f"the jewel in {item.get('slot') or 'socket'}")
    return sorted(set(names), key=str.casefold)


def _remove_row(ident: int, target: dict, players: dict[int, dict], player: dict,
                tree_info: dict | None) -> tuple[dict, set[int]]:
    depends_raw = info_node(tree_info, ident).get("depends")
    if not isinstance(depends_raw, list):
        return not_tested(f"tree-remove:{ident}", "tree-remove", f"Drop {node_name(target, ident)}",
                          "no dependency information", info={"node": ident}), set()
    depends = _ids(depends_raw, ident, sort=True)
    overridden = next((value for value in depends if value != ident and value in players
                       and override_facts(players[value]) is not None), None)
    if overridden is not None:
        return not_tested(f"tree-remove:{ident}", "tree-remove",
                          f"Drop {node_name(target, ident)}", OVERRIDE_REASON,
                          info={"node": ident}), set()
    also = sorted({node_name(players[value], value) for value in depends
                   if value != ident and value in players}, key=str.casefold)
    also += [name for name in _jewel_names(player, depends) if name not in also]
    refund = len(depends)
    detail = f"refunds {refund} point" + ("" if refund == 1 else "s")
    if also:
        detail += "; also removes: " + ", ".join(also)
    change = {"type": "dealloc", "target": ident, "nodes": depends}
    touches = [{"kind": "node", "key": value} for value in depends]
    value = row(f"tree-remove:{ident}", "tree-remove", f"Drop {node_name(target, ident)}",
                change, touches, detail=detail,
                info={"refund": refund, "alsoRemoves": also, "node": ident})
    return value, set(depends)


def _grouped(direction: str, kind: str, values: list[tuple[int, dict]]) -> dict:
    reasons = {"ascendancy": "Ascendancy nodes are not tested",
               "cluster": "Cluster jewel nodes are not tested",
               "conquered": "Timeless jewel nodes are not tested",
               "no-stats": "Nodes without stats PoB could compare are not tested"}
    titles = {"ascendancy": "Ascendancy nodes", "cluster": "Cluster jewel nodes",
              "conquered": "Timeless jewel nodes", "no-stats": "Nodes without stats"}
    names = sorted({node_name(value, ident) for ident, value in values}, key=str.casefold)
    ids = sorted({ident for ident, _ in values})
    category = f"tree-{direction}"
    label = f"{titles[kind]} ({len(ids)}): " + ", ".join(names)
    return not_tested(f"{category}:{'timeless' if kind == 'conquered' else kind}", category,
                      label, reasons[kind], info={"nodes": ids, "names": names})


def _untested_rows(direction: str, values: list[tuple[int, dict]], covered: set[int],
                   guide_jewel_sockets: set[int]) -> list[dict]:
    result = []
    for kind in ("ascendancy", "cluster", "conquered", "no-stats"):
        matches = [(ident, value) for ident, value in values
                   if classify_node(value) == kind and ident not in covered]
        if matches:
            result.append(_grouped(direction, kind, matches))
    category = f"tree-{direction}"
    for ident, value in sorted(values):
        kind = classify_node(value)
        if kind == "override":
            facts = override_facts(value)
            action = "Take" if direction == "add" else "Drop"
            result.append(not_tested(f"{category}:{ident}", category,
                                     f"{action} {facts['name']} on {facts['plain']}",
                                     OVERRIDE_REASON, detail="; ".join(facts["lines"]) or None,
                                     info={"node": ident, "override": facts["name"]}))
        elif kind == "mastery":
            result.append(not_tested(f"{category}:{ident}", category,
                                     f"{'Take' if direction == 'add' else 'Drop'} {node_name(value, ident)}",
                                     "Mastery nodes are not tested", info={"node": ident}))
        elif kind == "socket" and not (direction == "add" and ident in guide_jewel_sockets):
            result.append(not_tested(f"{category}:{ident}", category,
                                     f"Jewel socket {node_name(value, ident)}",
                                     "Jewel socket without a jewel is not tested", info={"node": ident}))
        elif kind == "unknown":
            node_type = str(value.get("type"))
            result.append(not_tested(f"{category}:{ident}", category, node_name(value, ident),
                                     f"Node type {node_type} is not tested", info={"node": ident}))
    return result


def tree_rows(player: dict, guide: dict, tree_info: dict | None,
              guide_jewel_sockets: set[int]) -> tuple[list[dict], list[dict]]:
    """Build tested and untested passive-tree rows."""
    players, guides = nodes_by_id(player), nodes_by_id(guide)
    if not guides:
        return [], []
    add_values = [(ident, guides[ident]) for ident in sorted(guides) if ident not in players]
    remove_values = [(ident, players[ident]) for ident in sorted(players) if ident not in guides]
    tested, untested, add_covered, remove_covered = [], [], set(), set()
    guide_only = {ident for ident, _ in add_values}
    for ident, value in add_values:
        if classify_node(value) == "testable":
            built, covered = _alloc_row(ident, value, guides, guide_only, tree_info)
            (untested if "reason" in built else tested).append(built)
            add_covered |= covered
    for ident, value in remove_values:
        if classify_node(value) == "testable":
            built, covered = _remove_row(ident, value, players, player, tree_info)
            (untested if "reason" in built else tested).append(built)
            remove_covered |= covered
    untested += _untested_rows("add", add_values, add_covered, guide_jewel_sockets)
    untested += _untested_rows("remove", remove_values, remove_covered, set())
    for ident in sorted(set(players) & set(guides)):
        left, right = players[ident], guides[ident]
        if left.get("override") != right.get("override"):
            yours, wanted = override_facts(left), override_facts(right)
            facts = yours or wanted
            label = (f"Tattoo or runegraft on {facts['plain']}: "
                     f"yours {yours['name'] if yours else 'none'}, "
                     f"the guide's {wanted['name'] if wanted else 'none'}")
            untested.append(not_tested(f"tree-add:override:{ident}", "tree-add", label,
                                       OVERRIDE_REASON, info={"node": ident}))
        if classify_node(left) == "mastery" and left.get("mastery") != right.get("mastery"):
            label = f"Mastery choice differs: yours {left.get('mastery')}, the guide's {right.get('mastery')}"
            untested.append(not_tested(f"tree-add:mastery-choice:{ident}", "tree-add", label,
                                       "Mastery choices are not tested", info={"node": ident}))
    return tested, untested
