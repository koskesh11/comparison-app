"""The run log (app/logging_setup.py): JSON lines, the job's context on every record, the token never written, old
files removed (cases from the first app's tests/test_runlog.py)."""

import json
import logging
import os
import time
from pathlib import Path

from comparison_app.app.logging_setup import RETENTION_DAYS, job_context, redact, setup

TOKEN = "s3cret-token-value"  # noqa: S105 - a made-up token the test must not find in the log


def records(data_dir: Path) -> list[dict[str, object]]:
    (log,) = (data_dir / "logs").glob("run-*.jsonl")
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]


def test_a_record_carries_its_job_and_hides_the_token(tmp_path: Path) -> None:
    setup(tmp_path, TOKEN)
    reset = job_context.set(("job1", "Worb"))
    try:
        logging.getLogger("comparison_app.compare.service").warning(
            "refused X-Api-Token: %s from %s", TOKEN, "127.0.0.1", extra={"event": "auth_refused"}
        )
    finally:
        job_context.reset(reset)
    (record,) = records(tmp_path)
    assert (record["jobId"], record["build"], record["event"], record["level"]) == (
        "job1",
        "Worb",
        "auth_refused",
        "WARNING",
    )
    assert TOKEN not in json.dumps(record) and "[redacted]" in str(record["message"])


def test_a_traceback_is_written_redacted(tmp_path: Path) -> None:
    setup(tmp_path, TOKEN)
    try:
        raise ValueError(f"token {TOKEN}")
    except ValueError:
        logging.getLogger("comparison_app.app.runner").exception("job failed")
    (record,) = records(tmp_path)
    assert "ValueError" in str(record["traceback"]) and TOKEN not in str(record["traceback"])


def test_old_log_files_are_removed(tmp_path: Path) -> None:
    logs = tmp_path / "logs"
    logs.mkdir()
    old = logs / "run-20200101.jsonl"
    old.write_text("{}\n", encoding="utf-8")
    past = time.time() - (RETENTION_DAYS + 1) * 86400
    os.utime(old, (past, past))
    setup(tmp_path, TOKEN)
    assert not old.exists()


def test_redact_covers_the_header_form() -> None:
    assert redact("X-Api-Token: abc123", "") == "X-Api-Token: [redacted]"
