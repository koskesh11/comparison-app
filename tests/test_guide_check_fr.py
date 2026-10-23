"""T-FR regression pair (spec B2, E10): owner's FR CoC v1 as player, v4 as guide. Skipped when the private builds are absent."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden_common as gc  # noqa: E402
import guide_check_testlib as helpers  # noqa: E402


class FrRegressionPairTests(helpers.PobGuardedTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.v1, cls.v4 = (gc.build_path(gc.RAW_BUILDS[key]) for key in ("v1", "v4"))
        if not (cls.v1.is_file() and cls.v4.is_file()):
            raise unittest.SkipTest("owner FR v1/v4 builds are not on this machine (private fixture, E10)")
        cls.cwd = gc.pob_cwd()
        cls.cwd.__enter__()
        settings = {"disabledSkills": [], "scenario": "Pinnacle Boss", "includeDrafts": True}
        cls.auditor = gc.offline_auditor(cls.v1, settings)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "auditor"):
            gc.close_engine(cls.auditor.engine)
        if hasattr(cls, "cwd"):
            cls.cwd.__exit__(None, None, None)
        super().tearDownClass()

    def test_known_differences_appear_as_rows(self):
        from guide_check import run_check
        result = run_check(self.auditor, self.v4, "FR v4")
        everything = result["rows"] + result["noChange"] + result["notTested"]
        text = " ".join(str(row.get("label")) for row in everything)
        # Real differences between these two files on this machine (checked 2026-10-23): the abyss-jewel gloves, a flask,
        # a Forbidden Rite group and a timeless jewel. The spec's "Cooldown Recovery support / re-taken keystone" are NOT
        # in this pair (open issue for the user in tasks/reports/010-eng.md).
        self.assertIn("Doom Hold", text)
        self.assertIn("Flask 2", text)
        self.assertIn("Forbidden Rite", text)
        categories = {row["category"] for row in result["rows"] + result["noChange"]}
        print("T-FR", result["counts"], sorted(categories))

    def test_mageblood_player_gets_flask_rows_as_not_tested_with_the_vault_note(self):
        """GATE 2 H5: PoB keeps the saved flasks under Mageblood, so a flask swap would show a phantom second flask."""
        from guide_check import MAGEBLOOD_NOTE, run_check, wears_mageblood
        import guide_lua

        guide_lua.ensure_loaded(self.auditor.engine)
        self.assertTrue(wears_mageblood(guide_lua.snapshot(self.auditor.engine, "player")))
        result = run_check(self.auditor, self.v4, "FR v4")
        ranked = result["rows"] + result["noChange"]
        self.assertEqual([], [row["id"] for row in ranked if row["category"] == "flask"])
        flasks = [row for row in result["notTested"] if row["category"] == "flask"]
        self.assertTrue(flasks)
        for row in flasks:
            self.assertIn("Mageblood", row["reason"])
            self.assertIn(MAGEBLOOD_NOTE, row["vaultRefs"])
            self.assertIsNone(row["result"])


if __name__ == "__main__":
    unittest.main()
