-- Write sandbox for the headless PoB Lua state (task 025).
-- Loaded by pob_headless.lua before any PoB code. Every way this state can write a file goes through
-- one check: io.open with w/a/+ modes, io.output(name), os.remove, os.rename, io.popen, os.execute,
-- and the host helpers MakeDir / RemoveDir. Reads stay unrestricted.
-- Allowed write roots (normalised, case-insensitive, ".." resolved, whole path components only):
--   AUTOBUILDER_DIR/**              the app's own output (Documents/Path of Building/Builds/AutoBuilder)
--   POB_DIR/Data/TimelessJewelData/*.bin   PoB's one-time timeless-jewel cache (user decision 2026-10-22)
--   USERDATA_DIR/**                 the engine's own PoB user data (Settings.xml, logs); see engine/pobhost.py
-- Anything else raises a Lua error naming the refused path and the rule. Not covered: raw ffi/kernel32
-- calls and junctions inside an allowed root (pure Lua cannot resolve them).

local BAD_COMPONENT = '[%c<>:"|?*]'
local RULE = "write sandbox (task 025): allowed roots are Builds/AutoBuilder/, "
	.. "PoB Data/TimelessJewelData/*.bin and the engine userdata folder"

-- Returns the canonical form "c:/dir/file" (lower case) or nil when the path is not understood.
local function normalize(path, workDir)
	if type(path) ~= "string" or path == "" then return nil end
	local p = path:gsub("\\", "/"):gsub("^//[?.]/", "")
	local drive, rest = p:match("^(%a):(.*)$")
	if drive then
		if rest:sub(1, 1) ~= "/" then return nil end -- "C:foo" is drive-relative: refuse
	elseif p:sub(1, 2) == "//" then
		return nil -- UNC share: never allowed
	else
		if not workDir:match("^%a:/") then return nil end -- no absolute working dir to resolve against
		if p:sub(1, 1) ~= "/" then return normalize(workDir .. "/" .. p, workDir) end
		drive, rest = workDir:match("^(%a):"), p
	end
	local stack = { drive:lower() .. ":" }
	for part in rest:gmatch("[^/]+") do
		if part == ".." then
			if #stack == 1 then return nil end
			stack[#stack] = nil
		elseif part ~= "." then
			if part:find(BAD_COMPONENT) or part:find("[ .]$") then return nil end
			stack[#stack + 1] = part:lower()
		end
	end
	return table.concat(stack, "/")
end

local function buildRoots(workDir)
	local roots = {}
	local function add(dir, spec)
		local norm = dir and normalize(dir, workDir)
		if norm then spec.dir = norm; roots[#roots + 1] = spec end
	end
	add(AUTOBUILDER_DIR, {})
	add(USERDATA_DIR, {})
	add(POB_DIR and (POB_DIR .. "/Data/TimelessJewelData"), { flat = true, ext = ".bin" })
	return roots
end

local function inRoot(norm, root)
	local prefix = root.dir .. "/"
	if norm:sub(1, #prefix) ~= prefix then return false end
	local rest = norm:sub(#prefix + 1)
	if rest == "" then return false end
	if root.flat and rest:find("/", 1, true) then return false end
	if root.ext and (#rest <= #root.ext or rest:sub(-#root.ext) ~= root.ext) then return false end
	return true
end

local workDir = (POB_DIR or ""):gsub("\\", "/")
local roots = buildRoots(workDir)

local function allowed(path)
	local norm = normalize(path, workDir)
	if not norm then return false end
	for _, root in ipairs(roots) do
		if inRoot(norm, root) then return true end
	end
	return false
end

local function refuse(op, path)
	error(string.format("write refused: %s '%s' is outside the allowed write roots; rule: %s",
		op, tostring(path), RULE), 0)
end

local function guard(op, path)
	if not allowed(path) then refuse(op, path) end
end

local ioOpen, ioOutput, ioPopen = io.open, io.output, io.popen
local osRemove, osRename, osExecute = os.remove, os.rename, os.execute

function io.open(path, mode)
	if tostring(mode or "r"):find("[wa+]") then guard("io.open(" .. tostring(mode) .. ")", path) end
	return ioOpen(path, mode)
end

function io.output(target, ...)
	if type(target) == "string" then guard("io.output", target) end
	return ioOutput(target, ...)
end

function os.remove(path)
	guard("os.remove", path)
	return osRemove(path)
end

function os.rename(from, to)
	guard("os.rename (source)", from)
	guard("os.rename (target)", to)
	return osRename(from, to)
end

function io.popen(command, ...)
	refuse("io.popen (a child process can write anywhere)", command)
	return ioPopen(command, ...)
end

function os.execute(command, ...)
	if command ~= nil then refuse("os.execute (a child process can write anywhere)", command) end
	return osExecute(command, ...)
end

-- Host helpers (stubs in the headless host, but a real host would create/delete directories).
local function directoryExists(path)
	local probe = NewFileSearch and NewFileSearch((tostring(path):gsub("[/\\]+$", "")), true)
	return probe ~= nil
end

local hostMakeDir, hostRemoveDir = MakeDir, RemoveDir

function MakeDir(path)
	if not allowed(path) and not directoryExists(path) then refuse("MakeDir", path) end
	if hostMakeDir then return hostMakeDir(path) end
end

function RemoveDir(path, recurse)
	guard("RemoveDir", path)
	if hostRemoveDir then return hostRemoveDir(path, recurse) end
end

WriteSandbox = { allowed = allowed, normalize = function(path) return normalize(path, workDir) end }
