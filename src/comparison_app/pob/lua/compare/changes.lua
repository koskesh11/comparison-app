-- Decision 011's button: the chain of the build (or the target) with skill settings changed in memory, the file never
-- touched. Rewrites the first app's guide_changes.lua :1-152 and guide.lua :182-209: every change is one field PoB
-- saves and loads (SkillsTab.lua:447-513; Build.lua's mainSocketGroup), set through Build.withChanges, so the build
-- is recalculated in PoB's order and put back newest first on every path, errors included.
local Rpc, Build, Scenario, Chain, Stages = ...

-- ChangeKind (pob/endpoints.py) -> where the field lives and its name.
local KINDS = {
	["gem.skill_part"] = { on = "gem", field = "skillPart" },
	["gem.stage_count"] = { on = "gem", field = "skillStageCount" },
	["gem.mine_count"] = { on = "gem", field = "skillMineCount" },
	["gem.minion"] = { on = "gem", field = "skillMinion" },
	["gem.minion_skill"] = { on = "gem", field = "skillMinionSkill" },
	["gem.count"] = { on = "gem", field = "count" },
	["group.count"] = { on = "group", field = "groupCount" },
	["group.main_active_skill"] = { on = "group", field = "mainActiveSkill" },
	["build.main_group"] = { on = "build", field = "mainSocketGroup" },
}

local function target(build, change, kind)
	if kind.on == "build" then return build end
	local group = build.skillsTab.socketGroupList[change.group]
	if not group then Rpc.fail("BadRequest", "no skill group " .. tostring(change.group)) end
	if kind.on == "group" then return group end
	local gem = group.gemList[change.gem]
	if not gem then Rpc.fail("BadRequest", "no gem " .. tostring(change.gem) .. " in group " .. change.group) end
	return gem
end

-- One change: sets the field, returns its undo. A missing value unsets the field, as a box left empty in PoB does.
-- "build.stage" switches all four sets of a stage instead (compare/stages.lua, decision 026).
local function change(request)
	if request.kind == "build.stage" then return Stages.stage(request.value) end
	local kind = KINDS[request.kind]
	if not kind then Rpc.fail("BadRequest", "unknown change kind " .. tostring(request.kind)) end
	local value = request.value
	if value ~= nil and type(value) ~= "number" and type(value) ~= "string" then
		Rpc.fail("BadRequest", "a change's value is a number or text, got " .. type(value))
	end
	return function(build)
		local tbl = target(build, request, kind)
		local before = tbl[kind.field]
		tbl[kind.field] = value
		return function() tbl[kind.field] = before end
	end
end

-- The chain under the scenario with the changes applied first, so the Calcs tab is pointed at the changed skill, and
-- every number of the sidebar's output after them (the header's DPS; tests/comparison_app/compare/
-- test_recalc_matches_apply.py compares both with a saved copy of the change).
Rpc.register("compare.chain_with", function(request)
	local changes = {}
	for index, each in ipairs(request.changes or {}) do changes[index] = change(each) end
	changes[#changes + 1] = Scenario.boss(request.boss, request.which)
	changes[#changes + 1] = Chain.calcsOnSidebar
	return Build.withChanges(changes, function(build)
		return { chain = Chain.read(build), output = Build.outputNumbers(build.calcsTab.mainOutput) }
	end, request.which)
end)
