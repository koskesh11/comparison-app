"""GATE 2 loop 1 (task 010): regressions found by review, on real Path of Building output.

H1 a second "Add support" on a full link, H3 request defaults through the route with the GUI payload,
H4 an already-broken rule made worse, M9 stuck guide job. Builds are the owner's golden EK / Worb copies
with real edits (a gem or passive nodes removed from a temp copy), never hand-made numbers.
"""

from __future__ import annotations

import shutil
import sys
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS_DIR.parent / "engine"))

from tests import golden_common as gc
from tests import guide_check_testlib as helpers
from tests.guide_testlib import decode_guide

DEX_CHAIN = (25411, 27656, 53213, 61834)  # tree-remove:53213 on EK: -2 Dex, EK sits exactly on its Dex requirement
DEX_LEAF = 32345  # a single Dex node: without it EK is at Dex 151 of 173, i.e. the rule is already broken


def _ek_auditor(path: Path):
    return gc.offline_auditor(path, gc.AUDIT_BUILDS["EK"])


class _EkEdits(helpers.PobGuardedTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ek = gc.build_path(gc.AUDIT_BUILDS["EK"]["file"])
        if not cls.ek.is_file():
            raise unittest.SkipTest("EK build is missing")
        cls.cwd = gc.pob_cwd()
        cls.cwd.__enter__()
        cls.temp = helpers.temp_dir()
        cls.auditor = None

    @classmethod
    def tearDownClass(cls):
        if cls.auditor is not None:
            gc.close_engine(cls.auditor.engine)
        if hasattr(cls, "cwd"):
            cls.cwd.__exit__(None, None, None)
        if hasattr(cls, "temp"):
            shutil.rmtree(cls.temp)
        super().tearDownClass()

    @classmethod
    def write(cls, name: str, text: str) -> Path:
        path = cls.temp / name
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    @staticmethod
    def rows(result: dict) -> dict:
        return {row["id"]: row for row in result["rows"] + result["noChange"]}


class TwoAddsOnAFullLinkTests(_EkEdits):
    """H1: EK group 1 is a 6-link (Body Armour). Player = 5 gems, guide = 6 + one more: two missing supports, one socket."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from guide_check import run_check

        text = cls.ek.read_text(encoding="utf-8")
        player = cls.write("five-links.xml", helpers.remove_gem_from_group(text, 1, "Brutality"))
        cls.auditor = _ek_auditor(player)
        extra = helpers.gem_line(cls.auditor.engine, "Added Fire Damage", 20, 20)
        guide = cls.write("seven-gems.xml", helpers.append_gem_to_group(text, 1, extra))
        cls.player = player
        cls.result = run_check(cls.auditor, guide, "seven gems")
        cls.rows_by_id = cls.rows(cls.result)
        cls.first = cls.rows_by_id["support-add:1:Added Fire Damage"]
        cls.second = cls.rows_by_id["support-add:1:Brutality"]

    def test_each_row_alone_is_valid_with_one_free_socket(self):
        import guide_apply

        for row in (self.first, self.second):
            self.assertEqual(1, row["info"]["freeSockets"])
            self.assertEqual(6, row["change"]["socketLimit"])
            self.assertFalse(row["locked"])
            self.assertEqual([], guide_apply.conflicts([row]))
            self.assertTrue(guide_apply.predict(self.auditor, [row])["ok"])

    def test_both_rows_conflict_and_preview_refuses(self):
        import guide_apply

        found = guide_apply.conflicts([self.first, self.second])
        self.assertEqual(1, len(found))
        self.assertIn("7th gem", found[0]["message"])
        result = guide_apply.predict(self.auditor, [self.first, self.second])
        self.assertFalse(result["ok"])
        self.assertEqual("conflict", result["refused"]["reason"])
        self.assertIsNone(result["combined"])

    def test_path_of_building_layer_refuses_a_seventh_gem_on_its_own(self):
        import guide_apply
        import guide_lua
        from pobhost import LuaError

        self.auditor.engine.load_build(self.player)
        plan = guide_apply.plan_changes([self.first, self.second])
        with self.assertRaises(LuaError) as caught:
            guide_lua.apply_changes(self.auditor.engine, plan, self.auditor.keys, "seven", save=False)
        self.assertIn("did not accept: group 1 has no free socket", str(caught.exception))


class AlreadyBrokenRuleTests(_EkEdits):
    """H4: EK without one Dex node already breaks the attribute rule; the guide takes 2 more Dex."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        text = cls.ek.read_text(encoding="utf-8")
        cut = helpers.spec_nodes_without(text, DEX_LEAF)
        worse = cut
        for node in DEX_CHAIN:
            worse = helpers.spec_nodes_without(worse, node)
        cls.cut, cls.worse = cls.write("dex-cut.xml", cut), cls.write("dex-worse.xml", worse)

    def _check(self, player: Path, guide: Path) -> dict:
        from guide_check import run_check

        if type(self).auditor is not None:
            gc.close_engine(type(self).auditor.engine)
        type(self).auditor = _ek_auditor(player)
        return run_check(type(self).auditor, guide, "dex")

    def test_the_rule_is_already_broken_and_a_worsening_row_is_locked(self):
        from rules import violations

        result = self._check(self.cut, self.worse)
        base = violations(self.auditor.rules, self.auditor.evaluate())
        self.assertTrue(any(v.startswith("[Attribute requirements must be met]") and "Dex" in v for v in base), base)
        row = self.rows(result)["tree-remove:53213"]
        self.assertTrue(row["locked"])
        self.assertTrue(row["lockReason"].startswith("Makes a rule you already break worse: Attribute requirements"),
                        row["lockReason"])
        self.assertIn("breaks a rule", row["chips"])
        self.assertFalse(row["tickable"])

    def test_by_name_check_alone_would_have_missed_it(self):
        import guide_check_eval
        from rules import worsened

        result = self._check(self.cut, self.worse)
        row = self.rows(result)["tree-remove:53213"]
        base = self.auditor.base_context()
        ctx = guide_check_eval.evaluate_change(self.auditor, row["change"])
        self.assertEqual([], self.auditor.breaks(ctx))
        found = worsened(self.auditor.rules, base, ctx)
        self.assertEqual(1, len(found))
        self.assertIn("Dex", found[0])
        self.assertIn("short by", found[0])

    def test_improving_the_broken_rule_is_not_blamed(self):
        result = self._check(self.worse, self.cut)
        rows = self.rows(result)
        row = rows["tree-add:53213"]
        self.assertFalse(row["locked"], row["lockReason"])
        self.assertEqual([], row["breaks"])
        self.assertTrue(all("already break" not in str(value.get("lockReason")) for value in rows.values()))


class _InlineThread:
    """Runs the job at start(), so the route test sees the finished job without sleeping."""

    def __init__(self, target, args=(), daemon=None):
        self.target, self.args = target, args

    def start(self):
        self.target(*self.args)


class RouteDefaultsTests(helpers.PobGuardedTestCase):
    """H3: the request goes through guide_routes.start_check with the payload the GUI sends (startGuide)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        import engine_pool

        cls.worb = gc.build_path(gc.AUDIT_BUILDS["Worb"]["file"])
        if not cls.worb.is_file():
            raise unittest.SkipTest("Worb build is missing")
        cls.cwd = gc.pob_cwd()
        cls.cwd.__enter__()
        cls.guide = decode_guide()
        cls.out = helpers.temp_dir()
        cls.pool = engine_pool.EnginePool(size=1)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "pool"):
            cls.pool.close()
        if hasattr(cls, "cwd"):
            cls.cwd.__exit__(None, None, None)
        for folder in (getattr(cls, "out", None), getattr(cls, "guide", None) and cls.guide.parent):
            if folder:
                shutil.rmtree(folder, ignore_errors=True)
        super().tearDownClass()

    def _state(self):
        import audit

        return SimpleNamespace(jobs={}, pool=self.pool, engine_lock=threading.Lock(), Auditor=audit.Auditor,
                               BUILDS_DIR=self.out, DEFAULT_OUT_DIR=self.out / "out", guide_capability=None,
                               resolve_build=lambda name: self.worb)

    def _run_route(self, payload: dict) -> tuple[SimpleNamespace, dict]:
        import audit
        import guide_routes
        import pobbin

        state = self._state()
        saved = {"leaveOut": gc.AUDIT_BUILDS["Worb"]["disabledSkills"], "scenario": "Pinnacle Boss"}
        imported = {"id": "F8CiRC9KVADl", "path": str(self.guide)}
        with mock.patch.object(guide_routes.threading, "Thread", _InlineThread), \
                mock.patch.object(pobbin, "import_link", return_value=imported), \
                mock.patch.object(guide_routes.build_settings, "get", return_value=saved), \
                mock.patch.object(guide_routes.build_settings, "update"), \
                mock.patch.object(audit.Obtainability, "load", return_value=gc.offline_obtainability()):
            started = guide_routes.start_check(state, payload)
        job = state.jobs[started["jobId"]]
        self.assertEqual("done", job["status"], job.get("error"))
        return state, job

    @staticmethod
    def _gui_payload(drafts: bool) -> dict:
        # exactly the object gui/index.html startGuide() posts: the player pick, the guide link and the drafts checkbox
        return {"player": {"build": "3.29/Worb.xml"}, "guide": {"link": "https://pobb.in/F8CiRC9KVADl"},
                "includeDrafts": drafts}

    @staticmethod
    def _model_notes(job: dict) -> list[str]:
        rows = job["report"]["rows"] + job["report"]["noChange"]
        return [row["interaction"]["note"] for row in rows
                if row.get("interaction") and "model not applied" in row["interaction"]["note"]]

    def test_drafts_ticked_in_the_gui_reach_the_auditor_and_name_the_draft_model(self):
        _, job = self._run_route(self._gui_payload(True))
        self.assertTrue(job["settings"]["includeDrafts"])
        self.assertEqual([], job["report"]["header"]["skippedDrafts"])
        self.assertTrue(any("Winter Orb" in note for note in self._model_notes(job)))

    def test_drafts_unticked_skip_the_draft_rules_and_models(self):
        _, job = self._run_route(self._gui_payload(False))
        self.assertFalse(job["settings"]["includeDrafts"])
        self.assertIn("CoC requires 100% crit and hit", job["report"]["header"]["skippedDrafts"])
        self.assertEqual([], self._model_notes(job))

    def test_header_names_scenario_left_out_skill_and_dps_stat(self):
        _, job = self._run_route(self._gui_payload(True))
        header = job["report"]["header"]
        self.assertEqual("Pinnacle Boss", header["scenario"])
        self.assertEqual(["Aspect of the Brine King"], header["leaveOut"])
        self.assertIn(header["dpsStat"], ("FullDPS", "CombinedDPS"))

    def test_flags_must_be_real_booleans(self):
        import guide_routes
        from api_errors import InvalidRequest

        for payload in ({"includeDrafts": "false"}, {"includeDrafts": 1}):
            with self.assertRaises(InvalidRequest):
                guide_routes._strict_bool(payload, "includeDrafts")
        state, job = self._run_route(self._gui_payload(True))
        ids = [job["report"]["rows"][0]["id"]]
        with self.assertRaises(InvalidRequest):
            guide_routes.apply(state, {"jobId": job["id"], "ids": ids, "force": "false"})


class StuckJobTests(unittest.TestCase):
    """M9: a guide job that never finishes must not block every later check."""

    def test_old_running_job_is_given_up_and_a_new_one_starts(self):
        import guide_routes

        old = guide_routes._new_job("old", "b.xml", {})
        old["started"] -= guide_routes.MAX_JOB_AGE_S + 1
        fresh = guide_routes._new_job("new", "b.xml", {})
        state = SimpleNamespace(jobs={"old": old, "new": fresh})
        guide_routes._expire_stuck_jobs(state)
        self.assertEqual("error", old["status"])
        self.assertEqual("Timeout", old["errorKind"])
        self.assertEqual("running", fresh["status"])


if __name__ == "__main__":
    unittest.main()
