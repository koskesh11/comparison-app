-- Write attempts inside the booted PoB session (tests/comparison_app/pob/test_write_sandbox.py). The one argument is a
-- JSON list of operations; each runs under pcall and answers {ok, value, error}. Returns the answers as JSON.
local dkjson = require("dkjson")
local operations = dkjson.decode((...))

local function open(path, mode)
	local file = assert(io.open(path, mode))
	file:close()
	return "file"
end

local function debugNames()
	local names = {}
	for _, name in ipairs({ "getupvalue", "setupvalue", "upvaluejoin", "upvalueid", "getinfo", "getlocal", "sethook",
		"getregistry", "setmetatable" }) do
		if debug[name] ~= nil then names[#names + 1] = name end
	end
	return {
		present = names,
		traceback = type(debug.traceback),
		loaded = tostring(package.loaded.debug.getupvalue) .. tostring(require("debug").getupvalue),
		getupvalue = tostring(pcall(debug.getupvalue, io.open, 1)),
	}
end

local RUN = {
	open = function(op) return open(op.path, op.mode) end,
	write = function(op)
		local file = assert(io.open(op.path, op.mode or "wb"))
		file:write(op.text)
		file:close()
		return "written"
	end,
	read = function(op)
		local file = assert(io.open(op.path, "rb"))
		local size = #file:read("*a")
		file:close()
		return size
	end,
	output = function(op) return tostring(io.output(op.path)) end,
	remove = function(op) return assert(os.remove(op.path)) end,
	rename = function(op) return assert(os.rename(op.from, op.to)) end,
	popen = function(op) return tostring(io.popen(op.command)) end,
	execute = function(op) return tostring(os.execute(op.command)) end,
	makedir = function(op)
		MakeDir(op.path)
		return "done"
	end,
	removedir = function(op)
		RemoveDir(op.path, true)
		return "done"
	end,
	debug = debugNames,
}

local answers = {}
for index, op in ipairs(operations) do
	local ok, value = pcall(RUN[op.op], op)
	answers[index] = ok and { ok = true, value = value } or { ok = false, error = tostring(value) }
end
return dkjson.encode(answers)
