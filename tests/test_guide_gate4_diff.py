"""GATE 4 regressions for passive overrides and mixed-active socket groups."""

from __future__ import annotations

import json
import shutil
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
ENGINE_DIR = TESTS_DIR.parent / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

import guide_apply  # noqa: E402
import guide_diff  # noqa: E402
from guide_diff_common import OVERRIDE_REASON, classify_node  # noqa: E402
from guide_diff_tree import _alloc_row, _remove_row  # noqa: E402
from guide_lua import ensure_loaded, snapshot  # noqa: E402
from pobhost import PobEngine  # noqa: E402
from tests import golden_common as gc  # noqa: E402
from tests import guide_check_testlib as helpers  # noqa: E402


SNAPSHOTS = TESTS_DIR / "fixtures" / "snapshots"


def _load(name: str) -> dict:
    return json.loads((SNAPSHOTS / name).read_text(encoding="utf-8"))


def _tree_info(player: dict, guide: dict) -> dict:
    candidates = guide_diff.tree_candidates(player, guide)
    nodes = {str(ident): {"path": [ident]} for ident in candidates["ids"]}
    for ident in candidates["removeIds"]:
        nodes.setdefault(str(ident), {})["depends"] = [ident]
    return {"nodes": nodes}


def _node_map(snapshot_value: dict) -> dict[int, dict]:
    return {node["id"]: node for node in snapshot_value["nodes"]}


def _real_diff() -> tuple[dict, dict, dict]:
    player, guide = _load("ek_player.json"), _load("pobb_guide.json")
    return player, guide, guide_diff.diff(player, guide, _tree_info(player, guide))


def _touched_nodes(row: dict) -> set[int]:
    change = row.get("change") or {}
    found = {value for value in change.get("nodes") or [] if isinstance(value, int)}
    if isinstance(change.get("target"), int):
        found.add(change["target"])
    found.update(touch["key"] for touch in row.get("touches") or []
                 if touch.get("kind") == "node" and isinstance(touch.get("key"), int))
    return found


class RealSnapshotOverrideTests(unittest.TestCase):
    def test_guide_overrides_are_all_untested(self):
        player, guide, result = _real_diff()
        tested = result["rows"]
        self.assertFalse(any("Tattoo" in row["label"] or "Runegraft" in row["label"]
                             for row in tested))
        players = _node_map(player)
        guide_only = [node for node in guide["nodes"]
                      if isinstance(node.get("override"), dict) and node["id"] not in players]
        hinekora_or_valako = [node for node in guide_only
                              if any(name in node["override"]["name"]
                                     for name in ("Hinekora", "Valako"))]
        self.assertGreaterEqual(len(hinekora_or_valako), 14)
        untested = {row["id"]: row for row in result["notTested"]}
        for node in guide_only:
            with self.subTest(node=node["id"]):
                found = untested[f"tree-add:{node['id']}"]
                self.assertIn(node["override"]["name"], found["label"])
                self.assertEqual(found["reason"], OVERRIDE_REASON)
        runegraft = untested["tree-add:30393"]
        self.assertIn("Take Runegraft of Gemcraft", runegraft["label"])
        self.assertEqual(runegraft["reason"], OVERRIDE_REASON)

    def test_both_side_override_difference_and_tested_touch_guard(self):
        _, guide, result = _real_diff()
        found = next(row for row in result["notTested"]
                     if row["id"] == "tree-add:override:5296")
        self.assertEqual(found["reason"], OVERRIDE_REASON)
        self.assertIn("Tattoo of the Hinekora Warrior", found["label"])
        self.assertIn("Intelligence", found["label"])
        override_ids = {node["id"] for node in guide["nodes"]
                        if isinstance(node.get("override"), dict)}
        self.assertFalse(any(_touched_nodes(row) & override_ids for row in result["rows"]))

    def test_override_on_allocation_path_is_untested(self):
        player, guide = _load("ek_player.json"), _load("pobb_guide.json")
        players = _node_map(player)
        override = next(node for node in guide["nodes"]
                        if isinstance(node.get("override"), dict) and node["id"] not in players)
        info = _tree_info(player, guide)
        target = next(node["id"] for node in guide["nodes"]
                      if node["id"] not in players and classify_node(node) == "testable")
        info["nodes"][str(target)]["path"] = [override["id"], target]
        result = guide_diff.diff(player, guide, info)
        found = next(row for row in result["notTested"] if row["id"] == f"tree-add:{target}")
        self.assertEqual(found["reason"], OVERRIDE_REASON)
        self.assertIn(override["override"]["name"], found["detail"])

    def test_player_only_override_in_removal_dependencies_is_untested(self):
        player, guide = _load("pobb_guide.json"), _load("ek_player.json")
        guides = _node_map(guide)
        override = next(node for node in player["nodes"]
                        if isinstance(node.get("override"), dict) and node["id"] not in guides)
        info = _tree_info(player, guide)
        target = guide_diff.tree_candidates(player, guide)["removeIds"][0]
        info["nodes"][str(target)]["depends"] = [target, override["id"]]
        result = guide_diff.diff(player, guide, info)
        found = next(row for row in result["notTested"]
                     if row["id"] == f"tree-remove:{target}")
        self.assertEqual(found["reason"], OVERRIDE_REASON)

    def test_conquered_override_still_guards_paths_and_dependencies(self):
        player, guide = _load("ek_player.json"), _load("pobb_guide.json")
        guides = _node_map(guide)
        override = next(node for node in guide["nodes"]
                        if isinstance(node.get("override"), dict) and node["conquered"])
        target = next(node for node in guide["nodes"] if classify_node(node) == "testable")
        path_info = {"nodes": {str(target["id"]): {"path": [override["id"], target["id"]]}}}
        added, covered = _alloc_row(target["id"], target, guides,
                                    {override["id"], target["id"]}, path_info)
        self.assertEqual(added.get("reason"), OVERRIDE_REASON)
        self.assertEqual(covered, set())
        depends_info = {"nodes": {str(target["id"]):
                                   {"depends": [target["id"], override["id"]]}}}
        removed, covered = _remove_row(target["id"], target, guides, player, depends_info)
        self.assertEqual(removed.get("reason"), OVERRIDE_REASON)
        self.assertEqual(covered, set())

    def test_mixed_active_groups_use_support_and_missing_skill_rows(self):
        _, _, result = _real_diff()
        missing = {row["id"]: row for row in result["notTested"]}
        forbidden = missing["group-add:missing:1:Forbidden Rite of Soul Sacrifice"]
        discipline = missing["group-add:missing:4:Discipline"]
        self.assertEqual(forbidden["reason"],
                         "you don't have Forbidden Rite of Soul Sacrifice in that group")
        self.assertEqual(discipline["reason"], "you don't have Discipline in that group")
        related = [row for row in result["rows"]
                   if row["id"].startswith(("support-", "gem-level"))
                   and (":1:" in row["id"] or "Group 1" in row["label"])]
        self.assertTrue(related)
        all_rows = result["rows"] + result["notTested"]
        self.assertFalse(any(row["id"].startswith("group-add:partial:") for row in all_rows))
        self.assertFalse(any("mixes skills" in row.get("reason", "") for row in all_rows))
        group_adds = [row for row in result["rows"] if row["category"] == "group-add"]
        self.assertFalse(any("Cyclone" in row["id"].removeprefix("group-add:")
                             for row in group_adds))

    def test_guide_jewel_over_player_cluster_jewel_is_not_tested(self):
        """H4: the test keeps the cluster passives, apply removes them, so the row must not be tickable."""
        _, _, result = _real_diff()
        found = next(row for row in result["notTested"] if row["id"] == "jewel:Jewel 9408")
        self.assertEqual("Replace Behemoth Bliss with Melding of the Flesh in Jewel 9408", found["label"])
        self.assertIn("Repeater", found["detail"])
        self.assertIn("Aerodynamics", found["detail"])
        self.assertIn("cluster jewel's passives", found["reason"])
        self.assertFalse(any(row["id"] == "jewel:Jewel 9408" for row in result["rows"]))
        ranked = {row["id"] for row in result["rows"]}
        self.assertTrue({"jewel:Jewel 59585", "jewel:Jewel 26196"} <= ranked | {
            row["id"] for row in result["notTested"]})
        self.assertIn("jewel:Jewel 59585", ranked)
        with self.assertRaisesRegex(Exception, "not tested, so it can't be applied"):
            guide_apply.resolve_ticks({"rows": result["rows"], "noChange": [],
                                       "notTested": result["notTested"], "config": []},
                                      ["jewel:Jewel 9408"])

    def test_guide_jewel_over_player_timeless_jewel_is_not_tested(self):
        player, guide = _load("ek_player.json"), _load("pobb_guide.json")
        timeless = next(item for item in player["items"] if item.get("timeless"))
        watcher = next(item for item in guide["items"] if "Watcher's Eye" in item["name"])
        moved = {**watcher, "socketNode": timeless["socketNode"], "slot": timeless["slot"]}
        guide = {**guide, "items": [item for item in guide["items"]
                                    if item.get("slot") != timeless["slot"]] + [moved]}
        result = guide_diff.diff(player, guide, _tree_info(player, guide))
        found = next(row for row in result["notTested"] if row["id"] == f"jewel:{timeless['slot']}")
        self.assertIn("Militant Faith", found["label"])
        self.assertIn("timeless jewel", found["reason"])
        self.assertFalse(any(row["id"] == found["id"] for row in result["rows"]))

    def test_snapshot_cluster_nodes_name_their_socket(self):
        player = _load("ek_player.json")
        by_id = _node_map(player)
        self.assertEqual(9408, by_id[66578]["socketNode"])  # Repeater of Behemoth Bliss
        self.assertEqual(7960, by_id[9408]["socketNode"])   # a medium cluster sits in a large one


    def test_override_row_cannot_be_applied(self):
        _, _, result = _real_diff()
        report = {"rows": result["rows"], "noChange": [],
                  "notTested": result["notTested"], "config": result["config"]}
        with self.assertRaisesRegex(Exception, "not tested, so it can't be applied"):
            guide_apply.resolve_ticks(report, ["tree-add:30393"])


class RealPobOverrideTests(helpers.PobGuardedTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.player_fixture, cls.guide_fixture = _load("ek_player.json"), _load("pobb_guide.json")
        players, guides = _node_map(cls.player_fixture), _node_map(cls.guide_fixture)
        cls.node_id = next(ident for ident in sorted(set(players) & set(guides))
                           if players[ident]["type"] == "Normal"
                           and guides[ident]["type"] == "Normal"
                           and players[ident].get("override") is None
                           and guides[ident].get("override") is None
                           and not any(players[ident].get(key) for key in
                                       ("socket", "cluster", "conquered", "ascendancy")))
        source = gc.build_path(gc.AUDIT_BUILDS["EK"]["file"])
        text = source.read_text(encoding="utf-8")
        marker = "<Overrides/>"
        if text.count(marker) != 1:
            raise AssertionError("expected one empty Overrides element")
        override = (f'<Overrides><Override dn="Tattoo of the Hinekora Warrior" '
                    f'icon="Art/2DArt/SkillIcons/passives/energyshield.png" nodeId="{cls.node_id}" '
                    'activeEffectImage="Art/2DArt/UIImages/InGame/AncestralTrial/'
                    'PassiveTreeTattoos/HinekoraTribePassiveBG.png">\n'
                    '3% increased maximum Energy Shield\n</Override></Overrides>')
        cls.temp = helpers.temp_dir()
        cls.path = cls.temp / "tattoo.xml"
        cls.path.write_text(text.replace(marker, override), encoding="utf-8", newline="\n")
        cls.cwd = gc.pob_cwd()
        cls.cwd.__enter__()
        cls.engine = PobEngine()
        cls.engine.load_build(cls.path)
        ensure_loaded(cls.engine)
        cls.modified = snapshot(cls.engine, "player")

    @classmethod
    def tearDownClass(cls):
        try:
            if hasattr(cls, "engine"):
                gc.close_engine(cls.engine)
            if hasattr(cls, "cwd"):
                cls.cwd.__exit__(None, None, None)
            if hasattr(cls, "temp"):
                shutil.rmtree(cls.temp)
        finally:
            super().tearDownClass()

    def test_real_pob_snapshot_and_diff_preserve_override(self):
        node = _node_map(self.modified)[self.node_id]
        self.assertEqual(node["override"]["name"], "Tattoo of the Hinekora Warrior")
        result = guide_diff.diff(self.modified, self.guide_fixture, None)
        found = next(row for row in result["notTested"]
                     if row["id"] == f"tree-add:override:{self.node_id}")
        self.assertTrue(found["label"].startswith("Tattoo or runegraft on"))
        self.assertIn("yours Tattoo of the Hinekora Warrior", found["label"])


if __name__ == "__main__":
    unittest.main()
