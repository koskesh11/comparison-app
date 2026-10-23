"""Tests for pure guide snapshot comparison."""

import json
import copy
import sys
import unittest
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

import guide_diff  # noqa: E402


def snap(**values: object) -> dict:
    base = {"schema": 1, "which": "player", "label": "Build", "pobVersion": "x",
            "className": "Witch", "ascendancy": None, "level": 90, "treeVersion": "3_29",
            "mainSkill": "Arc", "mainGroup": 1,
            "sets": {"item": None, "skill": None, "spec": None, "multiple": False},
            "points": {"used": 0, "available": 0}, "nodes": [], "groups": [], "items": [],
            "config": [], "handedness": {"weapon1TwoHanded": False, "weapon2": False}}
    base.update(values)
    return base


def node(node_id: int, name: str = "Node", **values: object) -> dict:
    base = {"id": node_id, "name": name, "type": "Normal", "ascendancy": None,
            "cluster": False, "conquered": False, "modKeyEmpty": False,
            "mastery": None, "socket": False}
    base.update(values)
    return base


def gem(name: str, support: bool = False, **values: object) -> dict:
    base = {"name": name, "gemId": name.replace(" ", ""), "isSupport": support,
            "level": 20, "quality": 20, "qualityId": None, "enabled": True,
            "count": None, "skillPart": None, "family": None}
    base.update(values)
    return base


def group(index: int, active: str = "Cyclone", gems: list[dict] | None = None, **values: object) -> dict:
    base = {"index": index, "label": f"Group {index}", "slot": None, "enabled": True,
            "fullDps": False, "mainActiveSkill": active, "socketLimit": None,
            "gems": gems if gems is not None else [gem(active)]}
    base.update(values)
    return base


def item(slot: str, name: str, **values: object) -> dict:
    base = {"slot": slot, "name": name, "title": None, "base": name, "rarity": "RARE",
            "variant": None, "raw": name, "mods": [], "corrupted": False,
            "flaskActive": None, "cluster": False, "timeless": False,
            "abyssJewels": [], "socketNode": None}
    base.update(values)
    return base


def tree_info(**nodes: dict) -> dict:
    return {"nodes": nodes}


def rows(result: dict, category: str) -> list[dict]:
    return [row for row in result["rows"] if row["category"] == category]


def assert_contract(case: unittest.TestCase, result: dict) -> None:
    required = {"id", "category", "label", "change", "touches", "note", "detail",
                "flags", "vaultRefs", "info"}
    found = result["rows"] + result["notTested"]
    case.assertEqual(len({value["id"] for value in found}), len(found))
    case.assertEqual(result["found"], len(found))
    for value in found + result["config"]:
        case.assertTrue(required <= value.keys())
        case.assertIn(value["category"], guide_diff.CATEGORY_ORDER)
        case.assertTrue(all(touch["kind"] in {"slot", "group", "gem", "node", "socket"}
                            for touch in value["touches"]))
    json.dumps(result)


class GemDiffTests(unittest.TestCase):
    def test_support_options_use_distinct_gem_indices_for_equal_dicts(self):
        first = gem("Twin", True)
        second = gem("Twin", True)
        shared = [gem(f"Shared {value}", True) for value in range(1, 4)]
        player = snap(groups=[group(1, gems=[gem("Cyclone"), first, second, *shared])])
        guide = snap(groups=[group(1, gems=[gem("Cyclone"), *shared, gem("New", True)])])
        found = rows(guide_diff.diff(player, guide, None), "support-replace")[0]
        self.assertEqual([option["gemIndex"] for option in found["info"]["options"]], [2, 3])

    def test_gem_level_label_quality_id(self):
        cases = [(None, None, "quality 20% (yours:", (19, 20)),
                 (None, "Anomalous", "quality 20% Anomalous (yours: level 20, quality 20% Default)",
                  (20, 20))]
        for old_id, new_id, label_text, qualities in cases:
            with self.subTest(new_id=new_id):
                player_gem = gem("Arc", quality=qualities[0], qualityId=old_id)
                guide_gem = gem("Arc", quality=qualities[1], qualityId=new_id)
                result = guide_diff.diff(snap(groups=[group(1, "Arc", [player_gem])]),
                                         snap(groups=[group(1, "Arc", [guide_gem])]), None)
                found = rows(result, "gem-level")[0]
                self.assertIn(label_text, found["label"])
                if new_id is None:
                    self.assertNotIn("Default", found["label"])
                else:
                    self.assertEqual(found["change"]["qualityId"], new_id)

    def test_default_and_none_quality_ids_are_equal(self):
        player = snap(groups=[group(1, "Arc", [gem("Arc", qualityId=None)])])
        guide = snap(groups=[group(1, "Arc", [gem("Arc", qualityId="Default")])])
        self.assertFalse(rows(guide_diff.diff(player, guide, None), "gem-level"))

    def test_t_worb_projectile_support_row_present(self):
        shared = [gem(name, True) for name in ("Cold", "Controlled", "Infused", "Inspiration")]
        player = snap(groups=[group(3, "Winter Orb", [gem("Winter Orb", count=5), *shared],
                                    socketLimit=6)])
        guide = snap(groups=[group(8, "Winter Orb", [gem("Winter Orb", count=5), *shared,
                                                       gem("Lesser Projectiles", True)], socketLimit=6)])
        result = guide_diff.diff(player, guide, None)
        additions = rows(result, "support-add")
        self.assertEqual(len(additions), 1)
        self.assertEqual(additions[0]["change"]["group"], 3)
        self.assertFalse(rows(result, "group-add"))
        self.assertFalse(rows(result, "gem-level"))
        self.assertFalse(any(row["id"].endswith(":part") for row in result["notTested"]))

    def test_t_coc_a_full_group_replaces_once_with_all_options(self):
        supports = [gem(f"Old {n}", True, family=f"old{n}") for n in range(1, 6)]
        player = snap(groups=[group(1, gems=[gem("Cyclone"), *supports])])
        guide = snap(groups=[group(1, gems=[gem("Cyclone"), gem("New", True, family="new")])])
        result = guide_diff.diff(player, guide, None)
        found = rows(result, "support-replace")
        self.assertEqual(len(found), 1)
        self.assertEqual(len(found[0]["info"]["options"]), 5)
        self.assertFalse(rows(result, "group-add"))

    def test_t_coc_a_free_socket_adds_and_custom_limit_replaces(self):
        cases = [(5, None, "support-add"), (4, 4, "support-replace")]
        for count, limit, expected in cases:
            with self.subTest(expected=expected):
                gems = [gem("Cyclone")] + [gem(f"Old {n}", True) for n in range(count - 1)]
                player = snap(groups=[group(1, gems=gems, socketLimit=limit)])
                guide = snap(groups=[group(1, gems=[gem("Cyclone"), gem("New", True)])])
                result = guide_diff.diff(player, guide, None)
                self.assertEqual(len(rows(result, expected)), 1)
                if expected == "support-add":
                    self.assertEqual(rows(result, expected)[0]["info"]["freeSockets"], 1)

    def test_awakened_family_swap_and_reverse(self):
        cases = [("Added Cold Damage", "Awakened Added Cold Damage", "Upgrade"),
                 ("Awakened Added Cold Damage", "Added Cold Damage", "Swap")]
        for old, new, label in cases:
            with self.subTest(old=old):
                player = snap(groups=[group(2, "Arc", [gem("Arc"), gem(old, True, family="cold")])])
                guide = snap(groups=[group(7, "Arc", [gem("Arc"), gem(new, True, family="cold")])])
                result = guide_diff.diff(player, guide, None)
                row = rows(result, "support-replace")[0]
                self.assertTrue(row["label"].startswith(label))
                self.assertFalse(rows(result, "support-add"))

    def test_t_coc_b_non_main_group_and_trigger_levels(self):
        player = snap(groups=[group(4, "Cyclone", [gem("Cyclone"), gem("Cast on Critical Strike", True),
                                                     gem("Arc", level=10)])])
        guide = snap(groups=[group(9, "Cyclone", [gem("Cyclone"), gem("Cast on Critical Strike", True),
                                                   gem("Arc", level=12), gem("Added", True)])])
        result = guide_diff.diff(player, guide, None)
        self.assertEqual(rows(result, "support-add")[0]["change"]["group"], 4)
        level = rows(result, "gem-level")[0]
        self.assertIn("trigger", level["flags"])
        self.assertIn("Trigger attack stays at cheapest level", level["vaultRefs"])
        self.assertNotIn("upgrade", level["label"].lower())

    def test_lower_level_and_group_add_edge_cases(self):
        player = snap(groups=[group(1, "Arc", [gem("Arc", level=20)])])
        guide = snap(groups=[group(2, "Arc", [gem("Arc", level=10)]),
                             group(3, "Brand", [gem("Brand", skillPart=2, count=3)]),
                             group(4, "Off", [gem("Off")], enabled=False),
                             group(5, "None", [gem("Support", True)])])
        result = guide_diff.diff(player, guide, None)
        self.assertIn("lower-level", rows(result, "gem-level")[0]["flags"])
        self.assertIn("skill part 2", rows(result, "group-add")[0]["note"])
        reasons = {row["reason"] for row in result["notTested"]}
        self.assertIn("Skill group is switched off in the guide", reasons)
        self.assertIn("Group has no active skill", reasons)

    def test_group_note_exact_and_coc_refs_with_another_trigger(self):
        added = guide_diff.diff(snap(), snap(groups=[group(1, "Brand", [
            gem("Brand", skillPart=2, count=3)])]), None)
        self.assertEqual(rows(added, "group-add")[0]["note"],
                         "Uses the guide's skill part 2 / gem count 3")
        player = snap(groups=[group(1, "Arc", [gem("Arc", level=1),
                                                gem("Cast when Damage Taken", True),
                                                gem("Cast on Critical Strike", True)])])
        guide = snap(groups=[group(1, "Arc", [gem("Arc", level=2),
                                               gem("Cast when Damage Taken", True),
                                               gem("Cast on Critical Strike", True)])])
        refs = rows(guide_diff.diff(player, guide, None), "gem-level")[0]["vaultRefs"]
        self.assertIn("CoC requires 100% crit and hit", refs)

    def test_partial_match_marks_player_group_used(self):
        player = snap(groups=[group(1, "A", [gem("A")]), group(2, "A", [gem("A")])])
        guide = snap(groups=[group(1, "A", [gem("A"), gem("B")]),
                             group(2, "A", [gem("A"), gem("New", True)])])
        result = guide_diff.diff(player, guide, None)
        self.assertTrue(any(value["id"] == "group-add:partial:1" for value in result["notTested"]))
        self.assertEqual(rows(result, "support-add")[0]["change"]["group"], 2)


class ItemDiffTests(unittest.TestCase):
    def test_item_display_names_hide_the_base_for_titled_items(self):
        player_item = item("Weapon 1", "Armageddon Stinger, Imbued Wand",
                           title="Armageddon Stinger", base="Imbued Wand")
        guide_item = item("Weapon 1", "Rune Needle, Prophecy Wand",
                          title="Rune Needle", base="Prophecy Wand")
        found = rows(guide_diff.diff(snap(items=[player_item]),
                                     snap(items=[guide_item]), None), "item")[0]
        self.assertEqual(found["label"], "Replace Armageddon Stinger with Rune Needle in Weapon 1")
        self.assertEqual(found["info"]["fromItem"], "Armageddon Stinger")
        self.assertEqual(found["info"]["toItem"], "Rune Needle")

    def test_item_same_name_other_anoint_is_listed(self):
        player = snap(items=[item("Amulet", "Unique", mods=[])])
        guide = snap(items=[item("Amulet", "Unique", mods=["Allocates Whispers of Doom"])])
        found = rows(guide_diff.diff(player, guide, None), "item")[0]
        self.assertIn("+ Allocates Whispers of Doom", found["note"])

    def test_same_name_differences_and_empty_slot(self):
        cases = [({"variant": "A"}, {"variant": "B"}, "variant"),
                 ({"corrupted": False}, {"corrupted": True}, "corrupted"),
                 ({"raw": "Sockets: R-G"}, {"raw": "Sockets: R-R"}, "sockets"),
                 ({"mods": ["old"]}, {"mods": ["new"]}, "+ new")]
        for before, after, text in cases:
            with self.subTest(text=text):
                player = snap(items=[item("Body Armour", "Coat", **before)])
                guide = snap(items=[item("Body Armour", "Coat", **after)])
                row = rows(guide_diff.diff(player, guide, None), "item")[0]
                self.assertIn(text, row["note"])
                self.assertIn("same-name", row["flags"])
        result = guide_diff.diff(snap(), snap(items=[item("Boots", "Steps")]), None)
        self.assertEqual(rows(result, "item")[0]["label"], "Add Steps in Boots")

    def test_same_name_base_difference_is_explained(self):
        player = snap(items=[item("Body Armour", "Coat", base="Simple Robe")])
        guide = snap(items=[item("Body Armour", "Coat", base="Vaal Regalia")])
        found = rows(guide_diff.diff(player, guide, None), "item")[0]
        self.assertIn("same-name", found["flags"])
        self.assertIn("base", found["note"])

    def test_abyss_metadata_is_ignored_after_whitespace_normalization(self):
        old = item("Belt", "Belt", abyssJewels=[{
            "slot": "Abyssal Socket 1", "name": "Eye", "raw": "  Unique ID: old\n Item Level: 1\n+10 Life"}])
        new = item("Belt", "Belt", abyssJewels=[{
            "slot": "Abyssal Socket 1", "name": "Eye", "raw": "Unique ID: new\nItem Level: 99\n+10 Life"}])
        self.assertFalse(rows(guide_diff.diff(snap(items=[old]), snap(items=[new]), None), "item"))

    def test_equivalent_slots_flask_and_abyss_package(self):
        ring = item("Ring 1", "Loop")
        self.assertFalse(rows(guide_diff.diff(snap(items=[{**ring, "slot": "Ring 2"}]),
                                               snap(items=[ring]), None), "item"))
        flask = item("Flask 1", "Quicksilver", flaskActive=False)
        guide = item("Flask 1", "Granite", flaskActive=True,
                     abyssJewels=[{"slot": "Abyssal Socket 1", "name": "Eye", "raw": "Eye raw"}])
        row = rows(guide_diff.diff(snap(items=[flask]), snap(items=[guide]), None), "flask")[0]
        self.assertEqual(row["change"]["flaskActive"], True)
        self.assertIn("flask-inactive", row["flags"])
        self.assertEqual(row["change"]["abyssJewels"][0]["slot"], "Abyssal Socket 1")

    def test_equal_flask_in_another_inactive_slot_is_equivalent(self):
        player = snap(items=[item("Flask 2", "Granite", flaskActive=False)])
        guide = snap(items=[item("Flask 1", "Granite", flaskActive=True)])
        self.assertFalse(rows(guide_diff.diff(player, guide, None), "flask"))

    def test_equal_inactive_flask_in_own_slot_is_activated_in_place(self):
        player = snap(items=[item("Flask 1", "Granite", flaskActive=False)])
        guide = snap(items=[item("Flask 1", "Granite", flaskActive=True)])
        found = rows(guide_diff.diff(player, guide, None), "flask")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["change"]["slot"], "Flask 1")
        self.assertEqual(found[0]["change"]["flaskActive"], True)

    def test_same_explicitly_inactive_flask_is_identical(self):
        snapshot = snap(items=[item("Flask 1", "Granite", flaskActive=False)])
        result = guide_diff.diff(snapshot, snapshot, None)
        self.assertTrue(result["identical"])
        self.assertFalse(rows(result, "flask"))

    def test_weapon_handedness_cases(self):
        player = snap(items=[item("Weapon 1", "Great Axe")],
                      handedness={"weapon1TwoHanded": True, "weapon2": False})
        guide = snap(items=[item("Weapon 1", "Sword"), item("Weapon 2", "Shield")])
        found = rows(guide_diff.diff(player, guide, None), "item")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["change"]["type"], "compound")
        self.assertIn("handedness", found[0]["flags"])
        player = snap(items=[item("Weapon 1", "Sword"), item("Weapon 2", "Shield")],
                      handedness={"weapon1TwoHanded": False, "weapon2": True})
        guide = snap(items=[item("Weapon 1", "Great Axe")],
                     handedness={"weapon1TwoHanded": True, "weapon2": False})
        row = rows(guide_diff.diff(player, guide, None), "item")[0]
        self.assertIn("removes your Weapon 2", row["note"])


class TreeAndJewelTests(unittest.TestCase):
    def test_f8b_only_masteries_differ(self):
        guide = snap(nodes=[node(12, "Life Mastery", type="Mastery", mastery=3)])
        result = guide_diff.diff(snap(), guide, None)
        self.assertEqual(result["rows"], [])
        self.assertEqual(len(result["notTested"]), 1)
        self.assertEqual(result["found"], 1)
        self.assertFalse(result["identical"])

    def test_zero_impact_node_still_counted(self):
        guide = snap(nodes=[node(22, "Travel")])
        result = guide_diff.diff(snap(), guide, tree_info(**{"22": {"path": [22]}}))
        self.assertEqual(result["found"], 1)
        self.assertEqual(rows(result, "tree-add")[0]["change"]["target"], 22)

    def test_paths_removals_and_missing_info(self):
        player = snap(nodes=[node(9, "Old"), node(8, "Socket")],
                      items=[item("Socket A", "Jewel", socketNode=8)])
        guide = snap(nodes=[node(1, "Target"), node(2, "Other")])
        info = tree_info(**{"1": {"path": [3, 2, 1]}, "9": {"depends": [9, 8]}})
        result = guide_diff.diff(player, guide, info)
        add = next(row for row in rows(result, "tree-add") if row["id"] == "tree-add:1")
        self.assertEqual(add["change"]["nodes"], [3, 2, 1])
        self.assertIn("includes 2 path nodes", add["detail"])
        self.assertIn("Other", add["detail"])
        remove = rows(result, "tree-remove")[0]
        self.assertIn("the jewel in Socket A", remove["detail"])
        missing = guide_diff.diff(snap(), snap(nodes=[node(1)]), None)
        self.assertEqual(missing["notTested"][0]["reason"], "no path to this node")

    def test_also_takes_excludes_nodes_already_allocated(self):
        player = snap(nodes=[node(2, "Already")])
        guide = snap(nodes=[node(1, "Target"), node(2, "Already")])
        result = guide_diff.diff(player, guide, tree_info(**{"1": {"path": [2, 1]}}))
        target = next(row for row in rows(result, "tree-add") if row["id"] == "tree-add:1")
        self.assertEqual(target["info"]["alsoTakes"], [])

    def test_node_classes_mastery_choice_and_no_tree(self):
        classified = [node(1, "Asc", ascendancy="Elementalist"), node(2, "Master", type="Mastery"),
                      node(70000, "Cluster"), node(4, "Sock", socket=True),
                      node(5, "Empty", modKeyEmpty=True), node(6, "Time", conquered=True),
                      node(7, "Start", type="ClassStart")]
        result = guide_diff.diff(snap(nodes=[node(8, "Master", type="Mastery", mastery=1)]),
                                 snap(nodes=[*classified, node(8, "Master", type="Mastery", mastery=2)]), None)
        ids = {row["id"] for row in result["notTested"]}
        self.assertIn("tree-add:ascendancy", ids)
        self.assertIn("tree-add:cluster", ids)
        self.assertIn("tree-add:mastery-choice:8", ids)
        self.assertNotIn("tree-add:7", ids)
        empty = guide_diff.diff(snap(nodes=[node(42)]), snap(), None)
        self.assertTrue(any(b["kind"] == "noTree" for b in empty["banners"]))
        self.assertFalse(rows(empty, "tree-remove"))

    def test_jewels_allocated_unallocated_excluded_and_pair(self):
        player = snap(nodes=[node(10, socket=True)])
        guide = snap(nodes=[node(10, socket=True)], items=[item("Socket X", "Rare Eye", socketNode=10)])
        self.assertEqual(rows(guide_diff.diff(player, guide, None), "jewel")[0]["change"]["type"], "item")
        guide = snap(nodes=[node(11, socket=True)], items=[item("Socket Y", "Rare Eye", socketNode=11)])
        result = guide_diff.diff(snap(), guide, tree_info(**{"11": {"path": [1, 11]}}))
        self.assertEqual(rows(result, "jewel")[0]["change"]["type"], "compound")
        excluded = snap(items=[item("C", "Cluster", socketNode=20, cluster=True),
                               item("T", "Timeless", socketNode=21, timeless=True)])
        self.assertFalse(rows(guide_diff.diff(snap(), excluded, None), "jewel"))
        pair = snap(nodes=[node(30, socket=True), node(31, socket=True)],
                    items=[item("A", "Forbidden Flame, Crimson Jewel", title="Forbidden Flame",
                                base="Crimson Jewel", socketNode=30),
                           item("B", "Forbidden Flesh, Cobalt Jewel", title="Forbidden Flesh",
                                base="Cobalt Jewel", socketNode=31)])
        info = tree_info(**{"30": {"path": [30]}, "31": {"path": [31]}})
        paired = rows(guide_diff.diff(snap(), pair, info), "jewel")
        self.assertEqual(len(paired), 1)
        self.assertIn("paired", paired[0]["flags"])
        missing = guide_diff.diff(snap(), pair, None)
        pair_rows = [value for value in missing["notTested"] if value["id"].startswith("jewel:pair:")]
        self.assertEqual(len(pair_rows), 1)
        self.assertEqual(pair_rows[0]["reason"], "No path to the jewel socket")

    def test_one_sided_pair_notes_and_jewel_socket_candidate(self):
        flame = item("A", "Forbidden Flame, Crimson Jewel", title="Forbidden Flame",
                     base="Crimson Jewel", socketNode=30)
        partner = item("B", "Forbidden Flesh, Cobalt Jewel", title="Forbidden Flesh",
                       base="Cobalt Jewel", socketNode=31)
        guide = snap(nodes=[node(30, socket=True)], items=[flame])
        player = snap(nodes=[node(30, socket=True), node(31, socket=True)], items=[partner])
        present = rows(guide_diff.diff(player, guide, None), "jewel")[0]
        self.assertIn("already in your build", present["note"])
        absent = rows(guide_diff.diff(snap(nodes=[node(30, socket=True)]), guide, None), "jewel")[0]
        self.assertIn("not in the guide", absent["note"])
        candidate_guide = snap(nodes=[node(40, socket=True)],
                               items=[item("C", "Rare Eye", socketNode=40)])
        self.assertEqual(guide_diff.tree_candidates(snap(), candidate_guide)["ids"], [40])

    def test_mod_key_empty_on_tested_path_is_suppressed(self):
        guide = snap(nodes=[node(1, "Target"), node(2, "Empty", modKeyEmpty=True)])
        result = guide_diff.diff(snap(), guide, tree_info(**{"1": {"path": [2, 1]}}))
        self.assertFalse(any(value["id"] == "tree-add:no-stats" for value in result["notTested"]))

    def test_nodes_without_stats_reason_wording(self):
        result = guide_diff.diff(snap(), snap(nodes=[node(5, "Empty", modKeyEmpty=True)]), None)
        found = next(value for value in result["notTested"] if value["id"] == "tree-add:no-stats")
        self.assertTrue(found["label"].startswith("Nodes without stats"))
        self.assertEqual(found["reason"], "Nodes without stats PoB could compare are not tested")


class ConfigBannerContractTests(unittest.TestCase):
    def test_config_labels_remove_pob_colours_and_trailing_colons(self):
        guide = snap(config=[
            {"var": "conditionEnemyChilled", "label": "Is the enemy ^x3F6DB3Chilled?",
             "type": "check", "value": True},
            {"var": "multiplierWitheredStackCount", "label": "# of ^7Withered Stacks:",
             "type": "count", "value": 15},
        ])
        result = guide_diff.diff(snap(), guide, None)
        chilled = next(value for value in result["config"]
                       if value["id"] == "config:conditionEnemyChilled")
        withered = next(value for value in result["config"]
                        if value["id"] == "config:multiplierWitheredStackCount")
        self.assertEqual(chilled["label"], "Is the enemy Chilled?")
        self.assertEqual(chilled["info"]["vars"][0]["label"], "Is the enemy Chilled?")
        self.assertEqual(withered["label"], "# of Withered Stacks")
        self.assertEqual(withered["detail"], "# of Withered Stacks: yours 0; guide 15")

    def test_config_sparse_values_use_pob_defaults(self):
        cases = [({"var": "conditionEnemyShocked", "label": "Shocked", "type": "check", "value": True},
                  "yours off; guide on"),
                 ({"var": "conditionShockEffect", "label": "Effect", "type": "count", "value": 20},
                  "yours 0; guide 20")]
        for entry, detail in cases:
            with self.subTest(var=entry["var"]):
                result = guide_diff.diff(snap(), snap(config=[entry]), None)
                self.assertIn(detail, result["config"][0]["detail"])
                self.assertEqual(result["config"][0]["change"]["vars"][entry["var"]], entry["value"])

    def test_config_absent_matches_explicit_default(self):
        defaults = [{"var": "checked", "label": "Checked", "type": "check", "value": False},
                    {"var": "amount", "label": "Amount", "type": "integer", "value": 0}]
        self.assertEqual(guide_diff.diff(snap(), snap(config=defaults), None)["config"], [])

    def test_config_count_not_in_found(self):
        guide = snap(config=[{"var": "conditionEnemyShocked", "label": "Shocked",
                              "type": "check", "value": True}])
        result = guide_diff.diff(snap(), guide, None)
        self.assertEqual(result["found"], 0)
        self.assertFalse(result["identical"])
        self.assertEqual(len(result["config"]), 1)

    def test_a7_identical_pair(self):
        player = snap(label="Player", items=[item("Boots", "Steps")], groups=[group(1, "Arc")])
        guide = snap(label="Guide", items=[item("Boots", "Steps")], groups=[group(1, "Arc")])
        result = guide_diff.diff(player, guide, None)
        self.assertTrue(result["identical"])
        self.assertEqual(result["found"], 0)
        self.assertEqual((result["rows"], result["notTested"], result["config"]), ([], [], []))

    def test_snapshot_with_null_values(self):
        null_item = item(None, None, base=None, mods=None, abyssJewels=None)
        null_gem = {**gem("Null"), "name": None, "level": None, "quality": None}
        null_group = group(1, gems=[null_gem], slot=None)
        guide = snap(items=[null_item], groups=[null_group],
                     nodes=[node(1, name=None)], level=None)
        player = snap(items=[dict(null_item)], groups=[group(1, gems=[dict(null_gem)], slot=None)],
                      level=None)
        result = guide_diff.diff(player, guide, tree_info(**{"1": {"path": None}}))
        assert_contract(self, result)

    def test_config_groups_text_and_booleans(self):
        player = snap(config=[{"var": "conditionEnemyShocked", "label": "Shocked", "type": "bool", "value": False},
                              {"var": "custom", "label": "Custom", "type": "text", "value": "a"}])
        guide = snap(config=[{"var": "conditionEnemyShocked", "label": "Shocked", "type": "bool", "value": True},
                             {"var": "conditionShockEffect", "label": "Effect", "type": "number", "value": 20},
                             {"var": "custom", "label": "Custom", "type": "text", "value": "b"}])
        result = guide_diff.diff(player, guide, None)
        self.assertEqual(len(result["config"]), 2)
        grouped = result["config"][1] if result["config"][0]["id"] == "config:custom" else result["config"][0]
        self.assertEqual(len(grouped["info"]["vars"]), 2)
        self.assertIn("off", grouped["detail"])
        text = next(row for row in result["config"] if row["id"] == "config:custom")
        self.assertFalse(text["info"]["tested"])
        self.assertIsNone(text["change"])

    def test_banners_and_identity(self):
        base = snap(label="One")
        result = guide_diff.diff(base, {**base, "label": "Two"}, None)
        self.assertTrue(result["identical"])
        self.assertEqual(result["found"], 0)
        sets = {"item": "Gear", "skill": "Links", "spec": "Tree", "multiple": True}
        guide = snap(className="Ranger", ascendancy="Deadeye", mainSkill="Ice Shot",
                     sourceTreeVersion="3_28", sets=sets)
        kinds = [b["kind"] for b in guide_diff.diff(base, guide, None)["banners"]]
        self.assertEqual(kinds[:4], ["class", "mainSkill", "treeVersion", "sets"])
        self.assertIn("noItems", kinds)
        self.assertIn("noTree", kinds)

    def test_schema_nulls_candidates_determinism_and_contract(self):
        for bad in (None, [], {"schema": 2}):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError, "unsupported snapshot schema"):
                    guide_diff.diff(bad, {"schema": 1}, None)
                with self.assertRaisesRegex(ValueError, "unsupported snapshot schema"):
                    guide_diff.tree_candidates(bad, {"schema": 1})
        minimal = guide_diff.diff({"schema": 1}, {"schema": 1}, None)
        self.assertTrue(minimal["identical"])
        player = snap(nodes=[node(9)], groups=[group(1, gems=[gem("Arc", level=None, quality=None)])])
        guide = snap(nodes=[node(2), node(1)], groups=[group(1, gems=[gem("Arc", level=None, quality=None)])])
        candidates = guide_diff.tree_candidates(player, guide)
        self.assertEqual(candidates, {"ids": [1, 2], "removeIds": [9]})
        result = guide_diff.diff(player, guide, None)
        assert_contract(self, result)
        needed = tree_info(**{str(ident): {"path": [ident]} for ident in candidates["ids"]},
                           **{str(ident): {"depends": [ident]} for ident in candidates["removeIds"]})
        resolved = guide_diff.diff(player, guide, needed)
        reasons = {value["reason"].casefold() for value in resolved["notTested"]}
        self.assertFalse(any("no path" in reason or "dependency information" in reason
                             for reason in reasons))
        first = json.dumps(result, sort_keys=True)
        shuffled = guide_diff.diff({**player, "nodes": list(reversed(player["nodes"]))},
                                   {**guide, "nodes": list(reversed(guide["nodes"]))}, None)
        self.assertEqual(first, json.dumps(shuffled, sort_keys=True))

    def test_reversing_nodes_items_and_groups_is_deterministic(self):
        player = snap(nodes=[node(5), node(6)],
                      items=[item("Boots", "Old Boots"), item("Gloves", "Old Gloves")],
                      groups=[group(1, "Arc"), group(2, "Brand")])
        guide = snap(nodes=[node(7), node(8)],
                     items=[item("Boots", "New Boots"), item("Gloves", "New Gloves")],
                     groups=[group(1, "Arc", [gem("Arc"), gem("Added", True)]), group(2, "Brand")])
        original = json.dumps(guide_diff.diff(player, guide, None), sort_keys=True)
        reversed_player = {**player, "nodes": list(reversed(player["nodes"])),
                           "items": list(reversed(player["items"])),
                           "groups": list(reversed(player["groups"]))}
        reversed_guide = {**guide, "nodes": list(reversed(guide["nodes"])),
                          "items": list(reversed(guide["items"])),
                          "groups": list(reversed(guide["groups"]))}
        self.assertEqual(original, json.dumps(guide_diff.diff(reversed_player, reversed_guide, None),
                                              sort_keys=True))
        before_player, before_guide = json.dumps(player, sort_keys=True), json.dumps(guide, sort_keys=True)
        guide_diff.tree_candidates(player, guide)
        guide_diff.diff(player, guide, None)
        self.assertEqual(json.dumps(player, sort_keys=True), before_player)
        self.assertEqual(json.dumps(guide, sort_keys=True), before_guide)


class RealSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = Path(__file__).parent / "fixtures" / "snapshots"
        cls.paths = sorted(directory.glob("*.json")) if directory.is_dir() else []
        if not cls.paths:
            raise unittest.SkipTest("snapshots not recorded yet")
        cls.snapshots = [json.loads(path.read_text(encoding="utf-8")) for path in cls.paths]

    def _load(self, name: str) -> dict:
        path = Path(__file__).parent / "fixtures" / "snapshots" / name
        if not path.is_file():
            self.skipTest(f"snapshot {name} not recorded yet")
        return json.loads(path.read_text(encoding="utf-8"))

    def _tree_info(self, player: dict, guide: dict) -> dict:
        candidates = guide_diff.tree_candidates(player, guide)
        nodes = {str(ident): {"path": [ident]} for ident in candidates["ids"]}
        for ident in candidates["removeIds"]:
            nodes.setdefault(str(ident), {})["depends"] = [ident]
        return {"nodes": nodes}

    def _coc_group(self, snapshot: dict) -> dict:
        return next(group for group in snapshot["groups"] if any(
            str(gem.get("name") or "").casefold().startswith("cast on critical strike")
            for gem in group.get("gems") or []))

    def test_real_identical_pairs(self):
        for name in ("ek_player.json", "worb_player.json", "pobb_guide.json"):
            with self.subTest(name=name):
                player = self._load(name)
                guide = json.loads(json.dumps(player))
                result = guide_diff.diff(player, guide, None)
                self.assertTrue(result["identical"])
                self.assertEqual(result["found"], 0)
                self.assertEqual(result["banners"], [])

    def test_real_t_coc_a_support_swap(self):
        player = self._load("ek_player.json")
        guide = copy.deepcopy(player)
        group = self._coc_group(guide)
        changed = next(gem for gem in group["gems"] if gem.get("isSupport")
                       and not str(gem.get("name") or "").casefold().startswith("cast on critical"))
        changed.update({"name": "Zzz Test Support", "family": "Zzz Test"})
        result = guide_diff.diff(player, guide, None)
        full = len(group["gems"]) >= (group.get("socketLimit") or 6)
        category = "support-replace" if full else "support-add"
        found = [value for value in rows(result, category) if "Zzz Test Support" in value["label"]]
        self.assertEqual(len(found), 1)
        self.assertEqual(result["rows"], found)
        self.assertEqual(result["notTested"], [])
        self.assertFalse(rows(result, "group-add"))
        if full:
            self.assertFalse(rows(result, "support-add"))

    def test_real_t_coc_b_group_support_add(self):
        player = self._load("ek_player.json")
        guide = copy.deepcopy(player)
        coc = self._coc_group(guide)
        candidates = [group for group in guide["groups"] if group is not coc
                      and len(group.get("gems") or []) < (group.get("socketLimit") or 6)]
        self.assertTrue(candidates)
        target = candidates[0]
        target["gems"].append(gem("Zzz Test Support", True, family="Zzz Test"))
        result = guide_diff.diff(player, guide, None)
        found = [value for value in rows(result, "support-add")
                 if "Zzz Test Support" in value["label"]]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["change"]["group"], target["index"])
        self.assertEqual(result["rows"], found)
        self.assertEqual(result["notTested"], [])

    def test_real_t_coc_c_trigger_level(self):
        player = self._load("ek_player.json")
        for delta, expected_flag in ((1, None), (-1, "lower-level")):
            with self.subTest(delta=delta):
                guide = copy.deepcopy(player)
                trigger = next(gem for gem in self._coc_group(guide)["gems"]
                               if str(gem.get("name") or "").casefold().startswith("cast on critical"))
                trigger["level"] += delta
                result = guide_diff.diff(player, guide, None)
                found = rows(result, "gem-level")
                self.assertEqual(len(found), 1)
                self.assertEqual(result["rows"], found)
                self.assertIn("trigger", found[0]["flags"])
                self.assertIn("Trigger attack stays at cheapest level", found[0]["vaultRefs"])
                self.assertNotIn("upgrade", found[0]["label"].casefold())
                self.assertEqual(expected_flag in found[0]["flags"], expected_flag is not None)

    def test_real_worb_part_and_count(self):
        player = self._load("worb_player.json")
        guide = copy.deepcopy(player)
        winter_orb = next(gem for group in guide["groups"] for gem in group.get("gems") or []
                          if gem.get("name") == "Winter Orb")
        winter_orb["count"] = (winter_orb.get("count") or 0) + 1
        result = guide_diff.diff(player, guide, None)
        found = [value for value in result["notTested"]
                 if value.get("reason") == "Skill part or gem count is set by hand and differs"]
        self.assertEqual(len(found), 1)
        self.assertEqual(result["found"], 1)
        self.assertFalse(rows(result, "gem-level"))

    def test_real_pair_of_forbidden_jewels(self):
        player = self._load("worb_player.json")
        guide = self._load("ek_player.json")
        if any((item.get("title") or item.get("name")) in {"Forbidden Flame", "Forbidden Flesh"}
               for item in player.get("items") or []):
            self.skipTest("worb snapshot already has Forbidden Flame or Forbidden Flesh")
        result = guide_diff.diff(player, guide, self._tree_info(player, guide))
        found = [value for value in result["rows"]
                 if value["id"].startswith("jewel:pair:Forbidden Flame+Forbidden Flesh")]
        self.assertEqual(len(found), 1)
        self.assertIn("paired", found[0]["flags"])
        self.assertEqual(found[0]["change"]["type"], "compound")

    def test_real_ek_vs_pobb_runs(self):
        player = self._load("ek_player.json")
        guide = self._load("pobb_guide.json")
        info = self._tree_info(player, guide)
        first = guide_diff.diff(player, guide, info)
        second = guide_diff.diff(player, guide, info)
        self.assertEqual(first["found"], len(first["rows"]) + len(first["notTested"]))
        assert_contract(self, first)
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(second, sort_keys=True))
        titled = [item for item in guide.get("items") or [] if item.get("title")]
        for found in first["rows"] + first["notTested"]:
            if found["category"] not in {"item", "flask", "jewel"}:
                continue
            for item in titled:
                if item["name"] in found["label"] or item["title"] in found["label"]:
                    self.assertIn(item["title"], found["label"])
                    self.assertNotIn(item["name"], found["label"])
        self.assertTrue(all("^x" not in value["label"] for value in first["config"]))

    def test_self_diff_and_pairwise_determinism(self):
        for snapshot in self.snapshots:
            with self.subTest(label=snapshot.get("label")):
                result = guide_diff.diff(snapshot, snapshot, None)
                self.assertTrue(result["identical"])
                self.assertEqual(result["found"], 0)
        for left in self.snapshots:
            for right in self.snapshots:
                with self.subTest(left=left.get("label"), right=right.get("label")):
                    one = guide_diff.diff(left, right, None)
                    two = guide_diff.diff(left, right, None)
                    self.assertEqual(json.dumps(one, sort_keys=True), json.dumps(two, sort_keys=True))
                    assert_contract(self, one)
                    candidates = guide_diff.tree_candidates(left, right)
                    nodes = {str(ident): {"path": [ident]} for ident in candidates["ids"]}
                    for ident in candidates["removeIds"]:
                        nodes.setdefault(str(ident), {})["depends"] = [ident]
                    info = {"nodes": nodes}
                    with_info = guide_diff.diff(left, right, info)
                    repeated = guide_diff.diff(left, right, info)
                    assert_contract(self, with_info)
                    self.assertEqual(json.dumps(with_info, sort_keys=True),
                                     json.dumps(repeated, sort_keys=True))

    def test_granted_skill_groups_are_not_add_skill_rows(self):
        """GATE 2 M1: a skill the guide gets from a passive node or an item has no gems to socket (EK: Assassin's Mark)."""
        ek, worb = self._load("ek_player.json"), self._load("worb_player.json")
        for player, guide, wanted in ((worb, ek, "Assassin"), (ek, worb, "Brine King")):
            found = guide_diff.diff(player, guide, None)
            granted = [row for row in found["notTested"] if row["id"].startswith("group-add:granted:")]
            self.assertTrue(any(wanted in row["label"] for row in granted), wanted)
            self.assertFalse(any(wanted in row["label"] for row in found["rows"]), wanted)
            self.assertEqual(found["found"], len(found["rows"]) + len(found["notTested"]))

    def test_support_add_rows_carry_socket_limit_and_free_sockets(self):
        player, guide = self._load("ek_player.json"), self._load("pobb_guide.json")
        adds = [row for row in guide_diff.diff(player, guide, None)["rows"] if row["category"] == "support-add"]
        self.assertTrue(adds)
        for row in adds:
            change = row["change"]
            self.assertEqual(change["freeSockets"], row["info"]["freeSockets"])
            self.assertGreaterEqual(change["socketLimit"] - change["freeSockets"], 1)


if __name__ == "__main__":
    unittest.main()
