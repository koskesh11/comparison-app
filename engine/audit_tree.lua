-- Passive-tree audit hooks, loaded by audit.lua.

local dkjson = require("dkjson")
local evaluateRequest, nodeSet, applyChange, sortedKeys, jsonObject = AuditCore.evaluateRequest, AuditCore.nodeSet,
	AuditCore.applyChange, AuditCore.sortedKeys, AuditCore.jsonObject

local function isMainTree(node)
	return not node.ascendancyName and node.type ~= "Mastery"
end

local function repathInputs(keep)
	local start
	local terminals, fixed = {}, {}
	for _, id in ipairs(sortedKeys(build.spec.allocNodes)) do
		local node = build.spec.allocNodes[id]
		if node.type == "ClassStart" then
			start = node
		elseif node.type == "Mastery" or node.ascendancyName then
			fixed[id] = true -- masteries hang off notables; ascendancy is its own tree
		elseif node.type ~= "Normal" or id >= 65536 or keep[id] then
			terminals[id] = node -- notables, keystones, jewel sockets, cluster jewel nodes
		end
	end
	return start, terminals, fixed
end

local function connectTerminals(start, terminals)
	local connected = { [start.id] = true }
	local remaining = #sortedKeys(terminals)
	while remaining > 0 do
		local prev, queue, head, found = {}, {}, 1, nil
		for _, id in ipairs(sortedKeys(connected)) do table.insert(queue, build.spec.nodes[id]); prev[id] = false end
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
		if not found then return nil end
		local id = found.id
		while id and not connected[id] do connected[id] = true; id = prev[id] end
		for _, terminalId in ipairs(sortedKeys(terminals)) do
			if connected[terminalId] then terminals[terminalId] = nil; remaining = remaining - 1 end
		end
	end
	return connected
end

local function nodeNames(ids)
	local names = {}
	for _, id in ipairs(ids) do
		local node = build.spec.nodes[id]
		table.insert(names, node.dn .. (node.type == "Normal" and "" or " (" .. node.type .. ")"))
	end
	return names
end

-- Cheapest connected tree that keeps every allocated non-travel node.
-- Repeatedly connects the nearest remaining terminal by BFS (Steiner heuristic).
-- request: { keep = {ids} } extra nodes that must stay (small nodes that matter)
function repathJSON(requestText)
	local keep = {}
	for _, id in ipairs((requestText and dkjson.decode(requestText) or {}).keep or {}) do keep[id] = true end
	local start, terminals, fixed = repathInputs(keep)
	local connected = connectTerminals(start, terminals)
	if not connected then return dkjson.encode({ error = "unreachable terminal" }) end
	for id in pairs(fixed) do connected[id] = true end
	local removeIds, addIds, current, new = {}, {}, 0, 0
	for _, id in ipairs(sortedKeys(build.spec.allocNodes)) do
		local node = build.spec.allocNodes[id]
		if node.type ~= "ClassStart" and not node.ascendancyName then current = current + 1 end
		if not connected[id] then table.insert(removeIds, id) end
	end
	for _, id in ipairs(sortedKeys(connected)) do
		local node = build.spec.nodes[id]
		if node.type ~= "ClassStart" and not node.ascendancyName then new = new + 1 end
		if not build.spec.allocNodes[id] then table.insert(addIds, id) end
	end
	return dkjson.encode({ currentPoints = current, newPoints = new, removeIds = removeIds, addIds = addIds,
		removed = nodeNames(removeIds), added = nodeNames(addIds) })
end

-- Allocated notables/keystones with everything that depends on them (PoB's node.depends
-- already includes masteries that would lose their last notable).
function listBranchesJSON()
	local branches = {}
	for _, id in ipairs(sortedKeys(build.spec.allocNodes)) do
		local node = build.spec.allocNodes[id]
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

-- Allocated small (Normal) main-tree nodes, for valuing travel nodes before re-pathing.
function listAllocatedNormalJSON()
	local ids = {}
	for _, id in ipairs(sortedKeys(build.spec.allocNodes)) do
		local node = build.spec.allocNodes[id]
		if node.type == "Normal" and not node.ascendancyName and id < 65536 then table.insert(ids, id) end
	end
	return dkjson.encode(ids)
end

-- Unallocated notables/keystones reachable within maxDist points, with PoB's own path to them.
-- request: { maxDist = n }
function listAdditionsJSON(requestText)
	local maxDist = dkjson.decode(requestText).maxDist or 6
	local additions = {}
	for _, id in ipairs(sortedKeys(build.spec.nodes)) do
		local node = build.spec.nodes[id]
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
	for _, id in ipairs(sortedKeys(build.spec.allocNodes)) do alloc[id] = build.spec.allocNodes[id] end
	for _, id in ipairs(request.removeIds or {}) do alloc[id] = nil end
	for _, id in ipairs(request.addIds or {}) do alloc[id] = build.spec.nodes[id] end
	local start
	for _, id in ipairs(sortedKeys(alloc)) do
		if alloc[id].type == "ClassStart" then start = alloc[id]; break end
	end
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
	for _, id in ipairs(sortedKeys(alloc)) do
		local node = alloc[id]
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
	local result = { nodes = jsonObject(), masteries = jsonObject() }
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
					local key = tostring(id)
					local m = result.masteries[key] or { name = node.dn, alloc = node.alloc == true,
						selected = build.spec.masterySelections[id], dist = node.pathDist, effects = jsonObject() }
					for effectId, ep in pairs(p.masteryEffects or {}) do
						local effect = build.spec.tree.masteryEffects[effectId]
						local e = m.effects[tostring(effectId)] or { text = effect and table.concat(effect.sd or {}, " / ") or "?", power = jsonObject() }
						e.power[statName] = { single = ep.singleStat, path = ep.pathPower }
						m.effects[tostring(effectId)] = e
					end
					result.masteries[key] = m
				else
					local n = result.nodes[tostring(id)] or { name = node.dn, type = node.type, alloc = node.alloc == true,
						dist = node.pathDist, power = jsonObject() }
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
	local result = jsonObject()
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
	local request = dkjson.decode(requestText)
	local results = {}
	for _, id in ipairs(sortedKeys(build.spec.allocNodes)) do
		local node = build.spec.allocNodes[id]
		local selected = build.spec.masterySelections[id]
		if node.type == "Mastery" and selected then
			local current = build.spec.tree.masteryEffects[selected]
			local entry = { masteryId = id, name = node.dn,
				current = current and table.concat(current.sd, " / ") or "?", options = {} }
			for _, option in ipairs(node.masteryEffects or {}) do
				local usedBy = isValueInTable(build.spec.masterySelections, option.effect)
				local effect = build.spec.tree.masteryEffects[option.effect]
				if effect and option.effect ~= selected and (not usedBy or usedBy == id) then
					local ctx = evaluateRequest(request, { removeNodes = { [node] = true },
						addNodes = { [masteryEffectNode(node, effect)] = true } })
					table.insert(entry.options, { effectId = option.effect,
						text = table.concat(effect.sd, " / "), ctx = ctx })
				end
			end
			table.sort(entry.options, function(a, b) return a.effectId < b.effectId end)
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
	local result = jsonObject()
	for _, id in ipairs(dkjson.decode(requestText).ids or {}) do
		local node = build.spec.nodes[id]
		if node then result[tostring(id)] = table.concat(node.sd or {}, "; ") end
	end
	return dkjson.encode(result)
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
	table.sort(diffs, function(a, b)
		local aDelta, bDelta = math.abs(a.to - a.from), math.abs(b.to - b.from)
		if aDelta ~= bDelta then return aDelta > bDelta end
		if a.type ~= b.type then return a.type < b.type end
		if a.stat ~= b.stat then return a.stat < b.stat end
		return a.source < b.source
	end)
	return dkjson.encode(diffs)
end
