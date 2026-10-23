"""Shared helpers for the golden regression baseline (tests/golden.json).

Used by tests/pin_golden.py (writes golden.json), tests/test_golden.py (reads it) and tests/perf_baseline.py.

HAZARD: PobEngine.__init__ does os.chdir(<PoB install>). Every path in here is absolute, and the cwd is
restored after each engine use (pob_cwd), so nothing can land in the install by a relative write.
"""

import contextlib
import ctypes
import hashlib
import json
import math
import os
import sys
from pathlib import Path
from unittest import mock

TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent
ENGINE_DIR = PROJECT_ROOT / "engine"
VAULT_DIR = PROJECT_ROOT / "vault"
GOLDEN_PATH = Path(os.environ.get("GOLDEN_JSON") or TESTS_DIR / "golden.json").resolve()  # env: negative tests
BUILDS_DIR = Path.home() / "Documents" / "Path of Building" / "Builds"
POB_INSTALL = Path(os.environ["APPDATA"]) / "Path of Building Community"
OFFLINE_LEAGUE = "Allflame"  # engine/cache/<league>/SkillGem.json, read only, never refreshed

if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

# A. Golden builds with the user's settings (engine/userdata/build_settings.json), as the Auditor computes them.
AUDIT_BUILDS = {
    "EK": {"file": "3.29/Ninja Builds/CoC EK Assa.xml", "disabledSkills": [], "scenario": "Pinnacle Boss",
           "includeDrafts": True},
    "Worb": {"file": "3.29/Worb.xml", "disabledSkills": ["Aspect of the Brine King"], "scenario": "Pinnacle Boss",
             "includeDrafts": True},
}

# B. Evidence builds as saved: raw PoB, no leave-out, no scenario config, no vault models.
RAW_BUILDS = {
    "v1": "AutoBuilder/FR CoC Occu Three Dragons.xml",
    "v2": "AutoBuilder/FR CoC Occu Three Dragons v2.xml",
    "v3": "AutoBuilder/FR CoC Occu Three Dragons v3.xml",
    "v4": "AutoBuilder/FR CoC Occu Three Dragons v4.xml",
    "source": "3.26/CoC/FR CoC Occu No Mirror Helm.xml",
    "EK": "3.29/Ninja Builds/CoC EK Assa.xml",
    "Worb": "3.29/Worb.xml",
}

RAW_KEYS = [
    "FullDPS", "CombinedDPS", "TotalDPS", "Speed", "SkillTriggerRate", "TriggerRateCap", "EffectiveSourceRate",
    "ProjectileCount", "ManaPerSecondCost", "LifePerSecondCost", "ESPerSecondCost", "ManaCost", "LifeCost",
    "ESCost", "ManaRegenRecovery", "LifeRegenRecovery", "EnergyShieldRegenRecovery", "EnergyShieldRecharge",
    "EnergyShield", "ManaUnreserved", "LifeUnreserved", "Life", "Mana", "PhysicalMaximumHitTaken", "TotalEHP",
    "FireResist", "ColdResist", "LightningResist", "ChaosResist", "CritChance", "HitChance",
]
OTHER_GROUP_KEYS = ["ESPerSecondCost", "ManaPerSecondCost", "LifePerSecondCost", "Speed", "SkillTriggerRate",
                    "TriggerRateCap", "TotalDPS"]
CONFIG_KEYS_OF_NOTE = ["conditionOnConsecratedGround", "enemyIsBoss", "multiplierChannelling"]

# Lua helpers defined in the test's own engine (engine.run), not an engine edit.
LUA_HELPERS = r"""
local dkjson = require("dkjson")
local function goldenPick(out, keys)
	local t = {}
	for _, k in ipairs(keys) do t[k] = out[k] end
	return t
end
function goldenConfigJSON()
	local r = {}
	for k, v in pairs(build.configTab.input) do
		local kind = type(v)
		if type(k) == "string" and (kind == "number" or kind == "string" or kind == "boolean") then r[k] = v end
	end
	return dkjson.encode(r)
end
function goldenMainOutputJSON(requestText)
	local keys = dkjson.decode(requestText).stats
	local out = build.calcsTab.mainOutput
	local present = {}
	for _, k in ipairs(keys) do present[k] = out[k] ~= nil end
	return dkjson.encode({ values = goldenPick(out, keys), present = present })
end
function goldenSkillPartsJSON()
	local group = build.skillsTab.socketGroupList[build.mainSocketGroup]
	local rows = {}
	for i, skill in ipairs(group.displaySkillList or {}) do
		local src = skill.activeEffect.srcInstance
		local parts = skill.activeEffect.grantedEffect.parts
		rows[i] = { name = skill.activeEffect.grantedEffect.name, part = skill.skillPartName or dkjson.null,
			partIndex = src and src.skillPart or dkjson.null, partCalcs = src and src.skillPartCalcs or dkjson.null,
			partCount = parts and #parts or 0 }
	end
	return dkjson.encode({ group = build.mainSocketGroup, label = group.displayLabel or dkjson.null,
		mainActiveSkill = group.mainActiveSkill, skills = rows })
end
function goldenSkillDPSJSON()
	local rows = {}
	for _, s in ipairs(build.calcsTab.mainOutput.SkillDPS or {}) do
		table.insert(rows, { name = s.name, dps = s.dps, count = s.count, trigger = s.trigger or dkjson.null,
			skillPart = s.skillPart or dkjson.null })
	end
	return dkjson.encode(rows)
end
function goldenOtherGroupsJSON(requestText)
	local keys = dkjson.decode(requestText).stats
	local calc = build.calcsTab:GetMiscCalculator()
	local origGroup = build.mainSocketGroup
	local rows = {}
	for gi, group in ipairs(build.skillsTab.socketGroupList) do
		if gi ~= origGroup and group.enabled ~= false then
			local origSkill = group.mainActiveSkill
			for si, skill in ipairs(group.displaySkillList or {}) do
				build.mainSocketGroup, group.mainActiveSkill = gi, si
				table.insert(rows, { group = gi, label = group.displayLabel or dkjson.null, index = si,
					name = skill.activeEffect.grantedEffect.name, includeInFullDPS = group.includeInFullDPS == true,
					out = goldenPick(calc({}, false), keys) })
			end
			group.mainActiveSkill = origSkill
		end
	end
	build.mainSocketGroup = origGroup
	return dkjson.encode(rows)
end
"""


# ---- environment -----------------------------------------------------------------------------------

@contextlib.contextmanager
def pob_cwd():
    """PobEngine chdirs into the PoB install; put the cwd back afterwards."""
    saved = os.getcwd()
    try:
        yield
    finally:
        os.chdir(saved)


def close_engine(engine) -> None:
    """Free the Lua state; one PoB state holds a lot of memory."""
    engine.close()


def offline_obtainability(league: str = OFFLINE_LEAGUE):
    """Obtainability.load() without the network: the cached SkillGem.json, parsed exactly like load()."""
    from obtainability import CACHE_DIR, GemVariant, Obtainability, gem_key
    result = Obtainability(league)
    lines = json.loads((CACHE_DIR / league / "SkillGem.json").read_text(encoding="utf-8"))["lines"]
    for line in lines:
        variant = GemVariant(line.get("gemLevel") or 1, line.get("gemQuality") or 0, bool(line.get("corrupted")))
        result.gems.setdefault(gem_key(line["name"]), []).append(variant)
    result._load_overrides()
    return result


def offline_auditor(build_path: Path, settings: dict, progress=lambda _: None, engine=None):
    """Auditor exactly as the GUI builds it, with Obtainability.load patched to the offline cache."""
    import audit
    with mock.patch.object(audit.Obtainability, "load", lambda *a, **k: offline_obtainability()):
        return audit.Auditor(build_path, settings["includeDrafts"], progress=progress,
                             disabled_skills=list(settings["disabledSkills"]), scenario=settings["scenario"],
                             engine=engine)


def jsonable(value):
    """Round-trip through JSON so pinned and fresh values compare as JSON-decoded data."""
    return json.loads(json.dumps(value))


# ---- fingerprints ----------------------------------------------------------------------------------

def file_fingerprint(path: Path) -> dict:
    data = Path(path).read_bytes()
    return {"path": str(path), "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def vault_fingerprint() -> dict:
    files = {}
    for folder in ("Rules", "Models", "Scenarios", "Gaps"):
        for path in sorted((VAULT_DIR / folder).glob("*.md")):
            files[f"{folder}/{path.name}"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def engine_fingerprint() -> dict:
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(ENGINE_DIR.glob("*")) if p.suffix in (".py", ".lua")}


def build_path(relative: str) -> Path:
    return BUILDS_DIR / relative


# ---- A: Auditor snapshot ---------------------------------------------------------------------------

def audit_snapshot(auditor) -> dict:
    """The keys run() reports (base, dpsBreakdown, models, rules, kpiSources, ...), via the Auditor's own methods."""
    from rules import violations
    base_ctx = auditor.evaluate()
    base = auditor.main_out(base_ctx)
    scenario_config = auditor.scenarios[auditor.scenario].get("pob_config") or {}
    return jsonable({
        "summary": auditor.summary,
        "disabledSkills": auditor.disabled_skills,
        "dpsAfterLeaveOut": auditor.dps_after_leave_out,
        "scenario": {"name": auditor.scenario, "config": scenario_config},
        "rules": {"active": [r.name for r in auditor.rules], "skipped": auditor.skipped,
                  "currentViolations": violations(auditor.rules, base_ctx)},
        "modelsLoaded": [m.name for m in auditor.models],
        "models": [m for k in base_ctx["skills"] for m in k.get("models", [])],
        "base": {"dps": base["FullDPS"], "ehp": base["TotalEHP"], "physMaxHit": base["PhysicalMaximumHitTaken"],
                 "manaMargin": auditor.mana_margin(base_ctx)},
        "dpsBreakdown": auditor.dps_breakdown(base["FullDPS"]),
        "kpiSources": auditor.kpi_sources(base_ctx),
        "reservation": auditor.reservations,
        "skills": [k["name"] for k in base_ctx["skills"]],
        "ctx": {
            "skills": [{"name": s["name"], "isMain": s["isMain"], "isAttack": s["isAttack"], "count": s["count"],
                        "out": s["out"], "models": s.get("models", [])} for s in base_ctx["skills"]],
            "supports": base_ctx["supports"],
            "keystones": sorted(base_ctx["keystones"]),  # Lua pairs() order is not deterministic
        },
        "keys": auditor.keys,
        "capabilityKeys": auditor.capability_keys,
        "equipped": sorted(auditor.equipped),
        "configAfterSetup": auditor.call("goldenConfigJSON") or {},
    })


def pin_audit_build(settings: dict) -> dict:
    """Fresh engine + Auditor for one golden build; returns the snapshot (engine closed, cwd restored)."""
    with pob_cwd():
        auditor = offline_auditor(build_path(settings["file"]), settings)
        try:
            auditor.engine.run(LUA_HELPERS)
            return audit_snapshot(auditor)
        finally:
            close_engine(auditor.engine)


# ---- B: raw PoB snapshot ---------------------------------------------------------------------------

def _call(engine, function: str, request: dict | None = None):
    from pobhost import _lua_str
    arg = _lua_str(json.dumps(request)) if request is not None else ""
    return json.loads(engine.run(f"return {function}({arg})"))


def raw_snapshot(engine, summary: dict) -> dict:
    main_output = _call(engine, "goldenMainOutputJSON", {"stats": RAW_KEYS})
    ctx = _call(engine, "evaluateJSON", {"removeNodes": [], "addNodes": [], "stats": RAW_KEYS})
    parts = _call(engine, "goldenSkillPartsJSON")
    by_index = parts["skills"]
    skills = []
    for index, skill in enumerate(ctx["skills"]):
        part = by_index[index] if index < len(by_index) else {}
        skills.append({"name": skill["name"], "isMain": skill["isMain"], "isAttack": skill["isAttack"],
                       "count": skill["count"], "part": part.get("part"), "partIndex": part.get("partIndex"),
                       "partCalcs": part.get("partCalcs"), "partCount": part.get("partCount"), "out": skill["out"]})
    seen = set(k for k, present in main_output["present"].items() if present)
    for skill in ctx["skills"]:
        seen |= set(skill["out"])
    config = _call(engine, "goldenConfigJSON") or {}
    return jsonable({
        "summary": summary,
        "mainGroup": {"index": parts["group"], "label": parts["label"], "mainActiveSkill": parts["mainActiveSkill"]},
        "mainOutput": main_output["values"],
        "skills": skills,
        "supports": ctx["supports"],
        "keystones": sorted(ctx["keystones"]),
        "skillDPS": _call(engine, "goldenSkillDPSJSON") or [],
        "otherGroups": _call(engine, "goldenOtherGroupsJSON", {"stats": OTHER_GROUP_KEYS}) or [],
        "config": config,
        "configOfNote": {k: config.get(k) for k in CONFIG_KEYS_OF_NOTE},
        "missingKeys": [k for k in RAW_KEYS if k not in seen],
        "missingInMainOutput": [k for k, present in main_output["present"].items() if not present],
        "missingPerSkill": {s["name"]: [k for k in RAW_KEYS if k not in s["out"]] for s in ctx["skills"]},
    })


def pin_raw_build(relative: str) -> dict:
    """Fresh engine, load as saved, dofile audit.lua, evaluateJSON (no models). Engine closed, cwd restored."""
    from pobhost import PobEngine, _lua_str
    with pob_cwd():
        engine = PobEngine()
        try:
            summary = engine.load_build(build_path(relative))
            engine.run(f"dofile({_lua_str((ENGINE_DIR / 'audit.lua').as_posix())})")
            engine.run(LUA_HELPERS)
            return raw_snapshot(engine, summary)
        finally:
            close_engine(engine)


# ---- comparison ------------------------------------------------------------------------------------

def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _numbers_equal(expected, actual, rel_tol: float | None) -> bool:
    if expected == actual:
        return True
    if isinstance(expected, float) and isinstance(actual, float) and math.isnan(expected) and math.isnan(actual):
        return True
    return bool(rel_tol) and abs(actual - expected) <= rel_tol * max(abs(expected), abs(actual))


def _fmt_change(expected, actual) -> str:
    if _is_number(expected) and _is_number(actual):
        pct = f", {100 * (actual - expected) / abs(expected):+.4g}%" if expected else ""
        return f" (delta {actual - expected:+.6g}{pct})"
    return ""


def diff(expected, actual, tolerances: dict | None = None, path: str = "", key: str = "") -> list[str]:
    """Every difference as 'path: golden X -> now Y'. tolerances: {key name: relative tolerance}."""
    tolerances = tolerances or {}
    if isinstance(expected, dict) and isinstance(actual, dict):
        found = []
        for k in sorted(set(expected) | set(actual), key=str):
            p = f"{path}.{k}" if path else str(k)
            if k not in actual:
                found.append(f"{p}: missing now (golden {expected[k]!r})")
            elif k not in expected:
                found.append(f"{p}: new key (now {actual[k]!r})")
            else:
                found += diff(expected[k], actual[k], tolerances, p, str(k))
        return found
    if isinstance(expected, list) and isinstance(actual, list) and len(expected) == len(actual):
        found = []
        for i, (e, a) in enumerate(zip(expected, actual)):
            found += diff(e, a, tolerances, f"{path}[{i}]", key)
        return found
    if _is_number(expected) and _is_number(actual):
        if _numbers_equal(expected, actual, tolerances.get(key)):
            return []
        return [f"{path}: golden {expected!r} -> now {actual!r}{_fmt_change(expected, actual)}"]
    if expected != actual or type(expected) is not type(actual):
        return [f"{path}: golden {expected!r} -> now {actual!r}"]
    return []


# ---- PoB install guard -----------------------------------------------------------------------------

# GUI window state written by SimpleGraphic.dll when the user closes the PoB GUI. Headless loads only
# lua51.dll, and both changed at 2026-10-21 23:25 with no headless run active, so they are not ours.
INSTALL_EXCLUDE = {"imgui.ini", os.path.join("SimpleGraphic", "SimpleGraphic.cfg")}


def install_snapshot(root: Path = POB_INSTALL) -> dict:
    snap = {}
    for dirpath, _, files in os.walk(root):
        for name in files:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, root)
            if rel in INSTALL_EXCLUDE:
                continue
            st = os.stat(full)
            snap[rel] = (st.st_size, st.st_mtime_ns)
    return snap


def install_diff(before: dict, after: dict) -> list[str]:
    lines = [f"added: {p} {after[p]}" for p in sorted(set(after) - set(before))]
    lines += [f"removed: {p} {before[p]}" for p in sorted(set(before) - set(after))]
    lines += [f"changed: {p} {before[p]} -> {after[p]}" for p in sorted(set(before) & set(after))
              if before[p] != after[p]]
    return lines
