"""F11 (unstaged deletions) and F12 (line endings) on a throwaway git repo."""

from collections.abc import Callable
from pathlib import Path

from checks import eol, git_state

Write = Callable[[str, str], Path]
Git = Callable[..., None]


def test_eol_reports_a_crlf_text_file_without_attributes(git_repo: Path, write: Write, run_git: Git) -> None:
    write("notes.md", "one\r\ntwo\r\n")
    run_git(git_repo, "add", "notes.md")
    problems = eol.check(git_repo)
    assert len(problems) == 1 and problems[0].startswith("notes.md: stored with crlf")


def test_eol_passes_once_gitattributes_normalizes(git_repo: Path, write: Write, run_git: Git) -> None:
    write(".gitattributes", "* text=auto eol=lf\n/frozen/** -text\n")
    write("notes.md", "one\r\ntwo\r\n")
    write("frozen/old.py", "x = 1\r\n")
    run_git(git_repo, "add", ".")
    assert eol.check(git_repo) == []


def test_git_state_reports_an_unstaged_deletion(git_repo: Path, write: Write, run_git: Git) -> None:
    path = write("kept.txt", "x\n")
    run_git(git_repo, "add", ".")
    run_git(git_repo, "commit", "-q", "-m", "one")
    assert git_state.check(git_repo) == []
    path.unlink()
    assert git_state.check(git_repo) == ["kept.txt: deleted but not staged (git rm it, or git restore it)"]
