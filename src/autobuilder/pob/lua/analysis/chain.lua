-- The damage chain of the main skill (decisions 009, 023): the rows of four PoB Calcs tab sections in PoB's order, each
-- cell with PoB's own text, the raw numbers it shows and its sources as PoB's hover popup lists them. Nothing here
-- computes a game number: rows and show conditions are CalcSections.lua with CalcsTab:CheckFlag, the text is
-- formatCalcStr (CalcFormat.lua:16-74), the sources are CalcBreakdownControl (CalcBreakdownControl.lua:60-527).
-- Grouping the rows into the mockup's steps and the gaps come later (compare/chain_table.py).
local Rpc, Build, Scenario = ...

-- Skill Hit Damage, Attack/Cast Rate, Crits, Accuracy (CalcSections.lua:105, 575, 605, 939).
local SECTIONS = { "HitDamage", "Speed", "Crit", "HitChance" }
local DAMAGE_TYPES = { "Physical", "Lightning", "Cold", "Fire", "Chaos" }
local TOTALS = { "AverageHit", "AverageDamage", "TotalDPS", "Speed", "HitSpeed", "HitChance", "CritChance",
	"CritMultiplier", "CritEffect" }

local function plain(text)
	return (tostring(text):gsub("%^x%x%x%x%x%x%x", ""):gsub("%^%d", ""))
end

-- The Calcs tab's selection pointed at the sidebar's main skill for one read (decision 023): the fields CALCS mode
-- reads instead of the sidebar's (CalcSetup.lua:564-567, 1585-1587, 1883; CalcActiveSkill.lua:251, 623, 649).
local function calcsOnMainSkill(build)
	local calcs = build.calcsTab.input
	local group = build.skillsTab.socketGroupList[build.mainSocketGroup]
	local skill = group and group.displaySkillList and group.displaySkillList[group.mainActiveSkill or 1]
	if not skill then Rpc.fail("NoMainSkill", "the build has no main skill in its sidebar") end
	local source = skill.activeEffect.srcInstance
	local before = {
		number = calcs.skill_number, mode = calcs.misc_buffMode, minion = calcs.showMinion,
		active = group.mainActiveSkillCalcs, part = source.skillPartCalcs, stages = source.skillStageCountCalcs,
		mines = source.skillMineCountCalcs,
	}
	calcs.skill_number, calcs.misc_buffMode, calcs.showMinion = build.mainSocketGroup, "EFFECTIVE", false
	group.mainActiveSkillCalcs = group.mainActiveSkill
	source.skillPartCalcs, source.skillStageCountCalcs = source.skillPart, source.skillStageCount
	source.skillMineCountCalcs = source.skillMineCount
	return function()
		calcs.skill_number, calcs.misc_buffMode, calcs.showMinion = before.number, before.mode, before.minion
		group.mainActiveSkillCalcs = before.active
		source.skillPartCalcs, source.skillStageCountCalcs = before.part, before.stages
		source.skillMineCountCalcs = before.mines
	end
end

local function outputValue(output, key)
	local ns, var = key:match("^(%a+)%.(%a+)$")
	if ns then return output[ns] and output[ns][var] end
	return output[key]
end

-- The total a "{p:mod:i,j}" cell shows, before PoB rounds it: the same Combine as formatCalcStr
-- (CalcFormat.lua:34-71), which returns only the rounded text.
local function modTotal(cell, indices, actor)
	local first = cell[indices[1]]
	if not first or not first.modType then return nil end
	local total = first.modType == "MORE" and 1 or 0
	for _, index in ipairs(indices) do
		local data = cell[index]
		if not data then break end
		local cfg = (data.cfg and actor.mainSkill and actor.mainSkill[data.cfg .. "Cfg"]) or {}
		local store = (data.enemy and actor.enemy and actor.enemy.modDB)
			or (data.cfg and actor.mainSkill and actor.mainSkill.skillModList) or actor.modDB
		if not store then break end
		local names = type(data.modName) == "table" and data.modName or { data.modName }
		local value = store:Combine(data.modType, cfg, unpack(names))
		total = first.modType == "MORE" and total * value or total + value
	end
	return first.modType == "MORE" and (total - 1) * 100 or total
end

-- The raw numbers behind a cell's text, with the precision PoB shows each at: output placeholders, then mod sums.
local function cellValues(cell, actor)
	local values = {}
	for precision, key in cell.format:gmatch("{(%d+):output:([%a%.:]+)}") do
		values[#values + 1] = { key = key, value = outputValue(actor.output, key), precision = tonumber(precision) }
	end
	for precision, list in cell.format:gmatch("{(%d+):mod:([%d,]+)}") do
		local indices = {}
		for index in list:gmatch("%d+") do indices[#indices + 1] = tonumber(index) end
		values[#values + 1] = { key = "mod", value = modTotal(cell, indices, actor), precision = tonumber(precision) }
	end
	return values
end

local function textOf(value)
	if type(value) == "string" or type(value) == "number" then return plain(value) end
	return nil
end

-- PoB's hover popup for a cell, as data: text lines, and tables with their columns and rows.
local function sources(popup, cell)
	popup.sourceData = nil
	popup:SetBreakdownData(cell)
	local found = {}
	for _, section in ipairs(popup.sectionList or {}) do
		if section.type == "TEXT" then
			local lines = {}
			for _, line in ipairs(section.lines) do lines[#lines + 1] = plain(line) end
			found[#found + 1] = { kind = "text", lines = lines }
		elseif section.type == "TABLE" then
			local columns, rows = {}, {}
			for _, column in ipairs(section.colList) do columns[#columns + 1] = { key = column.key, label = column.label } end
			for _, row in ipairs(section.rowList) do
				local cells = {}
				for _, column in ipairs(section.colList) do cells[column.key] = textOf(row[column.key]) end
				if row.mod then
					cells.value = type(row.value) == "number" and row.value or nil
					cells.sourceId = row.mod.source
				end
				rows[#rows + 1] = cells
			end
			found[#found + 1] = { kind = "table", label = section.label, columns = columns, rows = rows }
		end
	end
	return found
end

local function columnNames(data)
	local header = data[1]
	if header.label then return {} end
	local names = {}
	for index, cell in ipairs(header) do names[index] = plain(cell.format):gsub(":$", "") end
	return names
end

local function sectionRows(calcsTab, section, popup, actor)
	local data, rows = section.subSection[1].data, {}
	if not calcsTab:CheckFlag(section) then return rows end
	local names = columnNames(data)
	for _, row in ipairs(data) do
		if row.label and calcsTab:CheckFlag(row) then
			local cells = {}
			for index, cell in ipairs(row) do
				if cell.format and calcsTab:CheckFlag(cell) then
					cells[#cells + 1] = {
						column = names[index], text = plain(formatCalcStr(cell.format, actor, cell)),
						values = cellValues(cell, actor), sources = sources(popup, cell),
					}
				end
			end
			rows[#rows + 1] = { section = section.id, label = row.label, cells = cells }
		end
	end
	return rows
end

local function readChain(build)
	local calcsTab = build.calcsTab
	local actor = calcsTab.calcsEnv.player
	local popup = new("CalcBreakdownControl"):CalcBreakdownControl(calcsTab) -- reads calcsEnv, as the Calcs tab
	popup.clearDisplayFunc = function() end
	local rows = {}
	for _, id in ipairs(SECTIONS) do
		for _, section in ipairs(calcsTab.sectionList) do
			if section.id == id then
				for _, row in ipairs(sectionRows(calcsTab, section, popup, actor)) do rows[#rows + 1] = row end
			end
		end
	end
	local hitByType, totals = {}, { FullDPS = calcsTab.mainOutput.FullDPS }
	for _, damageType in ipairs(DAMAGE_TYPES) do hitByType[damageType] = actor.output[damageType .. "HitAverage"] end
	for _, key in ipairs(TOTALS) do totals[key] = actor.output[key] end
	local skill = actor.mainSkill
	local part = skill.skillPart and skill.activeEffect.grantedEffect.parts
		and skill.activeEffect.grantedEffect.parts[skill.skillPart]
	return {
		skill = skill.activeEffect.grantedEffect.name, part = part and part.name,
		rows = rows, hitByType = hitByType, totals = totals,
	}
end

Rpc.register("analysis.chain", function(request)
	return Build.withChanges({ Scenario.boss(request.boss), calcsOnMainSkill }, readChain)
end)
