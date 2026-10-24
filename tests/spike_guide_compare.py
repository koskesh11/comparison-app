"""T1 spike (task 010, eng review E3): the guide as a CompareEntry in the player's headless state.

usage:  python tests/spike_guide_compare.py [--mode primary|fallback] [--player KEY]
Prints one JSON object: timings (s), Lua memory (MB, collectgarbage count) and process working set (MB).
Not a pass/fail test; the numbers go to tasks/reports/010-eng.md. Reads only; writes the decoded guide XML to a temp dir.
"""

import argparse
import base64
import ctypes
import json
import sys
import tempfile
import time
import zlib
from ctypes import wintypes
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden_common as gc  # noqa: E402
from pobhost import PobEngine, _lua_str  # noqa: E402

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "pobb_F8CiRC9KVADl.code.txt"


class _Counters(ctypes.Structure):
    _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
        (n, ctypes.c_size_t) for n in ("PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                                       "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage",
                                       "QuotaNonPagedPoolUsage", "PagefileUsage", "PeakPagefileUsage")]


def working_set_mb() -> float:
    counters = _Counters()
    counters.cb = ctypes.sizeof(counters)
    handle = ctypes.windll.kernel32.GetCurrentProcess()
    ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.c_void_p(handle), ctypes.byref(counters), counters.cb)
    return round(counters.WorkingSetSize / 1048576, 1)


def decode_code(code: str) -> str:
    return zlib.decompress(base64.urlsafe_b64decode(code.strip())).decode("utf-8")


def lua_mb(engine) -> float:
    engine.run("collectgarbage('collect'); collectgarbage('collect')")
    return round(float(engine.run("return collectgarbage('count')")) / 1024, 1)


def mem(engine) -> dict:
    return {"luaMB": lua_mb(engine), "rssMB": working_set_mb()}


SPIKE_LUA = r'''
local xmlText = assert(io.open(%s, "rb")):read("*a")
local t0 = os.clock()
local entry = new("CompareEntry"):CompareEntry(xmlText, "Guide")
local loadS = os.clock() - t0
local ok = entry and entry.calcsTab and entry.calcsTab.mainOutput ~= nil
_G.__guide = entry
return string.format("%%s|%%f|%%s|%%s", tostring(ok), loadS, tostring(entry.spec and entry.spec.treeVersion),
	tostring(entry.spec and entry.spec.curAscendClassName))
'''

POWER_LUA = r'''
local tab = build.compareTab
local stat
for _, s in ipairs(data.powerStatList) do if s.stat == "FullDPS" then stat = s end end
tab.primaryBuild = tab.primaryBuild or build
local peak = 0
debug.sethook(function() local c = collectgarbage("count"); if c > peak then peak = c end end, "", 20000)
local t0 = os.clock()
tab:ComparePowerBuilder(_G.__guide, stat, tab.comparePowerCategories)
local elapsed = os.clock() - t0
debug.sethook()
local n = tab.comparePowerResults and #tab.comparePowerResults or -1
return string.format("%f|%d|%f", elapsed, n, peak / 1024)
'''

RELEASE_LUA = "_G.__guide = nil; collectgarbage('collect'); collectgarbage('collect'); return 'ok'"


def timed(fn):
    start = time.perf_counter()
    result = fn()
    return result, round(time.perf_counter() - start, 2)


def run_evaluate(engine, keys: list[str]) -> float:
    request = json.dumps({"removeNodes": [], "addNodes": [], "stats": keys, "extraSkills": []})
    _, seconds = timed(lambda: engine.run(f"return evaluateJSON({_lua_str(request)})"))
    return seconds


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["primary", "fallback"], default="primary")
    parser.add_argument("--player", default="EK")
    args = parser.parse_args()
    xml_dir = Path(tempfile.mkdtemp(prefix="guide_spike_"))
    guide_xml = xml_dir / "guide.xml"
    guide_xml.write_text(decode_code(FIXTURE.read_text()), encoding="utf-8")
    out: dict = {"mode": args.mode, "player": args.player}
    with gc.pob_cwd():
        engine = PobEngine()
        try:
            out["afterBoot"] = mem(engine)
            if args.mode == "fallback":
                # guide first as the primary build, one build in memory at a time
                _, out["guideAsPrimarySeconds"] = timed(lambda: engine.load_build(guide_xml))
                out["afterGuidePrimary"] = mem(engine)
            _, out["playerLoadSeconds"] = timed(lambda: engine.load_build(gc.build_path(gc.RAW_BUILDS[args.player])))
            out["afterPlayer"] = mem(engine)
            engine.run(f"dofile({_lua_str((gc.ENGINE_DIR / 'audit.lua').as_posix())})")
            out["evaluateKeys"] = len(gc.RAW_KEYS)
            out["evaluateSeconds"] = run_evaluate(engine, gc.RAW_KEYS)
            if args.mode == "primary":
                row, out["guideLoadWall"] = timed(lambda: engine.run(SPIKE_LUA % _lua_str(guide_xml.as_posix())))
                ok, load_s, tree_version, ascendancy = row.split("|")
                out.update(guideLoaded=ok, guideLoadLuaSeconds=round(float(load_s), 2), guideTree=tree_version,
                           guideAscendancy=ascendancy)
                out["afterGuideLoaded"] = mem(engine)
                row, out["powerWall"] = timed(lambda: engine.run(POWER_LUA))
                power_s, rows, peak_mb = row.split("|")
                out.update(powerLuaSeconds=round(float(power_s), 2), powerRows=int(rows),
                           powerPeakLuaMB=round(float(peak_mb), 1))
                out["afterPower"] = mem(engine)
                out["evaluateWithGuideLoadedSeconds"] = run_evaluate(engine, gc.RAW_KEYS)
                engine.run(RELEASE_LUA)
                out["afterRelease"] = mem(engine)
            out["peakRssMB"] = working_set_mb()
        finally:
            gc.close_engine(engine) if hasattr(gc, "close_engine") else engine.close()
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
