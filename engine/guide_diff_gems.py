"""Socket-group, support, and gem-level rows."""

from guide_diff_common import not_tested, number, row


def _gems(group: dict) -> list[dict]:
    return [value for value in group.get("gems") or [] if isinstance(value, dict)]


def _active(group: dict) -> list[dict]:
    return [value for value in _gems(group) if not value.get("isSupport")]


def _supports(group: dict, enabled_only: bool = False) -> list[dict]:
    values = [value for value in _gems(group) if value.get("isSupport")]
    return [value for value in values if value.get("enabled") is not False] if enabled_only else values


def _names(values: list[dict]) -> list[str]:
    return sorted({str(value.get("name") or "gem") for value in values}, key=str.casefold)


def _position(group: dict, gem: dict) -> int:
    for index, candidate in enumerate(_gems(group), 1):
        if candidate is gem:
            return index
    return 0


def _quality_id(gem: dict) -> str:
    value = gem.get("qualityId")
    return "Default" if value is None else str(value)


def _gem_payload(gem: dict, support: bool | None = None) -> dict:
    result = {"name": gem.get("name"), "gemId": gem.get("gemId"),
              "isSupport": bool(gem.get("isSupport")) if support is None else support,
              "level": number(gem.get("level")), "quality": number(gem.get("quality")),
              "qualityId": gem.get("qualityId"), "enabled": gem.get("enabled") is not False}
    if support is None:
        result.update({"count": gem.get("count"), "skillPart": gem.get("skillPart")})
    return result


def _guide_groups(snapshot: dict) -> list[dict]:
    values = [value for value in snapshot.get("groups") or [] if isinstance(value, dict)]
    return sorted(values, key=lambda value: (number(value.get("index")),
                                              "+".join(_names(_active(value))).casefold()))


def _player_groups(snapshot: dict) -> list[dict]:
    return _guide_groups(snapshot)


def _candidate_key(guide: dict, player: dict, used: set[int]) -> tuple:
    guide_active, player_active = set(_names(_active(guide))), set(_names(_active(player)))
    shared_active = len(guide_active & player_active)
    same_slot = guide.get("slot") is not None and guide.get("slot") == player.get("slot")
    guide_support, player_support = set(_names(_supports(guide, True))), set(_names(_supports(player)))
    return (-shared_active, -int(same_slot), -len(guide_support & player_support),
            int(number(player.get("index")) in used), number(player.get("index")))


def _match_group(guide: dict, players: list[dict], used: set[int]) -> dict | None:
    wanted = set(_names(_active(guide)))
    candidates = [value for value in players if wanted & set(_names(_active(value)))]
    return min(candidates, key=lambda value: _candidate_key(guide, value, used)) if candidates else None


def _part_note(group: dict) -> str | None:
    details = []
    for gem in _active(group):
        name = str(gem.get("name") or "skill")
        gem_details = []
        if gem.get("skillPart") is not None and gem.get("skillPart") != 1:
            gem_details.append(f"skill part {gem.get('skillPart')}")
        if gem.get("count") is not None and gem.get("count") != 1:
            gem_details.append(f"gem count {gem.get('count')}")
        if gem_details:
            details.append((name, " / ".join(gem_details)))
    if not details:
        return None
    if len(_active(group)) == 1:
        return "Uses the guide's " + details[0][1]
    return "Uses the guide's " + "; ".join(f"{name}: {value}" for name, value in details)


def _add_group(guide: dict, player: dict) -> dict:
    active = _names(_active(guide))
    key = "+".join(active)
    slot = guide.get("slot")
    equipped = any(isinstance(value, dict) and value.get("slot") == slot
                   for value in player.get("items") or [])
    change = {"type": "addGroup", "slot": slot if slot and equipped else None,
              "label": str(guide.get("label") or ", ".join(active)),
              "fullDps": guide.get("fullDps"),
              "gems": [_gem_payload(value) for value in _gems(guide)]}
    touches = [{"kind": "group", "key": f"add:{name}"} for name in active]
    return row(f"group-add:{key}", "group-add", f"Add skill {', '.join(active)}", change,
               touches, _part_note(guide), info={"supports": _names(_supports(guide, True)),
                                                "guideSlot": slot})


def _trigger_supports(groups: tuple[dict, dict]) -> list[str]:
    prefixes = ("cast on ", "cast when ", "cast while ", "spellslinger")
    names = [str(value.get("name") or "") for group in groups for value in _supports(group)]
    return [name for name in names if name.casefold().startswith(prefixes)]


def _level_row(guide_gem: dict, player_gem: dict, player_group: dict,
               guide_group: dict) -> dict | None:
    old = (number(player_gem.get("level")), number(player_gem.get("quality")), _quality_id(player_gem))
    new = (number(guide_gem.get("level")), number(guide_gem.get("quality")), _quality_id(guide_gem))
    if old == new:
        return None
    index, name = number(player_group.get("index")), str(guide_gem.get("name") or "gem")
    guide_quality = f"quality {new[1]}%" + (f" {new[2]}" if new[2] != old[2] else "")
    player_quality = f"quality {old[1]}%" + (f" {old[2]}" if new[2] != old[2] else "")
    label = (f'{name} in "{player_group.get("label") or f"Group {index}"}": guide uses level '
             f"{new[0]}, {guide_quality} (yours: level {old[0]}, {player_quality})")
    flags = ["lower-level"] if new[0] < old[0] else []
    refs = []
    triggers = _trigger_supports((player_group, guide_group))
    if triggers:
        flags.append("trigger")
        refs.append("Trigger attack stays at cheapest level")
        if any(name.casefold().startswith("cast on critical") for name in triggers):
            refs += ["CoC requires 100% crit and hit", "Trigger attack under the CoC cap"]
    change = {"type": "gemLevel", "group": index,
              "gemIndex": _position(player_group, player_gem), "name": name,
              "level": new[0], "quality": new[1], "qualityId": guide_gem.get("qualityId")}
    return row(f"gem-level:{index}:{name}", "gem-level", label, change,
               [{"kind": "gem", "key": [index, name]}], flags=flags, vault_refs=refs,
               info={"group": index, "name": name})


def _replace_change(group: dict, player_gem: dict, guide_gem: dict) -> dict:
    return {"type": "replaceSupport", "group": number(group.get("index")),
            "gemIndex": _position(group, player_gem),
            "replaced": player_gem.get("name"), "gem": _gem_payload(guide_gem, True)}


def _family_row(guide_gem: dict, old: dict, player_group: dict) -> dict:
    new_name, old_name = str(guide_gem.get("name")), str(old.get("name"))
    if new_name.startswith("Awakened ") and not old_name.startswith("Awakened "):
        label = f"Upgrade {old_name} to {new_name}"
    else:
        label = f"Swap {old_name} for {new_name} (same support family)"
    option = _replace_change(player_group, old, guide_gem)
    index = number(player_group.get("index"))
    return row(f"support-replace:{index}:{new_name}", "support-replace", label, option,
               [{"kind": "gem", "key": [index, old_name]}], flags=["family"],
               info={"candidates": [old_name], "options": [option]})


def _missing_support(guide_gem: dict, player_group: dict, guide_names: set[str]) -> dict:
    index, name = number(player_group.get("index")), str(guide_gem.get("name"))
    limit = player_group.get("socketLimit")
    limit = number(limit) if limit is not None else 6
    free = limit - len(_gems(player_group))
    label = str(player_group.get("label") or f"Group {index}")
    if free > 0:
        change = {"type": "addSupport", "group": index, "gem": _gem_payload(guide_gem, True)}
        return row(f"support-add:{index}:{name}", "support-add", f'Add support {name} in "{label}"',
                   change, [{"kind": "gem", "key": [index, name]}, {"kind": "socket", "key": index}],
                   info={"freeSockets": free})
    candidates = [value for value in _supports(player_group)
                  if str(value.get("name")) not in guide_names]
    candidates.sort(key=lambda value: (_position(player_group, value),
                                       str(value.get("name")).casefold()))
    if not candidates:
        return not_tested(f"support-replace:{index}:{name}", "support-replace", f"Add support {name}",
                          "No free socket and nothing to replace")
    options = [_replace_change(player_group, value, guide_gem) for value in candidates]
    names = [str(value.get("name")) for value in candidates]
    if len(names) == 1:
        text = f'Replace {names[0]} with {name} in "{label}"'
    else:
        text = f'Replace one of your supports with {name} in "{label}"'
    touches = [{"kind": "gem", "key": [index, value]} for value in names]
    return row(f"support-replace:{index}:{name}", "support-replace", text, options[0], touches,
               info={"candidates": names, "options": options})


def _matched_rows(guide: dict, player: dict) -> tuple[list[dict], list[dict]]:
    tested, untested = [], []
    player_gems = _gems(player)
    by_name = {}
    for value in player_gems:
        by_name.setdefault(str(value.get("name")), value)
    guide_support_names = set(_names(_supports(guide, True)))
    for guide_gem in [value for value in _gems(guide) if value.get("enabled") is not False]:
        name = str(guide_gem.get("name"))
        player_gem = by_name.get(name)
        if player_gem is not None:
            if guide_gem.get("isSupport") and player_gem.get("enabled") is False:
                untested.append(not_tested(f"support-add:{number(player.get('index'))}:{name}",
                                           "support-add", f"Switch on {name}",
                                           "Switched off in your build"))
                continue
            level = _level_row(guide_gem, player_gem, player, guide)
            if level:
                tested.append(level)
            if not guide_gem.get("isSupport") and (guide_gem.get("skillPart"), guide_gem.get("count")) \
                    != (player_gem.get("skillPart"), player_gem.get("count")):
                ident = number(player.get("index"))
                untested.append(not_tested(f"gem-level:{ident}:{name}:part", "gem-level", name,
                                           "Skill part or gem count is set by hand and differs"))
            continue
        if not guide_gem.get("isSupport"):
            continue
        family = guide_gem.get("family")
        family_match = next((value for value in _supports(player)
                             if family is not None and value.get("family") == family
                             and str(value.get("name")) not in guide_support_names), None)
        built = (_family_row(guide_gem, family_match, player) if family_match else
                 _missing_support(guide_gem, player, guide_support_names))
        (untested if "reason" in built else tested).append(built)
    return tested, untested


def gem_rows(player: dict, guide: dict) -> tuple[list[dict], list[dict]]:
    """Build group, support, and gem-level rows."""
    tested, untested, used = [], [], set()
    players = _player_groups(player)
    for guide_group in _guide_groups(guide):
        index = number(guide_group.get("index"))
        if guide_group.get("enabled") is False:
            untested.append(not_tested(f"group-add:disabled:{index}", "group-add",
                                       str(guide_group.get("label") or f"Group {index}"),
                                       "Skill group is switched off in the guide"))
            continue
        active = _active(guide_group)
        if not active:
            untested.append(not_tested(f"group-add:no-active:{index}", "group-add",
                                       str(guide_group.get("label") or f"Group {index}"),
                                       "Group has no active skill"))
            continue
        matched = _match_group(guide_group, players, used)
        if matched is None:
            tested.append(_add_group(guide_group, player))
            continue
        used.add(number(matched.get("index")))
        if not set(_names(active)) <= set(_names(_active(matched))):
            untested.append(not_tested(f"group-add:partial:{index}", "group-add",
                                       str(guide_group.get("label") or f"Group {index}"),
                                       "Group mixes skills the player has in different groups"))
            continue
        found, skipped = _matched_rows(guide_group, matched)
        tested += found
        untested += skipped
    return tested, untested
