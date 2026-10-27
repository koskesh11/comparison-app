"""Python write guard for the PoB install (the first app's engine/pobhost.py:18-81, task 037; kept as it was).

A PoB session moves the whole process into the PoB install, because PoB loads its modules by relative path
(pob/session.py). A relative-path write from any Python code in the process would then land in the install. One
process-wide audit hook refuses Python writes into every guarded folder. PoB's own Lua writes are not Python audit
events; the Lua write sandbox (pob/lua/sandbox.lua) covers those.
"""

import os
import sys
from pathlib import Path

GUARD_MESSAGE = "refused: write into the Path of Building install; use an absolute path outside it"
_WRITE_MODE_CHARS = frozenset("wax+")
_WRITE_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_APPEND | os.O_TRUNC
_PATH_EVENTS = {"os.remove": 1, "os.mkdir": 1, "os.rmdir": 1, "os.rename": 2}  # event -> leading path arguments
_OPEN_ARGS = 3  # the "open" audit event passes path, mode, flags


class _Guard:
    """The guarded folders of this process; one, because an audit hook cannot be removed."""

    def __init__(self) -> None:
        self.dirs: frozenset[str] = frozenset()
        self.installed = False


_GUARD = _Guard()


def _norm(path: object) -> str | None:
    """Absolute, case-folded form of a path argument against the current folder; None for non-paths (fds)."""
    if not isinstance(path, str | bytes | os.PathLike):
        return None
    try:
        text = os.fsdecode(path)
    except (TypeError, ValueError):
        return None
    return os.path.normcase(os.path.abspath(text))


def _is_guarded(path: object) -> bool:
    norm = _norm(path)
    if norm is None:
        return False
    return any(norm == root or norm.startswith(root.rstrip(os.sep) + os.sep) for root in _GUARD.dirs)


def _is_write_open(mode: object, flags: object) -> bool:
    if isinstance(mode, str):
        return not _WRITE_MODE_CHARS.isdisjoint(mode)
    return isinstance(flags, int) and bool(flags & _WRITE_FLAGS)


def _write_guard_hook(event: str, args: tuple[object, ...]) -> None:
    if not _GUARD.dirs:
        return
    if event == "open":
        if len(args) >= _OPEN_ARGS and _is_write_open(args[1], args[2]) and _is_guarded(args[0]):
            raise PermissionError(GUARD_MESSAGE)
        return
    count = _PATH_EVENTS.get(event)
    if count and any(_is_guarded(arg) for arg in args[:count]):
        raise PermissionError(GUARD_MESSAGE)


def _guard_forms(path: Path) -> set[str]:
    return {os.path.normcase(os.path.abspath(path)), os.path.normcase(os.path.realpath(path))}


def guard_dir(path: Path) -> None:
    """Refuse Python writes into `path` for the rest of the process (installs the audit hook once)."""
    _GUARD.dirs = _GUARD.dirs | _guard_forms(path)
    if not _GUARD.installed:
        sys.addaudithook(_write_guard_hook)
        _GUARD.installed = True


def unguard_dir(path: Path) -> None:
    """Tests only: stop guarding `path` (for example before removing a temporary stand-in folder)."""
    _GUARD.dirs = _GUARD.dirs - _guard_forms(path)
