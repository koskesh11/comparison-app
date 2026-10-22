"""Regenerate tests/golden.json from the current app (engine + vault) and the saved build files.

usage (from anywhere):  python tests/pin_golden.py [--determinism] [--verify-run] [--out PATH]
  --determinism  load every build a second time in a fresh engine and diff (result goes into golden.json)
  --verify-run   one full Auditor.run() on EK: its report keys must equal the method-based snapshot
"""

import argparse
import datetime
import json
import platform
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden_common as gc  # noqa: E402
from evidence_checks import evidence_checks  # noqa: E402


SPEC = "tasks/003-integrate-fr-coc-learnings.md Phase A spec / user golden-build facts"
# User-given anchors, checked by test_golden.py on fresh loads. digits None = exact value; floor = math.floor first.
ANCHORS = [
    {"label": "EK FullDPS as saved", "build": "audit:EK", "path": ["summary", "stats", "FullDPS"],
     "expected": 15136639.02, "digits": 2},
    {"label": "Worb FullDPS as saved", "build": "audit:Worb", "path": ["summary", "stats", "FullDPS"],
     "expected": 7176019.15, "digits": 2},
    {"label": "v4 FullDPS as saved", "build": "raw:v4", "path": ["summary", "stats", "FullDPS"],
     "expected": 57001026.47, "digits": 2},
    {"label": "EK mana margin 209.4 - 160.7 - 26.8", "build": "audit:EK", "path": ["base", "manaMargin"],
     "expected": 21.9, "digits": 1},
    {"label": "Worb leaves out Aspect of the Brine King", "build": "audit:Worb", "path": ["disabledSkills"],
     "expected": ["Aspect of the Brine King"], "digits": None},
    {"label": "Worb Winter Orb pobCount (count=5 saved in file)", "build": "audit:Worb",
     "path": ["models", 0, "pobCount"], "expected": 5, "digits": None},
    {"label": "Worb Winter Orb model multiplier (4 hits)", "build": "audit:Worb",
     "path": ["models", 0, "multiplier"], "expected": 4, "digits": None},
    {"label": "Worb Winter Orb expected rounds down to 4", "build": "audit:Worb",
     "path": ["models", 0, "expected"], "expected": 4, "digits": None, "floor": True},
]


def write(golden: dict, out: Path) -> None:
    out.write_text(json.dumps(golden, indent=1, sort_keys=False) + "\n", encoding="utf-8")


def load_existing(out: Path) -> dict:
    return json.loads(out.read_text(encoding="utf-8")) if out.is_file() else {}


def meta() -> dict:
    return {
        "pinnedAt": datetime.datetime.now().isoformat(timespec="seconds"),
        "pinnedBy": "tests/pin_golden.py",
        "python": platform.python_version(),
        "offlineLeague": gc.OFFLINE_LEAGUE,
        "note": "A = Auditor with the user's settings (include_drafts, leave-out, scenario, vault models); "
                "B = raw PoB as saved (load_build + audit.lua evaluateJSON, no models/scenario/leave-out). "
                "engineFiles/vault hashes are for telling an engine change from a vault change.",
        "engineFiles": gc.engine_fingerprint(),
    }


def inputs() -> dict:
    files = {f"audit:{k}": s["file"] for k, s in gc.AUDIT_BUILDS.items()}
    files.update({f"raw:{k}": rel for k, rel in gc.RAW_BUILDS.items()})
    return {key: gc.file_fingerprint(gc.build_path(rel)) for key, rel in files.items()}


def pin_audit() -> dict:
    result = {}
    for key, settings in gc.AUDIT_BUILDS.items():
        start = time.perf_counter()
        result[key] = {"settings": settings, "snapshot": gc.pin_audit_build(settings)}
        print(f"audit {key}: {time.perf_counter() - start:.1f}s", flush=True)
    return result


def pin_raw() -> dict:
    result = {}
    for key, rel in gc.RAW_BUILDS.items():
        start = time.perf_counter()
        result[key] = {"file": rel, "snapshot": gc.pin_raw_build(rel)}
        print(f"raw {key}: {time.perf_counter() - start:.1f}s", flush=True)
    return result


def determinism(audit: dict, raw: dict) -> dict:
    """Second load of every build in a fresh engine (same process); any difference is listed."""
    diffs = {}
    for key, entry in audit.items():
        diffs[f"audit:{key}"] = gc.diff(entry["snapshot"], gc.pin_audit_build(entry["settings"]))
    for key, entry in raw.items():
        diffs[f"raw:{key}"] = gc.diff(entry["snapshot"], gc.pin_raw_build(entry["file"]))
    return {"method": "each build loaded twice in fresh PobEngine instances (same process), full snapshot diffed "
                      "with exact float equality; cross-process: every test_golden run re-loads and compares",
            "checkedAt": datetime.datetime.now().isoformat(timespec="seconds"),
            "differences": diffs, "deterministic": not any(diffs.values())}


RUN_KEYS = ["disabledSkills", "scenario", "models", "dpsBreakdown", "kpiSources", "base"]


def verify_run(key: str = "EK") -> dict:
    """Full Auditor.run() once: the report's keys must equal the method-based snapshot (same auditor)."""
    settings = gc.AUDIT_BUILDS[key]
    with gc.pob_cwd():
        auditor = gc.offline_auditor(gc.build_path(settings["file"]), settings)
        try:
            auditor.engine.run(gc.LUA_HELPERS)
            snap = gc.audit_snapshot(auditor)
            start = time.perf_counter()
            report = gc.jsonable(auditor.run())
            seconds = time.perf_counter() - start
        finally:
            gc.close_engine(auditor.engine)
    diffs = {k: gc.diff(snap[k], report[k]) for k in RUN_KEYS}
    diffs["rules"] = gc.diff(snap["rules"], report["rules"])
    diffs["build.skills"] = gc.diff(snap["skills"], report["build"]["skills"])
    diffs["reservation"] = gc.diff(snap["reservation"], {k: v for k, v in report["reservation"].items()
                                                         if k != "overReserved"})
    print(f"verify-run {key}: run() {seconds:.1f}s", flush=True)
    return {"build": key, "runSeconds": round(seconds, 1), "differences": diffs, "equal": not any(diffs.values()),
            "checkedAt": datetime.datetime.now().isoformat(timespec="seconds")}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=gc.GOLDEN_PATH)
    parser.add_argument("--determinism", action="store_true")
    parser.add_argument("--verify-run", action="store_true")
    args = parser.parse_args()
    out = args.out.resolve()
    old = load_existing(out)
    golden = {"schema": 1, "meta": meta(), "tolerances": old.get("tolerances", {}),
              "tolerancesNote": old.get("tolerancesNote", "{} = exact equality on JSON-decoded floats everywhere"),
              "inputs": inputs(), "vault": gc.vault_fingerprint(),
              "anchors": [{**a, "source": SPEC} for a in ANCHORS]}
    golden["audit"] = pin_audit()
    write({**old, **golden}, out)  # partial progress survives an interruption
    golden["raw"] = pin_raw()
    golden["evidenceChecks"] = evidence_checks(golden["audit"], golden["raw"])
    write({**old, **golden}, out)
    if args.determinism:
        golden["determinism"] = determinism(golden["audit"], golden["raw"])
        write({**old, **golden}, out)
    if args.verify_run:
        golden["runEquivalence"] = verify_run()
        write({**old, **golden}, out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
