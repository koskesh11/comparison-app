-- Guide comparison entry orchestration. Loaded last by audit.lua.

local dkjson = require("dkjson")
local jsonObject, sortedKeys = AuditCore.jsonObject, AuditCore.sortedKeys
local NULL = dkjson.null

GuideCore = {
	jsonObject = jsonObject,
	encode = function(value) return dkjson.encode(value) end,
}

dofile(ENGINE_DIR .. "/guide_snapshot.lua")
dofile(ENGINE_DIR .. "/guide_changes.lua")

local function collectGuide()
	_G.__guide = nil
	collectgarbage("collect")
	collectgarbage("collect")
end

function guideReleaseJSON()
	collectGuide()
	return "ok"
end

function guideLoadJSON(requestText)
	local request = dkjson.decode(requestText)
	collectGuide()
	local ok, entry = pcall(function()
		local file, openError = io.open(request.xmlPath, "rb")
		if not file then error(openError or "could not open guide XML") end
		local xml = file:read("*a")
		file:close()
		return new("CompareEntry"):CompareEntry(xml, request.label)
	end)
	if not ok then collectGuide(); return GuideCore.encode({ ok = false, error = tostring(entry) }) end
	if not (entry.calcsTab and entry.calcsTab.mainOutput) then
		collectGuide()
		return GuideCore.encode({ ok = false, error = "guide calculation output is unavailable" })
	end
	_G.__guide = entry
	return GuideCore.encode({ ok = true, treeVersion = entry.spec.treeVersion,
		ascendancy = entry.spec.curAscendClassName and entry.spec.curAscendClassName ~= ""
			and entry.spec.curAscendClassName ~= "None"
			and entry.spec.curAscendClassName or NULL })
end

local function powerStat(name)
	for _, entry in ipairs(data.powerStatList) do if entry.stat == name then return entry end end
	error("unknown power stat: " .. tostring(name))
end

local function restoreCompare(tab, primary, results, buildFlag)
	tab.primaryBuild = primary
	tab.comparePowerResults = results
	build.buildFlag = buildFlag
end

local function saveItemRaws()
	local saved = {}
	for _, item in pairs(build.itemsTab.items) do table.insert(saved, { item = item, raw = item.raw }) end
	table.sort(saved, function(a, b) return a.item.id < b.item.id end)
	return saved
end

local function restoreItemRaws(saved)
	for _, row in ipairs(saved) do row.item.raw = row.raw end
end

local function tinyEntry()
	local entry = new("CompareEntry"):CompareEntry(build:SaveDB(build.buildName), "Probe")
	local candidates = {}
	for _, id in ipairs(sortedKeys(entry.spec.nodes)) do
		local node = entry.spec.nodes[id]
		if #candidates < 12 and not entry.spec.allocNodes[id] and id < 65536 and not node.ascendancyName
			and (node.type == "Normal" or node.type == "Notable") and (node.modKey or "") ~= ""
			and node.pathDist == 1 and node.path then
			table.insert(candidates, node)
		end
	end
	for _, node in ipairs(candidates) do entry.spec:AllocNode(node, node.path) end
	return entry
end

function probeJSON()
	local tab = build.compareTab
	local classOk = pcall(new, "CompareEntry")
	local result = { compareTab = tab ~= nil,
		comparePowerBuilder = tab and type(tab.ComparePowerBuilder) == "function" or false,
		compareEntry = classOk, pobVersion = launch.versionNumber, fields = {}, tinyRows = 0 }
	if not (result.comparePowerBuilder and classOk) then return GuideCore.encode(result) end
	local oldPrimary, oldResults, oldFlag = tab.primaryBuild, tab.comparePowerResults, build.buildFlag
	local oldRaws = saveItemRaws()
	local entry
	local ok, err = pcall(function()
		entry = tinyEntry()
		tab.primaryBuild = build
		tab:ComparePowerBuilder(entry, powerStat("Life"), { treeNodes = true })
		-- CI builds have fixed Life = 1, so PoB correctly filters every Life row as zero.
		-- Keep the required Life run, then use another real row only to expose the installed row schema.
		if #(tab.comparePowerResults or {}) == 0 then
			tab:ComparePowerBuilder(entry, powerStat("TotalEHP"), { treeNodes = true })
		end
		result.tinyRows = #(tab.comparePowerResults or {})
		if result.tinyRows > 0 then result.fields = sortedKeys(tab.comparePowerResults[1]) end
	end)
	restoreCompare(tab, oldPrimary, oldResults, oldFlag)
	restoreItemRaws(oldRaws)
	entry = nil
	collectgarbage("collect"); collectgarbage("collect")
	if not ok then error(err, 0) end
	return GuideCore.encode(result)
end

local function sortedIds(list)
	local ids = {}
	for _, node in ipairs(list or {}) do table.insert(ids, node.id) end
	table.sort(ids)
	return ids
end

local function nodeInfo(node)
	local allocated = build.spec.allocNodes[node.id] ~= nil
	return { name = node.dn, type = node.type, ascendancy = node.ascendancyName or NULL,
		cluster = node.id >= 65536, conquered = node.conqueredBy ~= nil,
		modKeyEmpty = (node.modKey or "") == "", path = allocated and NULL or (node.path and sortedIds(node.path) or NULL),
		pathDist = node.pathDist or NULL, depends = allocated and (node.depends and sortedIds(node.depends) or NULL) or NULL }
end

function treeInfoJSON(requestText)
	local request, nodes = dkjson.decode(requestText), jsonObject()
	local wanted = {}
	for _, id in ipairs(request.ids or {}) do wanted[id] = true end
	for _, id in ipairs(request.removeIds or {}) do wanted[id] = true end
	for _, id in ipairs(sortedKeys(wanted)) do
		local node = build.spec.nodes[id]
		if node then nodes[tostring(id)] = nodeInfo(node) end
	end
	return GuideCore.encode({ nodes = nodes })
end

local function categorySet(categories)
	if categories == nil then
		return { treeNodes = true, items = true, skillGems = true, supportGems = true, config = true }
	end
	local result = {}
	for _, name in ipairs(categories) do result[name] = true end
	return result
end

local function projectPowerRows(rows)
	local result = {}
	for _, row in ipairs(rows or {}) do
		table.insert(result, { category = row.category, name = row.name, nodeId = row.nodeId or NULL,
			slotName = row.slotName or NULL, impact = row.impact, impactStr = row.impactStr,
			impactPercent = row.impactPercent, pathDist = row.pathDist or NULL, perPoint = row.perPoint or NULL })
	end
	table.sort(result, function(a, b)
		if a.category ~= b.category then return a.category < b.category end
		if a.name ~= b.name then return a.name < b.name end
		return (a.nodeId == NULL and -1 or a.nodeId) < (b.nodeId == NULL and -1 or b.nodeId)
	end)
	return result
end

function guidePowerJSON(requestText)
	if not _G.__guide then error("no guide loaded") end
	local request = dkjson.decode(requestText)
	local tab = build.compareTab
	local oldPrimary, oldResults, oldFlag = tab.primaryBuild, tab.comparePowerResults, build.buildFlag
	local ok, rows = pcall(function()
		tab.primaryBuild = build
		tab:ComparePowerBuilder(_G.__guide, powerStat("FullDPS"), categorySet(request.categories))
		return projectPowerRows(tab.comparePowerResults)
	end)
	restoreCompare(tab, oldPrimary, oldResults, oldFlag)
	AuditCore.resetCalc()
	if not ok then error(rows, 0) end
	return GuideCore.encode(rows)
end

local baseEvaluateJSON = evaluateJSON

function evaluateJSON(requestText)
	local request = dkjson.decode(requestText)
	if request.repItem == nil and request.gemChange == nil then return baseEvaluateJSON(requestText) end
	local override = { removeNodes = AuditCore.nodeSet(request.removeNodes), addNodes = AuditCore.nodeSet(request.addNodes) }
	local undos = {}
	local ok, result = pcall(function()
		if request.repItem then
			local itemOverride, undo = GuideCore.itemOverride(request.repItem)
			for key, value in pairs(itemOverride) do override[key] = value end
			table.insert(undos, undo)
		end
		if request.gemChange then
			local apply = GuideCore.gemChange[request.gemChange.type]
			if not apply then error("unknown gem change type " .. tostring(request.gemChange.type)) end
			table.insert(undos, apply(request.gemChange))
		end
		return AuditCore.evaluateRequest(request, override)
	end)
	for index = #undos, 1, -1 do
		local undoOk, undoErr = pcall(undos[index])
		if not undoOk and ok then ok, result = false, undoErr end
	end
	AuditCore.resetCalc()
	if not ok then error(result, 0) end
	return GuideCore.encode(result)
end
