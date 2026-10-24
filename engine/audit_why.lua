-- PoB-derived requirements for guide-check explanations, loaded by audit.lua

local dkjson = require("dkjson")

local function baseEnv()
	local calcs = build.calcsTab.calcs
	local env = calcs.initEnv(build, "CALCULATOR", {})
	calcs.perform(env)
	return env
end

function modNeedsJSON(requestText)
	local request = dkjson.decode(requestText)
	local conditions = baseEnv().player.modDB.conditions
	local result = {}
	for _, line in ipairs(request.lines or {}) do
		local parsed = modLib.parseMod(line)
		local entry = { conditions = {}, flags = {} }
		for _, mod in ipairs(parsed or {}) do
			if mod.type == "FLAG" then table.insert(entry.flags, mod.name) end
			for _, tag in ipairs(mod) do
				if tag.type == "Condition" and tag.var then
					table.insert(entry.conditions, { var = tag.var, on = conditions[tag.var] == true })
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
	local limit = env.player.output.EnemyCurseLimit or build.calcsTab.mainOutput.EnemyCurseLimit
	local result = { limit = limit, slots = {}, curse = {} }
	for _, slot in ipairs(env.curseSlots or {}) do
		table.insert(result.slots, slot.name)
	end
	for _, gemId in ipairs(request.gemIds or {}) do
		local gem = data.gems[gemId]
		local effect = gem and gem.grantedEffect
		result.curse[gemId] = (effect and effect.skillTypes and effect.skillTypes[SkillType.AppliesCurse]) == true
	end
	return dkjson.encode(result)
end
