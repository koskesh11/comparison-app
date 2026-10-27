-- PoB's own cell formatter, formatCalcVal (CalcFormat.lua:12-14), on the values of a JSON list of
-- {value, precision}; value is a number or "inf", "-inf", "nan", "-0" (tests/autobuilder/pob/test_number_format.py).
-- Returns the texts as a JSON list.
local dkjson = require("dkjson")
local SPECIAL = { inf = math.huge, ["-inf"] = -math.huge, nan = 0 / 0, ["-0"] = -0.0 }
local texts = {}
for index, case in ipairs(dkjson.decode((...))) do
	local value = SPECIAL[case.value] or case.value
	texts[index] = formatCalcVal(value, case.precision)
end
return dkjson.encode(texts)
