"""F11: no unstaged deletions before a commit; they are the trace of an interrupted run, not a change anyone meant."""

from pathlib import Path

from checks.common import git

PATH_START = 3  # porcelain v1: two status letters and a space, then the path


def check(root: Path) -> list[str]:
    problems = []
    for entry in git(root, "status", "--porcelain=v1", "-z").split("\0"):
        if len(entry) > PATH_START and entry[1] == "D":
            problems.append(f"{entry[PATH_START:]}: deleted but not staged (git rm it, or git restore it)")
    return problems
