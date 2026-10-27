"""Shared fixtures for the src/ tests (docs/ARCHITECTURE.md, "Tests").

- pob_session: one Path of Building per test run (S6), with its user data and write root in a temporary folder. The PoB
  install and the owner's builds are listed before and after; any change outside Builds/AutoBuilder fails the run (S1;
  PoB's own timeless-jewel cache is allowed). Every test marked `pob` runs on one xdist worker (`--dist loadgroup`), so
  a parallel run boots PoB once.
- reference_xml: the two reference builds (decision 014), committed byte for byte under fixtures/builds.
- No network: outside tests/autobuilder/intake every socket refuses to connect (S2).
"""

import os
import socket
from collections.abc import Iterator
from pathlib import Path

import pytest

from autobuilder.pob.session import PobPaths, PobSession, open_session

POB_OWN_WRITES = ("Data/TimelessJewelData/",)
OUTPUT_FOLDER = ("AutoBuilder/",)
REFERENCE_BUILDS = Path(__file__).parent / "fixtures" / "builds"
REFERENCE_FILES = {"Worb": "Worb.xml", "CoC EK Assa": "CoC EK Assa.xml"}


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


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        if item.get_closest_marker("pob"):
            item.add_marker(pytest.mark.xdist_group("pob"))


@pytest.fixture(scope="session")
def pob_dir() -> Path:
    if not (pob_install() / "Launch.lua").is_file():
        pytest.skip(f"needs Path of Building in {pob_install()}")
    return pob_install()


@pytest.fixture(scope="session")
def pob_paths(pob_dir: Path, tmp_path_factory: pytest.TempPathFactory) -> PobPaths:
    root = tmp_path_factory.mktemp("pob")
    (root / "AutoBuilder").mkdir()
    return PobPaths(pob_dir, root / "user", root / "AutoBuilder")


@pytest.fixture(scope="session")
def pob_session(pob_paths: PobPaths) -> Iterator[PobSession]:
    roots = ((pob_paths.pob_dir, POB_OWN_WRITES), (builds_folder(), OUTPUT_FOLDER))
    before = [listing(folder, allowed) for folder, allowed in roots]
    previous = Path.cwd()
    with open_session(pob_paths) as opened:
        yield opened
    os.chdir(previous)
    for (folder, allowed), old in zip(roots, before, strict=True):
        touched = changed(old, listing(folder, allowed))
        assert not touched, f"PoB tests changed files in the read-only folder {folder}: {touched[:10]}"


@pytest.fixture(scope="session")
def reference_xml() -> dict[str, str]:
    return {name: (REFERENCE_BUILDS / file).read_text(encoding="utf-8") for name, file in REFERENCE_FILES.items()}


@pytest.fixture(autouse=True)
def no_network(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    if "intake" in request.path.parts:
        return

    def refuse(*_args: object, **_kwargs: object) -> None:
        raise OSError("tests do not use the network (S2); only tests/autobuilder/intake may")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
