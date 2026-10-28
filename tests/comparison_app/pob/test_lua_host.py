"""The Lua host on PoB's lua51.dll, in a bare Lua state: files run with text arguments, requests reach the dispatcher,
every failure comes back as a PobError with Lua's message and traceback (task 102, area A Q1, Q3)."""

import contextlib
from pathlib import Path

import pytest

from comparison_app.errors import PobError
from comparison_app.pob.lua_host import LuaHost

pytestmark = pytest.mark.pob


def lua_file(tmp_path: Path, source: str) -> Path:
    path = tmp_path / "probe.lua"
    path.write_text(source, encoding="utf-8")
    return path


def test_a_file_runs_with_text_arguments_and_answers_text(bare_lua: LuaHost, tmp_path: Path) -> None:
    probe = lua_file(tmp_path, "local a, b = ...\nreturn a .. '|' .. b .. '|' .. select('#', ...)\n")
    assert bare_lua.run_file(probe, "it's", 'quote " ]] \n ünï') == "it's|quote \" ]] \n ünï|2"


def test_a_result_that_is_not_text_is_none(bare_lua: LuaHost, tmp_path: Path) -> None:
    assert bare_lua.run_file(lua_file(tmp_path, "return true\n")) is None
    assert bare_lua.run_file(lua_file(tmp_path, "return\n")) is None


def test_a_file_that_does_not_compile_names_the_file(bare_lua: LuaHost, tmp_path: Path) -> None:
    with pytest.raises(PobError, match=r"probe\.lua does not compile: .*probe\.lua:1:"):
        bare_lua.run_file(lua_file(tmp_path, "local x = = 1\n"))


def test_a_lua_error_has_its_message_and_a_traceback(bare_lua: LuaHost, tmp_path: Path) -> None:
    with pytest.raises(PobError) as caught:
        bare_lua.run_file(lua_file(tmp_path, "local function deep() error('boom') end\ndeep()\n"))
    assert caught.value.message.endswith("probe.lua:1: boom")
    assert caught.value.traceback is not None and caught.value.traceback.startswith("stack traceback:")


def test_a_message_over_several_lines_stays_whole(bare_lua: LuaHost, tmp_path: Path) -> None:
    # PoB's startup prompt starts with "^1Error:\n\n" (Launch.lua:384); its reason is on the later lines.
    with pytest.raises(PobError) as caught:
        bare_lua.run_file(lua_file(tmp_path, "error('PoB startup failed: Error:\\n\\nthe real reason', 0)\n"))
    assert caught.value.message == "PoB startup failed: Error:\n\nthe real reason"
    assert caught.value.traceback is not None and caught.value.traceback.startswith("stack traceback:")


def test_a_missing_file_is_a_pob_error_and_leaves_the_stack_alone(bare_lua: LuaHost, tmp_path: Path) -> None:
    with pytest.raises(PobError, match="cannot read"):
        bare_lua.run_file(tmp_path / "missing.lua")
    assert bare_lua.run_file(lua_file(tmp_path, "return tostring(select('#', ...))\n")) == "0"


def test_an_error_that_is_not_text_says_what_it_was(bare_lua: LuaHost, tmp_path: Path) -> None:
    # The first app turned this into LuaError(None) (pobhost.py:148, measured by area A).
    with pytest.raises(PobError, match=r"^a Lua error that is not text \(a table\)$"):
        bare_lua.run_file(lua_file(tmp_path, "error({})\n"))


def test_the_stack_is_back_to_empty_after_every_kind_of_call(bare_lua: LuaHost, tmp_path: Path) -> None:
    for source in ("return 1, 2, 3\n", "error('x')\n", "local x = = 1\n"):
        with contextlib.suppress(PobError):
            bare_lua.run_file(lua_file(tmp_path, source))
    probe = lua_file(tmp_path, "return tostring(select('#', ...))\n")
    assert bare_lua.run_file(probe) == "0"


def test_requests_reach_the_dispatcher_byte_for_byte(bare_lua: LuaHost, tmp_path: Path) -> None:
    bare_lua.start(lua_file(tmp_path, "return function(name, payload) return name .. '=' .. payload end\n"))
    payload = b"\x00binary\xff" + b"x" * 1_000_000
    assert bare_lua.call("probe.echo", payload) == b"probe.echo=" + payload


def test_a_dispatcher_error_and_a_reply_that_is_not_text_raise(bare_lua: LuaHost, tmp_path: Path) -> None:
    bare_lua.start(lua_file(tmp_path, "return function(name) if name == 'bad' then error('no') end return 42 end\n"))
    with pytest.raises(PobError, match=r"no$"):
        bare_lua.call("bad", b"{}")
    with pytest.raises(PobError, match="answered good with something other than text"):
        bare_lua.call("good", b"{}")


def test_start_needs_a_function_and_call_needs_a_start(bare_lua: LuaHost, tmp_path: Path) -> None:
    with pytest.raises(PobError, match="not booted"):
        bare_lua.call("x", b"{}")
    with pytest.raises(PobError, match="returned no dispatcher function"):
        bare_lua.start(lua_file(tmp_path, "return 'not a function'\n"))


def test_a_closed_host_refuses_and_closing_twice_is_harmless(bare_lua: LuaHost, tmp_path: Path) -> None:
    bare_lua.close()
    bare_lua.close()
    assert bare_lua.closed
    with pytest.raises(PobError, match="closed"):
        bare_lua.run_file(lua_file(tmp_path, "return 'x'\n"))
