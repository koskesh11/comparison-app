"""Your build against a target (compare/service.py) on the reference builds: Worb against CoC EK Assa."""

import pytest

from autobuilder.analysis.chain import Cell, Chain, SourceTable, read_chain
from autobuilder.analysis.scenarios import Scenario
from autobuilder.compare.service import CALCS_ELSEWHERE, TARGET_PARTY, compare
from autobuilder.errors import NoTargetLoaded
from autobuilder.pob.session import PobSession

pytestmark = pytest.mark.pob


def _cell_difference(one: Cell, other: Cell) -> str:
    if (one.text, one.values) != (other.text, other.values):
        return f"{one.text} {one.values} != {other.text} {other.values}"
    for index, (source, again) in enumerate(zip(one.sources, other.sources, strict=False)):
        if source != again and isinstance(source, SourceTable) and isinstance(again, SourceTable):
            mine, theirs = [repr(row) for row in source.rows], [repr(row) for row in again.rows]
            if sorted(mine) == sorted(theirs):
                moved = [(at, mine[at], theirs[at]) for at in range(len(mine)) if mine[at] != theirs[at]]
                return f"source {index}: same rows, other order: {moved}"
            return f"source {index}: only first {set(mine) - set(theirs)}; only second {set(theirs) - set(mine)}"
        if source != again:
            return f"source {index}: {source} != {again}"
    return f"{len(one.sources)} sources != {len(other.sources)} sources"


def first_difference(one: Chain, other: Chain) -> str | None:
    """The first cell that differs between two chains, named, so a failure says what moved."""
    for row, again in zip(one.rows, other.rows, strict=False):
        for cell, same in zip(row.cells, again.cells, strict=False):
            if cell != same:
                return f"{row.label} / {cell.column}: {_cell_difference(cell, same)}"
    return None if one == other else "the chains differ outside their cells"


def test_worb_against_coc_ek_assa(pob_session: PobSession, reference_xml: dict[str, str]) -> None:
    yours, target = (reference_xml["Worb"], "Worb"), (reference_xml["CoC EK Assa"], "CoC EK Assa")
    result = compare(pob_session, yours, target, Scenario.PINNACLE_BOSS)
    assert (result.yours.chain.skill, result.target.chain.skill) == ("Winter Orb", "Ethereal Knives")
    assert result.warnings == (CALCS_ELSEWHERE,)  # Worb saves its Calcs tab on group 1, its main skill is group 2
    assert TARGET_PARTY not in result.warnings
    assert (result.yours.dps.key, result.target.dps.key) == ("FullDPS", "FullDPS")
    assert result.table.chips and result.table.steps
    assert first_difference(read_chain(pob_session, Scenario.PINNACLE_BOSS), result.yours.chain) is None  # unchanged
    with pytest.raises(NoTargetLoaded):
        read_chain(pob_session, Scenario.PINNACLE_BOSS, "target")
