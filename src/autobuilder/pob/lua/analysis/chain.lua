-- The damage chain of the main skill (decisions 009, 023): the rows of four PoB Calcs tab sections in PoB's order, each
-- cell with PoB's own text, the raw numbers it shows and its sources as PoB's hover popup lists them. Nothing here
-- computes a game number: rows and show conditions are CalcSections.lua with CalcsTab:CheckFlag, the text is
-- formatCalcStr (CalcFormat.lua:16-74), the sources are CalcBreakdownControl (CalcBreakdownControl.lua:60-527).
-- Grouping the rows into the mockup's steps and the gaps come later (compare/chain_table.py).
local Rpc, Build, Scenario = ...

-- Skill Hit Damage, Attack/Cast Rate, Crits, Accuracy (CalcSections.lua:105, 575, 605, 939).
local SECTIONS = { "HitDamage", "Speed", "Crit", "HitChance" }
local DAMAGE_TYPES = { "Physical", "Lightning", "Cold", "Fire", "Chaos" }
-- An attack's hit is per hand (CalcOffence.lua:2017, 2052, 2179); these are combined into the top level for every skill
-- (:2510-2513, :3959-3964).
local TOTALS = { "AverageDamage", "TotalDPS", "Speed", "HitSpeed", "HitChance", "CritChance", "CritMultiplier" }
local HANDS = { { output = "MainHand", flag = "weapon1Attack" }, { output = "OffHand", flag = "weapon2Attack" } }
-- What CALCS mode reads from the Calcs fields for every skill, not only the main one (CalcActiveSkill.lua:623, 649, 925).
local EVERY_SKILL = { skillStageCountCalcs = "skillStageCount", skillMineCountCalcs = "skillMineCount",
	skillMinionSkillCalcs = "skillMinionSkill" }

local function plain(text)
	return (tostring(text):gsub("%^x%x%x%x%x%x%x", ""):gsub("%^%d", ""))
end

-- The Calcs tab pointed at the sidebar for one read (decision 023): PoB's own pointing at the main skill (the compare
-- tab's CompareEntry:SyncCalcsSkillSelection, CompareEntry.lua:229-248, which reads only the calcsTab, skillsTab and
-- mainSocketGroup the open build has too), the sidebar's stage, mine and minion skill counts for every other skill,
-- buff mode "effective" and the minion view off (CalcSetup.lua:564-567). The undo keeps every field of the Calcs inputs,
-- groups and gems, also those the Calcs recalculation writes (CalcActiveSkill.lua:251, 697, 738, 926).
local function calcsOnSidebar(build)
	local group = build.skillsTab.socketGroupList[build.mainSocketGroup]
	if not (group and group.displaySkillList and group.displaySkillList[group.mainActiveSkill or 1]) then
		Rpc.fail("NoMainSkill", "the build has no main skill in its sidebar")
	end
	local calcs, tables = build.calcsTab.input, { build.calcsTab.input }
	for _, each in ipairs(build.skillsTab.socketGroupList) do
		tables[#tables + 1] = each
		for _, gem in ipairs(each.gemList) do tables[#tables + 1] = gem end
	end
	local undo = Build.keepFields(tables)
	if not common.classes.CompareEntry then LoadModule("Classes/CompareEntry") end
	common.classes.CompareEntry.SyncCalcsSkillSelection(build)
	for index = 2, #tables do
		for calcsField, field in pairs(EVERY_SKILL) do tables[index][calcsField] = tables[index][field] end
	end
	calcs.misc_buffMode, calcs.showMinion = "EFFECTIVE", false
	return undo
end

local function outputValue(output, key)
	local ns, var = key:match("^(%a+)%.(%a+)$")
	if ns then return output[ns] and output[ns][var] end
	return output[key]
end

-- The total of one "{p:mod:i,j}" placeholder before PoB rounds it, from formatCalcStr itself: it hands the total to
-- the global formatCalcVal to round (CalcFormat.lua:70), so a stand-in for that call records it. nil where PoB shows
-- "?" (:39-41).
local function modTotal(placeholder, cell, actor)
	local pobsRound, total = formatCalcVal, nil
	formatCalcVal = function(value, precision)
		total = value
		return pobsRound(value, precision)
	end
	local ok, problem = pcall(formatCalcStr, placeholder, actor, cell)
	formatCalcVal = pobsRound
	if not ok then error(problem, 0) end
	return total
end

-- The raw numbers behind a cell's text, with the precision PoB shows each at: output placeholders, then mod sums.
local function cellValues(cell, actor)
	local values = {}
	for precision, key in cell.format:gmatch("{(%d+):output:([%a%.:]+)}") do
		values[#values + 1] = { key = key, value = outputValue(actor.output, key), precision = tonumber(precision) }
	end
	for placeholder, precision in cell.format:gmatch("({(%d+):mod:[%d,]+})") do
		values[#values + 1] = { key = "mod", value = modTotal(placeholder, cell, actor), precision = tonumber(precision) }
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

-- The average hit per damage type, the average hit and the crit effect: per attacking hand for an attack (hand =
-- "MainHand", "OffHand"), else once from the top level.
local function hitOf(output, hand)
	local byType = {}
	for _, damageType in ipairs(DAMAGE_TYPES) do byType[damageType] = output[damageType .. "HitAverage"] end
	return { hand = hand, byType = byType, AverageHit = output.AverageHit, CritEffect = output.CritEffect }
end

local function hits(actor)
	local flags = actor.mainSkill.skillFlags
	if not flags.attack then return { hitOf(actor.output) } end
	local found = {}
	for _, hand in ipairs(HANDS) do
		if flags[hand.flag] then found[#found + 1] = hitOf(actor.output[hand.output], hand.output) end
	end
	return found
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
	local totals = { FullDPS = calcsTab.mainOutput.FullDPS }
	for _, key in ipairs(TOTALS) do totals[key] = actor.output[key] end
	local skill = actor.mainSkill
	local part = skill.skillPart and skill.activeEffect.grantedEffect.parts
		and skill.activeEffect.grantedEffect.parts[skill.skillPart]
	return {
		skill = skill.activeEffect.grantedEffect.name, part = part and part.name,
		rows = rows, hits = hits(actor), totals = totals,
	}
end

Rpc.register("analysis.chain", function(request)
	return Build.withChanges({ Scenario.boss(request.boss), calcsOnSidebar }, readChain)
end)
