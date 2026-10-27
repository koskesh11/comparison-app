"""Targets the owner pastes, saved to Builds\\AutoBuilder\\imports so he can open them in PoB (decision 012).

Rewrites the first app's engine/pobbin.py:139-156: a pobb.in build already saved is reused, so pasting the same link
again sends no request; a pasted code gets an id from its hash. Files are written whole or not at all.
"""

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from autobuilder.intake import code, pobbin

CODE_ID_CHARS = 16


@dataclass(frozen=True)
class ImportedBuild:
    import_id: str  # "pobb-<pobb.in id>" or "code-<start of the code's sha256>"
    xml: str
    path: Path
    fetched: bool  # a request went to pobb.in for it (False: a pasted code, or a saved import reused)


class ImportStore:
    def __init__(self, folder: Path) -> None:
        self.folder = folder

    def path(self, import_id: str) -> Path:
        return self.folder / f"{import_id}.xml"

    def saved(self, import_id: str) -> ImportedBuild | None:
        path = self.path(import_id)
        if not path.is_file():
            return None
        return ImportedBuild(import_id, code.checked_xml(path.read_bytes()), path, fetched=False)

    def save(self, import_id: str, xml: str, *, fetched: bool) -> ImportedBuild:
        self.folder.mkdir(parents=True, exist_ok=True)
        path = self.path(import_id)
        temp = path.with_suffix(".xml.tmp")
        temp.write_bytes(xml.encode("utf-8"))
        temp.replace(path)
        return ImportedBuild(import_id, xml, path, fetched=fetched)


def import_target(text: str, store: ImportStore, fetch: Callable[[str], str] = pobbin.fetch) -> ImportedBuild:
    """A pasted pobb.in link or PoB code, decoded and saved. Nothing is fetched or written for bad input."""
    text = text.strip()
    if not pobbin.looks_like_link(text):
        xml = code.decode(text)
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:CODE_ID_CHARS]
        return store.save(f"code-{digest}", xml, fetched=False)
    build_id = pobbin.parse_link(text)
    import_id = f"pobb-{build_id}"
    return store.saved(import_id) or store.save(import_id, code.decode(fetch(build_id)), fetched=True)
