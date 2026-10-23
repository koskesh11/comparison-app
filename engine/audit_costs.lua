-- Cost / skill-set audit hooks, loaded by audit.lua

local dkjson = require("dkjson")
local calcAsMain, pickStats, sortedKeys, MOD_LISTS, slotItemInUse = AuditCore.calcAsMain, AuditCore.pickStats,
	AuditCore.sortedKeys, AuditCore.MOD_LISTS, AuditCore.slotItemInUse

local REACTIVE_SKILL_DATA = {
	"triggeredByDamageTaken",
	"chanceToTriggerOnStun",
	"chanceToTriggerOnWardBreak",
	"triggeredOnDeath",
	"chanceToTriggerCounterattackOnBlock",
	"chanceToTriggerCounterAttackOnHit",
}

local function reactiveMarker(skill)
	for _, key in ipairs(REACTIVE_SKILL_DATA) do
		if skill.skillData and skill.skillData[key] ~= nil and skill.skillData[key] ~= false then
			return "skillData." .. key
		end
	end
	local trigger = skill.triggeredBy
	local effect = trigger and trigger.grantedEffect
	for _, stat in ipairs(effect and effect.stats or {}) do
		if stat == "trigger_effect_group_on_block" then
			return effect.name .. " (trigger_effect_group_on_block)"
		end
	end
	return nil
end

function otherSkillsJSON(requestText)
	local request = dkjson.decode(requestText)
	local rows = {}
	for gi, group in ipairs(build.skillsTab.socketGroupList) do
		if gi ~= build.mainSocketGroup and group.enabled ~= false then
			for si in ipairs(group.displaySkillList or {}) do
				local out, skill = calcAsMain(gi, si, {})
				local marker = reactiveMarker(skill)
				table.insert(rows, {
					group = gi, index = si, name = skill.activeEffect.grantedEffect.name,
					label = group.displayLabel or group.label or dkjson.null,
					includeInFullDPS = group.includeInFullDPS == true,
					out = pickStats(out, request.stats), triggered = out.SkillTriggerRate ~= nil,
					reactive = marker ~= nil, reactiveBy = marker or dkjson.null,
				})
			end
		end
	end
	return dkjson.encode(rows)
end

local function addSource(lines, seen, kind, name, line)
	if type(line) ~= "string" or not line:lower():find("consecrated ground", 1, true) then return end
	local key = kind .. "\0" .. name .. "\0" .. line
	if not seen[key] then
		seen[key] = true
		table.insert(lines, { kind = kind, name = name, line = line })
	end
end

local function addItemSources(lines, seen)
	local listNames = {}
	for _, listName in ipairs(MOD_LISTS) do table.insert(listNames, listName) end
	table.insert(listNames, "buffModLines")
	for _, slot in ipairs(build.itemsTab.orderedSlots) do
		-- Flasks count regardless of slot.active: Bottled Faith is used during the fight even when toggled off in PoB.
		local item = slotItemInUse(slot)
		if item then
			for _, listName in ipairs(listNames) do
				for _, modLine in ipairs(item[listName] or {}) do
					local inactive = modLine.variantList and item.variant and not modLine.variantList[item.variant]
					if not inactive then addSource(lines, seen, "item", item.name, modLine.line) end
				end
			end
		end
	end
end

local function addNodeSources(lines, seen)
	for _, id in ipairs(sortedKeys(build.spec.allocNodes)) do
		local node = build.spec.allocNodes[id]
		for _, line in ipairs(node.sd or {}) do addSource(lines, seen, "node", node.dn, line) end
	end
end

local function addGemSources(lines, seen)
	for _, group in ipairs(build.skillsTab.socketGroupList) do
		if group.enabled ~= false then
			for _, gem in ipairs(group.gemList or {}) do
				if gem.enabled and gem.gemData then
					local data = gem.gemData
					addSource(lines, seen, "gem", data.name, data.grantedEffect and data.grantedEffect.description)
					addSource(lines, seen, "gem", data.name,
						data.secondaryGrantedEffect and data.secondaryGrantedEffect.description)
				end
			end
		end
	end
end

local function sourceLess(a, b)
	if a.kind ~= b.kind then return a.kind < b.kind end
	if a.name ~= b.name then return a.name < b.name end
	return a.line < b.line
end

function consecratedSourcesJSON()
	local lines, seen = {}, {}
	addItemSources(lines, seen)
	addNodeSources(lines, seen)
	addGemSources(lines, seen)
	table.sort(lines, sourceLess)
	return dkjson.encode({ lines = lines })
end
