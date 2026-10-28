"""The local server (app/server.py) over real HTTP on a free port, with a stand-in runner: the guard on every request,
the page with its token, your builds, a job from start to report, errors as JSON with their kind."""

import json
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest

from comparison_app.app.inputs import CompareRequest
from comparison_app.app.jobs import JobStore
from comparison_app.app.server import AppServer
from comparison_app.app.settings import ENV_BUILDS_DIR, ENV_HOME, Settings
from comparison_app.app.state import AppState

TOKEN = "test-token"  # noqa: S105 - a made-up token for the test server


def finish(state: AppState, job_id: str, request: CompareRequest) -> None:
    state.jobs.finish(job_id, {"build": request.build})


@pytest.fixture
def server(tmp_path: Path) -> Iterator[AppServer]:
    builds = tmp_path / "Builds"
    builds.mkdir()
    (builds / "Worb.xml").write_text("<PathOfBuilding><Build/></PathOfBuilding>", encoding="utf-8")
    settings = Settings.from_environment({ENV_HOME: str(tmp_path), ENV_BUILDS_DIR: str(builds)})
    state = AppState(settings, TOKEN, JobStore(), lambda: pytest.fail("no PoB in these tests"))
    app = AppServer(("127.0.0.1", 0), state, finish)
    state.settings = replace(settings, port=app.server_address[1])
    thread = __import__("threading").Thread(target=app.serve_forever, daemon=True)
    thread.start()
    yield app
    app.shutdown()
    app.server_close()


def call(app: AppServer, path: str, body: object = None, headers: dict[str, str] | None = None) -> tuple[int, Any]:
    port = app.server_address[1]
    sent = {"Host": f"127.0.0.1:{port}", "X-Api-Token": TOKEN, **(headers or {})}
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data, headers=sent)
    try:
        with urllib.request.urlopen(request, timeout=10) as answer:  # noqa: S310 - the test's own local server
            raw, status, kind = answer.read(), answer.status, answer.headers["Content-Type"]
    except urllib.error.HTTPError as error:
        raw, status, kind = error.read(), error.code, error.headers["Content-Type"]
    return status, json.loads(raw) if kind == "application/json" else raw.decode("utf-8")


def test_the_page_carries_no_token_slot_and_the_guard_holds(server: AppServer) -> None:
    status, page = call(server, "/")
    assert status == 200 and "{{API_TOKEN}}" not in page
    assert call(server, "/api/builds", headers={"X-Api-Token": "guess"})[0] == 401
    assert call(server, "/", headers={"Host": "evil.example"})[0] == 403


def test_your_builds_and_the_meta_are_listed(server: AppServer) -> None:
    assert [build["path"] for build in call(server, "/api/builds")[1]] == ["Worb.xml"]
    assert call(server, "/api/meta")[1]["defaultScenario"] == "pinnacle_boss"


def test_a_job_runs_from_start_to_report(server: AppServer) -> None:
    status, started = call(server, "/api/compare", {"build": "Worb.xml", "targetImport": "pobb-x"})
    assert status == 200 and started["created"] is True
    for _ in range(50):
        job = call(server, f"/api/jobs/{started['job']}")[1]
        if job["status"] != "running":
            break
        time.sleep(0.05)
    assert (job["status"], job["report"]) == ("done", {"build": "Worb.xml"})


def test_errors_are_json_with_their_kind(server: AppServer) -> None:
    status, answer = call(server, "/api/compare", {"build": "Worb.xml"})
    assert (status, answer["error"]["kind"]) == (400, "InvalidInput")
    assert call(server, "/api/jobs/nothing")[1]["error"]["message"].startswith("No such job")
