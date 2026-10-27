-- The one file that loads code (check F7), in a fixed order. pob/lua_host.py runs it once with four absolute folders
-- and keeps the function it returns: every request after boot goes through that dispatcher (rpc.lua).
-- The working folder is PoB's install (pob/session.py), so PoB's own files load by relative path.
local luaDir, pobDir, userDir, writeRoot = ...

local function run(name, ...)
	return assert(loadfile(luaDir .. "/" .. name))(...)
end

run("vendor/_SimpleGraphic.def.lua") -- PoB's runtime API with headless bodies (vendor/README.md)
run("filesearch.lua") -- real file search over the stub's: PoB needs it for timeless jewels
local sandbox = run("sandbox.lua", pobDir, userDir, writeRoot) -- before any PoB code: refuses writes outside the roots
local host = run("boot.lua", pobDir, userDir) -- the rest of the host functions, real zlib, package paths
dofile("Launch.lua") -- PoB itself
host.start()
sandbox.seal() -- PoB is loaded: hide the debug functions that would reach the sandbox's originals

local dkjson = require("dkjson")
local Rpc = run("rpc.lua", dkjson)
local Build = run("build.lua", Rpc, host)
local Scenario = run("analysis/scenario.lua", Rpc, Build)
run("analysis/chain.lua", Rpc, Build, Scenario)
return Rpc.dispatch
