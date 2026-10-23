"""Optimize a build with gear fixed.

  python optimize.py <build.xml>                 # audit: numbered suggestions
  python optimize.py <build.xml> --apply 1,3     # apply suggestions, re-check rules, save to Builds/AutoBuilder
"""

import argparse
import json
from pathlib import Path

from audit import DEFAULT_SCENARIO, Auditor, file_sha256, fmt_dims, print_report
from pobhost import ENGINE_DIR, _lua_str

DEFAULT_OUT_DIR = Path.home() / "Documents" / "Path of Building" / "Builds" / "AutoBuilder"


class ChangeError(ValueError):
    pass


class StaleAudit(ChangeError):
    pass


def check_source_fresh(build_path: Path, expected_sha256: str) -> None:
    try:
        current_sha256 = file_sha256(build_path)
    except OSError:
        current_sha256 = None
    if current_sha256 != expected_sha256:
        raise StaleAudit(f"Build changed since audit; re-run the audit ({build_path.name})")


def _gem_touch(change: dict) -> tuple[str, tuple[int, int] | None] | None:
    if change["type"] not in ("gem", "swap", "replaceGem"):
        return None
    name = change.get("name") or change.get("replaced")
    socket = (change["group"], change["gemIndex"]) if change["type"] == "replaceGem" else None
    return name, socket


def _item_touches(change: dict) -> list[tuple[str, object, str]]:
    slots = [change.get("slot")]
    slots += [jewel.get("slot") for jewel in change.get("abyssJewels") or []]
    return [("slot", slot, "set") for slot in slots if slot is not None]


def _compound_touches(change: dict) -> list[tuple[str, object, str]]:
    return [touch for sub in change.get("changes") or [] for touch in _touches(sub)]


def _group_touches(change: dict) -> list[tuple[str, object, str]]:
    return [("group", gem.get("name"), "set") for gem in change.get("gems") or []
            if not gem.get("isSupport") and gem.get("name") is not None]


def _node_touches(change: dict) -> list[tuple[str, object, str]]:
    mode = "add" if change.get("type") == "alloc" else "remove"
    return [("node", node, mode) for node in change.get("nodes") or []]


def _gem_level_touches(change: dict) -> list[tuple[str, object, str]]:
    group, name = change.get("group"), change.get("name")
    return [("gem", (group, name), "set"),
            ("socket", (group, change.get("gemIndex")), "set")]


def _add_support_touches(change: dict) -> list[tuple[str, object, str]]:
    return [("gem", (change.get("group"), (change.get("gem") or {}).get("name")), "set")]


def _replace_support_touches(change: dict) -> list[tuple[str, object, str]]:
    group, gem = change.get("group"), change.get("gem") or {}
    return [("gem", (group, change.get("replaced")), "set"),
            ("gem", (group, gem.get("name")), "set"),
            ("socket", (group, change.get("gemIndex")), "set")]


TOUCHERS = {
    "item": _item_touches,
    "compound": _compound_touches,
    "addGroup": _group_touches,
    "alloc": _node_touches,
    "dealloc": _node_touches,
    "gemLevel": _gem_level_touches,
    "level": _gem_level_touches,
    "addSupport": _add_support_touches,
    "replaceSupport": _replace_support_touches,
    "config": lambda change: [("setting", "config", "set")],
}


def _touches(change: dict) -> list[tuple[str, object, str]]:
    touches = TOUCHERS.get(change.get("type"), lambda value: [])(change)
    return list(dict.fromkeys(touches))


def _touches_conflict(left: tuple, right: tuple) -> bool:
    kind, key, mode = left
    other_kind, other_key, other_mode = right
    if kind != other_kind or key != other_key:
        return False
    return kind != "node" or mode != other_mode


def _pair_detail(left: list[tuple], right: list[tuple], kind: str, key: object) -> str:
    if kind != "gem":
        return str(key)
    names = {touch_key[1] for touch_kind, touch_key, _ in left + right
             if touch_kind == "gem" and isinstance(touch_key, tuple) and touch_key[1] is not None}
    return ", ".join(sorted(map(str, names)))


def conflict_pairs(entries: list[tuple[object, dict]]) -> list[dict]:
    """Return deterministic pairs of guide changes that cannot be combined."""
    prepared = [(key, _touches(change)) for key, change in entries]
    found = []
    for index, (left_key, left) in enumerate(prepared):
        if any(kind == "setting" for kind, _, _ in left):
            found.append({"keys": (left_key, left_key), "kind": "setting", "detail": "config"})
        for right_key, right in prepared[index + 1:]:
            shared = [(kind, key) for touch in left for other in right
                      if _touches_conflict(touch, other) for kind, key, _ in [touch]]
            for kind, key in sorted(set(shared), key=lambda value: (value[0], str(value[1]))):
                report_kind = "gem" if kind == "socket" else kind
                detail = _pair_detail(left, right, report_kind, key)
                found.append({"keys": (left_key, right_key), "kind": report_kind, "detail": detail})
    unique = {(row["keys"], row["kind"], row["detail"]): row for row in found}
    return [unique[key] for key in sorted(unique, key=lambda value: (str(value[0]), value[1], value[2]))]


def check_conflicts(changes: list[dict]) -> None:
    if sum(c["type"] == "repath" for c in changes) > 1:
        raise ChangeError("pick at most one re-path")
    touches = [touch for change in changes if (touch := _gem_touch(change)) is not None]
    duplicates = set()
    for index, (name, socket) in enumerate(touches):
        for other_name, other_socket in touches[index + 1:]:
            same_name = name == other_name and (socket is None or other_socket is None or socket == other_socket)
            same_socket = socket is not None and socket == other_socket
            if same_name or same_socket:
                duplicates.update((name, other_name))
    if duplicates:
        raise ChangeError(f"several changes touch the same gem: {', '.join(sorted(duplicates))}")
    pairs = conflict_pairs(list(enumerate(changes)))
    if not pairs:
        return
    kind = pairs[0]["kind"]
    details = sorted({pair["detail"] for pair in pairs if pair["kind"] == kind})
    messages = {
        "slot": f"several changes use the same slot: {', '.join(details)}",
        "group": f"several changes add the same skill: {', '.join(details)}",
        "gem": f"several changes touch the same gem: {', '.join(details)}",
        "node": "several changes add and remove the same passive nodes",
        "setting": "settings the guide assumes are never applied",
    }
    raise ChangeError(messages[kind])


def save_xml(out_dir: Path, name: str, xml: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    for number in range(1, 10_001):
        candidate = name if number == 1 else f"{name[:-1]} {number})"
        path = out_dir / f"{candidate}.xml"
        try:
            with path.open("x", encoding="utf-8") as output:
                output.write(xml)
            return path
        except FileExistsError:
            continue
    raise ChangeError(f"no free optimized filename in {out_dir}")


def apply_changes(auditor: Auditor, ids: list[int], out_dir: Path = DEFAULT_OUT_DIR, force: bool = False) -> dict:
    """Apply suggestions by id to a fresh copy of the build; save it unless a rule breaks."""
    check_source_fresh(auditor.build_path, auditor.source_sha256)

    bad = [i for i in ids if not 1 <= i <= len(auditor.suggestions)]
    if not ids or bad:
        raise ChangeError(f"unknown suggestion ids: {bad or 'none picked'}")
    changes = [auditor.suggestions[i - 1] for i in sorted(set(ids))]
    check_conflicts(changes)

    engine = auditor.engine
    engine.load_build(auditor.build_path)  # fresh state: audits leave the build touched
    auditor.load_audit_hooks(auditor.disabled_skills)
    base_ctx = auditor.evaluate()
    auditor.breaks(base_ctx)  # Prime the baseline before applyChangesJSON mutates the loaded build.
    name = f"{auditor.summary['buildName']} (optimized)"
    request = json.dumps({"changes": changes, "stats": auditor.keys, "buildName": name,
                          "extraSkills": auditor.extra_request()})
    result = json.loads(engine.run(f"return applyChangesJSON({_lua_str(request)})"))
    result["ctx"] = auditor.adjust(result["ctx"])

    broken = auditor.breaks(result["ctx"])
    outcome = {"changes": changes, "dims": auditor.dimensions(result["ctx"], base_ctx), "violations": broken,
               "saved": False, "path": None}
    if broken and not force:
        return outcome
    path = save_xml(out_dir, name, result["xml"])
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
