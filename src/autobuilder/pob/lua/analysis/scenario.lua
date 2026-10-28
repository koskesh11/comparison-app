-- The scenario (decision 010): PoB's "Is the enemy a Boss?" box for one calculation, never saved into the build.
-- Replaces the first app's two ways: setConfig/restoreConfig (audit.lua:369-391), whose restore never recalculated, so
-- PoB kept the scenario's numbers (task 102, area A: CoC EK Assa FullDPS 14,420,419 instead of 15,136,639), and
-- guide_check_config.lua, which changed the inputs with no way back on an error. The change runs through
-- Build.withChanges, which recalculates after it and after its undo, on every path.
-- Returns `boss(value)`: the change for the other endpoint files.
local Rpc, Build = ...

local BOSS_BOX = "enemyIsBoss" -- ConfigOptions.lua:2086

-- The box's values as PoB lists them (None, Boss, Pinnacle, Uber in PoB 2.67.2), read from PoB, not typed in here.
local function isBossValue(build, value)
	for _, item in ipairs(build.configTab.varControls[BOSS_BOX].list) do
		if item.val == value then return true end
	end
	return false
end

-- The change that sets the box to `value`; its undo puts back exactly what was there (an unset box stays unset) and
-- lets PoB's BuildModList apply it again, which also resets the placeholders the box sets (ConfigOptions.lua:2086-2100).
local function boss(value)
	if type(value) ~= "string" or not isBossValue(Build.open(), value) then
		Rpc.fail("BadRequest", "the scenario needs one of PoB's values for " .. BOSS_BOX .. ", got " .. tostring(value))
	end
	return function(build)
		local input = build.configTab.input
		local before = input[BOSS_BOX]
		input[BOSS_BOX] = value
		build.configTab:BuildModList()
		return function()
			input[BOSS_BOX] = before
			build.configTab:BuildModList()
		end
	end
end

Rpc.register("analysis.summary", function(request)
	return Build.withChanges({ boss(request.boss) }, Build.summary, request.which)
end)

return { boss = boss }
