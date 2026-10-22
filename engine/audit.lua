-- Audit hooks run inside headless PoB. Data goes back to Python as JSON;
-- rule checking happens in Python (rules.py) using vault rules.

local dkjson = require("dkjson")
local calcFunc

local function mainGroup()
	return build.skillsTab.socketGroupList[build.mainSocketGroup]
end

local function isAttack(skill)
	return skill.activeEffect.grantedEffect.skillTypes[SkillType.Attack] == true
end

local function pickStats(output, keys)
	local t = {}
	for _, k in ipairs(keys) do t[k] = output[k] end
	return t
end

-- Outputs for every active skill in the main group (the skills used together),
-- under one override (e.g. { removeNodes = {...} }).
local function evaluate(override, keys, fast)
	calcFunc = calcFunc or build.calcsTab:GetMiscCalculator()
	local group = mainGroup()
	local original = group.mainActiveSkill
	local ctx = { skills = {}, supports = {}, keystones = {} }
	for index, skill in ipairs(group.displaySkillList or {}) do
		group.mainActiveSkill = index
		local isMain = index == original
		local out = calcFunc(override, isMain and not fast) -- fast: skip FullDPS roll-up
		table.insert(ctx.skills, {
			name = skill.activeEffect.grantedEffect.name, isMain = isMain, isAttack = isAttack(skill),
			out = pickStats(out, keys),
			-- PoB's per-gem "count" (instances in Full DPS) — the user may already model overlaps with it
			count = skill.activeEffect.srcInstance and skill.activeEffect.srcInstance.count or 1,
		})
	end
	group.mainActiveSkill = original
	for _, gem in ipairs(group.gemList) do
		if gem.enabled and gem.gemData and gem.gemData.grantedEffect.support then
			table.insert(ctx.supports, gem.gemData.grantedEffect.id)
		end
	end
	local removed = override.removeNodes or {}
	for _, node in pairs(build.spec.allocNodes) do
		if node.type == "Keystone" and not removed[node] then table.insert(ctx.keystones, node.dn) end
	end
	return ctx
end

local function nodeSet(ids)
	local set = {}
	for _, id in ipairs(ids or {}) do set[build.spec.nodes[id]] = true end
	return set
end

-- request: { removeNodes = {ids}, addNodes = {ids}, stats = {keys}, fast = bool }
function evaluateJSON(requestText)
	local request = dkjson.decode(requestText)
	local override = { removeNodes = nodeSet(request.removeNodes), addNodes = nodeSet(request.addNodes) }
	return dkjson.encode(evaluate(override, request.stats, request.fast))
end

-- Allocated notables/keystones with everything that depends on them (PoB's node.depends
-- already includes masteries that would lose their last notable).
function listBranchesJSON()
	local branches = {}
	for id, node in pairs(build.spec.allocNodes) do
		if (node.type == "Notable" or node.type == "Keystone") and not node.ascendancyName then
			local ids, names = {}, {}
			for _, dep in ipairs(node.depends or { node }) do
				if not dep.ascendancyName and dep.type ~= "ClassStart" then
					table.insert(ids, dep.id)
					if dep.type ~= "Normal" then table.insert(names, dep.dn) end
				end
			end
			table.insert(branches, { id = id, name = node.dn, points = #ids, removeIds = ids, removes = names })
		end
	end
	return dkjson.encode(branches)
end

-- Gems in the main group with their current level/quality.
function listMainGemsJSON()
	local gems = {}
	for _, gem in ipairs(mainGroup().gemList) do
		if gem.enabled and gem.gemData then
			table.insert(gems, { name = gem.gemData.name, level = gem.level, quality = gem.quality })
		end
	end
	return dkjson.encode(gems)
end

-- Upgrade gems in the main group to given level/quality variants.
-- request: { stats = {keys}, targets = { [gemName] = { {level=, quality=}, ... } } }
function auditGemLevelsJSON(requestText)
	local request = dkjson.decode(requestText)
	local group = mainGroup()
	local function recalc()
		build.skillsTab:ProcessSocketGroup(group)
		build.calcsTab:BuildOutput()
		return pickStats(build.calcsTab.mainOutput, request.stats)
	end
	local results = { base = recalc(), gems = {} }
	for _, gem in ipairs(group.gemList) do
		local targets = gem.enabled and gem.gemData and request.targets[gem.gemData.name]
		if targets then
			local level, quality = gem.level, gem.quality
			for _, target in ipairs(targets) do
				gem.level, gem.quality = target.level, target.quality
				local out = recalc()
				table.insert(results.gems, { gem = gem.gemData.name, from = level .. "/" .. quality,
					to = target.level .. "/" .. target.quality, out = out, ctx = evaluate({}, request.stats, true),
					fromLevel = level, fromQuality = quality, toLevel = target.level, toQuality = target.quality })
			end
			gem.level, gem.quality = level, quality
		end
	end
	recalc()
	calcFunc = nil -- build state was touched; rebuild calculator on next use
	return dkjson.encode(results)
end

local function supportsAnySkill(gemData, group)
	for _, skill in ipairs(group.displaySkillList or {}) do
		if calcLib.canGrantedEffectSupportActiveSkill(gemData.grantedEffect, skill) then return true end
	end
	return false
end

-- Try every compatible support gem in place of each linked support (except protected anchors).
-- request: { stats = {keys}, protected = {granted effect ids} }
function auditSupportSwapsJSON(requestText)
	local request = dkjson.decode(requestText)
	local protected = {}
	for _, id in ipairs(request.protected or {}) do protected[id] = true end
	local group = mainGroup()
	local linked = {}
	for _, gem in ipairs(group.gemList) do
		if gem.gemData then linked[gem.gemData.grantedEffect.id] = true end
	end
	local results = { base = evaluate({}, request.stats, true), swaps = {} }
	for _, gem in ipairs(group.gemList) do
		local effect = gem.enabled and gem.gemData and gem.gemData.grantedEffect
		if effect and effect.support and not protected[effect.id] then
			local saved = { gemId = gem.gemId, skillId = gem.skillId, level = gem.level, quality = gem.quality }
			for candidateId, candidate in pairs(data.gems) do
				local ce = candidate.grantedEffect
				if ce.support and not ce.unsupported and not linked[ce.id] and supportsAnySkill(candidate, group) then
					gem.gemId, gem.skillId = candidateId, nil
					build.skillsTab:ProcessSocketGroup(group)
					gem.level, gem.quality = candidate.naturalMaxLevel or 20, 20
					build.skillsTab:ProcessSocketGroup(group)
					table.insert(results.swaps, {
						replaced = gem.gemData and effect.name, with = candidate.name,
						ctx = evaluate({}, request.stats, true),
					})
				end
			end
			gem.gemId, gem.skillId, gem.level, gem.quality = saved.gemId, saved.skillId, saved.level, saved.quality
			build.skillsTab:ProcessSocketGroup(group)
		end
	end
	calcFunc = nil
	return dkjson.encode(results)
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

local function equippedItems()
	local list = {}
	for _, slot in ipairs(build.itemsTab.orderedSlots) do
		local item = slot.selItemId ~= 0 and build.itemsTab.items[slot.selItemId]
		local inUse = not slot.nodeId or build.spec.allocNodes[slot.nodeId]
		local flaskOn = not slot.slotName:match("^Flask") or slot.active
		local swap = slot.slotName:match("Swap") -- weapon swap isn't in use
		-- cluster/timeless jewels reshape the tree at build time; a calc override can't test them
		local treeJewel = item and (item.clusterJewel or (item.name or ""):match("Timeless Jewel"))
		if item and inUse and flaskOn and not swap and not treeJewel then table.insert(list, { slot = slot.slotName, item = item }) end
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

local function isMainTree(node)
	return not node.ascendancyName and node.type ~= "Mastery"
end

-- Cheapest connected tree that keeps every allocated non-travel node.
-- Repeatedly connects the nearest remaining terminal by BFS (Steiner heuristic).
-- request: { keep = {ids} } extra nodes that must stay (small nodes that matter)
function repathJSON(requestText)
	local keep = {}
	for _, id in ipairs((requestText and dkjson.decode(requestText) or {}).keep or {}) do keep[id] = true end
	local start
	local terminals, fixed = {}, {}
	for id, node in pairs(build.spec.allocNodes) do
		if node.type == "ClassStart" then
			start = node
		elseif node.type == "Mastery" or node.ascendancyName then
			fixed[id] = true -- masteries hang off notables; ascendancy is its own tree
		elseif node.type ~= "Normal" or id >= 65536 or keep[id] then
			terminals[id] = node -- notables, keystones, jewel sockets, cluster jewel nodes
		end
	end
	local connected = { [start.id] = true }
	local remaining = 0
	for _ in pairs(terminals) do remaining = remaining + 1 end
	while remaining > 0 do
		local prev, queue, head, found = {}, {}, 1, nil
		for id in pairs(connected) do table.insert(queue, build.spec.nodes[id]); prev[id] = false end
		while head <= #queue and not found do
			local node = queue[head]; head = head + 1
			for _, nb in ipairs(node.linked or {}) do
				if prev[nb.id] == nil and isMainTree(nb) and (nb.type ~= "ClassStart" or nb == start) then
					prev[nb.id] = node.id
					if terminals[nb.id] and not connected[nb.id] then found = nb; break end
					table.insert(queue, nb)
				end
			end
		end
		if not found then return dkjson.encode({ error = "unreachable terminal" }) end
		local id = found.id
		while id and not connected[id] do connected[id] = true; id = prev[id] end
		for tid in pairs(terminals) do
			if connected[tid] and terminals[tid] then terminals[tid] = nil; remaining = remaining - 1 end
		end
	end
	for id in pairs(fixed) do connected[id] = true end
	local removeIds, addIds, current, new = {}, {}, 0, 0
	for id, node in pairs(build.spec.allocNodes) do
		if node.type ~= "ClassStart" and not node.ascendancyName then current = current + 1 end
		if not connected[id] then table.insert(removeIds, id) end
	end
	for id in pairs(connected) do
		local node = build.spec.nodes[id]
		if node.type ~= "ClassStart" and not node.ascendancyName then new = new + 1 end
		if not build.spec.allocNodes[id] then table.insert(addIds, id) end
	end
	local function names(ids)
		local t = {}
		for _, id in ipairs(ids) do
			local n = build.spec.nodes[id]
			table.insert(t, n.dn .. (n.type == "Normal" and "" or " (" .. n.type .. ")"))
		end
		return t
	end
	return dkjson.encode({ currentPoints = current, newPoints = new, removeIds = removeIds, addIds = addIds,
		removed = names(removeIds), added = names(addIds) })
end

-- A gem's own stats at a level/quality, straight from PoB's gem data (catches effects PoB
-- doesn't put in its output, e.g. Cyclone movement speed while channelling).
local function gemStats(grantedEffect, level, quality)
	local values = {}
	local row = grantedEffect.levels[level] or {}
	for index, stat in ipairs(grantedEffect.stats or {}) do
		if type(row[index]) == "number" then values[stat] = row[index] end
	end
	for _, entry in ipairs(grantedEffect.constantStats or {}) do
		values[entry[1]] = (values[entry[1]] or 0) + (entry[2] or 0)
	end
	for _, entry in ipairs(grantedEffect.qualityStats or {}) do
		values[entry[1]] = (values[entry[1]] or 0) + entry[2] * quality
	end
	return values
end

-- request: { name, from = {level, quality}, to = {level, quality} } -> changed stats
function gemStatDiffJSON(requestText)
	local request = dkjson.decode(requestText)
	for _, gemData in pairs(data.gems) do
		if gemData.name == request.name then
			local effect = gemData.grantedEffect
			local before = gemStats(effect, request.from.level, request.from.quality)
			local after = gemStats(effect, request.to.level, request.to.quality)
			-- Readable text via PoB's own stat descriptions (game values are whole numbers)
			local function describe(stat, value)
				local ok, lines = pcall(build.data.describeStats, { [stat] = math.floor(value) }, effect.statDescriptionScope)
				return ok and lines and lines[1] or nil
			end
			local diffs = {}
			for stat, value in pairs(after) do
				local old = before[stat] or 0
				if old ~= value then
					table.insert(diffs, { stat = stat, from = old, to = value,
						fromText = describe(stat, old), toText = describe(stat, value) })
				end
			end
			return dkjson.encode(diffs)
		end
	end
	return "[]"
end

local function findMainGem(name)
	for _, gem in ipairs(mainGroup().gemList) do
		if gem.gemData and gem.gemData.name == name then return gem end
	end
	error("gem not found in main group: " .. tostring(name))
end

local function gemIdByName(name)
	for id, gemData in pairs(data.gems) do
		if gemData.name == name then return id, gemData end
	end
	error("unknown gem: " .. tostring(name))
end

local applyChange = {
	gem = function(change)
		local gem = findMainGem(change.name)
		gem.level, gem.quality = change.level, change.quality
	end,
	swap = function(change)
		local gem = findMainGem(change.replaced)
		local id, gemData = gemIdByName(change.with)
		gem.gemId, gem.skillId = id, nil
		build.skillsTab:ProcessSocketGroup(mainGroup())
		gem.level, gem.quality = gemData.naturalMaxLevel or 20, 20
	end,
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
	local ctx = evaluate({}, request.stats)
	-- the saved file keeps the user's own setup: skills left out and scenario config are calc-only
	restoreSkills()
	restoreConfig()
	return dkjson.encode({ ctx = ctx, xml = build:SaveDB(build.buildName) })
end

-- Scenario config (e.g. "Channeling for # seconds" vs a boss), applied for calculation only.
-- request: { config = { [var] = value } } -> previous values
local savedConfig = {}
function setConfigJSON(requestText)
	local input = build.configTab.input
	for var, value in pairs(dkjson.decode(requestText).config or {}) do
		if savedConfig[var] == nil then savedConfig[var] = { value = input[var] } end
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
	savedConfig = {}
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

-- Allocated small (Normal) main-tree nodes, for valuing travel nodes before re-pathing.
function listAllocatedNormalJSON()
	local ids = {}
	for id, node in pairs(build.spec.allocNodes) do
		if node.type == "Normal" and not node.ascendancyName and id < 65536 then table.insert(ids, id) end
	end
	return dkjson.encode(ids)
end

-- Unallocated notables/keystones reachable within maxDist points, with PoB's own path to them.
-- request: { maxDist = n }
function listAdditionsJSON(requestText)
	local maxDist = dkjson.decode(requestText).maxDist or 6
	local additions = {}
	for id, node in pairs(build.spec.nodes) do
		if not node.alloc and (node.type == "Notable" or node.type == "Keystone") and not node.ascendancyName
			and id < 65536 and node.path and node.pathDist and node.pathDist <= maxDist then
			local ids = {}
			for _, step in ipairs(node.path) do table.insert(ids, step.id) end
			table.insert(additions, { id = id, name = node.dn, type = node.type, pathIds = ids, points = #ids })
		end
	end
	return dkjson.encode(additions)
end

-- Is the main tree still one connected piece after these changes? (masteries/ascendancy excluded)
-- request: { removeIds = {}, addIds = {} }
function treeConnectedJSON(requestText)
	local request = dkjson.decode(requestText)
	local alloc = {}
	for id, node in pairs(build.spec.allocNodes) do alloc[id] = node end
	for _, id in ipairs(request.removeIds or {}) do alloc[id] = nil end
	for _, id in ipairs(request.addIds or {}) do alloc[id] = build.spec.nodes[id] end
	local start
	for _, node in pairs(alloc) do if node.type == "ClassStart" then start = node end end
	local seen, queue, head = { [start.id] = true }, { start }, 1
	while head <= #queue do
		local node = queue[head]; head = head + 1
		for _, nb in ipairs(node.linked or {}) do
			if alloc[nb.id] and not seen[nb.id] and not nb.ascendancyName then
				seen[nb.id] = true
				table.insert(queue, nb)
			end
		end
	end
	for id, node in pairs(alloc) do
		local needsLink = not node.ascendancyName and node.type ~= "Mastery" and node.type ~= "ClassStart"
		if needsLink and not seen[id] then return dkjson.encode({ connected = false, orphan = node.dn }) end
	end
	return dkjson.encode({ connected = true })
end

-- Run PoB's own PowerBuilder (heatmap / Power Report engine) for each stat and collect node power.
-- request: { stats = {"FullDPS", "TotalEHP"}, maxDist = n }
-- returns: { nodes = { [id] = { name, type, alloc, dist, power = { [stat] = { single, path } } } },
--            masteries = { [id] = { name, alloc, selected, effects = { [effectId] = { text, power = {...} } } } } }
function powerReportJSON(requestText)
	local request = dkjson.decode(requestText)
	local calcs = build.calcsTab
	local result = { nodes = {}, masteries = {} }
	local oldStat, oldDepth = calcs.powerStat, calcs.nodePowerMaxDepth
	calcs.nodePowerMaxDepth = request.maxDist
	for _, statName in ipairs(request.stats) do
		for _, entry in ipairs(data.powerStatList) do
			if entry.stat == statName then calcs.powerStat = entry end
		end
		calcs:PowerBuilder()
		for id, node in pairs(build.spec.nodes) do
			local p = node.power
			if p and p.singleStat and not node.ascendancyName and node.type ~= "ClassStart" then
				if node.type == "Mastery" then
					local m = result.masteries[id] or { name = node.dn, alloc = node.alloc == true,
						selected = build.spec.masterySelections[id], dist = node.pathDist, effects = {} }
					for effectId, ep in pairs(p.masteryEffects or {}) do
						local effect = build.spec.tree.masteryEffects[effectId]
						local e = m.effects[tostring(effectId)] or { text = effect and table.concat(effect.sd or {}, " / ") or "?", power = {} }
						e.power[statName] = { single = ep.singleStat, path = ep.pathPower }
						m.effects[tostring(effectId)] = e
					end
					result.masteries[tostring(id)] = m
				else
					local n = result.nodes[tostring(id)] or { name = node.dn, type = node.type, alloc = node.alloc == true,
						dist = node.pathDist, power = {} }
					n.power[statName] = { single = p.singleStat, path = p.pathPower }
					result.nodes[tostring(id)] = n
				end
			end
		end
	end
	calcs.powerStat, calcs.nodePowerMaxDepth = oldStat, oldDepth
	return dkjson.encode(result)
end

-- Node id lists for the power report: PoB's path for unallocated nodes, node.depends for allocated ones.
function nodePathsJSON(requestText)
	local result = {}
	for _, id in ipairs(dkjson.decode(requestText).ids or {}) do
		local node = build.spec.nodes[id]
		local ids = {}
		for _, n in ipairs((node.alloc and node.depends) or node.path or {}) do
			if not n.ascendancyName and n.type ~= "ClassStart" then table.insert(ids, n.id) end
		end
		result[tostring(id)] = ids
	end
	return dkjson.encode(result)
end

-- Same temporary node PoB's PowerBuilder uses to score a mastery effect.
local function masteryEffectNode(node, effect)
	local effectNode = { id = node.id, type = node.type, name = node.name, sd = {} }
	for i, sd in ipairs(effect.sd or {}) do effectNode.sd[i] = sd end
	build.spec.tree:ProcessStats(effectNode)
	return effectNode
end

-- Every alternative option for every allocated mastery (PowerBuilder only scores unallocated ones).
-- request: { stats = {keys} }
function masteryOptionsJSON(requestText)
	local keys = dkjson.decode(requestText).stats
	local results = {}
	for id, node in pairs(build.spec.allocNodes) do
		local selected = build.spec.masterySelections[id]
		if node.type == "Mastery" and selected then
			local current = build.spec.tree.masteryEffects[selected]
			local entry = { masteryId = id, name = node.dn, current = current and table.concat(current.sd, " / ") or "?", options = {} }
			for _, option in ipairs(node.masteryEffects or {}) do
				local usedBy = isValueInTable(build.spec.masterySelections, option.effect)
				local effect = build.spec.tree.masteryEffects[option.effect]
				if effect and option.effect ~= selected and (not usedBy or usedBy == id) then
					local ctx = evaluate({ removeNodes = { [node] = true }, addNodes = { [masteryEffectNode(node, effect)] = true } }, keys, true)
					table.insert(entry.options, { effectId = option.effect, text = table.concat(effect.sd, " / "), ctx = ctx })
				end
			end
			table.insert(results, entry)
		end
	end
	return dkjson.encode(results)
end

-- Apply a mastery choice exactly like PoB's mastery popup (TreeTab:SaveMasteryPopup).
applyChange.mastery = function(change)
	local node = build.spec.nodes[change.masteryId]
	local effect = build.spec.tree.masteryEffects[change.effectId]
	node.sd = effect.sd
	node.allMasteryOptions = false
	build.spec.tree:ProcessStats(node)
	build.spec.masterySelections[node.id] = effect.id
end

-- What a node does (its stat lines), so every suggestion can show it.
function nodeStatsJSON(requestText)
	local result = {}
	for _, id in ipairs(dkjson.decode(requestText).ids or {}) do
		local node = build.spec.nodes[id]
		if node then result[tostring(id)] = table.concat(node.sd or {}, "; ") end
	end
	return dkjson.encode(result)
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
	table.sort(skills, function(a, b) return a.amount > b.amount end)
	return dkjson.encode({ skills = skills, mana = out.Mana, manaUnreserved = out.ManaUnreserved,
		life = out.Life, lifeUnreserved = out.LifeUnreserved })
end

-- Why does a tree change help? Diff the main skill's damage/crit/speed modifiers and the player's
-- defence modifiers by PoB source. "Tree:<id>" of a jewel socket = a radius jewel's bonus.
-- request: { removeIds = {}, addIds = {} }
local WHY_SKILL_STATS = { "Damage", "ColdDamage", "FireDamage", "LightningDamage", "ChaosDamage", "PhysicalDamage",
	"ElementalDamage", "SpellDamage", "AreaOfEffect", "CritChance", "CritMultiplier", "Speed", "ProjectileCount" }
local WHY_PLAYER_STATS = { "Life", "EnergyShield", "Mana", "Armour", "Evasion", "BlockChance", "SpellBlockChance",
	"FireResist", "ColdResist", "LightningResist", "ChaosResist" }

local function sourceLabel(source)
	local id = tonumber(tostring(source):match("^Tree:(%d+)"))
	if not id then return tostring(source) end
	local node = build.spec.nodes[id]
	local jewel = build.itemsTab.sockets and build.itemsTab.sockets[id]
	local item = jewel and jewel.selItemId ~= 0 and build.itemsTab.items[jewel.selItemId]
	if item then return "radius of " .. (item.title or item.name) end
	return node and node.dn or tostring(source)
end

function whyJSON(requestText)
	local request = dkjson.decode(requestText)
	local calcs = build.calcsTab.calcs
	local function tab(override)
		local env = calcs.initEnv(build, "CALCULATOR", override)
		calcs.perform(env)
		local rows = {}
		local function add(list, modType, name, scope)
			for _, r in ipairs(list:Tabulate(modType, scope, name)) do
				local key = modType .. "|" .. name .. "|" .. sourceLabel(r.mod.source)
				rows[key] = (rows[key] or 0) + (r.value or 0)
			end
		end
		local skill = env.player.mainSkill
		for _, t in ipairs({ "INC", "MORE", "BASE" }) do
			for _, n in ipairs(WHY_SKILL_STATS) do add(skill.skillModList, t, n, skill.skillCfg) end
			for _, n in ipairs(WHY_PLAYER_STATS) do add(env.player.modDB, t, n, nil) end
		end
		return rows
	end
	local before = tab({})
	local after = tab({ removeNodes = nodeSet(request.removeIds), addNodes = nodeSet(request.addIds) })
	local diffs = {}
	for k, v in pairs(after) do
		if (before[k] or 0) ~= v then
			local t, n, s = k:match("^(.-)|(.-)|(.*)$")
			table.insert(diffs, { type = t, stat = n, source = s, from = before[k] or 0, to = v })
		end
	end
	for k, v in pairs(before) do
		if after[k] == nil and v ~= 0 then
			local t, n, s = k:match("^(.-)|(.-)|(.*)$")
			table.insert(diffs, { type = t, stat = n, source = s, from = v, to = 0 })
		end
	end
	table.sort(diffs, function(a, b) return math.abs(a.to - a.from) > math.abs(b.to - b.from) end)
	return dkjson.encode(diffs)
end
