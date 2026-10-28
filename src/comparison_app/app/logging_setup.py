"""The run log: one JSON line per record, a file per day, 14 days kept, the API token never written (the first app's
engine/runlog.py, kept with three changes).

- The handler sits on the package logger `comparison_app`; domain code logs with logging.getLogger(__name__).
- The job id and build name reach every record through a context value app/runner.py sets (interfaces.md 4.9), so
  domain functions never pass them around.
- A record that cannot be written goes to logging's own error report (Handler.handleError) instead of vanishing; the
  first app returned silently. Its POESESSID redaction is dropped: this app never handles that cookie.
"""

import contextvars
import json
import logging
import re
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path

LOGGER_NAME = "comparison_app"
RETENTION_DAYS = 14
_HEADER = re.compile(r"(X-Api-Token\s*:\s*)([^\s,;]+)", re.IGNORECASE)

job_context: contextvars.ContextVar[tuple[str | None, str | None]] = contextvars.ContextVar(
    "job_context", default=(None, None)
)  # (job id, build name), set by app/runner.py for the job's thread


def redact(text: str, token: str) -> str:
    clean = text.replace(token, "[redacted]") if token else text
    return _HEADER.sub(r"\1[redacted]", clean)


class JsonLinesHandler(logging.Handler):
    def __init__(self, log_dir: Path, token: str) -> None:
        super().__init__()
        self.log_dir, self.token = log_dir, token

    def emit(self, record: logging.LogRecord) -> None:
        try:
            now = datetime.now(UTC)
            job_id, build = job_context.get()
            detail = "".join(traceback.format_exception(*record.exc_info)) if record.exc_info else None
            payload = {
                "ts": now.isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "event": getattr(record, "event", None),
                "jobId": job_id,
                "build": build,
                "message": redact(record.getMessage(), self.token),
                "traceback": redact(detail, self.token) if detail else None,
            }
            with (self.log_dir / f"run-{now:%Y%m%d}.jsonl").open("a", encoding="utf-8") as output:
                output.write(json.dumps(payload, ensure_ascii=False) + "\n")
        except Exception:  # noqa: BLE001 - logging must not break a comparison; handleError reports it
            self.handleError(record)


def _remove_expired(log_dir: Path) -> None:
    cutoff = time.time() - RETENTION_DAYS * 86400
    for path in log_dir.glob("run-*.jsonl"):
        if path.stat().st_mtime < cutoff:
            path.unlink(missing_ok=True)


def setup(data_dir: Path, token: str) -> logging.Logger:
    """The package logger writing to data_dir/logs, with the token redacted; called once by app/main.py."""
    log_dir = data_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    _remove_expired(log_dir)
    logger = logging.getLogger(LOGGER_NAME)
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
    logger.addHandler(JsonLinesHandler(log_dir, token))
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
