"""F8: our own .lua files compile with PoB's lua51.dll (LuaJIT 2.1). Compile only, never run; PoB is not booted."""

import ctypes
import os
from pathlib import Path

from checks.common import LUA, Skip, rel


def pob_dir() -> Path:
    appdata = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
    return Path(os.environ.get("POB_DIR", Path(appdata) / "Path of Building Community"))


def _bind(dll: Path) -> ctypes.CDLL:
    os.add_dll_directory(str(dll.parent))
    lua = ctypes.CDLL(str(dll))
    lua.luaL_newstate.restype = ctypes.c_void_p
    lua.luaL_loadbuffer.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p]
    lua.lua_tolstring.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
    lua.lua_tolstring.restype = ctypes.c_char_p
    lua.lua_settop.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lua.lua_close.argtypes = [ctypes.c_void_p]
    return lua


def check(root: Path) -> list[str]:
    sources = sorted((root / LUA).rglob("*.lua")) if (root / LUA).exists() else []
    if not sources:
        return []
    dll = pob_dir() / "lua51.dll"
    if not dll.exists():
        raise Skip(f"PoB's lua51.dll not found at {dll}")
    lua = _bind(dll)
    state = lua.luaL_newstate()
    problems = []
    try:
        for path in sources:
            data = path.read_bytes()
            if lua.luaL_loadbuffer(state, data, len(data), f"={path.name}".encode()) != 0:
                problems.append(f"{rel(root, path)}: {lua.lua_tolstring(state, -1, None).decode(errors='replace')}")
            lua.lua_settop(state, 0)
    finally:
        lua.lua_close(state)
    return problems
