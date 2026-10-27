"""Paths and helpers shared by the checks."""

import ast
import subprocess
from collections.abc import Iterable, Iterator
from pathlib import Path

SRC = Path("src/autobuilder")
SRC_TESTS = Path("tests/autobuilder")
NEW_TESTS = (SRC_TESTS, Path("tests/architecture"), Path("tests/checks"))
NEW_TOOLS = (
    Path("tools/check.py"),
    Path("tools/checks"),
    Path("tools/install_hooks.py"),
    Path("tools/merge_to_main.py"),
)
WEB = Path("web")
MECHANICS = Path("mechanics")
LUA = SRC / "pob" / "lua"
ENDPOINTS = SRC / "pob" / "endpoints.py"
ARCHITECTURE = Path("docs/ARCHITECTURE.md")


class Skip(Exception):
    """A check that cannot run here (for example PoB is not installed); tools/check.py shows the reason."""


def files(root: Path, bases: Iterable[Path], pattern: str) -> Iterator[Path]:
    """Every file matching `pattern` under the given files or folders, sorted, without caches."""
    for base in bases:
        path = root / base
        if path.is_file() and path.match(pattern):
            yield path
        elif path.is_dir():
            yield from sorted(p for p in path.rglob(pattern) if "__pycache__" not in p.parts and p.is_file())


def parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def top_level_imports(tree: ast.Module) -> Iterator[tuple[ast.AST, str]]:
    """(node, top-level module name) for every absolute import in the tree."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield node, alias.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            yield node, node.module.split(".")[0]


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True, timeout=60).stdout
