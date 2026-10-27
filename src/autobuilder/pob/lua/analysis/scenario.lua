-- The scenario (decision 010): PoB's "Is the enemy a Boss?" box for one calculation, never saved into the build.
-- One context replaces the first app's two: setConfig/restoreConfig (audit.lua:369-391), whose restore never
-- recalculated, so PoB kept the scenario's numbers (task 102, area A: CoC EK Assa FullDPS 14,420,419 instead of
-- 15,136,639), and guide_check_config.lua, which changed the inputs with no way back on an error.
-- Returns `withBoss(boss, read)` for the other endpoint files.
local Rpc, Build = ...

local BOSS_BOX = "enemyIsBoss" -- ConfigOptions.lua:2086

-- Runs read(build) with the config values set and the build recalculated in PoB's order, then puts every value back
-- exactly as it was (an unset box stays unset) and recalculates, on every path. If putting back fails, no build
-- counts as open, because its state is unknown.
local function withConfig(values, read)
	local build = Build.open()
	local input = build.configTab.input
	local previous = {}
	for var in pairs(values) do
		previous[var] = { value = input[var] }
	end
	local ok, result = xpcall(function()
		for var, value in pairs(values) do
			input[var] = value
		end
		build.configTab:BuildModList()
		Build.recalculate(build)
		return read(build)
	end, Rpc.asError)
	local restored, problem = xpcall(function()
		for var, saved in pairs(previous) do
			input[var] = saved.value
		end
		build.configTab:BuildModList()
		Build.recalculate(build)
	end, Rpc.asError)
	if not restored then
		Build.forget()
		Rpc.fail("BuildNotRestored", "PoB could not put the build back, load it again: " .. tostring(problem.message))
	end
	if not ok then error(result, 0) end
	return result
end

-- The box's values as PoB lists them (None, Boss, Pinnacle, Uber in PoB 2.67.2), read from PoB, not typed in here.
local function isBossValue(build, value)
	for _, item in ipairs(build.configTab.varControls[BOSS_BOX].list) do
		if item.val == value then return true end
	end
	return false
end

local function withBoss(boss, read)
	if type(boss) ~= "string" or not isBossValue(Build.open(), boss) then
		Rpc.fail("BadRequest", "the scenario needs one of PoB's values for " .. BOSS_BOX .. ", got " .. tostring(boss))
	end
	return withConfig({ [BOSS_BOX] = boss }, read)
end

Rpc.register("analysis.summary", function(request)
	return withBoss(request.boss, Build.summary)
end)

return { withBoss = withBoss }
