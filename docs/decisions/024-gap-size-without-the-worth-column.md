# 024 The size of a chain gap, before the worth column exists

- Date: 2026-10-28 (task 109)
- Decided by: Claude (a technical call inside decision 009's 3 % rule; the worth column itself waits, decision 019)
- Status: accepted
- Scope: compare/chain_table.py, milestone 1

## Context
Decision 009 groups gaps "worth under 3 %" into one row and gives each gap of 3 % or more its own row, worth meaning
DPS as a PoB recalculation would show it. That column comes after milestone 1 (019), so milestone 1 needs another
measure of a gap's size that uses only PoB's numbers.

## Decision
- A chain step is a factor in PoB's hit product. A step's gap is how much the target's factor is above or below
  yours: `target factor / your factor - 1`. The factor is:
  - more, effective DPS modifier, crit effect, hit rate or speed, chance to hit: the value as PoB shows it, as a
    multiplier (a "more" of 95 % is 1.95);
  - increased: `1 + increased / 100`, with the type's total as PoB adds it (All Types plus the type);
  - base and added damage: the average of min and max.
- A step with one cell per damage type is weighted by the type's share of your average hit (`Chain.hits`, PoB's
  `<Type>HitAverage`): `gap = sum(share x (ratio - 1))`. The share and the main damage type come from PoB's numbers.
- The gap is arithmetic on two PoB numbers, not a recalculation. The page says so next to the 3 % group, and the worth
  column (019) replaces it as the measure when it comes.

## Consequences
- Steps that are not a factor (for example a crit chance below 100 % that feeds the crit effect) are grouped by the
  factor PoB derives from them (the crit effect), not by their own numbers; they keep their own rows for reading.
- A gap is first-order: two gaps do not add up exactly to the DPS difference. The combined total of the 3 % group is
  the product of its factors minus one, which is exact for the steps it holds.
