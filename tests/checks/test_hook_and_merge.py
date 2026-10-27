"""The commit hook and tools/merge_to_main.py refuse a planted violation; the merge checklist must be answered."""

import os
import subprocess
from collections.abc import Callable
from pathlib import Path

import merge_to_main
import pytest

REPO = Path(__file__).resolve().parents[2]
Git = Callable[..., None]
LONG_FILE = "src/autobuilder/too_long.py"
CHECKLIST = "- A1 first item.\n- A2 second item.\n"


def test_checklist_needs_every_item_answered_and_no_no() -> None:
    assert merge_to_main.checklist_problems(CHECKLIST, "A1: yes - by a test\nA2: n/a - no numbers shown\n") == []
    assert merge_to_main.checklist_problems(CHECKLIST, "A1: no - not yet\nA2: yes\n") == [
        "A2: not answered (`A2: yes - <how>` or `n/a - <why>`)",
        "A1: answered no",
    ]


def test_export_holds_tracked_files_only(
    git_repo: Path, run_git: Git, tmp_path_factory: pytest.TempPathFactory
) -> None:
    (git_repo / "tracked.txt").write_text("x\n")
    (git_repo / "untracked.txt").write_text("y\n")
    run_git(git_repo, "add", "tracked.txt")
    run_git(git_repo, "commit", "-q", "-m", "one")
    target = tmp_path_factory.mktemp("export")
    merge_to_main.export(git_repo, "HEAD", target)
    assert sorted(p.name for p in target.iterdir()) == ["tracked.txt"]


@pytest.fixture
def clone(tmp_path: Path, run_git: Git, monkeypatch: pytest.MonkeyPatch) -> Path:
    if not (REPO / ".git").exists():
        pytest.skip("needs a git checkout of the repo (not the clean export)")
    target = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", "--local", str(REPO), str(target)], check=True, timeout=300)
    for args in (["config", "user.email", "t@example.invalid"], ["config", "user.name", "check test"]):
        run_git(target, *args)
    current = subprocess.run(
        ["git", "branch", "--show-current"], cwd=target, capture_output=True, text=True, check=True, timeout=60
    ).stdout.strip()
    if current != "main":  # a clone has only the checked-out branch; the merge needs main too
        run_git(target, "branch", "main", "origin/main")
    monkeypatch.setenv("CHECK_VENV", str(REPO / ".venv"))
    return target


def plant_long_file(root: Path) -> None:
    path = root / LONG_FILE
    path.write_text('"""Planted by the test."""\n' + "X = 1\n" * 400)


@pytest.mark.slow
def test_the_hook_refuses_a_commit_with_a_failed_check(clone: Path, run_git: Git) -> None:
    subprocess.run(["python", "tools/install_hooks.py"], cwd=clone, check=True, timeout=60, capture_output=True)
    plant_long_file(clone)
    run_git(clone, "add", LONG_FILE)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=clone, capture_output=True, text=True, check=True).stdout
    result = subprocess.run(
        ["git", "commit", "-m", "planted"],
        cwd=clone,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ},
        check=False,
    )
    assert result.returncode != 0 and "F4 file sizes" in result.stdout + result.stderr
    assert (
        subprocess.run(["git", "rev-parse", "HEAD"], cwd=clone, capture_output=True, text=True, check=True).stdout
        == head
    )


@pytest.mark.slow
def test_the_merge_script_refuses_a_branch_whose_checks_fail(clone: Path, run_git: Git, tmp_path: Path) -> None:
    run_git(clone, "switch", "-q", "-c", "task-999-planted")
    plant_long_file(clone)
    run_git(clone, "add", LONG_FILE)
    run_git(clone, "commit", "-q", "-m", "planted")
    main_before = subprocess.run(
        ["git", "rev-parse", "main"], cwd=clone, capture_output=True, text=True, check=True
    ).stdout
    checklist = (clone / merge_to_main.CHECKLIST).read_text(encoding="utf-8")
    message = tmp_path / "message.txt"
    message.write_text("merge\n\n" + "".join(f"{item}: n/a - test\n" for item in merge_to_main.ITEM.findall(checklist)))
    assert merge_to_main.merge("task-999-planted", message, root=clone) == 1
    assert (
        subprocess.run(["git", "rev-parse", "main"], cwd=clone, capture_output=True, text=True, check=True).stdout
        == main_before
    )
