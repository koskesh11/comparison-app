"""Runtime baseline of a full Auditor.run() (not pass/fail). Writes golden.json["perf"] (or ["perfAfter"]).

usage:  python tests/perf_baseline.py [--key perf|perfAfter] [--runs N]
Build: FR CoC v4, include_drafts=True, scenario "Pinnacle Boss", no leave-out, offline Obtainability (Allflame cache).
If one run takes under 5 minutes a second run is made (unless --runs is given).
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

BUILD = "v4"
SETTINGS = {"file": gc.RAW_BUILDS[BUILD], "disabledSkills": [], "scenario": "Pinnacle Boss", "includeDrafts": True}
SECOND_RUN_BELOW_S = 300


def timed_run() -> dict:
    marks = []
    with gc.pob_cwd():
        start = time.perf_counter()
        auditor = gc.offline_auditor(gc.build_path(SETTINGS["file"]), SETTINGS,
                                     progress=lambda label: marks.append((label, time.perf_counter())))
        constructed = time.perf_counter()
        marks.clear()
        try:
            report = auditor.run()
        finally:
            gc.close_engine(auditor.engine)
        done = time.perf_counter()
    edges = marks + [("end", done)]
    sections = {label: round(edges[i + 1][1] - t, 1) for i, (label, t) in enumerate(marks)}
    if marks:
        sections["base (before first section)"] = round(marks[0][1] - constructed, 1)
    return {"constructSeconds": round(constructed - start, 2), "runSeconds": round(done - constructed, 1),
            "sections": sections, "suggestions": len(report["suggestions"]),
            "baseDps": report["base"]["dps"], "violations": report["rules"]["currentViolations"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--key", default="perf")
    parser.add_argument("--runs", type=int)
    args = parser.parse_args()
    runs = [timed_run()]
    print(json.dumps(runs[-1]), flush=True)
    wanted = args.runs or (2 if runs[0]["runSeconds"] < SECOND_RUN_BELOW_S else 1)
    while len(runs) < wanted:
        runs.append(timed_run())
        print(json.dumps(runs[-1]), flush=True)
    golden = json.loads(gc.GOLDEN_PATH.read_text(encoding="utf-8"))
    golden[args.key] = {
        "date": datetime.datetime.now().isoformat(timespec="seconds"),
        "build": BUILD, "settings": SETTINGS, "runs": runs,
        "machine": {"python": platform.python_version(), "processor": platform.processor(),
                    "platform": platform.platform()},
        "note": "Full Auditor(v4).run() wall time via time.perf_counter, construction (PoB boot + load + hooks + "
                "offline Obtainability) and run() separately; sections from the progress callback. Baseline before "
                "A1 scoring changes. Not pass/fail.",
    }
    gc.GOLDEN_PATH.write_text(json.dumps(golden, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {gc.GOLDEN_PATH} [{args.key}]")


if __name__ == "__main__":
    main()
