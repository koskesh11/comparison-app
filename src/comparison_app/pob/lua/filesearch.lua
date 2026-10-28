-- Read-only Windows file enumeration for the headless PoB shim.
-- Results are copied into Lua tables so no OS handle escapes NewFileSearch.

local ffi = require("ffi")
if ffi.os ~= "Windows" then return end
local bit = require("bit")
local kernel32 = ffi.load("kernel32")

ffi.cdef [[
	typedef struct { uint32_t dwLowDateTime; uint32_t dwHighDateTime; } ab_FILETIME;
	typedef struct {
		uint32_t dwFileAttributes;
		ab_FILETIME ftCreationTime, ftLastAccessTime, ftLastWriteTime;
		uint32_t nFileSizeHigh, nFileSizeLow, dwReserved0, dwReserved1;
		uint16_t cFileName[260];
		uint16_t cAlternateFileName[14];
	} ab_WIN32_FIND_DATAW;
	void *FindFirstFileW(const uint16_t *lpFileName, ab_WIN32_FIND_DATAW *lpFindFileData);
	int FindNextFileW(void *hFindFile, ab_WIN32_FIND_DATAW *lpFindFileData);
	int FindClose(void *hFindFile);
	int MultiByteToWideChar(unsigned int CodePage, uint32_t dwFlags, const char *lpMultiByteStr, int cbMultiByte,
		uint16_t *lpWideCharStr, int cchWideChar);
	int WideCharToMultiByte(unsigned int CodePage, uint32_t dwFlags, const uint16_t *lpWideCharStr, int cchWideChar,
		char *lpMultiByteStr, int cbMultiByte, const char *lpDefaultChar, int *lpUsedDefaultChar);
]]

local CP_UTF8 = 65001
local DIRECTORY_ATTRIBUTE = 0x10
local UINT32_SCALE = 4294967296

local function toWide(value)
	local count = kernel32.MultiByteToWideChar(CP_UTF8, 0, value, -1, nil, 0)
	if count == 0 then return nil end
	local buffer = ffi.new("uint16_t[?]", count)
	if kernel32.MultiByteToWideChar(CP_UTF8, 0, value, -1, buffer, count) == 0 then return nil end
	return buffer
end

local function fromWide(value)
	local count = kernel32.WideCharToMultiByte(CP_UTF8, 0, value, -1, nil, 0, nil, nil)
	if count == 0 then return nil end
	local buffer = ffi.new("char[?]", count)
	if kernel32.WideCharToMultiByte(CP_UTF8, 0, value, -1, buffer, count, nil, nil) == 0 then return nil end
	return ffi.string(buffer, count - 1)
end

local function globToPattern(glob)
	local parts = { "^" }
	for index = 1, #glob do
		local char = glob:sub(index, index)
		if char == "*" then
			parts[#parts + 1] = ".*"
		elseif char == "?" then
			parts[#parts + 1] = "[\1-\127\194-\244][\128-\191]*"
		else
			parts[#parts + 1] = char:gsub("%W", "%%%0")
		end
	end
	parts[#parts + 1] = "$"
	return table.concat(parts)
end

local function collectEntries(handle, data, pattern, wantDirectory)
	local entries = {}
	repeat
		local found = data[0]
		local name = fromWide(found.cFileName)
		local isDirectory = bit.band(found.dwFileAttributes, DIRECTORY_ATTRIBUTE) ~= 0
		if name and name ~= "." and name ~= ".." and isDirectory == wantDirectory
				and name:lower():match(pattern) then
			entries[#entries + 1] = {
				name = name,
				size = tonumber(found.nFileSizeHigh) * UINT32_SCALE + tonumber(found.nFileSizeLow),
				modified = (tonumber(found.ftLastWriteTime.dwHighDateTime) * UINT32_SCALE
					+ tonumber(found.ftLastWriteTime.dwLowDateTime)) / 1e7 - 11644473600,
			}
		end
	until kernel32.FindNextFileW(handle, data) == 0
	return entries
end

local methods = {}

function methods:GetFileName()
	return self._entries[self._index].name
end

function methods:GetFileSize()
	return self._entries[self._index].size
end

function methods:GetFileModifiedTime()
	return self._entries[self._index].modified
end

function methods:NextFile()
	if self._index >= #self._entries then return false end
	self._index = self._index + 1
	return true
end

function NewFileSearch(spec, findDirectories)
	if type(spec) ~= "string" then
		error("NewFileSearch() argument 1: expected string, got " .. type(spec))
	end
	local wideSpec = toWide(spec:gsub("/", "\\"))
	if not wideSpec then return nil end
	local data = ffi.new("ab_WIN32_FIND_DATAW[1]")
	local handle = kernel32.FindFirstFileW(wideSpec, data)
	if tonumber(ffi.cast("intptr_t", handle)) == -1 then return nil end
	local ok, entries = pcall(function()
		local glob = spec:match("([^/\\]*)$"):lower()
		return collectEntries(handle, data, globToPattern(glob), not not findDirectories)
	end)
	kernel32.FindClose(handle)
	if not ok then error(entries, 0) end
	if #entries == 0 then return nil end
	return setmetatable({ _entries = entries, _index = 1 }, { __index = methods })
end
