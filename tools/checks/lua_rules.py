"""F7: one endpoint table. Every Lua endpoint is registered once with Rpc.register, no global functions, `dofile`
only in loader.lua, and the names in Lua, in the Endpoint enum and in docs/ARCHITECTURE.md ("Endpoints") agree."""

import ast
import re
from pathlib import Path

from checks.common import ARCHITECTURE, ENDPOINTS, LUA, rel

GLOBAL_FUNCTION = re.compile(r"^\s*function\s+([A-Za-z_]\w*)\s*\(")
GLOBAL_ASSIGNED_FUNCTION = re.compile(r"^([A-Za-z_]\w*)\s*=\s*function\b")
LOADS_CODE = re.compile(r"\b(dofile|loadfile|loadstring)\s*\(")
REGISTER = re.compile(r"""Rpc\.register\(\s*["']([^"']+)["']""")
DOC_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|")


def enum_values(path: Path) -> set[str]:
    if not path.exists():
        return set()
    values = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.ClassDef) and node.name == "Endpoint":
            values |= {
                item.value.value
                for item in node.body
                if isinstance(item, ast.Assign) and isinstance(item.value, ast.Constant)
            }
    return values


def documented(path: Path) -> set[str]:
    if not path.exists():
        return set()
    names, inside = set(), False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = line.strip() == "## Endpoints"
        elif inside and (match := DOC_ROW.match(line)):
            names.add(match.group(1))
    return names


def scan_lua(root: Path) -> tuple[list[str], list[str]]:
    problems, registered = [], []
    for path in sorted((root / LUA).rglob("*.lua")) if (root / LUA).exists() else []:
        name = rel(root, path)
        if "vendor" in path.relative_to(root / LUA).parts:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            code = line.split("--", 1)[0]
            if match := GLOBAL_FUNCTION.match(code) or GLOBAL_ASSIGNED_FUNCTION.match(code):
                problems.append(f"{name}:{number}: global function `{match.group(1)}`; make it local or register it")
            if LOADS_CODE.search(code) and path.name != "loader.lua":
                problems.append(f"{name}:{number}: loads code outside loader.lua")
            registered += REGISTER.findall(code)
    return problems, registered


def check(root: Path) -> list[str]:
    problems, registered = scan_lua(root)
    seen: set[str] = set()
    for name in registered:
        if name in seen:
            problems.append(f"endpoint `{name}` is registered twice")
        seen.add(name)
    in_enum, in_doc = enum_values(root / ENDPOINTS), documented(root / ARCHITECTURE)
    for label, names in (("the Endpoint enum", in_enum), (f"{ARCHITECTURE.as_posix()} Endpoints", in_doc)):
        problems += [f"endpoint `{n}` is registered in Lua but missing from {label}" for n in sorted(seen - names)]
        problems += [f"endpoint `{n}` is in {label} but not registered in Lua" for n in sorted(names - seen)]
    return problems
