"""Run the locally installed Path of Building headless via its own lua51.dll (LuaJIT)."""

import ctypes
import json
import os
import sys
from pathlib import Path

POB_DIR = Path(os.environ.get("POB_DIR", Path(os.environ["APPDATA"]) / "Path of Building Community"))
ENGINE_DIR = Path(__file__).resolve().parent
LUA_MULTRET = -1


class LuaError(RuntimeError):
    pass


class PobEngine:
    def __init__(self, pob_dir: Path = POB_DIR):
        if not (pob_dir / "Launch.lua").is_file():
            raise FileNotFoundError(f"Path of Building not found at {pob_dir}")
        (ENGINE_DIR / "userdata").mkdir(exist_ok=True)
        os.add_dll_directory(str(pob_dir))
        os.chdir(pob_dir)  # PoB loads its modules relative to the install dir
        self._lua = ctypes.CDLL(str(pob_dir / "lua51.dll"))
        self._bind()
        self._L = self._lua.luaL_newstate()
        self._lua.luaL_openlibs(self._L)
        self.run(f"ENGINE_DIR = {_lua_str(ENGINE_DIR.as_posix())}; POB_DIR = {_lua_str(pob_dir.as_posix())}")
        self.run(f"dofile(ENGINE_DIR .. '/pob_headless.lua')")

    def _bind(self):
        lua = self._lua
        lua.luaL_newstate.restype = ctypes.c_void_p
        lua.luaL_openlibs.argtypes = [ctypes.c_void_p]
        lua.luaL_loadbuffer.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p]
        lua.lua_pcall.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        lua.lua_tolstring.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_size_t)]
        lua.lua_tolstring.restype = ctypes.c_void_p
        lua.lua_settop.argtypes = [ctypes.c_void_p, ctypes.c_int]
        lua.lua_gettop.argtypes = [ctypes.c_void_p]

    def _top_string(self) -> str | None:
        size = ctypes.c_size_t()
        ptr = self._lua.lua_tolstring(self._L, -1, ctypes.byref(size))
        return None if not ptr else ctypes.string_at(ptr, size.value).decode("utf-8", "replace")

    def run(self, code: str) -> str | None:
        """Execute Lua code; returns the first return value as a string (if any)."""
        src = code.encode("utf-8")
        base = self._lua.lua_gettop(self._L)
        if self._lua.luaL_loadbuffer(self._L, src, len(src), b"=host") != 0 or \
                self._lua.lua_pcall(self._L, 0, LUA_MULTRET, 0) != 0:
            err = self._top_string()
            self._lua.lua_settop(self._L, base)
            raise LuaError(err)
        result = self._top_string() if self._lua.lua_gettop(self._L) > base else None
        self._lua.lua_settop(self._L, base)
        return result

    def load_build(self, xml_path: Path) -> dict:
        self.run(f"loadBuildFromFile({_lua_str(Path(xml_path).as_posix())})")
        return json.loads(self.run("return summaryJSON()"))


def _lua_str(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python pobhost.py <build.xml>")
    build_path = Path(sys.argv[1]).resolve()
    print(json.dumps(PobEngine().load_build(build_path), indent=2))
