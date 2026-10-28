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
  - base damage: PoB shows no row for it, and a ratio of "Added Min/Max" alone would leave out the skill's own base.
    The base step is the type's average hit ("Skill Hit Damage", min and max averaged) divided by its increased, more
    and effective DPS factors: the rest of the hit, base, added x effectiveness, conversion and whatever else PoB
    multiplies in. It is marked derived. Added Min and Max keep their rows for reading, without a gap;
  - speed: "Hit Rate" where PoB shows it, else the casts, attacks or trigger rate per second (Worb: TotalDPS /
    AverageHit = 1,435,203.8 / 222,512.2 = 6.45 = its Hit Rate, not its 9.57 casts per second).
- A step with one cell per damage type is weighted by the type's share of your average hit (`Chain.hits`, PoB's
  `<Type>HitAverage`): `gap = sum(share x (ratio - 1))`. The share and the main damage type come from PoB's numbers.
- The gap is arithmetic on two PoB numbers, not a recalculation. The page says so next to the 3 % group, and the worth
  column (019) replaces it as the measure when it comes.

## Consequences
- Steps that are not a factor (for example a crit chance below 100 % that feeds the crit effect) are grouped by the
  factor PoB derives from them (the crit effect), not by their own numbers; they keep their own rows for reading.
- A gap is first-order: two gaps do not add up exactly to the DPS difference. The combined total of the 3 % group is
  the product of its factors minus one; for a dual-wield attack the two hands' products are averaged first, as PoB
  averages the hands' damage (CalcOffence.lua:2068-2073; review 111, finding 3: multiplying both hands counted a 2 %
  gap on each hand as 4 %). It is exact for one hand's steps; with two hands, speed steps are averaged too, where
  PoB takes the harmonic mean, so the total stays first-order there.
