"""Mageblood detection without private builds (task 010 N3). The belt line is PoB's own wording (Data/Uniques)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from guide_check import MAGEBLOOD_NOTE, _mageblood_reason, wears_mageblood  # noqa: E402

LINE = "Leftmost 3 Magic Utility Flasks constantly apply their Flask Effects to you"


def belt(*mods: str) -> dict:
    return {"slot": "Belt", "name": "Mageblood", "mods": list(mods)}


class MagebloodTests(unittest.TestCase):
    def test_belt_with_the_line_is_detected_in_any_case(self):
        self.assertTrue(wears_mageblood({"items": [belt(LINE)]}))
        self.assertTrue(wears_mageblood({"items": [belt(LINE.upper())]}))

    def test_other_belts_slots_and_missing_keys_are_not_mageblood(self):
        for player in ({}, {"items": None}, {"items": [belt("+50 to maximum Life")]}, {"items": [belt()]},
                       {"items": [{"slot": "Belt"}]}, {"items": [{"slot": "Ring", "mods": [LINE]}]}):
            with self.subTest(player=player):
                self.assertFalse(wears_mageblood(player))

    def test_flask_rows_get_the_reason_and_other_rows_do_not(self):
        player = {"items": [belt(LINE)]}
        self.assertIn(MAGEBLOOD_NOTE, _mageblood_reason({"category": "flask"}, player))
        self.assertIsNone(_mageblood_reason({"category": "unique"}, player))
        self.assertIsNone(_mageblood_reason({"category": "flask"}, {"items": [belt()]}))


if __name__ == "__main__":
    unittest.main()
