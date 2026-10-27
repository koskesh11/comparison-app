-- The endpoint table (docs/ARCHITECTURE.md, "Endpoints"; check F7). Each Lua file registers its endpoints once;
-- Python calls one by name through `dispatch`, the function loader.lua hands to pob/lua_host.py.
-- A request is one JSON object. A reply is an envelope: {ok = true, value = ...} or
-- {ok = false, error = {kind, message, traceback}}. inf, -inf and NaN are written as the JSON words Infinity,
-- -Infinity and NaN, which pob/wire.py reads as numbers (S12); dkjson alone writes them as null (dkjson.lua:293-295).
local dkjson = ...
local traceback = debug.traceback

local handlers = {}
local Rpc = {}

function Rpc.register(name, handler)
	if type(name) ~= "string" or type(handler) ~= "function" then
		error("Rpc.register needs a name and a function", 2)
	end
	if handlers[name] then error("endpoint registered twice: " .. name, 2) end
	handlers[name] = handler
end

-- An error an endpoint raises on purpose; pob/wire.py turns `kind` into its own error class.
function Rpc.fail(kind, message)
	error({ kind = kind, message = message }, 0)
end

local function word(text)
	return setmetatable({}, { __tojson = function() return text end })
end

-- A copy of `value` that dkjson can write as it is: non-finite numbers become their JSON words.
local function writable(value, seen)
	if type(value) == "number" then
		if value ~= value then return word("NaN") end
		if value == math.huge then return word("Infinity") end
		if value == -math.huge then return word("-Infinity") end
		return value
	end
	if type(value) ~= "table" then return value end
	if seen[value] then error("the reply contains a table inside itself", 0) end
	seen[value] = true
	local copy = {}
	for key, item in pairs(value) do
		copy[key] = writable(item, seen)
	end
	seen[value] = nil
	return copy
end

-- dkjson raises on a value JSON cannot hold (a function, a table key that is not text or a number).
local function encode(envelope)
	return dkjson.encode(writable(envelope, {}))
end

local function asError(err)
	if type(err) == "table" and type(err.kind) == "string" then return err end
	local message = tostring(err)
	return { kind = "LuaError", message = message, traceback = traceback(message, 2) }
end

function Rpc.dispatch(name, requestText)
	local handler = handlers[name]
	if not handler then
		return encode({ ok = false, error = { kind = "UnknownEndpoint", message = "no endpoint named " .. name } })
	end
	local ok, reply = xpcall(function()
		local request, _, problem = dkjson.decode(requestText, 1, nil)
		if problem or type(request) ~= "table" then Rpc.fail("BadRequest", "the request is not a JSON object") end
		return encode({ ok = true, value = handler(request) })
	end, asError)
	if ok then return reply end
	return encode({ ok = false, error = reply })
end

return Rpc
