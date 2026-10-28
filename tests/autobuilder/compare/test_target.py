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


@pytest.mark.parametrize(("name", "follows"), [("Worb", False), ("CoC EK Assa", True), ("Cyclone", False)])
def test_a_calcs_tab_on_another_skill_is_flagged(
    session: PobSession, reference_xml: dict[str, str], variant_xml: dict[str, str], name: str, follows: bool
) -> None:
    """Worb saves its Calcs tab on group 1 while its main skill is group 2; Cyclone is skill 2 of a group whose Calcs
    tab saves skill 1. PoB's CompareEntry points a target's Calcs tab at its main skill (CompareEntry.lua:180)."""
    xml = {**reference_xml, **variant_xml}[name]
    assert session.load_build(xml, name).calcs_on_main_skill is follows
    assert open_target(session, xml, name).summary.calcs_on_main_skill is True


def test_a_target_with_party_buffs_is_flagged(session: PobSession, reference_xml: dict[str, str]) -> None:
    """None of the owner's builds saves party buffs (0 files with ImportedBuffs, 2026-10-28), so this is CoC EK Assa
    with one added the way PartyTab.lua:575-581 saves it; the text itself is not checked, PoB's entry ignores it."""
    xml = reference_xml["CoC EK Assa"]
    empty = '<Party destination="All" ShowAdvanceTools="false" append="false"/>'
    assert xml.count(empty) == 1
    party = xml.replace(empty, empty[:-2] + '><ImportedBuffs name="Aura">Purity of Fire</ImportedBuffs></Party>')
    session.load_build(reference_xml["Worb"], "Worb")
    assert open_target(session, xml, "CoC EK Assa").summary.uses_party is False
    assert open_target(session, party, "party").summary.uses_party is True
