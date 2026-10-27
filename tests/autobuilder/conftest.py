"""Shared fixtures for the src/ tests (docs/ARCHITECTURE.md, "Tests").

- pob_session: one Path of Building per test run (S6). The PoB install and the owner's builds are listed before and
  after; any change outside Builds/AutoBuilder fails the run (S1; PoB's own timeless-jewel cache is allowed).
- No network: outside tests/autobuilder/intake every socket refuses to connect (S2).
"""

import os
import socket
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

POB_OWN_WRITES = ("Data/TimelessJewelData/",)
OUTPUT_FOLDER = ("AutoBuilder/",)


def pob_install() -> Path:
    appdata = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
    return Path(os.environ.get("POB_DIR", Path(appdata) / "Path of Building Community"))


def builds_folder() -> Path:
    return Path.home() / "Documents" / "Path of Building" / "Builds"


def listing(root: Path, allowed: tuple[str, ...]) -> dict[str, tuple[int, int]]:
    """Size and modification time of every file under root, except the allowed prefixes."""
    if not root.exists():
        return {}
    files = {}
    for path in root.rglob("*"):
        name = path.relative_to(root).as_posix()
        if path.is_file() and not name.startswith(allowed):
            stat = path.stat()
            files[name] = (stat.st_size, stat.st_mtime_ns)
    return files


def changed(before: dict[str, tuple[int, int]], after: dict[str, tuple[int, int]]) -> list[str]:
    return sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))


@pytest.fixture(scope="session")
def pob_session() -> Iterator[Any]:
    session = pytest.importorskip("autobuilder.pob.session", reason="no PobSession yet (milestone 1)")
    roots = ((pob_install(), POB_OWN_WRITES), (builds_folder(), OUTPUT_FOLDER))
    before = [listing(root, allowed) for root, allowed in roots]
    with session.open_session() as opened:
        yield opened
    for (root, allowed), old in zip(roots, before, strict=True):
        touched = changed(old, listing(root, allowed))
        assert not touched, f"PoB tests changed files in the read-only folder {root}: {touched[:10]}"


@pytest.fixture(autouse=True)
def no_network(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    if "intake" in request.path.parts:
        return

    def refuse(*_args: object, **_kwargs: object) -> None:
        raise OSError("tests do not use the network (S2); only tests/autobuilder/intake may")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
