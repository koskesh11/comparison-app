"""Merge a task branch into main only when every check passes (decision 006; CLAUDE.md "Tasks and code").

    python tools/merge_to_main.py task-NNN-slug --message merge-message.txt

Run it on the task branch, with a clean working tree. Steps, each one stops the merge when it fails:
1. the message answers every item of docs/ARCHITECTURE-CHECKLIST.md (M12) and none is "no";
2. `tools/check.py --full` passes in a clean export of the branch (M8: no git-ignored file is needed);
3. the first app's tests pass (`tools/run_tests.py --all`, frozen engine/);
4. git merges the branch into main with --no-ff and the message.
"""

import argparse
import io
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = Path("docs/ARCHITECTURE-CHECKLIST.md")
ITEM = re.compile(r"^- (A\d+) ", re.MULTILINE)
ANSWER = re.compile(r"^(A\d+): (yes|no|n/a) - \S", re.MULTILINE)
TIMEOUT = 1800


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True, timeout=120).stdout


def checklist_problems(checklist: str, message: str) -> list[str]:
    answers = dict(ANSWER.findall(message))
    problems = [
        f"{item}: not answered (`{item}: yes - <how>` or `n/a - <why>`)"
        for item in ITEM.findall(checklist)
        if item not in answers
    ]
    return problems + [f"{item}: answered no" for item, answer in answers.items() if answer == "no"]


def export(root: Path, branch: str, target: Path) -> None:
    """The branch's tracked files only, as a fresh checkout would have them."""
    archive = subprocess.run(
        ["git", "archive", "--format=tar", branch], cwd=root, capture_output=True, check=True, timeout=300
    ).stdout
    with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
        tar.extractall(target, filter="data")


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> bool:
    print(f"merge: {' '.join(command)}  (in {cwd})", flush=True)
    return subprocess.run(command, cwd=cwd, env=env, timeout=TIMEOUT, check=False).returncode == 0


def preconditions(root: Path, branch: str) -> list[str]:
    problems = []
    if git(root, "branch", "--show-current").strip() != branch:
        problems.append(f"switch to {branch} first: the old tests run on the checked-out branch")
    if git(root, "status", "--porcelain", "--untracked-files=no").strip():
        problems.append("the working tree has uncommitted changes")
    return problems


def merge(branch: str, message_file: Path, root: Path = ROOT) -> int:
    message = message_file.read_text(encoding="utf-8")
    problems = preconditions(root, branch) + checklist_problems((root / CHECKLIST).read_text(encoding="utf-8"), message)
    if problems:
        print("merge refused:\n" + "\n".join(f"  - {p}" for p in problems))
        return 1
    with tempfile.TemporaryDirectory(prefix="merge-check-") as folder:
        export(root, branch, Path(folder))
        env = {**os.environ, "CHECK_CLEAN": "1", "CHECK_VENV": str(root / ".venv")}
        if not run([sys.executable, "tools/check.py", "--full"], Path(folder), env):
            print("merge refused: the full checks failed in the clean export")
            return 1
    if not run([sys.executable, "tools/run_tests.py", "--all"], root):
        print("merge refused: the first app's tests failed")
        return 1
    git(root, "switch", "main")
    git(root, "merge", "--no-ff", branch, "-F", str(message_file.resolve()))
    print(f"merge: {branch} merged into main")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge a task branch into main when every check passes.")
    parser.add_argument("branch")
    parser.add_argument("--message", type=Path, required=True, help="merge commit message with the checklist answers")
    args = parser.parse_args()
    return merge(args.branch, args.message)


if __name__ == "__main__":
    sys.exit(main())
