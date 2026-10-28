"""Your build against a target (compare/service.py) on the reference builds: Worb against CoC EK Assa."""

import pytest

from autobuilder.analysis.chain import read_chain
from autobuilder.analysis.scenarios import Scenario
from autobuilder.compare.service import CALCS_ELSEWHERE, TARGET_PARTY, compare
from autobuilder.errors import NoTargetLoaded
from autobuilder.pob.session import PobSession

pytestmark = pytest.mark.pob


def test_worb_against_coc_ek_assa(pob_session: PobSession, reference_xml: dict[str, str]) -> None:
    yours, target = (reference_xml["Worb"], "Worb"), (reference_xml["CoC EK Assa"], "CoC EK Assa")
    result = compare(pob_session, yours, target, Scenario.PINNACLE_BOSS)
    assert (result.yours.chain.skill, result.target.chain.skill) == ("Winter Orb", "Ethereal Knives")
    assert result.warnings == (CALCS_ELSEWHERE,)  # Worb saves its Calcs tab on group 1, its main skill is group 2
    assert TARGET_PARTY not in result.warnings
    assert (result.yours.dps.key, result.target.dps.key) == ("FullDPS", "FullDPS")
    assert result.table.chips and result.table.steps
    assert read_chain(pob_session, Scenario.PINNACLE_BOSS) == result.yours.chain  # your build stays open, unchanged
    with pytest.raises(NoTargetLoaded):
        read_chain(pob_session, Scenario.PINNACLE_BOSS, "target")
