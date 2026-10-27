"""tools/check.py: one line per check and one summary line that names every failure (S5, S11)."""

from pathlib import Path

import check
import pytest
from checks.common import Skip


def _fails(_root: Path) -> list[str]:
    return ["a.py:1: planted problem"]


def _skips(_root: Path) -> list[str]:
    raise Skip("not here")


def _crashes(_root: Path) -> list[str]:
    raise ValueError("boom")


def test_summary_names_every_failure(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
                                     tmp_path: Path) -> None:
    monkeypatch.setattr(check, "CHECKS", [
        check.Check("X1", "passes", lambda _root: []), check.Check("X2", "fails", _fails),
        check.Check("X3", "skips", _skips), check.Check("X4", "crashes", _crashes),
        check.Check("X5", "only full", _fails, full=True)])
    assert check.main([], root=tmp_path) == 1
    lines = capsys.readouterr().out.splitlines()
    assert [line[:4].strip() for line in lines if not line.startswith(" ")][:4] == ["X1", "X2", "X3", "X4"]
    assert "      - a.py:1: planted problem" in lines
    assert "      - the check crashed: ValueError: boom" in lines
    assert lines[-1] == "check: 2 FAILED (X2 fails, X4 crashes); 1 passed, 1 skipped"


def test_all_green_returns_zero(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
                                tmp_path: Path) -> None:
    monkeypatch.setattr(check, "CHECKS", [check.Check("X1", "passes", lambda _root: [])])
    assert check.main([], root=tmp_path) == 0
    assert capsys.readouterr().out.splitlines()[-1] == "check: all 1 passed, 0 skipped"


def test_missing_dev_tools_name_the_install_command(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("CHECK_VENV", str(tmp_path / "no-venv"))
    assert check.tool("ruff", "check", ".")(tmp_path) == [f"dev tools not installed: {check.INSTALL}"]
