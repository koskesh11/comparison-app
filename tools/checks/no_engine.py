"""F3 (with import-linter): src/ and its tests never use the frozen first app (decision 004).

No import of an engine/ module, no engine/ path in a string, no sys.path edits, no import of the top-level notes
folder `mechanics` (it would resolve as a namespace package instead of failing).
"""

import ast
import re
from pathlib import Path

from checks.common import SRC, SRC_TESTS, files, parse, rel, top_level_imports

ENGINE_PATH = re.compile(r"(^|[/\\])engine[/\\]")


def engine_modules(root: Path) -> set[str]:
    return {path.stem for path in (root / "engine").glob("*.py")} | {"engine"}


def check(root: Path) -> list[str]:
    banned = engine_modules(root)
    problems = []
    for path in files(root, (SRC, SRC_TESTS), "*.py"):
        name, tree, found = rel(root, path), parse(path), []
        for node, module in top_level_imports(tree):
            if module in banned:
                found.append((node.lineno, f"imports `{module}` from the frozen engine/"))
            elif module == "mechanics":
                found.append((node.lineno, "imports the notes folder `mechanics`"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and node.attr == "path"
                and isinstance(node.value, ast.Name)
                and node.value.id == "sys"
            ):
                found.append((node.lineno, "uses sys.path (imports come from pyproject's pythonpath)"))
            elif isinstance(node, ast.Constant) and isinstance(node.value, str) and ENGINE_PATH.search(node.value):
                found.append((node.lineno, "names an engine/ path"))
        problems += [f"{name}:{line}: {text}" for line, text in sorted(found)]
    return problems
