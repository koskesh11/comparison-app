"""Jobs: a comparison runs as a job the page polls (docs/designs/target-design/interfaces.md 4.7).

One job runs at a time: a second start returns the running one. Jobs are replaced, never edited. Finished jobs beyond
`keep` are dropped (the first app's job dict never forgot one), and a job running longer than the limit is given up,
for every kind of job (the first app's stuck-job rule lived in one route only). Progress carries stage ids, no
words: the words live in app/present.
"""

import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Any

from comparison_app.app.settings import JOB_KEEP, JOB_RUN_LIMIT_S


class JobStatus(StrEnum):
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


class Stage(StrEnum):
    QUEUED = "queued"
    LOADING = "loading"  # opening your build and the target
    READING = "reading"  # the chains, snapshots and summaries
    COMPARING = "comparing"  # the table, the settings check, the config differences
    DONE = "done"


@dataclass(frozen=True)
class JobError:
    kind: str  # the stable id the page switches on (app/errors.py)
    message: str
    reference_id: str | None  # in the log, for an internal error


@dataclass(frozen=True)
class Job:
    id: str
    kind: str
    build: str
    status: JobStatus
    stage: Stage
    done: int | None
    total: int | None
    error: JobError | None
    report: dict[str, Any] | None  # the JSON the page draws (app/present/report.py)
    started_at: float
    finished_at: float | None


TIMEOUT = JobError("Timeout", "the comparison took too long and was given up", None)


class JobStore:
    """Thread-safe; the server's handler threads and the job's runner thread share it."""

    def __init__(
        self, *, keep: int = JOB_KEEP, run_limit_s: float = JOB_RUN_LIMIT_S, clock: Callable[[], float] = time.monotonic
    ) -> None:
        self._keep, self._limit, self._clock = keep, run_limit_s, clock
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def start(self, kind: str, build: str) -> tuple[Job, bool]:
        """(the job, whether it was created): a second start while one runs returns the running job."""
        with self._lock:
            self._sweep()
            running = next((job for job in self._jobs.values() if job.status is JobStatus.RUNNING), None)
            if running is not None:
                return running, False
            job = Job(
                uuid.uuid4().hex,
                kind,
                build,
                JobStatus.RUNNING,
                Stage.QUEUED,
                None,
                None,
                None,
                None,
                self._clock(),
                None,
            )
            self._jobs[job.id] = job
            return job, True

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            self._sweep()
            return self._jobs.get(job_id)

    def progress(self, job_id: str, stage: Stage, done: int | None = None, total: int | None = None) -> None:
        self._update(job_id, stage=stage, done=done, total=total)

    def finish(self, job_id: str, report: dict[str, Any]) -> None:
        self._update(job_id, status=JobStatus.DONE, stage=Stage.DONE, report=report, finished_at=self._clock())

    def fail(self, job_id: str, error: JobError) -> None:
        self._update(job_id, status=JobStatus.ERROR, error=error, finished_at=self._clock())

    def _update(self, job_id: str, **fields: Any) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is not None and job.status is JobStatus.RUNNING:  # a given-up job stays given up
                self._jobs[job_id] = replace(job, **fields)

    def _sweep(self) -> None:
        now = self._clock()
        for job in list(self._jobs.values()):
            if job.status is JobStatus.RUNNING and now - job.started_at > self._limit:
                self._jobs[job.id] = replace(job, status=JobStatus.ERROR, error=TIMEOUT, finished_at=now)
        finished = sorted(
            (job for job in self._jobs.values() if job.finished_at is not None), key=lambda job: job.finished_at or 0.0
        )
        for job in finished[: max(0, len(finished) - self._keep)]:
            del self._jobs[job.id]
