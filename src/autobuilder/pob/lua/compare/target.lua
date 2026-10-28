-- The target build (decision 009, card 109): PoB's own CompareEntry, loaded from XML text in the same session as the
-- owner's build, as PoB's compare tab does (CompareTab.lua:1246). Rewrites the first app's guide.lua:1-46, which kept
-- the target in an implicit global. One target at a time; the other endpoints reach it as Build.open("target").
local Rpc, Build = ...

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
	return Build.summary(entry)
end)

Rpc.register("target.release", function()
	Build.setTarget(nil)
	collectgarbage()
	return true
end)
