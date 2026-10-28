-- The build endpoints (docs/ARCHITECTURE.md, "Endpoints"): open a build from its XML text, read its summary and its
-- whole state. Rewrites the first app's engine/pob_headless.lua:75-112, which never looked at PoB's error prompt: a
-- broken file "loaded" and showed the previous build's numbers under the new name (task 102, area A, measured).
-- Returns what the other endpoint files share: the open build, recalculate(), the summary.
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
local target = nil -- the target build, PoB's CompareEntry (compare/target.lua); nil when none is loaded

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

-- A build by its handle: "own" (or nil) is the build open in PoB's build mode, "target" the CompareEntry beside it.
local function openBuild(which)
	if which == "target" then
		if not target then Rpc.fail("NoTarget", "no target is loaded: none was loaded yet, or the last load failed") end
		return target
	end
	if which ~= nil and which ~= "own" then
		Rpc.fail("BadRequest", "which is \"own\" or \"target\", got " .. tostring(which))
	end
	if not loaded then Rpc.fail("NoBuild", "no build is open: none was loaded yet, or the last load failed") end
	return main.modes.BUILD
end

-- compare/target.lua sets the target after a load that succeeded and clears it on every other path.
local function setTarget(entry)
	target = entry
end

-- PoB's own recalculation, as the GUI runs it after any change: flag the build and run one frame. The frame's build
-- step (Build.lua:1258-1273) wipes the global calculation cache, updates the socket groups, rebuilds the output,
-- refreshes the stat list (which sorts SkillDPS, Build.lua:1934) and the config tab's calculator. Calling those
-- steps by hand skipped the last two (measured on CoC EK Assa: SkillDPS came back in another order). No path of the
-- first app did the first three (task 102, area A Q5). Every change to a build goes through here.
local function recalculate(build)
	if build == target then
		-- The target is not in build mode, so no frame reaches it: PoB's compare tab recalculates an entry with
		-- CompareEntry:Rebuild (CompareEntry.lua:250-256: global cache wipe, socket groups, BuildOutput).
		build:Rebuild()
		return
	end
	launch.promptMsg = nil
	build.buildFlag = true
	host.frame()
	-- PoB catches an error inside a frame and shows it as a prompt (Launch.lua:112-118).
	local prompt = launch.promptMsg
	launch.promptMsg = nil
	if prompt then error("PoB failed to recalculate: " .. promptText(prompt), 0) end
	if build.buildFlag or main.modes.BUILD ~= build then error("PoB did not recalculate the build", 0) end
end

local function mainSkillName(build)
	local group = build.skillsTab.socketGroupList[build.mainSocketGroup]
	local skill = group and group.displaySkillList and group.displaySkillList[group.mainActiveSkill or 1]
	return skill and skill.activeEffect.grantedEffect.name or nil
end

-- Whether PoB's Calcs tab follows the sidebar's main skill as saved: its group, active skill and part (CalcSetup.lua
-- :1585-1587, 1883; CalcActiveSkill.lua:251). The chain points it there for its read (decision 023); the owner may look
-- at another skill when he opens the Calcs tab in PoB.
local function calcsOnMainSkill(build)
	local group = build.skillsTab.socketGroupList[build.mainSocketGroup]
	if not group then return true end
	local skill = group.displaySkillList and group.displaySkillList[group.mainActiveSkill or 1]
	local source = skill and skill.activeEffect.srcInstance or {}
	return (build.calcsTab.input.skill_number or 1) == build.mainSocketGroup
		and (group.mainActiveSkillCalcs or 1) == (group.mainActiveSkill or 1)
		and (source.skillPartCalcs or 1) == (source.skillPart or 1)
end

-- PoB's Full DPS list: one row per skill, mirage, minion or damage over time it adds up (Calcs.lua:179, 217, 254,
-- 309-349).
local function skillDps(output)
	local rows = {}
	for index, skill in ipairs(output.SkillDPS or {}) do
		rows[index] = { name = skill.name, dps = skill.dps, count = skill.count, part = skill.skillPart }
	end
	return rows
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
		calcsOnMainSkill = calcsOnMainSkill(build),
		skillDps = skillDps(output),
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

local SCALARS = { string = true, number = true, boolean = true }

local function scalars(tbl)
	local copy = {}
	for key, value in pairs(tbl) do
		if SCALARS[type(value)] then copy[key] = value end
	end
	return copy
end

-- Every field of every socket group and gem: the sidebar's skill selection and the Calcs tab's own among them
-- (mainActiveSkill(Calcs), skillPart(Calcs), skillStageCount(Calcs), skillMinion(Calcs), ...; CalcsTab.lua:46-92,
-- CompareEntry.lua:229-248), which PoB also writes while it recalculates (CalcActiveSkill.lua:251, 629, 697, 738, 926).
local function skillFields(build)
	local groups = {}
	for index, group in ipairs(build.skillsTab.socketGroupList) do
		local gems = {}
		for gemIndex, gem in ipairs(group.gemList) do gems[gemIndex] = scalars(gem) end
		groups[index] = { fields = scalars(group), gems = gems }
	end
	return { mainSocketGroup = build.mainSocketGroup, groups = groups }
end

-- A change's undo for fields it cannot list ahead: saves every field of each table that is not a table and returns
-- the function that puts them back; a value written meanwhile is set back, a field added meanwhile is removed.
local function keepFields(tables)
	local saved = {}
	for index, tbl in ipairs(tables) do
		local copy = {}
		for key, value in pairs(tbl) do
			if type(value) ~= "table" then copy[key] = value end
		end
		saved[index] = copy
	end
	return function()
		for index, tbl in ipairs(tables) do
			local copy = saved[index]
			for key, value in pairs(tbl) do
				if type(value) ~= "table" and copy[key] == nil then tbl[key] = nil end
			end
			for key, value in pairs(copy) do tbl[key] = value end
		end
	end
end

-- What tests/comparison_app/pob/test_every_endpoint_restores.py compares (M6): every number of both PoB calculations
-- (the sidebar's and the Calcs tab's), the config inputs and placeholders (the boss box sets placeholders of other
-- boxes, ConfigOptions.lua:2086-2100), the Calcs tab's inputs and the fields of every skill group and gem.
Rpc.register("build.state", function(request)
	local build = openBuild(request.which)
	return {
		output = numbers(build.calcsTab.mainOutput, "", {}, STATE_DEPTH),
		calcsOutput = numbers(build.calcsTab.calcsOutput, "", {}, STATE_DEPTH),
		config = scalars(build.configTab.input),
		placeholder = scalars(build.configTab.placeholder),
		calcs = scalars(build.calcsTab.input),
		skills = skillFields(build),
	}
end)

-- Runs read(build) with every change applied and the build recalculated once, then undoes the changes newest first
-- and recalculates, on every path (the first app's guide.lua:188-207 shape). A change is a function(build) that
-- applies itself and returns its undo. If undoing fails, no build counts as open: its state is unknown.
local function withChanges(changes, read, which)
	local build = openBuild(which)
	local undos = {}
	local ok, result = xpcall(function()
		for _, change in ipairs(changes) do
			undos[#undos + 1] = change(build)
		end
		recalculate(build)
		return read(build)
	end, Rpc.asError)
	local restored, problem = xpcall(function()
		for index = #undos, 1, -1 do
			undos[index](build)
		end
		recalculate(build)
	end, Rpc.asError)
	if not restored then
		if build == target then target = nil else loaded = false end
		Rpc.fail("BuildNotRestored", "PoB could not put the build back, load it again: " .. tostring(problem.message))
	end
	if not ok then error(result, 0) end
	return result
end

return {
	open = openBuild, summary = summary, withChanges = withChanges, keepFields = keepFields, setTarget = setTarget,
	-- every number of a PoB output, as build.state reads it
	outputNumbers = function(output) return numbers(output, "", {}, STATE_DEPTH) end,
}
