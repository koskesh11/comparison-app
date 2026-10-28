"""The job store (app/jobs.py): one job at a time, replaced not edited, a cap on finished jobs, stuck jobs given up."""

from comparison_app.app.jobs import TIMEOUT, JobError, JobStatus, JobStore, Stage


class Clock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_one_job_runs_at_a_time() -> None:
    store = JobStore()
    first, created = store.start("compare", "Worb")
    again, created_again = store.start("compare", "CoC EK Assa")
    assert (created, created_again, again) == (True, False, first)


def test_progress_and_finish_replace_the_job() -> None:
    store = JobStore()
    job, _ = store.start("compare", "Worb")
    store.progress(job.id, Stage.READING, 1, 3)
    reading = store.get(job.id)
    assert reading is not None and (reading.stage, reading.done, reading.total) == (Stage.READING, 1, 3)
    store.finish(job.id, {"ok": True})
    done = store.get(job.id)
    assert done is not None and (done.status, done.stage, done.report) == (JobStatus.DONE, Stage.DONE, {"ok": True})
    assert job.stage is Stage.QUEUED  # the first Job object is unchanged
    assert store.start("compare", "Worb")[1] is True  # nothing runs now


def test_a_failed_job_keeps_its_error() -> None:
    store = JobStore()
    job, _ = store.start("compare", "Worb")
    store.fail(job.id, JobError("EngineError", "PoB failed", "ref1"))
    failed = store.get(job.id)
    assert failed is not None and failed.error == JobError("EngineError", "PoB failed", "ref1")


def test_only_the_newest_finished_jobs_are_kept() -> None:
    clock = Clock()
    store = JobStore(keep=2, clock=clock)
    ids = []
    for number in range(3):
        clock.now = float(number)
        job, _ = store.start("compare", str(number))
        store.finish(job.id, {})
        ids.append(job.id)
    assert [store.get(job_id) is not None for job_id in ids] == [False, True, True]


def test_a_stuck_job_is_given_up_and_stays_given_up() -> None:
    clock = Clock()
    store = JobStore(run_limit_s=10.0, clock=clock)
    job, _ = store.start("compare", "Worb")
    clock.now = 11.0
    given_up = store.get(job.id)
    assert given_up is not None and (given_up.status, given_up.error) == (JobStatus.ERROR, TIMEOUT)
    store.finish(job.id, {"late": True})  # the runner finishing late changes nothing
    late = store.get(job.id)
    assert late is not None and late.report is None
