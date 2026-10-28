"""Starting the app (app/main.py): checked settings, a fresh token in userdata/api-token, the log set up; PoB starts
only on the first comparison."""

from pathlib import Path

import pytest

from comparison_app.app.main import prepare
from comparison_app.app.settings import ENV_BUILDS_DIR, ENV_HOME, ENV_POB_DIR, Settings
from comparison_app.errors import PobNotInstalled


def test_prepare_writes_a_fresh_token_and_starts_no_pob(tmp_path: Path, pob_dir: Path) -> None:
    (tmp_path / "Builds").mkdir()
    env = {ENV_HOME: str(tmp_path), ENV_BUILDS_DIR: str(tmp_path / "Builds"), ENV_POB_DIR: str(pob_dir)}
    state = prepare(Settings.from_environment(env))
    assert (tmp_path / "userdata" / "api-token").read_text(encoding="utf-8") == state.token
    assert state._session is None  # opened on the first comparison
    assert prepare(Settings.from_environment(env)).token != state.token


def test_prepare_refuses_a_missing_pob(tmp_path: Path) -> None:
    (tmp_path / "Builds").mkdir()
    env = {ENV_HOME: str(tmp_path), ENV_BUILDS_DIR: str(tmp_path / "Builds"), ENV_POB_DIR: str(tmp_path / "pob")}
    with pytest.raises(PobNotInstalled):
        prepare(Settings.from_environment(env))
