"""Real-Path-of-Building guide-check integration contracts."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import time
import unittest
from pathlib import Path
from unittest import mock

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parent
ENGINE_DIR = ROOT / "engine"
sys.path.insert(0, str(ENGINE_DIR))

from tests import golden_common as gc
from tests import guide_check_testlib as helpers

_PERF = {}


def tearDownModule():
    if _PERF:
        print("GUIDE_CHECK_PERF " + json.dumps(_PERF, sort_keys=True))


def _write(directory: Path, name: str, text: str) -> Path:
    path = directory / name
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def _without_perf(result: dict) -> str:
    return json.dumps({key: value for key, value in result.items() if key != "perf"},
                      sort_keys=True, allow_nan=False)


def _canonical(value: dict) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


class _EkCase(helpers.PobGuardedTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = gc.AUDIT_BUILDS["EK"]
        cls.player = gc.build_path(cls.settings["file"])
        if not cls.player.is_file():
            raise unittest.SkipTest("EK build is missing")
        cls.cwd = gc.pob_cwd()
        cls.cwd.__enter__()
        cls.auditor = gc.offline_auditor(cls.player, cls.settings)
        cls.temp = helpers.temp_dir()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "auditor"):
            gc.close_engine(cls.auditor.engine)
        if hasattr(cls, "cwd"):
            cls.cwd.__exit__(None, None, None)
        if hasattr(cls, "temp"):
            shutil.rmtree(cls.temp)
        super().tearDownClass()


class RealEkGuideCheckTests(_EkCase):
    def test_identical_pair_ignores_only_scenario_overlay(self):
        from guide_check import run_check

        guide = helpers.copy_build(self.player, self.temp, "same.xml")
        result = run_check(self.auditor, guide, "same")
        self.assertEqual("identical", result["state"])
        self.assertEqual([], result["config"])
        self.assertEqual(0, result["counts"]["found"])

    def test_coc_support_replacement_uses_full_dps_once(self):
        from guide_check import run_check
        from guide_lua import evaluate_with

        old = next(line for line in self.player.read_text(encoding="utf-8").splitlines()
                   if 'nameSpec="Brutality"' in line)
        new = helpers.gem_line(self.auditor.engine, "Cooldown Recovery", 20, 20)
        guide = helpers.edited_copy(self.player, self.temp, old, new, "cooldown.xml")
        result = run_check(self.auditor, guide, "cooldown")
        rows = [row for row in result["rows"] + result["noChange"]
                if row["category"] == "support-replace"]
        self.assertEqual(1, len(rows))
        row = rows[0]
        request = {"removeNodes": [], "addNodes": [], "stats": self.auditor.keys,
                   "extraSkills": self.auditor.extra_request(), "gemChange": row["change"]}
        from guide_check_eval import models_not_applied
        with models_not_applied(self.auditor):
            independent = self.auditor.adjust(evaluate_with(self.auditor.engine, request))
        expected = self.auditor.main_out(independent)[self.auditor.dps_key]
        self.assertAlmostEqual(expected, row["result"]["after"]["dps"],
                               delta=1e-9 * max(1, abs(expected)))

    def test_trigger_level_row_keeps_vault_interaction(self):
        from guide_check import run_check

        text = helpers.set_gem_attrs(self.player.read_text(encoding="utf-8"),
                                     "Cyclone", level=20, quality=20)
        with mock.patch("guide_interactions.vault_note_status",
                        side_effect=AssertionError("vault status re-read")):
            result = run_check(self.auditor, _write(self.temp, "cyclone.xml", text), "cyclone")
        row = next(value for value in result["rows"] + result["noChange"]
                   if value["category"] == "gem-level" and "Cyclone" in value["label"])
        self.assertIn("trigger attack", row["interaction"]["note"].lower())
        self.assertIn("Trigger attack stays at cheapest level", row["interaction"]["vaultRefs"])
        self.assertNotIn("upgrade", json.dumps(row).lower())

    def test_tree_granted_group_is_not_evaluated(self):
        from guide_check import run_check

        gem = helpers.gem_line(self.auditor.engine, "Mark On Hit", 20, 20)
        text = self.player.read_text(encoding="utf-8").replace(' source="Tree:48239"', '', 1)
        text = helpers.append_gem_to_group(text, 2, gem)
        result = run_check(self.auditor, _write(self.temp, "granted-support.xml", text), "granted")
        candidates = [row for row in result["notTested"]
                      if (row.get("change") or {}).get("group") == 2]
        self.assertTrue(candidates, [row["id"] for row in result["notTested"]])
        row = next(row for row in candidates if row["category"] == "support-add")
        self.assertEqual("This skill is granted by your passive tree or an item, so its gems can't be changed.",
                         row["reason"])
        self.assertNotIn(".lua", row["reason"])
        self.assertTrue(all(".lua:" not in value["reason"] for value in result["notTested"]))

    def test_normal_group_with_free_socket_is_evaluated(self):
        from guide_check import run_check
        from guide_lua import evaluate_with

        original = self.player.read_text(encoding="utf-8")
        player_text = helpers.remove_gem_from_group(original, 4, "Enlighten")
        player = _write(self.temp, "free-player.xml", player_text)
        auditor = gc.offline_auditor(player, self.settings)
        try:
            result = run_check(auditor, self.player, "original")
            row = next(row for row in result["rows"] + result["noChange"]
                       if row["id"] == "support-add:4:Enlighten")
            delta = row["result"]["delta"]
            self.assertTrue(all(isinstance(delta[key], (int, float))
                                for key in ("dpsPct", "ehpPct", "manaMargin")))
            request = {"removeNodes": [], "addNodes": [], "stats": auditor.keys,
                       "extraSkills": auditor.extra_request(), "gemChange": row["change"]}
            independent = auditor.adjust(evaluate_with(auditor.engine, request))
            expected = auditor.main_out(independent)[auditor.dps_key]
            self.assertAlmostEqual(expected, row["result"]["after"]["dps"],
                                   delta=1e-9 * max(1, abs(expected)))
        finally:
            gc.close_engine(auditor.engine)

    def test_full_group_never_adds_a_seventh_gem(self):
        from guide_check import run_check

        gem = helpers.gem_line(self.auditor.engine, "Added Fire Damage", 20, 20)
        text = helpers.append_gem_to_group(self.player.read_text(encoding="utf-8"), 1, gem)
        result = run_check(self.auditor, _write(self.temp, "seventh-ek.xml", text), "seventh")
        all_rows = result["rows"] + result["noChange"] + result["notTested"]
        self.assertFalse(any((row.get("change") or {}).get("type") == "addSupport"
                             and (row.get("change") or {}).get("group") == 1 for row in all_rows))
        candidates = [row for row in all_rows if row.get("id") == "support-replace:1:Added Fire Damage"]
        self.assertTrue(candidates)

    def test_locked_wrath_row_is_ranked_in_place(self):
        from guide_check import run_check

        gem = helpers.gem_line(self.auditor.engine, "Wrath", 20, 0)
        skill = ('\t\t\t<Skill includeInFullDPS="false" mainActiveSkillCalcs="1" '
                 'label="" enabled="true" mainActiveSkill="1">\n' + gem + '\n\t\t\t</Skill>\n')
        text = self.player.read_text(encoding="utf-8").replace("\t\t</SkillSet>", skill + "\t\t</SkillSet>", 1)
        result = run_check(self.auditor, _write(self.temp, "wrath.xml", text), "wrath")
        row = next(row for row in result["rows"] if row["id"] == "group-add:Wrath")
        self.assertIn("breaks a rule", row["chips"])
        self.assertTrue(row["locked"])
        self.assertFalse(row["tickable"])
        self.assertTrue(row["lockReason"].startswith("Breaks a rule:"))
        self.assertEqual(result["sorts"]["best"].index(row["id"]) + 1, row["rank"])
        before = result["rows"][row["rank"] - 2:row["rank"] - 1]
        after = result["rows"][row["rank"]:row["rank"] + 1]
        self.assertTrue(not before or before[0]["sortScore"] >= row["sortScore"])
        self.assertTrue(not after or row["sortScore"] >= after[0]["sortScore"])

    def test_only_mastery_selection_difference_is_not_testable(self):
        from guide_check import run_check

        lua = r'''local d=require("dkjson"); local rows={}
for id,selected in pairs(build.spec.masterySelections) do
 local effects={}; for _,v in ipairs(build.spec.nodes[id].masteryEffects or {}) do
  table.insert(effects,v.effect)
 end
 table.insert(rows,{node=id,selected=selected,effects=effects})
end
return d.encode(rows)'''
        choices = json.loads(self.auditor.engine.run(lua))
        choice = next(row for row in choices if any(v != row["selected"] for v in row["effects"]))
        replacement = next(v for v in choice["effects"] if v != choice["selected"])
        text = self.player.read_text(encoding="utf-8")
        old = f'{{{choice["node"]},{choice["selected"]}}}'
        new = f'{{{choice["node"]},{replacement}}}'
        self.assertIn(old, text)
        result = run_check(self.auditor, _write(self.temp, "mastery.xml", text.replace(old, new, 1)),
                           "mastery")
        self.assertEqual("nothingTestable", result["state"])
        self.assertEqual([], result["rows"])
        self.assertEqual([], result["noChange"])
        self.assertTrue(any("mastery" in row["id"] and row.get("reason")
                            for row in result["notTested"]))


class RealPobbContractTests(_EkCase):
    class Progress:
        def __init__(self):
            self.stages, self.updates = [], []

        def __call__(self, label):
            self.stages.append(label)

        def testing(self, done, total):
            self.updates.append((done, total))

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from tests.guide_testlib import decode_guide
        from guide_check import run_check

        cls.guide = decode_guide()
        cls.progress = cls.Progress()
        started = time.monotonic()
        cls.result = run_check(cls.auditor, cls.guide, "pobb fixture", cls.progress)
        cls.wall_seconds = time.monotonic() - started
        _PERF.update({"wallSeconds": cls.wall_seconds,
                      "perfSeconds": cls.result["perf"]["seconds"],
                      "luaMB": cls.result["perf"]["luaMB"],
                      "luaMBGuideLoaded": cls.result["perf"]["luaMBGuideLoaded"]})

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "guide"):
            shutil.rmtree(cls.guide.parent)
        super().tearDownClass()

    def test_full_contract_progress_chips_sorts_sha_and_breakdown(self):
        from guide_diff_common import CATEGORY_ORDER

        result = self.result
        self.assertEqual(result["counts"]["found"],
                         result["counts"]["tested"] + result["counts"]["notTested"])
        self.assertEqual(["Loading both builds in Path of Building", "Testing differences",
                          "Ranking and explaining"], self.progress.stages)
        self.assertEqual((0, self.progress.updates[0][1]), self.progress.updates[0])
        self.assertEqual(self.progress.updates[-1][1], self.progress.updates[-1][0])
        self.assertEqual(hashlib.sha256(self.player.read_bytes()).hexdigest(), result["sha"])
        self.assertEqual(str(self.player), result["playerPath"])
        rows = result["rows"]
        self.assertEqual(result["sorts"]["best"], [row["id"] for row in rows])
        order = {name: index for index, name in enumerate(CATEGORY_ORDER)}
        tie = lambda row: (order.get(row["category"], len(order)), row["label"].casefold(), row["id"])
        for key, delta in (("dps", "dpsPct"), ("ehp", "ehpPct")):
            expected = sorted(rows, key=lambda row: (-(row["result"]["delta"][delta] or 0), *tie(row)))
            self.assertEqual([row["id"] for row in expected], result["sorts"][key])
        for row in rows + result["noChange"]:
            delta = row["result"]["delta"]
            self.assertTrue(all(isinstance(delta[key], (int, float))
                                for key in ("dpsPct", "ehpPct", "manaMargin", "maxHit")))
            tradeoff = min(delta["dpsPct"], delta["ehpPct"]) < -0.1
            self.assertEqual(tradeoff, "trade-off" in row["chips"])
            self.assertEqual(not tradeoff and max(delta["dpsPct"], delta["ehpPct"]) > 0.1,
                             "helps" in row["chips"])
            self.assertEqual(bool(row["breaks"]), "breaks a rule" in row["chips"])
            self.assertEqual(bool(row["breaks"]),
                             row["locked"] and row["lockReason"].startswith("Breaks a rule:")
                             if "breaks a rule" in row["chips"] else False)
            self.assertTrue(row["lockReason"] if row["locked"] else row["tickable"])
        real_breakdowns = [entry for row in rows + result["noChange"]
                           for entry in row["breakdown"]]
        numeric = [entry for entry in real_breakdowns
                   if isinstance(entry["before"], (int, float))
                   and isinstance(entry["after"], (int, float))]
        self.assertTrue(numeric)
        json.dumps(result, allow_nan=False)

    def test_granted_group_reason_has_no_lua_path(self):
        row = next(row for row in self.result["notTested"]
                   if row["id"] == "gem-level:2:Assassin's Mark")
        self.assertEqual("This skill is granted by your passive tree or an item, so its gems can't be changed.",
                         row["reason"])
        self.assertNotIn(".lua", row["reason"])

    def test_engine_wording_has_no_verdicts_or_paths(self):
        forbidden = re.compile(r"\b(best|wrong|should|fix|mistake|upgrade)\b", re.I)
        strings = []
        for row in self.result["rows"] + self.result["noChange"]:
            strings += row["chips"] + row["why"]
            strings += [row.get("lockReason"), row.get("zeroNote")]
            strings += [(row.get("interaction") or {}).get("note")]
            strings += [(row.get("conditional") or {}).get("text")]
        strings += [row.get("reason") for row in self.result["notTested"]]
        strings += [row.get("text") for row in self.result["header"]["banners"]]
        for value in filter(None, strings):
            self.assertIsNone(forbidden.search(value), value)
        encoded = json.dumps(self.result)
        self.assertNotIn("pob-autobuilder", encoded.casefold())
        self.assertNotIn(".lua:", encoded)

    def test_compare_power_matches_rows_and_node_paths(self):
        import guide_lua
        from guide_check_eval import evaluate_change
        from display import fmt_pct

        loaded = guide_lua.load_guide(self.auditor.engine, self.guide, "pobb fixture")
        self.assertTrue(loaded["ok"])
        try:
            powers = guide_lua.guide_power(self.auditor.engine, ["treeNodes", "items"])
        finally:
            guide_lua.release_guide(self.auditor.engine)
        by_node = {row["nodeId"]: row for row in powers
                   if row["category"] == "Tree" and row.get("nodeId") is not None}
        by_slot = {row["slotName"]: row for row in powers
                   if row["category"] == "Item" and row.get("slotName")}
        all_rows = self.result["rows"] + self.result["noChange"]
        base = self.auditor.base_context()
        for node, power in by_node.items():
            dims = self.auditor.dimensions(self.auditor.evaluate([], [node]), base)
            self.assertAlmostEqual(dims["dps"], power["impactPercent"],
                                   delta=1e-6 * max(1, abs(dims["dps"] or 0)))
        for row in all_rows:
            change, info = row.get("change") or {}, row.get("info") or {}
            if row["category"] == "tree-add" and info.get("node") in by_node:
                node = info["node"]
                if info.get("pathNodes", 0) > 0:
                    path = self.auditor.dimensions(self.auditor.evaluate([], change["nodes"]),
                                                   base)["dps"]
                    shown = row["result"]["delta"]["dpsPct"]
                    self.assertAlmostEqual(path, shown, delta=1e-6 * max(1, abs(path or 0)))
                    self.assertEqual(fmt_pct(path) != fmt_pct(by_node[node]["impactPercent"]),
                                     row["nodeAlone"] is not None)
            if change.get("type") == "item" and change.get("slot") in by_slot:
                ctx = evaluate_change(self.auditor, change)
                dims = self.auditor.dimensions(ctx, base)
                self.assertAlmostEqual(dims["dps"], by_slot[change["slot"]]["impactPercent"],
                                       delta=1e-6 * max(1, abs(dims["dps"] or 0)))

    def test_time_limit_cuts_in_test_order(self):
        import guide_check
        from guide_check import run_check

        class Counter:
            def __init__(self):
                self.value = 0

            def __call__(self):
                value, self.value = self.value, self.value + 1
                return value

        _player, _guide, differences, _powers, _memory, _error = guide_check._load_pair(
            self.auditor, self.guide, "pobb fixture")
        limited = run_check(self.auditor, self.guide, "pobb fixture", deadline_s=5, clock=Counter())
        self.assertEqual(self.result["counts"]["found"], limited["counts"]["found"])
        self.assertTrue(limited["perf"]["timeLimit"])
        cut = [row for row in limited["notTested"] if "time limit" in row["reason"]]
        tested = limited["rows"] + limited["noChange"]
        self.assertTrue(cut)
        self.assertTrue(all(row.get("change") for row in cut))
        order = [row["id"] for row in differences["rows"]]
        first_cut = min(order.index(row["id"]) for row in cut)
        normal_skips = {row["id"] for row in limited["notTested"]
                        if "time limit" not in row["reason"]}
        expected = set(order[:first_cut]) - normal_skips
        self.assertEqual(expected, {row["id"] for row in tested})
        non_tree_cut = any(not row["category"].startswith("tree-") for row in cut)
        self.assertFalse(non_tree_cut and any(row["category"].startswith("tree-") for row in tested))

    def test_release_in_finally_bad_guide_and_runlog(self):
        import guide_check
        import guide_lua

        before = _canonical(guide_lua.snapshot(self.auditor.engine, "player"))
        with mock.patch.object(guide_check, "diff", side_effect=RuntimeError("sentinel")):
            with self.assertRaisesRegex(RuntimeError, "sentinel"):
                guide_check.run_check(self.auditor, self.guide, "pobb fixture")
        self.assertEqual("nil", self.auditor.engine.run("return tostring(_G.__guide)"))
        self.assertEqual(before, _canonical(guide_lua.snapshot(self.auditor.engine, "player")))
        bad = _write(self.temp, "bad.txt", "not xml")
        with self.assertRaises(guide_check.GuideLoadError):
            guide_check.run_check(self.auditor, bad, "bad")
        events = []
        with mock.patch("runlog.log_event", side_effect=lambda *a, **k: events.append((a, k))):
            guide_check.run_check(self.auditor, self.player, "same", job_id="job",
                                  source={"source": "pobb.in"})
        self.assertEqual(1, len(events))
        args, kwargs = events[0]
        payload = json.loads(args[2])
        self.assertEqual("guide_check", args[1])
        self.assertEqual(self.player.stat().st_size, payload["bytes"]["player"])
        self.assertNotIn("xml", json.dumps(payload).lower())
        self.assertEqual("job", kwargs["job_id"])

    def test_determinism_on_same_auditor(self):
        import guide_lua
        from guide_check import run_check

        before = _canonical(guide_lua.snapshot(self.auditor.engine, "player"))
        again = run_check(self.auditor, self.guide, "pobb fixture")
        self.assertEqual(_without_perf(self.result), _without_perf(again))
        self.assertEqual(before, _canonical(guide_lua.snapshot(self.auditor.engine, "player")))
        compound = [row for row in again["rows"] + again["noChange"]
                    if (row.get("change") or {}).get("type") == "compound"
                    and len((row.get("change") or {}).get("changes") or []) >= 2]
        self.assertTrue(compound)
        self.assertTrue(all(row["result"] is not None for row in compound))

    def _rows_by_id(self):
        return {row["id"]: row for row in self.result["rows"] + self.result["noChange"]}

    def test_removal_and_add_in_one_set_keep_both_and_reload_equal(self):
        """GATE 2 H2: PoB prunes a path that lost its connection; the add used to vanish silently (EK 118 -> 116)."""
        import guide_apply
        import guide_lua
        from guide_check_eval import restore_player

        self.addCleanup(restore_player, self.auditor)  # save() leaves the reloaded copy in the shared engine
        rows = self._rows_by_id()
        remove, add = rows["tree-remove:46897"], rows["tree-add:40508"]
        self.assertFalse(remove["locked"] or add["locked"])
        before = self.result["header"]["points"]["used"]
        out = self.temp / "h2-out"
        predicted = guide_apply.predict(self.auditor, [remove, add])
        saved = guide_apply.save(self.auditor, [remove, add], out)
        self.assertTrue(predicted["ok"] and saved["saved"], saved.get("refused"))
        # PoB re-paths the add after the removal (the stored one-node path lost its connection): the fresh path is
        # longer, so the budget is whatever PoB really allocates, and it equals the reloaded file.
        after = predicted["points"]["after"]
        self.assertEqual(before - len(remove["change"]["nodes"]) + 3, after)  # 118 - 2 removed + 3 fresh path nodes
        self.assertEqual(2, predicted["points"]["rerouted"])
        self.assertEqual("Path re-routed: +2 nodes after removing " + remove["label"], predicted["points"]["note"])
        self.assertEqual(predicted["points"], saved["points"])
        reloaded = guide_lua.snapshot(self.auditor.engine, "player")["points"]["used"]
        self.assertEqual(after, reloaded)
        self.assertEqual(predicted["combined"], saved["combined"])
        self.assertTrue(saved["reload"]["equal"], saved["reload"])
        nodes = {value["id"] for value in guide_lua.snapshot(self.auditor.engine, "player")["nodes"]}
        self.assertIn(40508, nodes)
        self.assertTrue(nodes.isdisjoint(remove["change"]["nodes"]))

    def test_add_that_needs_a_node_the_removal_drops_is_refused_not_half_applied(self):
        """The same set when the only way to the add runs through a dropped node: PoB gave 58244 back silently."""
        import guide_apply
        from guide_check_eval import restore_player

        self.addCleanup(restore_player, self.auditor)
        rows = self._rows_by_id()
        remove, add = rows["tree-remove:58244"], rows["tree-add:32176"]
        result = guide_apply.predict(self.auditor, [remove, add])
        self.assertFalse(result["ok"])
        self.assertEqual("pob", result["refused"]["reason"])
        self.assertIn("which a ticked removal drops", result["refused"]["message"])
        self.assertIsNone(result["combined"])

    def test_jewel_row_conflicts_with_a_removal_of_its_socket(self):
        """GATE 2 H2: a jewel in an allocated socket silently went inactive when a ticked removal dropped the socket."""
        import copy
        import guide_apply

        rows = self._rows_by_id()
        jewel, remove = rows["jewel:Jewel 59585"], rows["tree-remove:32710"]
        self.assertIn(59585, remove["change"]["nodes"])
        found = guide_apply.conflicts([jewel, remove])
        self.assertEqual([[jewel["id"], remove["id"]]], [value["ids"] for value in found])
        loose = copy.deepcopy(jewel)
        loose["change"].pop("socketNode")
        self.assertEqual([], guide_apply.conflicts([loose, remove]))

    def test_flask_rows_are_tested_with_the_uptime_note_and_without_the_mageblood_note(self):
        """GATE 2 H5 control and M8: no Mageblood on EK, so flasks are tested; the 100% uptime gap note now reaches them."""
        flasks = [row for row in self.result["rows"] + self.result["noChange"] if row["category"] == "flask"]
        self.assertTrue(flasks)
        self.assertFalse(any(row["category"] == "flask" for row in self.result["notTested"]))
        refs = lambda row: (row["interaction"] or {}).get("vaultRefs") or []
        self.assertTrue(any("Mods PoB can't value" in refs(row) for row in flasks))
        self.assertFalse(any("Mageblood flasks" in refs(row) for row in flasks))


class RealWorbTests(helpers.PobGuardedTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = gc.AUDIT_BUILDS["Worb"]
        cls.player = gc.build_path(cls.settings["file"])
        if not cls.player.is_file():
            raise unittest.SkipTest("Winter Orb build is missing")
        cls.cwd = gc.pob_cwd()
        cls.cwd.__enter__()
        cls.auditor = gc.offline_auditor(cls.player, cls.settings)
        cls.temp = helpers.temp_dir()

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "auditor"):
            gc.close_engine(cls.auditor.engine)
        if hasattr(cls, "cwd"):
            cls.cwd.__exit__(None, None, None)
        if hasattr(cls, "temp"):
            shutil.rmtree(cls.temp)
        super().tearDownClass()

    def test_support_replacement_includes_model_and_is_tested(self):
        from guide_check import run_check

        old = next(line for line in self.player.read_text(encoding="utf-8").splitlines()
                   if 'nameSpec="Infused Channelling"' in line)
        new = helpers.gem_line(self.auditor.engine, "Greater Multiple Projectiles", 20, 20)
        guide = helpers.edited_copy(self.player, self.temp, old, new, "gmp.xml")
        result = run_check(self.auditor, guide, "gmp")
        row = next(value for value in result["rows"] + result["noChange"]
                   if value["category"] == "support-replace")
        self.assertIsNotNone(row["result"])
        self.assertIn("Winter Orb", row["interaction"]["note"])
        self.assertIn("Winter Orb projectile overlap", row["interaction"]["vaultRefs"])
        from guide_check_eval import models_not_applied
        with models_not_applied(self.auditor):
            expected = self.auditor.main_out(self.auditor.base_context())[self.auditor.dps_key]
        self.assertEqual(expected, result["base"]["dps"])
        self.assertIn("model not applied", row["interaction"]["note"])

    def test_zero_rows_stay_in_no_change_despite_the_model_note(self):
        """GATE 2 M4: the Winter Orb model note used to lift every zero tree row out of No change in PoB."""
        from guide_check import run_check
        from tests.guide_testlib import decode_guide

        guide = decode_guide()
        try:
            result = run_check(self.auditor, guide, "pobb fixture")
        finally:
            shutil.rmtree(guide.parent)
        self.assertTrue(result["noChange"])
        noted = [row for row in result["noChange"]
                 if "model not applied" in str((row.get("interaction") or {}).get("note"))]
        self.assertTrue(noted, "the model note stays on the row, it just does not rank it")
        for row in result["noChange"]:
            self.assertFalse(row["locked"])
            self.assertEqual([], (row.get("interaction") or {}).get("carries") or [])
        for row in result["rows"]:
            if row.get("zeroNote"):
                self.assertTrue(row["locked"] or row["interaction"]["carries"], row["id"])

    def test_full_winter_orb_group_never_adds_seventh_gem(self):
        from guide_check import run_check

        gem = helpers.gem_line(self.auditor.engine, "Greater Multiple Projectiles", 20, 20)
        text = helpers.append_gem_to_group(self.player.read_text(encoding="utf-8"), 2, gem)
        result = run_check(self.auditor, _write(self.temp, "seventh-worb.xml", text), "seventh")
        all_rows = result["rows"] + result["noChange"] + result["notTested"]
        self.assertFalse(any((row.get("change") or {}).get("type") == "addSupport"
                             and (row.get("change") or {}).get("group") == 2 for row in all_rows))

    def test_worb_player_ek_guide_restores_apply_path(self):
        import guide_lua
        from guide_check import run_check

        guide = gc.build_path(gc.AUDIT_BUILDS["EK"]["file"])
        before = _canonical(guide_lua.snapshot(self.auditor.engine, "player"))
        base = self.auditor.base_context()
        started = time.monotonic()
        result = run_check(self.auditor, guide, "EK")
        _PERF["worbEkWallSeconds"] = time.monotonic() - started
        _PERF["worbEkLuaMB"] = result["perf"]["luaMB"]
        all_rows = result["rows"] + result["noChange"] + result["notTested"]
        candidates = [row for row in all_rows if "Forbidden" in row["id"]]
        self.assertTrue(candidates, [row["id"] for row in all_rows if row["category"] == "jewel"])
        pair = next(row for row in candidates
                    if row["id"] == "jewel:pair:Forbidden Flame+Forbidden Flesh")
        if pair["result"] is None:
            self.assertEqual("No path to the jewel socket", pair["reason"])
        else:
            self.assertIsInstance(pair["result"]["delta"]["dpsPct"], (int, float))
        self.assertEqual(before, _canonical(guide_lua.snapshot(self.auditor.engine, "player")))
        dims = self.auditor.dimensions(self.auditor.evaluate(parts=self.auditor.multi_part), base)
        self.assertTrue(all((dims[key] or 0) == 0 for key in ("dps", "ehp", "physMaxHit")))
        again = run_check(self.auditor, guide, "EK")
        self.assertEqual(_without_perf(result), _without_perf(again))
        weapon = next((row for row in result["rows"] + result["noChange"]
                       if row["id"].startswith("item:pair:")), None)
        if weapon:
            self.assertIsNotNone(weapon["result"])


class RealApplyPathTests(helpers.PobGuardedTestCase):
    """Two-handed player vs one-handed guide pair: a compound row with two items uses the apply path."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = {"file": "3.26/VFoS Berserker.xml", "disabledSkills": [],
                        "scenario": "Pinnacle Boss", "includeDrafts": True}
        cls.player = gc.build_path(cls.settings["file"])
        cls.guide = gc.build_path(gc.AUDIT_BUILDS["EK"]["file"])
        if not cls.player.is_file() or not cls.guide.is_file():
            raise unittest.SkipTest("VFoS Berserker or EK build is missing")
        cls.cwd = gc.pob_cwd()
        cls.cwd.__enter__()
        cls.auditor = gc.offline_auditor(cls.player, cls.settings)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "auditor"):
            gc.close_engine(cls.auditor.engine)
        if hasattr(cls, "cwd"):
            cls.cwd.__exit__(None, None, None)
        super().tearDownClass()

    def test_weapon_pair_uses_apply_path_and_restores_player(self):
        import guide_lua
        from guide_check import run_check
        from guide_check_eval import evaluate_change

        before = _canonical(guide_lua.snapshot(self.auditor.engine, "player"))
        base = self.auditor.base_context()
        result = run_check(self.auditor, self.guide, "EK")
        row = next(value for value in result["rows"] + result["noChange"]
                   if value["id"] == "item:Weapon 1+Weapon 2")
        self.assertEqual(2, len([c for c in row["change"]["changes"] if c["type"] == "item"]))
        delta = row["result"]["delta"]
        self.assertTrue(all(isinstance(delta[key], (int, float))
                            for key in ("dpsPct", "ehpPct", "manaMargin", "maxHit")))
        first = self.auditor.dimensions(evaluate_change(self.auditor, row["change"]), base)
        second = self.auditor.dimensions(evaluate_change(self.auditor, row["change"]), base)
        self.assertEqual(first["dps"], second["dps"])
        self.assertAlmostEqual(first["dps"], delta["dpsPct"], delta=1e-9 * max(1, abs(first["dps"])))
        self.assertAlmostEqual(first["ehp"], delta["ehpPct"], delta=1e-9 * max(1, abs(first["ehp"])))
        self.assertEqual(before, _canonical(guide_lua.snapshot(self.auditor.engine, "player")))
        dims = self.auditor.dimensions(self.auditor.base_context(), base)
        self.assertTrue(all((dims[key] or 0) == 0 for key in ("dps", "ehp", "physMaxHit")))
        again = run_check(self.auditor, self.guide, "EK")
        self.assertEqual(_without_perf(result), _without_perf(again))

    def test_alternate_weapon_sets_are_listed_not_tested(self):
        from guide_check import run_check

        result = run_check(self.auditor, self.guide, "EK")
        tested = result["rows"] + result["noChange"]
        self.assertFalse([row["id"] for row in tested if row["id"].endswith(" Swap")])
        swaps = [row for row in result["notTested"] if row["id"].endswith(" Swap")]
        self.assertTrue(swaps)
        self.assertTrue(all(row["reason"] == "Alternate weapon sets are not tested." for row in swaps))


class RealConditionalRetestTests(helpers.PobGuardedTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.settings = gc.AUDIT_BUILDS["EK"]
        cls.original = gc.build_path(cls.settings["file"])
        if not cls.original.is_file():
            raise unittest.SkipTest("EK build is missing")
        cls.temp = helpers.temp_dir()
        text = helpers.spec_nodes_without(cls.original.read_text(encoding="utf-8"), 11730)
        text = text.replace('<Input boolean="true" name="useEnduranceCharges"/>',
                            '<Input boolean="false" name="useEnduranceCharges"/>')
        cls.player = _write(cls.temp, "conditional-player.xml", text)
        cls.cwd = gc.pob_cwd()
        cls.cwd.__enter__()
        cls.auditor = gc.offline_auditor(cls.player, cls.settings)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "auditor"):
            gc.close_engine(cls.auditor.engine)
        if hasattr(cls, "cwd"):
            cls.cwd.__exit__(None, None, None)
        if hasattr(cls, "temp"):
            shutil.rmtree(cls.temp)
        super().tearDownClass()

    def test_zero_tree_row_is_retested_with_guide_setting(self):
        from guide_check import run_check
        from guide_check_eval import config_applied

        result = run_check(self.auditor, self.original, "original")
        row = next(value for value in result["noChange"] if value["id"] == "tree-add:11730")
        self.assertEqual(0, row["sortScore"])
        self.assertIsNotNone(row["conditional"])
        self.assertGreater(row["conditional"]["ehpPct"], 0)
        self.assertTrue(any("Endurance" in label for label in row["conditional"]["settings"]))
        config = next(value for value in result["config"] if "Endurance" in value["label"])
        self.assertFalse(config["tickable"])
        self.assertIsInstance(config["result"]["delta"]["ehpPct"], (int, float))
        with config_applied(self.auditor, {"useEnduranceCharges": True}):
            base = self.auditor.base_context()
            ctx = self.auditor.evaluate(add_ids=[11730], parts=self.auditor.multi_part)
            expected = self.auditor.dimensions(ctx, base)["ehp"]
        self.assertAlmostEqual(expected, row["conditional"]["ehpPct"],
                               delta=1e-6 * max(1, abs(expected)))

    def test_a_reloading_row_does_not_drop_the_guide_setting_for_later_rows(self):
        """GATE 2 M2: an apply-path (compound) row reloads the build, which dropped the setting for every later row."""
        import copy
        import guide_lua
        from guide_check import run_check
        from guide_check_retest import retest_zero_rows
        from guide_diff_items import _item_change

        result = run_check(self.auditor, self.original, "original")
        tree = next(value for value in result["noChange"] if value["id"] == "tree-add:11730")
        config = [value for value in result["config"] if value.get("change")]
        items = {value["slot"]: value for value in guide_lua.snapshot(self.auditor.engine, "player")["items"]}
        same_pair = {"type": "compound", "changes": [_item_change(items[slot], slot)
                                                     for slot in ("Weapon 1", "Weapon 2")]}
        reloading = {"id": "same-weapons", "change": same_pair, "zeroNote": "zero"}
        alone, after_reload = copy.deepcopy(tree), copy.deepcopy(tree)
        alone["conditional"] = after_reload["conditional"] = None
        retest_zero_rows(self.auditor, [alone], config)
        retest_zero_rows(self.auditor, [reloading, after_reload], config)
        self.assertIsNotNone(alone["conditional"])
        self.assertEqual(alone["conditional"], after_reload["conditional"])
        self.assertIsNone(reloading.get("conditional"))


if __name__ == "__main__":
    unittest.main()
