"""M7: the "recalculate with the target's skill setting" button (decision 011) changes in PoB exactly what a real
change to the build does.

Runs once per ChangeKind member; while the enum is empty nothing runs. The first change kind makes this fail until
its test is written here: apply the change in memory and recalculate, then apply it to a copy of the build, save,
reload and recalculate; the chain values must match, or the change is shown as "not tested" with the reason.
"""

from typing import Any

import pytest

from comparison_app.pob.endpoints import ChangeKind

pytestmark = pytest.mark.pob


@pytest.mark.parametrize("kind", list(ChangeKind))
def test_in_memory_change_matches_a_saved_change(pob_session: Any, kind: ChangeKind) -> None:
    pytest.fail(f"write the parity test for {kind} (module docstring)")
