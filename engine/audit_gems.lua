-- Gem audit hooks (levels, swaps, replacements), loaded by audit.lua

local dkjson = require("dkjson")
local evaluateRequest, pickStats, sortedKeys, applyChange, mainGroup, resetCalc = AuditCore.evaluateRequest,
	AuditCore.pickStats, AuditCore.sortedKeys, AuditCore.applyChange, AuditCore.mainGroup, AuditCore.resetCalc

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

function listGemsJSON()
	local gems = {}
	for gi, group in ipairs(build.skillsTab.socketGroupList) do
		if group.enabled ~= false then
			for i, gem in ipairs(group.gemList) do
				if gem.enabled and gem.gemData then
					table.insert(gems, { group = gi, gemIndex = i,
						groupLabel = group.displayLabel or group.label or dkjson.null,
						isMainGroup = gi == build.mainSocketGroup, name = gem.gemData.name,
						gemId = gem.gemId or dkjson.null, level = gem.level, quality = gem.quality,
						support = gem.gemData.grantedEffect.support == true,
						granted = group.source ~= nil, source = group.source or dkjson.null })
				end
			end
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
			local ok, err = pcall(function()
				for _, target in ipairs(targets) do
					gem.level, gem.quality = target.level, target.quality
					local out = recalc()
					table.insert(results.gems, { gem = gem.gemData.name, from = level .. "/" .. quality,
						to = target.level .. "/" .. target.quality, out = out, ctx = evaluateRequest(request),
						fromLevel = level, fromQuality = quality, toLevel = target.level, toQuality = target.quality })
				end
			end)
			gem.level, gem.quality = level, quality
			if not ok then recalc(); resetCalc(); error(err, 0) end
		end
	end
	recalc()
	resetCalc()
	return dkjson.encode(results)
end

local function snapshotGem(gem)
	local saved = {}
	for key, value in pairs(gem) do saved[key] = value end
	return saved
end

local function restoreGem(group, gem, saved)
	local keys = {}
	for key in pairs(gem) do table.insert(keys, key) end
	for _, key in ipairs(keys) do gem[key] = nil end
	for key, value in pairs(saved) do gem[key] = value end
	build.skillsTab:ProcessSocketGroup(group)
end

local function gemIdByName(name)
	for _, id in ipairs(sortedKeys(data.gems)) do
		local gemData = data.gems[id]
		if gemData.name == name then return id, gemData end
	end
	error("unknown gem: " .. tostring(name))
end

local function resolveReplacement(r, index)
	local prefix = "replacement " .. tostring(index) .. ": "
	if type(r) ~= "table" then error(prefix .. "entry must be a table") end
	if type(r.group) ~= "number" then error(prefix .. "group must be a number") end
	if type(r.gemIndex) ~= "number" then error(prefix .. "gemIndex must be a number") end
	local group = build.skillsTab.socketGroupList[r.group]
	if not group then error(prefix .. "group " .. tostring(r.group) .. " does not exist") end
	local gem = group.gemList[r.gemIndex]
	if not gem or not gem.gemData then error(prefix .. "gem does not exist or has no gemData") end
	if gem.gemData.name ~= r.name then
		error(prefix .. "expected " .. tostring(r.name) .. ", found " .. tostring(gem.gemData.name))
	end
	local ok, id, gemData = pcall(gemIdByName, r.with)
	if not ok then error(prefix .. tostring(id)) end
	if type(r.level) ~= "number" then error(prefix .. "level must be a number") end
	if type(r.quality) ~= "number" then error(prefix .. "quality must be a number") end
	return group, gem, id, gemData
end

local function replaceGem(group, gem, id, level, quality)
	gem.gemId, gem.skillId = id, nil
	build.skillsTab:ProcessSocketGroup(group)
	gem.level, gem.quality = level, quality
	build.skillsTab:ProcessSocketGroup(group)
	return gem.level, gem.quality
end

local function validateReplacements(replacements)
	local resolved, seen = {}, {}
	for index, replacement in ipairs(replacements) do
		local group, gem, id, gemData = resolveReplacement(replacement, index)
		local key = tostring(replacement.group) .. ":" .. tostring(replacement.gemIndex)
		if seen[key] then error("replacement " .. index .. ": duplicate group+gemIndex " .. key) end
		table.insert(resolved, { request = replacement, group = group, gem = gem, id = id, gemData = gemData })
		seen[key] = true
	end
	return resolved
end

local function evaluateSingleReplacement(entry, request)
	local saved = snapshotGem(entry.gem)
	local appliedLevel, appliedQuality
	local ok, ctx = pcall(function()
		appliedLevel, appliedQuality = replaceGem(entry.group, entry.gem, entry.id,
			entry.request.level, entry.request.quality)
		return evaluateRequest(request)
	end)
	restoreGem(entry.group, entry.gem, saved)
	if not ok then resetCalc(); error(ctx, 0) end
	return appliedLevel, appliedQuality, ctx
end

local function evaluateCombinedReplacements(entries, request)
	local saved = {}
	for index, entry in ipairs(entries) do saved[index] = snapshotGem(entry.gem) end
	local ok, ctx = pcall(function()
		for _, entry in ipairs(entries) do
			replaceGem(entry.group, entry.gem, entry.id, entry.request.level, entry.request.quality)
		end
		return evaluateRequest(request)
	end)
	for index = #entries, 1, -1 do restoreGem(entries[index].group, entries[index].gem, saved[index]) end
	if not ok then resetCalc(); error(ctx, 0) end
	return ctx
end

function auditGemReplaceJSON(requestText)
	local request = dkjson.decode(requestText)
	local replacements = request.replacements or {}
	local entries = validateReplacements(replacements)
	local single = setmetatable({}, { __jsontype = "array" })
	for index, entry in ipairs(entries) do
		local level, quality, ctx = evaluateSingleReplacement(entry, request)
		local r = replacements[index]
		table.insert(single, { group = r.group, gemIndex = r.gemIndex, name = r.name,
			with = r.with, level = level, quality = quality, ctx = ctx })
	end
	local combined = evaluateCombinedReplacements(entries, request)
	resetCalc()
	return dkjson.encode({ single = single, combined = combined })
end

local function supportsAnySkill(gemData, group)
	for _, skill in ipairs(group.displaySkillList or {}) do
		if calcLib.canGrantedEffectSupportActiveSkill(gemData.grantedEffect, skill) then return true end
	end
	return false
end

local function gemKey(name)
	local key = string.lower(name)
	key = (key:gsub(" support$", ""))
	return key:match("^%s*(.-)%s*$")
end

local function candidateLevel(request, candidate)
	if type(request.levels) == "table" then
		local key = gemKey(candidate.name)
		local target = request.levels[key]
		if not target then return nil end
		if type(target) ~= "table" or type(target.level) ~= "number" or type(target.quality) ~= "number" then
			error("levels[" .. key .. "]: level and quality must be numbers")
		end
		return target.level, target.quality
	end
	return candidate.naturalMaxLevel or 20, 20
end

local function trySupportCandidate(results, skipped, request, group, gem, effect, candidateId, candidate)
	local level, quality = candidateLevel(request, candidate)
	if level == nil then skipped[candidateId] = true; return end
	replaceGem(group, gem, candidateId, level, quality)
	local appliedLevel, appliedQuality = gem.level, gem.quality
	local ctx = evaluateRequest(request)
	local row = { replaced = gem.gemData and effect.name, with = candidate.name,
		level = appliedLevel, quality = appliedQuality, ctx = ctx }
	table.insert(results.swaps, row)
end

local function trySupportReplacements(results, skipped, request, group, gem, effect, linked, wanted)
	local saved = snapshotGem(gem)
	local ok, err = pcall(function()
		for _, candidateId in ipairs(sortedKeys(data.gems)) do
			local candidate = data.gems[candidateId]
			local ce = candidate.grantedEffect
			local selected = not wanted or wanted[effect.name .. "\0" .. candidate.name]
			if selected and ce.support and not ce.unsupported and not linked[ce.id]
				and supportsAnySkill(candidate, group) then
				trySupportCandidate(results, skipped, request, group, gem, effect, candidateId, candidate)
			end
		end
	end)
	restoreGem(group, gem, saved)
	if not ok then resetCalc(); error(err, 0) end
end

local function candidateSet(candidates)
	if candidates == nil then return nil end
	if type(candidates) ~= "table" then error("candidates must be an array") end
	local meta = getmetatable(candidates)
	if meta and meta.__jsontype == "object" then error("candidates must be an array") end
	local wanted = {}
	for index, candidate in ipairs(candidates) do
		if type(candidate) ~= "table" or type(candidate.replaced) ~= "string"
			or type(candidate.with) ~= "string" then
			error("candidates entry " .. index .. ": replaced and with must be strings")
		end
		wanted[candidate.replaced .. "\0" .. candidate.with] = true
	end
	return wanted
end

-- Try every compatible support gem in place of each linked support (except protected anchors).
-- request: { stats = {keys}, protected = {granted effect ids} }
function auditSupportSwapsJSON(requestText)
	local request = dkjson.decode(requestText)
	local wanted = candidateSet(request.candidates)
	local protected = {}
	for _, id in ipairs(request.protected or {}) do protected[id] = true end
	local group = mainGroup()
	local linked = {}
	for _, gem in ipairs(group.gemList) do
		if gem.gemData then linked[gem.gemData.grantedEffect.id] = true end
	end
	local results = { base = evaluateRequest(request),
		swaps = setmetatable({}, { __jsontype = "array" }) }
	local skipped = type(request.levels) == "table" and {} or nil
	for _, gem in ipairs(group.gemList) do
		local effect = gem.enabled and gem.gemData and gem.gemData.grantedEffect
		if effect and effect.support and not protected[effect.id] then
			trySupportReplacements(results, skipped, request, group, gem, effect, linked, wanted)
		end
	end
	if skipped then results.skipped = #sortedKeys(skipped) end
	resetCalc()
	return dkjson.encode(results)
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
	for _, id in ipairs(sortedKeys(data.gems)) do
		local gemData = data.gems[id]
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
			table.sort(diffs, function(a, b)
				local aDelta, bDelta = math.abs(a.to - a.from), math.abs(b.to - b.from)
				if aDelta ~= bDelta then return aDelta > bDelta end
				return a.stat < b.stat
			end)
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

applyChange.gem = function(change)
	local gem = findMainGem(change.name)
	gem.level, gem.quality = change.level, change.quality
end

applyChange.swap = function(change)
	local gem = findMainGem(change.replaced)
	local id, gemData = gemIdByName(change.with)
	local level = type(change.level) == "number" and change.level or gemData.naturalMaxLevel or 20
	local quality = type(change.quality) == "number" and change.quality or 20
	replaceGem(mainGroup(), gem, id, level, quality)
end

applyChange.replaceGem = function(change)
	local group, gem, id = resolveReplacement(change, 1)
	replaceGem(group, gem, id, change.level, change.quality)
end
