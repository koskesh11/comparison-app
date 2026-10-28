"""Your chain and the target's side by side, step by step (card 109, decisions 009 and 024).

Steps are PoB's Calcs rows in PoB's order. Rows of the hit product (increased, more, effective DPS modifier, speed,
crit effect, chance to hit) are aligned by what they are, so a spell lines up with an attack's main hand row; the
others by their label. A step's gap is the target's factor over yours (decision 024); per-type steps weigh each type
by its share of your hit. The base step is derived: PoB shows no row for it.
"""

import math
from collections.abc import Callable, Iterable, Mapping

from autobuilder.analysis.chain import Cell, Chain, Hit, Row
from autobuilder.compare.types import ChainTable, Pair, SmallGaps, Step

SMALL = 0.03  # decision 009: gaps under 3 % share one row
ALL_TYPES = "All Types"
OFF_HAND = "OH "
HAND_PREFIXES = ("MH ", OFF_HAND)
# Labels as PoB 2.67.2 writes them (tests/autobuilder/fixtures/recorded_chains.json), without the hand prefix.
FACTOR_STEPS = {
    "Total Increased": "increased",
    "Total More": "more",
    "Effective DPS Mod": "effective",
    "Eff. DPS Mod": "effective",
    "Skill Hit Damage": "hit",
    "Hit Damage": "hit",
    "Crit Effect Mod": "crit effect",
    "Chance to Hit": "hit chance",
}
SPEED_LABELS = ("Hit Rate", "Casts per second", "Att. per second", "Skill Trigger Rate")  # the first one shown counts
BASE_LABEL = "Base damage (the rest of the hit)"
NOT_A_FACTOR = {"hit"}  # the hit range is the result of the other steps, shown for reading

Key = tuple[str, str]  # (hand, step or label)
Factors = dict[str | None, float | None]  # per column


def _bare(label: str) -> str:
    return label[3:] if label.startswith(HAND_PREFIXES) else label


def _speed_label(chain: Chain) -> str | None:
    bare = {_bare(row.label) for row in chain.rows}
    return next((label for label in SPEED_LABELS if label in bare), None)


def _key(row: Row, speed: str | None) -> Key:
    hand = "OH" if row.label.startswith(OFF_HAND) else ""
    bare = _bare(row.label)
    step = "speed" if bare == speed else FACTOR_STEPS.get(bare)
    return (hand, step) if step else (hand, f"{row.section}:{bare}")


def _numbers(cell: Cell) -> list[float | None]:
    return [value.value for value in cell.values]


def _shown(row: Row) -> dict[str | None, float | None]:
    """A row's value per column: the one number of a cell, or the average of a min-max cell."""
    found: dict[str | None, float | None] = {}
    for cell in row.cells:
        numbers = _numbers(cell)
        known = [number for number in numbers if number is not None]
        found[cell.column] = sum(known) / len(known) if known and len(known) == len(numbers) else None
    return found


def _factors(step: str, row: Row) -> Factors:
    shown = _shown(row)
    if step not in ("increased", "more"):
        return dict(shown)
    every = shown.get(ALL_TYPES) or 0.0
    factors: Factors = {}
    for column, value in shown.items():
        if column == ALL_TYPES or value is None:
            continue
        own = value / 100
        factors[column] = 1 + every / 100 + own if step == "increased" else (1 + every / 100) * (1 + own)
    return factors


def _base(by_step: Mapping[str, Factors]) -> Factors:
    """The base step per type: the average hit over its increased, more and effective factors (decision 024)."""
    base: Factors = {}
    for column, hit in by_step.get("hit", {}).items():
        divisors = [by_step.get(step, {}).get(column) for step in ("increased", "more", "effective")]
        known = [divisor for divisor in divisors if divisor]
        base[column] = hit / math.prod(known) if hit is not None and len(known) == len(divisors) else None
    return base


def _ratio(yours: float | None, target: float | None) -> float | None:
    if yours is None or target is None:
        return None
    if yours == 0:
        return None if target == 0 else math.inf
    return target / yours - 1


def _gap(yours: Factors, target: Factors, shares: Mapping[str, float]) -> float | None:
    if list(yours) == [None] or list(target) == [None]:
        return _ratio(yours.get(None), target.get(None))
    weighted = [(share, _ratio(yours.get(kind), target.get(kind))) for kind, share in shares.items() if share > 0]
    if not weighted or any(ratio is None for _, ratio in weighted):
        return None
    return sum(share * ratio for share, ratio in weighted if ratio is not None)


def _shares(hits: Iterable[Hit]) -> dict[str, float]:
    total: dict[str, float] = {}
    for hit in hits:
        for kind, value in hit.by_type.items():
            total[kind] = total.get(kind, 0.0) + value
    whole = sum(total.values())
    return {kind: value / whole for kind, value in total.items()} if whole > 0 else {}


def _indexed(chain: Chain) -> dict[Key, Row]:
    speed = _speed_label(chain)
    return {_key(row, speed): row for row in chain.rows}  # in PoB's order


def _pairs(yours: Row | None, target: Row | None, keep: Callable[[str | None], bool]) -> tuple[Pair, ...]:
    mine = {cell.column: cell for cell in yours.cells} if yours else {}
    theirs = {cell.column: cell for cell in target.cells} if target else {}
    columns = list(mine) + [column for column in theirs if column not in mine]
    return tuple(Pair(column, mine.get(column), theirs.get(column)) for column in columns if keep(column))


def _side_by_side(yours: Factors, target: Factors) -> tuple[tuple[str | None, float | None, float | None], ...]:
    columns = list(yours) + [column for column in target if column not in yours]
    return tuple((column, yours.get(column), target.get(column)) for column in columns)


def _factor_rows(rows: Mapping[Key, Row]) -> dict[Key, Factors]:
    return {key: _factors(key[1], row) for key, row in rows.items() if key[1] in (*FACTOR_STEPS.values(), "speed")}


def _base_step(
    hand: str, yours: Mapping[Key, Factors], target: Mapping[Key, Factors], shares: Mapping[str, float]
) -> Step:
    mine = _base({key[1]: value for key, value in yours.items() if key[0] == hand})
    theirs = _base({key[1]: value for key, value in target.items() if key[0] == hand})
    label = f"{OFF_HAND}{BASE_LABEL}" if hand else BASE_LABEL
    gap = _gap(mine, theirs, shares) if mine and theirs else None
    return Step("HitDamage", label, (), gap, factors=_side_by_side(mine, theirs), derived=True)


def _size(step: Step) -> float:
    return abs(step.gap) if step.gap is not None else -1.0


def build_table(yours: Chain, target: Chain) -> ChainTable:
    shares = _shares(yours.hits) or _shares(target.hits)
    hitting = set(shares) | set(_shares(target.hits))

    def shown(column: str | None) -> bool:
        return column is None or column == ALL_TYPES or column in hitting

    mine, theirs = _indexed(yours), _indexed(target)
    factors_yours, factors_target = _factor_rows(mine), _factor_rows(theirs)
    steps: list[Step] = []
    no_effect: list[Step] = []
    for key in list(mine) + [key for key in theirs if key not in mine]:
        if key[1] == "increased":  # the derived base step comes before the first scaling step
            steps.append(_base_step(key[0], factors_yours, factors_target, shares))
        row_yours, row_target = mine.get(key), theirs.get(key)
        row = row_yours or theirs[key]
        both = key in factors_yours and key in factors_target
        gap = _gap(factors_yours[key], factors_target[key], shares) if both and key[1] not in NOT_A_FACTOR else None
        side = _side_by_side(factors_yours.get(key, {}), factors_target.get(key, {}))
        steps.append(Step(row.section, row.label, _pairs(row_yours, row_target, shown), gap, factors=side))
        unused = _pairs(row_yours, row_target, lambda column: not shown(column))
        if unused:
            no_effect.append(Step(row.section, row.label, unused, None))
    small = [step for step in steps if step.gap is not None and abs(step.gap) < SMALL]
    kept = tuple(step for step in steps if not any(step is each for each in small))
    total = math.prod(1 + step.gap for step in small if step.gap is not None) - 1
    chips = tuple(sorted((step for step in kept if step.gap is not None), key=_size, reverse=True))
    return ChainTable(kept, SmallGaps(tuple(small), total), tuple(no_effect), chips, shares)
