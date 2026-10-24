-- Stable guide/player snapshots for the pure-Python comparison layer.

local dkjson = require("dkjson")
local jsonObject, sortedKeys = AuditCore.jsonObject, AuditCore.sortedKeys
local NULL = dkjson.null

local function nullable(value)
	if value == nil or value == "" or value == "None" then return NULL end
	return value
end

local function activeItem(buildObj, slot)
	return slot and slot.selItemId ~= 0 and buildObj.itemsTab.items[slot.selItemId] or nil
end

local function activeModLines(item)
	local lines = {}
	for _, listName in ipairs(AuditCore.MOD_LISTS) do
		for _, line in ipairs(item[listName] or {}) do
			if item:CheckModLineVariant(line) then table.insert(lines, line.line) end
		end
	end
	return lines
end

local function abyssJewels(buildObj, slotName, item)
	local rows = {}
	for index = 1, item.abyssalSocketCount or 0 do
		local name = slotName .. " Abyssal Socket " .. index
		local jewel = activeItem(buildObj, buildObj.itemsTab.slots[name])
		if jewel then table.insert(rows, { slot = name, name = jewel.name, raw = jewel.raw or jewel:BuildRaw() }) end
	end
	table.sort(rows, function(a, b) return a.slot < b.slot end)
	return rows
end

local function snapshotItem(buildObj, slot)
	local item = activeItem(buildObj, slot)
	if not item or slot.parentSlot then return nil end
	local flask = NULL
	if slot.slotName:match("^Flask %d+$") then flask = slot.active == true end
	local socketAllocated = NULL
	if slot.nodeId then socketAllocated = buildObj.spec.allocNodes[slot.nodeId] ~= nil end
	return { slot = slot.slotName, name = item.name, title = item.title or NULL,
		base = item.baseName, rarity = item.rarity,
		variant = item.variantList and item.variantList[item.variant] or NULL,
		raw = item.raw or item:BuildRaw(), mods = activeModLines(item), corrupted = item.corrupted == true,
		flaskActive = flask, cluster = item.clusterJewel ~= nil,
		timeless = (item.baseName == "Timeless Jewel" or (item.name or ""):match("Timeless Jewel") ~= nil),
		abyssJewels = abyssJewels(buildObj, slot.slotName, item), socketNode = slot.nodeId or NULL,
		weaponSet = slot.weaponSet or NULL, socketAllocated = socketAllocated }
end

local function snapshotItems(buildObj)
	local rows = {}
	for _, slot in ipairs(buildObj.itemsTab.orderedSlots) do
		local row = snapshotItem(buildObj, slot)
		if row then table.insert(rows, row) end
	end
	table.sort(rows, function(a, b) return a.slot < b.slot end)
	return rows
end

local function gemFamily(gem)
	if not gem.gemData then return gem.nameSpec end
	local effect = gem.gemData.grantedEffect
	if effect.plusVersionOf and data.skills[effect.plusVersionOf] then return data.skills[effect.plusVersionOf].name end
	local variants = data.gemsByGameId[gem.gemData.gameId]
	local variantKey = ((gem.gemData.variantId or ""):gsub("Alt%u$", ""))
	local plain = variants and variants[variantKey]
	return plain and plain.name or gem.gemData.name
end

local function snapshotGem(gem)
	local effect = gem.gemData and gem.gemData.grantedEffect
	return { name = gem.gemData and gem.gemData.name or gem.nameSpec, gemId = gem.gemId or NULL,
		isSupport = effect and effect.support == true or false, level = gem.level, quality = gem.quality,
		qualityId = gem.qualityId or "Default", enabled = gem.enabled ~= false, count = gem.count or NULL,
		skillPart = gem.skillPart or NULL, family = gemFamily(gem) }
end

local function socketLimit(buildObj, group)
	if not group.slot then return NULL end
	local item = activeItem(buildObj, buildObj.itemsTab.slots[group.slot])
	if not item then return NULL end
	local count = 0
	for _, socket in ipairs(item.sockets or {}) do
		local color = type(socket) == "table" and socket.color or socket
		if color ~= "A" then count = count + 1 end
	end
	return count
end

local function snapshotGroups(buildObj)
	local rows = {}
	for index, group in ipairs(buildObj.skillsTab.socketGroupList) do
		local gems = {}
		for _, gem in ipairs(group.gemList or {}) do table.insert(gems, snapshotGem(gem)) end
		table.insert(rows, { index = index,
			label = group.label and group.label ~= "" and group.label or group.displayLabel or "",
			slot = group.slot or NULL, enabled = group.enabled ~= false, fullDps = group.includeInFullDPS == true,
			mainActiveSkill = group.mainActiveSkill or 1, socketLimit = socketLimit(buildObj, group),
			source = group.source or NULL, gems = gems })
	end
	return rows
end

local function tattooOverride(buildObj, id)
	local override = (buildObj.spec.hashOverrides or {})[id]
	if not override then return NULL end
	local plainNode = buildObj.spec.tree.nodes[id]
	local plainName = plainNode and plainNode.dn or NULL
	return jsonObject({ name = override.dn or NULL, lines = override.sd or {}, plain = plainName })
end

-- node id -> the socket whose cluster jewel provides it (nested clusters are followed by walking up this map)
local function clusterSockets(buildObj)
	local parents = {}
	for _, subGraph in pairs(buildObj.spec.subGraphs or {}) do
		for _, node in ipairs(subGraph.nodes) do
			parents[node.id] = subGraph.parentSocket.id
		end
	end
	return parents
end

local function snapshotNodes(buildObj)
	local rows = {}
	local sockets = clusterSockets(buildObj)
	for _, id in ipairs(sortedKeys(buildObj.spec.allocNodes)) do
		local node = buildObj.spec.allocNodes[id]
		table.insert(rows, { id = id, name = node.dn, type = node.type,
			ascendancy = node.ascendancyName or NULL, cluster = id >= 65536,
			conquered = node.conqueredBy ~= nil, modKeyEmpty = (node.modKey or "") == "",
			mastery = buildObj.spec.masterySelections[id] or NULL, socket = node.type == "Socket",
			override = tattooOverride(buildObj, id), socketNode = sockets[id] or NULL })
	end
	return rows
end

local function configDefault(entry)
	if entry.type == "check" then return false end
	if entry.type == "count" or entry.type == "integer" or entry.type == "float" then return 0 end
	return nil
end

local function snapshotConfig(buildObj)
	local rows = {}
	for _, entry in ipairs(require("Modules.ConfigOptions")) do
		if entry.var then
			local value = buildObj.configTab.input[entry.var]
			if value ~= nil and value ~= configDefault(entry) then
				table.insert(rows, { var = entry.var,
					label = type(entry.label) == "string" and entry.label or entry.var,
					type = entry.type, value = value })
			end
		end
	end
	table.sort(rows, function(a, b) return a.var < b.var end)
	return rows
end

local function setNames(buildObj)
	local items, skills, tree = buildObj.itemsTab, buildObj.skillsTab, buildObj.treeTab
	local itemSet = items.activeItemSet
	local skillSet = skills.skillSets and skills.skillSets[skills.activeSkillSetId]
	local spec = tree.specList and tree.specList[tree.activeSpec]
	local multiple = #(items.itemSetOrderList or {}) > 1 or #(skills.skillSetOrderList or {}) > 1
		or #(tree.specList or {}) > 1
	return { item = itemSet and itemSet.title or NULL, skill = skillSet and skillSet.title or NULL,
		spec = spec and spec.title or NULL, multiple = multiple }
end

local function mainSkillName(buildObj)
	local group = buildObj.skillsTab.socketGroupList[buildObj.mainSocketGroup]
	local index = group and (group.mainActiveSkill or 1)
	local skill = group and group.displaySkillList and group.displaySkillList[index]
	return skill and skill.activeEffect and skill.activeEffect.grantedEffect.name or NULL
end

local function handedness(buildObj)
	local weapon1 = activeItem(buildObj, buildObj.itemsTab.slots["Weapon 1"])
	local info = weapon1 and weapon1.base and data.weaponTypeInfo[weapon1.base.type]
	return { weapon1TwoHanded = info ~= nil and info.oneHand == false,
		weapon2 = activeItem(buildObj, buildObj.itemsTab.slots["Weapon 2"]) ~= nil }
end

function GuideCore.snapshot(which)
	local buildObj = which == "player" and build or which == "guide" and _G.__guide
	if which ~= "player" and which ~= "guide" then error("unknown snapshot source " .. tostring(which)) end
	if not buildObj then error("no guide loaded") end
	local used = buildObj.spec:CountAllocNodes()
	-- Modules/Build.lua:902 uses 99 level points + 23 quest points + PoB's ExtraPoints.
	local available = 99 + 23 + (buildObj.calcsTab.mainOutput.ExtraPoints or 0)
	return { schema = 1, which = which,
		label = which == "player" and buildObj.buildName or buildObj.label,
		pobVersion = launch.versionNumber, className = buildObj.spec.curClassName,
		ascendancy = nullable(buildObj.spec.curAscendClassName), level = buildObj.characterLevel,
		treeVersion = buildObj.spec.treeVersion, mainSkill = mainSkillName(buildObj), mainGroup = buildObj.mainSocketGroup,
		sets = setNames(buildObj), points = { used = used, available = available }, nodes = snapshotNodes(buildObj),
		groups = snapshotGroups(buildObj), items = snapshotItems(buildObj), config = snapshotConfig(buildObj),
		handedness = handedness(buildObj) }
end

function snapshotJSON(requestText)
	return GuideCore.encode(GuideCore.snapshot(dkjson.decode(requestText).which))
end
