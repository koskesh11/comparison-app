"""Guide apply planning tests and slow real-Path-of-Building integration tests."""

import json
import importlib.util
import math
import os
import shutil
import sys
import tempfile
import threading
import unittest
from itertools import combinations
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parent
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(TESTS_DIR))

from api_errors import InvalidRequest  # noqa: E402
import guide_apply  # noqa: E402
import guide_diff  # noqa: E402
import guide_lua  # noqa: E402
import guide_routes  # noqa: E402
import engine_pool  # noqa: E402
import pobbin  # noqa: E402
import audit  # noqa: E402
import golden_common as gc  # noqa: E402


SETTINGS = {"includeDrafts": True, "disabledSkills": [], "scenario": "Pinnacle Boss"}


def fixture_report() -> dict:
    folder = TESTS_DIR / "fixtures" / "snapshots"
    player = json.loads((folder / "ek_player.json").read_text(encoding="utf-8"))
    guide = json.loads((folder / "pobb_guide.json").read_text(encoding="utf-8"))
    found = guide_diff.diff(player, guide, None)
    rows = [{**row, "locked": False} for row in found["rows"]]
    return {"rows": rows, "noChange": [], "config": found["config"],
            "notTested": found["notTested"]}


class GuideLuaRequestTests(unittest.TestCase):
    def test_apply_changes_optional_request_fields(self):
        with mock.patch.object(guide_lua, "_call", return_value={}) as call:
            guide_lua.apply_changes(object(), [], ["FullDPS"], "Build",
                                    extra_skills=[{"group": 1}], save=False)
        self.assertEqual(call.call_args.args[2], {
            "changes": [], "stats": ["FullDPS"], "buildName": "Build",
            "extraSkills": [{"group": 1}], "save": False,
        })


class GuideApplyPureTests(unittest.TestCase):
    def test_combined_maps_non_finite_numbers_to_none(self):
        base = {"dps": math.nan, "ehp": 0, "manaMargin": None, "maxHit": 0}
        after = {"dps": 1, "ehp": 0, "manaMargin": 2, "maxHit": 0}
        result = guide_apply._combined(base, after)
        self.assertIsNone(result["delta"]["dpsPct"])
        self.assertIsNone(result["delta"]["manaMargin"])

    def test_plan_changes_flattens_orders_and_deduplicates_paths(self):
        rows = [
            {"id": "compound", "change": {"type": "compound", "changes": [
                {"type": "item", "slot": "Weapon 2"},
                {"type": "alloc", "target": 9, "nodes": [7, 8, 9]},
            ]}},
            {"id": "weapon1", "change": {"type": "item", "slot": "Weapon 1"}},
            {"id": "short-alloc", "change": {"type": "alloc", "target": 8, "nodes": [8]}},
            {"id": "short-remove", "change": {"type": "dealloc", "target": 2, "nodes": [2]}},
            {"id": "long-remove", "change": {"type": "dealloc", "target": 3, "nodes": [1, 2, 3]}},
            {"id": "level", "change": {"type": "gemLevel"}},
            {"id": "replace", "change": {"type": "replaceSupport"}},
            {"id": "support", "change": {"type": "addSupport"}},
            {"id": "group", "change": {"type": "addGroup"}},
        ]
        planned = guide_apply.plan_changes(rows)
        # a removal is ticked: PoB re-paths every add after it, so a path covered by another is still kept (GATE 2 H2)
        self.assertEqual([change["type"] for change in planned],
                         ["dealloc", "alloc", "alloc", "item", "item", "gemLevel",
                          "replaceSupport", "addSupport", "addGroup"])
        self.assertEqual(planned[0]["target"], 3)
        self.assertEqual([change["target"] for change in planned[1:3]], [9, 8])
        self.assertTrue(all(change["afterRemoval"] for change in planned[1:3]))
        self.assertEqual([[1, 2, 3]] * 2, [change["removedNodes"] for change in planned[1:3]])
        self.assertEqual([change["slot"] for change in planned[3:5]], ["Weapon 1", "Weapon 2"])

    def test_plan_changes_without_a_removal_keeps_stored_paths_and_deduplicates(self):
        rows = [
            {"id": "long", "change": {"type": "alloc", "target": 9, "nodes": [7, 8, 9]}},
            {"id": "short", "change": {"type": "alloc", "target": 8, "nodes": [8]}},
        ]
        planned = guide_apply.plan_changes(rows)
        self.assertEqual([change["target"] for change in planned], [9])
        self.assertNotIn("afterRemoval", planned[0])

    def test_resolve_ticks_returns_report_order_and_merges_duplicates(self):
        report = fixture_report()
        first, second = report["rows"][:2]
        resolved = guide_apply.resolve_ticks(report, [second["id"], first["id"], second["id"]])
        self.assertEqual([row["id"] for row in resolved], [first["id"], second["id"]])

    def test_resolve_ticks_refusals(self):
        report = fixture_report()
        locked = {**report["rows"][0], "id": "locked:test", "label": "Locked row",
                  "locked": True, "lockReason": "blocked by PoB"}
        report["rows"].append(locked)
        cases = [
            ([report["config"][0]["id"]], "settings the guide assumes are never applied"),
            ([report["notTested"][0]["id"]], "not tested, so it can't be applied"),
            ([locked["id"]], "Locked row: blocked by PoB"),
            (["missing"], "unknown"),
            ([], "empty"),
            ([str(index) for index in range(501)], "500"),
            ([1], "string"),
            (["x" * 201], "200"),
        ]
        for ids, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(InvalidRequest, message):
                guide_apply.resolve_ticks(report, ids)

    def test_conflicts_have_row_ids_and_address_first_row(self):
        cases = [
            ({"type": "item", "slot": "Weapon 1"},
             {"type": "item", "slot": "Weapon 1"}, "same slot"),
            ({"type": "addGroup", "gems": [{"name": "Skill", "isSupport": False}]},
             {"type": "addGroup", "gems": [{"name": "Skill", "isSupport": False}]}, "same skill"),
            ({"type": "gemLevel", "group": 1, "gemIndex": 1, "name": "Gem"},
             {"type": "replaceSupport", "group": 1, "gemIndex": 1,
              "replaced": "Old", "gem": {"name": "New"}}, "same gem"),
            ({"type": "alloc", "nodes": [1]},
             {"type": "dealloc", "nodes": [1]}, "one adds and one removes the same passive nodes"),
        ]
        for left, right, reason in cases:
            rows = [{"id": "a", "label": "First", "change": left},
                    {"id": "b", "label": "Second", "change": right}]
            with self.subTest(reason=reason):
                self.assertEqual(guide_apply.conflicts(rows), [{
                    "ids": ["a", "b"], "message": f"Can't combine with Second ({reason}).",
                }])

    def test_not_applied_counts_distinct_locked_categories(self):
        report = fixture_report()
        report["rows"] = [
            {"id": "open", "locked": False, "chips": []},
            {"id": "unobtainable", "locked": True, "chips": ["unobtainable"]},
            {"id": "locked", "locked": True, "chips": ["breaks a rule"]},
        ]
        report["noChange"] = [{"id": "no-change", "locked": False, "chips": []}]
        result = guide_apply.not_applied(report, ["open"])
        self.assertEqual(result, {"config": len(report["config"]),
                                  "notTested": len(report["notTested"]),
                                  "unobtainable": 1, "locked": 1, "unticked": 1,
                                  "total": len(report["config"]) + len(report["notTested"]) + 3})


def builds_listing() -> list[tuple[str, int, int]]:
    return [(str(path.relative_to(gc.BUILDS_DIR)), path.stat().st_size, path.stat().st_mtime_ns)
            for path in sorted(gc.BUILDS_DIR.rglob("*")) if path.is_file()]


class GuideApplyIntegrationTests(unittest.TestCase):
    """Slow tests using one real Path of Building engine for the class."""

    @classmethod
    def setUpClass(cls):
        cls.saved_cwd = os.getcwd()
        cls.install_before = gc.install_snapshot()
        cls.temp = tempfile.TemporaryDirectory()
        root = Path(cls.temp.name)
        cls.ek_path = root / "CoC EK Assa.xml"
        cls.vfos_path = root / "VFoS Berserker.xml"
        shutil.copyfile(gc.BUILDS_DIR / "3.29/Ninja Builds/CoC EK Assa.xml", cls.ek_path)
        shutil.copyfile(gc.BUILDS_DIR / "3.26/VFoS Berserker.xml", cls.vfos_path)
        cls.player_bytes = cls.ek_path.read_bytes()
        cls.vfos_bytes = cls.vfos_path.read_bytes()
        cls.cwd = gc.pob_cwd()
        cls.cwd.__enter__()
        cls.auditor = gc.offline_auditor(cls.ek_path, SETTINGS)
        fixtures = TESTS_DIR / "fixtures" / "snapshots"
        cls.player = json.loads((fixtures / "ek_player.json").read_text(encoding="utf-8"))
        cls.guide = json.loads((fixtures / "pobb_guide.json").read_text(encoding="utf-8"))
        candidates = guide_diff.tree_candidates(cls.player, cls.guide)
        cls.auditor.engine.load_build(cls.ek_path)
        guide_lua.ensure_loaded(cls.auditor.engine)
        info = guide_lua.tree_info(cls.auditor.engine, candidates["ids"], candidates["removeIds"])
        found = guide_diff.diff(cls.player, cls.guide, info)
        cls.report = {"rows": [{**row, "locked": False, "chips": []} for row in found["rows"]],
                      "noChange": [], "config": found["config"], "notTested": found["notTested"]}

    @classmethod
    def tearDownClass(cls):
        gc.close_engine(cls.auditor.engine)
        cls.cwd.__exit__(None, None, None)
        os.chdir(cls.saved_cwd)
        cls.temp.cleanup()
        changed = [line for line in gc.install_diff(cls.install_before, gc.install_snapshot())
                   if "Data\\TimelessJewelData\\" not in line]
        assert changed == [], changed

    def setUp(self):
        self.builds_before = builds_listing()
        self.out_dir = Path(self.temp.name) / self._testMethodName
        self.addCleanup(self.assert_external_files_unchanged)

    def assert_external_files_unchanged(self):
        self.assertEqual(self.player_bytes, self.ek_path.read_bytes())
        self.assertEqual(self.vfos_bytes, self.vfos_path.read_bytes())
        self.assertEqual(self.builds_before, builds_listing())

    def _small_tree_and_item(self) -> list[dict]:
        free = self.player["points"]["available"] - self.player["points"]["used"]
        trees = [row for row in self.report["rows"] if row["category"] == "tree-add"
                 and len(row["change"]["nodes"]) <= free]
        item = next(row for row in self.report["rows"] if row["category"] == "item")
        return [min(trees, key=lambda row: len(row["change"]["nodes"])), item]

    def test_predict_save_reload_and_never_overwrite(self):
        rows = self._small_tree_and_item()
        with mock.patch.object(audit.Obtainability, "load", side_effect=AssertionError("network")):
            predicted = guide_apply.predict(self.auditor, rows)
            first = guide_apply.save(self.auditor, rows, self.out_dir)
            second = guide_apply.save(self.auditor, rows, self.out_dir)
        self.assertTrue(predicted["ok"] and first["saved"] and second["saved"])
        self.assertEqual(predicted["combined"], first["combined"])
        self.assertEqual(first["reload"], {"checked": True, "equal": True, "diffs": [], "error": None})
        self.assertTrue(Path(first["path"]).is_file())
        self.assertEqual(Path(second["path"]).name, "CoC EK Assa (guide check 2).xml")

    def test_point_budget_refuses_without_writing(self):
        rows = [row for row in self.report["rows"] if row["category"] == "tree-add"]
        result = guide_apply.save(self.auditor, rows, self.out_dir)
        self.assertEqual(result["refused"]["reason"], "budget")
        needs = result["points"]["needs"]
        self.assertEqual(result["refused"]["message"],
                         f"needs {needs} more points; also tick a removal")
        self.assertFalse(result["saved"])
        self.assertFalse(self.out_dir.exists())

    def _vfos_auditor(self):
        return gc.offline_auditor(self.vfos_path, SETTINGS, engine=self.auditor.engine)

    def test_two_handed_player_accepts_handedness_compound(self):
        vfos = self._vfos_auditor()
        vfos.engine.load_build(self.vfos_path)
        vfos.load_audit_hooks([])
        player = guide_lua.snapshot(vfos.engine, "player")
        found = guide_diff.diff(player, self.player, None)
        row = next({**value, "locked": False} for value in found["rows"]
                   if value["change"]["type"] == "compound" and "handedness" in value["flags"])
        predicted = guide_apply.predict(vfos, [row])
        # This real build already breaks the Int requirement (short by 121); the pair makes it 125 (GATE 2 H4).
        self.assertEqual(predicted["refused"]["reason"], "rule")
        self.assertIn("already broken in your build and made worse", predicted["refused"]["message"])
        saved = guide_apply.save(vfos, [row], self.out_dir, force=True)
        self.assertTrue(saved["saved"])
        self.assertEqual(predicted["combined"], saved["combined"])
        self.assertTrue(saved["reload"]["equal"], saved["reload"])

    def test_two_handed_player_refuses_offhand_only(self):
        vfos = self._vfos_auditor()
        shield = next(item for item in self.player["items"] if item["slot"] == "Weapon 2")
        row = {"id": "offhand", "label": "Offhand only", "change": {
            "type": "item", "slot": "Weapon 2", "raw": shield["raw"]}}
        result = guide_apply.save(vfos, [row], self.out_dir)
        self.assertEqual(result["refused"]["reason"], "pob")
        self.assertFalse(result["saved"])
        self.assertFalse(self.out_dir.exists())

    def test_two_handed_mainhand_clears_offhand_and_reloads(self):
        self.auditor.engine.load_build(self.vfos_path)
        guide_lua.ensure_loaded(self.auditor.engine)
        axe = next(item for item in guide_lua.snapshot(self.auditor.engine, "player")["items"]
                   if item["slot"] == "Weapon 1")
        row = {"id": "axe", "label": "Two-handed axe", "change": {
            "type": "item", "slot": "Weapon 1", "raw": axe["raw"]}}
        # PoB accepts the two-handed mainhand and clears Weapon 2 as part of the item mutation.
        predicted = guide_apply.predict(self.auditor, [row])
        saved = guide_apply.save(self.auditor, [row], self.out_dir, force=True)
        self.assertEqual(predicted["refused"]["reason"], "rule")
        self.assertTrue(saved["saved"])
        self.assertEqual(predicted["combined"], saved["combined"])
        self.assertTrue(saved["reload"]["equal"], saved["reload"])


@unittest.skipUnless(importlib.util.find_spec("guide_check"), "engine/guide_check.py not present yet")
class GuideCheckIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved_cwd = os.getcwd()
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.player = cls.root / "CoC EK Assa.xml"
        shutil.copyfile(gc.BUILDS_DIR / "3.29/Ninja Builds/CoC EK Assa.xml", cls.player)
        code = (TESTS_DIR / "fixtures" / "pobb_F8CiRC9KVADl.code.txt").read_text(encoding="utf-8")
        cls.guide = cls.root / "guide.xml"
        cls.guide.write_text(pobbin.decode(code), encoding="utf-8")
        cls.cwd = gc.pob_cwd()
        cls.cwd.__enter__()
        cls.pool = engine_pool.EnginePool(size=1)

    @classmethod
    def tearDownClass(cls):
        cls.pool.close()
        cls.cwd.__exit__(None, None, None)
        os.chdir(cls.saved_cwd)
        cls.temp.cleanup()

    def test_job_preview_and_apply_reload(self):
        settings = {"includeDrafts": True, "leaveOut": [], "scenario": "Pinnacle Boss"}
        job = guide_routes._new_job("j", "CoC EK Assa.xml", settings)
        state = SimpleNamespace(
            jobs={"j": job}, pool=self.pool, engine_lock=threading.Lock(), Auditor=audit.Auditor,
            BUILDS_DIR=self.root, DEFAULT_OUT_DIR=self.root / "out", guide_capability=None,
        )
        imported = {"id": "F8CiRC9KVADl", "path": str(self.guide)}
        spec = {"playerPath": self.player, "guideLink": "pobb.in/F8CiRC9KVADl",
                "build": "CoC EK Assa.xml", "settings": settings}
        with mock.patch.object(pobbin, "import_link", return_value=imported), \
                mock.patch.object(audit.Obtainability, "load",
                                  return_value=gc.offline_obtainability()):
            guide_routes.run_guide_job(state, "j", spec)
        self.assertEqual(job["status"], "done", job.get("error"))
        self.assertTrue(job["report"]["rows"])
        pair = self._accepted_pair(state, job)
        with mock.patch.object(audit.Obtainability, "load", side_effect=AssertionError("network")), \
                mock.patch.object(guide_routes.build_settings, "update"):
            previewed = guide_routes.preview(state, {"jobId": "j", "ids": pair})
            applied = guide_routes.apply(state, {"jobId": "j", "ids": pair, "force": True})
        self.assertEqual(previewed["combined"], applied["combined"])
        self.assertTrue(applied["saved"], applied)
        self.assertTrue(applied["reload"]["equal"], applied["reload"])

    @staticmethod
    def _accepted_pair(state, job):
        rows = [row for row in job["report"]["rows"] if not row.get("locked")]
        for left, right in combinations(rows, 2):
            if guide_apply.conflicts([left, right]):
                continue
            ids = [left["id"], right["id"]]
            result = guide_routes.preview(state, {"jobId": "j", "ids": ids})
            if not result["refused"] or result["refused"]["reason"] == "rule":
                return ids
        raise AssertionError("no applicable non-conflicting pair")


if __name__ == "__main__":
    unittest.main()
