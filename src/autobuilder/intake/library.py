"""Your builds: the .xml files in PoB's Builds folder (the first app's engine/server.py:43-57, kept with one fix).

The fix: one check decides both what is listed and what may be opened. The first app listed every .xml it found
(server.py:45), including ones its resolver then refused (server.py:53-54), such as a link that points outside.
"""

from dataclasses import dataclass
from pathlib import Path

from autobuilder.errors import InvalidInput
from autobuilder.intake.code import checked_xml


@dataclass(frozen=True)
class BuildFile:
    path: str  # relative to the Builds folder, with forward slashes: what the page sends back
    name: str
    folder: str
    modified: float


class Library:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def _allowed(self, path: Path) -> Path | None:
        """The real file when it is an .xml file inside the Builds folder, after following links; else None."""
        try:
            real = path.resolve(strict=True)
        except OSError:
            return None
        if real.suffix.lower() != ".xml" or not real.is_file() or not real.is_relative_to(self.root):
            return None
        return real

    def builds(self) -> list[BuildFile]:
        """Every build that `read` will open, newest first."""
        found = []
        for path in self.root.rglob("*.xml"):
            if self._allowed(path) is None:
                continue
            relative = path.relative_to(self.root)
            folder = relative.parent.as_posix()
            found.append(
                BuildFile(relative.as_posix(), path.stem, "" if folder == "." else folder, path.stat().st_mtime)
            )
        return sorted(found, key=lambda build: build.modified, reverse=True)

    def read(self, relative: str) -> str:
        """The build's XML text; InvalidInput outside the folder, Unreadable when it is not a PoB build."""
        real = self._allowed(self.root / relative)
        if real is None:
            raise InvalidInput("Pick an .xml build inside the Path of Building Builds folder.")
        return checked_xml(real.read_bytes())
