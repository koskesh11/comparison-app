-- The sandbox's path rules in a bare Lua state (tests/autobuilder/pob/test_write_sandbox.py): loads sandbox.lua with
-- three folders and answers, for each further argument, whether a write there is allowed. Returns JSON booleans.
local luaDir, pobDir, userDir, writeRoot = ...
local paths = { select(5, ...) }
local dkjson = assert(loadfile(pobDir .. "/lua/dkjson.lua"))()
local sandbox = assert(loadfile(luaDir .. "/sandbox.lua"))(pobDir, userDir, writeRoot)
local answers = {}
for index, path in ipairs(paths) do
	answers[index] = sandbox.allowed(path)
end
return dkjson.encode(answers)
