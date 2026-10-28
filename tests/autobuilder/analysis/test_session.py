"""A build opened as saved (decision 018), with the hash of the exact text PoB was given."""

import hashlib

import pytest

from autobuilder.analysis.session import open_build
from autobuilder.pob.session import PobSession

pytestmark = pytest.mark.pob


def test_a_build_opens_with_its_summary_and_the_hash_of_its_bytes(
    pob_session: PobSession, reference_xml: dict[str, str]
) -> None:
    opened = open_build(pob_session, reference_xml["CoC EK Assa"], "CoC EK Assa")
    assert (opened.name, opened.summary.main_skill) == ("CoC EK Assa", "Ethereal Knives")
    assert opened.sha256 == hashlib.sha256(reference_xml["CoC EK Assa"].encode("utf-8")).hexdigest()
