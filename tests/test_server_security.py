import io
import json
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent
ENGINE_DIR = PROJECT_ROOT / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

import optimize
import runlog
import server


class FakeHandler(server.Handler):
    def __init__(self, path: str, body: bytes = b"", headers: dict | None = None):
        self.path = path
        self.headers = {"Host": "127.0.0.1:8765", "Content-Length": str(len(body)), **(headers or {})}
        self.rfile = io.BytesIO(body)
        self.wfile = io.BytesIO()
        self.status = None
        self.response_headers = {}

    def send_response(self, status, message=None):
        self.status = int(status)

    def send_header(self, keyword, value):
        self.response_headers[keyword] = value

    def end_headers(self):
        pass

    def response_json(self):
        return json.loads(self.wfile.getvalue())


class FakePool:
    def __init__(self, engine=object()):
        self.engine = engine
        self.entered = 0

    @contextmanager
    def lease(self):
        self.entered += 1
        yield self.engine


class ServerSecurityTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        runlog.setup(Path(self.temp_dir.name), token="t0ken")
        self.token_patch = mock.patch.object(server, "API_TOKEN", "t0ken")
        self.token_patch.start()
        server.jobs.clear()

    def tearDown(self):
        server.jobs.clear()
        self.token_patch.stop()
        self.temp_dir.cleanup()

    def get(self, path: str, headers: dict | None = None) -> FakeHandler:
        handler = FakeHandler(path, headers=headers)
        handler.do_GET()
        return handler

    def post(self, path: str, data: dict, headers: dict | None = None) -> FakeHandler:
        body = json.dumps(data).encode("utf-8")
        handler = FakeHandler(path, body, headers)
        handler.do_POST()
        return handler

    def test_api_requires_token(self):
        missing = self.get("/api/builds")
        wrong = self.get("/api/builds", {"X-Api-Token": "wrong"})
        with mock.patch.object(server, "API_TOKEN", ""):
            empty_server_token = self.get("/api/builds", {"X-Api-Token": "t0ken"})
        with mock.patch.object(server, "list_builds", return_value=[]), \
                mock.patch.object(server, "load_scenarios", return_value={"Mapping"}), \
                mock.patch.object(server.build_settings, "_load_all", return_value={}):
            right = self.get("/api/builds", {"X-Api-Token": "t0ken"})

        self.assertEqual((missing.status, missing.response_json()["kind"]), (401, "Unauthorized"))
        self.assertEqual((wrong.status, wrong.response_json()["kind"]), (401, "Unauthorized"))
        self.assertEqual(empty_server_token.status, 401)
        self.assertEqual(right.status, 200)
        self.assertFalse(any(name.lower().startswith("access-control") for name in right.response_headers))

    def test_api_rejects_foreign_origin_and_host(self):
        token = {"X-Api-Token": "t0ken"}
        self.assertEqual(self.get("/api/builds", {**token, "Origin": "http://evil.example"}).status, 403)
        self.assertEqual(self.get("/api/builds", {**token, "Host": "evil.example:8765"}).status, 403)
        self.assertEqual(self.get("/api/builds", {"Host": "evil.example:8765"}).status, 403)
        with mock.patch.object(server, "list_builds", return_value=[]), \
                mock.patch.object(server, "load_scenarios", return_value=set()), \
                mock.patch.object(server.build_settings, "_load_all", return_value={}):
            for headers in (
                token,
                {**token, "Host": "localhost:8765"},
                {**token, "Origin": "http://localhost:8765"},
            ):
                self.assertEqual(self.get("/api/builds", headers).status, 200)

    def test_unknown_path_returns_named_json_error(self):
        handler = self.get("/api/unknown", {"X-Api-Token": "t0ken"})
        self.assertEqual(handler.status, 404)
        self.assertEqual(handler.response_json(), {"error": "not found", "kind": "NotFound"})

    def test_gui_contains_token_without_requiring_header(self):
        handler = self.get("/")
        text = handler.wfile.getvalue().decode("utf-8")
        self.assertEqual(handler.status, 200)
        self.assertIn("t0ken", text)
        self.assertNotIn("__API_TOKEN__", text)

    def test_done_job_holds_no_engine_or_auditor(self):
        engine = object()
        pool = FakePool(engine)
        auditor = mock.Mock()
        auditor.run.return_value = {"suggestions": [{"x": 1}]}
        auditor.source_sha256 = "abc"
        server.jobs["j"] = {
            "id": "j", "status": "running", "progress": "Queued", "build": "x.xml",
            "error": None, "report": None, "sha": None,
            "settings": {"includeDrafts": False, "leaveOut": [], "scenario": "Mapping"},
        }
        with mock.patch.object(server, "pool", pool), mock.patch.object(server, "Auditor", return_value=auditor):
            server.run_audit("j", Path("x.xml"), False, [], "Mapping")

        job = server.jobs["j"]
        self.assertEqual(job["status"], "done")
        self.assertNotIn("auditor", job)
        self.assertNotIn(auditor, job.values())
        self.assertNotIn(engine, job.values())
        self.assertTrue({"sha", "settings", "auditor"}.isdisjoint(server.Handler.public_job(job)))

    def test_apply_rebuilds_auditor_using_pool(self):
        engine = object()
        pool = FakePool(engine)
        auditor = mock.Mock()
        outcome = {"saved": False, "path": None, "dims": {}, "violations": []}
        server.jobs["j"] = self.done_job()
        with mock.patch.object(server, "pool", pool), \
                mock.patch.object(server, "resolve_build", return_value=Path("x.xml")), \
                mock.patch.object(server, "check_source_fresh"), \
                mock.patch.object(server, "Auditor", return_value=auditor) as auditor_type, \
                mock.patch.object(server, "apply_changes", return_value=outcome) as apply:
            handler = self.post("/api/jobs/j/apply", {"ids": [1]}, {"X-Api-Token": "t0ken"})

        self.assertEqual(handler.status, 200)
        self.assertEqual(pool.entered, 1)
        auditor_type.assert_called_once_with(Path("x.xml"), False, disabled_skills=[], scenario="Mapping", engine=engine)
        self.assertEqual(auditor.suggestions, [{"x": 1}])
        self.assertEqual(auditor.source_sha256, "abc")
        apply.assert_called_once_with(auditor, [1], force=False)
        self.assertEqual(handler.response_json(), outcome)

    def test_stale_apply_does_not_lease_engine(self):
        pool = FakePool()
        server.jobs["j"] = self.done_job()
        with mock.patch.object(server, "pool", pool), \
                mock.patch.object(server, "resolve_build", return_value=Path("x.xml")), \
                mock.patch.object(server, "check_source_fresh", side_effect=optimize.StaleAudit("changed")):
            handler = self.post("/api/jobs/j/apply", {"ids": [1]}, {"X-Api-Token": "t0ken"})

        self.assertEqual(handler.status, 409)
        self.assertEqual(handler.response_json()["kind"], "StaleAudit")
        self.assertEqual(pool.entered, 0)

    @staticmethod
    def done_job() -> dict:
        return {
            "id": "j", "status": "done", "progress": "Done", "build": "x.xml",
            "error": None, "report": {"suggestions": [{"x": 1}]}, "sha": "abc",
            "settings": {"includeDrafts": False, "leaveOut": [], "scenario": "Mapping"},
        }


if __name__ == "__main__":
    unittest.main()
