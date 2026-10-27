-- PoB's host functions for a headless Lua state (the first app's engine/pob_headless.lua:1-74, adapted from PoB's
-- src/HeadlessWrapper.lua). loader.lua runs it after the vendored runtime stub and before Launch.lua, with PoB's
-- folder and this session's user-data folder. It returns `start` (PoB's first frame; raises on a startup error) and
-- `frame` (one more frame, which is how PoB opens a build).
-- The globals below are host functions PoB calls by name; tools/checks/lua_rules.py lists them.
local pobDir, userDir = ...

-- Keep PoB's user data (Settings.xml) out of the install and out of Documents.
function GetScriptPath() return pobDir end
function GetRuntimePath() return pobDir end
function GetUserPath() return userDir end
function GetVirtualScreenSize() return 1920, 1080 end
arg = arg or {} -- Main.lua reads command-line args

-- Real zlib Inflate/Deflate (timeless jewel LUTs, build codes) via PoB's bundled zlib1.dll.
local ffi = require("ffi")
ffi.cdef [[
	unsigned long compressBound(unsigned long sourceLen);
	int compress2(uint8_t *dest, unsigned long *destLen, const uint8_t *source, unsigned long sourceLen, int level);
	int uncompress(uint8_t *dest, unsigned long *destLen, const uint8_t *source, unsigned long sourceLen);
]]
local zlib = ffi.load(pobDir .. "/zlib1.dll")
local Z_OK, Z_BUF_ERROR = 0, -5

function Deflate(data)
	local destLen = ffi.new("unsigned long[1]", zlib.compressBound(#data))
	local dest = ffi.new("uint8_t[?]", destLen[0])
	if zlib.compress2(dest, destLen, data, #data, 9) ~= Z_OK then return nil, "deflate failed" end
	return ffi.string(dest, destLen[0])
end

function Inflate(data)
	local size = math.max(#data * 8, 1024)
	while true do
		local destLen = ffi.new("unsigned long[1]", size)
		local dest = ffi.new("uint8_t[?]", size)
		local rc = zlib.uncompress(dest, destLen, data, #data)
		if rc == Z_OK then return ffi.string(dest, destLen[0]) end
		if rc ~= Z_BUF_ERROR then return nil, "inflate failed (" .. rc .. ")" end
		size = size * 4
	end
end

package.path = "lua/?.lua;lua/?/init.lua;" .. package.path
package.cpath = "?.dll;" .. package.cpath

__callbackTable__ = {} -- read and written by the stub's SetCallback / GetCallback

local function runCallback(name, ...)
	if __callbackTable__[name] then
		return __callbackTable__[name](...)
	elseif __mainObject__ and __mainObject__[name] then
		return __mainObject__[name](__mainObject__, ...)
	end
end

local l_require = require
function require(name)
	if name == "lcurl.safe" then return end -- no network needed
	return l_require(name)
end

local function start()
	__mainObject__.continuousIntegrationMode = false
	runCallback("OnInit")
	runCallback("OnFrame")
	if __mainObject__.promptMsg then
		error("PoB startup failed: " .. tostring(__mainObject__.promptMsg))
	end
end

local function frame()
	runCallback("OnFrame")
end

return { start = start, frame = frame }
