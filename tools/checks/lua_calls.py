"""F6: only pob/lua_host.py talks to the Lua state; everything else calls `PobSession.call(Endpoint, payload)`.

This replaces the first app's five ways of calling PoB, which built Lua source from Python strings
(task 102, section 3).
"""

import ast
import re
from pathlib import Path

from checks.common import SRC, files, parse, rel, top_level_imports

HOST = "pob/lua_host.py"
LUA_API = re.compile(r"^luaL?_|^luaJIT_")


def check(root: Path) -> list[str]:
    problems = []
    for path in files(root, (SRC,), "*.py"):
        module = rel(root / SRC, path)
        if module == HOST:
            continue
        tree = parse(path)
        where = f"{SRC.as_posix()}/{module}"
        problems += [
            f"{where}:{node.lineno}: imports ctypes; only {HOST} may"
            for node, name in top_level_imports(tree)
            if name == "ctypes"
        ]
        problems += [
            f"{where}:{node.lineno}: calls the Lua C API (`{node.attr}`); only {HOST} may"
            for node in ast.walk(tree)
            if isinstance(node, ast.Attribute) and LUA_API.match(node.attr)
        ]
    return problems
