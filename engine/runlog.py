"""Structured, redacted JSON-lines logging for local server runs."""

import json
import logging
import re
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

RETENTION_DAYS = 14
_TOKEN = ""
_LOGGER = logging.getLogger("pob.run")
_LOGGER.propagate = False

_HEADER = re.compile(r"(X-Api-Token\s*:\s*)([^\s,;]+)", re.IGNORECASE)
_JSON_SESSION = re.compile(r'("POESESSID"\s*:\s*")([^"]*)(")', re.IGNORECASE)
_SESSION = re.compile(r"(POESESSID\s*(?:=|:\s*))([^;\s,\"}]+)", re.IGNORECASE)


def set_token(token: str) -> None:
    global _TOKEN
    _TOKEN = token


def redact(text: str) -> str:
    """Return text with known authentication secrets removed."""
    clean = str(text)
    if _TOKEN:
        clean = clean.replace(_TOKEN, "[redacted]")
    clean = _HEADER.sub(r"\1[redacted]", clean)
    clean = _JSON_SESSION.sub(r"\1[redacted]\3", clean)
    return _SESSION.sub(r"\1[redacted]", clean)


class Redactor(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact(record.getMessage())
        record.args = None
        if record.exc_info:
            detail = "".join(traceback.format_exception(*record.exc_info))
            record.traceback_text = redact(detail)
            record.exc_info = None
            record.exc_text = None
        return True


class DailyJsonHandler(logging.Handler):
    def __init__(self, log_dir: Path):
        super().__init__()
        self.log_dir = log_dir
        self.addFilter(Redactor())

    def emit(self, record: logging.LogRecord) -> None:
        try:
            now = datetime.now(timezone.utc)
            payload = {
                "ts": now.isoformat(),
                "level": record.levelname,
                "event": getattr(record, "event", None),
                "jobId": getattr(record, "jobId", None),
                "build": getattr(record, "build", None),
                "message": record.getMessage(),
                "traceback": getattr(record, "traceback_text", None),
            }
            path = self.log_dir / f"run-{now:%Y%m%d}.jsonl"
            with path.open("a", encoding="utf-8") as output:
                output.write(json.dumps(payload, ensure_ascii=False) + "\n")
        except Exception:
            return


def _remove_expired(log_dir: Path) -> None:
    cutoff = time.time() - RETENTION_DAYS * 86400
    for path in log_dir.glob("run-*.jsonl"):
        try:
            if path.stat().st_mtime < cutoff:
                path.unlink()
        except FileNotFoundError:
            continue


def setup(userdata_dir: Path | None = None, token: str = "") -> logging.Logger:
    log_dir = (userdata_dir or Path(__file__).resolve().parent / "userdata") / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    _remove_expired(log_dir)
    set_token(token)
    for handler in list(_LOGGER.handlers):
        _LOGGER.removeHandler(handler)
        handler.close()
    _LOGGER.addHandler(DailyJsonHandler(log_dir))
    _LOGGER.setLevel(logging.INFO)
    _LOGGER.propagate = False
    return _LOGGER


def log_event(level: str | int, event: str, message: str,
              job_id: str | None = None, build: str | None = None,
              exc: BaseException | None = None) -> None:
    numeric_level = logging._nameToLevel.get(level.upper(), logging.INFO) if isinstance(level, str) else level
    exc_info = (type(exc), exc, exc.__traceback__) if exc is not None else None
    _LOGGER.log(numeric_level, message, extra={"event": event, "jobId": job_id, "build": build},
                exc_info=exc_info)
