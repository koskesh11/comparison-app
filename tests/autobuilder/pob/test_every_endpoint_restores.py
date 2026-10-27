"""M6 (S13): every endpoint leaves the build as it was, also when Lua fails halfway.

The first app restored state by convention and two restores left stale numbers (task 102: audit.lua:386-390 kept
FullDPS at the scenario value). Runs once per Endpoint member; while the enum is empty nothing runs. The first
endpoint makes this fail until its test is written here: change the build through the endpoint, show the state
differs while changed (a restore of unchanged state proves nothing), force a Lua error after the change, and compare
the build's numbers and config with the state before.
"""

from typing import Any

import pytest

from autobuilder.pob.endpoints import Endpoint

pytestmark = pytest.mark.pob


@pytest.mark.parametrize("endpoint", list(Endpoint))
def test_endpoint_leaves_the_build_as_it_was(pob_session: Any, endpoint: Endpoint) -> None:
    pytest.fail(f"write the restore test for {endpoint} (module docstring)")
