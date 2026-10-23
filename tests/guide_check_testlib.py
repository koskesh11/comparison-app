"""Helpers for guide-check integration tests using disposable XML copies."""

from __future__ import annotations

import re
import shutil
import tempfile
import json
import unittest
from contextlib import contextmanager
from pathlib import Path

from tests import golden_common as gc


def temp_dir() -> Path:
    return Path(tempfile.mkdtemp(prefix="pob_guide_check_"))


def edited_copy(source: Path, directory: Path, old: str, new: str,
                name: str = "guide.xml") -> Path:
    text = source.read_text(encoding="utf-8")
    changed = text.replace(old, new)
    if changed == text:
        raise AssertionError(f"edit marker not found: {old!r}")
    path = directory / name
    path.write_text(changed, encoding="utf-8", newline="\n")
    return path


def regex_copy(source: Path, directory: Path, pattern: str, replacement: str,
               name: str = "guide.xml") -> Path:
    text = source.read_text(encoding="utf-8")
    changed, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise AssertionError(f"expected one edit for {pattern!r}, got {count}")
    path = directory / name
    path.write_text(changed, encoding="utf-8", newline="\n")
    return path


def copy_build(source: Path, directory: Path, name: str = "guide.xml") -> Path:
    path = directory / name
    shutil.copyfile(source, path)
    return path


def gem_line(engine, name: str, level: int = 20, quality: int = 0) -> str:
    """Build an XML Gem line from the installed PoB gem table."""
    from pobhost import _lua_str
    lua = ("local name=" + _lua_str(name) + "; for id,g in pairs(data.gems) do "
           "if g.name==name then return require('dkjson').encode({id=id,"
           "skill=g.grantedEffectId,variant=g.variantId}) end end")
    value = json.loads(engine.run(lua))
    attrs = {"enabled": "true", "enableGlobal2": "true", "enableGlobal1": "true",
             "gemId": value["id"], "level": str(level), "nameSpec": name,
             "quality": str(quality), "skillId": value["skill"], "count": "1",
             "variantId": value.get("variant") or value["skill"]}
    return "\t\t\t\t<Gem " + " ".join(f'{key}="{val}"' for key, val in attrs.items()) + "/>"


def _first_skill_set(text: str) -> tuple[int, int]:
    start = text.index("<SkillSet ")
    return start, text.index("</SkillSet>", start)


def _replace_skill(text: str, group_index: int, transform) -> str:
    start, end = _first_skill_set(text)
    matches = list(re.finditer(r"(?ms)^\s*<Skill\b.*?</Skill>\s*$", text[start:end]))
    if not 1 <= group_index <= len(matches):
        raise AssertionError(f"skill group {group_index} not found")
    match = matches[group_index - 1]
    left, right = start + match.start(), start + match.end()
    changed = transform(text[left:right])
    if changed == text[left:right]:
        raise AssertionError(f"skill group {group_index} was not changed")
    return text[:left] + changed + text[right:]


def remove_gem(text: str, name: str) -> str:
    pattern = rf'(?m)^\s*<Gem\b[^>]*\bnameSpec="{re.escape(name)}"[^>]*/>\s*\r?\n?'
    changed, count = re.subn(pattern, "", text, count=1)
    if count != 1:
        raise AssertionError(f"gem not found: {name}")
    return changed


def remove_gem_from_group(text: str, group_index: int, name: str) -> str:
    return _replace_skill(text, group_index, lambda block: remove_gem(block, name))


def append_gem_to_group(text: str, group_index: int, gem_xml: str) -> str:
    def append(block: str) -> str:
        position = block.rfind("</Skill>")
        return block[:position] + gem_xml.rstrip() + "\n" + block[position:]
    return _replace_skill(text, group_index, append)


def set_gem_attrs(text: str, name: str, **attrs) -> str:
    pattern = rf'(<Gem\b[^>]*\bnameSpec="{re.escape(name)}"[^>]*/>)'
    match = re.search(pattern, text)
    if not match:
        raise AssertionError(f"gem not found: {name}")
    line = match.group(1)
    for key, value in attrs.items():
        attr = rf'\b{re.escape(key)}="[^"]*"'
        replacement = f'{key}="{value}"'
        line = re.sub(attr, replacement, line) if re.search(attr, line) else line[:-2] + f' {replacement}/>'
    return text[:match.start()] + line + text[match.end():]


def spec_nodes_without(text: str, node_id: int) -> str:
    match = re.search(r'(<Spec\b[^>]*\bnodes=")([^"]*)(")', text)
    if not match:
        raise AssertionError("Spec nodes attribute not found")
    nodes = match.group(2).split(",")
    wanted = str(node_id)
    if wanted not in nodes:
        raise AssertionError(f"node not allocated: {node_id}")
    nodes.remove(wanted)
    return text[:match.start(2)] + ",".join(nodes) + text[match.end(2):]


@contextmanager
def install_guard(case):
    before_install = gc.install_snapshot()
    before_builds = gc.install_snapshot(gc.BUILDS_DIR)
    try:
        yield
    finally:
        assert_install_unchanged(case, before_install, before_builds)


class PobGuardedTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._install_before = gc.install_snapshot()
        cls._builds_before = gc.install_snapshot(gc.BUILDS_DIR)

    @classmethod
    def tearDownClass(cls):
        try:
            assert_install_unchanged(cls(), cls._install_before, cls._builds_before)
        finally:
            super().tearDownClass()


def assert_install_unchanged(case, before_install: dict, before_builds: dict) -> None:
    allowed = ("Data\\TimelessJewelData\\", "AutoBuilder")
    install = [line for line in gc.install_diff(before_install, gc.install_snapshot())
               if not any(value in line for value in allowed)]
    builds = [line for line in gc.install_diff(before_builds, gc.install_snapshot(gc.BUILDS_DIR))
              if "AutoBuilder" not in line]
    case.assertEqual([], install)
    case.assertEqual([], builds)
