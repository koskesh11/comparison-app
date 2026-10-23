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
import pobhost
import runlog
import server


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


if __name__ == "__main__":
    unittest.main()
