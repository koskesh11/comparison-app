"""The comparison's records (compare/types.py): frozen, and a step is PoB's own row unless it says it is derived."""

import dataclasses

import pytest

from autobuilder.compare.types import Pair, Step


def test_a_step_is_pobs_row_unless_marked_derived() -> None:
    step = Step("HitDamage", "Total More", (Pair("Cold", None, None),), 0.1)
    assert (step.derived, step.factors) == (False, ())


def test_records_are_frozen() -> None:
    step = Step("Crit", "Crit Chance", (), None)
    with pytest.raises(dataclasses.FrozenInstanceError):
        step.gap = 1.0  # type: ignore[misc]
