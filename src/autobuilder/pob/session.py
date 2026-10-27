"""One PoB: a booted Lua state and the only way src/ calls it (docs/ARCHITECTURE.md, "How src/ calls PoB").

`start_session` checks the install, guards it against Python writes, moves the process into it and boots PoB through
pob/lua/loader.lua. PoB loads its modules by relative path, also after boot, so the move is process-wide and stays
(target design, interfaces 4.1); every path the app passes is absolute. After boot every request is
`call(Endpoint, payload)`.
"""

import os
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from autobuilder.errors import PobNotInstalled
from autobuilder.pob import wire
from autobuilder.pob.endpoints import Endpoint
from autobuilder.pob.lua_host import LuaHost
from autobuilder.pob.write_guard import guard_dir

LUA_DIR = Path(__file__).resolve().parent / "lua"
LOADER = LUA_DIR / "loader.lua"
INSTALL_FILES = ("Launch.lua", "lua51.dll")


@dataclass(frozen=True)
class PobPaths:
    pob_dir: Path  # the install: Launch.lua and lua51.dll
    user_dir: Path  # PoB's user data for this session (Settings.xml), never the owner's own PoB settings
    write_root: Path  # the one builds folder the app writes to (Builds\AutoBuilder)


@dataclass(frozen=True)
class BuildSummary:
    """The build PoB has open (build.load, build.summary). A stat PoB did not compute is not in `stats`."""

    pob_version: str | None
    build_name: str | None
    class_name: str | None
    ascendancy: str | None
    level: float | None
    main_skill: str | None
    stats: Mapping[str, float]

    @classmethod
    def from_wire(cls, value: object) -> "BuildSummary":
        data = wire.table(value)
        stats = {key: wire.number(item) for key, item in wire.table(data.get("stats")).items()}
        return cls(
            pob_version=wire.text(data.get("pobVersion")),
            build_name=wire.text(data.get("buildName")),
            class_name=wire.text(data.get("className")),
            ascendancy=wire.text(data.get("ascendancy")),
            level=wire.number(data.get("level")),
            main_skill=wire.text(data.get("mainSkill")),
            stats={key: item for key, item in stats.items() if item is not None},
        )


class PobSession:
    """One booted PoB; the pool lends it to one job at a time."""

    def __init__(self, host: LuaHost) -> None:
        self._host = host

    @property
    def closed(self) -> bool:
        return self._host.closed

    def close(self) -> None:
        self._host.close()

    def call(self, endpoint: Endpoint, payload: Mapping[str, Any] | None = None) -> Any:
        return wire.decode_reply(self._host.call(endpoint.value, wire.encode_request(payload)))

    def load_build(self, xml: str, name: str) -> BuildSummary:
        """Open a build from its XML text. A build PoB cannot open raises BuildLoadFailed and leaves none open."""
        return BuildSummary.from_wire(self.call(Endpoint.BUILD_LOAD, {"xml": xml, "name": name}))

    def summary(self) -> BuildSummary:
        return BuildSummary.from_wire(self.call(Endpoint.BUILD_SUMMARY))


def _overlap(first: Path, second: Path) -> bool:
    one, two = (Path(os.path.normcase(os.path.abspath(folder))) for folder in (first, second))
    return one.is_relative_to(two) or two.is_relative_to(one)


def check_paths(paths: PobPaths) -> None:
    """Absolute folders (the boot moves the process into PoB's), a PoB install in `pob_dir`, and the two folders the
    sandbox lets PoB write to (sandbox.lua) apart from the install. Settings keeps them out of the owner's builds."""
    if not all(folder.is_absolute() for folder in (paths.pob_dir, paths.user_dir, paths.write_root)):
        raise ValueError(f"PoB paths must be absolute: {paths}")
    if _overlap(paths.user_dir, paths.pob_dir) or _overlap(paths.write_root, paths.pob_dir):
        raise ValueError(f"PoB's user data and write root must be outside its install and not contain it: {paths}")
    missing = [name for name in INSTALL_FILES if not (paths.pob_dir / name).is_file()]
    if missing:
        raise PobNotInstalled(f"Path of Building not found in {paths.pob_dir} (missing {', '.join(missing)})")


def start_session(paths: PobPaths) -> PobSession:
    check_paths(paths)
    folders = (paths.pob_dir, paths.user_dir, paths.write_root)
    paths.user_dir.mkdir(parents=True, exist_ok=True)
    guard_dir(paths.pob_dir)
    os.chdir(paths.pob_dir)
    host = LuaHost(paths.pob_dir / "lua51.dll")
    try:
        host.start(LOADER, *(folder.as_posix() for folder in (LUA_DIR, *folders)))
    except BaseException:
        host.close()
        raise
    return PobSession(host)


@contextmanager
def open_session(paths: PobPaths) -> Iterator[PobSession]:
    session = start_session(paths)
    try:
        yield session
    finally:
        session.close()
