-- Makes the open build's next `count` BuildOutput calls raise (tests/autobuilder/pob/conftest.py, fail_output): PoB
-- failing halfway through a change. The instance field shadows CalcsTab's method and removes itself after the last
-- failure; count 0 removes it at once.
local count = tonumber((...))
local calcsTab = main.modes.BUILD.calcsTab
calcsTab.BuildOutput = nil
if count == 0 then return "off" end
calcsTab.BuildOutput = function()
	count = count - 1
	if count == 0 then calcsTab.BuildOutput = nil end
	error("forced failure in BuildOutput (test)", 0)
end
return "armed"
