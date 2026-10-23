"""Integration tests for safely applying audited build changes."""

import hashlib
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden_common as gc  # noqa: E402

import optimize  # noqa: E402


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

    def test_source_sha256_matches_file(self):
        expected = hashlib.sha256(self.build_path.read_bytes()).hexdigest()

        self.assertEqual(self.auditor.source_sha256, expected)


if __name__ == "__main__":
    unittest.main()
