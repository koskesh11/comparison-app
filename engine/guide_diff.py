"""Pure comparison of two Path of Building guide snapshots.

``found`` counts tested rows plus ``notTested`` rows. Configuration entries are
reported separately and are deliberately not included in that count.
"""

import logging

from guide_diff_common import CATEGORY_ORDER, clean_label, node_id, nodes_by_id, row, validate_snapshot
from guide_diff_gems import gem_rows
from guide_diff_items import equipment_rows, jewel_rows, unmatched_jewel_sockets
from guide_diff_tree import candidate_ids, tree_rows

_CONFIG_GROUPS = [
    ("enemyIsBoss", "presetBossSkills", "enemyPhysicalReduction", "enemyLightningResist",
     "enemyColdResist", "enemyFireResist", "enemyChaosResist", "enemyMaxResist"),
    ("conditionEnemyShocked", "conditionShockEffect"),
    ("conditionEnemyChilled", "conditionEnemyChilledEffect"),
    ("conditionEnemyScorched", "conditionScorchedEffect"),
    ("conditionEnemyBrittle", "conditionBrittleEffect"),
    ("conditionEnemySapped", "conditionSapEffect"),
]


def tree_candidates(player: dict, guide: dict) -> dict:
    """Return sorted ids for Lua path and dependency discovery."""
    player = validate_snapshot(player)
    guide = validate_snapshot(guide)
    add, remove = candidate_ids(player, guide)
    add = sorted(set(add) | set(unmatched_jewel_sockets(player, guide)))
    if not nodes_by_id(guide):
        remove = []
    return {"ids": add, "removeIds": remove}


def _banner(kind: str, text: str, data: object) -> dict:
    return {"kind": kind, "text": text, "data": data}


def _class_banner(player: dict, guide: dict) -> dict | None:
    left = {"className": player.get("className"), "ascendancy": player.get("ascendancy")}
    right = {"className": guide.get("className"), "ascendancy": guide.get("ascendancy")}
    if left == right:
        return None
    text = (f"The guide uses {right['ascendancy'] or right['className'] or 'an unknown class'}; "
            f"yours is {left['ascendancy'] or left['className'] or 'an unknown class'}.")
    return _banner("class", text, {"player": left, "guide": right})


def _sets_banner(kind: str, sets: dict, prefix: str) -> dict:
    labels = (("item", "Items"), ("spec", "Tree"), ("skill", "Skills"))
    parts = [f'{label} "{sets.get(key)}"' for key, label in labels if sets.get(key) is not None]
    return _banner(kind, f"Using {prefix} active sets: {', '.join(parts)}.",
                   {key: sets.get(key) for key in ("item", "skill", "spec")})


def _banners(player: dict, guide: dict) -> list[dict]:
    result = []
    class_value = _class_banner(player, guide)
    if class_value:
        result.append(class_value)
    left, right = player.get("mainSkill"), guide.get("mainSkill")
    if left is not None and right is not None and left != right:
        text = f"The guide's main skill is {right}, yours is {left}. All numbers are measured on yours."
        result.append(_banner("mainSkill", text, {"player": left, "guide": right}))
    version = guide.get("sourceTreeVersion") or guide.get("treeVersion")
    if version is not None and version != player.get("treeVersion"):
        shown = str(version).replace("_", ".")
        result.append(_banner("treeVersion", f"Guide tree converted by Path of Building from version {shown}.",
                              {"guide": version, "player": player.get("treeVersion")}))
    guide_sets = guide.get("sets") if isinstance(guide.get("sets"), dict) else {}
    if guide_sets.get("multiple") or any(guide_sets.get(key) is not None for key in ("item", "skill", "spec")):
        result.append(_sets_banner("sets", guide_sets, "the guide's"))
    player_sets = player.get("sets") if isinstance(player.get("sets"), dict) else {}
    if player_sets.get("multiple"):
        result.append(_sets_banner("playerSets", player_sets, "your"))
    if not (guide.get("items") or []):
        result.append(_banner("noItems", "The guide has no items.", {}))
    if not nodes_by_id(guide):
        result.append(_banner("noTree", "The guide has no passive tree.", {}))
    return result


def _config_map(snapshot: dict) -> dict[str, dict]:
    result = {}
    for value in snapshot.get("config") or []:
        if isinstance(value, dict) and value.get("var") is not None:
            result.setdefault(str(value.get("var")), value)
    return result


def _display(value: object) -> str:
    if value is True:
        return "on"
    if value is False:
        return "off"
    if value is None:
        return "default setting"
    return str(value)


def _config_value(entry: dict, other: dict) -> object:
    value = entry.get("value")
    if value is not None:
        return value
    config_type = entry.get("type") or other.get("type")
    if config_type == "check":
        return False
    if config_type in {"count", "countAllowZero", "integer", "float"}:
        return 0
    return None


def _config_row(names: list[str], players: dict[str, dict], guides: dict[str, dict]) -> dict:
    facts, changes, labels, text_setting = [], {}, [], False
    for name in names:
        left, right = players.get(name, {}), guides.get(name, {})
        label = clean_label(right.get("label") or left.get("label") or name)
        player_value = _config_value(left, right)
        guide_value = _config_value(right, left)
        labels.append(label)
        facts.append({"var": name, "label": label, "player": player_value, "guide": guide_value})
        changes[name] = guide_value
        text_setting |= right.get("type") == "text" or left.get("type") == "text"
    detail = "; ".join(f"{fact['label']}: yours {_display(fact['player'])}; "
                       f"guide {_display(fact['guide'])}" for fact in facts)
    built = row(f"config:{names[0]}", "config", " + ".join(labels),
                None if text_setting else {"type": "config", "vars": changes}, detail=detail,
                info={"vars": facts, "tested": not text_setting})
    if text_setting:
        built["reason"] = "Custom text settings are not tested"
    return built


def _config_rows(player: dict, guide: dict) -> list[dict]:
    players, guides = _config_map(player), _config_map(guide)
    differing = {name for name in set(players) | set(guides)
                 if _config_value(players.get(name, {}), guides.get(name, {}))
                 != _config_value(guides.get(name, {}), players.get(name, {}))}
    result, handled = [], set()
    for group in _CONFIG_GROUPS:
        names = [name for name in group if name in differing]
        if names:
            result.append(_config_row(names, players, guides))
            handled.update(names)
    for name in sorted(differing - handled, key=str.casefold):
        result.append(_config_row([name], players, guides))
    return sorted(result, key=lambda value: (value["label"].casefold(), value["id"]))


def _sort(rows: list[dict]) -> list[dict]:
    order = {name: index for index, name in enumerate(CATEGORY_ORDER)}
    return sorted(rows, key=lambda value: (order[value["category"]], value["label"].casefold(), value["id"]))


def _dedupe(tested: list[dict], untested: list[dict]) -> tuple[list[dict], list[dict]]:
    seen, left, right = set(), [], []
    for destination, values in ((left, tested), (right, untested)):
        for value in values:
            if value["id"] in seen:
                logging.warning("guide diff: duplicate row id %s dropped", value["id"])
                continue
            seen.add(value["id"])
            destination.append(value)
    return _sort(left), _sort(right)


def diff(player: dict, guide: dict, tree_info: dict | None) -> dict:
    """Compare snapshots and return tested, untested, config, and banner rows."""
    player = validate_snapshot(player)
    guide = validate_snapshot(guide)
    tested, untested = [], []
    found, skipped = equipment_rows(player, guide)
    tested += found
    untested += skipped
    found, skipped = jewel_rows(player, guide, tree_info)
    tested += found
    untested += skipped
    found, skipped = gem_rows(player, guide)
    tested += found
    untested += skipped
    sockets = {node_id(value.get("socketNode")) for value in guide.get("items") or []
               if isinstance(value, dict) and node_id(value.get("socketNode")) is not None}
    found, skipped = tree_rows(player, guide, tree_info, sockets)
    tested += found
    untested += skipped
    tested, untested = _dedupe(tested, untested)
    config = _config_rows(player, guide)
    count = len(tested) + len(untested)
    return {"found": count, "rows": tested, "notTested": untested, "config": config,
            "identical": count == 0 and not config, "banners": _banners(player, guide)}
