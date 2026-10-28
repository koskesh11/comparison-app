-- NewFileSearch in a bare Lua state (tests/comparison_app/pob/test_filesearch.py): loads filesearch.lua, searches
-- `spec` and returns every entry and whether NextFile stays false after the last, as JSON (null when nothing matched).
local luaDir, pobDir, spec, directories = ...
local dkjson = assert(loadfile(pobDir .. "/lua/dkjson.lua"))()
assert(loadfile(luaDir .. "/filesearch.lua"))()
local search = NewFileSearch(spec, directories == "1")
if not search then return dkjson.encode(dkjson.null) end
local entries = {}
repeat
	entries[#entries + 1] = {
		name = search:GetFileName(), size = search:GetFileSize(), modified = search:GetFileModifiedTime(),
	}
until not search:NextFile()
return dkjson.encode({ entries = entries, exhausted = not search:NextFile() })
