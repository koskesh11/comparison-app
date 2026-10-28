-- The target build (decision 009, card 109): PoB's own CompareEntry, loaded from XML text in the same session as the
-- owner's build, as PoB's compare tab does (CompareTab.lua:1246). Rewrites the first app's guide.lua:1-46, which kept
-- the target in an implicit global. One target at a time; the other endpoints reach it as Build.open("target").
local Rpc, Build = ...

-- PoB saves party buffs as Party/ImportedBuffs text (PartyTab.lua:575-581) and reads only those back (:516-542). The
-- entry's Party tab is a stub (CompareEntry.lua:107-111), so a target's saved party buffs are not in its numbers.
local function usesParty(entry)
	for _, section in ipairs(entry.xmlSectionList or {}) do
		if section.elem == "Party" then
			for _, node in ipairs(section) do
				if type(node) == "table" and node.elem == "ImportedBuffs" and tostring(node[1] or ""):match("%S") then
					return true
				end
			end
		end
	end
	return false
end

Rpc.register("target.load", function(request)
	Build.setTarget(nil) -- every failure below, the request's own included, leaves no target
	if type(request.xml) ~= "string" or type(request.name) ~= "string" then
		Rpc.fail("BadRequest", "target.load needs the build's xml and name as text")
	end
	local entry = new("CompareEntry"):CompareEntry(request.xml, request.name)
	-- LoadFromXML reports a broken file only with ConPrintf and stops before the tabs exist (CompareEntry.lua:65-72).
	if not (entry.calcsTab and entry.calcsTab.mainOutput) then
		Rpc.fail("TargetNotLoaded", "PoB could not open the target build")
	end
	Build.setTarget(entry)
	local opened = Build.summary(entry)
	opened.usesParty = usesParty(entry)
	return opened
end)

Rpc.register("target.release", function()
	Build.setTarget(nil)
	collectgarbage()
	return true
end)
