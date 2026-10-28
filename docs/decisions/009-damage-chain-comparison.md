# 009 The comparison is PoB's damage chain

- Date: 2026-10-27 (grilling rounds 13-16)
- Decided by: owner; layout details proposed by Claude and approved
- Status: accepted; the worth column waits until after milestone 1 (019)
- Scope: the analyzer's main view

## Context
The owner's model is PoB's Calcs tab, section "Skill Hit Damage". A clickable mockup with real PoB 2.67.2 numbers (Worb
against pobb.in/v8XfQn1yFnAs, Pinnacle Boss, Winter Orb part 1) was approved: "This is exactly how I envisioned it."
Its data came from PoB's own hover breakdown, `actor.breakdown[damageType]` (CalcOffence.lua:3360-3610). The mockup
lives at https://claude.ai/artifact/Reo6j5waAVyfGARJ9Bmtpj (private); an exported copy is docs/mockup/damage-chain.html
(2026-10-28, decision 025).

## Decision
- The vectors are the terms of the damage calculation, whatever their source: increased, more, added flat damage,
  damage effectiveness, penetration, resistance reduction, damage taken, crit, speed, and so on. The skill's own base,
  added flat damage and conversion / "gain as" are separate vectors (round 3).
- One row per step of the chain, in PoB's calculation order, with biggest-gap-first chips on top. Columns: you | target
  | the gap | what it is worth in DPS (a PoB recalculation) | sources. Every source is one click away.
- Milestone 1 covers hit damage of the main skill.
- Gaps under 3 % are grouped into one expandable row whose header shows the combined total; each difference worth 3 %
  or more gets its own row (rounds 3-4). The same applies to defensive values when they come.
- Values with no effect stay, listed in a table of their own (an overcapped resistance can feed another mod).
- The skill parts and settings saved in the two PoBs are used exactly as saved (011).
- Visual design (colours, styling) is reworked later; the function is fixed.

## Consequences
- The mockup and its scratch script are the reference, not a throwaway prototype: the chain is built for real in
  `src/`.
