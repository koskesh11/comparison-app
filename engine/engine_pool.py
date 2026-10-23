"""Reusable pool of isolated Path of Building engines."""

import contextlib
import logging
import queue
import threading
from collections.abc import Callable, Iterator

from pobhost import ENGINE_DIR, PobEngine

Entry = tuple[int, PobEngine | None]


class EnginePool:
    def __init__(self, size: int = 2, factory: Callable[[int], PobEngine] | None = None):
        if size < 1:
            raise ValueError("engine pool size must be positive")
        self.size = size
        self._factory = factory or self._default_factory
        self._queue: queue.Queue[Entry] = queue.Queue(maxsize=size)
        self._lock = threading.Lock()
        self._closed = False
        made = []
        try:
            for slot in range(size):
                engine = self._factory(slot)
                made.append(engine)
                self._queue.put_nowait((slot, engine))
        except BaseException:
            for engine in made:
                self._close_engine(engine)
            raise

    @staticmethod
    def _default_factory(slot: int) -> PobEngine:
        return PobEngine(userdata_dir=ENGINE_DIR / "userdata" / f"engine-{slot}")

    @staticmethod
    def _close_engine(engine: PobEngine) -> None:
        try:
            engine.close()
        except BaseException:
            logging.exception("failed to close Path of Building engine")

    def _get_entry(self) -> Entry:
        while True:
            with self._lock:
                if self._closed:
                    raise RuntimeError("engine pool is closed")
            try:
                entry = self._queue.get(timeout=0.05)
            except queue.Empty:
                continue
            with self._lock:
                if not self._closed:
                    return entry
            if entry[1] is not None:
                self._close_engine(entry[1])
            raise RuntimeError("engine pool is closed")

    def _create_dead_slot(self, slot: int) -> PobEngine:
        with self._lock:
            if self._closed:
                raise RuntimeError("engine pool is closed")
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
            except BaseException:
                self._queue.put_nowait((slot, None))
            else:
                self._queue.put_nowait((slot, replacement))

    def _return(self, entry: Entry) -> None:
        slot, engine = entry
        with self._lock:
            if not self._closed:
                self._queue.put_nowait((slot, engine))
                return
        if engine is not None:
            self._close_engine(engine)

    @contextlib.contextmanager
    def lease(self) -> Iterator[PobEngine]:
        slot, engine = self._get_entry()
        if engine is None:
            engine = self._create_dead_slot(slot)
        try:
            yield engine
        except BaseException:
            self._close_engine(engine)
            self._replace(slot)
            raise
        else:
            self._return((slot, engine))

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
        for _, engine in queued:
            if engine is not None:
                self._close_engine(engine)
