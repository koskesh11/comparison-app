"""Starts the app: settings checked, a fresh API token (also in userdata/api-token, as the first app kept it), the run
log, one PoB session opened on the first comparison, the server on 127.0.0.1:8765 and the page in the browser."""

import webbrowser

from comparison_app.app.jobs import JobStore
from comparison_app.app.logging_setup import setup
from comparison_app.app.security import new_token
from comparison_app.app.server import AppServer
from comparison_app.app.settings import Settings
from comparison_app.app.state import AppState
from comparison_app.pob.session import start_session


def prepare(settings: Settings) -> AppState:
    """The checked settings as a ready state: token written, log set up; PoB is not started yet."""
    settings.validate()
    token = new_token()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "api-token").write_text(token, encoding="utf-8")
    setup(settings.data_dir, token)
    jobs = JobStore(keep=settings.job_keep, run_limit_s=settings.job_run_limit_s)
    return AppState(settings, token, jobs, lambda: start_session(settings.pob_paths()))


def main() -> None:
    state = prepare(Settings.from_environment())
    server = AppServer((state.settings.host, state.settings.port), state)
    webbrowser.open(f"http://{state.settings.host}:{state.settings.port}/")
    try:
        server.serve_forever()
    finally:
        server.server_close()
        state.close()
