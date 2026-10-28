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

## Refined after the review (2026-10-28, tasks/reports/108-review.md)
- The pointing is PoB's own: `CompareEntry:SyncCalcsSkillSelection` (CompareEntry.lua:229-248, the compare tab's),
  which also copies the main skill's minion, minion item set and minion skill fields. No field list of ours to fall
  behind PoB.
- CALCS mode reads the Calcs stage, mine and minion-skill counts for every skill, not only the main one
  (CalcActiveSkill.lua:623, 649, 925; the enemy's mine count is the max over all mine skills, :626). The chain copies
  the sidebar's counts into them for every gem, so the premise "pointed at the main skill, the Calcs tab equals the
  sidebar" holds for the whole build instead of only the main skill. Chosen over a flag: the chain is the sidebar's
  build, and the flag "your Calcs tab follows another skill" (card 109) already covers what the owner sees in PoB.
  The game effect on a build with a second mine or stage skill is unverified by output (no such reference build).
- The undo saves every field (not a table) of the Calcs inputs, every group and every gem, and puts them back; build.state
  compares the same fields, so M6 sees what PoB's Calcs recalculation writes (measured: Stone Golem as main skill
  left `skillMinionCalcs` behind before this).
- A cell's raw mod total comes from formatCalcStr itself: a stand-in for the global `formatCalcVal` it rounds with
  (CalcFormat.lua:70) records the value, one placeholder per call. Nothing of formatCalcStr's math is copied.
- An attack's hit (per-type average, AverageHit, CritEffect) is read per attacking hand (output.MainHand/OffHand,
  CalcOffence.lua:2017, 2052, 2179); the totals are the top-level ones PoB combines for both hands (:2510-2513,
  :3959-3964).

## Consequences
- The chain shows the main skill with the numbers of PoB's Calcs tab. The flag "your Calcs tab follows another skill"
  (card 109) stays, because the owner may look at a different skill when he checks the chain in PoB.
- A read costs two more recalculations; they are joined with the scenario's into one change set.
