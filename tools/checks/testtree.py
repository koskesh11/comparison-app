"""M3: the test tree. Every src/ module has its mirrored test file, the tests that guard milestone 1's code exist
(M4-M7, M11), PoB and owner tests carry their markers, and no test boots its own PoB (S6)."""

import re
from pathlib import Path

from checks.common import SRC, SRC_TESTS, files, rel

REQUIRED = {
    "tests/comparison_app/test_number_cases.py": "M4: PoB edge cases (inf, NaN, missing) and the shared number formats",
    "tests/comparison_app/test_golden_has_all_keys.py": "M5: every report key is in the golden snapshot",
    "tests/comparison_app/pob/test_every_endpoint_restores.py": "M6: every endpoint leaves the build as it was (S13)",
    "tests/comparison_app/compare/test_recalc_matches_apply.py": "M7: the in-memory button matches a saved change",
}
REQUIRED_WITH = {  # src/comparison_app module -> tests that must exist as soon as it does
    "pob/lua_host.py": [
        "tests/comparison_app/pob/test_write_guard.py",
        "tests/comparison_app/pob/test_write_sandbox.py",
    ],
}
USES_POB = re.compile(r"\bpob_session\b|comparison_app\.pob\.(session|lua_host)\b")
USES_OWNER_BUILDS = re.compile(r"\bowner_builds\b|Path of Building[/\\]+Builds")
# Booting PoB in a test: a session, or a bare LuaHost started with PoB's loader. A bare LuaHost alone (Lua's standard
# libraries, no PoB) is allowed: the host's own tests need one.
BOOTS_POB = re.compile(r"\b(PobSession|start_session|open_session)\(|\bLOADER\b|loader\.lua")


def required(root: Path) -> list[str]:
    problems = [f"{test}: missing ({why})" for test, why in REQUIRED.items() if not (root / test).exists()]
    for module, tests in REQUIRED_WITH.items():
        if (root / SRC / module).exists():
            problems += [
                f"{test}: missing (required with {SRC.as_posix()}/{module}, M11)"
                for test in tests
                if not (root / test).exists()
            ]
    return problems


def mirrored(root: Path) -> list[str]:
    problems = []
    for path in files(root, (SRC,), "*.py"):
        if path.name == "__init__.py":
            continue
        module = path.relative_to(root / SRC)
        expected = SRC_TESTS / module.parent / f"test_{module.name}"
        if not (root / expected).exists():
            problems.append(f"{rel(root, path)}: no test file {expected.as_posix()}")
    return problems


def markers(root: Path) -> list[str]:
    problems = []
    for path in files(root, (SRC_TESTS,), "test_*.py"):
        text, name = path.read_text(encoding="utf-8"), rel(root, path)
        if USES_POB.search(text) and "pytest.mark.pob" not in text:
            problems.append(f"{name}: uses PoB but is not marked pytest.mark.pob")
        if USES_OWNER_BUILDS.search(text) and "pytest.mark.owner" not in text:
            problems.append(f"{name}: reads the owner's builds but is not marked pytest.mark.owner")
        if BOOTS_POB.search(text):
            problems.append(f"{name}: boots its own PoB; use the shared pob_session fixture (S6)")
    return problems


def check(root: Path) -> list[str]:
    return required(root) + mirrored(root) + markers(root)
