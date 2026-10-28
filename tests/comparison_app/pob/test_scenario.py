"""The scenario context (pob/lua/analysis/scenario.lua) and recalculate() (build.lua): a change goes through PoB's own
recalculation order and is put back on every path. The first app's restore left the scenario's numbers in place
(audit.lua:386-390; task 102 area A measured CoC EK Assa FullDPS 14,420,419 instead of 15,136,639)."""

import re
from collections.abc import Callable

import pytest

from comparison_app.errors import NoBuildLoaded, PobError
from comparison_app.pob.endpoints import Endpoint
from comparison_app.pob.session import PobSession

pytestmark = pytest.mark.pob

CONFIG_SET = re.compile(r"<ConfigSet [^>]*>")


def saved_with_boss(xml: str, boss: str) -> str:
    """The build as PoB would save it with the boss box set to `boss` (one Input line in the active config set)."""
    return CONFIG_SET.sub(lambda tag: f'{tag.group(0)}<Input name="enemyIsBoss" string="{boss}"/>', xml, count=1)


@pytest.mark.parametrize("name", ["Worb", "CoC EK Assa"])
@pytest.mark.parametrize("boss", ["None", "Boss", "Uber"])
def test_a_scenario_gives_the_numbers_of_the_build_saved_that_way(
    pob_session: PobSession, reference_xml: dict[str, str], name: str, boss: str
) -> None:
    """recalculate() against PoB's own path: a fresh load of the build saved with that boss box."""
    pob_session.load_build(saved_with_boss(reference_xml[name], boss), name)
    expected = pob_session.call(Endpoint.BUILD_SUMMARY)["stats"]
    pob_session.load_build(reference_xml[name], name)
    assert pob_session.call(Endpoint.ANALYSIS_SUMMARY, {"boss": boss})["stats"] == expected


def test_the_measured_stale_restore_is_gone(pob_session: PobSession, reference_xml: dict[str, str]) -> None:
    """PoB 2.67.2 numbers; a PoB update may move them (re-measure, keep the shape of the test)."""
    pob_session.load_build(reference_xml["CoC EK Assa"], "CoC EK Assa")
    under_no_boss = pob_session.call(Endpoint.ANALYSIS_SUMMARY, {"boss": "None"})["stats"]["FullDPS"]
    assert round(under_no_boss) == 14_420_419
    assert round(pob_session.summary().stats["FullDPS"]) == 15_136_639


@pytest.mark.parametrize("boss", ["Bogus", "pinnacle", 3, None])
def test_a_value_pob_does_not_list_is_refused_before_any_change(
    pob_session: PobSession, reference_xml: dict[str, str], boss: object
) -> None:
    pob_session.load_build(reference_xml["Worb"], "Worb")
    before = pob_session.call(Endpoint.BUILD_STATE)
    with pytest.raises(PobError, match="needs one of PoB's values for enemyIsBoss"):
        pob_session.call(Endpoint.ANALYSIS_SUMMARY, {"boss": boss})
    assert pob_session.call(Endpoint.BUILD_STATE) == before


def test_a_restore_that_fails_leaves_no_build_open(
    pob_session: PobSession, reference_xml: dict[str, str], fail_output: Callable[[int], None]
) -> None:
    """The change and the restore both fail: the build's state is unknown, so reads refuse until the next load."""
    pob_session.load_build(reference_xml["Worb"], "Worb")
    fail_output(2)
    with pytest.raises(PobError, match="could not put the build back, load it again"):
        pob_session.call(Endpoint.ANALYSIS_SUMMARY, {"boss": "Uber"})
    with pytest.raises(NoBuildLoaded):
        pob_session.summary()
