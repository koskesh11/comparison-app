-- A stand-in for loader.lua in a bare Lua state: rpc.lua with PoB's dkjson and endpoints that return or raise what
-- the tests need (tests/autobuilder/pob/test_wire.py, test_lua_host.py).
local luaDir, pobDir = ...
local dkjson = assert(loadfile(pobDir .. "/lua/dkjson.lua"))()
local Rpc = assert(loadfile(luaDir .. "/rpc.lua"))(dkjson)

Rpc.register("probe.echo", function(request) return request end)

Rpc.register("probe.numbers", function()
	return {
		inf = math.huge, ninf = -math.huge, nan = 0 / 0, plain = 7.5757, negative = -3, zero = -0.0,
		list = { 1, math.huge, 3 }, nested = { deeper = { value = -math.huge } },
		almostFour = 3.9999999999999996, long = 7176019.123456789, sum = 0.1 + 0.2, tiny = 5e-324, level = 98,
	}
end)

Rpc.register("probe.nothing", function() return nil end)

Rpc.register("probe.fail", function(request) Rpc.fail(request.kind, request.message) end)

Rpc.register("probe.crash", function(request) error(request.message) end)

Rpc.register("probe.crash_table", function() error({}) end)

Rpc.register("probe.cycle", function()
	local loop = {}
	loop.self = loop
	return loop
end)

Rpc.register("probe.function", function() return { f = print } end)

Rpc.register("probe.register_twice", function()
	Rpc.register("probe.echo", function() end)
end)

return Rpc.dispatch
