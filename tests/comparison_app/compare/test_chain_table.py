"""The chain table (card 109, decisions 009 and 024) on chains recorded from PoB (fixtures/recorded_chains.json)."""

import json
import math
from pathlib import Path
from typing import Any

import pytest

from comparison_app.analysis.chain import Chain, parse_chain
from comparison_app.compare.chain_table import BASE_LABEL, SMALL, build_table
from comparison_app.compare.types import ChainTable, Step

RECORDED = Path(__file__).parents[1] / "fixtures" / "recorded_chains.json"


@pytest.fixture(scope="module")
def chains() -> dict[str, Chain]:
    data = json.loads(RECORDED.read_text(encoding="utf-8"))
    return {name: parse_chain(chain) for name, chain in data["chains"].items()}


def every_step(table: ChainTable) -> list[Step]:
    return [*table.steps, *table.small.steps]


def step(table: ChainTable, label: str) -> Step:
    (found,) = [each for each in every_step(table) if each.label == label]
    return found


def test_a_build_against_itself_has_no_gap(chains: dict[str, Chain]) -> None:
    table = build_table(chains["Worb"], chains["Worb"])
    assert table.chips == ()
    assert {each.gap for each in table.small.steps} == {0.0}
    assert table.small.total == 0.0


def edited(data: dict[str, Any], label: str, column: str, scale: float, add: float = 0.0) -> None:
    (row,) = [row for row in data["rows"] if row["label"] == label]
    (cell,) = [cell for cell in row["cells"] if cell.get("column") == column]
    for value in cell["values"]:
        value["value"] = value["value"] * scale + add


def test_the_gaps_of_a_one_type_hit_multiply_to_the_hit_ratio() -> None:
    """Worb hits with cold only, so its steps' gaps are cold's ratios; base x increased x more x effective is the hit
    by decision 024's construction, so their factors multiply to the target's cold hit over yours. The target is the
    recorded Worb with a 1.5 times bigger cold hit and 100 more cold increased."""
    data = json.loads(RECORDED.read_text(encoding="utf-8"))["chains"]["Worb"]
    yours = parse_chain(data)
    edited(data, "Skill Hit Damage", "Cold", 1.5)
    edited(data, "Total Increased", "Cold", 1.0, 100.0)
    table = build_table(yours, parse_chain(data))
    assert table.shares == {"Cold": 1.0}
    labels = (BASE_LABEL, "Total Increased", "Total More", "Effective DPS Mod")
    gaps = [step(table, label).gap for label in labels]
    assert None not in gaps and gaps[1] == pytest.approx(100 / (100 + 386 + 628))
    assert math.prod(1 + (gap or 0) for gap in gaps) == pytest.approx(1.5)


def test_a_target_without_your_damage_type_has_no_per_type_gap(chains: dict[str, Chain]) -> None:
    """CoC EK Assa deals no cold, PoB has no cold effective DPS modifier for it, so the base step has no gap."""
    assert step(build_table(chains["Worb"], chains["CoC EK Assa"]), BASE_LABEL).gap is None


def test_small_gaps_share_one_row_and_chips_are_the_biggest_first(chains: dict[str, Chain]) -> None:
    table = build_table(chains["Worb"], chains["CoC EK Assa"])
    assert all(each.gap is not None and abs(each.gap) < SMALL for each in table.small.steps)
    sizes = [abs(each.gap) for each in table.chips if each.gap is not None]
    assert sizes == sorted(sizes, reverse=True) and all(size >= SMALL for size in sizes)
    assert table.small.total == pytest.approx(math.prod(1 + (each.gap or 0) for each in table.small.steps) - 1)


def test_damage_types_neither_build_hits_with_are_in_their_own_table(chains: dict[str, Chain]) -> None:
    table = build_table(chains["Worb"], chains["CoC EK Assa"])
    hitting = {kind for chain in (chains["Worb"], chains["CoC EK Assa"]) for hit in chain.hits for kind in hit.by_type}
    unused = {pair.column for each in table.no_effect for pair in each.cells}
    shown = {pair.column for each in every_step(table) for pair in each.cells} - {None, "All Types"}
    assert unused and not unused & hitting
    assert shown <= hitting


def test_a_spell_lines_up_with_an_attacks_main_hand(chains: dict[str, Chain]) -> None:
    table = build_table(chains["Worb"], chains["Cyclone"])
    increased = step(table, "Total Increased")
    assert all(pair.yours and pair.target for pair in increased.cells)
    assert increased.cells[0].target is not None and increased.cells[0].column == "All Types"
    speed = step(table, "Hit Rate")  # Worb's speed step; the target's is its main hand's attacks per second
    assert speed.gap is not None
    assert [each.label for each in every_step(table) if "Att. per second" in each.label] == []
