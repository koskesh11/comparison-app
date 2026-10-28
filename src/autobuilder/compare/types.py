"""The comparison's records (card 109, decisions 009 and 024): the chain of two builds side by side."""

from collections.abc import Mapping
from dataclasses import dataclass

from autobuilder.analysis.chain import Cell


@dataclass(frozen=True)
class Pair:
    column: str | None  # the damage type column ("Cold", "All Types"); None in one-column rows
    yours: Cell | None  # None when your chain has no such row or cell
    target: Cell | None


@dataclass(frozen=True)
class Step:
    section: str  # PoB's Calcs section id
    label: str  # PoB's row label, yours where both have it; the derived base step has its own
    cells: tuple[Pair, ...]
    gap: float | None  # decision 024: target factor / your factor - 1; None for a row that is no factor of the hit
    factors: tuple[tuple[str | None, float | None, float | None], ...] = ()  # (column, yours, target) the gap uses
    derived: bool = False  # the base step, which PoB shows no row for (decision 024): arithmetic on PoB's numbers


@dataclass(frozen=True)
class SmallGaps:
    steps: tuple[Step, ...]  # every step whose gap is under 3 % either way (decision 009)
    total: float  # the product of their factors minus one


@dataclass(frozen=True)
class ChainTable:
    steps: tuple[Step, ...]  # PoB's order, without the small gaps
    small: SmallGaps
    no_effect: tuple[Step, ...]  # the cells of damage types neither build hits with (decision 009:21-23)
    chips: tuple[Step, ...]  # the steps with a gap of 3 % or more, biggest first
    shares: Mapping[str, float]  # your average hit by damage type, as shares that add up to 1
