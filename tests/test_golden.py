"""Golden regression baseline: re-load the golden and evidence builds and compare with tests/golden.json.

Only reads golden.json (regenerate with: python tests/pin_golden.py --determinism --verify-run).
Failure kinds are kept apart:
  - "input build changed, re-pin?"   a build file differs from the one pinned (wrong/unsaved file)
  - "vault changed"                  rule/model/scenario notes differ (not an engine regression)
  - "<build>: N differences"         numbers regression with the exact golden and current values
  - tearDownModule                   the PoB install was modified during this module
"""

import functools
import json
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden_common as gc  # noqa: E402

GOLDEN = json.loads(gc.GOLDEN_PATH.read_text(encoding="utf-8"))
TOLERANCES = GOLDEN.get("tolerances", {})
MAX_LINES = 80
_install_before: dict = {}


def setUpModule():
    _install_before.update(gc.install_snapshot())


def tearDownModule():
    changes = gc.install_diff(_install_before, gc.install_snapshot())
    if changes:
        jewel = [c for c in changes if "TimelessJewelData" in c]
        text = "\n  ".join(changes)
        print(f"\nPoB install changed during test_golden ({len(changes)} files, TimelessJewelData: {len(jewel)}):"
              f"\n  {text}")
        raise AssertionError(f"PoB install changed: {len(changes)} files (see output above)")


def input_changes(keys=None) -> list[str]:
    found = []
    for key, pinned in GOLDEN["inputs"].items():
        if keys is not None and key not in keys:
            continue
        path = Path(pinned["path"])
        if not path.is_file():
            found.append(f"{key}: {path} missing (pinned size {pinned['size']})")
            continue
        now = gc.file_fingerprint(path)
        if (now["size"], now["sha256"]) != (pinned["size"], pinned["sha256"]):
            found.append(f"{key}: {path} size {pinned['size']} -> {now['size']}, "
                         f"sha256 {pinned['sha256'][:12]} -> {now['sha256'][:12]}")
    return found


@functools.cache
def fresh_audit(key: str) -> dict:
    return gc.pin_audit_build(GOLDEN["audit"][key]["settings"])


@functools.cache
def fresh_raw(key: str) -> dict:
    return gc.pin_raw_build(GOLDEN["raw"][key]["file"])


def fresh(build: str) -> dict:
    kind, key = build.split(":", 1)
    return fresh_audit(key) if kind == "audit" else fresh_raw(key)


def report(title: str, lines: list[str]) -> str:
    more = f"\n  ... {len(lines) - MAX_LINES} more" if len(lines) > MAX_LINES else ""
    return f"{title}\n  " + "\n  ".join(lines[:MAX_LINES]) + more


class InputsTests(unittest.TestCase):
    def test_build_files_unchanged(self):
        changed = input_changes()
        if changed:
            self.fail(report("input build changed, re-pin? (python tests/pin_golden.py)", changed))

    def test_vault_notes_unchanged(self):
        lines = gc.diff(GOLDEN["vault"], gc.vault_fingerprint())
        if lines:
            self.fail(report("vault changed (not an engine regression); re-pin if intended", lines))


class GoldenNumbersTests(unittest.TestCase):
    def check(self, build: str, golden: dict) -> None:
        if input_changes({build}):
            self.skipTest(f"input build changed, re-pin? ({build})")
        now = fresh(build)
        vault_lines = []
        if build.startswith("audit:"):
            pinned = {"rules": golden["rules"], "modelsLoaded": golden["modelsLoaded"]}
            vault_lines = gc.diff({"rules": {k: pinned["rules"][k] for k in ("active", "skipped")},
                                   "modelsLoaded": pinned["modelsLoaded"]},
                                  {"rules": {k: now["rules"][k] for k in ("active", "skipped")},
                                   "modelsLoaded": now["modelsLoaded"]})
        lines = gc.diff(golden, now, TOLERANCES)
        if lines:
            head = (f"{build}: {len(lines)} differences vs golden.json"
                    + (" (rule/model set changed too: vault change?)" if vault_lines else ""))
            self.fail(report(head, lines))


def _numbers_test(build: str, golden: dict):
    def test(self):
        self.check(build, golden)
    return test


for _key, _entry in GOLDEN["audit"].items():
    setattr(GoldenNumbersTests, f"test_audit_{_key}", _numbers_test(f"audit:{_key}", _entry["snapshot"]))
for _key, _entry in GOLDEN["raw"].items():
    setattr(GoldenNumbersTests, f"test_raw_{_key}", _numbers_test(f"raw:{_key}", _entry["snapshot"]))


def _lookup(snapshot, path: list):
    value = snapshot
    for step in path:
        value = value[step]
    return value


class AnchorTests(unittest.TestCase):
    """User-given anchor values (tasks/003 Phase A spec), stored in golden.json["anchors"]."""

    def test_anchors(self):
        for anchor in GOLDEN["anchors"]:
            with self.subTest(anchor=anchor["label"]):
                if input_changes({anchor["build"]}):
                    self.skipTest(f"input build changed, re-pin? ({anchor['build']})")
                value = _lookup(fresh(anchor["build"]), anchor["path"])
                if anchor.get("floor"):
                    value = math.floor(value)
                shown = f"{value:.{anchor['digits']}f}" if anchor["digits"] is not None else value
                expected = f"{anchor['expected']:.{anchor['digits']}f}" if anchor["digits"] is not None \
                    else anchor["expected"]
                self.assertEqual(shown, expected, f"{anchor['label']}: expected {expected}, now {value!r} "
                                                  f"({anchor['build']} {'.'.join(map(str, anchor['path']))})")


if __name__ == "__main__":
    unittest.main()
