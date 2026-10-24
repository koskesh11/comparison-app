-- Audit hooks run inside headless PoB. Data goes back to Python as JSON;
-- rule checking happens in Python (rules.py) using vault rules.

local dkjson = require("dkjson")
local calcFunc

local function jsonObject(t)
	return setmetatable(t or {}, { __jsontype = "object" })
end

local function sortedKeys(t)
	local keys = {}
	for key in pairs(t) do table.insert(keys, key) end
	table.sort(keys)
	return keys
end

local function mainGroup()
	return build.skillsTab.socketGroupList[build.mainSocketGroup]
end

local function isAttack(skill)
	return skill.activeEffect.grantedEffect.skillTypes[SkillType.Attack] == true
end

local function pickStats(output, keys)
	local t = jsonObject()
	for _, k in ipairs(keys) do t[k] = output[k] end
	return t
end

local function calcAsMain(groupIndex, skillIndex, override)
	calcFunc = calcFunc or build.calcsTab:GetMiscCalculator()
	local group = build.skillsTab.socketGroupList[groupIndex]
	local skill = group and group.displaySkillList and group.displaySkillList[skillIndex]
	if not skill then
		error("no skill at group " .. tostring(groupIndex) .. " index " .. tostring(skillIndex))
	end
	local originalGroup = build.mainSocketGroup
	local originalSkill = group.mainActiveSkill
	local originalViewMode = build.viewMode
	build.mainSocketGroup = groupIndex
	group.mainActiveSkill = skillIndex
	build.viewMode = "SKILLS" -- Modules/Calcs.lua:103: avoid the TREE-mode FullDPS roll-up.
	local ok, out = pcall(calcFunc, override, false)
	build.mainSocketGroup = originalGroup
	group.mainActiveSkill = originalSkill
	build.viewMode = originalViewMode
	if not ok then error(out, 0) end
	return out, skill, group
end

local function skillDpsRows(list)
	local rows = {}
	if type(list) ~= "table" then return rows end
	for _, skill in ipairs(list) do
		table.insert(rows, { name = skill.name, dps = skill.dps, count = skill.count,
			trigger = skill.trigger or dkjson.null, skillPart = skill.skillPart or dkjson.null })
	end
	return rows
end

local function skillPartInfo(skill)
	local effect = skill.activeEffect
	local grantedEffect = effect and effect.grantedEffect
	local parts = grantedEffect and grantedEffect.parts
	local partCount = type(parts) == "table" and #parts or 0
	local src = effect and effect.srcInstance
	if partCount >= 2 and src then
		local partIndex = src.skillPart
		local part = partIndex and parts[partIndex]
		return partIndex or dkjson.null, partCount, part and part.name or dkjson.null
	end
	return dkjson.null, partCount, skill.skillPartName or dkjson.null
end

local function supportIds(group)
	local supports = {}
	for _, gem in ipairs(group.gemList) do
		if gem.enabled and gem.gemData and gem.gemData.grantedEffect.support then
			table.insert(supports, gem.gemData.grantedEffect.id)
		end
	end
	return supports
end

local function keystoneNames(override)
	local names = {}
	local removed = override.removeNodes or {}
	for _, node in pairs(build.spec.allocNodes) do
		if node.type == "Keystone" and not removed[node] then table.insert(names, node.dn) end
	end
	table.sort(names)
	return names
end

local function mainSkillRows(group, override, keys, fast, ctx)
	local original = group.mainActiveSkill
	local ok, err = pcall(function()
		for index, skill in ipairs(group.displaySkillList or {}) do
		group.mainActiveSkill = index
		local isMain = index == original
		local out = calcFunc(override, isMain and not fast) -- fast: skip FullDPS roll-up
		local partIndex, partCount, part = skillPartInfo(skill)
		if isMain then ctx.skillDPS = skillDpsRows(out.SkillDPS) end
		table.insert(ctx.skills, {
			name = skill.activeEffect.grantedEffect.name, isMain = isMain, isAttack = isAttack(skill),
			part = part, partIndex = partIndex, partCount = partCount,
			out = pickStats(out, keys),
			-- PoB's per-gem "count" (instances in Full DPS) — the user may already model overlaps with it
			count = skill.activeEffect.srcInstance and skill.activeEffect.srcInstance.count or 1,
		})
		end
	end)
	group.mainActiveSkill = original
	if not ok then error(err, 0) end
end

local function usedTogetherRows(override, keys, extraSkills)
	local rows = {}
	for n, entry in ipairs(extraSkills or {}) do
		if type(entry) ~= "table" or type(entry.group) ~= "number" or type(entry.index) ~= "number" then
			error("extraSkills entry " .. n .. ": group and index must be numbers")
		end
		local out, skill = calcAsMain(entry.group, entry.index, override)
		table.insert(rows, { group = entry.group, index = entry.index,
			name = skill.activeEffect.grantedEffect.name, out = pickStats(out, keys) })
	end
	return rows
end

-- Outputs for every active skill in the main group (the skills used together),
-- under one override (e.g. { removeNodes = {...} }).
local evaluate

local function collectPartVariants(group)
	local variants = {}
	for _, skill in ipairs(group.displaySkillList or {}) do
		local _, partCount = skillPartInfo(skill)
		local effect = skill.activeEffect
		local src = effect and effect.srcInstance
		local parts = effect and effect.grantedEffect and effect.grantedEffect.parts
		if partCount >= 2 and src then
			local current = src.skillPart or 1
			for partIndex = 1, partCount do
				if partIndex ~= current then
					table.insert(variants, { skill = effect.grantedEffect.name, partIndex = partIndex,
						partName = parts[partIndex].name, src = src })
				end
			end
		end
	end
	return variants
end

local function evaluatePart(override, keys, fast, extraSkills, variant)
	local saved = variant.src.skillPart
	variant.src.skillPart = variant.partIndex
	calcFunc = nil
	local ok, ctx = pcall(evaluate, override, keys, fast, extraSkills, false)
	variant.src.skillPart = saved
	calcFunc = nil
	if not ok then error(ctx, 0) end
	return { skill = variant.skill, partIndex = variant.partIndex,
		partName = variant.partName, ctx = ctx }
end

local function partVariantRows(group, override, keys, fast, extraSkills)
	local rows = setmetatable({}, { __jsontype = "array" })
	for _, variant in ipairs(collectPartVariants(group)) do
		table.insert(rows, evaluatePart(override, keys, fast, extraSkills, variant))
	end
	return rows
end

evaluate = function(override, keys, fast, extraSkills, partVariants)
	calcFunc = calcFunc or build.calcsTab:GetMiscCalculator()
	local group = mainGroup()
	local ctx = { skills = {}, supports = {}, keystones = {}, skillDPS = {} }
	mainSkillRows(group, override, keys, fast, ctx)
	ctx.supports = supportIds(group)
	ctx.keystones = keystoneNames(override)
	ctx.usedTogether = usedTogetherRows(override, keys, extraSkills)
	if partVariants then ctx.byPart = partVariantRows(group, override, keys, fast, extraSkills) end
	return ctx
end

-- Evaluate with the request's stats and extra skills (skills from other groups used together).
local function evaluateRequest(request, override)
	return evaluate(override or {}, request.stats, request.fast, request.extraSkills, request.partVariants)
end

local function nodeSet(ids)
	local set = {}
	for _, id in ipairs(ids or {}) do set[build.spec.nodes[id]] = true end
	return set
end

-- request: { removeNodes = {ids}, addNodes = {ids}, stats = {keys}, fast = bool, extraSkills = {...} }
function evaluateJSON(requestText)
	local request = dkjson.decode(requestText)
	local override = { removeNodes = nodeSet(request.removeNodes), addNodes = nodeSet(request.addNodes) }
	return dkjson.encode(evaluateRequest(request, override))
end

local MOD_LISTS = { "implicitModLines", "explicitModLines", "enchantModLines", "crucibleModLines", "scourgeModLines" }

-- Numeric outputs (player + minion) with every active skill as the main skill.
-- scope "main": only the main group (skills used together); "all": every enabled group.
local function allOutputs(override, scope)
	calcFunc = calcFunc or build.calcsTab:GetMiscCalculator()
	local origGroup = build.mainSocketGroup
	local outs = {}
	for gi, group in ipairs(build.skillsTab.socketGroupList) do
		if (scope == "all" and group.enabled ~= false) or gi == origGroup then
			local origSkill = group.mainActiveSkill
			for si in ipairs(group.displaySkillList or {}) do
				build.mainSocketGroup, group.mainActiveSkill = gi, si
				local out = calcFunc(override, false)
				local flat = {}
				for k, v in pairs(out) do if type(v) == "number" then flat[k] = v end end
				for k, v in pairs(type(out.Minion) == "table" and out.Minion or {}) do
					if type(v) == "number" then flat["Minion." .. k] = v end
				end
				outs[gi .. ":" .. si] = flat
			end
			group.mainActiveSkill = origSkill
		end
	end
	build.mainSocketGroup = origGroup
	return outs
end

local function changedKeys(baseOuts, outs)
	local changed = {}
	for key, base in pairs(baseOuts) do
		for k, v in pairs(base) do
			local nv = outs[key] and outs[key][k]
			if nv and math.abs(nv - v) > 1e-6 * math.max(1, math.abs(v)) then changed[k] = true end
		end
	end
	local list = {}
	for k in pairs(changed) do table.insert(list, k) end
	table.sort(list)
	return list
end

-- Conditions a mod line depends on (e.g. "LowLife", "AffectedByMalevolence"): if PoB's
-- config has them off, the mod shows no effect even though it works in game.
local CONDITION_TAGS = { Condition = true, ActorCondition = true, Multiplier = true, MultiplierThreshold = true, StatThreshold = true }
local function modConditions(modLine)
	local found, list = {}, {}
	for _, mod in ipairs(modLine.modList or {}) do
		for _, tag in ipairs(mod) do
			if type(tag) == "table" and CONDITION_TAGS[tag.type] then
				local name = tag.var or (tag.varList and table.concat(tag.varList, "/")) or tag.stat or tag.type
				if not found[name] then found[name] = true; table.insert(list, name) end
			end
		end
	end
	return list
end

local function slotItemInUse(slot)
	local item = slot.selItemId ~= 0 and build.itemsTab.items[slot.selItemId]
	if not item then return nil end
	if (slot.slotName == "Graft 1" or slot.slotName == "Graft 2")
		and not build.spec.treeVersion:find("3_27") then return nil end
	if slot.slotName == "Ring 3" then
		local mainEnv = build.calcsTab.mainEnv
		if not (mainEnv and mainEnv.initialNodeModDB
			and mainEnv.initialNodeModDB:Flag(nil, "AdditionalRingSlot")) then return nil end
	end
	local activeSet = build.itemsTab.activeItemSet.useSecondWeaponSet and 2 or 1
	if slot.weaponSet and slot.weaponSet ~= activeSet then return nil end
	if slot.nodeId and not build.spec.allocNodes[slot.nodeId] then return nil end
	return item
end

local function equippedItems()
	local list = {}
	for _, slot in ipairs(build.itemsTab.orderedSlots) do
		local item = slotItemInUse(slot)
		local flaskOn = not slot.slotName:match("^Flask") or slot.active
		-- cluster/timeless jewels reshape the tree at build time; a calc override can't test them
		local treeJewel = item and (item.clusterJewel or (item.name or ""):match("Timeless Jewel"))
		if item and flaskOn and not treeJewel then table.insert(list, { slot = slot.slotName, item = item }) end
	end
	return list
end

-- Remove each mod line from each equipped item: does any output change?
function auditWastedModsJSON()
	local baseMain = allOutputs({}, "main")
	local baseAll -- computed lazily: only needed for mods that change nothing in the main group
	local results = {}
	for _, entry in ipairs(equippedItems()) do
		local item = entry.item
		for _, listName in ipairs(MOD_LISTS) do
			for index, modLine in ipairs(item[listName] or {}) do
				-- uniques list every variant's lines; only the selected variant's lines are active
				local inactiveVariant = modLine.variantList and item.variant and not modLine.variantList[item.variant]
				if inactiveVariant then goto continue end
				local copy = new("Item"):Item(item:BuildRaw())
				table.remove(copy[listName], index)
				copy:BuildAndParseRaw()
				local override = { repSlotName = entry.slot, repItem = copy }
				local changed = changedKeys(baseMain, allOutputs(override, "main"))
				local otherSkills = false
				if #changed == 0 then
					baseAll = baseAll or allOutputs({}, "all")
					changed = changedKeys(baseAll, allOutputs(override, "all"))
					otherSkills = #changed > 0
				end
				table.insert(results, {
					slot = entry.slot, item = item.name, line = modLine.line, kind = listName:gsub("ModLines", ""),
					rarity = item.rarity, crafted = modLine.crafted == true,
					unsupported = modLine.extra ~= nil, changed = #changed, otherSkills = otherSkills,
					conditions = modConditions(modLine), sample = { changed[1], changed[2], changed[3] },
				})
				::continue::
			end
		end
	end
	calcFunc = nil
	return dkjson.encode(results)
end

local applyChange = {
	repath = function(change)
		local spec = build.spec
		for _, id in ipairs(change.removeIds) do
			spec.nodes[id].alloc = false
			spec.allocNodes[id] = nil
		end
		for _, id in ipairs(change.addIds) do
			spec.nodes[id].alloc = true
			spec.allocNodes[id] = spec.nodes[id]
		end
		spec:BuildAllDependsAndPaths()
	end,
}

AuditCore = {
	evaluate = evaluate, evaluateRequest = evaluateRequest, nodeSet = nodeSet, applyChange = applyChange, sortedKeys = sortedKeys,
	calcAsMain = calcAsMain, pickStats = pickStats, MOD_LISTS = MOD_LISTS, mainGroup = mainGroup,
	jsonObject = jsonObject, slotItemInUse = slotItemInUse, skillPartInfo = skillPartInfo,
	resetCalc = function() calcFunc = nil end,
}

-- request: { changes = [...], stats = {keys}, buildName = "..." } -> { ctx, xml }
function applyChangesJSON(requestText)
	local request = dkjson.decode(requestText)
	for _, change in ipairs(request.changes) do
		local apply = applyChange[change.type] or error("unknown change type " .. tostring(change.type))
		apply(change)
	end
	for _, group in ipairs(build.skillsTab.socketGroupList) do build.skillsTab:ProcessSocketGroup(group) end
	build.buildFlag = true
	build.calcsTab:BuildOutput()
	calcFunc = nil
	build.buildName = request.buildName or build.buildName
	local ctx = evaluateRequest(request)
	-- the saved file keeps the user's own setup: skills left out and scenario config are calc-only
	restoreSkills()
	restoreConfig()
	return dkjson.encode({ ctx = ctx, xml = request.save ~= false and build:SaveDB(build.buildName) or nil })
end

-- Scenario config (e.g. "Channeling for # seconds" vs a boss), applied for calculation only.
-- request: { config = { [var] = value } } -> previous values
local savedConfig = jsonObject()
function setConfigJSON(requestText)
	local input = build.configTab.input
	for var, value in pairs(dkjson.decode(requestText).config or {}) do
		if savedConfig[var] == nil then savedConfig[var] = jsonObject({ value = input[var] }) end
		input[var] = value
	end
	build.configTab:BuildModList()
	build.buildFlag = true
	build.calcsTab:BuildOutput()
	calcFunc = nil
	return dkjson.encode(savedConfig)
end

function restoreConfig()
	for var, saved in pairs(savedConfig) do build.configTab.input[var] = saved.value end
	savedConfig = jsonObject()
	build.configTab:BuildModList()
end

-- Positive "capability" outputs (ailment chances etc.) so the audit can show what a change loses.
function capabilityKeysJSON()
	local keys = {}
	for k, v in pairs(build.calcsTab.mainOutput) do
		if type(v) == "number" and v > 0 and (k:match("Freeze") or k:match("Chill") or k:match("Shock")
			or k:match("Ignite") or k:match("Bleed") or k:match("Poison"))
			and (k:match("Chance") or k:match("Effect") or k:match("Duration")) then
			table.insert(keys, k)
		end
	end
	table.sort(keys)
	return dkjson.encode(keys)
end

-- Titles of equipped items (for models that depend on specific uniques).
function equippedTitlesJSON()
	local titles = {}
	for _, slot in ipairs(build.itemsTab.orderedSlots) do
		local item = slot.selItemId ~= 0 and build.itemsTab.items[slot.selItemId]
		if item then table.insert(titles, item.title or item.name) end
	end
	return dkjson.encode(titles)
end

-- Leave skills out of the calculation (e.g. a boss-only aura) without touching the build file.
-- request: { names = {skill names} } -> names actually disabled
local disabledGems = {}
function disableSkillsJSON(requestText)
	local wanted = {}
	for _, name in ipairs(dkjson.decode(requestText).names or {}) do wanted[name] = true end
	local disabled = {}
	for _, group in ipairs(build.skillsTab.socketGroupList) do
		for _, gem in ipairs(group.gemList) do
			local name = gem.gemData and gem.gemData.name or gem.nameSpec
			if gem.enabled and wanted[name] then
				gem.enabled = false
				table.insert(disabledGems, gem)
				table.insert(disabled, name)
			end
		end
		build.skillsTab:ProcessSocketGroup(group)
	end
	build.buildFlag = true
	build.calcsTab:BuildOutput()
	calcFunc = nil
	return dkjson.encode(disabled)
end

-- Re-enable skills disabled for calculation (before saving, so the file keeps the user's setup).
function restoreSkills()
	for _, gem in ipairs(disabledGems) do gem.enabled = true end
	disabledGems = {}
	for _, group in ipairs(build.skillsTab.socketGroupList) do build.skillsTab:ProcessSocketGroup(group) end
end

-- Every skill that reserves mana or life, with PoB's own reserved amount, plus the pools.
function reservationsJSON()
	local env = build.calcsTab.mainEnv
	local out = build.calcsTab.mainOutput
	local skills = {}
	for _, skill in ipairs(env.player.activeSkillList) do
		local data_ = skill.skillData
		for _, pool in ipairs({ "Mana", "Life" }) do
			local amount = data_[pool .. "ReservedBase"]
			if amount and amount > 0 then
				table.insert(skills, { name = skill.activeEffect.grantedEffect.name, pool = pool, amount = amount,
					percent = data_[pool .. "ReservedPercent"] })
			end
		end
	end
	-- Input order is ipairs(activeSkillList), so ties stay deterministic; a name tie-break would change the pinned golden order.
	table.sort(skills, function(a, b) return a.amount > b.amount end)
	return dkjson.encode({ skills = skills, mana = out.Mana, manaUnreserved = out.ManaUnreserved,
		life = out.Life, lifeUnreserved = out.LifeUnreserved })
end

dofile(ENGINE_DIR .. "/audit_tree.lua")
dofile(ENGINE_DIR .. "/audit_costs.lua")
dofile(ENGINE_DIR .. "/audit_gems.lua")
dofile(ENGINE_DIR .. "/guide.lua")
dofile(ENGINE_DIR .. "/audit_why.lua")
