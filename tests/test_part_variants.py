"""Fast synthetic tests for per-part values on shown suggestions."""

import ast
import json
import sys
import unittest
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

import models  # noqa: E402
import part_variants  # noqa: E402
import scoring  # noqa: E402
from audit import Auditor  # noqa: E402
from display import fmt_pct  # noqa: E402


def context(dps: float, part: str, projectiles: float, skill_dps: float | None = None,
            name: str = "Main", part_index: int = 1, part_count: int = 2) -> dict:
    return {
        "skills": [{"name": name, "isMain": True, "part": part,
                    "partIndex": part_index, "partCount": part_count,
                    "out": {"FullDPS": dps, "ProjectileCount": projectiles,
                            "TotalEHP": 100, "PhysicalMaximumHitTaken": 100}, "models": []}],
        "skillDPS": [{"name": name, "skillPart": part, "dps": skill_dps or dps, "count": 1}],
    }


def alt(skill: str, index: int, name: str, ctx: dict) -> dict:
    return {"skill": skill, "partIndex": index, "partName": name, "ctx": ctx}


class Obtainable:
    @staticmethod
    def gem_obtainable(_name: str) -> bool:
        return True


class SwapAuditor:
    rules: list = []
    _swap_levels = {}
    obtainable = Obtainable()
    keys = ["FullDPS", "ProjectileCount"]
    dps_key = "FullDPS"
    capability_keys: list[str] = []

    def __init__(self, multi_part: bool) -> None:
        self.multi_part = multi_part
        self.suggestions: list[dict] = []
        self.calls: list[tuple[str, dict]] = []
        self.base = context(100, "Saved", 1)
        self.first_swaps = [
            {"replaced": "Old", "with": "Winner", "level": 20, "quality": 20,
             "ctx": context(120, "Saved", 1)},
            {"replaced": "Other", "with": "Runner Up", "level": 20, "quality": 20,
             "ctx": context(110, "Saved", 1)},
            {"replaced": "Bad", "with": "Alt Star", "level": 20, "quality": 20,
             "ctx": context(90, "Saved", 1)},
        ]

    @staticmethod
    def extra_request() -> list:
        return []

    def call(self, function: str, request: dict) -> dict:
        self.calls.append((function, request))
        if "candidates" not in request:
            return {"base": self.base, "swaps": self.first_swaps}
        base = {**self.base, "byPart": [alt("Main", 2, "Alternate", context(200, "Alternate", 5, part_index=2))]}
        swaps = []
        for candidate in request["candidates"]:
            first = next(row for row in self.first_swaps
                         if (row["replaced"], row["with"]) == (candidate["replaced"], candidate["with"]))
            alt_dps = 50 if candidate["with"] == "Winner" else 260
            swaps.append({**first, "ctx": {**first["ctx"], "byPart": [
                alt("Main", 2, "Alternate", context(alt_dps, "Alternate", 5, part_index=2))
            ]}})
        return {"base": base, "swaps": swaps}

    @staticmethod
    def adjust(ctx: dict) -> dict:
        return ctx

    @staticmethod
    def breaks(_ctx: dict) -> list:
        return []

    @staticmethod
    def main_out(ctx: dict) -> dict:
        return scoring.skill_out(next(skill for skill in ctx["skills"] if skill["isMain"]))

    def dimensions(self, ctx: dict, base_ctx: dict) -> dict:
        dims = {"dps": scoring.change_pct(self.main_out(ctx)["FullDPS"],
                                           self.main_out(base_ctx)["FullDPS"]), "skills": []}
        return {**dims, "parts": part_variants.parts_dims(ctx, base_ctx, dims, self.dps_key)}

    def suggest(self, change: dict) -> int:
        self.suggestions.append(change)
        return len(self.suggestions)


class PartVariantTests(unittest.TestCase):
    def test_skill_changes_carries_new_projectiles_and_prefers_matching_part(self):
        base = context(100, "One", 1)
        changed = context(120, "One", 3)
        changed["skills"].insert(0, {"name": "Main", "isMain": False, "part": "Other",
                                    "out": {"ProjectileCount": 9}})
        self.assertEqual(scoring.skill_changes(changed, base)[0]["projectiles"], 3)
        self.assertIsNone(scoring.skill_changes({"skills": [], "skillDPS": changed["skillDPS"]}, base)[0]["projectiles"])

    def test_skill_change_labels_include_available_part_and_projectiles(self):
        rows = [
            {"name": "Forbidden Rite of Soul Sacrifice", "part": "1 Projectile", "projectiles": 5.9, "pct": 32.19},
            {"name": "Cyclone", "part": None, "projectiles": 1, "pct": -4.09},
            {"name": "Cyclone", "part": None, "projectiles": None, "pct": -4.09},
        ]
        self.assertEqual(scoring.skill_pcts_text(rows, 3),
                         "Forbidden Rite of Soul Sacrifice (1 Projectile, 5 proj) +32.1%, "
                         "Cyclone (1 proj) -4.0%, Cyclone -4.0%")

    def test_parts_dims_and_text_use_raw_pob_values(self):
        base = context(16780000.0, "1 Projectile", 1)
        changed = context(29020000.0, "1 Projectile", 1)
        base["byPart"] = [alt("Main", 2, "All Primary Projectiles",
                              context(99480000.0, "All Primary Projectiles", 5, part_index=2))]
        changed["byPart"] = [alt("Main", 2, "All Primary Projectiles",
                                 context(57690000.0, "All Primary Projectiles", 5, part_index=2))]
        dims = {"dps": scoring.change_pct(29020000.0, 16780000.0), "skills": []}
        parts = part_variants.parts_dims(changed, base, dims, "FullDPS")
        self.assertEqual([row["saved"] for row in parts], [True, False])
        self.assertEqual(parts[0]["dps"], dims["dps"])
        self.assertAlmostEqual(parts[1]["dps"], -42.01, places=2)
        self.assertEqual([fmt_pct(row["dps"]) for row in parts], ["+72.9%", "-42.0%"])
        self.assertTrue(parts[1]["skills"])
        self.assertEqual(part_variants.parts_text({"parts": parts}),
                         "parts: 1 Projectile (saved) +72.9% | All Primary Projectiles -42.0%")

    def test_parts_dims_requires_both_variant_lists(self):
        base, changed = context(100, "Saved", 1), context(110, "Saved", 1)
        dims = {"dps": 10, "skills": []}
        self.assertEqual(part_variants.parts_dims(changed, {**base, "byPart": []}, dims, "FullDPS"), [])
        self.assertEqual(part_variants.parts_dims({**changed, "byPart": []}, base, dims, "FullDPS"), [])
        self.assertEqual(part_variants.parts_text({"parts": []}), "")

    def test_missing_base_alt_is_na(self):
        base = {**context(100, "Saved", 1), "byPart": [alt("Main", 3, "Other", context(300, "Other", 3))]}
        changed = {**context(110, "Saved", 1), "byPart": [alt(
            "Main", 2, "Alternate", context(220, "Alternate", 2, part_index=2))]}
        parts = part_variants.parts_dims(changed, base, {"dps": 10, "skills": []}, "FullDPS")
        self.assertIsNone(parts[1]["dps"])
        self.assertEqual(parts[1]["skills"], [])
        self.assertEqual(part_variants.parts_text({"parts": parts}),
                         "parts: Saved (saved) +10.0% | Alternate n/a")

    def test_two_skills_prefix_labels_and_each_gets_saved_row(self):
        base = context(100, "Main Saved", 1)
        changed = context(110, "Main Saved", 1)
        base["skills"].append({"name": "Other", "isMain": False, "part": "Other Saved", "partCount": 2,
                               "partIndex": 1, "out": {"FullDPS": 20}})
        for target, value in ((base, 20), (changed, 25)):
            target["byPart"] = [
                alt("Main", 2, "Main Alt", context(200 if target is base else 220, "Main Alt", 2, name="Main")),
                alt("Other", 2, "Other Alt", context(value, "Other Alt", 2, name="Other")),
            ]
        parts = part_variants.parts_dims(changed, base, {"dps": 10, "skills": []}, "FullDPS")
        self.assertEqual([row["saved"] for row in parts], [True, False, True, False])
        text = part_variants.parts_text({"parts": parts})
        self.assertIn("Main: Main Saved (saved)", text)
        self.assertIn("Other: Other Saved (saved)", text)

    def test_adjust_copies_and_adjusts_nested_contexts(self):
        stub = type("Stub", (), {"models": [], "equipped": set()})()
        nested = context(200, "Alt", 2)
        source = {**context(100, "Saved", 1), "byPart": [alt("Main", 2, "Alt", nested)]}
        result = Auditor.adjust(stub, source)
        self.assertEqual(result["byPart"][0]["ctx"], nested)
        self.assertIsNot(result["byPart"][0]["ctx"], nested)
        stub.models = [models.Model("test", "verified", {"kind": "line_overlap", "applies_to": {"skill": "Main"},
                       "params": {"enemy_radius_m": 1, "spacing_m": 1}, "multiplies": ["FullDPS"]})]
        modelled = Auditor.adjust(stub, source)
        self.assertNotEqual(modelled["byPart"][0]["ctx"]["skills"][0]["out"]["FullDPS"], 200)

    def test_single_part_support_swaps_make_one_plain_call(self):
        auditor = SwapAuditor(False)
        result = Auditor.support_swaps(auditor)
        self.assertEqual(len(auditor.calls), 1)
        self.assertNotIn("partVariants", auditor.calls[0][1])
        self.assertNotIn("candidates", auditor.calls[0][1])
        self.assertTrue(all("partVariants" not in request for _, request in auditor.calls))
        self.assertNotIn("depends" + "OnPart", result)
        self.assertNotIn("depends" + "OnPartTotal", result)

    def test_multi_part_support_swaps_recalculate_only_shown_without_reranking(self):
        auditor = SwapAuditor(True)
        result = Auditor.support_swaps(auditor, top=2)
        self.assertEqual(len(auditor.calls), 2)
        first, second = auditor.calls[0][1], auditor.calls[1][1]
        self.assertNotIn("partVariants", first)
        self.assertNotIn("candidates", first)
        self.assertTrue(second["partVariants"])
        self.assertEqual(second["candidates"], [
            {"replaced": "Old", "with": "Winner"},
            {"replaced": "Other", "with": "Runner Up"},
        ])
        self.assertEqual([(row["id"], row["with"]) for row in result["items"]],
                         [(1, "Winner"), (2, "Runner Up")])
        self.assertEqual(result["items"][0]["dims"]["parts"][1]["dps"], -75)
        self.assertEqual(result["items"][1]["dims"]["parts"][1]["dps"], 30)
        self.assertNotIn("Alt Star", [row["with"] for row in result["items"]])

    def test_evaluate_and_with_parts_only_request_variants_for_multi_part(self):
        class Engine:
            def __init__(self) -> None:
                self.requests = []

            def run(self, code: str) -> str:
                payload = code.split("evaluateJSON(", 1)[1][:-1]
                request = json.loads(ast.literal_eval(payload))
                self.requests.append(request)
                return json.dumps(context(100, "Saved", 1))

        stub = type("Stub", (), {})()
        stub.engine = Engine()
        stub.keys = ["FullDPS"]
        stub.extra_skills = []
        stub.extra_request = lambda: []
        stub.models = []
        stub.equipped = set()
        stub.adjust = lambda ctx: Auditor.adjust(stub, ctx)
        stub.multi_part = False
        Auditor.evaluate(stub, parts=True)
        self.assertNotIn("partVariants", stub.engine.requests[-1])
        self.assertEqual(Auditor.with_parts(stub, {"x": 1}), {"x": 1})
        stub.multi_part = True
        Auditor.evaluate(stub, parts=True)
        self.assertTrue(stub.engine.requests[-1]["partVariants"])
        self.assertEqual(Auditor.with_parts(stub, {"x": 1}), {"x": 1, "partVariants": True})


if __name__ == "__main__":
    unittest.main()
