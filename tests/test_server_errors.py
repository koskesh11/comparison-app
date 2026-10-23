import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent
ENGINE_DIR = PROJECT_ROOT / "engine"

if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

import optimize
import server


class FakeHandler(server.Handler):
    def __init__(self, path: str, body: bytes):
        self.path = path
        self.headers = {"Content-Length": str(len(body))}
        self.rfile = io.BytesIO(body)
        self.wfile = io.BytesIO()
        self.status = None

    def send_response(self, status, message=None):
        self.status = int(status)

    def send_header(self, keyword, value):
        pass

    def end_headers(self):
        pass


class ServerErrorTests(unittest.TestCase):
    job_id = "server-error-test"

    def setUp(self):
        server.jobs[self.job_id] = {"status": "done", "auditor": object(), "build": "x.xml"}

    def tearDown(self):
        server.jobs.pop(self.job_id, None)

    def post_apply(self):
        body = json.dumps({"ids": [1]}).encode("utf-8")
        handler = FakeHandler(f"/api/jobs/{self.job_id}/apply", body)
        handler.do_POST()
        return handler.status, json.loads(handler.wfile.getvalue())

    def test_stale_audit_returns_conflict_with_error_kind(self):
        message = "Build changed since audit; re-run the audit (x.xml)"
        with mock.patch.object(server, "apply_changes", side_effect=optimize.StaleAudit(message)):
            status, body = self.post_apply()

        self.assertEqual(status, 409)
        self.assertEqual(body, {"error": message, "kind": "StaleAudit"})

    def test_change_error_returns_bad_request(self):
        with mock.patch.object(server, "apply_changes", side_effect=optimize.ChangeError("boom")):
            status, body = self.post_apply()

        self.assertEqual(status, 400)
        self.assertEqual(body, {"error": "boom"})


if __name__ == "__main__":
    unittest.main()
