"""Every folder, port and limit the app uses, resolved once (docs/designs/target-design/interfaces.md 4.5).

The only module that reads the environment (check F5). The write root is exactly Builds\\AutoBuilder, never the Builds
folder itself (review of card 105, finding 3); PoB's install half of that is pob/session.check_paths. Documents is read
from Windows' own setting for it (the registry's User Shell Folders, which follows a Documents folder OneDrive moved),
with the home folder's Documents as the fallback.
"""

import os
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from comparison_app.errors import SetupProblem
from comparison_app.pob.session import PobPaths, check_paths

HOST, PORT = "127.0.0.1", 8765  # the server never binds elsewhere
ENV_POB_DIR = "POB_DIR"  # the name the first app and the tests already use
ENV_BUILDS_DIR = "COMPARISON_APP_BUILDS_DIR"
ENV_HOME = "COMPARISON_APP_HOME"  # the project folder; found by walking up to pyproject.toml otherwise
WRITE_FOLDER = "AutoBuilder"  # the one folder under Builds the app writes to (decision 003, 012)
IMPORTS_FOLDER = "imports"  # imported targets (decision 012)
JOB_KEEP = 20  # finished jobs kept
JOB_RUN_LIMIT_S = 900.0  # a running job older than this is given up
SHELL_FOLDERS = r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders"


@dataclass(frozen=True)
class Settings:
    host: str
    port: int
    pob_dir: Path
    builds_dir: Path
    write_root: Path  # builds_dir / "AutoBuilder", always
    imports_dir: Path
    data_dir: Path  # <project>/userdata: the API token, logs, PoB's user data for the app's sessions
    web_dir: Path  # <project>/web: the page (card 113)
    job_keep: int = JOB_KEEP
    job_run_limit_s: float = JOB_RUN_LIMIT_S

    def pob_paths(self) -> PobPaths:
        return PobPaths(self.pob_dir, self.data_dir / "pob", self.write_root)

    @classmethod
    def from_environment(cls, env: Mapping[str, str] | None = None) -> "Settings":
        source = os.environ if env is None else env
        home = Path(source[ENV_HOME]) if ENV_HOME in source else _project()
        appdata = Path(source.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
        pob_dir = Path(source.get(ENV_POB_DIR, str(appdata / "Path of Building Community")))
        builds = (
            Path(source[ENV_BUILDS_DIR])
            if ENV_BUILDS_DIR in source
            else _documents(source) / "Path of Building" / "Builds"
        )
        write_root = builds / WRITE_FOLDER
        return cls(
            HOST, PORT, pob_dir, builds, write_root, write_root / IMPORTS_FOLDER, home / "userdata", home / "web"
        )

    def validate(self) -> None:
        """Absolute folders, PoB installed (check_paths), the Builds folder there; one friendly message each."""
        folders = (self.pob_dir, self.builds_dir, self.data_dir, self.web_dir)
        if not all(folder.is_absolute() for folder in folders):
            raise SetupProblem(f"the app's folders must be absolute paths: {', '.join(map(str, folders))}")
        if self.write_root != self.builds_dir / WRITE_FOLDER:
            raise SetupProblem(f"the app writes only to {self.builds_dir / WRITE_FOLDER}, not {self.write_root}")
        if not self.builds_dir.is_dir():
            raise SetupProblem(f"PoB's Builds folder was not found: {self.builds_dir} (set {ENV_BUILDS_DIR})")
        check_paths(self.pob_paths())


def _project() -> Path:
    for folder in Path(__file__).resolve().parents:
        if (folder / "pyproject.toml").is_file():
            return folder
    raise SetupProblem(f"the project folder was not found above {Path(__file__)} (set {ENV_HOME})")


def _documents(env: Mapping[str, str]) -> Path:
    """Windows' Documents folder as Explorer has it, else the home folder's Documents."""
    if sys.platform == "win32":
        import winreg  # noqa: PLC0415 - Windows only

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, SHELL_FOLDERS) as key:
                value, _ = winreg.QueryValueEx(key, "Personal")
        except OSError:
            value = None
        if isinstance(value, str) and value:
            expanded = value
            for name, setting in env.items():  # %USERPROFILE% and friends, from the environment given
                expanded = expanded.replace(f"%{name}%", setting)
            return Path(expanded)
    return Path.home() / "Documents"
