"""Fast unit tests for rule applicability."""

import sys
import unittest
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from audit import protected_supports  # noqa: E402
from rules import applies, violations  # noqa: E402
from vault import Rule  # noqa: E402


def context(supports: list[str], mana_cost: float = 0) -> dict:
    return {"supports": supports, "keystones": [], "usedTogether": [], "skills": [{
        "name": "Main", "isMain": True, "isAttack": False, "out": {"ManaCost": mana_cost},
    }]}


def mana_rule(**spec: object) -> Rule:
    return Rule("Arcane Surge needs mana", "verified", "validity", {
        **spec, "require": [{"stat": "ManaCost", "op": ">", "value": 0}],
    })


class RuleConditionTests(unittest.TestCase):
    def test_linked_support_condition_applies_and_checks_requirement(self):
        rule = mana_rule(when_support_linked=["SupportArcaneSurge"])

        broken = violations([rule], context(["SupportArcaneSurge"], 0))

        self.assertEqual(len(broken), 1)
        self.assertTrue(broken[0].startswith("[Arcane Surge needs mana]"))
        self.assertEqual(violations([rule], context(["SupportArcaneSurge"], 25)), [])

    def test_linked_support_condition_does_not_apply_when_unlinked(self):
        rule = mana_rule(when_support_linked=["SupportArcaneSurge"])

        self.assertEqual(violations([rule], context([], 0)), [])

    def test_top_level_and_nested_support_conditions_must_both_match(self):
        rule = mana_rule(when={"linked_support_any": ["SupportCastOnCrit"]},
                         when_support_linked=["SupportArcaneSurge"])

        self.assertFalse(applies(rule, context(["SupportArcaneSurge"])))
        self.assertFalse(applies(rule, context(["SupportCastOnCrit"])))
        self.assertTrue(applies(rule, context(["SupportArcaneSurge", "SupportCastOnCrit"])))

    def test_linked_support_condition_rejects_non_list_values(self):
        rule = mana_rule(when_support_linked="SupportArcaneSurge")

        with self.assertRaisesRegex(
                ValueError,
                "rule 'Arcane Surge needs mana': when_support_linked must be a list of granted effect ids"):
            applies(rule, context(["SupportArcaneSurge"]))

    def test_only_nested_condition_protects_a_support_from_swaps(self):
        top_level = mana_rule(when_support_linked=["SupportArcaneSurge"])
        nested = mana_rule(when={"linked_support_any": ["SupportCastOnCriticalStrike"]})

        self.assertEqual(protected_supports([top_level]), [])
        self.assertEqual(protected_supports([nested]), ["SupportCastOnCriticalStrike"])


if __name__ == "__main__":
    unittest.main()
