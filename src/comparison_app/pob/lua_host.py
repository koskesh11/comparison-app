"""The one Lua state, on PoB's own lua51.dll (LuaJIT 2.1) through ctypes (docs/ARCHITECTURE.md, "How src/ calls PoB").

Only this module touches the Lua C API (check F6). It runs fixed Lua files and passes requests to the dispatcher the
boot file returns; it never turns Python strings into Lua code, so nothing needs escaping. One Lua state must not be
used by two threads at once, so every use holds the lock. Replaces the first app's engine/pobhost.py :84-188.
"""

import ctypes
import os
import threading
from pathlib import Path

from comparison_app.errors import PobError

LUA_REGISTRYINDEX = -10000
LUA_GLOBALSINDEX = -10002
LUA_TSTRING = 4
LUA_TFUNCTION = 6
STACK_SLOTS = 8  # the most a call pushes: traceback handler, chunk or dispatcher, and its arguments


def _bind(lua: ctypes.CDLL) -> ctypes.CDLL:
    state, text, size, number = ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t, ctypes.c_int
    signatures: dict[str, tuple[list[type], type | None]] = {
        "luaL_newstate": ([], state),
        "luaL_openlibs": ([state], None),
        "luaL_loadbuffer": ([state, text, size, text], number),
        "lua_pcall": ([state, number, number, number], number),
        "lua_tolstring": ([state, number, ctypes.POINTER(size)], ctypes.c_void_p),
        "lua_pushlstring": ([state, text, size], None),
        "lua_settop": ([state, number], None),
        "lua_gettop": ([state], number),
        "lua_checkstack": ([state, number], number),
        "lua_type": ([state, number], number),
        "lua_typename": ([state, number], text),
        "lua_getfield": ([state, number, text], None),
        "lua_remove": ([state, number], None),
        "lua_rawgeti": ([state, number, number], None),
        "luaL_ref": ([state, number], number),
        "lua_close": ([state], None),
    }
    for name, (argtypes, restype) in signatures.items():
        function = getattr(lua, name)
        function.argtypes = argtypes
        function.restype = restype
    return lua


class LuaHost:
    """A Lua state with Lua's standard libraries; `start` boots a dispatcher, `call` sends it requests."""

    def __init__(self, dll: Path) -> None:
        self._dll_dir = os.add_dll_directory(str(dll.parent))
        try:
            self._lua = _bind(ctypes.CDLL(str(dll)))
            state = self._lua.luaL_newstate()
            if not state:
                raise PobError("could not create a Lua state")
        except BaseException:
            self._dll_dir.close()
            raise
        self._lock = threading.Lock()
        self._dispatcher: int | None = None
        self._state: int | None = state
        self._lua.luaL_openlibs(state)
        # Keep Lua's own traceback function: the boot later hides most of the debug library (sandbox.lua seal).
        self._lua.lua_getfield(state, LUA_GLOBALSINDEX, b"debug")
        self._lua.lua_getfield(state, -1, b"traceback")
        self._lua.lua_remove(state, -2)
        self._traceback: int = self._lua.luaL_ref(state, LUA_REGISTRYINDEX)

    @property
    def closed(self) -> bool:
        return self._state is None

    def close(self) -> None:
        with self._lock:
            if self._state is not None:
                state, self._state = self._state, None
                self._lua.lua_close(state)
                self._dll_dir.close()

    def run_file(self, path: Path, *args: str) -> str | None:
        """Run a Lua file with text arguments; returns its first result when that is text."""
        with self._lock:
            state, base = self._run(path, args)
            result = self._text(state, -1)
            self._lua.lua_settop(state, base)
            return result

    def start(self, path: Path, *args: str) -> None:
        """Run the boot file; the function it returns answers every later `call`."""
        with self._lock:
            state, base = self._run(path, args)
            if self._lua.lua_type(state, -1) != LUA_TFUNCTION:
                self._lua.lua_settop(state, base)
                raise PobError(f"{path.name} returned no dispatcher function")
            self._dispatcher = self._lua.luaL_ref(state, LUA_REGISTRYINDEX)
            self._lua.lua_settop(state, base)

    def call(self, name: str, payload: bytes) -> bytes:
        """Send one request to the dispatcher: `dispatch(name, payload)` must answer with text."""
        with self._lock:
            state = self._open()
            if self._dispatcher is None:
                raise PobError("the Lua state is not booted")
            base = self._prepare(state)
            self._lua.lua_rawgeti(state, LUA_REGISTRYINDEX, self._dispatcher)
            for argument in (name.encode("utf-8"), payload):
                self._lua.lua_pushlstring(state, argument, len(argument))
            self._pcall(state, base, 2)
            reply = self._bytes(state, -1)
            self._lua.lua_settop(state, base)
            if reply is None:
                raise PobError(f"the dispatcher answered {name} with something other than text")
            return reply

    def _open(self) -> int:
        if self._state is None:
            raise PobError("the Lua state is closed")
        return self._state

    def _prepare(self, state: int) -> int:
        """Room on the stack and the traceback handler at base + 1; returns base."""
        if not self._lua.lua_checkstack(state, STACK_SLOTS):
            raise PobError("the Lua stack is full")
        base: int = self._lua.lua_gettop(state)
        self._lua.lua_rawgeti(state, LUA_REGISTRYINDEX, self._traceback)
        return base

    def _run(self, path: Path, args: tuple[str, ...]) -> tuple[int, int]:
        """Load a file and call it with `args`; its first result stays on top of the stack."""
        state = self._open()
        try:
            source = path.read_bytes()
        except OSError as error:
            raise PobError(f"cannot read {path}: {error}") from error
        base = self._prepare(state)
        if self._lua.luaL_loadbuffer(state, source, len(source), f"@{path.name}".encode()) != 0:
            message = self._text(state, -1) or "unreadable load error"
            self._lua.lua_settop(state, base)
            raise PobError(f"{path.name} does not compile: {message}")
        for argument in args:
            data = argument.encode("utf-8")
            self._lua.lua_pushlstring(state, data, len(data))
        self._pcall(state, base, len(args))
        return state, base

    def _pcall(self, state: int, base: int, nargs: int) -> None:
        if self._lua.lua_pcall(state, nargs, 1, base + 1) != 0:
            message = self._text(state, -1)
            if message is None:
                kind = self._lua.lua_typename(state, self._lua.lua_type(state, -1)).decode()
                message = f"a Lua error that is not text (a {kind})"
            self._lua.lua_settop(state, base)
            # debug.traceback appends "\nstack traceback:..." to the message; the message itself may span lines.
            text, marker, stack = message.rpartition("\nstack traceback:")
            raise PobError(text, traceback=marker.lstrip("\n") + stack) if marker else PobError(message)

    def _bytes(self, state: int, index: int) -> bytes | None:
        if self._lua.lua_type(state, index) != LUA_TSTRING:
            return None
        size = ctypes.c_size_t()
        pointer = self._lua.lua_tolstring(state, index, ctypes.byref(size))
        return ctypes.string_at(pointer, size.value)

    def _text(self, state: int, index: int) -> str | None:
        data = self._bytes(state, index)
        return None if data is None else data.decode("utf-8", "replace")
