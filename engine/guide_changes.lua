-- Persistent guide changes and reversible what-if changes.

local dkjson = require("dkjson")
local applyChange, sortedKeys = AuditCore.applyChange, AuditCore.sortedKeys

local function requireSlot(name)
	local slot = build.itemsTab.slots[name]
	if not slot then error("unknown item slot: " .. tostring(name)) end
	return slot
end

local function parseItem(raw, context)
	local item = new("Item"):Item(raw)
	if not item.base then error("unparseable item raw" .. (context and " for " .. context or "")) end
	item:NormaliseQuality()
	return item
end

local function gemIdByName(name)
	for _, id in ipairs(sortedKeys(data.gems)) do
		if data.gems[id].name == name then return id end
	end
	error("unknown gem: " .. tostring(name))
end

local function gemInstance(spec)
	return { nameSpec = spec.name, gemId = spec.gemId or gemIdByName(spec.name),
		level = spec.level, quality = spec.quality, qualityId = spec.qualityId or "Default",
		enabled = spec.enabled ~= false, enableGlobal1 = true, enableGlobal2 = false,
		count = spec.count or 1, skillPart = spec.skillPart }
end

local function groupAt(index)
	local group = build.skillsTab.socketGroupList[index]
	if not group then error("unknown socket group: " .. tostring(index)) end
	return group
end

local function gemAt(change)
	local group = groupAt(change.group)
	local gem = group.gemList[change.gemIndex]
	if not gem or not gem.gemData then error("gem not found at group " .. change.group .. " index " .. change.gemIndex) end
	return group, gem
end

local function snapshotGem(gem)
	local saved = {}
	for key, value in pairs(gem) do saved[key] = value end
	return saved
end

local function restoreGem(group, gem, saved)
	local keys = {}
	for key in pairs(gem) do table.insert(keys, key) end
	table.sort(keys)
	for _, key in ipairs(keys) do gem[key] = nil end
	for key, value in pairs(saved) do gem[key] = value end
	build.skillsTab:ProcessSocketGroup(group)
end

local function removeIdentity(list, wanted)
	for index, value in ipairs(list) do
		if value == wanted then table.remove(list, index); return end
	end
end

local function applyGemLevel(change)
	local group, gem = gemAt(change)
	if gem.gemData.name ~= change.name then
		error("expected gem " .. tostring(change.name) .. ", found " .. tostring(gem.gemData.name))
	end
	local saved = snapshotGem(gem)
	local ok, err = pcall(function()
		gem.level, gem.quality = change.level, change.quality
		if change.qualityId ~= nil then gem.qualityId = change.qualityId end
		build.skillsTab:ProcessSocketGroup(group)
	end)
	if not ok then restoreGem(group, gem, saved); error(err, 0) end
	return function() restoreGem(group, gem, saved) end
end

local function applyAddSupport(change)
	local group = groupAt(change.group)
	local gem = gemInstance(change.gem)
	table.insert(group.gemList, gem)
	local ok, err = pcall(function()
		build.skillsTab:ProcessSocketGroup(group)
		if not gem.gemData then error("gem not found after ProcessSocketGroup: " .. tostring(change.gem.name)) end
	end)
	if not ok then
		removeIdentity(group.gemList, gem); pcall(build.skillsTab.ProcessSocketGroup, build.skillsTab, group); error(err, 0)
	end
	return function()
		removeIdentity(group.gemList, gem)
		build.skillsTab:ProcessSocketGroup(group)
	end
end

local function applyReplaceSupport(change)
	local group, gem = gemAt(change)
	if gem.gemData.name ~= change.replaced then
		error("expected gem " .. tostring(change.replaced) .. ", found " .. tostring(gem.gemData.name))
	end
	local saved, replacement = snapshotGem(gem), gemInstance(change.gem)
	local ok, err = pcall(function()
		gem.gemId, gem.skillId, gem.nameSpec = replacement.gemId, nil, replacement.nameSpec
		build.skillsTab:ProcessSocketGroup(group)
		gem.level, gem.quality, gem.qualityId = replacement.level, replacement.quality, replacement.qualityId
		gem.enabled, gem.count, gem.skillPart = replacement.enabled, replacement.count, replacement.skillPart
		gem.enableGlobal1, gem.enableGlobal2 = true, false
		build.skillsTab:ProcessSocketGroup(group)
		if not gem.gemData then error("gem not found after ProcessSocketGroup: " .. change.gem.name) end
	end)
	if not ok then restoreGem(group, gem, saved); error(err, 0) end
	return function() restoreGem(group, gem, saved) end
end

local function applyAddGroup(change)
	local gems = {}
	for _, spec in ipairs(change.gems or {}) do table.insert(gems, gemInstance(spec)) end
	local group = { label = change.label, slot = change.slot, enabled = change.enabled ~= false,
		-- A guide group participates in Full DPS unless the change explicitly opts out.
		includeInFullDPS = change.fullDps ~= false, mainActiveSkill = 1, gemList = gems }
	table.insert(build.skillsTab.socketGroupList, group)
	local ok, err = pcall(function()
		build.skillsTab:ProcessSocketGroup(group)
		for _, gem in ipairs(group.gemList) do
			if not gem.gemData then error("gem not found after ProcessSocketGroup: " .. tostring(gem.nameSpec)) end
		end
	end)
	if not ok then
		removeIdentity(build.skillsTab.socketGroupList, group)
		pcall(build.skillsTab.ProcessSocketGroup, build.skillsTab, group)
		error(err, 0)
	end
	return function()
		build.skillsTab:ProcessSocketGroup(group)
		removeIdentity(build.skillsTab.socketGroupList, group)
	end
end

GuideCore.gemChange = { gemLevel = applyGemLevel, level = applyGemLevel,
	addSupport = applyAddSupport, replaceSupport = applyReplaceSupport, addGroup = applyAddGroup }

for name, apply in pairs(GuideCore.gemChange) do
	applyChange[name] = function(change) apply(change) end
end

applyChange.alloc = function(change)
	local target = build.spec.nodes[change.target]
	if not target then error("unknown node " .. tostring(change.target)) end
	if build.spec.allocNodes[change.target] then error("node already allocated " .. change.target) end
	if not target.path then error("no path to node " .. change.target) end
	local path, includes = {}, false
	for _, id in ipairs(change.nodes or {}) do
		local node = build.spec.nodes[id]
		if not node then error("unknown node " .. tostring(id)) end
		if id == change.target then includes = true end
		table.insert(path, node)
	end
	if not includes then error("allocation path must include target " .. change.target) end
	build.spec:AllocNode(target, path)
end

applyChange.dealloc = function(change)
	local target = build.spec.nodes[change.target]
	if not target then error("unknown node " .. tostring(change.target)) end
	if not build.spec.allocNodes[change.target] then error("node not allocated " .. change.target) end
	build.spec:DeallocNode(target)
end

applyChange.item = function(change)
	local specs = { { slot = requireSlot(change.slot), item = parseItem(change.raw, change.slot) } }
	for _, jewel in ipairs(change.abyssJewels or {}) do
		table.insert(specs, { slot = requireSlot(jewel.slot), item = parseItem(jewel.raw, jewel.slot) })
	end
	for _, row in ipairs(specs) do row.old = row.slot.selItemId end
	local flaskOld = specs[1].slot.active
	local flaskSetOld = build.itemsTab.activeItemSet[change.slot]
		and build.itemsTab.activeItemSet[change.slot].active
	local ok, err = pcall(function()
		for _, row in ipairs(specs) do
			row.added = true; build.itemsTab:AddItem(row.item, true); row.slot:SetSelItemId(row.item.id)
		end
		if change.flaskActive ~= nil and change.slot:match("^Flask") then
			local slot = specs[1].slot
			slot.active = change.flaskActive; build.itemsTab.activeItemSet[change.slot].active = change.flaskActive
			if slot.controls and slot.controls.activate then slot.controls.activate.state = change.flaskActive end
		end
		build.itemsTab:PopulateSlots()
		for _, row in ipairs(specs) do
			if row.slot.selItemId ~= row.item.id then
				error("PoB did not accept item " .. tostring(row.item.name) .. " in slot " .. row.slot.slotName)
			end
		end
		build.buildFlag = true
	end)
	if ok then return end
	for index = #specs, 1, -1 do
		local row = specs[index]; pcall(row.slot.SetSelItemId, row.slot, row.old)
		if row.added then pcall(build.itemsTab.DeleteItem, build.itemsTab, row.item, true) end
	end
	specs[1].slot.active = flaskOld
	if change.flaskActive ~= nil and change.slot:match("^Flask") then
		build.itemsTab.activeItemSet[change.slot].active = flaskSetOld
		local controls = specs[1].slot.controls
		if controls and controls.activate then controls.activate.state = flaskOld end
	end
	pcall(build.itemsTab.PopulateSlots, build.itemsTab)
	error(err, 0)
end

applyChange.compound = function(change)
	for _, subChange in ipairs(change.changes or {}) do
		local apply = applyChange[subChange.type] or error("unknown change type " .. tostring(subChange.type))
		apply(subChange)
	end
end

local function temporaryAbyss(jewels)
	local changed = {}
	local ok, err = pcall(function()
		for _, spec in ipairs(jewels or {}) do
			local slot = requireSlot(spec.slot)
			local old = slot.selItemId
			slot:SetSelItemId(0)
			local row = { slot = slot, old = old }
			table.insert(changed, row)
			if spec.raw then
				local item = parseItem(spec.raw, spec.slot)
				build.itemsTab:AddItem(item, true)
				row.item = item
				slot:SetSelItemId(item.id)
			end
		end
	end)
	local function undo()
		local firstError
		for index = #changed, 1, -1 do
			local row = changed[index]
			local okRestore, restoreError = pcall(row.slot.SetSelItemId, row.slot, row.old)
			if not okRestore and not firstError then firstError = restoreError end
			if row.item then
				local okDelete, deleteError = pcall(build.itemsTab.DeleteItem, build.itemsTab, row.item, true)
				if not okDelete and not firstError then firstError = deleteError end
			end
		end
		if firstError then error(firstError, 0) end
	end
	if not ok then undo(); error(err, 0) end
	return undo
end

function GuideCore.itemOverride(spec)
	local slot = requireSlot(spec.slot)
	local item = parseItem(spec.raw, spec.slot)
	local override = { repSlotName = spec.slot, repItem = item }
	local jewels, bySlot = {}, {}
	for _, jewel in ipairs(spec.jewels or {}) do bySlot[jewel.slot] = jewel end
	for index = 1, item.abyssalSocketCount or 0 do
		local name = spec.slot .. " Abyssal Socket " .. index
		table.insert(jewels, bySlot[name] or { slot = name })
		bySlot[name] = nil
	end
	for _, jewel in pairs(bySlot) do table.insert(jewels, jewel) end
	table.sort(jewels, function(a, b) return a.slot < b.slot end)
	if spec.flaskActive ~= nil and (item.type == "Flask" or item.type == "Tincture" or spec.slot:match("^Flask")) then
		if (slot.active == true) ~= spec.flaskActive then
			if item.type == "Tincture" then override.toggleTincture = item else override.toggleFlask = item end
		end
	end
	return override, temporaryAbyss(jewels)
end
