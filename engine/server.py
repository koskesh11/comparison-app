"""Local GUI server: python server.py, then open http://127.0.0.1:8765."""

import hmac
import json
import secrets
import sys
import threading
import uuid
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import build_settings
import runlog
from api_errors import ApiError, Forbidden, InvalidRequest, Unauthorized, classify
from audit import DEFAULT_SCENARIO, Auditor
from engine_pool import EnginePool
from optimize import DEFAULT_OUT_DIR, apply_changes, check_source_fresh
from pobhost import LuaError
from vault import load_scenarios

HOST, PORT = "127.0.0.1", 8765
BUILDS_DIR = (Path.home() / "Documents" / "Path of Building" / "Builds").resolve()
GUI_FILE = Path(__file__).resolve().parent.parent / "gui" / "index.html"
TOKEN_FILE = Path(__file__).resolve().parent / "userdata" / "api-token"
MAX_BODY_BYTES = 64 * 1024
VALID_HOSTS = {f"127.0.0.1:{PORT}", f"localhost:{PORT}"}
VALID_ORIGINS = {f"http://127.0.0.1:{PORT}", f"http://localhost:{PORT}"}
PUBLIC_JOB_KEYS = ("id", "status", "progress", "build", "error", "report")

API_TOKEN = ""
pool = None
engine_lock = threading.Lock()
jobs: dict[str, dict] = {}


def list_builds() -> list[dict]:
    builds = []
    for path in BUILDS_DIR.rglob("*.xml"):
        rel = path.relative_to(BUILDS_DIR)
        builds.append({"path": rel.as_posix(), "name": path.stem,
                       "folder": rel.parent.as_posix() if rel.parent != Path(".") else "",
                       "mtime": path.stat().st_mtime})
    return sorted(builds, key=lambda build: build["mtime"], reverse=True)


def resolve_build(rel_path: str) -> Path:
    path = (BUILDS_DIR / rel_path).resolve()
    if BUILDS_DIR not in path.parents or path.suffix.lower() != ".xml" or not path.is_file():
        raise InvalidRequest("build must be an .xml file inside the PoB Builds folder")
    return path


def run_audit(job_id: str, build_path: Path, include_drafts: bool,
              leave_out: list[str], scenario: str) -> None:
    job = jobs[job_id]

    def progress(label: str) -> None:
        job["progress"] = label

    runlog.log_event("INFO", "job_start", "audit started", job_id, job["build"])
    try:
        with engine_lock, pool.lease() as engine:
            auditor = Auditor(build_path, include_drafts, progress, disabled_skills=leave_out,
                              scenario=scenario, engine=engine)
            report = auditor.run()
            source_sha256 = auditor.source_sha256
            del auditor
        job.update(status="done", report=report, sha=source_sha256)
        runlog.log_event("INFO", "job_done", "audit completed", job_id, job["build"])
    except Exception as error:
        _, body = classify(error)
        job.update(status="error", error=f"{body['kind']}: {body['error']}")
        runlog.log_event("ERROR", "error", body["error"], job_id, job["build"], error)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def send_json(self, payload: dict, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, error: Exception) -> None:
        status, body = classify(error)
        job_id, build = self._request_context()
        detail = None if isinstance(error, ApiError) else error
        runlog.log_event("ERROR", "error", body["error"], job_id, build, detail)
        self.send_json(body, status)

    def guard(self, is_api: bool) -> None:
        host = self.headers.get("Host")
        if host not in VALID_HOSTS:
            self._refuse("bad_host", Forbidden("forbidden host"))
        origin = self.headers.get("Origin")
        if origin is not None and origin not in VALID_ORIGINS:
            self._refuse("bad_origin", Forbidden("forbidden origin"))
        if is_api:
            self._guard_token()

    def _guard_token(self) -> None:
        supplied = self.headers.get("X-Api-Token") or ""
        if not supplied:
            self._refuse("missing_token", Unauthorized("unauthorized"))
        matches = bool(API_TOKEN) and hmac.compare_digest(
            supplied.encode("utf-8"), API_TOKEN.encode("utf-8"))
        if not matches:
            self._refuse("bad_token", Unauthorized("unauthorized"))

    @staticmethod
    def _refuse(reason: str, error: ApiError) -> None:
        runlog.log_event("WARNING", "auth_refused", reason)
        raise error

    def read_json(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length") or 0)
            if length < 0 or length > MAX_BODY_BYTES:
                raise ValueError("request too large")
            data = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, json.JSONDecodeError) as error:
            raise InvalidRequest(str(error)) from error
        if not isinstance(data, dict):
            raise InvalidRequest("expected a JSON object")
        return data

    @staticmethod
    def public_job(job: dict) -> dict:
        return {key: job.get(key) for key in PUBLIC_JOB_KEYS}

    def do_GET(self) -> None:
        try:
            self.guard(self.path.startswith("/api/"))
            self._get_route()
        except Exception as error:
            self.send_error_json(error)

    def _get_route(self) -> None:
        if self.path == "/":
            self._serve_gui()
        elif self.path == "/api/builds":
            self.send_json({"builds": list_builds(), "outDir": str(DEFAULT_OUT_DIR),
                            "scenarios": sorted(load_scenarios()), "defaultScenario": DEFAULT_SCENARIO,
                            "settings": build_settings._load_all()})
        elif self.path.startswith("/api/jobs/"):
            job = jobs.get(self.path.removeprefix("/api/jobs/"))
            if job:
                self.send_json(self.public_job(job))
            else:
                self._not_found("unknown job")
        else:
            self._not_found("not found")

    def _serve_gui(self) -> None:
        text = GUI_FILE.read_text(encoding="utf-8").replace("__API_TOKEN__", API_TOKEN)
        body = text.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        try:
            self.guard(self.path.startswith("/api/"))
            self._post_route()
        except Exception as error:
            self.send_error_json(error)

    def _post_route(self) -> None:
        if self.path == "/api/audit":
            self._start_audit(self.read_json())
        elif self.path.startswith("/api/jobs/") and self.path.endswith("/apply"):
            self._apply(self.read_json())
        else:
            self._not_found("not found")

    def _start_audit(self, data: dict) -> None:
        build = str(data.get("build", ""))
        build_path = resolve_build(build)
        leave_out = [str(name).strip() for name in data.get("leaveOut", []) if str(name).strip()]
        scenario = str(data.get("scenario") or DEFAULT_SCENARIO)
        if scenario not in load_scenarios():
            raise InvalidRequest(f"unknown scenario {scenario!r}")
        build_settings.update(build, leaveOut=leave_out, scenario=scenario)
        job_id = uuid.uuid4().hex
        settings = {"includeDrafts": bool(data.get("includeDrafts")),
                    "leaveOut": leave_out, "scenario": scenario}
        jobs[job_id] = {"id": job_id, "status": "running", "progress": "Queued", "build": build,
                        "error": None, "report": None, "sha": None, "settings": settings}
        threading.Thread(target=run_audit, args=(job_id, build_path, settings["includeDrafts"],
                                                leave_out, scenario), daemon=True).start()
        self.send_json({"jobId": job_id})

    def _apply(self, data: dict) -> None:
        job_id = self.path.removeprefix("/api/jobs/").removesuffix("/apply")
        job = jobs.get(job_id)
        if not job or job.get("status") != "done":
            raise InvalidRequest("audit not finished")
        ids = self._parse_ids(data.get("ids", []))
        build_path = resolve_build(job["build"])
        check_source_fresh(build_path, job["sha"])
        outcome = self._apply_with_engine(job, build_path, ids, bool(data.get("force")))
        if outcome["saved"]:
            saved_rel = Path(outcome["path"]).resolve().relative_to(BUILDS_DIR).as_posix()
            build_settings.update(saved_rel, **build_settings.get(job["build"]))
        message = f"apply saved={bool(outcome['saved'])} path={outcome.get('path')}"
        runlog.log_event("INFO", "apply", message, job_id, job["build"])
        self.send_json(outcome)

    @staticmethod
    def _parse_ids(value) -> list[int]:
        if not isinstance(value, list):
            raise InvalidRequest("ids must be a list of integers")
        try:
            return [int(item) for item in value]
        except (TypeError, ValueError) as error:
            raise InvalidRequest("ids must be a list of integers") from error

    @staticmethod
    def _apply_with_engine(job: dict, build_path: Path, ids: list[int], force: bool) -> dict:
        settings = job["settings"]
        with engine_lock, pool.lease() as engine:
            auditor = Auditor(build_path, settings["includeDrafts"], disabled_skills=settings["leaveOut"],
                              scenario=settings["scenario"], engine=engine)
            auditor.suggestions = job["report"]["suggestions"]
            auditor.source_sha256 = job["sha"]
            return apply_changes(auditor, ids, force=force)

    def _not_found(self, message: str) -> None:
        job_id, build = self._request_context()
        runlog.log_event("ERROR", "error", message, job_id, build)
        self.send_json({"error": message, "kind": "NotFound"}, HTTPStatus.NOT_FOUND)

    def _request_context(self) -> tuple[str | None, str | None]:
        if not self.path.startswith("/api/jobs/"):
            return None, None
        job_id = self.path.removeprefix("/api/jobs/").removesuffix("/apply")
        job = jobs.get(job_id)
        return job_id, job.get("build") if job else None


def main() -> None:
    global API_TOKEN, pool
    API_TOKEN = secrets.token_urlsafe(32)
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(API_TOKEN, encoding="utf-8")
    runlog.setup(token=API_TOKEN)
    pool = EnginePool()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}"
    print(f"PoB Autobuilder running at {url}  (Ctrl+C to stop)")
    if "--no-browser" not in sys.argv:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        pool.close()


if __name__ == "__main__":
    main()
