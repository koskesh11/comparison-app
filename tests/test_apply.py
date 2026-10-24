"""Integration tests for safely applying audited build changes."""

import hashlib
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden_common as gc  # noqa: E402

import audit  # noqa: E402
import optimize  # noqa: E402


class ConflictTableTests(unittest.TestCase):
    def assert_conflict(self, changes, message, kind=None):
        with self.assertRaisesRegex(optimize.ChangeError, f"^{message}$"):
            optimize.check_conflicts(changes)
        if kind is not None:
            self.assertEqual(optimize.conflict_pairs(list(enumerate(changes)))[0]["kind"], kind)

    def test_table_driven_conflicts(self):
        cases = [
            ([{"type": "item", "slot": "Weapon 1"},
              {"type": "item", "slot": "Weapon 1"}],
             "several changes use the same slot: Weapon 1", "slot"),
            ([{"type": "item", "slot": "Weapon 1"},
              {"type": "compound", "changes": [{"type": "item", "slot": "Body Armour",
                                                   "abyssJewels": [{"slot": "Weapon 1"}]}]}],
             "several changes use the same slot: Weapon 1", "slot"),
            ([{"type": "addGroup", "gems": [{"name": "A", "isSupport": False}]},
              {"type": "addGroup", "gems": [{"name": "A", "isSupport": False},
                                               {"name": "B", "isSupport": False}]}],
             "several changes add the same skill: A", "group"),
            ([{"type": "alloc", "nodes": [1, 2]}, {"type": "dealloc", "nodes": [2]}],
             "several changes add and remove the same passive nodes", "node"),
            ([{"type": "config"}], "settings the guide assumes are never applied", "setting"),
            ([{"type": "gemLevel", "group": 1, "gemIndex": 2, "name": "A"},
              {"type": "replaceSupport", "group": 1, "gemIndex": 2,
               "replaced": "B", "gem": {"name": "C"}}],
             "several changes touch the same gem: A, B, C", "gem"),
        ]
        for changes, message, kind in cases:
            with self.subTest(message=message):
                self.assert_conflict(changes, message, kind)

    def test_non_conflicting_table_entries(self):
        cases = [
            [{"type": "alloc", "nodes": [1, 2]}, {"type": "alloc", "nodes": [2, 3]}],
            [{"type": "gemLevel", "group": 1, "gemIndex": 2, "name": "A"},
             {"type": "gemLevel", "group": 2, "gemIndex": 2, "name": "A"}],
            [{"type": "future"}, {"type": "future"}],
        ]
        for changes in cases:
            with self.subTest(changes=changes):
                optimize.check_conflicts(changes)
                self.assertEqual(optimize.conflict_pairs(list(enumerate(changes))), [])

    def test_old_gem_conflicts_are_unchanged(self):
        changes = [{"type": "gem", "name": "A"}, {"type": "swap", "name": "A"}]
        self.assert_conflict(changes, "several changes touch the same gem: A")
        replacements = [{"type": "replaceGem", "group": 1, "gemIndex": 2, "replaced": "A"},
                        {"type": "replaceGem", "group": 1, "gemIndex": 2, "replaced": "B"}]
        self.assert_conflict(replacements, "several changes touch the same gem: A, B")

    def test_repath_conflict_is_unchanged(self):
        self.assert_conflict([{"type": "repath"}, {"type": "repath"}], "pick at most one re-path")

    def test_guide_check_filename_never_overwrites(self):
        with tempfile.TemporaryDirectory() as folder:
            out_dir = Path(folder)
            sentinel = out_dir / "Build (guide check).xml"
            sentinel.write_text("sentinel", encoding="utf-8")
            saved = optimize.save_xml(out_dir, "Build (guide check)", "<xml/>")
        self.assertEqual(saved.name, "Build (guide check 2).xml")

    def test_check_source_fresh_reports_changed_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "build.xml"
            path.write_text("changed", encoding="utf-8")
            with self.assertRaisesRegex(optimize.StaleAudit, "re-run the audit"):
                optimize.check_source_fresh(path, "old hash")


class ApplyChangesTests(unittest.TestCase):
    def setUp(self):
        self.saved_cwd = os.getcwd()
        self.auditor = None
        self.addCleanup(self._restore_cwd)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.addCleanup(self._close_engine)

        root = Path(self.temp_dir.name).resolve()
        self.build_path = root / "build" / "CoC EK Assa.xml"
        self.build_path.parent.mkdir(parents=True)
        shutil.copyfile(gc.BUILDS_DIR / "3.29/Ninja Builds/CoC EK Assa.xml", self.build_path)
        self.out_dir = root / "out"
        settings = {"includeDrafts": True, "disabledSkills": [], "scenario": "Pinnacle Boss"}
        with gc.pob_cwd():
            self.auditor = gc.offline_auditor(self.build_path, settings)
        os.chdir(self.saved_cwd)
        self.auditor.suggestions = [{"type": "gem", "name": "Brutality", "level": 20, "quality": 20}]

    def _close_engine(self):
        if self.auditor is not None and self.auditor.engine._L is not None:
            gc.close_engine(self.auditor.engine)

    def _restore_cwd(self):
        os.chdir(self.saved_cwd)

    def apply(self):
        with gc.pob_cwd():
            os.chdir(gc.POB_INSTALL)
            return optimize.apply_changes(self.auditor, [1], out_dir=self.out_dir, force=True)

    def test_apply_stale_audit(self):
        with self.build_path.open("ab") as build:
            build.write(b"\n")

        with self.assertRaises(optimize.StaleAudit) as caught:
            self.apply()

        self.assertIsInstance(caught.exception, optimize.ChangeError)
        self.assertIn("re-run the audit", str(caught.exception))
        self.assertTrue(not self.out_dir.exists() or not any(self.out_dir.iterdir()))

    def test_apply_never_overwrites(self):
        name = self.auditor.summary["buildName"]
        self.out_dir.mkdir()
        sentinel = self.out_dir / f"{name} (optimized).xml"
        sentinel.write_text("SENTINEL", encoding="utf-8")

        first = self.apply()

        first_path = Path(first["path"])
        first_bytes = first_path.read_bytes()
        self.assertTrue(first["saved"])
        self.assertEqual(first_path.name, f"{name} (optimized 2).xml")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "SENTINEL")
        self.assertTrue(first_bytes)
        self.assertTrue(first_bytes.startswith(b"<"))

        second = self.apply()

        self.assertEqual(Path(second["path"]).name, f"{name} (optimized 3).xml")
        self.assertEqual(first_path.read_bytes(), first_bytes)
        self.assertEqual(len(list(self.out_dir.iterdir())), 3)

    def test_apply_missing_source_is_stale(self):
        self.build_path.unlink()

        with self.assertRaises(optimize.StaleAudit):
            self.apply()

        self.assertTrue(not self.out_dir.exists() or not any(self.out_dir.iterdir()))

    def violations_stub(self, adds_new_break: bool):
        """Rules stub: one violation already on the untouched build; optionally one more once the build changed."""
        with gc.pob_cwd():
            os.chdir(gc.POB_INSTALL)
            base_ctx = self.auditor.evaluate()

        def stub(rules, ctx):
            found = ["[Existing rule] already broken before apply"]
            if adds_new_break and ctx != base_ctx:
                found.append("[New rule] broken by the change")
            return found
        return mock.patch.object(audit, "violations", stub)

    def test_apply_accepts_change_that_adds_no_new_break(self):
        with self.violations_stub(adds_new_break=False):
            outcome = self.apply_unforced()

        self.assertEqual(outcome["violations"], [])
        self.assertTrue(outcome["saved"])

    def test_apply_rejects_change_that_adds_a_new_break(self):
        with self.violations_stub(adds_new_break=True):
            outcome = self.apply_unforced()

        self.assertEqual(outcome["violations"], ["[New rule] broken by the change"])
        self.assertFalse(outcome["saved"])
        self.assertTrue(not self.out_dir.exists() or not any(self.out_dir.iterdir()))

    def test_apply_auditor_reuses_given_obtainability_without_network(self):
        given = self.auditor.obtainable
        with mock.patch.object(audit.Obtainability, "load", side_effect=AssertionError("network")):
            with gc.pob_cwd():
                os.chdir(gc.POB_INSTALL)
                second = audit.Auditor(self.build_path, True, disabled_skills=[], scenario="Pinnacle Boss",
                                       engine=self.auditor.engine, obtainable=given)
            os.chdir(self.saved_cwd)

        self.assertIs(second.obtainable, given)

    def apply_unforced(self):
        # Brutality at level 1 / quality 0 really changes this build (level 20 does not), so the context differs
        self.auditor.suggestions = [{"type": "gem", "name": "Brutality", "level": 1, "quality": 0}]
        with gc.pob_cwd():
            os.chdir(gc.POB_INSTALL)
            return optimize.apply_changes(self.auditor, [1], out_dir=self.out_dir, force=False)

    def test_source_sha256_matches_file(self):
        expected = hashlib.sha256(self.build_path.read_bytes()).hexdigest()

        self.assertEqual(self.auditor.source_sha256, expected)


if __name__ == "__main__":
    unittest.main()
