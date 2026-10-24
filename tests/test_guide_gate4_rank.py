"""GATE 4 M-a: "Best" lists pure gains first, trade-offs after (labelled), on the real EK guide-check report."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from guide_check_rank import is_tradeoff, rank_rows, score  # noqa: E402

REPORT = Path(__file__).resolve().parent / "fixtures" / "guide_report_ek.json"


def _delta(dps: float, ehp: float) -> dict:
    return {"id": f"{dps}/{ehp}", "category": "item", "label": f"r{dps}/{ehp}",
            "result": {"delta": {"dpsPct": dps, "ehpPct": ehp}}}


class RealReportRankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))
        cls.rows = {row["id"]: row for row in cls.report["rows"]}
        cls.best = [cls.rows[ident] for ident in cls.report["sorts"]["best"]]

    def test_every_pure_gain_comes_before_every_trade_off(self):
        flags = [is_tradeoff(row) for row in self.best]
        self.assertIn(True, flags)
        self.assertIn(False, flags)
        self.assertEqual(flags, sorted(flags), "a trade-off row ranks above a pure gain")

    def test_trade_off_rows_carry_the_label_and_both_numbers(self):
        for row in self.best:
            delta = row["result"]["delta"]
            self.assertEqual(is_tradeoff(row), "trade-off" in row["chips"], row["id"])
            self.assertTrue(all(isinstance(delta[key], (int, float)) for key in ("dpsPct", "ehpPct")))

    def test_each_block_is_sorted_by_the_larger_gain(self):
        for flag in (False, True):
            scores = [score(row) for row in self.best if is_tradeoff(row) == flag]
            self.assertEqual(scores, sorted(scores, reverse=True))

    def test_doom_hold_dps_minus_41_6_is_a_trade_off_no_longer_rank_one(self):
        gloves = self.rows["item:Gloves"]
        self.assertAlmostEqual(gloves["result"]["delta"]["dpsPct"], -41.578, places=2)
        self.assertTrue(is_tradeoff(gloves))
        self.assertGreater(gloves["rank"], 1)
        self.assertFalse(is_tradeoff(self.best[0]))
        self.assertEqual(self.best[0]["rank"], 1)


class RankUnitTests(unittest.TestCase):
    def test_pure_gain_with_small_gain_beats_a_big_gain_that_costs_the_other_axis(self):
        rows, sorts = rank_rows([_delta(-40.0, 14.0), _delta(2.0, 0.0), _delta(5.0, -0.05)])
        self.assertEqual([row["id"] for row in rows], ["5.0/-0.05", "2.0/0.0", "-40.0/14.0"])
        self.assertEqual(sorts["best"], [row["id"] for row in rows])
        self.assertEqual(sorts["dps"][0], "5.0/-0.05")


if __name__ == "__main__":
    unittest.main()
