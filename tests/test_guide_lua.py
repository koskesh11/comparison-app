"""Integration tests for guide snapshots and reversible PoB mutations."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests import guide_testlib as gl
from tests import golden_common as gc

from guide_lua import (apply_changes, ensure_loaded, evaluate_with, guide_power, load_guide,
                       probe, release_guide, snapshot, tree_info)
from pobhost import LuaError, _lua_str


STATS = ["FullDPS", "CombinedDPS", "TotalEHP", "Life", "Mana"]


def main_out(ctx: dict) -> dict:
    return next(skill["out"] for skill in ctx["skills"] if skill["isMain"])


class ReadOnlyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.install_before = gc.install_snapshot()
        cls.cwd = gc.pob_cwd()
        cls.cwd.__enter__()
        cls.engine = gl.make_engine("EK")
        ensure_loaded(cls.engine)
        cls.guide_path = gl.decode_guide()
        result = load_guide(cls.engine, cls.guide_path, "pobb guide")
        assert result["ok"], result

    @classmethod
    def tearDownClass(cls):
        release_guide(cls.engine)
        gc.close_engine(cls.engine)
        cls.cwd.__exit__(None, None, None)
        diff = [line for line in gc.install_diff(cls.install_before, gc.install_snapshot())
                if "Data\\TimelessJewelData\\" not in line]
        assert diff == [], diff

    def test_probe_is_real_and_restores_player(self):
        before = gl.canonical(snapshot(self.engine, "player"))
        result = probe(self.engine)
        self.assertTrue(result["compareTab"] and result["comparePowerBuilder"] and result["compareEntry"])
        self.assertGreaterEqual(result["tinyRows"], 1)
        self.assertTrue({"category", "name", "nodeId", "impact", "impactStr", "impactPercent",
                         "pathDist", "perPoint"}.issubset(result["fields"]))
        self.assertEqual(before, gl.canonical(snapshot(self.engine, "player")))

    def test_snapshots_validate_and_are_deterministic(self):
        for which in ("player", "guide"):
            first = snapshot(self.engine, which)
            gl.validate_snapshot(first)
            self.assertEqual(gl.canonical(first), gl.canonical(snapshot(self.engine, which)))
        player = snapshot(self.engine, "player")
        self.assertTrue(player["className"] and player["ascendancy"] and player["mainSkill"])
        used = sum(not node["ascendancy"] and node["type"] != "ClassStart" for node in player["nodes"])
        self.assertEqual(used, player["points"]["used"])
        self.assertIn("Weapon 1", {item["slot"] for item in player["items"]})

    def test_real_guide_variant_gem_families_use_plain_gems(self):
        guide = snapshot(self.engine, "guide")
        variants = [gem for group in guide["groups"] for gem in group["gems"]
                    if gem["name"].startswith("Awakened ")
                    or (gem["gemId"] or "").endswith(("AltX", "AltY", "AltZ"))]
        self.assertTrue(variants)
        for gem in variants:
            with self.subTest(gem=gem["name"]):
                gem_id = _lua_str(gem["gemId"])
                expected = self.engine.run(
                    f"local g=data.gems[{gem_id}]; local e=g.grantedEffect; "
                    "if e.plusVersionOf then return data.skills[e.plusVersionOf].name end; "
                    "local variants=data.gemsByGameId[g.gameId]; "
                    "local key=(g.variantId or ''):gsub('Alt%u$',''); "
                    "return variants[key].name")
                self.assertNotEqual(gem["name"], gem["family"])
                self.assertEqual(expected, gem["family"])

    def test_release_makes_guide_snapshot_fail_then_reload(self):
        release_guide(self.engine)
        with self.assertRaises(LuaError):
            snapshot(self.engine, "guide")
        self.assertTrue(load_guide(self.engine, self.guide_path, "pobb guide")["ok"])

    def test_tree_info_uses_path_and_depends_without_mutation(self):
        before = snapshot(self.engine, "player")
        guide = snapshot(self.engine, "guide")
        player_ids = {node["id"] for node in before["nodes"]}
        guide_ids = {node["id"] for node in guide["nodes"]}
        guide_by_id = {node["id"]: node for node in guide["nodes"]}
        player_by_id = {node["id"]: node for node in before["nodes"]}
        add = [node_id for node_id in sorted(guide_ids - player_ids)
               if not guide_by_id[node_id]["ascendancy"] and guide_by_id[node_id]["type"] != "ClassStart"][:3]
        remove = [node_id for node_id in sorted(player_ids - guide_ids)
                  if not player_by_id[node_id]["ascendancy"] and player_by_id[node_id]["type"] != "ClassStart"][:3]
        result = tree_info(self.engine, add + [99999999], remove)
        self.assertNotIn("99999999", result["nodes"])
        direct_request = json.dumps({"ids": add + remove})
        direct = json.loads(self.engine.run(f"return nodePathsJSON('{direct_request}')"))
        for node_id in add:
            row = result["nodes"][str(node_id)]
            self.assertIn(node_id, row["path"])
            self.assertGreaterEqual(row["pathDist"], 1)
            self.assertTrue(set(row["path"]).isdisjoint(player_ids))
            self.assertEqual(sorted(direct[str(node_id)]), row["path"])
            self.assertIsNone(row["depends"])
        for node_id in remove:
            row = result["nodes"][str(node_id)]
            self.assertIn(node_id, row["depends"])
            self.assertEqual(sorted(direct[str(node_id)]), row["depends"])
            self.assertIsNone(row["path"])
        self.assertEqual(gl.canonical(before), gl.canonical(snapshot(self.engine, "player")))

    def test_snapshot_node_ids_are_pob_alloc_nodes(self):
        expected = json.loads(self.engine.run(
            "local r={}; for id in pairs(build.spec.allocNodes) do table.insert(r,id) end; "
            "table.sort(r); return require('dkjson').encode(r)"))
        self.assertEqual(expected, [node["id"] for node in snapshot(self.engine, "player")["nodes"]])

    def test_rep_item_and_failures_restore_state(self):
        player = snapshot(self.engine, "player")
        before = gl.canonical(player)
        base = evaluate_with(self.engine, {"removeNodes": [], "addNodes": [], "stats": STATS})
        weapon = next(item for item in player["items"] if item["slot"] == "Weapon 1")
        same = evaluate_with(self.engine, {"removeNodes": [], "addNodes": [], "stats": STATS,
                                           "repItem": {"slot": "Weapon 1", "raw": weapon["raw"]}})
        self.assertEqual(main_out(base), main_out(same))
        for rep in ({"slot": "No Such Slot", "raw": weapon["raw"]},
                    {"slot": "Weapon 1", "raw": "garbage"}):
            with self.assertRaises(LuaError):
                evaluate_with(self.engine, {"stats": STATS, "repItem": rep})
        self.assertEqual(before, gl.canonical(snapshot(self.engine, "player")))

    def test_abyss_jewels_and_flask_restore_state(self):
        player = snapshot(self.engine, "player")
        before = gl.canonical(player)
        base = main_out(evaluate_with(self.engine, {"stats": STATS}))
        belt = next(item for item in player["items"] if item["abyssJewels"])
        with_jewels = main_out(evaluate_with(self.engine, {"stats": STATS, "repItem": {
            "slot": belt["slot"], "raw": belt["raw"], "jewels": belt["abyssJewels"]}}))
        self.assertEqual(base, with_jewels)
        without_jewels = main_out(evaluate_with(self.engine, {"stats": STATS, "repItem": {
            "slot": belt["slot"], "raw": belt["raw"]}}))
        self.assertTrue(any(without_jewels.get(key) != base.get(key) for key in STATS))
        flask = next(item for item in player["items"] if item["slot"] == "Flask 1")
        evaluate_with(self.engine, {"stats": STATS, "repItem": {
            "slot": flask["slot"], "raw": flask["raw"], "flaskActive": True}})
        # An inactive copy can be numerically equal when the build's flask was already inactive;
        # restoration, not a forced delta, is the invariant here.
        evaluate_with(self.engine, {"stats": STATS, "repItem": {
            "slot": flask["slot"], "raw": flask["raw"], "flaskActive": False}})
        self.assertEqual(before, gl.canonical(snapshot(self.engine, "player")))

    def test_gem_change_restores_state(self):
        player = snapshot(self.engine, "player")
        before = gl.canonical(player)
        base = main_out(evaluate_with(self.engine, {"stats": STATS}))
        group = player["groups"][player["mainGroup"] - 1]
        change = changed = None
        for index, gem in enumerate(group["gems"], 1):
            if not gem["isSupport"]:
                continue
            candidate = {"type": "gemLevel", "group": player["mainGroup"], "gemIndex": index,
                         "name": gem["name"], "level": 1, "quality": 0}
            candidate_out = main_out(evaluate_with(self.engine, {"stats": STATS, "gemChange": candidate}))
            if candidate_out["FullDPS"] != base["FullDPS"]:
                change, changed = candidate, candidate_out
                break
        self.assertIsNotNone(change, "no main-group support changed FullDPS at level 1")
        self.assertNotEqual(base["FullDPS"], changed["FullDPS"])
        self.assertEqual(base, main_out(evaluate_with(self.engine, {"stats": STATS})))
        self.assertEqual(before, gl.canonical(snapshot(self.engine, "player")))
        bad = dict(change, name="Definitely Not This Gem")
        with self.assertRaises(LuaError):
            evaluate_with(self.engine, {"stats": STATS, "gemChange": bad})
        self.assertEqual(before, gl.canonical(snapshot(self.engine, "player")))

    def test_added_and_replaced_gems_restore_state(self):
        player, guide = snapshot(self.engine, "player"), snapshot(self.engine, "guide")
        before = gl.canonical(player)
        main = player["groups"][player["mainGroup"] - 1]
        guide_group = next(group for group in guide["groups"] if any(not gem["isSupport"] for gem in group["gems"]))
        existing = {gem["name"] for gem in main["gems"]}
        added = next(gem for group in guide["groups"] for gem in group["gems"]
                     if gem["isSupport"] and gem["name"] not in existing)
        support = {key: added[key] for key in ("name", "gemId", "level", "quality", "qualityId", "enabled")}
        changes = [
            {"type": "addSupport", "group": player["mainGroup"], "gem": support},
            {"type": "replaceSupport", "group": player["mainGroup"], "gemIndex": 1,
             "replaced": main["gems"][0]["name"], "gem": support},
            {"type": "addGroup", "slot": guide_group["slot"], "label": "temporary guide group",
             "gems": guide_group["gems"]},
        ]
        base = main_out(evaluate_with(self.engine, {"stats": STATS}))
        for change in changes:
            result = evaluate_with(self.engine, {"stats": STATS, "gemChange": change})
            self.assertIn("FullDPS", main_out(result))
            self.assertEqual(base, main_out(evaluate_with(self.engine, {"stats": STATS})))
            self.assertEqual(before, gl.canonical(snapshot(self.engine, "player")))
        with self.assertRaises(LuaError):
            evaluate_with(self.engine, {"stats": STATS, "gemChange": {
                "type": "addSupport", "group": player["mainGroup"],
                "gem": {"name": "Definitely Not A Gem", "level": 1, "quality": 0}}})
        self.assertEqual(before, gl.canonical(snapshot(self.engine, "player")))
    def test_guide_power_and_non_finite_json(self):
        before = gl.canonical(snapshot(self.engine, "player"))
        rows = guide_power(self.engine)
        self.assertTrue(rows)
        self.assertLessEqual({row["category"] for row in rows},
                             {"Tree", "Item", "Skill gem", "Support gem", "Config"})
        encoded = self.engine.run("return GuideCore.encode({0/0, 1/0})")
        self.assertEqual([None, None], json.loads(encoded))
        self.assertEqual(before, gl.canonical(snapshot(self.engine, "player")))

    def test_guide_power_tree_impacts_match_evaluate(self):
        rows = guide_power(self.engine, ["treeNodes"])
        base = main_out(evaluate_with(self.engine, {"stats": ["FullDPS"]}))["FullDPS"]
        checked = 0
        for row in rows:
            if row["category"] != "Tree" or row["nodeId"] is None:
                continue
            changed = main_out(evaluate_with(self.engine, {"stats": ["FullDPS"],
                                                           "addNodes": [row["nodeId"]]}))["FullDPS"]
            self.assertAlmostEqual(row["impact"], changed - base,
                                   delta=1e-6 * max(1, abs(row["impact"])))
            checked += 1
            if checked == 5:
                break
        self.assertGreater(checked, 0)

    def test_guide_power_equals_direct_builder_and_evaluate(self):
        before = gl.canonical(snapshot(self.engine, "player"))
        rows = guide_power(self.engine)
        direct = json.loads(self.engine.run(r'''local tab=build.compareTab
local oldPrimary,oldResults,oldFlag=tab.primaryBuild,tab.comparePowerResults,build.buildFlag
local stat; for _,v in ipairs(data.powerStatList) do if v.stat=="FullDPS" then stat=v end end
local ok,result=pcall(function()
	tab.primaryBuild=build
	tab:ComparePowerBuilder(__guide,stat,{treeNodes=true,items=true,skillGems=true,supportGems=true,config=true})
	local out={}; for _,v in ipairs(tab.comparePowerResults or {}) do
		table.insert(out,{category=v.category,name=v.name,nodeId=v.nodeId or require("dkjson").null,impact=v.impact})
	end; return require("dkjson").encode(out)
end)
tab.primaryBuild,tab.comparePowerResults,build.buildFlag=oldPrimary,oldResults,oldFlag
if not ok then error(result,0) end; return result'''))
        project = lambda row: (row["category"], row["name"], row["nodeId"] or -1, row["impact"])
        self.assertEqual(sorted(map(project, direct)), sorted(map(project, rows)))
        guide_items = {item["slot"]: item for item in snapshot(self.engine, "guide")["items"]}
        base = main_out(evaluate_with(self.engine, {"stats": ["FullDPS"]}))["FullDPS"]
        checked = 0
        for row in rows:
            if row["category"] != "Item" or row["slotName"] is None:
                continue
            item = guide_items[row["slotName"]]
            changed = main_out(evaluate_with(self.engine, {"stats": ["FullDPS"], "repItem": {
                "slot": item["slot"], "raw": item["raw"], "jewels": item["abyssJewels"]}}))["FullDPS"]
            self.assertAlmostEqual(changed - base, row["impact"],
                                   delta=1e-6 * max(1, abs(row["impact"])))
            checked += 1
        self.assertGreaterEqual(checked, 5)
        tree_checked = 0
        for row in rows:
            if row["category"] != "Tree" or row["nodeId"] is None:
                continue
            changed = main_out(evaluate_with(self.engine, {"stats": ["FullDPS"],
                                                           "addNodes": [row["nodeId"]]}))["FullDPS"]
            self.assertAlmostEqual(changed - base, row["impact"],
                                   delta=1e-6 * max(1, abs(row["impact"])))
            tree_checked += 1
            if tree_checked == 5:
                break
        self.assertGreaterEqual(tree_checked, 1)
        self.assertEqual(before, gl.canonical(snapshot(self.engine, "player")))


class ApplyTests(unittest.TestCase):
    def setUp(self):
        self.cwd = gc.pob_cwd()
        self.cwd.__enter__()
        self.engine = gl.make_engine("EK")
        ensure_loaded(self.engine)

    def tearDown(self):
        gc.close_engine(self.engine)
        self.cwd.__exit__(None, None, None)

    def test_apply_item_and_unknown_change(self):
        guide_path = gl.decode_guide()
        self.assertTrue(load_guide(self.engine, guide_path)["ok"])
        guide = snapshot(self.engine, "guide")
        player = snapshot(self.engine, "player")
        candidates = [item for item in guide["items"] if item["slot"] in {p["slot"] for p in player["items"]}]
        item = candidates[0]
        result = apply_changes(self.engine, [{"type": "item", "slot": item["slot"], "raw": item["raw"],
                                              "abyssJewels": item["abyssJewels"]}], ["FullDPS"])
        self.assertTrue(result["xml"].startswith(("<?xml", "<PathOfBuilding")))
        changed = next(row for row in snapshot(self.engine, "player")["items"] if row["slot"] == item["slot"])
        self.assertEqual(item["name"], changed["name"])
        belt = next(row for row in player["items"] if row["abyssJewels"])
        apply_changes(self.engine, [{"type": "item", "slot": belt["slot"], "raw": belt["raw"],
                                     "abyssJewels": belt["abyssJewels"]}], ["FullDPS"])
        changed_belt = next(row for row in snapshot(self.engine, "player")["items"] if row["slot"] == belt["slot"])
        self.assertEqual([row["name"] for row in belt["abyssJewels"]],
                         [row["name"] for row in changed_belt["abyssJewels"]])
        with self.assertRaises(LuaError):
            apply_changes(self.engine, [{"type": "unknown"}], ["FullDPS"])

    def test_item_with_empty_guide_sockets_checks_and_applies_to_the_same_numbers(self):
        """GATE 2 M3: the check emptied abyss sockets the guide leaves empty while the apply kept your jewel."""
        player = snapshot(self.engine, "player")
        belt = next(row for row in player["items"] if row["abyssJewels"])
        base = main_out(evaluate_with(self.engine, {"stats": STATS}))
        spec = {"slot": belt["slot"], "raw": belt["raw"]}
        checked = main_out(evaluate_with(self.engine, {"stats": STATS, "repItem": {**spec, "jewels": []}}))
        applied = apply_changes(self.engine, [{"type": "item", **spec, "abyssJewels": []}], STATS, save=False)
        self.assertNotEqual(base, checked)
        self.assertEqual(checked, main_out(applied["ctx"]))
        changed = next(row for row in snapshot(self.engine, "player")["items"] if row["slot"] == belt["slot"])
        self.assertEqual([], changed["abyssJewels"])

    def test_apply_tree_round_trip(self):
        load_guide(self.engine, gl.decode_guide())
        original = snapshot(self.engine, "player")
        guide = snapshot(self.engine, "guide")
        original_ids = {node["id"] for node in original["nodes"]}
        target = next(node["id"] for node in guide["nodes"] if node["id"] not in original_ids
                      and not node["ascendancy"] and not node["cluster"])
        path = tree_info(self.engine, [target])["nodes"][str(target)]["path"]
        self.assertTrue(path)
        apply_changes(self.engine, [{"type": "alloc", "target": target, "nodes": path}], ["FullDPS"])
        self.assertTrue(set(path).issubset({node["id"] for node in snapshot(self.engine, "player")["nodes"]}))
        while True:
            extras = {node["id"] for node in snapshot(self.engine, "player")["nodes"]} - original_ids
            if not extras:
                break
            info = tree_info(self.engine, [], extras)["nodes"]
            leaf = next(node_id for node_id in extras if info[str(node_id)]["depends"] == [node_id])
            apply_changes(self.engine, [{"type": "dealloc", "target": leaf, "nodes": [leaf]}], ["FullDPS"])
        self.assertEqual(sorted(original_ids), [node["id"] for node in snapshot(self.engine, "player")["nodes"]])

    def test_apply_gem_changes_and_repath(self):
        load_guide(self.engine, gl.decode_guide())
        player, guide = snapshot(self.engine, "player"), snapshot(self.engine, "guide")
        main_index = player["mainGroup"]
        main = player["groups"][main_index - 1]
        first = main["gems"][0]
        apply_changes(self.engine, [{"type": "gemLevel", "group": main_index, "gemIndex": 1,
                                     "name": first["name"], "level": 1, "quality": 0}], ["FullDPS"])
        self.assertEqual(1, snapshot(self.engine, "player")["groups"][main_index - 1]["gems"][0]["level"])
        existing = {gem["name"] for gem in main["gems"]}
        added = next(gem for group in guide["groups"] for gem in group["gems"]
                     if gem["isSupport"] and gem["name"] not in existing)
        spec = {key: added[key] for key in ("name", "gemId", "level", "quality", "qualityId", "enabled")}
        apply_changes(self.engine, [{"type": "addSupport", "group": main_index, "gem": spec}], ["FullDPS"])
        self.assertEqual(spec["name"], snapshot(self.engine, "player")["groups"][main_index - 1]["gems"][-1]["name"])
        replaced = snapshot(self.engine, "player")["groups"][main_index - 1]["gems"][1]
        apply_changes(self.engine, [{"type": "replaceSupport", "group": main_index, "gemIndex": 2,
                                     "replaced": replaced["name"], "gem": spec}], ["FullDPS"])
        self.assertEqual(spec["name"], snapshot(self.engine, "player")["groups"][main_index - 1]["gems"][1]["name"])
        guide_group = next(group for group in guide["groups"] if group["gems"])
        old_count = len(snapshot(self.engine, "player")["groups"])
        apply_changes(self.engine, [{"type": "addGroup", "slot": guide_group["slot"], "label": "guide group",
                                     "gems": guide_group["gems"]}], ["FullDPS"])
        self.assertEqual(old_count + 1, len(snapshot(self.engine, "player")["groups"]))
        request = json.loads(self.engine.run("return repathJSON('{}')"))
        result = apply_changes(self.engine, [{"type": "repath", "removeIds": request["removeIds"],
                                              "addIds": request["addIds"]}], ["FullDPS"])
        self.assertIsInstance(main_out(result["ctx"])["FullDPS"], (int, float))


class RefusalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player_path = gc.build_path("3.26/VFoS Berserker.xml")
        cls.guide_path = gc.build_path(gc.RAW_BUILDS["EK"])
        if not cls.player_path.is_file() or not cls.guide_path.is_file():
            raise unittest.SkipTest("VFoS Berserker or EK build is missing")

    def setUp(self):
        self.cwd = gc.pob_cwd()
        self.cwd.__enter__()
        from pobhost import PobEngine
        self.engine = PobEngine()
        self.engine.load_build(self.player_path)
        ensure_loaded(self.engine)
        self.assertTrue(load_guide(self.engine, self.guide_path, "EK guide")["ok"])
        guide = snapshot(self.engine, "guide")
        self.weapons = {item["slot"]: item for item in guide["items"]
                        if item["slot"] in {"Weapon 1", "Weapon 2"}}

    def tearDown(self):
        gc.close_engine(self.engine)
        self.cwd.__exit__(None, None, None)

    def _change(self, slot: str) -> dict:
        item = self.weapons[slot]
        return {"type": "item", "slot": slot, "raw": item["raw"]}

    def test_weapon_2_refusal_raises_and_restores(self):
        before = gl.canonical(snapshot(self.engine, "player"))
        with self.assertRaisesRegex(LuaError, "PoB did not accept item"):
            apply_changes(self.engine, [self._change("Weapon 2")], ["FullDPS"])
        self.assertEqual(before, gl.canonical(snapshot(self.engine, "player")))

    def test_weapon_pair_compound_succeeds_in_slot_order(self):
        compound = {"type": "compound", "changes": [self._change("Weapon 1"),
                                                        self._change("Weapon 2")]}
        apply_changes(self.engine, [compound], ["FullDPS"])
        player = snapshot(self.engine, "player")
        equipped = {item["slot"] for item in player["items"]}
        self.assertTrue({"Weapon 1", "Weapon 2"} <= equipped)
        self.assertFalse(player["handedness"]["weapon1TwoHanded"])

    def test_weapon_pair_compound_refuses_other_order_and_restores(self):
        before = gl.canonical(snapshot(self.engine, "player"))
        compound = {"type": "compound", "changes": [self._change("Weapon 2"),
                                                        self._change("Weapon 1")]}
        with self.assertRaisesRegex(LuaError, "PoB did not accept item"):
            apply_changes(self.engine, [compound], ["FullDPS"])
        self.assertEqual(before, gl.canonical(snapshot(self.engine, "player")))


class FixtureTests(unittest.TestCase):
    def test_recorded_snapshots_match_fresh_engines(self):
        fixture_dir = Path(__file__).resolve().parent / "fixtures" / "snapshots"
        cases = [("EK", "ek_player.json", None), ("Worb", "worb_player.json", None),
                 ("EK", "pobb_guide.json", "guide")]
        for build_key, filename, which in cases:
            expected = json.loads((fixture_dir / filename).read_text(encoding="utf-8"))
            gl.validate_snapshot(expected)
            with gc.pob_cwd():
                engine = gl.make_engine(build_key)
                try:
                    ensure_loaded(engine)
                    if which:
                        self.assertTrue(load_guide(engine, gl.decode_guide(), "pobb guide")["ok"])
                    self.assertEqual(expected, snapshot(engine, which or "player"))
                finally:
                    gc.close_engine(engine)


if __name__ == "__main__":
    unittest.main()
