"""F7 (Lua endpoint table), F8 (Lua syntax), F9 (browser code), F10 (notes), M3 (test tree)."""

import faulthandler
from collections.abc import Callable
from pathlib import Path

import pytest
from checks.common import Skip

from checks import lua_rules, lua_syntax, notes, testtree, web

Write = Callable[[str, str], Path]

ENUM = 'from enum import StrEnum\n\n\nclass Endpoint(StrEnum):\n    CHAIN = "analysis.chain"\n'
DOC = "# Architecture\n\n## Endpoints\n| name | does |\n|---|---|\n| `analysis.chain` | the chain |\n\n## Next\n"


def test_lua_rules_pass_when_lua_enum_and_doc_agree(tmp_path: Path, write: Write) -> None:
    write("src/comparison_app/pob/endpoints.py", ENUM)
    write("docs/ARCHITECTURE.md", DOC)
    write(
        "src/comparison_app/pob/lua/analysis/chain.lua",
        'local function chain() end\nRpc.register("analysis.chain", chain)\n',
    )
    write("src/comparison_app/pob/lua/loader.lua", 'dofile("x.lua")\n')
    write("src/comparison_app/pob/lua/vendor/stub.lua", "function GlobalFromPoB() end\n")
    assert lua_rules.check(tmp_path) == []


def test_lua_rules_report_globals_loads_duplicates_and_mismatches(tmp_path: Path, write: Write) -> None:
    write("src/comparison_app/pob/endpoints.py", ENUM)
    write("docs/ARCHITECTURE.md", DOC)
    write(
        "src/comparison_app/pob/lua/analysis/chain.lua",
        'function chainJSON() end\nhelper = function() end\ndofile("other.lua")\n'
        'Rpc.register("analysis.chain", f)\nRpc.register("analysis.chain", g)\nRpc.register("compare.target", h)\n',
    )
    problems = [p.split(": ", 1)[-1] for p in lua_rules.check(tmp_path)]
    assert problems == [
        "global function `chainJSON`; make it local or register it",
        "global function `helper`; make it local or register it",
        "loads code outside loader.lua",
        "endpoint `analysis.chain` is registered twice",
        "endpoint `compare.target` is registered in Lua but missing from the Endpoint enum",
        "endpoint `compare.target` is registered in Lua but missing from docs/ARCHITECTURE.md Endpoints",
    ]


def test_lua_rules_allow_a_host_function_only_in_its_own_file(tmp_path: Path, write: Write) -> None:
    write("src/comparison_app/pob/lua/boot.lua", "function GetUserPath() return dir end\n")
    write("src/comparison_app/pob/lua/build.lua", "function GetUserPath() return elsewhere end\n")
    assert lua_rules.check(tmp_path) == [
        "src/comparison_app/pob/lua/build.lua:1: global function `GetUserPath`; make it local or register it"
    ]


def test_lua_syntax_reports_a_file_that_does_not_compile(tmp_path: Path, write: Write) -> None:
    write("src/comparison_app/pob/lua/good.lua", "local x = 1\nreturn x\n")
    write("src/comparison_app/pob/lua/bad.lua", "local x = = 1\n")
    # LuaJIT raises its errors as Windows SEH exceptions (0xE24C4A00 + code) and catches them itself; faulthandler,
    # which pytest enables, would print each one as a fatal exception.
    faulthandler.disable()
    try:
        problems = lua_syntax.check(tmp_path)
    except Skip as reason:
        pytest.skip(str(reason))
    finally:
        faulthandler.enable()
    assert len(problems) == 1 and problems[0].startswith("src/comparison_app/pob/lua/bad.lua: bad.lua:1:")


def test_web_reports_inline_code_and_a_script_that_does_not_parse(tmp_path: Path, write: Write) -> None:
    write(
        "web/index.html", '<script src="js/main.js"></script>\n<script>alert(1)</script>\n<p style="x" onclick="y">\n'
    )
    write("web/js/main.js", "export const ok = 1;\n")
    write("web/js/bad.js", "const = ;\n")
    try:
        problems = web.check(tmp_path)
    except Skip as reason:
        pytest.skip(str(reason))
    assert problems[:3] == [
        "web/index.html:2: inline script",
        "web/index.html:3: style attribute",
        "web/index.html:3: event handler attribute",
    ]
    assert len(problems) == 4 and problems[3].startswith("web/js/bad.js: ")


def test_notes_report_missing_front_matter_status_and_blocks(tmp_path: Path, write: Write) -> None:
    write("mechanics/Home.md", "no front matter needed at the top level\n")
    write("mechanics/_templates/Rule.md", "template\n")
    write("mechanics/Interactions/Good.md", "---\r\ntype: interaction\r\nstatus: verified\r\n---\r\ntext\r\n")
    write("mechanics/Interactions/Bare.md", "just text\n")
    write("mechanics/Gaps/Odd.md", "---\ntype: gap\nstatus: maybe\n---\n")
    write("mechanics/Rules/Two.md", "---\ntype: rule\nstatus: draft\n---\n```rule\na\n```\n```rule\nb\n```\n")
    assert notes.check(tmp_path) == [
        "mechanics/Gaps/Odd.md: status is 'maybe', expected draft or verified",
        "mechanics/Interactions/Bare.md: no front matter (--- ... ---) at the top",
        "mechanics/Rules/Two.md: needs exactly one ```rule block",
    ]


def test_testtree_requires_mirrored_and_guard_tests_and_honest_markers(tmp_path: Path, write: Write) -> None:
    for test in testtree.REQUIRED:
        write(test, "")
    write("src/comparison_app/pob/lua_host.py", "")
    write("src/comparison_app/pob/endpoints.py", "")
    write("tests/comparison_app/pob/test_endpoints.py", "def test_x(pob_session):\n    open_session(paths)\n")
    problems = testtree.check(tmp_path)
    assert problems == [
        "tests/comparison_app/pob/test_write_guard.py: missing (required with src/comparison_app/pob/lua_host.py, M11)",
        "tests/comparison_app/pob/test_write_sandbox.py: missing"
        " (required with src/comparison_app/pob/lua_host.py, M11)",
        "src/comparison_app/pob/lua_host.py: no test file tests/comparison_app/pob/test_lua_host.py",
        "tests/comparison_app/pob/test_endpoints.py: uses PoB but is not marked pytest.mark.pob",
        "tests/comparison_app/pob/test_endpoints.py: boots its own PoB; use the shared pob_session fixture (S6)",
    ]


def test_testtree_counts_a_bare_host_started_with_the_loader_as_a_pob_boot(tmp_path: Path, write: Write) -> None:
    for test in testtree.REQUIRED:
        write(test, "")
    write("tests/comparison_app/pob/test_host.py", "import pytest\npytest.mark.pob\nLuaHost(dll)\n")
    write("tests/comparison_app/pob/test_boot.py", "import pytest\npytest.mark.pob\nLuaHost(dll).start(LOADER)\n")
    assert testtree.check(tmp_path) == [
        "tests/comparison_app/pob/test_boot.py: boots its own PoB; use the shared pob_session fixture (S6)"
    ]
