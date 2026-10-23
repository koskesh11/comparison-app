"""HTTP-independent guide-check route handlers and job lifecycle."""

from __future__ import annotations

import importlib.util
import threading
import time
import uuid
from pathlib import Path

import build_settings
import guide_apply
import guide_lua
import optimize
import pobbin
import runlog
from api_errors import ApiError, InvalidRequest, StaleAudit, Unavailable
from audit import DEFAULT_SCENARIO
from vault import load_scenarios

GUIDE_POST_PATHS = {"/api/guide-check", "/api/guide-preview", "/api/guide-apply"}
_START_LOCK = threading.Lock()
MAX_JOB_AGE_S = 15 * 60  # a running guide job older than this is given up, so one stuck job cannot block all checks


class JobProgress:
    def __init__(self, job: dict):
        self.job = job

    def __call__(self, label: str) -> None:
        stages = self.job.setdefault("stages", [])
        if label not in stages:
            stages.append(label)
        self.job.update(stage=label, progress=label)
        if label != "Testing differences":
            self.job.update(done=None, total=None)

    def testing(self, done, total) -> None:
        self.job.update(done=int(done), total=int(total))


def load_run_check():
    try:
        from guide_check import run_check
    except ModuleNotFoundError as error:
        if error.name != "guide_check":
            raise
        raise Unavailable("Guide check is not installed in this build.") from error
    return run_check


def capability_from_probe(probe, check_available) -> dict:
    version = probe.get("pobVersion")
    fields = ("compareTab", "comparePowerBuilder", "compareEntry")
    engine_ready = all(probe.get(field) is True for field in fields)
    if not engine_ready:
        shown = str(version).split("-", 1)[0] if version else "unknown"
        reason = f"Guide check needs Path of Building 2.64 or newer; yours is {shown}."
    elif not check_available:
        reason = "Guide check is not installed in this build."
    else:
        reason = None
    return {"available": reason is None, "pobVersion": version, "reason": reason}


def probe_capability(state) -> dict:
    try:
        with state.engine_lock, state.pool.lease() as engine:
            probe = guide_lua.probe(engine)
        found = importlib.util.find_spec("guide_check") is not None
        result = capability_from_probe(probe, found)
    except Exception as error:
        runlog.log_event("ERROR", "error", "guide capability probe failed", exc=error)
        result = {"available": False, "pobVersion": None,
                  "reason": "Guide check could not start. See the log."}
    state.guide_capability = result
    return result


def capability(state) -> dict:
    return state.guide_capability or {
        "available": False, "pobVersion": None, "reason": "Guide check is not ready."}


def handle_post(state, path, data) -> dict:
    routes = {"/api/guide-check": start_check, "/api/guide-preview": preview,
              "/api/guide-apply": apply}
    handler = routes.get(path)
    if handler is None:
        raise InvalidRequest("unknown guide route")
    return handler(state, data)


def _link(value) -> tuple[str, str]:
    if not isinstance(value, str):
        raise InvalidRequest(pobbin.MSG_BAD_LINK)
    return value, pobbin.parse_link(value)


def _request_spec(state, data: dict) -> tuple[dict, dict, str]:
    player, guide = data.get("player"), data.get("guide")
    if not isinstance(player, dict) or set(player) & {"build", "link"} not in ({"build"}, {"link"}):
        raise InvalidRequest("player must contain exactly one of build or link")
    if not isinstance(guide, dict) or "link" not in guide:
        raise InvalidRequest("guide must contain a link")
    guide_link, _ = _link(guide.get("link"))
    if "build" in player:
        if not isinstance(player["build"], str):
            raise InvalidRequest("build must be a string")
        path = state.resolve_build(player["build"])
        return {"playerPath": path, "guideLink": guide_link}, build_settings.get(player["build"]), player["build"]
    player_link, player_id = _link(player.get("link"))
    return {"playerLink": player_link, "guideLink": guide_link}, {}, f"pobb.in/{player_id}"


def _settings(data: dict, saved: dict, build: str, local_build: bool) -> dict:
    leave_out = data.get("leaveOut", saved.get("leaveOut", []))
    if not isinstance(leave_out, list) or any(not isinstance(name, str) for name in leave_out):
        raise InvalidRequest("leaveOut must be a list of strings")
    scenario = data.get("scenario", saved.get("scenario", DEFAULT_SCENARIO))
    if not isinstance(scenario, str) or scenario not in load_scenarios():
        raise InvalidRequest(f"unknown scenario {scenario!r}")
    include = _strict_bool(data, "includeDrafts")
    if ("scenario" in data or "leaveOut" in data) and local_build:
        build_settings.update(build, leaveOut=leave_out, scenario=scenario)
    return {"includeDrafts": include, "leaveOut": leave_out, "scenario": scenario}


def start_check(state, data) -> dict:
    if not isinstance(data, dict):
        raise InvalidRequest("expected a JSON object")
    spec, saved, build = _request_spec(state, data)
    settings = _settings(data, saved, build, "playerPath" in spec)
    spec.update(settings=settings, build=build)
    with _START_LOCK:
        _expire_stuck_jobs(state)
        running = next((job for job in state.jobs.values()
                        if job.get("kind") == "guide" and job.get("status") == "running"), None)
        if running:
            return {"jobId": running["id"], "running": True}
        job_id = uuid.uuid4().hex
        state.jobs[job_id] = _new_job(job_id, build, settings)
        runlog.log_event("INFO", "job_start", "guide check started", job_id, build)
        threading.Thread(target=run_guide_job, args=(state, job_id, spec), daemon=True).start()
    return {"jobId": job_id, "running": False}


def _expire_stuck_jobs(state, clock=time.monotonic) -> None:
    for job in state.jobs.values():
        if job.get("kind") == "guide" and job.get("status") == "running"                 and clock() - job.get("started", clock()) > MAX_JOB_AGE_S:
            job.update(status="error", error="The check took too long and was given up. Try again.",
                       errorKind="Timeout", report=None)
            runlog.log_event("ERROR", "error", "guide check expired", job.get("id"), job.get("build"))


def _new_job(job_id: str, build: str, settings: dict) -> dict:
    return {"id": job_id, "kind": "guide", "status": "running", "progress": "Queued", "started": time.monotonic(),
            "stage": "Queued", "stages": [], "done": None, "total": None, "build": build,
            "error": None, "errorKind": None, "referenceId": None, "report": None,
            "sha": None, "playerPath": None, "settings": settings, "obtainable": None}


def _run_with_engine(state, spec: dict, guide: dict, progress: JobProgress):
    player_path = Path(spec["playerPath"])
    progress("Loading both builds in Path of Building")
    run_check = load_run_check()
    settings = spec["settings"]
    with state.engine_lock, state.pool.lease() as engine:
        auditor = state.Auditor(player_path, settings["includeDrafts"], lambda _: None,
                                disabled_skills=settings["leaveOut"], scenario=settings["scenario"],
                                engine=engine)
        result = run_check(auditor, guide["path"], f"pobb.in/{guide['id']}", progress)
        saved = result, auditor.source_sha256, auditor.obtainable
        del auditor
    return player_path, saved


def run_guide_job(state, job_id, spec) -> None:
    job, progress = state.jobs[job_id], JobProgress(state.jobs[job_id])
    try:
        progress("Fetching the guide from pobb.in")
        guide = pobbin.import_link(spec["guideLink"], state.DEFAULT_OUT_DIR)
        if "playerLink" in spec:
            progress("Fetching your build from pobb.in")
            player = pobbin.import_link(spec["playerLink"], state.DEFAULT_OUT_DIR)
            spec = {**spec, "playerPath": Path(player["path"])}
        player_path, (result, sha, obtainable) = _run_with_engine(state, spec, guide, progress)
        job.update(status="done", report=result, sha=sha, playerPath=player_path,
                   obtainable=obtainable, progress="Done", stage="Done")
        runlog.log_event("INFO", "job_done", "guide check completed", job_id, job["build"])
    except Exception as error:
        _guide_error(job, job_id, error)


def _guide_error(job: dict, job_id: str, error: Exception) -> None:
    if isinstance(error, ApiError):
        imported = (pobbin.BadLink, pobbin.Unreadable, pobbin.TooLarge, pobbin.FetchFailed)
        kind = type(error).__name__ if isinstance(error, imported) else error.kind
        job.update(status="error", error=str(error), errorKind=kind, report=None)
        runlog.log_event("ERROR", "error", str(error), job_id, job["build"])
        return
    job.update(status="error", error="The check failed. Reference ID is in the log.",
               errorKind="EngineError", referenceId=job_id, report=None)
    message = f"guide check failed ({type(error).__name__})"
    runlog.log_event("ERROR", "error", message, job_id, job["build"], error)


def _finished_job(state, data: dict) -> tuple[dict, list[dict]]:
    job = state.jobs.get(str(data.get("jobId", "")))
    if not job or job.get("kind") != "guide" or job.get("status") == "error":
        raise InvalidRequest("That check is no longer available; run it again.")
    if job.get("status") == "running":
        raise InvalidRequest("The check is still running.")
    ids = data.get("ids")
    if not isinstance(ids, list):
        raise InvalidRequest("ids must be a list")
    return job, guide_apply.resolve_ticks(job["report"], ids)


def _fresh(job: dict) -> None:
    try:
        optimize.check_source_fresh(job["playerPath"], job["sha"])
    except optimize.StaleAudit as error:
        raise StaleAudit("Your build changed since the check; run it again.") from error


def _auditor(state, job: dict, engine):
    settings = job["settings"]
    return state.Auditor(job["playerPath"], settings["includeDrafts"],
                         disabled_skills=settings["leaveOut"], scenario=settings["scenario"],
                         engine=engine, obtainable=job["obtainable"])


def preview(state, data) -> dict:
    job, rows = _finished_job(state, data)
    _fresh(job)
    with state.engine_lock, state.pool.lease() as engine:
        auditor = _auditor(state, job, engine)
        result = guide_apply.predict(auditor, rows)
        del auditor
    return result


def _carry_settings(state, job: dict, result: dict) -> None:
    if not result.get("saved") or not result.get("path"):
        return
    try:
        rel = Path(result["path"]).resolve().relative_to(Path(state.BUILDS_DIR).resolve()).as_posix()
    except ValueError:
        return
    settings = job["settings"]
    build_settings.update(rel, leaveOut=settings["leaveOut"], scenario=settings["scenario"])


def _strict_bool(data: dict, name: str) -> bool:
    value = data.get(name, False)
    if not isinstance(value, bool):
        raise InvalidRequest(f"{name} must be a boolean")
    return value


def apply(state, data) -> dict:
    job, rows = _finished_job(state, data)
    _fresh(job)
    with state.engine_lock, state.pool.lease() as engine:
        auditor = _auditor(state, job, engine)
        result = guide_apply.save(auditor, rows, state.DEFAULT_OUT_DIR,
                                  force=_strict_bool(data, "force"))
        del auditor
    ids = [row["id"] for row in rows]
    result.update(applied={"count": len(rows), "ids": ids,
                           "labels": [row["label"] for row in rows]},
                  notApplied=guide_apply.not_applied(job["report"], ids))
    _carry_settings(state, job, result)
    message = f"guide apply saved={result.get('saved')} path={result.get('path')}"
    runlog.log_event("INFO", "apply", message, str(data.get("jobId", "")), job["build"])
    return result
