r"""The app's folders and limits (app/settings.py): the only reader of the environment, the write root exactly
Builds\AutoBuilder."""

from pathlib import Path

import pytest

from comparison_app.app.settings import ENV_BUILDS_DIR, ENV_HOME, ENV_POB_DIR, HOST, PORT, Settings
from comparison_app.errors import PobNotInstalled, SetupProblem


def env(tmp_path: Path, **extra: str) -> dict[str, str]:
    builds = tmp_path / "Builds"
    builds.mkdir(exist_ok=True)
    return {
        ENV_HOME: str(tmp_path / "project"),
        ENV_BUILDS_DIR: str(builds),
        ENV_POB_DIR: str(tmp_path / "pob"),
        **extra,
    }


def test_the_folders_come_from_the_environment_given(tmp_path: Path) -> None:
    settings = Settings.from_environment(env(tmp_path))
    assert (settings.host, settings.port) == (HOST, PORT) == ("127.0.0.1", 8765)
    assert settings.write_root == tmp_path / "Builds" / "AutoBuilder"
    assert settings.imports_dir == tmp_path / "Builds" / "AutoBuilder" / "imports"
    assert settings.data_dir == tmp_path / "project" / "userdata"
    assert settings.pob_paths().user_dir == tmp_path / "project" / "userdata" / "pob"


def test_the_write_root_is_never_the_builds_folder_itself(tmp_path: Path) -> None:
    settings = Settings.from_environment(env(tmp_path))
    broken = Settings(**{**settings.__dict__, "write_root": settings.builds_dir})
    with pytest.raises(SetupProblem, match="writes only to"):
        broken.validate()


def test_setup_problems_say_what_to_fix(tmp_path: Path) -> None:
    with pytest.raises(SetupProblem, match="Builds folder was not found"):
        Settings.from_environment({**env(tmp_path), ENV_BUILDS_DIR: str(tmp_path / "missing")}).validate()
    with pytest.raises(PobNotInstalled):
        Settings.from_environment(env(tmp_path)).validate()  # no PoB in tmp_path / "pob"


def test_the_project_and_documents_are_found_without_overrides() -> None:
    settings = Settings.from_environment({"APPDATA": str(Path("/appdata").resolve())})
    assert (settings.data_dir.parent / "pyproject.toml").is_file()
    assert settings.builds_dir.parts[-2:] == ("Path of Building", "Builds")
