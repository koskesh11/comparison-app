"""Pasted targets saved for PoB to open (decision 012): one request per new link, none for a link already saved or a
pasted code, nothing written for bad input. A temporary folder stands in for Builds\\AutoBuilder\\imports."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from comparison_app.errors import BadLink, Unreadable
from comparison_app.intake import pobbin
from comparison_app.intake.store import ImportStore, import_target

SMALL_XML = '<PathOfBuilding><Build level="1"/></PathOfBuilding>'
LINK = "https://pobb.in/F8CiRC9KVADl"


def files(folder: Path) -> list[str]:
    return sorted(path.name for path in folder.rglob("*") if path.is_file())


def test_a_link_is_fetched_once_and_then_reused(tmp_path: Path, recorded_code: str, opener: Any) -> None:
    fake = opener(recorded_code.encode("ascii"))
    store = ImportStore(tmp_path / "imports")
    first = import_target(LINK, store, lambda build_id: pobbin.fetch(build_id, fake))
    again = import_target("pobb.in/F8CiRC9KVADl", store, lambda build_id: pobbin.fetch(build_id, fake))
    assert len(fake.requests) == 1
    assert (first.import_id, first.fetched, again.fetched) == ("pobb-F8CiRC9KVADl", True, False)
    assert first.path == tmp_path / "imports" / "pobb-F8CiRC9KVADl.xml" and again.xml == first.xml
    assert first.path.read_bytes().decode("utf-8") == first.xml
    assert files(tmp_path) == ["pobb-F8CiRC9KVADl.xml"]


def test_a_pasted_code_is_saved_under_its_hash_without_a_request(tmp_path: Path, code_of: Callable[[str], str]) -> None:
    store = ImportStore(tmp_path / "imports")
    pasted = import_target(f"  {code_of(SMALL_XML)}\n", store, fetch=lambda _: pytest.fail("no request for a code"))
    assert pasted.import_id.startswith("code-") and len(pasted.import_id) == len("code-") + 16
    assert (pasted.xml, pasted.fetched) == (SMALL_XML, False)
    assert import_target(code_of(SMALL_XML), store).import_id == pasted.import_id


@pytest.mark.parametrize(
    ("text", "error"),
    [("https://evil.example/abcd", BadLink), ("https://pobb.in/abc", BadLink), ("not a code", Unreadable)],
)
def test_bad_input_sends_no_request_and_writes_nothing(tmp_path: Path, text: str, error: type[Exception]) -> None:
    with pytest.raises(error):
        import_target(text, ImportStore(tmp_path / "imports"), fetch=lambda _: pytest.fail("no request"))
    assert files(tmp_path) == []


def test_a_fetched_code_that_is_not_a_build_is_not_saved(tmp_path: Path) -> None:
    with pytest.raises(Unreadable):
        import_target(LINK, ImportStore(tmp_path / "imports"), fetch=lambda _: "garbage")
    assert files(tmp_path) == []
