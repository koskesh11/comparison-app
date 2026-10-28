"""One comparison job end to end (app/runner.py, app/state.py): your build from a Builds folder, the target from a
saved import (no network), the report in the job; a refused input and a PoB failure end the job with their kind."""

from pathlib import Path

import pytest

from comparison_app.app.inputs import compare_request
from comparison_app.app.jobs import JobStatus, JobStore
from comparison_app.app.runner import run_compare
from comparison_app.app.settings import ENV_BUILDS_DIR, ENV_HOME, ENV_POB_DIR, Settings
from comparison_app.app.state import AppState
from comparison_app.intake.store import ImportStore
from comparison_app.pob.session import PobSession

pytestmark = pytest.mark.pob


def state_for(tmp_path: Path, session: PobSession, reference_xml: dict[str, str]) -> AppState:
    builds = tmp_path / "Builds"
    (builds / "3.29").mkdir(parents=True)
    (builds / "3.29" / "Worb.xml").write_text(reference_xml["Worb"], encoding="utf-8")
    env = {ENV_HOME: str(tmp_path), ENV_BUILDS_DIR: str(builds), ENV_POB_DIR: str(tmp_path / "pob")}
    settings = Settings.from_environment(env)
    ImportStore(settings.imports_dir).save("code-test", reference_xml["CoC EK Assa"], fetched=False)
    return AppState(settings, "token", JobStore(), lambda: session)


def run(state: AppState, body: dict[str, object]) -> object:
    job, _ = state.jobs.start("compare", str(body.get("build")))
    run_compare(state, job.id, compare_request(body))
    return state.jobs.get(job.id)


def test_a_comparison_job_ends_with_the_report(
    tmp_path: Path, pob_session: PobSession, reference_xml: dict[str, str]
) -> None:
    state = state_for(tmp_path, pob_session, reference_xml)
    job = run(state, {"build": "3.29/Worb.xml", "targetImport": "code-test"})
    assert job is not None and job.status is JobStatus.DONE and job.report is not None  # type: ignore[attr-defined]
    assert job.report["yours"]["skill"] == "Winter Orb"  # type: ignore[attr-defined]
    assert job.report["settings"]["match"] == "different_skill"  # type: ignore[attr-defined]


def test_a_refused_input_ends_the_job_with_its_kind(
    tmp_path: Path, pob_session: PobSession, reference_xml: dict[str, str]
) -> None:
    state = state_for(tmp_path, pob_session, reference_xml)
    outside = run(state, {"build": "../secret.xml", "targetImport": "code-test"})
    gone = run(state, {"build": "3.29/Worb.xml", "targetImport": "pobb-gone"})
    assert (outside.status, outside.error.kind) == (JobStatus.ERROR, "InvalidInput")  # type: ignore[attr-defined]
    assert "no longer there" in gone.error.message  # type: ignore[attr-defined]
