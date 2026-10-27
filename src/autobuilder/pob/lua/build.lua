-- The build endpoints (docs/ARCHITECTURE.md, "Endpoints"): open a build from its XML text, read its summary and its
-- whole state. Rewrites the first app's engine/pob_headless.lua:75-112, which never looked at PoB's error prompt: a
-- broken file "loaded" and showed the previous build's numbers under the new name (task 102, area A, measured).
local Rpc, host = ...

-- The summary's PoB output keys (the first app's summaryJSON, pob_headless.lua:87-93).
local SUMMARY_STATS = {
	"FullDPS", "CombinedDPS", "TotalDPS", "TotalDotDPS",
	"CritChance", "HitChance", "Speed",
	"Life", "EnergyShield", "Mana",
	"FireResist", "ColdResist", "LightningResist", "ChaosResist",
	"PhysicalMaximumHitTaken", "TotalEHP",
}
local STATE_DEPTH = 2 -- build.state reads numbers this many tables deep into PoB's main output

local loaded = false -- a build is open and PoB reported no error for it; reads refuse otherwise

-- PoB's error prompt (Launch.lua:381-388) without colour codes, the version line and the key help.
local function promptText(message)
	local plain = message:gsub("%^x%x%x%x%x%x%x", ""):gsub("%^%d", "")
	local lines = {}
	for line in (plain .. "\n"):gmatch("([^\n]*)\n") do
		if line ~= "" and line ~= "Error:" and not line:match("^v%d") and not line:match("^Press ") then
			lines[#lines + 1] = line
		end
	end
	return table.concat(lines, "\n")
end

local function openBuild()
	if not loaded then Rpc.fail("NoBuild", "no build is open: none was loaded yet, or the last load failed") end
	return main.modes.BUILD
end

local function mainSkillName(build)
	local group = build.skillsTab.socketGroupList[build.mainSocketGroup]
	local skill = group and group.displaySkillList and group.displaySkillList[group.mainActiveSkill or 1]
	return skill and skill.activeEffect.grantedEffect.name or nil
end

local function summary(build)
	local output, stats = build.calcsTab.mainOutput, {}
	for _, key in ipairs(SUMMARY_STATS) do
		stats[key] = output[key]
	end
	return {
		pobVersion = launch.versionNumber,
		buildName = build.buildName,
		className = build.spec.curClassName,
		ascendancy = build.spec.curAscendClassName,
		level = build.characterLevel,
		mainSkill = mainSkillName(build),
		stats = stats,
	}
end

-- Every number in `tbl`, `depth` tables deep, under dotted keys ("MainHand.Accuracy").
local function numbers(tbl, prefix, into, depth)
	for key, value in pairs(tbl) do
		if type(value) == "number" then
			into[prefix .. tostring(key)] = value
		elseif type(value) == "table" and depth > 0 then
			numbers(value, prefix .. tostring(key) .. ".", into, depth - 1)
		end
	end
	return into
end

Rpc.register("build.load", function(request)
	loaded = false -- every failure below, the request's own included, leaves no build open
	if type(request.xml) ~= "string" or type(request.name) ~= "string" then
		Rpc.fail("BadRequest", "build.load needs the build's xml and name as text")
	end
	-- PoB reports a bad build only through its prompt (Build.lua:2222-2236) and keeps the first prompt until it is
	-- dismissed (Launch.lua:382), so an old one would hide this load's result.
	launch.promptMsg = nil
	wipeTable(main.popups)
	main:SetMode("BUILD", false, request.name, request.xml)
	host.frame()
	if launch.promptMsg then Rpc.fail("BuildNotLoaded", promptText(launch.promptMsg)) end
	if main.mode ~= "BUILD" then Rpc.fail("BuildNotLoaded", "PoB did not open the build") end
	-- A dialog means PoB stopped half way, for example to convert a build made for an older game version
	-- (Build.lua:104-108).
	if main.popups[1] then Rpc.fail("BuildNotLoaded", "PoB opened a dialog instead of the build") end
	local opened = summary(main.modes.BUILD)
	loaded = true
	return opened
end)

Rpc.register("build.summary", function()
	return summary(openBuild())
end)

-- What tests/autobuilder/pob/test_every_endpoint_restores.py compares (M6): every number of PoB's main output, the
-- config inputs and the main skill selection.
Rpc.register("build.state", function()
	local build = openBuild()
	local config = {}
	for key, value in pairs(build.configTab.input) do
		if type(value) ~= "table" then config[key] = value end
	end
	local group = build.skillsTab.socketGroupList[build.mainSocketGroup]
	return {
		output = numbers(build.calcsTab.mainOutput, "", {}, STATE_DEPTH),
		config = config,
		mainSocketGroup = build.mainSocketGroup,
		mainActiveSkill = group and group.mainActiveSkill,
	}
end)
