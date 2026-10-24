-- PoB-derived requirements for guide-check explanations, loaded by audit.lua

local dkjson = require("dkjson")

local function baseEnv()
	local calcs = build.calcsTab.calcs
	local env = calcs.initEnv(build, "CALCULATOR", {})
	calcs.perform(env)
	return env
end

-- "AffectedByPrecision" -> a skill the player can add, only when PoB has an active skill gem of that name
local function skillNames()
	local names = {}
	for _, gem in pairs(data.gems) do
		local effect = gem.grantedEffect
		if effect and not effect.support and gem.name then
			names[gem.name:gsub("[^%w]", "")] = gem.name
		end
	end
	return names
end

function modNeedsJSON(requestText)
	local request = dkjson.decode(requestText)
	local conditions = baseEnv().player.modDB.conditions
	local skills = skillNames()
	local result = {}
	for _, line in ipairs(request.lines or {}) do
		local parsed = modLib.parseMod(line)
		local entry = { conditions = {}, flags = {}, text = line }
		for _, mod in ipairs(parsed or {}) do
			if mod.type == "FLAG" then table.insert(entry.flags, mod.name) end
			for _, tag in ipairs(mod) do
				if tag.type == "Condition" and tag.var then
					local label = tag.var:match("^AffectedBy(.+)$")
					table.insert(entry.conditions, { var = tag.var, on = conditions[tag.var] == true,
						skill = label and skills[label] })
				end
			end
		end
		table.insert(result, entry)
	end
	return dkjson.encode(result)
end

function curseStateJSON(requestText)
	local request = dkjson.decode(requestText)
	local env = baseEnv()
	local modDB = env.player.modDB
	local limit = env.player.output.EnemyCurseLimit or build.calcsTab.mainOutput.EnemyCurseLimit
	-- CalcPerform.lua:3226-3227 and 3278-3311: only slots that are not ignoreHexLimit / socketedCursesHexLimit
	-- count against the limit; PoB appends the others after the limited slots
	local result = { limit = limit, slots = {}, curse = {}, mark = {},
		limitBypass = modDB:Flag(nil, "CursesIgnoreHexLimit") or modDB:Sum("BASE", nil, "SocketedCursesHexLimitValue") > 0 }
	for _, slot in ipairs(env.curseSlots or {}) do
		if not slot.ignoreHexLimit and not slot.socketedCursesHexLimit then
			table.insert(result.slots, slot.name)
		end
	end
	for _, gemId in ipairs(request.gemIds or {}) do
		local gem = data.gems[gemId]
		local types = gem and gem.grantedEffect and gem.grantedEffect.skillTypes
		result.curse[gemId] = (types and types[SkillType.AppliesCurse]) == true
		result.mark[gemId] = (types and types[SkillType.Mark]) == true
	end
	return dkjson.encode(result)
end
