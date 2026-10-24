"""Gate 4 why-line, conditional-note, and curse-limit contracts."""

from __future__ import annotations

import shutil
import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parent
sys.path.insert(0, str(ROOT / "engine"))

from tests import golden_common as gc  # noqa: E402
from tests import guide_check_testlib as helpers  # noqa: E402
from tests.guide_testlib import decode_guide  # noqa: E402

import guide_check  # noqa: E402
from guide_check import _explain  # noqa: E402
from guide_check_notes import _curse_note, _need_texts  # noqa: E402
from guide_check_why import explain_row, item_why  # noqa: E402

GENERIC_ZERO_NOTE = ("PoB shows no change from this alone; the reason is not determined "
                     "(a cap, a missing condition, or a stat PoB does not count).")


def _item(snapshot: dict, slot: str) -> dict:
    return next(item for item in snapshot.get("items") or [] if item.get("slot") == slot)


def _slot(row: dict) -> str:
    return str((row.get("info") or {}).get("slot") or (row.get("change") or {}).get("slot"))


def _gem_ids(row: dict) -> list[str]:
    change = row.get("change") or {}
    if change.get("gems"):
        return [gem["gemId"] for gem in change["gems"]]
    gem = change.get("gem") or {}
    return [gem["gemId"]] if gem.get("gemId") else []


class RealGate4WhyTests(helpers.PobGuardedTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = gc.AUDIT_BUILDS["EK"]
        cls.cwd = gc.pob_cwd()
        cls.cwd.__enter__()
        cls.auditor = gc.offline_auditor(gc.build_path(cls.settings["file"]), cls.settings)
        cls.guide_path = decode_guide()
        loaded = guide_check._load_pair(cls.auditor, cls.guide_path, "pobb fixture")
        cls.player, cls.guide = loaded[:2]
        cls.result = guide_check.run_check(cls.auditor, cls.guide_path, "pobb fixture")
        cls.rows = cls.result["rows"] + cls.result["noChange"]

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "auditor"):
            gc.close_engine(cls.auditor.engine)
        if hasattr(cls, "cwd"):
            cls.cwd.__exit__(None, None, None)
        if hasattr(cls, "guide_path"):
            shutil.rmtree(cls.guide_path.parent)
        super().tearDownClass()

    def test_doom_hold_gloves_name_removed_player_lines(self):
        """Doom Hold (DPS -41.6%) was rank 1 before the pure-gains-first sort (M-a); it is now the first trade-off."""
        row = next(row for row in self.rows if row["category"] == "item" and _slot(row) == "Gloves")
        player, guide = _item(self.player, "Gloves"), _item(self.guide, "Gloves")
        removed = [line for line in player["mods"] if line not in guide["mods"]]
        self.assertIn("Critical Strikes with Spells inflict Impale", removed)
        for line in removed:
            self.assertIn("- " + line, row["why"])
        minus = next(index for index, line in enumerate(row["why"]) if line.startswith("- "))
        plus = next(index for index, line in enumerate(row["why"]) if line.startswith("+ "))
        self.assertLess(minus, plus)

    def test_top_three_most_negative_rows_keep_loss_and_skill_lines(self):
        rows = sorted(self.rows, key=lambda row: row["result"]["delta"]["dpsPct"])[:3]
        for row in rows:
            with self.subTest(row=row["id"]):
                self.assertTrue(row["why"])
                if (row.get("dims") or {}).get("skills"):
                    self.assertTrue(row["why"][-1].startswith("PoB per-skill DPS:"))
                if row["category"] in {"item", "flask", "jewel"}:
                    player, guide = _item(self.player, _slot(row)), _item(self.guide, _slot(row))
                    removed = [line for line in player["mods"] if line not in guide["mods"]]
                    if len(removed) <= 8:
                        self.assertTrue(all("- " + line in row["why"] for line in removed))
                if row["category"].startswith("tree-"):
                    self.assertTrue(any(" -> " in line for line in row["why"]))

    def test_mageblood_row_names_both_belt_jewels(self):
        row = next(row for row in self.rows if row["category"] == "item"
                   and _slot(row) == "Belt" and "Darkness Enthroned" in row["label"])
        player, guide = _item(self.player, "Belt"), _item(self.guide, "Belt")
        guide_slots = {jewel.get("slot") for jewel in guide.get("abyssJewels") or []}
        dropped = [jewel for jewel in player.get("abyssJewels") or []
                   if jewel.get("slot") not in guide_slots]
        self.assertTrue(dropped)
        for jewel in dropped:
            line = next(line for line in row["why"] if jewel.get("slot") in line)
            self.assertIn(jewel.get("name"), line)
            self.assertIn("you can keep your jewel in the empty socket - not tested", line)

    def test_viper_road_names_frenzy_flag(self):
        row = next(row for row in self.rows if row["category"] == "item"
                   and "Ralakesh's Impatience" in row["label"])
        self.assertIn("- Count as having maximum number of Frenzy Charges", row["why"])

    def test_gains_only_real_row_has_no_minus_line(self):
        rows = [row for row in self.rows if row["category"] in {"item", "flask", "jewel"}
                and row["result"]["delta"]["dpsPct"] >= 0
                and row["result"]["delta"]["ehpPct"] >= 0 and row["why"]]
        self.assertTrue(rows)
        for row in rows:
            with self.subTest(row=row["id"]):
                self.assertFalse(any(line.startswith("- ") for line in row["why"]))

    def test_watchers_eye_needs_precision_and_discipline(self):
        row = next(row for row in self.rows if "Watcher's Eye" in row["label"])
        player, guide = _item(self.player, _slot(row)), _item(self.guide, _slot(row))
        added = [line for line in guide["mods"] if line not in player["mods"]]
        parsed = self.auditor.call("modNeedsJSON", {"lines": added})
        expected = [condition["skill"] for value in parsed
                    for condition in value.get("conditions") or []
                    if condition.get("skill") and not condition["on"]]
        text = row["conditional"]["text"]
        self.assertIn("needs Precision (not in your build", text)
        self.assertIn("needs Discipline (not in your build", text)
        self.assertTrue(all(f"needs {label} (not in your build" in text for label in expected))

    def test_no_real_row_says_needs_a_generic_buff(self):
        for row in self.rows:
            text = (row.get("conditional") or {}).get("text") or ""
            for generic in ("needs Aura", "needs ArcaneSurge", "needs GloriousMadness", "needs Herald"):
                self.assertNotIn(generic, text, row["id"])

    def test_melding_over_player_cluster_jewel_is_not_tested_now(self):
        """H4: Melding replaces the player's cluster jewel, so the "needs" note moved to the unit test below."""
        self.assertFalse(any("Melding of the Flesh" in row["label"] for row in self.rows))

    def test_curse_zero_note_follows_pobs_own_limit_rule(self):
        """EK has a socketed-curse limit bypass and a Mark in the slots, so the note falls back to the neutral text."""
        row = next(row for row in self.result["noChange"]
                   if row["label"].startswith("Add skill Despair"))
        state = self.auditor.call("curseStateJSON", {"gemIds": _gem_ids(row)})
        self.assertTrue(state["limitBypass"])
        self.assertEqual(GENERIC_ZERO_NOTE, row["zeroNote"])
        self.assertNotIn("full", row["zeroNote"])
        non_curse = next(value for value in self.result["noChange"]
                         if "Grand Spectrum" in value["label"])
        self.assertEqual(GENERIC_ZERO_NOTE, non_curse["zeroNote"])


class _State:
    def __init__(self, state):
        self.state = state

    def call(self, name, _request):
        return self.state


def _curse_row():
    return {"zeroNote": GENERIC_ZERO_NOTE, "change": {"gem": {"gemId": "G"}}}


def _state(**changes):
    return {"limit": 2, "slots": ["Enfeeble", "Despair"], "curse": {"G": True},
            "mark": {"G": False}, "limitBypass": False, **changes}


class CurseAndNeedsNoteTests(unittest.TestCase):
    def test_limited_slots_at_limit_say_used_up(self):
        note = _curse_note(_State(_state()), _curse_row())
        self.assertIn("curse limit (2) is used up", note)
        self.assertNotIn("full", note)

    def test_fewer_limited_slots_than_limit_gives_no_claim(self):
        """Lua now drops ignoreHexLimit / Blasphemy slots from "slots": one hex + one bypass curse -> 1 slot of 2."""
        self.assertIsNone(_curse_note(_State(_state(slots=["Enfeeble"])), _curse_row()))

    def test_mark_gem_and_limit_bypass_fall_back_to_the_neutral_note(self):
        self.assertIsNone(_curse_note(_State(_state(mark={"G": True})), _curse_row()))
        self.assertIsNone(_curse_note(_State(_state(limitBypass=True)), _curse_row()))
        self.assertIsNone(_curse_note(_State(_state(mark={})), _curse_row()))

    def test_max_res_flag_gives_the_raised_max_res_note_without_build_claim(self):
        parsed = [{"text": "x", "conditions": [], "flags": ["ElementalResistMaxIsHighestResistMax"]}]
        texts = _need_texts(parsed, {"groups": []})
        self.assertEqual(["needs a raised maximum Elemental Resistance"], texts)

    def test_needs_only_for_skill_gems_not_generic_buffs_or_downsides(self):
        cond = lambda var, skill=None: {"var": var, "on": False, **({"skill": skill} if skill else {})}
        parsed = [{"text": "x while affected by Precision", "conditions": [cond("AffectedByPrecision", "Precision")]},
                  {"text": "y", "conditions": [cond("AffectedByAura"), cond("AffectedByArcaneSurge")]},
                  {"text": "Unaffected by Curses while affected by Zealotry",
                   "conditions": [cond("AffectedByZealotry", "Zealotry")]}]
        self.assertEqual(["needs Precision (not in your build)"], _need_texts(parsed, {"groups": []}))


class FastWhyTests(unittest.TestCase):
    def test_explain_skips_note_calls_after_deadline(self):
        class Auditor:
            def call(self, *_args, **_kwargs):
                raise AssertionError("PoB note call after deadline")

        row = {"category": "item", "info": {"slot": "Belt"}, "conditional": None,
               "zeroNote": None, "result": {"delta": {"dpsPct": 0, "ehpPct": 0}},
               "dims": {}}
        player = {"items": [{"slot": "Belt", "mods": []}]}
        guide = {"items": [{"slot": "Belt", "mods": ["added"]}], "groups": []}
        _explain(Auditor(), [row], player, guide, lambda: 2, 0, 1)
        self.assertEqual(["+ added"], row["why"])

    def test_loss_bigger_keeps_six_removed_and_two_added_lines(self):
        row = {"result": {"delta": {"dpsPct": -20, "ehpPct": 5}}}
        player = {"mods": [f"old {index}" for index in range(6)]}
        guide = {"mods": [f"new {index}" for index in range(4)]}
        lines = item_why(row, player, guide)
        self.assertEqual(8, len(lines))
        self.assertEqual(6, sum(line.startswith("- ") for line in lines))
        self.assertEqual(2, sum(line.startswith("+ ") for line in lines))

    def test_gains_only_omits_removed_lines(self):
        row = {"result": {"delta": {"dpsPct": 0, "ehpPct": 1}}}
        lines = item_why(row, {"mods": ["old"]}, {"mods": ["new"]})
        self.assertFalse(any(line.startswith("- ") for line in lines))

    def test_missing_abyss_jewel_keys_do_not_crash(self):
        row = {"result": {"delta": {"dpsPct": -1, "ehpPct": 0}}}
        self.assertEqual(["- old", "+ new"],
                         item_why(row, {"mods": ["old"]}, {"mods": ["new"]}))

    def test_explain_row_keeps_skill_line_after_item_cap(self):
        skills = [{"name": "Skill", "pct": -1, "projectiles": None}]
        row = {"category": "item", "result": {"delta": {"dpsPct": -20, "ehpPct": 0}},
               "dims": {"skills": skills}, "zeroNote": None}
        player = {"mods": [f"old {index}" for index in range(8)]}
        lines = explain_row(None, row, {}, player, {"mods": []})
        self.assertEqual(9, len(lines))
        self.assertTrue(lines[-1].startswith("PoB per-skill DPS:"))


if __name__ == "__main__":
    unittest.main()
