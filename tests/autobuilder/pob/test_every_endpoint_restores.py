"""M6 (S13): every endpoint leaves the build as its effect says (pob/endpoints.py), also when PoB fails halfway.

The first app restored state by convention and two restores left stale numbers (task 102: audit.lua:386-390 kept
FullDPS at the scenario value). The state compared is build.state: every number of both PoB calculations, the config
inputs and placeholders, the Calcs tab's inputs and the fields of every skill group and gem. Runs once per Endpoint
member, by its effect:
- read: the state is the same after the call;
- temporary: on both reference builds the reply differs from the same read of the build as saved (a restore of
  unchanged state proves nothing), the state is the same afterwards, and again after PoB fails halfway (the next
  BuildOutput raises, lua/fail_output.lua);
- replace: a second build gives a different state (a restore of unchanged state proves nothing), a build PoB cannot
  open fails halfway and leaves none open, and loading the first build again gives its state back exactly.
An endpoint without an effect, or without its case below, fails until the case is written.
"""

import json
from collections.abc import Callable
from typing import Any

import pytest

from autobuilder.errors import BuildLoadFailed, NoBuildLoaded, PobError
from autobuilder.pob.endpoints import EFFECTS, Effect, Endpoint
from autobuilder.pob.session import PobSession

pytestmark = pytest.mark.pob

FailOutput = Callable[[int], None]

READ_REQUESTS: dict[Endpoint, dict[str, Any]] = {
    Endpoint.BUILD_SUMMARY: {},
    Endpoint.BUILD_STATE: {},
}


def summary_without_a_boss(session: PobSession) -> tuple[Any, Any]:
    return session.call(Endpoint.ANALYSIS_SUMMARY, {"boss": "None"}), session.call(Endpoint.BUILD_SUMMARY)


def chain_without_a_boss(session: PobSession) -> tuple[Any, Any]:
    return session.call(Endpoint.ANALYSIS_CHAIN, {"boss": "None"}), session.call(
        Endpoint.ANALYSIS_CHAIN, {"boss": "Pinnacle"}
    )


# Endpoint -> (its reply while the build is changed, the same read of the build as saved)
TEMPORARY_CASES: dict[Endpoint, Callable[[PobSession], tuple[Any, Any]]] = {
    Endpoint.ANALYSIS_SUMMARY: summary_without_a_boss,
    Endpoint.ANALYSIS_CHAIN: chain_without_a_boss,
}


def state(session: PobSession) -> str:
    """The build's state as sorted JSON, so inf and NaN compare as themselves."""
    return json.dumps(session.call(Endpoint.BUILD_STATE), sort_keys=True)


def check_read(session: PobSession, builds: dict[str, str], endpoint: Endpoint) -> None:
    if endpoint not in READ_REQUESTS:
        pytest.fail(f"write the request for {endpoint} in READ_REQUESTS")
    session.load_build(builds["Worb"], "Worb")
    before = state(session)
    session.call(endpoint, READ_REQUESTS[endpoint])
    assert state(session) == before


def check_replace(session: PobSession, builds: dict[str, str], endpoint: Endpoint) -> None:
    assert endpoint is Endpoint.BUILD_LOAD, f"write the replace case for {endpoint}"
    session.load_build(builds["Worb"], "Worb")
    worb = state(session)
    session.load_build(builds["CoC EK Assa"], "CoC EK Assa")
    assert state(session) != worb
    with pytest.raises(BuildLoadFailed):
        session.load_build(builds["Worb"][:500], "broken")
    with pytest.raises(NoBuildLoaded):
        state(session)
    session.load_build(builds["Worb"], "Worb")
    assert state(session) == worb


def check_temporary(session: PobSession, builds: dict[str, str], endpoint: Endpoint, fail: FailOutput) -> None:
    case = TEMPORARY_CASES.get(endpoint)
    if case is None:
        pytest.fail(f"write the temporary case for {endpoint} in TEMPORARY_CASES")
    for name, xml in builds.items():
        session.load_build(xml, name)
        before = state(session)
        changed, saved = case(session)
        assert changed != saved, f"{endpoint} on {name}: the change did not change the reply"
        assert state(session) == before
        fail(1)
        with pytest.raises(PobError, match="forced failure in BuildOutput"):
            case(session)
        assert state(session) == before


CHECKS: dict[Effect, Callable[[PobSession, dict[str, str], Endpoint, FailOutput], None]] = {
    Effect.READ: lambda session, builds, endpoint, _: check_read(session, builds, endpoint),
    Effect.TEMPORARY: check_temporary,
    Effect.REPLACE: lambda session, builds, endpoint, _: check_replace(session, builds, endpoint),
}


@pytest.mark.parametrize("endpoint", list(Endpoint))
def test_endpoint_leaves_the_build_as_its_effect_says(
    pob_session: PobSession, reference_xml: dict[str, str], fail_output: FailOutput, endpoint: Endpoint
) -> None:
    effect = EFFECTS.get(endpoint)
    if effect is None:
        pytest.fail(f"{endpoint} has no effect in pob/endpoints.py EFFECTS")
    CHECKS[effect](pob_session, reference_xml, endpoint, fail_output)


@pytest.mark.parametrize("name", ["Cyclone", "Stone Golem"])
def test_the_chain_puts_back_what_the_calcs_tab_writes(
    pob_session: PobSession, variant_xml: dict[str, str], fail_output: FailOutput, name: str
) -> None:
    """The chain points the Calcs tab at a main skill the saved Calcs tab is not on, and PoB's Calcs recalculation
    writes that gem's Calcs fields (CalcActiveSkill.lua:251, 697, 738, 926): every field is back afterwards."""
    pob_session.load_build(variant_xml[name], name)
    before = state(pob_session)
    pob_session.call(Endpoint.ANALYSIS_CHAIN, {"boss": "Pinnacle"})
    assert state(pob_session) == before
    fail_output(1)
    with pytest.raises(PobError, match="forced failure in BuildOutput"):
        pob_session.call(Endpoint.ANALYSIS_CHAIN, {"boss": "Pinnacle"})
    assert state(pob_session) == before
