"""Real-build characterisation tests for guide comparison checks R4-R6."""

from __future__ import annotations

import json
import unittest
from contextlib import contextmanager

from tests import golden_common as gc
from tests import guide_testlib as gl

from guide_lua import apply_changes, ensure_loaded, evaluate_with, load_guide, snapshot
from pobhost import LuaError, PobEngine


STATS = gc.RAW_KEYS


def main_out(ctx: dict) -> dict:
    return next(skill["out"] for skill in ctx["skills"] if skill["isMain"])


@contextmanager
def loaded_engine(path):
    engine = PobEngine()
    try:
        engine.load_build(path)
        ensure_loaded(engine)
        yield engine
    finally:
        gc.close_engine(engine)


def item_at(data: dict, slot: str) -> dict:
    return next(item for item in data["items"] if item["slot"] == slot)


def full_dps(engine) -> float:
    return main_out(evaluate_with(engine, {"stats": STATS}))["FullDPS"]


class R4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ek_path = gc.build_path(gc.RAW_BUILDS["EK"])
        cls.scourge_path = gc.build_path("League Start ScourgeArrow Ice Spear.xml")
        if not cls.ek_path.is_file() or not cls.scourge_path.is_file():
            raise unittest.SkipTest("EK or ScourgeArrow Ice Spear build is missing")
        cls.guide_path = gl.decode_guide()
        with gc.pob_cwd(), loaded_engine(cls.ek_path) as engine:
            assert load_guide(engine, cls.guide_path, "pobb guide")["ok"]
            cls.guide = snapshot(engine, "guide")
        with gc.pob_cwd(), loaded_engine(cls.scourge_path) as engine:
            cls.scourge = snapshot(engine, "player")

    def _percentages(self, slot: str, raw: str) -> tuple[float, float]:
        with gc.pob_cwd():
            with loaded_engine(self.ek_path) as override_engine:
                base = full_dps(override_engine)
                request = {"stats": STATS, "repItem": {"slot": slot, "raw": raw}}
                override = main_out(evaluate_with(override_engine, request))["FullDPS"]
            with loaded_engine(self.ek_path) as apply_engine:
                result = apply_changes(apply_engine, [{"type": "item", "slot": slot, "raw": raw}], STATS)
                applied = main_out(result["ctx"])["FullDPS"]
        return 100 * (override - base) / base, 100 * (applied - base) / base

    def test_r4_cluster_override_misses_tree_reshape(self):
        raw = item_at(self.guide, "Jewel 13170")["raw"]
        override, applied = self._percentages("Jewel 13170", raw)
        self.assertEqual(override, 0)
        self.assertLess(applied, -1)

    def test_r4_timeless_override_misses_tree_reshape(self):
        raw = item_at(self.scourge, "Jewel 61834")["raw"]
        override, applied = self._percentages("Jewel 61419", raw)
        self.assertEqual(override, 0)
        self.assertLess(applied, -5)

    def test_r4_timeless_control_matches_apply(self):
        raw = next(item["raw"] for item in self.guide["items"] if item["title"] == "Militant Faith")
        override, applied = self._percentages("Jewel 61419", raw)
        self.assertAlmostEqual(override, applied, delta=1e-9)


class R5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ek_path = gc.build_path(gc.RAW_BUILDS["EK"])
        cls.vfos_path = gc.build_path("3.26/VFoS Berserker.xml")
        if not cls.ek_path.is_file() or not cls.vfos_path.is_file():
            raise unittest.SkipTest("EK or VFoS Berserker build is missing")

    def test_r5_two_handed_override_counts_offhand_but_apply_refuses(self):
        with gc.pob_cwd(), loaded_engine(self.vfos_path) as engine:
            self.assertTrue(load_guide(engine, self.ek_path, "EK guide")["ok"])
            guide = snapshot(engine, "guide")
            dagger, shield = item_at(guide, "Weapon 1"), item_at(guide, "Weapon 2")
            base = main_out(evaluate_with(engine, {"stats": STATS}))
            dagger_out = main_out(evaluate_with(engine, {"stats": STATS, "repItem": {
                "slot": "Weapon 1", "raw": dagger["raw"]}}))
            shield_out = main_out(evaluate_with(engine, {"stats": STATS, "repItem": {
                "slot": "Weapon 2", "raw": shield["raw"]}}))
            self.assertTrue(dagger_out)
            self.assertNotEqual(base["EnergyShield"], shield_out["EnergyShield"])
            with self.assertRaises(LuaError):
                apply_changes(engine, [{"type": "item", "slot": "Weapon 2", "raw": shield["raw"]}], STATS)

    def test_r5_two_handed_apply_matches_mainhand_override_and_clears_offhand(self):
        with gc.pob_cwd():
            with loaded_engine(self.ek_path) as override_engine:
                self.assertTrue(load_guide(override_engine, self.vfos_path, "VFoS guide")["ok"])
                axe = item_at(snapshot(override_engine, "guide"), "Weapon 1")
                overridden = main_out(evaluate_with(override_engine, {"stats": STATS, "repItem": {
                    "slot": "Weapon 1", "raw": axe["raw"]}}))["FullDPS"]
            with loaded_engine(self.ek_path) as apply_engine:
                result = apply_changes(apply_engine, [{"type": "item", "slot": "Weapon 1",
                                                        "raw": axe["raw"]}], STATS)
                self.assertEqual(overridden, main_out(result["ctx"])["FullDPS"])
                player = snapshot(apply_engine, "player")
                self.assertNotIn("Weapon 2", {item["slot"] for item in player["items"]})
                self.assertTrue(player["handedness"]["weapon1TwoHanded"])


class R6Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ek_path = gc.build_path(gc.RAW_BUILDS["EK"])
        if not cls.ek_path.is_file():
            raise unittest.SkipTest("EK build is missing")

    @staticmethod
    def _awakened(engine) -> dict:
        return json.loads(engine.run(r'''local group=build.skillsTab.socketGroupList[1]
for index,gem in ipairs(group.gemList) do
	local effect=gem.gemData and gem.gemData.grantedEffect
	if effect and effect.support then
		for _,gemId in ipairs(AuditCore.sortedKeys(data.gems)) do
			local candidate=data.gems[gemId]
			if candidate.grantedEffect.plusVersionOf==effect.id then
				return require("dkjson").encode({baseName=gem.gemData.name,baseIndex=index,
					name=candidate.name,gemId=gemId,level=candidate.naturalMaxLevel})
			end
		end
	end
end
error("no main-group support with an awakened version")'''))

    def test_r6_awakened_add_supersedes_plain_support(self):
        with gc.pob_cwd(), loaded_engine(self.ek_path) as engine:
            found = self._awakened(engine)
            gem = {"name": found["name"], "gemId": found["gemId"], "level": found["level"],
                   "quality": 20, "qualityId": "Default", "enabled": True}
            base = full_dps(engine)
            added = main_out(evaluate_with(engine, {"stats": STATS, "gemChange": {
                "type": "addSupport", "group": 1, "gem": gem}}))["FullDPS"]
            replaced = main_out(evaluate_with(engine, {"stats": STATS, "gemChange": {
                "type": "replaceSupport", "group": 1, "gemIndex": found["baseIndex"],
                "replaced": found["baseName"], "gem": gem}}))["FullDPS"]
            self.assertEqual(added, replaced)
            self.assertNotEqual(base, added)
        with gc.pob_cwd(), loaded_engine(self.ek_path) as engine:
            apply_changes(engine, [{"type": "addSupport", "group": 1, "gem": gem}], STATS)
            names = json.loads(engine.run(r'''local out={}; local group=build.skillsTab.socketGroupList[1]
for _,skill in ipairs(build.calcsTab.mainEnv.player.activeSkillList or {}) do
	if skill.socketGroup==group then
		for _,effect in ipairs(skill.effectList or {}) do table.insert(out,effect.grantedEffect.name) end
	end
end
return require("dkjson").encode(out)'''))
            self.assertIn(found["name"], names)
            self.assertNotIn(found["baseName"], names)


if __name__ == "__main__":
    unittest.main()
