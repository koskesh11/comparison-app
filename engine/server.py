"""Local GUI server: python server.py, then open http://127.0.0.1:8765

Only listens on localhost. Builds are read from the PoB Builds folder only.
"""

import json
import sys
import threading
import traceback
import uuid
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import build_settings
from audit import DEFAULT_SCENARIO, Auditor
from vault import load_scenarios
from optimize import DEFAULT_OUT_DIR, ChangeError, StaleAudit, apply_changes

HOST, PORT = "127.0.0.1", 8765
BUILDS_DIR = (Path.home() / "Documents" / "Path of Building" / "Builds").resolve()
GUI_FILE = Path(__file__).resolve().parent.parent / "gui" / "index.html"
MAX_BODY_BYTES = 64 * 1024

engine_lock = threading.Lock()  # one PoB calculation at a time
jobs: dict[str, dict] = {}


def list_builds() -> list[dict]:
    builds = []
    for path in BUILDS_DIR.rglob("*.xml"):
        rel = path.relative_to(BUILDS_DIR)
        builds.append({"path": rel.as_posix(), "name": path.stem,
                       "folder": rel.parent.as_posix() if rel.parent != Path(".") else "",
                       "mtime": path.stat().st_mtime})
    return sorted(builds, key=lambda b: b["mtime"], reverse=True)


def resolve_build(rel_path: str) -> Path:
    path = (BUILDS_DIR / rel_path).resolve()
    if BUILDS_DIR not in path.parents or path.suffix.lower() != ".xml" or not path.is_file():
        raise ValueError("build must be an .xml file inside the PoB Builds folder")
    return path


def run_audit(job_id: str, build_path: Path, include_drafts: bool, leave_out: list[str], scenario: str) -> None:
    job = jobs[job_id]

    def progress(label: str) -> None:
        job["progress"] = label

    try:
        with engine_lock:
            auditor = Auditor(build_path, include_drafts, progress, disabled_skills=leave_out, scenario=scenario)
            job["report"] = auditor.run()
            job["auditor"] = auditor
        job["status"] = "done"
    except Exception as error:  # surfaced to the GUI; full trace in the console
        traceback.print_exc()
        job.update(status="error", error=f"{type(error).__name__}: {error}")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # keep the console quiet
        pass

    def send_json(self, payload, status=HTTPStatus.OK):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY_BYTES:
            raise ValueError("request too large")
        data = json.loads(self.rfile.read(length) or b"{}")
        if not isinstance(data, dict):
            raise ValueError("expected a JSON object")
        return data

    def public_job(self, job: dict) -> dict:
        return {k: v for k, v in job.items() if k != "auditor"}

    def do_GET(self):
        if self.path == "/":
            body = GUI_FILE.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/builds":
            self.send_json({"builds": list_builds(), "outDir": str(DEFAULT_OUT_DIR),
                            "scenarios": sorted(load_scenarios()), "defaultScenario": DEFAULT_SCENARIO,
                            "settings": build_settings._load_all()})
        elif self.path.startswith("/api/jobs/"):
            job = jobs.get(self.path.removeprefix("/api/jobs/"))
            self.send_json(self.public_job(job) if job else {"error": "unknown job"},
                           HTTPStatus.OK if job else HTTPStatus.NOT_FOUND)
        else:
            self.send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self):
        try:
            data = self.read_json()
            if self.path == "/api/audit":
                build_path = resolve_build(str(data.get("build", "")))
                leave_out = [str(n).strip() for n in data.get("leaveOut", []) if str(n).strip()]
                scenario = str(data.get("scenario") or DEFAULT_SCENARIO)
                if scenario not in load_scenarios():
                    raise ValueError(f"unknown scenario {scenario!r}")
                build_settings.update(data["build"], leaveOut=leave_out, scenario=scenario)
                job_id = uuid.uuid4().hex
                jobs[job_id] = {"id": job_id, "status": "running", "progress": "Queued", "build": data["build"]}
                threading.Thread(target=run_audit, args=(job_id, build_path, bool(data.get("includeDrafts")), leave_out, scenario),
                                 daemon=True).start()
                self.send_json({"jobId": job_id})
            elif self.path.startswith("/api/jobs/") and self.path.endswith("/apply"):
                job = jobs.get(self.path.removeprefix("/api/jobs/").removesuffix("/apply"))
                if not job or job.get("status") != "done":
                    raise ValueError("audit not finished")
                ids = [int(i) for i in data.get("ids", [])]
                with engine_lock:
                    outcome = apply_changes(job["auditor"], ids, force=bool(data.get("force")))
                if outcome["saved"]:
                    # the optimized build keeps the source build's settings (left-out skills, scenario)
                    saved_rel = Path(outcome["path"]).resolve().relative_to(BUILDS_DIR).as_posix()
                    build_settings.update(saved_rel, **build_settings.get(job["build"]))
                self.send_json(outcome)
            else:
                self.send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
        except StaleAudit as error:
            self.send_json({"error": str(error), "kind": "StaleAudit"}, HTTPStatus.CONFLICT)
        except (ValueError, ChangeError, KeyError) as error:
            self.send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
        except Exception as error:
            traceback.print_exc()
            self.send_json({"error": f"{type(error).__name__}: {error}"}, HTTPStatus.INTERNAL_SERVER_ERROR)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}"
    print(f"PoB Autobuilder running at {url}  (Ctrl+C to stop)")
    if "--no-browser" not in sys.argv:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
