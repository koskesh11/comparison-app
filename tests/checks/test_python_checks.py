"""F3 (no engine), F4 (sizes), F5/F14 (structure), F6 (Lua only through lua_host), F13 (patch counts)."""

from collections.abc import Callable
from pathlib import Path

from checks import lua_calls, no_engine, patch_counts, sizes, structure

Write = Callable[[str, str], Path]


def test_no_engine_reports_engine_imports_paths_and_sys_path(tmp_path: Path, write: Write) -> None:
    write("engine/audit.py", "")
    write("src/autobuilder/ok.py", "import json\nfrom autobuilder import pob\n")
    write(
        "tests/autobuilder/test_bad.py",
        "import sys\nimport audit\nimport mechanics\nsys.path.insert(0, 'x')\nPATH = 'engine/pobhost.py'\n",
    )
    problems = no_engine.check(tmp_path)
    assert [p.split(": ", 1)[1] for p in problems] == [
        "imports `audit` from the frozen engine/",
        "imports the notes folder `mechanics`",
        "uses sys.path (imports come from pyproject's pythonpath)",
        "names an engine/ path",
    ]


def test_sizes_reports_a_long_file_and_an_exemption_without_reason(tmp_path: Path, write: Write) -> None:
    write("src/autobuilder/long.py", "x = 1\n" * 401)
    write("src/autobuilder/fine.py", "x = 1\n" * 400)
    write("src/autobuilder/pob/lua/vendor/stub.lua", "x = 1\n" * 500)
    write(
        "tools/checks/size_exemptions.toml",
        '[[exempt]]\npath = "src/autobuilder/pob/lua/vendor/stub.lua"\nreason = "copied from PoB"\n'
        '[[exempt]]\npath = "src/autobuilder/other.lua"\nreason = ""\n',
    )
    assert sizes.check(tmp_path) == [
        "tools/checks/size_exemptions.toml: entry src/autobuilder/other.lua has no reason",
        "src/autobuilder/long.py: 401 lines (limit 400); split it, it does two jobs",
    ]


def test_network_environment_and_personal_paths(tmp_path: Path, write: Write) -> None:
    write("src/autobuilder/intake/pobbin.py", "import urllib.request\n")
    write("src/autobuilder/app/settings.py", "import os\nHOME = os.environ['HOME']\n")
    write("src/autobuilder/analysis/session.py", "import os, socket\nX = os.getenv('X')\n")
    write("tests/autobuilder/test_x.py", "BUILDS = 'C:\\\\Users\\\\someone\\\\Documents'\n")
    problems = structure.check_network(tmp_path)
    assert len(problems) == 3
    assert "session.py:1: imports `socket`" in problems[0] and "reads the environment" in problems[1]
    assert problems[2].startswith("tests/autobuilder/test_x.py:1: a personal path")


def test_subprocess_needs_a_listed_module_no_pipe_and_a_timeout(tmp_path: Path, write: Write) -> None:
    write(
        "src/autobuilder/pob/runner.py",
        "import subprocess\nsubprocess.run(['x'], stdout=subprocess.PIPE)\nsubprocess.Popen(['y'])\n",
    )
    problems = structure.check_subprocess(tmp_path)
    assert [p.split(": ", 1)[1].split(";")[0] for p in problems] == [
        "imports subprocess",
        "a pipe to a child process",
        "a child process without timeout= (S4)",
    ]


def test_only_lua_host_uses_ctypes_and_the_lua_api(tmp_path: Path, write: Write) -> None:
    write("src/autobuilder/pob/lua_host.py", "import ctypes\nlua = ctypes.CDLL('x')\nlua.luaL_loadbuffer(1)\n")
    write("src/autobuilder/analysis/chain.py", "import ctypes\nsession.lua.lua_pcall(1)\n")
    problems = lua_calls.check(tmp_path)
    assert [p.split(": ", 1)[1] for p in problems] == [
        "imports ctypes; only pob/lua_host.py may",
        "calls the Lua C API (`lua_pcall`); only pob/lua_host.py may",
    ]


def test_patch_without_a_call_count_is_reported(tmp_path: Path, write: Write) -> None:
    write(
        "tests/autobuilder/test_fetch.py",
        "from unittest import mock\n\n"
        "@mock.patch('autobuilder.intake.pobbin.fetch')\ndef test_counted(fetch):\n    fetch.assert_called_once()\n\n"
        "def test_uncounted():\n    with mock.patch.object(obj, 'fetch'):\n        run()\n\n"
        "def test_no_patch():\n    assert True\n",
    )
    assert patch_counts.check(tmp_path) == [
        "tests/autobuilder/test_fetch.py:7: test_uncounted patches a function but never checks how often it was called"
    ]
