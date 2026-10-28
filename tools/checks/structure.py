"""F5 and F14: where src/ may reach the network, the environment and child processes.

F5: network modules only in intake/, league/ and app/ (S2); the environment only in app/settings.py; no personal
paths in src/ or its tests. F14: subprocess only in a module listed here with a reason, never with a pipe, always
with a timeout (S4).
"""

import ast
import re
from pathlib import Path

from checks.common import SRC, SRC_TESTS, files, parse, rel, top_level_imports

NETWORK = {"urllib", "urllib3", "http", "socket", "ssl", "requests", "httpx", "aiohttp", "ftplib", "smtplib"}
NETWORK_FOLDERS = ("intake/", "league/", "app/")
ENVIRONMENT_MODULES = {"app/settings.py"}
SUBPROCESS_MODULES: dict[str, str] = {}  # module (relative to src/comparison_app) -> reason
PERSONAL = re.compile(r"[A-Za-z]:[\\/]Users[\\/]|7800x3D", re.IGNORECASE)
TIMEOUT_CALLS = {"run", "call", "check_call", "check_output"}


def _is(node: ast.AST, owner: str, attrs: set[str]) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr in attrs
        and isinstance(node.value, ast.Name)
        and node.value.id == owner
    )


def check_network(root: Path) -> list[str]:
    problems = []
    for path in files(root, (SRC,), "*.py"):
        module, tree = rel(root / SRC, path), parse(path)
        for node, name in top_level_imports(tree):
            if name in NETWORK and not module.startswith(NETWORK_FOLDERS):
                problems.append(
                    f"{SRC.as_posix()}/{module}:{node.lineno}: imports `{name}`; network code lives in "
                    f"{', '.join(NETWORK_FOLDERS)}"
                )
        for node in ast.walk(tree):
            if (_is(node, "os", {"environ", "getenv", "putenv"})) and module not in ENVIRONMENT_MODULES:
                problems.append(
                    f"{SRC.as_posix()}/{module}:{node.lineno}: reads the environment; only app/settings.py may"
                )
    for path in files(root, (SRC, SRC_TESTS), "*.py"):
        for node in ast.walk(parse(path)):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and PERSONAL.search(node.value):
                problems.append(f"{rel(root, path)}:{node.lineno}: a personal path; take it from settings")
    return problems


def check_subprocess(root: Path) -> list[str]:
    problems = []
    for path in files(root, (SRC,), "*.py"):
        module, tree = rel(root / SRC, path), parse(path)
        where = f"{SRC.as_posix()}/{module}"
        for node, name in top_level_imports(tree):
            if name == "subprocess" and module not in SUBPROCESS_MODULES:
                problems.append(
                    f"{where}:{node.lineno}: imports subprocess; list the module in "
                    "tools/checks/structure.py with a reason"
                )
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not _is(node.func, "subprocess", TIMEOUT_CALLS | {"Popen"}):
                continue
            keywords = {kw.arg: kw.value for kw in node.keywords}
            if any(_is(keywords.get(arg), "subprocess", {"PIPE"}) for arg in ("stdout", "stderr")):
                problems.append(f"{where}:{node.lineno}: a pipe to a child process; write to a temp file (S4)")
            if isinstance(node.func, ast.Attribute) and node.func.attr in TIMEOUT_CALLS and "timeout" not in keywords:
                problems.append(f"{where}:{node.lineno}: a child process without timeout= (S4)")
    return problems
