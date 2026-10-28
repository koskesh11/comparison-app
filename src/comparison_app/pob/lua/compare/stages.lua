-- Build stages, PoB's loadouts (decision 026): each a tree, an item set, a skill set and a config set with one title.
-- The list and which stage is active come from PoB's own buildMode.SyncLoadouts (Modules/Build.lua:771-895), run on a
-- stand-in for the one dropdown it fills; a build whose active sets are not one stage gets PoB's "no loadout" (entry 1,
-- :894), which is decision 026's mixed build. Returns the stage switch for compare/changes.lua.
local Rpc, Build = ...

-- PoB's list and active stage for a build (the owner's or the target, PoB's CompareEntry, which has no dropdown).
local function loadouts(build)
	local stand = { list = {}, selected = 1 }
	function stand:SetSel(index) self.selected = index end
	build.controls = build.controls or {}
	local real = build.controls.buildLoadouts
	build.controls.buildLoadouts = stand
	local ok, problem = pcall(main.modes.BUILD.SyncLoadouts, build)
	build.controls.buildLoadouts = real
	if not ok then error(problem, 0) end
	local titles, active = {}, nil
	for index, entry in ipairs(stand.list) do
		if not entry:match("^%^7%^7") then -- PoB's own entries (headers, "New Loadout") start with ^7^7 (:860-864)
			titles[#titles + 1] = entry
			if index == stand.selected then active = entry end
		end
	end
	return titles, active
end

local function title(set) return set and set.title or "Default" end

-- The four sets' titles as they are active now, for the message on a mixed build.
local function parts(build)
	return {
		tree = title(build.treeTab.specList[build.treeTab.activeSpec]),
		items = title(build.itemsTab.itemSets[build.itemsTab.activeItemSetId]),
		skills = title(build.skillsTab.skillSets[build.skillsTab.activeSkillSetId]),
		config = title(build.configTab.configSets[build.configTab.activeConfigSetId]),
	}
end

Rpc.register("build.stages", function(request)
	local build = Build.open(request.which)
	local titles, active = loadouts(build)
	return { stages = titles, active = active, parts = parts(build) }
end)

-- PoB's set lookup for a loadout title, mirrored from the dropdown's callback (Build.lua:359-398): PoB keeps it in a
-- closure over the main build, which the target does not have. The first set whose title equals the stage, or, for a
-- title with a {link}, the set SyncLoadouts linked to it.
local function setId(orderList, sets, stage, links)
	for _, id in ipairs(orderList) do
		if stage == (sets[id].title or "Default") then return id end
		local link = stage:match("%{(%w+)%}")
		if link then return links[link] and links[link].setId end
	end
	return nil
end

local function specId(build, stage)
	for id, name in ipairs(build.treeTab:GetSpecList()) do
		if stage == name then return id end
		local link = stage:match("%{(%w+)%}")
		if link then return build.treeListSpecialLinks[link] and build.treeListSpecialLinks[link].setId end
	end
	return nil
end

-- The change that puts a build on a stage with PoB's own switches (TreeTab.lua:549, ItemsTab.lua:1591,
-- SkillsTab.lua:1478, ConfigTab.lua:1337), as the dropdown does (Build.lua:395-416); its undo puts the old sets back.
local function stage(wanted)
	if type(wanted) ~= "string" then Rpc.fail("BadRequest", "a stage change needs the stage's title") end
	return function(build)
		loadouts(build) -- fills the {link} tables setId reads
		local items, skills, configs = build.itemsTab, build.skillsTab, build.configTab
		local ids = {
			spec = specId(build, wanted),
			item = #items.itemSetOrderList == 1 and 1 or setId(items.itemSetOrderList, items.itemSets, wanted,
				build.itemListSpecialLinks),
			skill = #skills.skillSetOrderList == 1 and 1 or setId(skills.skillSetOrderList, skills.skillSets, wanted,
				build.skillListSpecialLinks),
			config = #configs.configSetOrderList == 1 and 1 or setId(configs.configSetOrderList, configs.configSets,
				wanted, build.configListSpecialLinks),
		}
		if not (ids.spec and ids.item and ids.skill and ids.config) then
			Rpc.fail("BadRequest", "the build has no stage " .. wanted)
		end
		local before = { build.treeTab.activeSpec, items.activeItemSetId, skills.activeSkillSetId, configs.activeConfigSetId }
		build.treeTab:SetActiveSpec(ids.spec)
		items:SetActiveItemSet(ids.item)
		skills:SetActiveSkillSet(ids.skill)
		configs:SetActiveConfigSet(ids.config)
		-- PoB's switch only swaps the sets and flags the build (SkillsTab.lua:1493-1497); the new skill set's skill lists
		-- come with a recalculation, which the changes after this one (the Calcs pointing) need
		Build.recalculate(build)
		return function()
			configs:SetActiveConfigSet(before[4])
			skills:SetActiveSkillSet(before[3])
			items:SetActiveItemSet(before[2])
			build.treeTab:SetActiveSpec(before[1])
		end
	end
end

-- The loaded build (or the target) put on a stage and left there, so every read of a comparison sees it (decision 026);
-- the file is never written, and loading the build again, or switching back, gives the saved state.
Rpc.register("build.set_stage", function(request)
	local build = Build.open(request.which)
	stage(request.stage)(build)
	local titles, active = loadouts(build)
	return { stages = titles, active = active, parts = parts(build) }
end)

return { stage = stage }
