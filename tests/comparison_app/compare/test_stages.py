"""Build stages (compare/stages.py, decision 026) on the variety builds: PoB's list, the switch, the mixed refusal."""

import pytest

from comparison_app.analysis.chain import read_chain
from comparison_app.analysis.scenarios import Scenario
from comparison_app.compare.service import compare
from comparison_app.compare.stages import Stages, mixed_message, read_stages, set_stage
from comparison_app.errors import MixedStages
from comparison_app.pob.session import PobSession

PHYS_DOT_PARTS = {"tree": "90 self cast", "items": "90", "skills": "90", "config": "90"}


def test_the_mixed_message_names_the_parts() -> None:
    message = mixed_message("Your", Stages(("90", "90 self cast"), None, PHYS_DOT_PARTS))
    assert message.startswith("Your build mixes stages: tree '90 self cast'; items, skills and config '90'.")


@pytest.mark.pob
def test_pobs_stages_and_the_active_one(
    pob_session: PobSession, variety_xml: dict[str, str], reference_xml: dict[str, str]
) -> None:
    pob_session.load_build(variety_xml["Elemental Hit Slayer"], "Elemental Hit Slayer")
    stages = read_stages(pob_session)
    assert (len(stages.titles), stages.titles[0], stages.active) == (7, "Level 12", "4 Stone 95")
    pob_session.load_build(variety_xml["Phys Dot Elementalist"], "Phys Dot Elementalist")
    assert (read_stages(pob_session).mixed(), read_stages(pob_session).parts) == (True, PHYS_DOT_PARTS)
    pob_session.load_build(reference_xml["Worb"], "Worb")
    assert read_stages(pob_session) == Stages(("Default",), "Default", {part: "Default" for part in PHYS_DOT_PARTS})


@pytest.mark.pob
def test_a_stage_switch_lasts_for_the_reads(pob_session: PobSession, variety_xml: dict[str, str]) -> None:
    pob_session.load_build(variety_xml["Elemental Hit Slayer"], "Elemental Hit Slayer")
    assert set_stage(pob_session, "Level 12").active == "Level 12"
    assert read_chain(pob_session, Scenario.PINNACLE_BOSS).skill == "Spectral Throw"  # the level-12 stage's skill


@pytest.mark.pob
def test_a_mixed_build_is_compared_only_on_a_stage_picked(pob_session: PobSession, variety_xml: dict[str, str]) -> None:
    phys = (variety_xml["Phys Dot Elementalist"], "Phys Dot Elementalist")
    winter = (variety_xml["Winter Orb"], "Winter Orb")
    with pytest.raises(MixedStages, match="tree '90 self cast'; items, skills and config '90'"):
        compare(pob_session, phys, winter, Scenario.PINNACLE_BOSS)
    result = compare(pob_session, phys, winter, Scenario.PINNACLE_BOSS, stages=("90", None))
    assert result.yours.chain.skill == "Kinetic Blast"  # the "90" stage's main skill
