"""A pool of PoB sessions, leased one job at a time (the first app's engine/engine_pool.py, kept as it was).

Milestone 1 uses size 1: one session holds your build and the target (task 102, area A Q7). A lease whose body raises
closes that session and makes a new one, so a session left in an unknown state is never lent again.
"""

import contextlib
import logging
import queue
import threading
from collections.abc import Callable, Iterator
from typing import Protocol

LOG = logging.getLogger(__name__)
POLL_SECONDS = 0.05


class Closeable(Protocol):
    def close(self) -> None: ...


class SessionPool[T: Closeable]:
    def __init__(self, size: int, factory: Callable[[int], T]) -> None:
        if size < 1:
            raise ValueError("pool size must be positive")
        self.size = size
        self._factory = factory
        self._queue: queue.Queue[tuple[int, T | None]] = queue.Queue(maxsize=size)
        self._lock = threading.Lock()
        self._closed = False
        made: list[T] = []
        try:
            for slot in range(size):
                session = self._factory(slot)
                made.append(session)
                self._queue.put_nowait((slot, session))
        except BaseException:
            for session in made:
                self._close_session(session)
            raise

    @staticmethod
    def _close_session(session: T) -> None:
        try:
            session.close()
        except BaseException:  # closing must not hide the error that made us close; logged
            LOG.exception("failed to close a PoB session")

    def _get_entry(self) -> tuple[int, T | None]:
        while True:
            with self._lock:
                if self._closed:
                    raise RuntimeError("the session pool is closed")
            try:
                entry = self._queue.get(timeout=POLL_SECONDS)
            except queue.Empty:
                continue
            with self._lock:
                if not self._closed:
                    return entry
            if entry[1] is not None:
                self._close_session(entry[1])
            raise RuntimeError("the session pool is closed")

    def _create_dead_slot(self, slot: int) -> T:
        with self._lock:
            if self._closed:
                raise RuntimeError("the session pool is closed")
            try:
                return self._factory(slot)
            except BaseException:
                self._queue.put_nowait((slot, None))
                raise

    def _replace(self, slot: int) -> None:
        with self._lock:
            if self._closed:
                return
            try:
                replacement = self._factory(slot)
            except BaseException:  # the slot stays dead and the next lease retries; logged
                LOG.exception("failed to start a replacement PoB session")
                self._queue.put_nowait((slot, None))
            else:
                self._queue.put_nowait((slot, replacement))

    def _return(self, entry: tuple[int, T]) -> None:
        slot, session = entry
        with self._lock:
            if not self._closed:
                self._queue.put_nowait((slot, session))
                return
        self._close_session(session)

    @contextlib.contextmanager
    def lease(self) -> Iterator[T]:
        slot, session = self._get_entry()
        if session is None:
            session = self._create_dead_slot(slot)
        try:
            yield session
        except BaseException:
            self._close_session(session)
            self._replace(slot)
            raise
        else:
            self._return((slot, session))

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            queued = []
            while True:
                try:
                    queued.append(self._queue.get_nowait())
                except queue.Empty:
                    break
        for _, session in queued:
            if session is not None:
                self._close_session(session)
