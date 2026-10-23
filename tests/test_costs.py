"""Engine-free unit tests for resource costs and conditional scenarios."""

import copy
import json
import sys
import types
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden_common as gc  # noqa: E402

import costs  # noqa: E402
from audit import Auditor  # noqa: E402
from rules import violations  # noqa: E402
from vault import Rule  # noqa: E402


def context(skills: list[dict], extras: list[dict] | None = None,
            keystones: list[str] | None = None) -> dict:
    return {"skills": skills, "usedTogether": extras or [], "supports": [],
            "keystones": keystones or []}


def sum_rule(stat: str, ref: str, allow_deficit: dict | None = None) -> Rule:
    requirement = {"sum_over_skill_set": stat, "op": "<=", "ref": ref}
    if allow_deficit:
        requirement["allow_deficit"] = allow_deficit
    return Rule("r", "verified", "validity", {"require": [requirement]})


def golden_context(snapshot: dict, with_extras: bool = False) -> dict:
    extras = []
    if with_extras:
        extras = [{"name": row["name"], "group": row["group"], "out": row["out"]}
                  for row in snapshot["otherGroups"]
                  if "SkillTriggerRate" in row["out"] and row["name"] != "Tempest Shield"
                  and any((row["out"].get(costs.KEYS[r]["cost"]) or 0) > 0 for r in costs.RESOURCES)]
    return context(snapshot["skills"], extras)


class RuleCostTests(unittest.TestCase):
    def test_zero_sum_skips_even_with_negative_regen(self):
        ctx = context([{"name": "Righteous Fire", "isMain": True,
                        "out": {"ManaPerSecondCost": 0, "ManaRegenRecovery": -50}}])

        self.assertEqual(violations([sum_rule("ManaPerSecondCost", "ManaRegenRecovery")], ctx), [])

    def test_deficit_seconds_are_floored(self):
        rule = sum_rule("ManaPerSecondCost", "ManaRegenRecovery",
                        {"pool": "ManaUnreserved", "min_seconds": 30})
        skills = [{"name": "Main", "isMain": True,
                   "out": {"ManaPerSecondCost": 100, "ManaRegenRecovery": 100, "ManaUnreserved": 600}},
                  {"name": "Second", "isMain": False, "out": {"ManaPerSecondCost": 23.3}}]

        broken = violations([rule], context(skills))
        skills[0]["out"]["ManaUnreserved"] = 700

        self.assertIn("25s", broken[0])
        self.assertNotIn("26s", broken[0])
        self.assertEqual(violations([rule], context(skills)), [])

    def test_es_cost_without_deficit_fails_only_above_regen(self):
        rule = sum_rule("ESPerSecondCost", "EnergyShieldRegenRecovery")
        skill = {"name": "Main", "isMain": True,
                 "out": {"ESPerSecondCost": 2300, "EnergyShieldRegenRecovery": 2251}}

        self.assertEqual(len(violations([rule], context([skill]))), 1)
        skill["out"]["EnergyShieldRegenRecovery"] = 2300
        self.assertEqual(violations([rule], context([skill])), [])

    def test_rules_sum_and_check_used_together_extras(self):
        main = {"name": "Main", "isMain": True,
                "out": {"ESPerSecondCost": 40, "EnergyShieldRegenRecovery": 50,
                        "ESCost": 1, "EnergyShield": 10}}
        extra = {"name": "Extra", "group": 7,
                 "out": {"ESPerSecondCost": 20, "ESCost": 11, "EnergyShield": 10}}
        each = Rule("each", "verified", "validity", {
            "require": [{"each_skill": "ESCost", "op": "<=", "ref": "EnergyShield"}]})

        self.assertEqual(len(violations([sum_rule("ESPerSecondCost", "EnergyShieldRegenRecovery")],
                                        context([main], [extra]))), 1)
        self.assertIn("Extra", violations([each], context([main], [extra]))[0])


class CostFunctionTests(unittest.TestCase):
    def test_gate4_consecrated_lines_verbatim(self):
        cfg = {"conditionOnConsecratedGround": {
            "value": True, "only_if": "build_has_consecrated_ground_source"}}
        stationary = "You have Consecrated Ground around you while stationary"
        source = {"kind": "tree", "name": "Sanctuary", "line": stationary}
        match = costs.consecrated_source(stationary)
        self.assertIsNotNone(match)
        self.assertFalse(match["conditional"])
        plan = costs.plan_conditional(cfg, [source])[0]
        self.assertTrue(plan["applied"])
        self.assertEqual(plan["source"], f"Sanctuary: {stationary}")

        for line in ("Create Profane Ground instead of Consecrated Ground",
                     "Create Fungal Ground instead of Consecrated Ground"):
            self.assertIsNone(costs.consecrated_source(line))
        for line in ("10% chance to create Consecrated Ground on Melee Kill, lasting 4 seconds",
                     "Create Consecrated Ground when you Shatter an Enemy"):
            match = costs.consecrated_source(line)
            self.assertIsNotNone(match)
            self.assertTrue(match["conditional"])
            row = costs.plan_conditional(cfg, [{"kind": "tree", "name": "Source", "line": line}])[0]
            self.assertFalse(row["applied"])

    def test_cost_dims_requires_matching_used_together_counts(self):
        base_main = {"name": "Main", "isMain": True, "out": {
            "ESPerSecondCost": 30, "EnergyShieldRegenRecovery": 50}}
        base_extra = {"name": "Extra", "group": 2, "out": {"ESPerSecondCost": 10}}
        changed_main = {"name": "Main", "isMain": True, "out": {
            "ESPerSecondCost": 20, "EnergyShieldRegenRecovery": 50}}
        changed_extra = {"name": "Extra", "group": 2, "out": {"ESPerSecondCost": 5}}

        self.assertEqual(costs.cost_dims(context([changed_main]), context([base_main], [base_extra])), {})
        self.assertEqual(costs.cost_dims(context([changed_main], [changed_extra]),
                                         context([base_main], [base_extra])),
                         {"ES": {"from": 10, "to": 25}})

    def test_auditor_extra_request_shape(self):
        stub = types.SimpleNamespace(extra_skills=[
            {"group": 2, "index": 3, "name": "Assassin's Mark"},
            {"group": 7, "index": 2, "name": "Withering Step"},
        ])

        self.assertEqual(Auditor.extra_request(stub), [
            {"group": 2, "index": 3}, {"group": 7, "index": 2}])

    def test_margin_pool_floor_no_cost_and_es_recharge(self):
        main = {"name": "Main", "isMain": True, "out": {
            "ESPerSecondCost": 30, "EnergyShieldRegenRecovery": 20, "EnergyShield": 99,
            "EnergyShieldRecharge": 11876.9, "EnergyShieldRechargeDelay": 1.909,
        }}
        extra = {"name": "Extra", "group": 2, "out": {"ESPerSecondCost": 3}}
        ctx = context([main], [extra])
        original = copy.deepcopy(ctx)

        result = costs.margin(ctx, "ES")

        self.assertEqual(result["lines"], [{"name": "Main", "value": -30, "group": None},
                                           {"name": "Extra", "value": -3, "group": 2}])
        self.assertEqual((result["total"], result["margin"], result["poolSeconds"]), (33, -13, 7))
        self.assertEqual(result["recharge"]["text"], "+11,876/s, only after 1.90 s without damage")
        self.assertFalse(costs.margin(ctx, "Mana")["hasCost"])
        self.assertEqual(ctx, original)

    def test_classify_other_skills(self):
        rows = [
            {"group": 7, "index": 2, "name": "Trigger", "triggered": True, "reactive": False,
             "reactiveBy": None, "out": {"ESPerSecondCost": 14}},
            {"group": 2, "index": 3, "name": "Self", "triggered": False, "reactive": False,
             "reactiveBy": None, "out": {"LifePerSecondCost": 8}},
            {"group": 6, "index": 1, "name": "Damage", "triggered": True, "reactive": True,
             "reactiveBy": "skillData.triggeredByDamageTaken", "out": {"ManaPerSecondCost": 321.2}},
            {"group": 4, "index": 2, "name": "Block", "triggered": True, "reactive": True,
             "reactiveBy": "Support (trigger_effect_group_on_block)", "out": {"ESPerSecondCost": 2}},
            {"group": 1, "index": 1, "name": "Free", "triggered": True, "reactive": False,
             "reactiveBy": None, "out": {"ManaPerSecondCost": 0}},
            {"group": 8, "index": 1, "name": "Empty", "triggered": True, "reactive": False,
             "reactiveBy": None, "out": []},
        ]

        extra, excluded = costs.classify_other_skills(rows)

        self.assertEqual(extra, [{"group": 7, "index": 2, "name": "Trigger"}])
        self.assertEqual([row["name"] for row in excluded], ["Self", "Block", "Damage"])
        self.assertTrue(excluded[0]["reason"].startswith("self-cast"))
        self.assertEqual(excluded[1]["reason"], "triggered by block: rate depends on hits you take")
        self.assertEqual(excluded[2]["reason"], "triggered by damage taken: rate depends on hits you take")

    def test_plan_conditional_requires_real_source_and_validates_first(self):
        lines = [
            {"kind": "item", "name": "Bottled Faith, Sulphur Flask",
             "line": "133% increased Critical Strike Chance against Enemies on Consecrated Ground during Effect"},
            {"kind": "item", "name": "Bottled Faith, Sulphur Flask",
             "line": "Consecrated Ground created by this Flask has Tripled Radius"},
            {"kind": "item", "name": "Bottled Faith, Sulphur Flask",
             "line": "Consecrated Ground created during Effect applies 10% increased Damage taken to Enemies"},
            {"kind": "item", "name": "Bottled Faith, Sulphur Flask",
             "line": "Creates Consecrated Ground on Use"},
        ]
        cfg = {"conditionOnConsecratedGround": {
            "value": True, "only_if": "build_has_consecrated_ground_source"}}

        applied = costs.plan_conditional(cfg, lines)
        absent = costs.plan_conditional(cfg, lines[:-1])
        empty = costs.plan_conditional(cfg, [])

        self.assertEqual(applied[0]["source"],
                         "Bottled Faith, Sulphur Flask: Creates Consecrated Ground on Use")
        self.assertTrue(applied[0]["applied"])
        self.assertEqual(applied[0]["conditionalSources"], [])
        self.assertEqual((absent[0]["applied"], absent[0]["source"]), (False, None))
        self.assertEqual(absent[0]["conditionalSources"], [])
        self.assertEqual(empty[0], {"var": "conditionOnConsecratedGround", "value": True,
                                    "applied": False, "source": None, "conditionalSources": []})
        self.assertEqual(costs.plan_conditional(None, lines), [])
        self.assertEqual(costs.plan_conditional({}, lines), [])
        with self.assertRaises(ValueError):
            costs.plan_conditional({"bad": {"value": True, "only_if": "unknown"}}, lines)

    def test_consecrated_always_sources_apply_case_and_whitespace_insensitively(self):
        cfg = {"conditionOnConsecratedGround": {
            "value": True, "only_if": "build_has_consecrated_ground_source"}}
        lines = [
            {"kind": "item", "name": "Bottled Faith, Sulphur Flask",
             "line": "  Creates Consecrated Ground on Use  "},
            {"kind": "tree", "name": "Sanctuary",
             "line": "YOU HAVE CONSECRATED GROUND AROUND YOU WHILE STATIONARY"},
        ]
        for line in lines:
            with self.subTest(line=line["line"]):
                match = costs.consecrated_source(line["line"])
                self.assertIsNotNone(match)
                self.assertFalse(match["conditional"])
                plan = costs.plan_conditional(cfg, [line])[0]
                self.assertTrue(plan["applied"])
                self.assertEqual(plan["source"], f"{line['name']}: {line['line']}")

    def test_consecrated_conditional_sources_stay_off_and_are_reported(self):
        cfg = {"conditionOnConsecratedGround": {
            "value": True, "only_if": "build_has_consecrated_ground_source"}}
        cases = [
            ("on kill", "10% chance to create Consecrated Ground on Melee Kill, lasting 4 seconds"),
            ("on kill", "Create Consecrated Ground when you Kill an Enemy"),
            ("on hit", "Create Consecrated Ground on Hit, lasting 4 seconds"),
            ("on hit", "10% chance to create Consecrated Ground when you Hit a Rare or Unique Enemy, lasting 8 seconds"),
            ("on hit", "Create Consecrated Ground, lasting 8 seconds, when you Hit a Magic, Rare or Unique Enemy, up to once every 10 seconds"),
            ("when hit", "25% chance to create Consecrated Ground when Hit, lasting 8 seconds"),
            ("on death", "100% chance to create Consecrated Ground on Death, lasting 8 seconds"),
            ("on block", "25% chance to create Consecrated Ground when you Block"),
            ("on crit", "Creates Consecrated Ground on Critical Strike"),
            ("on crit", "10% chance on Critical Strike to create Consecrated Ground"),
            ("on shatter", "100% chance to create Consecrated Ground when you Shatter an Enemy"),
            ("Purifying Flame", "Purifying Flame also creates Consecrated Ground around you"),
            ("Purifying Flame", "Puryfing Flame has 20% chance to also create Consecrated Ground around you"),
            ("Rational Doctrine", "You have Consecrated Ground around you while Stationary if Strength is your highest Attribute"),
            ("Rational Doctrine", "You have Consecrated Ground around you while"),
            ("Bound by Destiny", "Consecrated Ground around you while Stationary if 5 Shaper Items are Equipped"),
            ("Zealotry", "Aura gives a chance to create Consecrated Ground against Stronger Enemies."),
        ]
        for label, line in cases:
            with self.subTest(label=label, line=line):
                match = costs.consecrated_source(line)
                self.assertIsNotNone(match)
                self.assertTrue(match["conditional"])
                row = {"kind": "item", "name": "Source", "line": line}
                plan = costs.plan_conditional(cfg, [row])[0]
                self.assertFalse(plan["applied"])
                self.assertIsNone(plan["source"])
                self.assertEqual(plan["conditionalSources"], [
                    f"conditional source (off): Source: {line} ({label})"])

    def test_consecrated_excluded_texts_do_not_match(self):
        lines = [
            "Create Profane Ground instead of Consecrated Ground",
            "Create Fungal Ground instead of Consecrated Ground",
            "133% increased Critical Strike Chance against Enemies on Consecrated Ground during Effect",
            "20% increased Damage while on Consecrated Ground",
            "Effects of Consecrated Ground you create linger for 4 seconds",
            "Consecrated Ground you create applies 15% increased Damage taken to Enemies",
            "Consecrated Ground created by this Flask has Tripled Radius",
            "Consecrated Ground created during Effect applies 10% increased Damage taken to Enemies",
            "30% increased Effect of Consecrated Ground you create",
            "Gain Arcane Surge for 4 seconds when you create Consecrated Ground while affected by Zealotry",
            "Inflict Hallowing Flame on Rare or Unique Enemies when you Hit them while on Consecrated Ground",
        ]
        for line in lines:
            with self.subTest(line=line):
                self.assertIsNone(costs.consecrated_source(line))

    def test_plan_conditional_prefers_always_source_and_sorts_conditional_sources(self):
        cfg = {"conditionOnConsecratedGround": {
            "value": True, "only_if": "build_has_consecrated_ground_source"}}
        conditional = {"kind": "item", "name": "Zed",
                       "line": "Creates Consecrated Ground on Critical Strike"}
        always = {"kind": "item", "name": "Alpha", "line": "Creates Consecrated Ground on Use"}
        row = costs.plan_conditional(cfg, [conditional, always, conditional])[0]
        self.assertTrue(row["applied"])
        self.assertEqual(row["source"], "Alpha: Creates Consecrated Ground on Use")
        self.assertEqual(row["conditionalSources"], [
            "conditional source (off): Zed: Creates Consecrated Ground on Critical Strike (on crit)"])

    def test_eldritch_battery_marks_es_outputs_unverified(self):
        main = {"name": "Main", "isMain": True, "out": {
            "ESPerSecondCost": 120, "EnergyShieldRegenRecovery": 20, "EnergyShield": 1000}}
        base = context([main], keystones=[costs.ELDRITCH_BATTERY])
        changed = context([{**main, "out": {**main["out"], "ESPerSecondCost": 110}}],
                          keystones=[costs.ELDRITCH_BATTERY])
        note = costs.ES_UNVERIFIED

        self.assertEqual(costs.margin(base, "ES")["unverified"], note)
        self.assertEqual(costs.cost_dims(changed, base)["ES"]["unverified"], note)
        self.assertEqual(costs.kpi_entries(base)[0]["unverified"], note)
        self.assertTrue(costs.dims_text(costs.cost_dims(changed, base)).endswith(f" [{note}]"))
        broken = violations([sum_rule("ESPerSecondCost", "EnergyShieldRegenRecovery")], base)
        self.assertTrue(broken[0].endswith(f" [{note}]"))

    def test_es_outputs_are_unchanged_without_eldritch_battery(self):
        main = {"name": "Main", "isMain": True, "out": {
            "ESPerSecondCost": 120, "EnergyShieldRegenRecovery": 20, "EnergyShield": 1000}}
        base = context([main])
        changed = context([{**main, "out": {**main["out"], "ESPerSecondCost": 110}}])

        self.assertEqual(costs.margin(base, "ES"), {
            "resource": "ES", "regen": 20,
            "lines": [{"name": "Main", "value": -120, "group": None}],
            "total": 120, "margin": -100, "pool": 1000, "poolSeconds": 10,
            "hasCost": True, "recharge": {"perSecond": 0, "delay": None, "text": "none"},
        })
        self.assertEqual(costs.cost_dims(changed, base), {"ES": {"from": -100, "to": -90}})
        self.assertNotIn("unverified", costs.kpi_entries(base)[0])
        self.assertEqual(costs.dims_text(costs.cost_dims(changed, base)),
                         " | ES margin -100 -> -90/s")
        self.assertEqual(violations(
            [sum_rule("ESPerSecondCost", "EnergyShieldRegenRecovery")], base),
            ["[r] total ESPerSecondCost 120.0 vs EnergyShieldRegenRecovery 20.0"])


class GoldenCostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        golden = json.loads(gc.GOLDEN_PATH.read_text(encoding="utf-8"))
        cls.snapshots = {key: value["snapshot"] for key, value in golden["raw"].items()}

    def test_main_group_es_margins(self):
        expected = {"v2": 695.6, "v4": 1084.4, "source": 1077.0}
        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertEqual(round(costs.margin(golden_context(self.snapshots[key]), "ES")["margin"], 1), value)

    def test_triggered_extras_es_margins_v2_v4_and_source_1031_946(self):
        v2 = costs.margin(golden_context(self.snapshots["v2"], True), "ES")["margin"]
        v4 = costs.margin(golden_context(self.snapshots["v4"], True), "ES")["margin"]
        source = costs.margin(golden_context(self.snapshots["source"], True), "ES")["margin"]
        source_expected = 2692.2 - 60.192 - 1554.96 - 19.783104 - 4 * 2.8333333333333 - 13.986013986014

        self.assertEqual(round(v2, 1), 661.9)
        self.assertEqual(round(v4, 1), 1051.0)
        self.assertAlmostEqual(source, source_expected, places=3)

    def test_ek_mana_margin_and_auditor_delegate(self):
        ctx = golden_context(self.snapshots["EK"])
        value = costs.margin(ctx, "Mana")["margin"]

        self.assertEqual(round(value, 1), 21.9)
        self.assertEqual(Auditor.mana_margin(ctx), value)


if __name__ == "__main__":
    unittest.main()
