"""M11: the Python write guard (ported from tests/test_pobhost_write_guard.py, task 037). A temporary folder stands in
for the PoB install; the last test uses the shared PoB session, which moves the process into the real install."""

import os
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest

from autobuilder.pob import write_guard
from autobuilder.pob.session import PobSession
from autobuilder.pob.write_guard import GUARD_MESSAGE, guard_dir, unguard_dir

NO_SUCH = "__write_guard_probe_no_such_dir__"


def refused(action: Callable[..., object], *args: object) -> None:
    with pytest.raises(PermissionError) as caught:
        action(*args)
    assert str(caught.value) == GUARD_MESSAGE


@pytest.fixture
def guarded(tmp_path: Path) -> Iterator[Path]:
    root = tmp_path / "install"
    root.mkdir()
    (root / "existing.txt").write_text("hello", encoding="utf-8")
    cwd = Path.cwd()
    guard_dir(root)
    yield root
    unguard_dir(root)  # before cleanup, or the cleanup itself is refused
    os.chdir(cwd)


def test_relative_write_after_chdir_is_refused(guarded: Path) -> None:
    os.chdir(guarded)
    refused(open, "relative.txt", "w")
    assert not (guarded / "relative.txt").exists()


def test_absolute_writes_inside_are_refused_in_every_form(guarded: Path) -> None:
    target = guarded / "absolute.txt"
    refused(open, target, "w")
    refused(open, str(target).upper(), "a")  # case-insensitive
    refused(open, os.fsencode(target), "xb")
    refused(open, guarded / "existing.txt", "r+")
    refused(target.write_text, "x")
    assert not target.exists()


def test_os_level_writes_inside_are_refused(guarded: Path, tmp_path: Path) -> None:
    existing = guarded / "existing.txt"
    refused(os.open, str(guarded / "low.txt"), os.O_WRONLY | os.O_CREAT)
    refused(os.open, str(existing), os.O_RDWR)
    refused(os.remove, existing)
    refused(os.mkdir, guarded / "sub")
    refused(os.rename, existing, guarded / "moved.txt")
    refused(os.replace, existing, guarded / "moved.txt")
    refused(os.rename, existing, tmp_path / "moved.txt")
    assert existing.exists() and not (guarded / "sub").exists()


def test_rmdir_inside_is_refused(guarded: Path) -> None:
    unguard_dir(guarded)
    (guarded / "empty").mkdir()
    guard_dir(guarded)
    refused(os.rmdir, guarded / "empty")
    assert (guarded / "empty").is_dir()


def test_reads_inside_are_allowed(guarded: Path) -> None:
    assert (guarded / "existing.txt").read_text(encoding="utf-8") == "hello"
    os.chdir(guarded)
    with open("existing.txt", "rb") as handle:
        assert handle.read() == b"hello"
    os.close(os.open("existing.txt", os.O_RDONLY))


def test_writes_elsewhere_and_to_a_lookalike_sibling_are_allowed(guarded: Path, tmp_path: Path) -> None:
    os.chdir(guarded)
    other = tmp_path / "other"
    other.mkdir()
    (other / "out.txt").write_text("ok", encoding="utf-8")
    os.replace(other / "out.txt", other / "moved.txt")
    os.remove(other / "moved.txt")
    sibling = Path(str(guarded) + "-sibling")
    sibling.mkdir()
    (sibling / "x.txt").write_text("ok", encoding="utf-8")
    assert os.listdir(other) == [] and (sibling / "x.txt").is_file()


def test_an_fd_open_is_ignored(guarded: Path, tmp_path: Path) -> None:
    fd = os.open(tmp_path / "fd.txt", os.O_WRONLY | os.O_CREAT)
    with open(fd, "w") as handle:
        handle.write("ok")
    assert guarded.is_dir()


def test_the_hook_installs_once(guarded: Path) -> None:
    guard_dir(guarded)
    guard_dir(guarded)
    assert write_guard._GUARD.installed


@pytest.mark.pob
def test_relative_write_in_a_real_session_is_refused(pob_session: PobSession, pob_dir: Path) -> None:
    assert os.path.normcase(Path.cwd()) == os.path.normcase(pob_dir)
    # a folder that does not exist: a broken guard fails with FileNotFoundError, not a stray file
    refused(open, f"{NO_SUCH}/x.txt", "w")
    assert not (pob_dir / NO_SUCH).exists()
    with open("Launch.lua", "rb") as handle:
        assert handle.read(1)
