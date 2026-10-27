"""The scenario picker's four scenarios and PoB's boss box (decisions 010, 022)."""

import pytest

from autobuilder.analysis.scenarios import BOSS_BOX, DEFAULT, Scenario
from autobuilder.pob.endpoints import Endpoint
from autobuilder.pob.session import PobSession


def test_every_scenario_sets_the_boss_box_and_pinnacle_is_the_default() -> None:
    assert set(BOSS_BOX) == set(Scenario)
    assert DEFAULT is Scenario.PINNACLE_BOSS
    assert BOSS_BOX[Scenario.MAPPING] == BOSS_BOX[Scenario.PINNACLE_BOSS] == "Pinnacle"


@pytest.mark.pob
@pytest.mark.parametrize("scenario", list(Scenario))
def test_pob_accepts_every_scenarios_value(
    pob_session: PobSession, reference_xml: dict[str, str], scenario: Scenario
) -> None:
    pob_session.load_build(reference_xml["Worb"], "Worb")
    assert pob_session.call(Endpoint.ANALYSIS_SUMMARY, {"boss": BOSS_BOX[scenario]})["stats"]["FullDPS"] > 0
