"""What every handler receives, built once in app/main.py; nothing else holds global state (interfaces.md 4.6).

One PoB session serves the app, opened on the first comparison; one job runs at a time (app/jobs.py), and the lock
keeps the session to one caller. Tests build a state with their own session.
"""

import threading
from collections.abc import Callable
from dataclasses import dataclass, field

from comparison_app.app.jobs import JobStore
from comparison_app.app.settings import Settings
from comparison_app.pob.session import PobSession


@dataclass
class AppState:
    settings: Settings
    token: str
    jobs: JobStore
    open_session: Callable[[], PobSession]
    lock: threading.Lock = field(default_factory=threading.Lock)
    _session: PobSession | None = None

    def session(self) -> PobSession:
        """The app's PoB session; call it while holding `lock`."""
        if self._session is None:
            self._session = self.open_session()
        return self._session

    def close(self) -> None:
        with self.lock:
            if self._session is not None:
                self._session.close()
                self._session = None
