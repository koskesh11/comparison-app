"""Fixtures for the PoB layer's tests.

- bare_lua: a Lua state on PoB's lua51.dll with Lua's standard libraries and no PoB, for the host's and rpc.lua's own
  tests. It is not a PoB boot (S6 counts only those).
- PROBES: Lua files under lua/ that these tests run in a bare state or in the shared session. They are test code:
  the checks for src/ Lua do not apply to them.
"""

from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

from autobuilder.pob.lua_host import LuaHost
from autobuilder.pob.session import LUA_DIR, PobSession

PROBES = Path(__file__).parent / "lua"


@pytest.fixture
def bare_lua(pob_dir: Path) -> Iterator[LuaHost]:
    host = LuaHost(pob_dir / "lua51.dll")
    yield host
    host.close()


@pytest.fixture
def fail_output(pob_session: PobSession) -> Iterator[Callable[[int], None]]:
    """Arms the open build's next `count` BuildOutput calls to raise (lua/fail_output.lua); disarmed after the test."""

    def arm(count: int) -> None:
        pob_session._host.run_file(PROBES / "fail_output.lua", str(count))  # the probe needs the session's state

    yield arm
    arm(0)


@pytest.fixture
def probe_rpc(bare_lua: LuaHost, pob_dir: Path) -> LuaHost:
    """A bare state booted with rpc.lua and the probe endpoints of lua/dispatcher.lua."""
    bare_lua.start(PROBES / "dispatcher.lua", LUA_DIR.as_posix(), pob_dir.as_posix())
    return bare_lua
