"""Tests for gems already in a build that cannot be obtained."""

import sys
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
ENGINE_DIR = TESTS_DIR.parent / "engine"
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

import golden_common as gc  # noqa: E402
import unobtainable  # noqa: E402
from obtainability import Obtainability, gem_key  # noqa: E402
from optimize import ChangeError, check_conflicts  # noqa: E402
from pobhost import LuaError  # noqa: E402

SETTINGS = {"includeDrafts": True, "disabledSkills": [], "scenario": "Pinnacle Boss"}
TRIGGER_LINE = "Forbidden Rite of Soul Sacrifice: 10.03/s -> 5.07/s, cap 10.10/s -> 7.57/s"
ENGINE_TRIGGER_LINE = (
    "Forbidden Rite of Soul Sacrifice: 10.03/s -> 5.06/s, cap 10.10/s -> 7.57/s; "
    "Cyclone attack rate 10.03/s overshoots the 7.57/s cap: only 50% of attacks trigger "
    "(about every 2nd attack); see breakpoints (B5)"
)
REMOVAL_LINE = "removes Awakened Cast On Critical Strike's own bonuses (e.g. cooldown recovery)"


def gem_row(group: int, index: int, name: str, granted: bool = False) -> dict:
    return {
        "group": group, "gemIndex": index, "groupLabel": f"Group {group}", "isMainGroup": group == 1,
        "name": name, "gemId": name.replace(" ", ""), "level": 5, "quality": 20,
        "support": True, "granted": granted, "source": "socket",
    }


def skill(name: str, rate: float | None = None, cap: float | None = None,
          source: float | None = None, is_attack: bool = False) -> dict:
    out = {}
    if rate is not None:
        out["SkillTriggerRate"] = rate
    if cap is not None:
        out["TriggerRateCap"] = cap
    if source is not None:
        out["EffectiveSourceRate"] = source
    return {"name": name, "isAttack": is_attack, "out": out}


class FakeAuditor:
    multi_part = False

    def __init__(self, gems: list[dict], obtainable: Obtainability, bad_with: str | None = None):
        self.gems = gems
        self.obtainable = obtainable
        self.bad_with = bad_with
        self.keys = ["FullDPS"]
        self.calls: list[tuple[str, dict | None]] = []
        self.suggestions: list[dict] = []

    def call(self, function: str, request: dict | None = None):
        self.calls.append((function, request))
        if function == "listGemsJSON":
            return self.gems
        replacements = request["replacements"]
        if self.bad_with and (len(replacements) > 1 or replacements[0]["with"] == self.bad_with):
            raise LuaError(f"invalid replacement {self.bad_with}")
        singles = [self._single(row) for row in replacements]
        return {"single": singles, "combined": self._ctx("combined")}

    @staticmethod
    def _ctx(tag: str) -> dict:
        rate, cap = ((5.0799999, 7.5757575757576) if tag in ("one", "combined")
                     else (10.0399999, 10.1099999))
        return {"tag": tag, "skills": [skill("Forbidden Rite of Soul Sacrifice", rate, cap)]}

    def _single(self, row: dict) -> dict:
        tag = "one" if row["gemIndex"] == 3 else "two"
        return {"group": row["group"], "gemIndex": row["gemIndex"], "name": row["name"],
                "with": row["with"], "level": row["level"], "quality": row["quality"],
                "ctx": self._ctx(tag)}

    @staticmethod
    def extra_request() -> list[dict]:
        return [{"group": 9, "index": 1}]

    @staticmethod
    def adjust(ctx: dict) -> dict:
        return ctx

    @staticmethod
    def dimensions(ctx: dict, base_ctx: dict) -> dict:
        return {"dps": ctx["tag"]}

    @staticmethod
    def breaks(ctx: dict) -> list[str]:
        return [f"rule {ctx['tag']}"]

    def suggest(self, change: dict) -> int:
        self.suggestions.append(change)
        return len(self.suggestions)


class OfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obtainable = Obtainability.from_cache("Allflame")

    def test_flagged_rows_are_sorted_labelled_and_skip_granted(self):
        gems = [
            gem_row(4, 2, "Empower"), gem_row(1, 5, "Awakened Void Manipulation"),
            gem_row(3, 1, "Totally Made Up Support"), gem_row(1, 3, "Awakened Cast On Critical Strike"),
            gem_row(5, 1, "Awakened Empower"), gem_row(1, 1, "Awakened Void Manipulation", granted=True),
        ]
        checked, rows = unobtainable.flagged_rows(gems, self.obtainable)
        self.assertEqual(checked, 5)
        self.assertEqual([(r["group"], r["gemIndex"]) for r in rows], [(1, 3), (1, 5), (3, 1)])
        for row in rows[:2]:
            self.assertTrue(row["label"].startswith(
                "Unobtainable since 3.28.0: All Awakened Support Gems can no longer be obtained"))
            self.assertTrue(row["label"].endswith("(vault: Unobtainable gems)"))
        self.assertEqual(rows[2]["label"],
                         f"not listed on poe.ninja Allflame (cache {self.obtainable.cache_date}), unverified")

    def test_choose_replacement_uses_best_uncorrupted_listing(self):
        expected = {
            "Awakened Cast On Critical Strike": {"with": "Cast On Critical Strike", "level": 20, "quality": 20},
            "Awakened Void Manipulation": {"with": "Void Manipulation", "level": 20, "quality": 20},
        }
        for name, replacement in expected.items():
            with self.subTest(name=name):
                self.assertEqual(unobtainable.choose_replacement(name, self.obtainable), (replacement, None))
        self.assertEqual(unobtainable.choose_replacement("Totally Made Up Support", self.obtainable),
                         (None, "Totally Made Up Support has no normal version"))
        replacement, note = unobtainable.choose_replacement("Awakened Totally Made Up", self.obtainable)
        self.assertIsNone(replacement)
        self.assertIn("Totally Made Up has no uncorrupted listing", note)

    def test_unknown_cache_date_is_rendered_once(self):
        status = {"state": "unlisted", "league": "X", "cacheDate": None}
        self.assertEqual(unobtainable.flag_label(status),
                         "not listed on poe.ninja X (cache date unknown), unverified")
        replacement, note = unobtainable.choose_replacement("Awakened Missing", Obtainability("X"))
        self.assertIsNone(replacement)
        self.assertEqual(note, "Missing has no uncorrupted listing on poe.ninja X (cache date unknown)")

    def test_trigger_why_formats_changes_and_used_together(self):
        base = {"skills": [skill("Forbidden Rite of Soul Sacrifice", 10.0399999, 10.1099999)],
                "usedTogether": [skill("Second", 2.0, 3.0)]}
        changed = {"skills": [skill("Forbidden Rite of Soul Sacrifice", 5.0799999, 7.5757575757576)],
                   "usedTogether": [skill("Second", 2.0, 3.0)]}
        self.assertEqual(unobtainable.trigger_why(base, changed), [TRIGGER_LINE])
        self.assertEqual(unobtainable.trigger_why(base, base), [])

    def test_trigger_why_handles_missing_caps_and_skills(self):
        base = {"skills": [skill("No Cap", 3.0), skill("Gone", 4.0, 5.0)]}
        changed = {"skills": [skill("No Cap", 2.0)]}
        self.assertEqual(unobtainable.trigger_why(base, changed), [
            "No Cap: 3.00/s -> 2.00/s",
            "Gone: 4.00/s -> n/a, cap 5.00/s -> n/a",
        ])

    def test_trigger_why_appends_shared_overshoot_explanation(self):
        base = {"skills": [skill("Forbidden Rite of Soul Sacrifice", 10.0399999, 10.1099999)]}
        changed = {"skills": [
            skill("Forbidden Rite of Soul Sacrifice", 5.06616, 7.5757575757576, 10.032),
            skill("Cyclone", is_attack=True),
        ]}

        self.assertEqual(unobtainable.trigger_why(base, changed), [
            "Forbidden Rite of Soul Sacrifice: 10.03/s -> 5.06/s, cap 10.10/s -> 7.57/s; "
            "Cyclone attack rate 10.03/s overshoots the 7.57/s cap: only 50% of attacks trigger "
            "(about every 2nd attack); see breakpoints (B5)",
        ])

    def test_trigger_why_does_not_append_without_overshoot(self):
        base = {"skills": [skill("Triggered", 7, 10)]}
        for changed in (
                {"skills": [skill("Triggered", 5, 10, 8)]},
                {"skills": [skill("Triggered", 8, 8, 10)]}):
            with self.subTest(changed=changed):
                self.assertEqual(unobtainable.trigger_why(base, changed),
                                 ["Triggered: 7.00/s -> " + ("5.00/s, cap 10.00/s -> 10.00/s"
                                                              if changed["skills"][0]["out"]["SkillTriggerRate"] == 5
                                                              else "8.00/s, cap 10.00/s -> 8.00/s")])

    def test_removal_why_only_describes_trigger_supports(self):
        self.assertEqual(unobtainable.removal_why("Awakened Cast On Critical Strike"), [REMOVAL_LINE])
        self.assertEqual(unobtainable.removal_why("Awakened Void Manipulation"), [])
        self.assertEqual(unobtainable.removal_why("Awakened Cast While Channelling"),
                         ["removes Awakened Cast While Channelling's own bonuses"])

    def test_swap_levels_only_contains_obtainable_uncorrupted_variants(self):
        levels = unobtainable.swap_levels(self.obtainable)
        self.assertEqual(levels["cooldown recovery"], {"level": 3, "quality": 20})
        self.assertNotIn("awakened cast on critical strike", levels)
        self.assertTrue(all(key == gem_key(key) for key in levels))

    def test_skipped_count_accepts_count_list_and_missing(self):
        self.assertEqual(unobtainable.skipped_count({"skipped": 4}), 4)
        self.assertEqual(unobtainable.skipped_count({"skipped": ["one", "two"]}), 2)
        self.assertEqual(unobtainable.skipped_count({}), 0)
        self.assertEqual(unobtainable.skipped_count({"skipped": None}), 0)

    def test_alert_lines_empty_and_complete(self):
        self.assertEqual(unobtainable.alert_lines({"items": []}, lambda dims: "DIMS"), [])
        section = {"checked": 3, "items": [{
            "id": 1, "group": 1, "gemIndex": 3, "name": "Awakened CoC", "level": 6, "quality": 20,
            "label": "denied", "replacement": {"with": "CoC", "level": 20, "quality": 20},
            "replacementNote": None, "dims": {}, "why": ["reason"], "breaks": ["rule"],
        }, {
            "id": None, "group": 2, "gemIndex": 1, "name": "Unknown", "level": 1, "quality": 0,
            "label": "unlisted", "replacement": None, "replacementNote": "no normal", "dims": None,
            "why": [], "breaks": [],
        }], "combined": {"ids": [1], "dims": {}, "why": ["together reason"], "breaks": ["together rule"]}}
        self.assertEqual(unobtainable.alert_lines(section, lambda dims: "DIMS"), [
            "!! 2 unobtainable or unlisted gem(s) already in your build (3 gems checked):",
            "   [1] group 1 gem 3: Awakened CoC 6/20: denied",
            "         -> CoC 20/20: DIMS", "         why: reason",
            "         !! breaks (shown, still offered: the current gem can't be obtained): rule",
            "       group 2 gem 1: Unknown 1/0: unlisted", "         no replacement: no normal",
            "   together [1]: DIMS", "         why: together reason",
            "         !! breaks (shown, still offered: the current gem can't be obtained): together rule",
        ])

    def test_alert_lines_print_part_values_for_item_and_combined(self):
        parts = [{"skill": "Main", "partName": "Saved", "saved": True, "dps": 12.34, "skills": []}]
        item = {"id": 1, "group": 1, "gemIndex": 1, "name": "Old", "level": 1, "quality": 0,
                "label": "denied", "replacement": {"with": "New", "level": 20, "quality": 20},
                "replacementNote": None, "dims": {"parts": parts}, "why": [], "breaks": []}
        lines = unobtainable.alert_lines(
            {"checked": 1, "items": [item],
             "combined": {"ids": [1], "dims": {"parts": parts}, "why": [], "breaks": []}},
            lambda dims: "DIMS")
        self.assertEqual(lines.count("         parts: Saved (saved) +12.3%"), 2)

    def test_replace_gem_conflict_rules(self):
        check_conflicts([
            {"type": "replaceGem", "name": "Awakened X", "group": 1, "gemIndex": 2},
            {"type": "replaceGem", "name": "Awakened X", "group": 2, "gemIndex": 2},
        ])
        with self.assertRaisesRegex(ChangeError, "several changes touch the same gem: Awakened X"):
            check_conflicts([{"type": "replaceGem", "name": "Awakened X", "group": 1, "gemIndex": 2},
                             {"type": "swap", "replaced": "Awakened X"}])
        with self.assertRaisesRegex(ChangeError, "several changes touch the same gem: Awakened X"):
            check_conflicts([{"type": "replaceGem", "name": "Awakened X", "group": 1, "gemIndex": 2},
                             {"type": "replaceGem", "name": "Awakened X", "group": 1, "gemIndex": 2}])
        with self.assertRaisesRegex(ChangeError, "several changes touch the same gem: Awakened X, Awakened Y"):
            check_conflicts([{"type": "replaceGem", "name": "Awakened X", "group": 1, "gemIndex": 2},
                             {"type": "replaceGem", "name": "Awakened Y", "group": 1, "gemIndex": 2}])
        with self.assertRaisesRegex(ChangeError, "several changes touch the same gem: X"):
            check_conflicts([{"type": "gem", "name": "X"}, {"type": "swap", "replaced": "X"}])
        with self.assertRaisesRegex(ChangeError, "pick at most one re-path"):
            check_conflicts([{"type": "repath"}, {"type": "repath"}])

    def test_check_builds_items_suggestions_combined_why_and_breaks(self):
        gems = [gem_row(1, 3, "Awakened Cast On Critical Strike"),
                gem_row(1, 5, "Awakened Void Manipulation")]
        auditor = FakeAuditor(gems, self.obtainable)
        base = {"skills": [skill("Forbidden Rite of Soul Sacrifice", 10.0399999, 10.1099999)]}
        section = unobtainable.check(auditor, base)
        self.assertEqual([item["id"] for item in section["items"]], [1, 2])
        self.assertEqual(auditor.suggestions, [
            {"type": "replaceGem", "group": 1, "gemIndex": 3, "name": "Awakened Cast On Critical Strike",
             "with": "Cast On Critical Strike", "level": 20, "quality": 20},
            {"type": "replaceGem", "group": 1, "gemIndex": 5, "name": "Awakened Void Manipulation",
             "with": "Void Manipulation", "level": 20, "quality": 20},
        ])
        self.assertEqual(section["items"][0]["why"], [TRIGGER_LINE, REMOVAL_LINE])
        self.assertEqual(section["items"][0]["breaks"], ["rule one"])
        self.assertEqual(section["combined"]["ids"], [1, 2])
        self.assertEqual(section["combined"]["why"], [TRIGGER_LINE, REMOVAL_LINE])
        self.assertEqual(section["combined"]["breaks"], ["rule combined"])
        request = next(request for function, request in auditor.calls if function == "auditGemReplaceJSON")
        self.assertEqual(request["extraSkills"], [{"group": 9, "index": 1}])

    def test_check_requests_part_variants_for_multi_part_build(self):
        auditor = FakeAuditor([gem_row(1, 3, "Awakened Cast On Critical Strike")], self.obtainable)
        auditor.multi_part = True
        unobtainable.check(auditor, {"skills": []})
        request = next(request for function, request in auditor.calls if function == "auditGemReplaceJSON")
        self.assertTrue(request["partVariants"])

    def test_check_with_no_flags_does_not_evaluate_replacements(self):
        auditor = FakeAuditor([gem_row(1, 1, "Empower")], self.obtainable)
        self.assertEqual(unobtainable.check(auditor, {"skills": []}),
                         {"checked": 1, "items": [], "combined": None})
        self.assertEqual([function for function, request in auditor.calls], ["listGemsJSON"])

    def test_check_without_viable_normal_gem_does_not_suggest(self):
        obtainable = Obtainability("X", deny={"awakened totally made up"}, deny_sources={
            "awakened totally made up": {"since": "1", "reason": "gone", "note": "N"}})
        auditor = FakeAuditor([gem_row(1, 1, "Awakened Totally Made Up")], obtainable)
        section = unobtainable.check(auditor, {"skills": []})
        item = section["items"][0]
        self.assertIsNone(item["replacement"])
        self.assertEqual(item["replacementNote"],
                         "Totally Made Up has no uncorrupted listing on poe.ninja X (cache date unknown)")
        self.assertIsNone(item["id"])
        self.assertIsNone(section["combined"])
        self.assertEqual(auditor.suggestions, [])

    def test_check_recovers_when_one_replacement_is_rejected_by_pob(self):
        gems = [gem_row(1, 3, "Awakened Cast On Critical Strike"),
                gem_row(1, 5, "Awakened Void Manipulation")]
        auditor = FakeAuditor(gems, self.obtainable, bad_with="Void Manipulation")
        base = {"skills": [skill("Forbidden Rite of Soul Sacrifice", 10.0399999, 10.1099999)]}
        section = unobtainable.check(auditor, base)
        self.assertEqual([item["id"] for item in section["items"]], [1, None])
        self.assertEqual(section["items"][1]["replacementNote"],
                         "PoB cannot apply Void Manipulation: invalid replacement Void Manipulation")
        self.assertIsNone(section["combined"])
        self.assertEqual(len(auditor.suggestions), 1)

    def test_check_with_one_replacement_has_no_combined_result(self):
        auditor = FakeAuditor([gem_row(1, 3, "Awakened Cast On Critical Strike")], self.obtainable)
        base = {"skills": [skill("Forbidden Rite of Soul Sacrifice", 10.0399999, 10.1099999)]}
        self.assertIsNone(unobtainable.check(auditor, base)["combined"])

    def test_check_uses_level_and_quality_applied_by_pob(self):
        class AppliedAuditor(FakeAuditor):
            def _single(self, row: dict) -> dict:
                result = super()._single(row)
                return {**result, "level": 19, "quality": 17}

        auditor = AppliedAuditor([gem_row(1, 3, "Awakened Cast On Critical Strike")], self.obtainable)
        base = {"skills": [skill("Forbidden Rite of Soul Sacrifice", 10.0399999, 10.1099999)]}
        item = unobtainable.check(auditor, base)["items"][0]
        self.assertEqual(item["replacement"], {"with": "Cast On Critical Strike", "level": 19, "quality": 17})
        self.assertEqual(auditor.suggestions[0]["level"], 19)
        self.assertEqual(auditor.suggestions[0]["quality"], 17)


class EngineTests(unittest.TestCase):
    def audit_build(self, key: str):
        settings = {**SETTINGS, "disabledSkills": ["Aspect of the Brine King"] if key == "Worb" else []}
        context = gc.pob_cwd()
        context.__enter__()
        self.addCleanup(context.__exit__, None, None, None)
        auditor = gc.offline_auditor(gc.build_path(gc.RAW_BUILDS[key]), settings)
        self.addCleanup(gc.close_engine, auditor.engine)
        return auditor, unobtainable.check(auditor, auditor.evaluate())

    def test_source_build_replacements_and_impact(self):
        auditor, section = self.audit_build("source")
        self.assertEqual([(i["group"], i["gemIndex"], i["name"], i["level"], i["quality"])
                          for i in section["items"]], [
            (1, 3, "Awakened Cast On Critical Strike", 6, 20),
            (1, 5, "Awakened Void Manipulation", 5, 20),
        ])
        self.assertEqual([i["state"] for i in section["items"]], ["denied", "denied"])
        self.assertEqual([i["replacement"] for i in section["items"]], [
            {"with": "Cast On Critical Strike", "level": 20, "quality": 20},
            {"with": "Void Manipulation", "level": 20, "quality": 20},
        ])
        self.assertEqual([i["id"] for i in section["items"]], [1, 2])
        self.assertEqual([i["replacementNote"] for i in section["items"]], [None, None])
        self.assertEqual(section["combined"]["ids"], [1, 2])
        damage = next(row for row in section["combined"]["dims"]["skills"]
                      if row["name"] == "Forbidden Rite of Soul Sacrifice")
        self.assertEqual(round(damage["from"] / 1e6, 2), 16.54)
        self.assertEqual(round(damage["to"] / 1e6, 2), 7.68)
        self.assertIn(ENGINE_TRIGGER_LINE, section["combined"]["why"])
        self.assertIn(REMOVAL_LINE, section["combined"]["why"])
        es = section["combined"]["dims"]["costs"]["ES"]
        self.assertAlmostEqual(es["to"] - es["from"], 800.1, delta=0.15)
        self.assertEqual(auditor.suggestions, [
            {"type": "replaceGem", "group": 1, "gemIndex": 3, "name": "Awakened Cast On Critical Strike",
             "with": "Cast On Critical Strike", "level": 20, "quality": 20},
            {"type": "replaceGem", "group": 1, "gemIndex": 5, "name": "Awakened Void Manipulation",
             "with": "Void Manipulation", "level": 20, "quality": 20},
        ])

    def assert_empty_build(self, key: str) -> None:
        auditor, section = self.audit_build(key)
        self.assertEqual(section["items"], [])
        self.assertIsNone(section["combined"])
        self.assertGreater(section["checked"], 0)
        self.assertEqual(auditor.suggestions, [])

    def test_v1_has_no_flagged_gems(self):
        self.assert_empty_build("v1")

    def test_v2_has_no_flagged_gems(self):
        self.assert_empty_build("v2")

    def test_v3_has_no_flagged_gems(self):
        self.assert_empty_build("v3")

    def test_v4_has_no_flagged_gems(self):
        self.assert_empty_build("v4")

    def test_ek_has_no_flagged_gems(self):
        self.assert_empty_build("EK")

    def test_worb_has_no_flagged_gems(self):
        self.assert_empty_build("Worb")


if __name__ == "__main__":
    unittest.main()
