"""Equipment, flask, and jewel rows for guide snapshot comparison."""

from collections import Counter

from guide_diff_common import display_name, item_name, node_id, nodes_by_id, not_tested, row

PAIRS = {"Forbidden Flame": "Forbidden Flesh", "Forbidden Flesh": "Forbidden Flame"}
SLOT_GROUPS = (("Ring 1", "Ring 2", "Ring 3"),
               ("Flask 1", "Flask 2", "Flask 3", "Flask 4", "Flask 5"))


def _clean_raw(raw: object) -> str:
    stripped = [line.strip() for line in str(raw or "").splitlines()]
    lines = [line for line in stripped if not line.startswith(("Unique ID:", "Item Level:"))]
    return " ".join(" ".join(lines).split())


def _sockets(item: dict) -> str:
    for line in str(item.get("raw") or "").splitlines():
        if line.strip().lower().startswith("sockets:"):
            return line.strip()
    return ""


def signature(item: dict) -> tuple:
    """Return the complete item signature used by snapshot comparison."""
    abyss = sorted((str(value.get("name") or ""), _clean_raw(value.get("raw")))
                   for value in item.get("abyssJewels") or [] if isinstance(value, dict))
    return (item_name(item), item.get("base"), item.get("variant"), bool(item.get("corrupted")),
            _sockets(item), tuple(sorted(str(value) for value in item.get("mods") or [])), tuple(abyss))


def _items(snapshot: dict, jewels: bool = False) -> list[dict]:
    values = []
    for value in snapshot.get("items") or []:
        if not isinstance(value, dict) or "Abyssal Socket" in str(value.get("slot") or ""):
            continue
        if (value.get("socketNode") is not None) == jewels:
            values.append(value)
    return sorted(values, key=lambda value: (str(value.get("slot") or "").casefold(),
                                             item_name(value).casefold(), repr(signature(value))))


def _item_change(item: dict, slot: str, flask_active: bool | None = None) -> dict:
    abyss = [{"slot": value.get("slot"), "raw": value.get("raw")}
             for value in item.get("abyssJewels") or [] if isinstance(value, dict)]
    abyss.sort(key=lambda value: (str(value.get("slot") or "").casefold(), str(value.get("raw") or "")))
    change = {"type": "item", "slot": slot, "name": item_name(item), "raw": item.get("raw"),
              "abyssJewels": abyss, "flaskActive": flask_active}
    if node_id(item.get("socketNode")) is not None:
        change["socketNode"] = node_id(item.get("socketNode"))
    return change


def _touches(item: dict, slot: str) -> list[dict]:
    result = [{"kind": "slot", "key": slot}]
    result += [{"kind": "slot", "key": value.get("slot")}
               for value in item.get("abyssJewels") or [] if isinstance(value, dict)]
    return result


def _differences(player: dict, guide: dict) -> list[str]:
    result = []
    if player.get("base") != guide.get("base"):
        result.append("base")
    if player.get("variant") != guide.get("variant"):
        result.append("variant")
    if bool(player.get("corrupted")) != bool(guide.get("corrupted")):
        result.append("corrupted")
    if _sockets(player) != _sockets(guide):
        result.append("sockets")
    old, new = Counter(player.get("mods") or []), Counter(guide.get("mods") or [])
    for value, count in sorted((new - old).items(), key=lambda pair: str(pair[0]).casefold()):
        result += [f"+ {value}"] * count
    for value, count in sorted((old - new).items(), key=lambda pair: str(pair[0]).casefold()):
        result += [f"- {value}"] * count
    if signature(player)[-1] != signature(guide)[-1]:
        result.append("abyss jewels")
    if len(result) > 6:
        return result[:6] + [f"and {len(result) - 6} more"]
    return result


def _slot_group(slot: str) -> tuple[str, ...] | None:
    return next((group for group in SLOT_GROUPS if slot in group), None)


def _placements(player_items: list[dict], guide_items: list[dict]) -> tuple[list[tuple[dict, str]], list[dict]]:
    """Match equivalent ring/flask slots and choose deterministic destinations."""
    placements, failures, handled = [], [], set()
    player_by_slot = {value.get("slot"): value for value in player_items}
    for slots in SLOT_GROUPS:
        guides = [value for value in guide_items if value.get("slot") in slots]
        players = [value for value in player_items if value.get("slot") in slots]
        used = set()
        remaining = []
        for guide in guides:
            match = next((player for player in players
                          if player.get("slot") not in used and signature(player) == signature(guide)), None)
            if match is not None:
                used.add(match.get("slot"))
                if guide.get("slot") == match.get("slot") and str(guide.get("slot")).startswith("Flask") \
                        and match.get("flaskActive") is False and guide.get("flaskActive") is not False:
                    placements.append((guide, str(guide.get("slot"))))
            else:
                remaining.append(guide)
            handled.add(id(guide))
        placed = set(used)
        for guide in remaining:
            own = str(guide.get("slot") or "")
            target = own if own not in placed else next((slot for slot in slots if slot not in placed), None)
            if target is None:
                failures.append(guide)
            else:
                placements.append((guide, target))
                placed.add(target)
    placements += [(value, str(value.get("slot") or "")) for value in guide_items if id(value) not in handled]
    return placements, failures


def _equipment_row(guide: dict, target_slot: str, player: dict | None) -> dict | None:
    category = "flask" if target_slot.startswith("Flask") else "item"
    same = player is not None and signature(player) == signature(guide)
    inactive = (category == "flask" and player is not None and player.get("flaskActive") is False
                and guide.get("flaskActive") is not False)
    if same and not inactive:
        return None
    same_name = player is not None and item_name(player) == item_name(guide)
    differences = _differences(player, guide) if same_name and player is not None else []
    name, old = display_name(guide), display_name(player) if player else None
    label = f"Replace {old} with {name} in {target_slot}" if player else f"Add {name} in {target_slot}"
    abyss_count = len(guide.get("abyssJewels") or [])
    if abyss_count:
        label += f" (with {abyss_count} abyss jewel" + ("" if abyss_count == 1 else "s") + ")"
    note = f"Same item, different: {', '.join(differences)}" if same_name and differences else None
    flags = ["same-name"] if same_name and differences else []
    active = True if inactive else None
    if inactive:
        note = f"Only if you use this flask: your {target_slot} is switched off in the build."
        flags.append("flask-inactive")
    return row(f"{category}:{target_slot}", category, label,
               _item_change(guide, target_slot, active), _touches(guide, target_slot), note,
               flags=flags, info={"slot": target_slot, "fromItem": old, "toItem": name,
                                  "differing": differences})


def _weapon_pair(player: dict, guide: dict, player_by_slot: dict, guide_by_slot: dict) -> dict | None:
    player_two = bool((player.get("handedness") or {}).get("weapon1TwoHanded"))
    guide_two = bool((guide.get("handedness") or {}).get("weapon1TwoHanded"))
    one, two, old = guide_by_slot.get("Weapon 1"), guide_by_slot.get("Weapon 2"), player_by_slot.get("Weapon 1")
    if not player_two or guide_two or one is None or two is None:
        return None
    if old is not None and signature(old) == signature(one):
        return None
    changes = [_item_change(one, "Weapon 1"), _item_change(two, "Weapon 2")]
    touches = _touches(one, "Weapon 1") + _touches(two, "Weapon 2")
    return row("item:Weapon 1+Weapon 2", "item",
               f"Replace your two-handed weapon with {display_name(one)} and {display_name(two)}",
               {"type": "compound", "changes": changes}, touches, flags=["handedness"],
               info={"slot": "Weapon 1+Weapon 2", "fromItem": display_name(old),
                     "toItem": f"{display_name(one)} + {display_name(two)}", "differing": ["handedness"]})


def equipment_rows(player: dict, guide: dict) -> tuple[list[dict], list[dict]]:
    """Build ordinary item and flask rows."""
    players, guides = _items(player), _items(guide)
    player_by_slot = {value.get("slot"): value for value in players}
    guide_by_slot = {value.get("slot"): value for value in guides}
    pair = _weapon_pair(player, guide, player_by_slot, guide_by_slot)
    skip = {"Weapon 1", "Weapon 2"} if pair else set()
    placements, failures = _placements(players, guides)
    tested = [pair] if pair else []
    for guide_item, target in placements:
        if guide_item.get("slot") in skip:
            continue
        built = _equipment_row(guide_item, target, player_by_slot.get(target))
        if built is None:
            continue
        if (guide.get("handedness") or {}).get("weapon1TwoHanded") and target == "Weapon 1" \
                and (player.get("handedness") or {}).get("weapon2"):
            built["note"] = "A two-handed weapon removes your Weapon 2 item in the calculation."
            built["flags"] = sorted(set(built["flags"] + ["handedness"]))
        tested.append(built)
    untested = [not_tested(f"{'flask' if str(value.get('slot')).startswith('Flask') else 'item'}:{value.get('slot')}",
                           "flask" if str(value.get("slot")).startswith("Flask") else "item",
                           f"Add {display_name(value)}", "No free slot for this item") for value in failures]
    return tested, untested


def _unmatched_jewels(player: dict, guide: dict) -> list[dict]:
    player_values = _items(player, jewels=True)
    used = set()
    result = []
    for guide_item in _items(guide, jewels=True):
        match = next((index for index, value in enumerate(player_values)
                      if index not in used and signature(value) == signature(guide_item)), None)
        if match is None:
            result.append(guide_item)
        else:
            used.add(match)
    return result


def unmatched_jewel_sockets(player: dict, guide: dict) -> list[int]:
    """Return sockets requiring allocation for unmatched testable guide jewels."""
    allocated = set(nodes_by_id(player))
    result = {node_id(value.get("socketNode")) for value in _unmatched_jewels(player, guide)
              if not value.get("cluster") and not value.get("timeless")
              and node_id(value.get("socketNode")) not in allocated}
    return sorted(value for value in result if value is not None)


def _path(tree_info: dict | None, socket: int) -> list[int] | None:
    nodes = (tree_info or {}).get("nodes") or {}
    facts = nodes.get(socket, nodes.get(str(socket), {})) if isinstance(nodes, dict) else {}
    values = facts.get("path") if isinstance(facts, dict) else None
    if not isinstance(values, list) or socket not in [node_id(value) for value in values]:
        return None
    result = []
    for value in values:
        ident = node_id(value)
        if ident is not None and ident not in result:
            result.append(ident)
    return result


def _single_jewel(player: dict, guide: dict, jewel: dict, tree_info: dict | None,
                  unmatched: list[dict]) -> dict:
    slot = str(jewel.get("slot") or "socket")
    socket, name = node_id(jewel.get("socketNode")), display_name(jewel)
    if jewel.get("cluster") or jewel.get("timeless"):
        reason = "Cluster jewels are not tested" if jewel.get("cluster") else "Timeless jewels are not tested"
        return not_tested(f"jewel:{slot}", "jewel", name, reason, info={"slot": slot, "node": socket})
    allocated = set(nodes_by_id(player))
    player_at = next((value for value in _items(player, jewels=True)
                      if node_id(value.get("socketNode")) == socket), None)
    other_guides = [value for value in _items(guide, jewels=True) if value is not jewel]
    if player_at and any(signature(player_at) == signature(value) for value in other_guides):
        return not_tested(f"jewel:{slot}", "jewel", name, "Socket is used by another jewel")
    change = _item_change(jewel, slot)
    label = f"Replace {display_name(player_at)} with {name} in {slot}" if player_at else f"Add {name} in {slot}"
    touches = _touches(jewel, slot)
    points = 0
    if socket not in allocated:
        path = _path(tree_info, socket) if socket is not None else None
        if path is None:
            return not_tested(f"jewel:{slot}", "jewel", name, "No path to the jewel socket")
        points = len(path)
        change = {"type": "compound", "changes": [
            {"type": "alloc", "target": socket, "nodes": path}, change]}
        touches += [{"kind": "node", "key": value} for value in path]
        label = f"Add {name} in socket {slot} (costs {points} point{'' if points == 1 else 's'})"
    flags, note = [], None
    partner = PAIRS.get(name)
    if partner:
        flags.append("paired")
        in_player = any(display_name(value) == partner for value in _items(player, jewels=True))
        in_guide = any(display_name(value) == partner for value in _items(guide, jewels=True))
        state = "already in your build" if in_player else "not in the guide" if not in_guide else "also needed"
        note = f"Needs both: its partner {partner} is {state}"
    return row(f"jewel:{slot}", "jewel", label, change, touches, note, flags=flags,
               info={"slot": slot, "fromItem": display_name(player_at) if player_at else None,
                     "toItem": name, "differing": [], "points": points})


def _paired_row(first: dict, second: dict, tree_info: dict | None, player: dict) -> dict:
    changes, nodes, touches = [], [], []
    allocated = set(nodes_by_id(player))
    names = sorted((display_name(first), display_name(second)), key=str.casefold)
    row_id = f"jewel:pair:{names[0]}+{names[1]}"
    label = f"{names[0]} + {names[1]} (needs both)"
    for jewel in (first, second):
        socket = node_id(jewel.get("socketNode"))
        touches += _touches(jewel, str(jewel.get("slot") or "socket"))
        if socket not in allocated:
            path = _path(tree_info, socket) if socket is not None else None
            if path is None:
                return not_tested(row_id, "jewel", label, "No path to the jewel socket",
                                  touches, flags=["paired"], info={"points": 0, "names": names})
            nodes += path
        changes.append(_item_change(jewel, str(jewel.get("slot") or "socket")))
    if nodes:
        merged = list(dict.fromkeys(nodes))
        changes.insert(0, {"type": "alloc", "target": merged[-1], "nodes": merged})
        touches += [{"kind": "node", "key": value} for value in merged]
    return row(row_id, "jewel", label,
               {"type": "compound", "changes": changes}, touches, flags=["paired"],
               info={"points": len(set(nodes)), "names": names})


def jewel_rows(player: dict, guide: dict, tree_info: dict | None) -> tuple[list[dict], list[dict]]:
    """Build jewel rows, including paired Forbidden jewels."""
    unmatched = _unmatched_jewels(player, guide)
    tested, untested, consumed = [], [], set()
    for first in unmatched:
        first_name = display_name(first)
        if id(first) in consumed or first_name not in PAIRS or first.get("cluster") or first.get("timeless"):
            continue
        partner = next((value for value in unmatched if value is not first
                        and display_name(value) == PAIRS[first_name]
                        and not value.get("cluster") and not value.get("timeless")), None)
        if partner is None:
            continue
        built = _paired_row(first, partner, tree_info, player)
        (untested if "reason" in built else tested).append(built)
        consumed |= {id(first), id(partner)}
    for jewel in unmatched:
        if id(jewel) in consumed:
            continue
        built = _single_jewel(player, guide, jewel, tree_info, unmatched)
        (untested if "reason" in built else tested).append(built)
    return tested, untested
