-- The skill settings and config of the build or the target (`which`), for the differences card 110 shows (decisions
-- 010, 011). Rewrites the first app's guide_snapshot.lua :64-106, 141-207: the settings PoB saves and uses (stages,
-- mines, minion, group count, enableGlobal, the Calcs selection; SkillsTab.lua:449, 503-513; Calcs.lua:119-127) were
-- missing, and config defaults were worked out by hand instead of PoB's GetDefaultState (ConfigTab.lua:941-948).
local Rpc, Build = ...

local CONFIG_OPTIONS = require("Modules.ConfigOptions") -- the list PoB's config tab is built from (ConfigTab.lua:12)
local GROUP_FIELDS = { "label", "displayLabel", "slot", "source", "enabled", "includeInFullDPS", "groupCount",
	"mainActiveSkill", "mainActiveSkillCalcs" }
local GEM_FIELDS = { "nameSpec", "enabled", "enableGlobal1", "enableGlobal2", "level", "quality", "count",
	"skillPart", "skillPartCalcs", "skillStageCount", "skillStageCountCalcs", "skillMineCount", "skillMineCountCalcs",
	"skillMinion", "skillMinionCalcs", "skillMinionSkill", "skillMinionSkillCalcs" }

local function fields(tbl, names)
	local copy = {}
	for _, name in ipairs(names) do copy[name] = tbl[name] end
	return copy
end

local function indexOf(list, item)
	for index, each in ipairs(list) do
		if each == item then return index end
	end
	return nil
end

-- The active skills PoB made of a group (CalcSetup.lua:1910), each with its gem and the name of its part.
local function activeSkills(group)
	local found = {}
	for index, skill in ipairs(group.displaySkillList or {}) do
		local effect = skill.activeEffect
		local parts = effect.grantedEffect.parts
		found[index] = {
			name = effect.grantedEffect.name, gem = indexOf(group.gemList, effect.srcInstance),
			part = skill.skillPart and parts and parts[skill.skillPart] and parts[skill.skillPart].name,
		}
	end
	return found
end

local function groups(build)
	local found = {}
	for index, group in ipairs(build.skillsTab.socketGroupList) do
		local gems = {}
		for gemIndex, gem in ipairs(group.gemList) do
			-- a gem's effect is its gem data's; an item-granted skill carries it on the gem itself (SkillsTab.lua:1186, 1371)
			local effect = gem.gemData and gem.gemData.grantedEffect or gem.grantedEffect
			gems[gemIndex] = fields(gem, GEM_FIELDS)
			gems[gemIndex].name = effect and effect.name or gem.nameSpec
			gems[gemIndex].support = effect and effect.support == true or false
		end
		found[index] = { fields = fields(group, GROUP_FIELDS), gems = gems, skills = activeSkills(group) }
	end
	return found
end

-- PoB colours a box that is set: red when the build cannot use it, blue when it can (ConfigTab.lua:697-708); boxes
-- marked doNotHighlight have no colour, so they count as usable.
local function boxState(control, value, default)
	if value == nil or value == default then return "default" end
	if not (control and control.borderFunc) then return "set" end
	local red, green = control.borderFunc()
	return red > green and "unusable" or "set"
end

-- Every config box that is not at PoB's default, in PoB's list order, with its section.
local function config(configTab)
	local set = configTab.configSets[configTab.activeConfigSetId]
	local rows, section = {}, nil
	for _, entry in ipairs(CONFIG_OPTIONS) do
		if entry.section then section = entry.section end
		if entry.var then
			local value = set.input[entry.var]
			local default = configTab:GetDefaultState(entry.var, type(value))
			local state = boxState(configTab.varControls[entry.var], value, default)
			if state ~= "default" or set.placeholder[entry.var] ~= nil then
				rows[#rows + 1] = {
					var = entry.var, section = section, label = type(entry.label) == "string" and entry.label or entry.var,
					type = entry.type, value = value, placeholder = set.placeholder[entry.var], state = state,
				}
			end
		end
	end
	local custom = {}
	for _, block in ipairs(set.customModsList or {}) do
		if tostring(block.text or ""):match("%S") then
			custom[#custom + 1] = { title = block.title, enabled = block.enabled ~= false, text = block.text }
		end
	end
	local titles = {}
	for index, id in ipairs(configTab.configSetOrderList) do titles[index] = configTab.configSets[id].title or "Default" end
	return { rows = rows, customMods = custom, sets = titles, activeSet = set.title or "Default" }
end

Rpc.register("compare.snapshot", function(request)
	local build = Build.open(request.which)
	return {
		mainSocketGroup = build.mainSocketGroup, calcsSkillNumber = build.calcsTab.input.skill_number,
		groups = groups(build), config = config(build.configTab),
	}
end)
