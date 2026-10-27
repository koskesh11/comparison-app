"""A throwaway repo tree for the check tests: each test plants a violation and expects the check to report it."""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

Write = Callable[[str, str], Path]


@pytest.fixture
def write(tmp_path: Path) -> Write:
    def write_file(relative: str, text: str) -> Path:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
        return path
    return write_file


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    for args in (["init", "-q"], ["config", "core.autocrlf", "false"], ["config", "user.email", "t@example.invalid"],
                 ["config", "user.name", "check test"]):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True, timeout=60)
    return tmp_path


@pytest.fixture
def run_git() -> Callable[..., None]:
    def run(root: Path, *args: str) -> None:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, timeout=60)
    return run
