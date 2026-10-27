"""M11: the Lua write sandbox (ported from tests/test_write_sandbox.py, task 025). The path rules run in a bare Lua
state (lua/sandbox_rules.lua); real write attempts run inside the shared PoB session (lua/sandbox_writes.lua).

Refusal probes use paths in a folder that does not exist, so a broken sandbox fails the test with an OS error instead
of writing into the PoB install or the owner's builds."""

import json
from pathlib import Path
from typing import Any

import pytest

from autobuilder.pob.lua_host import LuaHost
from autobuilder.pob.session import LUA_DIR, PobPaths, PobSession

pytestmark = pytest.mark.pob

PROBES = Path(__file__).parent / "lua"

NO_SUCH = "__sandbox_probe_no_such_dir__"
BUILDS = Path.home() / "Documents" / "Path of Building" / "Builds"
RULE = "write sandbox (task 025)"


def allowed(host: LuaHost, paths: PobPaths, *probes: str) -> list[bool]:
    folders = (LUA_DIR, paths.pob_dir, paths.user_dir, paths.write_root)
    answers = host.run_file(PROBES / "sandbox_rules.lua", *(f.as_posix() for f in folders), *probes)
    assert answers is not None
    result: list[bool] = json.loads(answers)
    return result


def attempt(session: PobSession, *operations: dict[str, Any]) -> list[dict[str, Any]]:
    answers = session._host.run_file(PROBES / "sandbox_writes.lua", json.dumps(operations))  # the probe needs the state
    assert answers is not None
    result: list[dict[str, Any]] = json.loads(answers)
    return result


def assert_refused(answers: list[dict[str, Any]]) -> None:
    for answer in answers:
        assert not answer["ok"] and "write refused" in answer["error"] and RULE in answer["error"], answer


def test_timeless_cache_allows_only_flat_bin_files(bare_lua: LuaHost, pob_paths: PobPaths) -> None:
    timeless = (pob_paths.pob_dir / "Data" / "TimelessJewelData").as_posix()
    good = [f"{timeless}/GloriousVanity.bin", f"{timeless}/glorioUSvanity.BIN", "Data/TimelessJewelData/Elegant.bin"]
    bad = [
        f"{timeless}/GloriousVanity.zip", f"{timeless}/NodeIndexMapping.lua", f"{timeless}/.bin",
        f"{timeless}/sub/x.bin", f"{timeless}/../x.bin", f"{timeless}x/x.bin", f"{timeless}/x.bin.exe", timeless,
    ]  # fmt: skip
    assert allowed(bare_lua, pob_paths, *good, *bad) == [True] * len(good) + [False] * len(bad)


def test_write_root_and_user_data_are_allowed_and_nothing_near_them(bare_lua: LuaHost, pob_paths: PobPaths) -> None:
    root, user = pob_paths.write_root.as_posix(), pob_paths.user_dir.as_posix()
    good = [f"{root}/x.xml", f"{root.upper()}/sub/x.xml", f"{root}/./sub/../again.xml", f"{user}/Settings.xml"]
    bad = [
        f"{root}/../{NO_SUCH}/x.xml", f"{root}/sub/../../{NO_SUCH}/x", f"{root}2/x.xml", f"{root}./x", f"{root} /x",
        f"{root}/x.xml:stream", "C:foo", "//server/share/x", f"{NO_SUCH}/x.txt", "Data/ModCache.lua",
        (BUILDS / "3.29" / NO_SUCH / "x.xml").as_posix(), root,
    ]  # fmt: skip
    assert allowed(bare_lua, pob_paths, *good, *bad) == [True] * len(good) + [False] * len(bad)


def test_writes_into_the_install_and_the_owners_builds_are_refused(pob_session: PobSession, pob_dir: Path) -> None:
    target = (pob_dir / NO_SUCH / "x.txt").as_posix()
    answers = attempt(pob_session, *({"op": "open", "path": target, "mode": m} for m in ("w", "wb", "a", "r+", "w+b")))
    assert_refused(answers)
    assert all(target in answer["error"] for answer in answers)
    assert_refused(attempt(pob_session, {"op": "open", "path": "Data/TimelessJewelData/x.zip", "mode": "wb"}))
    assert_refused(attempt(pob_session, {"op": "open", "path": (BUILDS / NO_SUCH / "x.xml").as_posix(), "mode": "w"}))


def test_invalid_open_modes_are_refused_before_the_c_runtime(pob_session: PobSession, pob_paths: PobPaths) -> None:
    target = (pob_paths.pob_dir / NO_SUCH / "x.txt").as_posix()
    answers = attempt(
        pob_session, *({"op": "open", "path": target, "mode": m} for m in ("W", "R", "rw", "wbb", "x", "", 42, True))
    )
    assert_refused(answers)
    assert all("invalid mode" in answer["error"] for answer in answers)
    probe = (pob_paths.write_root / "mode-probe.xml").as_posix()
    modes = ("w", "wb", "w+b", "wb+", "a", "ab", "a+", "r+", "r+b", "rb+")
    answers = attempt(pob_session, *({"op": "open", "path": probe, "mode": mode} for mode in modes))
    assert [answer["ok"] for answer in answers] == [True] * len(modes)


def test_writes_into_the_write_root_work_and_read_back(pob_session: PobSession, pob_paths: PobPaths) -> None:
    target = pob_paths.write_root / "saved build.xml"
    shouting = str(target).upper()
    answers = attempt(
        pob_session,
        {"op": "write", "path": target.as_posix(), "text": "<PathOfBuilding/>"},
        {"op": "write", "path": shouting, "mode": "ab", "text": "!"},
        {"op": "read", "path": (pob_paths.pob_dir / "Launch.lua").as_posix()},
    )
    assert [answer["ok"] for answer in answers] == [True, True, True]
    assert target.read_text(encoding="utf-8") == "<PathOfBuilding/>!" and answers[2]["value"] > 100


def test_remove_rename_output_and_child_processes_are_refused(pob_session: PobSession, pob_paths: PobPaths) -> None:
    inside = pob_paths.write_root / "inside.xml"
    inside.write_text("x", encoding="utf-8")
    outside = (pob_paths.pob_dir / NO_SUCH / "y").as_posix()
    assert_refused(
        attempt(
            pob_session,
            {"op": "remove", "path": outside},
            {"op": "remove", "path": (BUILDS / NO_SUCH / "x.xml").as_posix()},
            {"op": "rename", "from": inside.as_posix(), "to": outside},
            {"op": "rename", "from": (BUILDS / NO_SUCH / "a").as_posix(), "to": inside.as_posix()},
            {"op": "output", "path": outside},
            {"op": "removedir", "path": (pob_paths.pob_dir / "TreeData").as_posix()},
            {"op": "makedir", "path": outside},
            {"op": "popen", "command": "cmd /c echo hi > x.txt"},
            {"op": "execute", "command": "cmd /c echo hi > x.txt"},
        )
    )
    assert inside.is_file()


def test_remove_and_rename_inside_the_write_root_work(pob_session: PobSession, pob_paths: PobPaths) -> None:
    old, new = pob_paths.write_root / "old.xml", pob_paths.write_root / "new.xml"
    old.write_text("x", encoding="utf-8")
    answers = attempt(
        pob_session,
        {"op": "rename", "from": old.as_posix(), "to": new.as_posix()},
        {"op": "remove", "path": new.as_posix()},
        {"op": "makedir", "path": "TreeData"},  # PoB calls this on every tree load; the folder exists
    )
    assert [answer["ok"] for answer in answers] == [True, True, True]
    assert not old.exists() and not new.exists()


def test_the_originals_are_out_of_reach_through_the_debug_library(pob_session: PobSession) -> None:
    (answer,) = attempt(pob_session, {"op": "debug"})
    assert answer["value"] == {"present": [], "traceback": "function", "loaded": "nilnil", "getupvalue": "false"}
