import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
ENGINE_DIR = TESTS_DIR.parent / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

import api_errors
import optimize
import pobhost
import runlog


class RunLogTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.userdata = Path(self.temp_dir.name)

    def tearDown(self):
        runlog.set_token("")
        self.temp_dir.cleanup()

    def records(self) -> list[dict]:
        files = list((self.userdata / "logs").glob("run-*.jsonl"))
        self.assertEqual(len(files), 1)
        return [json.loads(line) for line in files[0].read_text(encoding="utf-8").splitlines()]

    def test_log_redacts_secrets(self):
        logger = runlog.setup(self.userdata, token="tok")
        logger = runlog.setup(self.userdata, token="tok")
        runlog.log_event("INFO", "plain", "X-Api-Token: tok POESESSID=abcdef123")
        logger.info("%s %s", "tok", '"POESESSID": "abcdef123"', extra={"event": "args"})
        try:
            raise RuntimeError("POESESSID: abcdef123 and X-Api-Token: tok")
        except RuntimeError as error:
            runlog.log_event("ERROR", "failed", "token tok", exc=error)

        raw = "\n".join(json.dumps(record) for record in self.records())
        self.assertNotIn("tok", raw)
        self.assertNotIn("abcdef123", raw)
        self.assertIn("[redacted]", raw)
        records = self.records()
        self.assertEqual(len(records), 3)
        self.assertIn("RuntimeError", records[-1]["traceback"])
        for record in records:
            self.assertTrue({"ts", "level", "event", "message"} <= record.keys())

    def test_retention(self):
        logs = self.userdata / "logs"
        logs.mkdir()
        old = logs / "run-20200101.jsonl"
        recent = logs / "run-20200102.jsonl"
        old.touch()
        recent.touch()
        now = time.time()
        os.utime(old, (now - 15 * 86400, now - 15 * 86400))
        os.utime(recent, (now - 13 * 86400, now - 13 * 86400))

        runlog.setup(self.userdata)

        self.assertFalse(old.exists())
        self.assertTrue(recent.exists())

    def test_one_json_object_per_line(self):
        logger = runlog.setup(self.userdata)
        logger.info("one", extra={"event": "first", "jobId": "j", "build": "b.xml"})
        logger.warning("two", extra={"event": "second"})

        records = self.records()
        self.assertEqual([record["message"] for record in records], ["one", "two"])
        self.assertEqual(records[0]["jobId"], "j")
        self.assertIsNone(records[1]["jobId"])


class ApiErrorTests(unittest.TestCase):
    def test_lua_error_uses_first_non_empty_line(self):
        status, body = api_errors.classify(pobhost.LuaError("\nfirst line\ntrace details"))
        self.assertEqual(status, 500)
        self.assertEqual(body, {"error": "engine error: first line", "kind": "EngineError"})

    def test_unknown_error_hides_message(self):
        status, body = api_errors.classify(RuntimeError("sensitive detail"))
        self.assertEqual(status, 500)
        self.assertEqual(body, {"error": "internal error (RuntimeError)", "kind": "EngineError"})

    def test_key_error_names_missing_field(self):
        status, body = api_errors.classify(KeyError("build"))
        self.assertEqual(status, 400)
        self.assertEqual(body, {"error": "missing field build", "kind": "InvalidRequest"})

    def test_optimize_stale_audit_keeps_named_kind(self):
        status, body = api_errors.classify(optimize.StaleAudit("changed"))
        self.assertEqual(status, 409)
        self.assertEqual(body, {"error": "changed", "kind": "StaleAudit"})


if __name__ == "__main__":
    unittest.main()
