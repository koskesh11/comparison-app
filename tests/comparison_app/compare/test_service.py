"""Your build against a target (compare/service.py) on the reference builds: Worb against CoC EK Assa."""

import pytest
from tests.comparison_app.conftest import stages

from comparison_app.analysis.chain import Cell, Chain, SourceTable, read_chain
from comparison_app.analysis.scenarios import Scenario
from comparison_app.compare.recalc import changes_to_match, recalculate
from comparison_app.compare.service import CALCS_ELSEWHERE, TARGET_PARTY, compare
from comparison_app.compare.skill_settings import Match
from comparison_app.errors import NoTargetLoaded
from comparison_app.pob.session import PobSession

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
    # two different main skills: the chain waits until the owner picks the target's group (decision 011)
    assert (result.settings.match, result.table) == (Match.DIFFERENT_SKILL, None)
    assert [each.box.var for each in result.config.looks_wrong] == ["multiplierChannelling"]
    assert first_difference(read_chain(pob_session, Scenario.PINNACLE_BOSS), result.yours.chain) is None  # unchanged
    with pytest.raises(NoTargetLoaded):
        read_chain(pob_session, Scenario.PINNACLE_BOSS, "target")


def test_the_chain_shows_when_both_main_skills_are_set_up_alike(
    pob_session: PobSession, reference_xml: dict[str, str]
) -> None:
    worb = (reference_xml["Worb"], "Worb")
    result = compare(pob_session, worb, worb, Scenario.PINNACLE_BOSS)
    assert result.settings.match is Match.SAME
    assert result.table is not None and result.table.steps and result.table.chips == ()
    assert result.config.differences == ()


# Neighbouring stages of the variety builds (decision 014, extended; 026): one pair per path through the comparison.
STAGE_PAIRS = [
    ("Elemental Hit Slayer", "Level 12", "Level 28", Match.DIFFERENT_SKILL),  # Spectral Throw, then Elemental Hit
    ("Elemental Hit Slayer", "2 Stone 90", "4 Stone 95", Match.SETTINGS_DIFFER),  # Fire Attack, then Cold Attack
    ("Winter Orb", "Nightmare Pinnacles", "Occultist Swap", Match.SAME),
    ("Phys Dot Elementalist", "95", "Autobomber Swap", Match.SAME),  # a minion main skill: no hit, few rows
]


@pytest.mark.parametrize("pair", STAGE_PAIRS, ids=lambda pair: f"{pair[0]}: {pair[1]} -> {pair[2]}")
def test_neighbouring_stages_of_a_build(
    pob_session: PobSession, variety_xml: dict[str, str], pair: tuple[str, str, str, Match]
) -> None:
    build, first, second, match = pair
    by_title = dict(stages(variety_xml[build]))
    result = compare(pob_session, (by_title[first], first), (by_title[second], second), Scenario.PINNACLE_BOSS)
    assert result.settings.match is match
    assert (result.table is not None) == (match is Match.SAME)
    if match is Match.SETTINGS_DIFFER:  # the button: your stage recalculated with the target's setting
        changes = changes_to_match(result.settings, result.yours.snapshot, result.target.snapshot)
        recalculated = recalculate(pob_session, Scenario.PINNACLE_BOSS, changes)
        assert recalculated.chain.part == result.target.chain.part != result.yours.chain.part
