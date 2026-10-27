# 023 The chain reads PoB's Calcs tab, pointed at the main skill

- Date: 2026-10-27 (task 108)
- Decided by: Claude (a technical call; it refines task 102's cross-area C3)
- Status: accepted
- Scope: the damage chain (analysis.chain) and every later read of Calcs-tab numbers

## Context
Task 102 (cross-area C3) chose PoB's main calculation (`mainEnv`, the sidebar's main skill) for the chain. The owner's
model is the Calcs tab's "Skill Hit Damage" section (decision 009). Task 108 found that several of that section's
numbers exist only in the Calcs tab's own calculation: the per-type effective DPS modifier and hit ranges are written
only when `env.mode == "CALCS"` (Modules/CalcOffence.lua:3598, 3653-3655, PoB 2.67.2). The Calcs tab follows its own
skill selection and buff mode (CalcSetup.lua:564-567, 1585-1587; CalcActiveSkill.lua:251-926), and a saved build can
point it elsewhere: Worb saves Calcs group 1 while its main skill is group 2.

## Decision
- The chain reads the Calcs tab's calculation (`calcsEnv`), with the Calcs selection pointed at the sidebar's main
  skill for the read only: group, active skill, part, stages and mines copied from the sidebar, buff mode
  "effective", minion view off. The change goes through `recalculate()` and is put back on every path, like the
  scenario.
- Rows, cell text and sources are PoB's own: the Calcs sections, `CalcsTab:CheckFlag`, `formatCalcStr` and the
  `CalcBreakdownControl` popup; no PoB formula is copied.

## Consequences
- The chain shows the main skill with the numbers of PoB's Calcs tab. The flag "your Calcs tab follows another skill"
  (card 109) stays, because the owner may look at a different skill when he checks the chain in PoB.
- A read costs two more recalculations; they are joined with the scenario's into one change set.
