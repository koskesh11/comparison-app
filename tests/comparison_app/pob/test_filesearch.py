"""filesearch.lua, PoB's NewFileSearch over the Windows API (ported from tests/test_headless_filesearch.py), in a bare
Lua state (lua/filesearch_probe.lua). PoB needs it to find its timeless-jewel data (DataJewelFileLoader.lua:27)."""

import json
import os
from pathlib import Path
from typing import Any

import pytest

from comparison_app.pob.lua_host import LuaHost
from comparison_app.pob.session import LUA_DIR

pytestmark = pytest.mark.pob

PROBES = Path(__file__).parent / "lua"


@pytest.fixture
def folder(tmp_path: Path) -> Path:
    for name in ("alpha.txt", "beta.txt", "gamma.TXT", "delta.txtx", "ünïcode.txt", "data.zip.part0", "data.zip.part1"):
        (tmp_path / name).write_text(name, encoding="utf-8")
    (tmp_path / "sub").mkdir()
    return tmp_path


def search(host: LuaHost, pob_dir: Path, spec: str, directories: bool = False) -> Any:
    answer = host.run_file(
        PROBES / "filesearch_probe.lua", LUA_DIR.as_posix(), pob_dir.as_posix(), spec, "1" if directories else ""
    )
    assert answer is not None
    return json.loads(answer)


def names(result: Any) -> list[str]:
    return sorted(entry["name"] for entry in result["entries"])


def test_no_match_and_a_missing_folder_give_nothing(bare_lua: LuaHost, pob_dir: Path, folder: Path) -> None:
    assert search(bare_lua, pob_dir, f"{folder.as_posix()}/*.xyz") is None
    assert search(bare_lua, pob_dir, f"{folder.as_posix()}/nope/*.txt") is None


def test_an_exact_file_reports_its_name_size_and_time(bare_lua: LuaHost, pob_dir: Path, folder: Path) -> None:
    path = folder / "beta.txt"
    (entry,) = search(bare_lua, pob_dir, path.as_posix())["entries"]
    assert (entry["name"], entry["size"]) == ("beta.txt", path.stat().st_size)
    assert abs(entry["modified"] - path.stat().st_mtime) <= 2


def test_a_glob_uses_long_utf8_names_and_both_slashes(bare_lua: LuaHost, pob_dir: Path, folder: Path) -> None:
    result = search(bare_lua, pob_dir, f"{folder.as_posix()}/*.txt")
    assert names(result) == ["alpha.txt", "beta.txt", "gamma.TXT", "ünïcode.txt"] and result["exhausted"]
    assert names(search(bare_lua, pob_dir, str(folder / "*.txt"))) == names(result)
    assert names(search(bare_lua, pob_dir, f"{folder.as_posix()}/data.zip.part*")) == [
        "data.zip.part0",
        "data.zip.part1",
    ]


def test_the_directory_flag_picks_folders_or_files(bare_lua: LuaHost, pob_dir: Path, folder: Path) -> None:
    assert names(search(bare_lua, pob_dir, f"{folder.as_posix()}/*", directories=True)) == ["sub"]
    assert "sub" not in names(search(bare_lua, pob_dir, f"{folder.as_posix()}/*"))
    assert search(bare_lua, pob_dir, (folder / "sub").as_posix()) is None


def test_a_real_install_file_is_found(bare_lua: LuaHost, pob_dir: Path) -> None:
    path = pob_dir / "Data" / "TimelessJewelData" / "MilitantFaith.zip"
    if not path.is_file():
        pytest.skip(f"{path} is not in this install")
    (entry,) = search(bare_lua, pob_dir, path.as_posix())["entries"]
    assert (entry["name"], entry["size"]) == ("MilitantFaith.zip", os.stat(path).st_size)
