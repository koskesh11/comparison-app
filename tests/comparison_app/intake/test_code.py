"""A PoB code to its XML (ported from tests/test_pobbin.py DecodeTests), plus the cut-off stream the first app let
through (task 102, area F finding 9) and a decoded build PoB itself refuses."""

import base64
import zlib

import pytest

from comparison_app.errors import BuildLoadFailed, TooLarge, Unreadable
from comparison_app.intake import code
from comparison_app.intake.pobbin import MAX_CODE_BYTES
from comparison_app.pob.session import PobSession

SMALL_XML = '<PathOfBuilding><Build level="1"/></PathOfBuilding>'


def make_code(xml: str) -> str:
    return base64.urlsafe_b64encode(zlib.compress(xml.encode("utf-8"))).decode("ascii")


def test_the_recorded_pobb_in_code_decodes_to_a_pob_build(recorded_code: str) -> None:
    xml = code.decode(recorded_code)
    assert "<PathOfBuilding>" in xml[:200] and "<Build" in xml


def test_a_small_build_round_trips() -> None:
    assert code.decode(make_code(SMALL_XML)) == SMALL_XML


@pytest.mark.parametrize(
    "text",
    [
        "!!!not base64!!!",
        base64.urlsafe_b64encode(b"plain text, not zlib").decode(),
        make_code("<html><body>hello</body></html>"),
        base64.urlsafe_b64encode(zlib.compress("<PathOfBuilding>é</PathOfBuilding>".encode("latin-1"))).decode(),
    ],
    ids=["not base64", "not zlib", "not a PoB build", "not UTF-8"],
)
def test_text_that_is_not_a_build_code_is_unreadable(text: str) -> None:
    with pytest.raises(Unreadable, match="Couldn't read that build"):
        code.decode(text)


def test_a_cut_off_code_is_refused() -> None:
    whole = zlib.compress(SMALL_XML.encode("utf-8"))
    cut = base64.urlsafe_b64encode(whole[: len(whole) - 6]).decode()
    with pytest.raises(Unreadable, match="cut off"):
        code.decode(cut)


def test_a_zlib_bomb_stops_at_the_limit() -> None:
    bomb = make_code("<PathOfBuilding>" + "a" * (10 * 1024 * 1024) + "</PathOfBuilding>")
    assert len(bomb) < MAX_CODE_BYTES  # tiny on the wire, huge once inflated
    with pytest.raises(TooLarge):
        code.decode(bomb)
    with pytest.raises(TooLarge):
        code.decode("A" * (MAX_CODE_BYTES + 1))


@pytest.mark.parametrize(
    "xml", ['<!DOCTYPE x [<!ENTITY a "b">]><PathOfBuilding/>', "<PathOfBuilding><!ENTITY a 'b'></PathOfBuilding>"]
)
def test_entities_and_doctype_are_refused(xml: str) -> None:
    with pytest.raises(Unreadable):
        code.decode(make_code(xml))


@pytest.mark.pob
def test_a_decoded_build_pob_cannot_open_fails_with_pobs_reason(pob_session: PobSession) -> None:
    xml = code.decode(make_code("<PathOfBuilding><Build level='1'></PathOfBuilding>"))
    with pytest.raises(BuildLoadFailed, match="trying to close <Build>"):
        pob_session.load_build(xml, "pasted")
