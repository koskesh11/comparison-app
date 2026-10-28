"""The local HTTP server (the first app's engine/server.py, rewritten around AppState; interfaces.md 4.6).

Routes: GET / (the page, with the API token in it), GET /api/meta (stage ids, scenarios), GET /api/builds (your
builds), POST /api/compare (starts a job), GET /api/jobs/<id> (its progress and report). Every request passes
app/security.check_request first; every error is answered through app/errors.reply_for. The job runs on its own
thread; `run` is the runner (app/runner.run_compare), passed in so tests can give their own.
"""

import json
import logging
import threading
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from comparison_app.analysis.scenarios import DEFAULT, Scenario
from comparison_app.app.errors import reply_for
from comparison_app.app.inputs import CompareRequest, compare_request
from comparison_app.app.jobs import Job, Stage
from comparison_app.app.runner import run_compare
from comparison_app.app.security import COMMON_HEADERS, Refused, body_limit, check_request
from comparison_app.app.state import AppState
from comparison_app.errors import InvalidInput
from comparison_app.intake.library import Library

logger = logging.getLogger(__name__)
TOKEN_SLOT = "{{API_TOKEN}}"  # noqa: S105 - where web/index.html takes the token (card 113), not a secret
PLACEHOLDER_PAGE = "<!doctype html><title>Comparison app</title><p>The page comes with card 113.</p>"
Runner = Callable[[AppState, str, CompareRequest], None]


class AppServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], state: AppState, run: Runner = run_compare) -> None:
        super().__init__(address, Handler)
        self.state, self.run = state, run


def job_json(job: Job) -> dict[str, Any]:
    error = job.error and {"kind": job.error.kind, "message": job.error.message, "referenceId": job.error.reference_id}
    return {
        "id": job.id,
        "status": job.status.value,
        "stage": job.stage.value,
        "done": job.done,
        "total": job.total,
        "build": job.build,
        "error": error,
        "report": job.report,
    }


class Handler(BaseHTTPRequestHandler):
    server: AppServer

    def log_message(self, format: str, *args: Any) -> None:
        logger.debug(format, *args)

    def do_GET(self) -> None:
        self._answer(self._get)

    def do_POST(self) -> None:
        self._answer(self._post)

    def _answer(self, route: Callable[[], tuple[int, str, bytes]]) -> None:
        try:
            check_request(
                dict(self.headers),
                port=self.server.state.settings.port,
                token=self.server.state.token,
                api=self.path.startswith("/api/"),
            )
            status, kind, body = route()
        except Exception as error:  # every failure is answered with its reply; refusals and bugs are logged
            reply = reply_for(error)
            if isinstance(error, Refused):
                logger.warning("request refused: %s", error.reason, extra={"event": "auth_refused"})
            elif reply.reference_id is not None:
                logger.exception("request failed, reference %s", reply.reference_id, extra={"event": "error"})
            payload = {"error": {"kind": reply.kind, "message": reply.message, "referenceId": reply.reference_id}}
            status, kind, body = reply.status, "application/json", json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        for name, value in COMMON_HEADERS:
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, payload: object) -> tuple[int, str, bytes]:
        return 200, "application/json", json.dumps(payload).encode("utf-8")

    def _get(self) -> tuple[int, str, bytes]:
        state = self.server.state
        if self.path == "/":
            page = state.settings.web_dir / "index.html"
            text = page.read_text(encoding="utf-8") if page.is_file() else PLACEHOLDER_PAGE
            return 200, "text/html; charset=utf-8", text.replace(TOKEN_SLOT, state.token).encode("utf-8")
        if self.path == "/api/meta":
            return self._json(
                {
                    "stages": [stage.value for stage in Stage],
                    "scenarios": [s.value for s in Scenario],
                    "defaultScenario": DEFAULT.value,
                }
            )
        if self.path == "/api/builds":
            builds = Library(state.settings.builds_dir).builds()
            return self._json(
                [{"path": b.path, "name": b.name, "folder": b.folder, "modified": b.modified} for b in builds]
            )
        if self.path.startswith("/api/jobs/"):
            job = state.jobs.get(self.path.removeprefix("/api/jobs/"))
            if job is None:
                raise InvalidInput("No such job; start the comparison again.")
            return self._json(job_json(job))
        raise InvalidInput(f"No page {self.path}.")

    def _post(self) -> tuple[int, str, bytes]:
        if self.path != "/api/compare":
            raise InvalidInput(f"No page {self.path}.")
        request = compare_request(self._body(body_limit(carries_code=True)))
        state = self.server.state
        job, created = state.jobs.start("compare", request.build)
        if created:
            threading.Thread(target=self.server.run, args=(state, job.id, request), daemon=True).start()
        return self._json({"job": job.id, "created": created})

    def _body(self, limit: int) -> dict[str, object]:
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError as error:
            raise InvalidInput("The request has no readable length.") from error
        if length < 0 or length > limit:
            raise InvalidInput("The request is too large.")
        try:
            data = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError as error:
            raise InvalidInput("The request is not JSON.") from error
        if not isinstance(data, dict):
            raise InvalidInput("The request must be a JSON object.")
        return data
