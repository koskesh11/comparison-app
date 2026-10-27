"""F13 (S7): a test that patches a function with unittest.mock also asserts how often it was called."""

import ast
from pathlib import Path

from checks.common import NEW_TESTS, files, parse, rel

COUNTS = {
    "assert_called",
    "assert_called_once",
    "assert_called_with",
    "assert_called_once_with",
    "assert_not_called",
    "assert_has_calls",
    "assert_any_call",
    "call_count",
    "await_count",
    "assert_awaited_once",
}


def _patches(node: ast.AST) -> bool:
    func = node.func if isinstance(node, ast.Call) else node
    if isinstance(func, ast.Attribute) and func.attr == "object":
        func = func.value
    return (isinstance(func, ast.Name) and func.id == "patch") or (
        isinstance(func, ast.Attribute) and func.attr == "patch"
    )


def check(root: Path) -> list[str]:
    problems = []
    for path in files(root, NEW_TESTS, "test_*.py"):
        for node in ast.walk(parse(path)):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) or not node.name.startswith("test"):
                continue
            inner = list(ast.walk(node))
            patched = any(_patches(d) for d in node.decorator_list) or any(
                isinstance(n, ast.Call) and _patches(n) for n in inner
            )
            counted = any(isinstance(n, ast.Attribute) and n.attr in COUNTS for n in inner)
            if patched and not counted:
                problems.append(
                    f"{rel(root, path)}:{node.lineno}: {node.name} patches a function but never checks "
                    "how often it was called"
                )
    return problems
