"""Run the locally installed Path of Building headless via its own lua51.dll (LuaJIT)."""

import ctypes
import json
import os
import sys
from pathlib import Path

POB_DIR = Path(os.environ.get("POB_DIR", Path(os.environ["APPDATA"]) / "Path of Building Community"))
ENGINE_DIR = Path(__file__).resolve().parent
# The only folder (besides the engine's userdata and PoB's timeless cache) the Lua state may write to.
AUTOBUILDER_DIR = Path.home() / "Documents" / "Path of Building" / "Builds" / "AutoBuilder"
LUA_MULTRET = -1
LUA_GLOBALSINDEX = -10002
LUA_REGISTRYINDEX = -10000


class LuaError(RuntimeError):
    pass


class PobEngine:
    def __init__(self, pob_dir: Path = POB_DIR, userdata_dir: Path | None = None,
                 autobuilder_dir: Path | None = None):
        if not (pob_dir / "Launch.lua").is_file():
            raise FileNotFoundError(f"Path of Building not found at {pob_dir}")
        userdata_dir = Path(userdata_dir) if userdata_dir is not None else ENGINE_DIR / "userdata"
        userdata_dir.mkdir(parents=True, exist_ok=True)
        autobuilder_dir = Path(autobuilder_dir) if autobuilder_dir is not None else AUTOBUILDER_DIR
        os.add_dll_directory(str(pob_dir))
        os.chdir(pob_dir)  # PoB loads its modules relative to the install dir
        self._lua = ctypes.CDLL(str(pob_dir / "lua51.dll"))
        self._bind()
        self._L = None
        self._traceback_ref = None
        try:
            self._L = self._lua.luaL_newstate()
            if self._L is None:
                raise LuaError("could not create Lua state")
            self._lua.luaL_openlibs(self._L)
            self._lua.lua_getfield(self._L, LUA_GLOBALSINDEX, b"debug")
            self._lua.lua_getfield(self._L, -1, b"traceback")
            self._lua.lua_remove(self._L, -2)
            self._traceback_ref = self._lua.luaL_ref(self._L, LUA_REGISTRYINDEX)
            self.run(f"ENGINE_DIR = {_lua_str(ENGINE_DIR.as_posix())}; "
                     f"POB_DIR = {_lua_str(pob_dir.as_posix())}; "
                     f"USERDATA_DIR = {_lua_str(userdata_dir.as_posix())}; "
                     f"AUTOBUILDER_DIR = {_lua_str(autobuilder_dir.as_posix())}")
            self.run(f"dofile(ENGINE_DIR .. '/pob_headless.lua')")
        except BaseException:
            self.close()
            raise

    def _bind(self):
        lua = self._lua
        lua.luaL_newstate.restype = ctypes.c_void_p
        lua.luaL_openlibs.argtypes = [ctypes.c_void_p]
        lua.luaL_loadbuffer.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p]
        lua.luaL_loadbuffer.restype = ctypes.c_int
        lua.lua_pcall.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int]
        lua.lua_pcall.restype = ctypes.c_int
        lua.lua_tolstring.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_size_t)]
        lua.lua_tolstring.restype = ctypes.c_void_p
        lua.lua_settop.argtypes = [ctypes.c_void_p, ctypes.c_int]
        lua.lua_gettop.argtypes = [ctypes.c_void_p]
        lua.lua_gettop.restype = ctypes.c_int
        lua.lua_getfield.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p]
        lua.lua_getfield.restype = None
        lua.lua_remove.argtypes = [ctypes.c_void_p, ctypes.c_int]
        lua.lua_remove.restype = None
        lua.luaL_ref.argtypes = [ctypes.c_void_p, ctypes.c_int]
        lua.luaL_ref.restype = ctypes.c_int
        lua.lua_rawgeti.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        lua.lua_rawgeti.restype = None
        lua.lua_close.argtypes = [ctypes.c_void_p]
        lua.lua_close.restype = None

    def _stack_string(self, index: int) -> str | None:
        size = ctypes.c_size_t()
        ptr = self._lua.lua_tolstring(self._L, index, ctypes.byref(size))
        return None if not ptr else ctypes.string_at(ptr, size.value).decode("utf-8", "replace")

    @property
    def closed(self) -> bool:
        return self._L is None

    def close(self) -> None:
        if self._L is not None:
            state, self._L = self._L, None
            self._lua.lua_close(state)
            self._traceback_ref = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def run(self, code: str) -> str | None:
        """Execute Lua code; returns the first return value as a string (if any)."""
        if self.closed:
            raise LuaError("engine is closed")
        src = code.encode("utf-8")
        base = self._lua.lua_gettop(self._L)
        self._lua.lua_rawgeti(self._L, LUA_REGISTRYINDEX, self._traceback_ref)
        handler = base + 1
        if self._lua.luaL_loadbuffer(self._L, src, len(src), b"=host") != 0:
            err = self._stack_string(-1)
            self._lua.lua_settop(self._L, base)
            raise LuaError(err)
        if self._lua.lua_pcall(self._L, 0, LUA_MULTRET, handler) != 0:
            err = self._stack_string(-1)
            self._lua.lua_settop(self._L, base)
            raise LuaError(err)
        result = self._stack_string(base + 2) if self._lua.lua_gettop(self._L) > handler else None
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
