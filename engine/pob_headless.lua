-- Boots the locally installed Path of Building headless.
-- Adapted from PoB's src/HeadlessWrapper.lua. Expects:
--   cwd          = PoB install dir (Launch.lua, Modules/, Data/ ...)
--   ENGINE_DIR   = this folder (global, set by the host)

dofile(ENGINE_DIR .. "/_SimpleGraphic.def.lua")
dofile(ENGINE_DIR .. "/filesearch.lua")

local POB_DIR = POB_DIR
-- Keep PoB's user data (Settings.xml) out of the install and out of Documents.
function GetScriptPath() return POB_DIR end
function GetRuntimePath() return POB_DIR end
function GetUserPath() return USERDATA_DIR or (ENGINE_DIR .. "/userdata") end
function GetVirtualScreenSize() return 1920, 1080 end
arg = arg or {} -- Main.lua reads command-line args

-- Real zlib Inflate/Deflate (timeless jewel LUTs, build codes) via PoB's bundled zlib1.dll.
local ffi = require("ffi")
ffi.cdef [[
	unsigned long compressBound(unsigned long sourceLen);
	int compress2(uint8_t *dest, unsigned long *destLen, const uint8_t *source, unsigned long sourceLen, int level);
	int uncompress(uint8_t *dest, unsigned long *destLen, const uint8_t *source, unsigned long sourceLen);
]]
local zlib = ffi.load(POB_DIR .. "/zlib1.dll")
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

__callbackTable__ = {}
function runCallback(name, ...)
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

dofile("Launch.lua")
__mainObject__.continuousIntegrationMode = false
runCallback("OnInit")
runCallback("OnFrame")
if __mainObject__.promptMsg then
	error("PoB startup failed: " .. tostring(__mainObject__.promptMsg))
end

build = __mainObject__.main.modes["BUILD"]

local dkjson = require("dkjson")

function loadBuildFromFile(path)
	local f = assert(io.open(path, "rb"))
	local xmlText = f:read("*a")
	f:close()
	__mainObject__.main:SetMode("BUILD", false, path:match("([^/\\]+)%.xml$") or "", xmlText)
	runCallback("OnFrame")
	build = __mainObject__.main.modes["BUILD"]
end

local SUMMARY_STATS = {
	"FullDPS", "CombinedDPS", "TotalDPS", "TotalDotDPS",
	"CritChance", "HitChance", "Speed",
	"Life", "EnergyShield", "Mana",
	"FireResist", "ColdResist", "LightningResist", "ChaosResist",
	"PhysicalMaximumHitTaken", "TotalEHP",
}

function summaryJSON()
	local out = build.calcsTab.mainOutput
	local stats = {}
	for _, key in ipairs(SUMMARY_STATS) do
		stats[key] = out[key]
	end
	local group = build.skillsTab.socketGroupList[build.mainSocketGroup]
	local skill = group and group.displaySkillList and group.displaySkillList[group.mainActiveSkill or 1]
	return dkjson.encode({
		pobVersion = launch.versionNumber,
		buildName = build.buildName,
		className = build.spec.curClassName,
		ascendancy = build.spec.curAscendClassName,
		level = build.characterLevel,
		mainSkill = skill and skill.activeEffect.grantedEffect.name or nil,
		stats = stats,
	})
end
