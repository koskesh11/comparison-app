"""M6 (S13): every endpoint leaves the build as its effect says (pob/endpoints.py), also when PoB fails halfway.

The first app restored state by convention and two restores left stale numbers (task 102: audit.lua:386-390 kept
FullDPS at the scenario value). The state compared is build.state: every number of PoB's main output, the config
inputs and the main skill selection. Runs once per Endpoint member, by its effect:
- read: the state is the same after the call;
- replace: a second build gives a different state (a restore of unchanged state proves nothing), a build PoB cannot
  open fails halfway and leaves none open, and loading the first build again gives its state back exactly.
An endpoint without an effect, or a read endpoint without a request below, fails until its case is written.
"""

import json
from collections.abc import Callable
from typing import Any

import pytest

from autobuilder.errors import BuildLoadFailed, NoBuildLoaded
from autobuilder.pob.endpoints import EFFECTS, Effect, Endpoint
from autobuilder.pob.session import PobSession

pytestmark = pytest.mark.pob

READ_REQUESTS: dict[Endpoint, dict[str, Any]] = {
    Endpoint.BUILD_SUMMARY: {},
    Endpoint.BUILD_STATE: {},
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


CHECKS: dict[Effect, Callable[[PobSession, dict[str, str], Endpoint], None]] = {
    Effect.READ: check_read,
    Effect.REPLACE: check_replace,
}


@pytest.mark.parametrize("endpoint", list(Endpoint))
def test_endpoint_leaves_the_build_as_its_effect_says(
    pob_session: PobSession, reference_xml: dict[str, str], endpoint: Endpoint
) -> None:
    effect = EFFECTS.get(endpoint)
    if effect is None:
        pytest.fail(f"{endpoint} has no effect in pob/endpoints.py EFFECTS")
    CHECKS[effect](pob_session, reference_xml, endpoint)
