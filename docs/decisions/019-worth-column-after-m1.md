# 019 The worth column and the config ranking come after milestone 1

- Date: 2026-10-27 (task 102 review)
- Decided by: Claude (the owner said "just do"; he approved the task 102 report with this call in it)
- Status: accepted
- Scope: the analyzer's main view and config differences, milestone 1 only

## Context
Decision 009 gives the chain a column "what it is worth in DPS (a PoB recalculation)", and decision 010 sorts config
differences "by how much they change the numbers". Both need one PoB recalculation per difference. A chain gap also has
to be written as a PoB mod, and PoB's calculation override has no field for an extra mod (CalcSetup.lua, task 102
review). Whether every chain term can be written that way is not checked. The roadmap's milestone 1 has neither; its
item 1 after milestone 1 is "the marginal value of each vector".

## Decision
- Milestone 1 shows the chain with you, target, the gap and the sources, without the worth column.
- Config differences are listed in PoB's own order in milestone 1.
- The worth column and sorting config differences by their effect are part of item 1 after milestone 1.

## Consequences
- Decisions 009 (the worth column) and 010 (the sort order) apply from item 1 on.
- The first app's per-difference measuring code (engine/guide_check.py:246-264, engine/guide_check_retest.py:8-17) stays
  in engine/ until then.
