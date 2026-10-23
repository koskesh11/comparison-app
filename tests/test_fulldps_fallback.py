"""Real-PoB regression for builds with every Full DPS group unticked."""

import sys
import unittest
from pathlib import Path
from unittest import mock

TESTS_DIR = Path(__file__).resolve().parent
ENGINE_DIR = TESTS_DIR.parent / "engine"
for path in (TESTS_DIR, ENGINE_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import audit  # noqa: E402
import golden_common as gc  # noqa: E402

SETTINGS = {"includeDrafts": True, "disabledSkills": [], "scenario": "Pinnacle Boss"}


class FullDpsFallbackTests(unittest.TestCase):
    def test_real_pob_output_without_full_dps_uses_combined_dps(self):
        original = audit.Auditor.load_audit_hooks

        def without_full_dps(auditor, disabled):
            auditor.engine.run(
                "for _, g in ipairs(build.skillsTab.socketGroupList) do "
                "g.includeInFullDPS = false end")
            return original(auditor, disabled)

        with gc.pob_cwd(), mock.patch.object(audit.Auditor, "load_audit_hooks", without_full_dps):
            auditor = gc.offline_auditor(gc.build_path(gc.RAW_BUILDS["EK"]), SETTINGS)
            try:
                self.assertEqual(auditor.dps_key, "CombinedDPS")
                self.assertTrue(auditor.dps_measure["warning"].startswith(
                    "No skill group is in Full DPS"))
                self.assertIsInstance(auditor.raw_main_out(), dict)
                self.assertIn(auditor.raw_main_out().get("FullDPS"), (None, 0))
                self.assertGreater(auditor.raw_dps(), 0)
                auditor.dps_breakdown(1.0)
            finally:
                gc.close_engine(auditor.engine)


if __name__ == "__main__":
    unittest.main()
