"""Guide-check contracts. Real PoB smoke tests are skipped when its builds are absent."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parent
ENGINE_DIR = ROOT / "engine"
sys.path.insert(0, str(ENGINE_DIR))

from tests import golden_common as gc
from tests import guide_check_testlib as helpers


class AvailabilityTests(unittest.TestCase):
    def test_real_cache_and_unknown_states(self):
        from guide_check_avail import row_availability
        from obtainability import Obtainability

        available = Obtainability.from_cache("Allflame")
        normal = {"change": {"type": "addSupport", "gem": {
            "name": "Brutality", "level": 20, "quality": 20, "qualityId": "Default"}}}
        awakened = {"change": {"type": "addSupport", "gem": {
            "name": "Awakened Brutality", "level": 5, "quality": 20, "qualityId": "Default"}}}
        high = {"change": {"type": "gemLevel", "name": "Brutality",
                            "level": 25, "quality": 20, "qualityId": "Default"}}
        alternate = {"change": {**normal["change"], "gem": {
            **normal["change"]["gem"], "qualityId": "Anomalous"}}}
        self.assertEqual("obtainable", row_availability(available, normal)["state"])
        self.assertEqual("unobtainable", row_availability(available, awakened)["state"])
        self.assertEqual("unobtainable", row_availability(available, high)["state"])
        self.assertEqual("unknown", row_availability(available, alternate)["state"])
        empty = Obtainability("Allflame")
        self.assertEqual("unknown", row_availability(empty, normal)["state"])

    def test_non_gem_categories(self):
        from guide_check_avail import row_availability
        from obtainability import Obtainability

        obtainable = Obtainability("Allflame")
        self.assertEqual("notChecked", row_availability(obtainable, {"category": "item"})["state"])
        self.assertEqual("n/a", row_availability(obtainable, {"category": "tree-add"})["state"])


class InteractionTests(unittest.TestCase):
    def test_table_references_exist_and_statuses_load(self):
        from guide_interactions import INTERACTIONS, vault_note_status

        statuses = vault_note_status()
        self.assertTrue(statuses)
        for entry in INTERACTIONS:
            for name in entry.get("refs", []):
                self.assertIn(name, statuses)


class DiffTests(unittest.TestCase):
    def test_add_group_preserves_full_dps(self):
        import guide_diff

        fixture = TESTS_DIR / "fixtures" / "snapshots"
        player = json.loads((fixture / "ek_player.json").read_text(encoding="utf-8"))
        guide = json.loads((fixture / "pobb_guide.json").read_text(encoding="utf-8"))
        result = guide_diff.diff(player, guide, {"nodes": {}})
        guide_groups = {g["label"]: g for g in guide["groups"]}
        rows = [row for row in result["rows"] if row["category"] == "group-add"]
        for row in rows:
            self.assertEqual(guide_groups[row["change"]["label"]]["fullDps"],
                             row["change"]["fullDps"])

if __name__ == "__main__":
    unittest.main()
