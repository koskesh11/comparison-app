import io
import hashlib
import json
import sys
import tempfile
import threading
import unittest
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent
ENGINE_DIR = PROJECT_ROOT / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

import optimize
import pobhost
import pobbin
import runlog
import server
import guide_routes
import guide_apply
import engine_pool
from api_errors import InvalidRequest
from tests.guide_apply_testlib import fake_result


class FakeHandler(server.Handler):
    def __init__(self, path: str, body: bytes):
        self.path = path
        self.headers = {
            "Host": "127.0.0.1:8765", "X-Api-Token": "t0ken",
            "Content-Length": str(len(body)),
        }
        self.rfile = io.BytesIO(body)
        self.wfile = io.BytesIO()
        self.status = None
        self.sent_headers = {}

    def send_response(self, status, message=None):
        self.status = int(status)

    def send_header(self, keyword, value):
        self.sent_headers[keyword] = value

    def end_headers(self):
        pass


class ServerErrorTests(unittest.TestCase):
    job_id = "server-error-test"

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        runlog.setup(Path(self.temp_dir.name), token="t0ken")
        self.token = mock.patch.object(server, "API_TOKEN", "t0ken")
        self.token.start()
        server.jobs[self.job_id] = {
            "id": self.job_id, "status": "done", "progress": "Done", "build": "x.xml",
            "error": None, "sha": "s", "settings": {
                "includeDrafts": False, "leaveOut": [], "scenario": "Mapping",
            }, "report": {"suggestions": []},
        }

    def tearDown(self):
        server.jobs.pop(self.job_id, None)
        self.token.stop()
        self.temp_dir.cleanup()

    def post_apply(self, error):
        body = json.dumps({"ids": [1]}).encode("utf-8")
        handler = FakeHandler(f"/api/jobs/{self.job_id}/apply", body)

        @contextmanager
        def lease():
            yield object()

        pool = mock.Mock()
        pool.lease.side_effect = lease
        with mock.patch.object(server, "pool", pool), \
                mock.patch.object(server, "resolve_build", return_value=Path("x.xml")), \
                mock.patch.object(server, "check_source_fresh"), \
                mock.patch.object(server, "Auditor", return_value=mock.Mock()), \
                mock.patch.object(server, "apply_changes", side_effect=error):
            handler.do_POST()
        return handler.status, json.loads(handler.wfile.getvalue())

    def test_stale_audit_returns_conflict_with_error_kind(self):
        message = "Build changed since audit; re-run the audit (x.xml)"
        status, body = self.post_apply(optimize.StaleAudit(message))
        self.assertEqual(status, 409)
        self.assertEqual(body, {"error": message, "kind": "StaleAudit"})

    def test_change_error_returns_bad_request(self):
        status, body = self.post_apply(optimize.ChangeError("boom"))
        self.assertEqual(status, 400)
        self.assertEqual(body, {"error": "boom", "kind": "InvalidRequest"})

    def test_lua_error_returns_sanitized_engine_error(self):
        status, body = self.post_apply(pobhost.LuaError("first line\nsecret traceback"))
        self.assertEqual(status, 500)
        self.assertEqual(body, {"error": "engine error: first line", "kind": "EngineError"})

    def test_unknown_error_does_not_leak_message(self):
        status, body = self.post_apply(RuntimeError("private data"))
        self.assertEqual(status, 500)
        self.assertEqual(body, {"error": "internal error (RuntimeError)", "kind": "EngineError"})


class GuideRoutePureTests(unittest.TestCase):
    def test_capability_table(self):
        good = {"compareTab": True, "comparePowerBuilder": True, "compareEntry": True,
                "pobVersion": "2.64.1-beta"}
        self.assertEqual(guide_routes.capability_from_probe(good, True), {
            "available": True, "pobVersion": "2.64.1-beta", "reason": None})
        old = guide_routes.capability_from_probe({**good, "compareTab": False,
                                                  "pobVersion": "2.60.0-dev"}, True)
        self.assertEqual(old["reason"],
                         "Guide check needs Path of Building 2.64 or newer; yours is 2.60.0.")
        missing = guide_routes.capability_from_probe(good, False)
        self.assertEqual(missing["reason"], "Guide check is not installed in this build.")

    def test_job_progress_records_new_stages_and_testing_counts(self):
        job = {"stages": []}
        progress = guide_routes.JobProgress(job)
        progress("Testing differences")
        progress("Testing differences")
        progress.testing(2, 7)
        self.assertEqual(job, {"stages": ["Testing differences"], "stage": "Testing differences",
                               "progress": "Testing differences", "done": 2, "total": 7})

    def test_handle_post_dispatches_exact_routes(self):
        state = object()
        with mock.patch.object(guide_routes, "start_check", return_value={"route": "check"}), \
                mock.patch.object(guide_routes, "preview", return_value={"route": "preview"}), \
                mock.patch.object(guide_routes, "apply", return_value={"route": "apply"}):
            self.assertEqual(guide_routes.handle_post(state, "/api/guide-check", {}), {"route": "check"})
            self.assertEqual(guide_routes.handle_post(state, "/api/guide-preview", {}), {"route": "preview"})
            self.assertEqual(guide_routes.handle_post(state, "/api/guide-apply", {}), {"route": "apply"})
        with self.assertRaises(InvalidRequest):
            guide_routes.handle_post(state, "/api/nope", {})


class GuideRouteJobTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        runlog.setup(self.root, token="t0ken")
        self.player = self.root / "player.xml"
        self.player.write_text("player", encoding="utf-8")
        self.settings_patch = mock.patch.object(
            guide_routes.build_settings, "SETTINGS_FILE", self.root / "build_settings.json")
        self.settings_patch.start()
        self.pool = CountingPool()
        self.state = SimpleNamespace(
            jobs={}, pool=self.pool, engine_lock=threading.Lock(), Auditor=mock.Mock(),
            BUILDS_DIR=self.root, DEFAULT_OUT_DIR=self.root,
            resolve_build=lambda rel: self.player,
            load_scenarios=lambda: {"Mapping", "Pinnacle Boss"}, guide_capability=None,
        )

    def tearDown(self):
        self.settings_patch.stop()
        self.temp.cleanup()

    def spec(self):
        return {"playerPath": self.player, "guideLink": "pobb.in/Guide1", "build": "player.xml",
                "settings": {"includeDrafts": False, "leaveOut": [], "scenario": "Mapping"}}

    def test_import_api_errors_are_public_and_do_not_lease(self):
        cases = [
            (pobbin.TooLarge(pobbin.MSG_TOO_LARGE), "TooLarge"),
            (pobbin.FetchFailed("fetch failed"), "FetchFailed"),
            (pobbin.Unreadable(pobbin.MSG_UNREADABLE), "Unreadable"),
        ]
        for error, kind in cases:
            with self.subTest(kind=kind):
                self.state.jobs = {"j": guide_routes._new_job("j", "player.xml", self.spec()["settings"])}
                with mock.patch.object(pobbin, "import_link", side_effect=error):
                    guide_routes.run_guide_job(self.state, "j", self.spec())
                job = self.state.jobs["j"]
                self.assertEqual((job["status"], job["error"], job["errorKind"]),
                                 ("error", str(error), kind))
                self.assertIsNone(job["report"])
        self.assertEqual(self.pool.entered, 0)

    def test_internal_error_is_sanitized_logged_and_replaces_engine(self):
        made = []

        def factory(slot):
            engine = ClosingEngine()
            made.append(engine)
            return engine

        pool = engine_pool.EnginePool(size=1, factory=factory)
        self.addCleanup(pool.close)
        self.state.pool = pool
        auditor = SimpleNamespace(source_sha256="sha", obtainable=object())
        self.state.Auditor = mock.Mock(return_value=auditor)
        self.state.jobs["j"] = guide_routes._new_job("j", "player.xml", self.spec()["settings"])
        imported = {"id": "Guide1", "path": str(self.root / "guide.xml")}
        error = pobhost.LuaError("secret first line\ntraceback with C:\\Users\\x")
        with mock.patch.object(pobbin, "import_link", return_value=imported), \
                mock.patch.object(guide_routes, "load_run_check",
                                  return_value=mock.Mock(side_effect=error)):
            guide_routes.run_guide_job(self.state, "j", self.spec())
        job = self.state.jobs["j"]
        self.assertEqual(job["error"], "The check failed. Reference ID is in the log.")
        self.assertEqual(job["referenceId"], "j")
        self.assertNotIn("secret", job["error"])
        self.assertNotIn("C:\\", job["error"])
        self.assertEqual(len(made), 2)
        self.assertTrue(made[0].closed)
        records = [json.loads(line) for path in (self.root / "logs").glob("run-*.jsonl")
                   for line in path.read_text(encoding="utf-8").splitlines()]
        self.assertTrue(any(row["level"] == "ERROR" and row["jobId"] == "j" for row in records))

    def test_double_click_reuses_running_job_then_allows_another(self):
        entered, release, finished = threading.Event(), threading.Event(), threading.Event()

        def blocked(state, job_id, spec):
            entered.set()
            release.wait(2)
            state.jobs[job_id]["status"] = "done"
            finished.set()

        request = {"player": {"build": "player.xml"}, "guide": {"link": "pobb.in/Guide1"},
                   "scenario": "Mapping"}
        with mock.patch.object(guide_routes, "run_guide_job", side_effect=blocked):
            first = guide_routes.start_check(self.state, request)
            self.assertTrue(entered.wait(1))
            second = guide_routes.start_check(self.state, request)
            self.assertEqual(second, {"jobId": first["jobId"], "running": True})
            self.assertEqual(len(self.state.jobs), 1)
            release.set()
            self.assertTrue(finished.wait(1))
            third = guide_routes.start_check(self.state, request)
        self.assertFalse(third["running"])
        self.assertNotEqual(third["jobId"], first["jobId"])
        self.assertEqual(len(self.state.jobs), 2)

    def test_bad_links_and_builds_fail_before_creating_job(self):
        bad = {"player": {"link": "evil.example/x"}, "guide": {"link": "pobb.in/Guide1"}}
        with self.assertRaisesRegex(InvalidRequest, "That is not a pobb.in build link"):
            guide_routes.start_check(self.state, bad)
        self.state.resolve_build = mock.Mock(side_effect=InvalidRequest("bad build"))
        with self.assertRaisesRegex(InvalidRequest, "bad build"):
            guide_routes.start_check(self.state, {
                "player": {"build": "../x.xml"}, "guide": {"link": "pobb.in/Guide1"}})
        self.assertEqual(self.state.jobs, {})


class GuidePreviewApplyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.player = self.root / "player.xml"
        self.player.write_text("player", encoding="utf-8")
        self.report = fake_result()
        self.ids = [self.report["rows"][0]["id"]]
        self.obtainable = object()
        self.pool = CountingPool(engine=object())
        self.auditor = mock.Mock()
        self.state = SimpleNamespace(
            jobs={"j": self.done_job()}, pool=self.pool, engine_lock=threading.Lock(),
            Auditor=mock.Mock(return_value=self.auditor), BUILDS_DIR=self.root,
            DEFAULT_OUT_DIR=self.root, guide_capability=None,
        )

    def tearDown(self):
        self.temp.cleanup()

    def done_job(self):
        return {"id": "j", "kind": "guide", "status": "done", "build": "player.xml",
                "report": self.report, "sha": hashlib.sha256(b"player").hexdigest(),
                "playerPath": self.player, "obtainable": self.obtainable,
                "settings": {"includeDrafts": False, "leaveOut": ["Aura"], "scenario": "Mapping"}}

    def test_stale_preview_and_apply_do_not_lease(self):
        self.player.write_text("changed", encoding="utf-8")
        for function in (guide_routes.preview, guide_routes.apply):
            with self.subTest(function=function.__name__), self.assertRaisesRegex(
                    guide_routes.StaleAudit, "^Your build changed since the check; run it again\\.$"):
                function(self.state, {"jobId": "j", "ids": self.ids})
        self.assertEqual(self.pool.entered, 0)

    def test_preview_shape_and_obtainability_reuse(self):
        result = {"ok": True, "refused": None, "conflicts": [], "ids": self.ids,
                  "combined": None, "points": None, "violations": []}
        with mock.patch.object(guide_apply, "predict", return_value=result):
            actual = guide_routes.preview(self.state, {"jobId": "j", "ids": self.ids})
        self.assertEqual(actual, result)
        self.assertEqual(set(actual), {"ok", "refused", "conflicts", "ids", "combined",
                                       "points", "violations"})
        self.state.Auditor.assert_called_once_with(
            self.player, False, disabled_skills=["Aura"], scenario="Mapping",
            engine=self.pool.engine, obtainable=self.obtainable)

    def test_apply_shape_counts_and_carries_settings(self):
        saved_path = self.root / "saved.xml"
        base = {"ok": True, "refused": None, "conflicts": [], "ids": self.ids,
                "combined": None, "points": None, "violations": [], "saved": True,
                "path": str(saved_path), "fileName": saved_path.name,
                "reload": {"checked": True, "equal": True, "diffs": [], "error": None}}
        with mock.patch.object(guide_apply, "save", return_value=base), \
                mock.patch.object(guide_routes.build_settings, "update") as update:
            actual = guide_routes.apply(self.state, {"jobId": "j", "ids": self.ids})
        expected = {"ok", "refused", "conflicts", "ids", "combined", "points", "violations",
                    "saved", "path", "fileName", "reload", "applied", "notApplied"}
        self.assertEqual(set(actual), expected)
        self.assertEqual(actual["applied"], {"count": 1, "ids": self.ids,
                                             "labels": [self.report["rows"][0]["label"]]})
        self.assertEqual(actual["notApplied"], guide_apply.not_applied(self.report, self.ids))
        update.assert_called_once_with("saved.xml", leaveOut=["Aura"], scenario="Mapping")


class CountingPool:
    def __init__(self, engine=object()):
        self.engine = engine
        self.entered = 0

    @contextmanager
    def lease(self):
        self.entered += 1
        yield self.engine


class ClosingEngine:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


if __name__ == "__main__":
    unittest.main()
