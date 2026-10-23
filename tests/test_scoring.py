"""Fast unit tests for DPS scoring and per-skill reporting."""

import copy
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden_common as gc  # noqa: E402

import models  # noqa: E402
import scoring  # noqa: E402
from audit import Auditor  # noqa: E402


def ctx_of(snapshot: dict) -> dict:
    return {"skills": snapshot["skills"], "skillDPS": snapshot["skillDPS"]}


def main_out(ctx: dict) -> dict:
    return next(skill for skill in ctx["skills"] if skill["isMain"])["out"]


class ScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        golden = json.loads(gc.GOLDEN_PATH.read_text(encoding="utf-8"))
        cls.snapshots = {key: value["snapshot"] for key, value in golden["raw"].items()}

    def test_v3_to_v4_uses_full_dps_and_reports_each_skill(self):
        base, new = ctx_of(self.snapshots["v3"]), ctx_of(self.snapshots["v4"])

        full_dps_pct = scoring.change_pct(main_out(new)["FullDPS"], main_out(base)["FullDPS"])
        changes = scoring.skill_changes(new, base)

        self.assertEqual(round(full_dps_pct, 1), 48.1)
        self.assertEqual([row["name"] for row in changes],
                         ["Forbidden Rite of Soul Sacrifice", "Cyclone"])
        self.assertEqual(changes[0]["part"], "All Primary Projectiles")
        self.assertEqual(changes[0]["count"], 1)
        self.assertEqual(round(changes[0]["pct"], 1), 48.5)
        self.assertEqual(round(changes[1]["pct"], 1), -25.0)

    def test_earlier_versions_use_full_dps(self):
        values = [main_out(ctx_of(self.snapshots[key]))["FullDPS"] for key in ("v1", "v2", "v3")]

        self.assertEqual(round(scoring.change_pct(values[1], values[0]), 1), 184.4)
        self.assertEqual(round(scoring.change_pct(values[2], values[1]), 1), 146.4)

    def test_v4_tile_and_measure(self):
        ctx = ctx_of(self.snapshots["v4"])

        self.assertEqual(scoring.dps_measure(ctx), {"key": "FullDPS", "warning": None})
        self.assertEqual(
            scoring.tile_text(scoring.base_skill_rows(ctx)),
            "Forbidden Rite of Soul Sacrifice 56.83M (All Primary Projectiles, x1) + "
            "Cyclone 0.16M (x1); Forbidden Rite of Soul Sacrifice 7.52/s of 7.57/s cap",
        )

    def test_trigger_limits_explain_source_and_unknown_shortfall(self):
        v4 = scoring.trigger_info(ctx_of(self.snapshots["v4"]))["Forbidden Rite of Soul Sacrifice"]
        v2 = scoring.trigger_info(ctx_of(self.snapshots["v2"]))["Forbidden Rite of Soul Sacrifice"]
        v1 = scoring.trigger_info(ctx_of(self.snapshots["v1"]))["Forbidden Rite of Soul Sacrifice"]

        self.assertEqual(v4["rate"], 7.524)
        self.assertAlmostEqual(v4["cap"], 7.5757, places=3)
        self.assertFalse(v4["atCap"])
        self.assertEqual(v4["why"], "limited by the trigger source: Cyclone at 7.52/s")
        self.assertEqual(v2["rate"], v2["sourceRate"])
        self.assertLess(v2["rate"], v2["cap"])
        self.assertTrue(v2["why"].startswith("limited by the trigger source"))
        self.assertEqual(v1["why"],
                         "Cyclone attack rate 10.03/s overshoots the 7.57/s cap: only 50% of attacks "
                         "trigger (about every 2nd attack); see breakpoints (B5)")

    def test_trigger_overshoot_why_ordinals_and_omitted_approximation(self):
        for n, ordinal in ((2, "2nd"), (3, "3rd"), (4, "4th"), (11, "11th"), (21, "21st")):
            with self.subTest(n=n):
                text = scoring.trigger_overshoot_why(21 / n, 15, 21, "Cyclone")
                self.assertIn(f"about every {ordinal} attack", text)
        text = scoring.trigger_overshoot_why(10, 10.5, 11, "")
        self.assertEqual(text,
                         "trigger source attack rate 11.00/s overshoots the 10.50/s cap: only 90% of "
                         "attacks trigger; see breakpoints (B5)")

    def test_trigger_overshoot_why_rejects_non_overshoots(self):
        cases = [
            (7, 7, 10), (5, 7, 7), (0, 7, 10), (None, 7, 10),
            (5, None, 10), (5, 7, None),
        ]
        for rate, cap, source in cases:
            with self.subTest(rate=rate, cap=cap, source=source):
                self.assertIsNone(scoring.trigger_overshoot_why(rate, cap, source, "Cyclone"))

    def test_trigger_shortfall_below_source_and_cap_keeps_generic_text(self):
        ctx = {"skills": [{"name": "Cyclone", "isAttack": True, "out": {}}, {
            "name": "Triggered", "isAttack": False, "out": {
                "SkillTriggerRate": 5, "TriggerRateCap": 10, "EffectiveSourceRate": 8,
            }}]}

        self.assertEqual(scoring.trigger_info(ctx)["Triggered"]["why"],
                         "below the cap and below the source rate (8.00/s); PoB gives no further reason")

    def test_zero_trigger_cap_and_source_are_absent(self):
        ctx = {"skills": [{"name": "Triggered", "isAttack": False, "out": {
            "SkillTriggerRate": 0, "TriggerRateCap": 0, "EffectiveSourceRate": 0,
        }}]}

        info = scoring.trigger_info(ctx)["Triggered"]

        self.assertEqual(info, {"rate": 0, "cap": None, "sourceRate": None,
                                "atCap": False, "why": None})

    def test_combined_dps_fallback_warns_and_empty_skills_have_no_changes(self):
        ctx = {"skills": [{"name": "Fallback", "isMain": True,
                           "out": {"FullDPS": 0, "CombinedDPS": 1000}}], "skillDPS": []}

        self.assertEqual(scoring.dps_measure(ctx), {
            "key": "CombinedDPS",
            "warning": "No skill group is in Full DPS ('Include in Full DPS' unticked): "
                       "DPS % uses the main skill Fallback only",
        })
        self.assertEqual(scoring.skill_changes(ctx, ctx), [])

    def test_combined_dps_fallback_accepts_all_empty_lua_shapes(self):
        warning = "No skill group is in Full DPS ('Include in Full DPS' unticked): " \
                  "DPS % uses the main skill Fallback only"
        for out in ([], {}, {"CombinedDPS": 1000}):
            with self.subTest(out=out):
                ctx = {"skills": [{"name": "Fallback", "isMain": True, "out": out}]}
                self.assertEqual(scoring.dps_measure(ctx), {"key": "CombinedDPS", "warning": warning})

    def test_skill_out_and_auditor_main_out_normalize_non_dict_values(self):
        value = {"CombinedDPS": 1000}
        self.assertEqual(scoring.skill_out({"out": []}), {})
        self.assertEqual(scoring.skill_out({"out": None}), {})
        self.assertIs(scoring.skill_out({"out": value}), value)
        ctx = {"skills": [{"name": "Main", "isMain": True, "out": []}]}
        self.assertEqual(Auditor.main_out(ctx), {})

    def test_model_updates_full_dps_skill_row_count_without_mutation(self):
        ctx = {
            "skills": [{"name": "Winter Orb", "isMain": True, "count": 5, "out": {
                "FullDPS": 7176019.1459774, "ProjectileCount": 6, "AreaOfEffectRadius": 26,
            }}],
            "skillDPS": [{"name": "Winter Orb", "dps": 1435203.8291955, "count": 5,
                          "trigger": None, "skillPart": "Channelling"}],
        }
        original = copy.deepcopy(ctx)
        model = models.Model(name="t", status="verified", spec={
            "kind": "line_overlap", "applies_to": {"skill": "Winter Orb"},
            "multiplies": ["FullDPS"], "params": {"spacing_m": 1.4, "enemy_radius_m": 0.5},
        })

        adjusted = models.apply_models([model], ctx, set())
        row = adjusted["skillDPS"][0]
        main = adjusted["skills"][0]

        self.assertEqual(row["count"], main["models"][0]["multiplier"])
        self.assertEqual(row["pobCount"], 5)
        self.assertAlmostEqual(row["dps"] * row["count"], main["out"]["FullDPS"], places=6)
        self.assertEqual(ctx, original)

    def test_model_without_full_dps_does_not_update_rows(self):
        rows = [{"name": "Winter Orb", "dps": 10, "count": 5}]
        ctx = {"skills": [{"name": "Main", "isMain": True, "out": {}},
                          {"name": "Winter Orb", "isMain": False, "count": 5,
                           "out": {"ProjectileCount": 6, "AreaOfEffectRadius": 26}}],
               "skillDPS": rows}
        model = models.Model(name="t", status="verified", spec={
            "kind": "line_overlap", "applies_to": {"skill": "Winter Orb"},
            "multiplies": ["FullDPS"], "params": {"spacing_m": 1.4, "enemy_radius_m": 0.5},
        })

        adjusted = models.apply_models([model], ctx, set())

        self.assertEqual(adjusted["skillDPS"], rows)

    def test_equal_contributions_sort_by_name_then_part(self):
        ctx = {"skillDPS": [
            {"name": "Beta", "skillPart": None, "dps": 10, "count": 1},
            {"name": "Alpha", "skillPart": "Two", "dps": 5, "count": 2},
            {"name": "Alpha", "skillPart": "One", "dps": 10, "count": 1},
        ]}

        rows = scoring.skill_rows(ctx)
        changes = scoring.skill_changes(ctx, ctx)

        expected = [("Alpha", "One"), ("Alpha", "Two"), ("Beta", None)]
        self.assertEqual([(row["name"], row["part"]) for row in rows], expected)
        self.assertEqual([(row["name"], row["part"]) for row in changes], expected)


if __name__ == "__main__":
    unittest.main()
