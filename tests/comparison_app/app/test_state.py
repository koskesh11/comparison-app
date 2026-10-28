"""The app state (app/state.py): one PoB session, opened on first use, closed once."""

from pathlib import Path

from comparison_app.app.jobs import JobStore
from comparison_app.app.settings import ENV_BUILDS_DIR, ENV_HOME, Settings
from comparison_app.app.state import AppState


class Session:
    closed = 0

    def close(self) -> None:
        Session.closed += 1


def test_the_session_opens_once_and_closes(tmp_path: Path) -> None:
    opened: list[Session] = []

    def make_session() -> Session:
        opened.append(Session())
        return opened[-1]

    settings = Settings.from_environment({ENV_HOME: str(tmp_path), ENV_BUILDS_DIR: str(tmp_path)})
    state = AppState(settings, "token", JobStore(), make_session)  # type: ignore[arg-type]
    assert state.session() is state.session() is opened[0]
    state.close()
    state.close()
    assert (len(opened), Session.closed) == (1, 1)
