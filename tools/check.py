"""Run the checks for src/ (decision 006; the list is in docs/ARCHITECTURE.md, "Checks").

    python tools/check.py           the fast checks F1-F14 (the commit hook runs these)
    python tools/check.py --full    also the merge checks M1-M3, M8, M9 (tools/merge_to_main.py runs these)

One line per check, then one summary line that names every failure. Exit code 1 when a check fails.
"""

import argparse
import os
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from checks.common import Skip

from checks import (
    eol,
    git_state,
    lua_calls,
    lua_rules,
    lua_syntax,
    no_engine,
    notes,
    patch_counts,
    sizes,
    structure,
    testtree,
    web,
)

ROOT = Path(__file__).resolve().parents[1]
INSTALL = "python -m venv .venv  then  .venv\\Scripts\\python -m pip install --group dev"
SHOWN_PROBLEMS = 15
TOOL_TIMEOUT = 900


@dataclass(frozen=True)
class Check:
    id: str
    name: str
    run: Callable[[Path], list[str]]
    full: bool = False
    git: bool = False  # needs a git checkout (not run in the clean export)


def venv_python() -> Path | None:
    venv = Path(os.environ.get("CHECK_VENV", ROOT / ".venv"))
    for candidate in (venv / "Scripts" / "python.exe", venv / "bin" / "python"):
        if candidate.exists():
            return candidate
    return None


def tool(*args: str) -> Callable[[Path], list[str]]:
    """A check that runs `python -m <args>` from the dev tools; its output lines are the problems."""

    def run(root: Path) -> list[str]:
        python = venv_python()
        if python is None:
            return [f"dev tools not installed: {INSTALL}"]
        env = {**os.environ, "PYTHONPATH": str(root / "src")}
        result = subprocess.run(
            [str(python), "-m", *args],
            cwd=root,
            capture_output=True,
            text=True,
            env=env,
            timeout=TOOL_TIMEOUT,
            check=False,
        )
        if result.returncode == 0:
            return []
        lines = [line for line in (result.stdout + result.stderr).splitlines() if line.strip()]
        if any("No module named" in line for line in lines):
            return [f"dev tools not installed: {INSTALL}", *lines[:3]]
        return lines or [f"exit code {result.returncode}"]

    return run


def both(*runs: Callable[[Path], list[str]]) -> Callable[[Path], list[str]]:
    return lambda root: [problem for run in runs for problem in run(root)]


def clean_export(root: Path) -> list[str]:
    if os.environ.get("CHECK_CLEAN") != "1":
        raise Skip("tools/merge_to_main.py runs the full checks in a clean export of the branch")
    return [] if not (root / ".git").exists() else ["CHECK_CLEAN is set, but this is a git checkout"]


CHECKS = [
    Check("F1", "format", tool("ruff", "format", "--check", ".")),
    Check("F2", "lint", tool("ruff", "check", ".")),
    Check("F3", "import rules", both(tool("importlinter.cli"), no_engine.check)),
    Check("F4", "file sizes", sizes.check),
    Check("F5", "network and environment", structure.check_network),
    Check("F6", "Lua only through lua_host", lua_calls.check),
    Check("F7", "Lua endpoint table", lua_rules.check),
    Check("F8", "Lua syntax", lua_syntax.check),
    Check("F9", "browser code", web.check),
    Check("F10", "notes format", notes.check),
    Check("F11", "no unstaged deletions", git_state.check, git=True),
    Check("F12", "line endings", eol.check, git=True),
    Check("F13", "patched functions are counted", patch_counts.check),
    Check("F14", "child processes", structure.check_subprocess),
    Check("M1", "types", tool("mypy"), full=True),
    Check(
        "M2",
        "tests and coverage (M4-M7, M10, M11)",
        tool(
            "pytest",
            "-q",
            "-n",
            "auto",
            "--dist",
            "loadgroup",
            "--cov=autobuilder",
            "--cov-report=term",
            "--cov-fail-under=80",
        ),
        full=True,
    ),
    Check("M3", "test tree", testtree.check, full=True),
    Check("M8", "clean checkout", clean_export, full=True),
    Check(
        "M9",
        "dead code and duplication",
        both(
            tool("vulture", "src/autobuilder", "--min-confidence", "80"),
            tool("pylint", "--disable=all", "--enable=duplicate-code", "src/autobuilder"),
        ),
        full=True,
    ),
]


def run_check(check: Check, root: Path) -> tuple[str, list[str]]:
    try:
        problems = check.run(root)
    except Skip as reason:
        return f"skipped: {reason}", []
    except Exception as error:  # noqa: BLE001 - a crashing check is a failed check, reported with its error
        return "FAIL", [f"the check crashed: {type(error).__name__}: {error}"]
    return ("FAIL" if problems else "ok"), problems


def main(argv: list[str] | None = None, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--full", action="store_true", help="also run the merge checks")
    args = parser.parse_args(argv)
    in_export = os.environ.get("CHECK_CLEAN") == "1"
    selected = [c for c in CHECKS if (args.full or not c.full) and not (in_export and c.git)]
    failed, skipped = [], 0
    for check in selected:
        started = time.monotonic()
        status, problems = run_check(check, root)
        print(f"{check.id:<4}{check.name:.<44} {status} ({time.monotonic() - started:.1f} s)", flush=True)
        for problem in problems[:SHOWN_PROBLEMS]:
            print(f"      - {problem}")
        if len(problems) > SHOWN_PROBLEMS:
            print(f"      ... and {len(problems) - SHOWN_PROBLEMS} more")
        failed += [f"{check.id} {check.name}"] if status == "FAIL" else []
        skipped += status.startswith("skipped")
    passed = len(selected) - len(failed) - skipped
    if failed:
        print(f"check: {len(failed)} FAILED ({', '.join(failed)}); {passed} passed, {skipped} skipped")
        return 1
    print(f"check: all {passed} passed, {skipped} skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
