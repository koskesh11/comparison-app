"""Optimize a build with gear fixed.

  python optimize.py <build.xml>                 # audit: numbered suggestions
  python optimize.py <build.xml> --apply 1,3     # apply suggestions, re-check rules, save to Builds/AutoBuilder
"""

import argparse
import json
from pathlib import Path

from audit import DEFAULT_SCENARIO, Auditor, fmt_dims, print_report
from pobhost import ENGINE_DIR, _lua_str

DEFAULT_OUT_DIR = Path.home() / "Documents" / "Path of Building" / "Builds" / "AutoBuilder"


class ChangeError(ValueError):
    pass


def check_conflicts(changes: list[dict]) -> None:
    if sum(c["type"] == "repath" for c in changes) > 1:
        raise ChangeError("pick at most one re-path")
    touched = [c.get("name") or c.get("replaced") for c in changes if c["type"] in ("gem", "swap")]
    duplicates = sorted({g for g in touched if touched.count(g) > 1})
    if duplicates:
        raise ChangeError(f"several changes touch the same gem: {', '.join(duplicates)}")


def apply_changes(auditor: Auditor, ids: list[int], out_dir: Path = DEFAULT_OUT_DIR, force: bool = False) -> dict:
    """Apply suggestions by id to a fresh copy of the build; save it unless a rule breaks."""
    bad = [i for i in ids if not 1 <= i <= len(auditor.suggestions)]
    if not ids or bad:
        raise ChangeError(f"unknown suggestion ids: {bad or 'none picked'}")
    changes = [auditor.suggestions[i - 1] for i in sorted(set(ids))]
    check_conflicts(changes)

    engine = auditor.engine
    engine.load_build(auditor.build_path)  # fresh state: audits leave the build touched
    auditor.load_audit_hooks(auditor.disabled_skills)
    base_ctx = auditor.evaluate()
    name = f"{auditor.summary['buildName']} (optimized)"
    request = json.dumps({"changes": changes, "stats": auditor.keys, "buildName": name})
    result = json.loads(engine.run(f"return applyChangesJSON({_lua_str(request)})"))
    result["ctx"] = auditor.adjust(result["ctx"])

    broken = auditor.breaks(result["ctx"])
    outcome = {"changes": changes, "dims": auditor.dimensions(result["ctx"], base_ctx), "violations": broken,
               "saved": False, "path": None}
    if broken and not force:
        return outcome
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}.xml"
    path.write_text(result["xml"], encoding="utf-8")
    return {**outcome, "saved": True, "path": str(path)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("build", type=Path)
    parser.add_argument("--include-drafts", action="store_true", help="also apply draft vault rules")
    parser.add_argument("--apply", help="comma-separated suggestion numbers, e.g. 1,3")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--force", action="store_true", help="save even if the result breaks a rule")
    parser.add_argument("--leave-out", action="append", default=[], help="skill to leave out, e.g. 'Aspect of the Brine King'")
    parser.add_argument("--scenario", default=DEFAULT_SCENARIO, help="vault scenario, e.g. Mapping")
    args = parser.parse_args()

    auditor = Auditor(args.build.resolve(), args.include_drafts, disabled_skills=args.leave_out, scenario=args.scenario)
    print_report(auditor.run())
    if not args.apply:
        print(f"\n{len(auditor.suggestions)} applicable suggestions. Re-run with --apply 1,2,... to build them.")
        return
    try:
        ids = [int(p) for p in args.apply.replace(" ", "").split(",") if p]
        outcome = apply_changes(auditor, ids, args.out_dir, args.force)
    except (ChangeError, ValueError) as error:
        raise SystemExit(f"cannot apply: {error}")
    print("\n== Applied")
    for change in outcome["changes"]:
        print(f"   {change}")
    print(f"   result: {fmt_dims(outcome['dims'])}")
    for v in outcome["violations"]:
        print(f"   !! breaks {v}")
    print(f"   saved: {outcome['path']}" if outcome["saved"] else "   not saved: breaks a rule (use --force)")


if __name__ == "__main__":
    main()
