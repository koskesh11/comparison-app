"""The target beside the owner's build (card 109): PoB's CompareEntry in the same session gives the same chain as the
same build opened as the owner's, and reading one build never moves the other's numbers (they share PoB's global
calculation cache, which every recalculation wipes first)."""

import hashlib
from collections.abc import Iterator

import pytest

from autobuilder.analysis.chain import read_chain
from autobuilder.analysis.scenarios import Scenario
from autobuilder.compare.target import open_target, release_target
from autobuilder.errors import NoTargetLoaded, TargetLoadFailed
from autobuilder.pob.session import PobSession

pytestmark = pytest.mark.pob


@pytest.fixture
def session(pob_session: PobSession) -> Iterator[PobSession]:
    yield pob_session
    release_target(pob_session)


@pytest.mark.parametrize("name", ["CoC EK Assa", "Cyclone"])
def test_the_targets_chain_is_the_chain_of_the_same_build_as_yours(
    session: PobSession, reference_xml: dict[str, str], variant_xml: dict[str, str], name: str
) -> None:
    xml = {**reference_xml, **variant_xml}[name]
    session.load_build(xml, name)
    yours = read_chain(session, Scenario.PINNACLE_BOSS)
    session.load_build(reference_xml["Worb"], "Worb")
    worb = read_chain(session, Scenario.PINNACLE_BOSS)
    opened = open_target(session, xml, name)
    assert (opened.summary.main_skill, opened.sha256) == (yours.skill, hashlib.sha256(xml.encode()).hexdigest())
    assert read_chain(session, Scenario.PINNACLE_BOSS, "target") == yours
    assert read_chain(session, Scenario.PINNACLE_BOSS) == worb


def test_a_target_pob_cannot_open_leaves_none(session: PobSession, reference_xml: dict[str, str]) -> None:
    session.load_build(reference_xml["Worb"], "Worb")
    open_target(session, reference_xml["CoC EK Assa"], "CoC EK Assa")
    with pytest.raises(TargetLoadFailed):
        open_target(session, reference_xml["CoC EK Assa"][:500], "broken")
    with pytest.raises(NoTargetLoaded):
        read_chain(session, Scenario.PINNACLE_BOSS, "target")
