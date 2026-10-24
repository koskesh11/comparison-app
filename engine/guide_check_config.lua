local dkjson = require("dkjson")

function guideConfigSwapJSON(requestText)
	local request = dkjson.decode(requestText)
	local input = build.configTab.input
	local previous, clear = {}, {}
	local touched = {}
	for var in pairs(request.values or {}) do touched[var] = true end
	for _, var in ipairs(request.clear or {}) do touched[var] = true end
	for var in pairs(touched) do
		if input[var] == nil then table.insert(clear, var) else previous[var] = input[var] end
	end
	for var, value in pairs(request.values or {}) do input[var] = value end
	for _, var in ipairs(request.clear or {}) do input[var] = nil end
	table.sort(clear)
	build.configTab:BuildModList()
	build.buildFlag = true
	build.calcsTab:BuildOutput()
	AuditCore.resetCalc()
	return dkjson.encode({ values = previous, clear = clear })
end
