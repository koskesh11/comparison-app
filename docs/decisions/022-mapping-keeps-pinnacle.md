# 022 The Mapping scenario keeps the boss box at Pinnacle

- Date: 2026-10-27 (task 106)
- Decided by: owner ("stay pinnacle")
- Status: accepted
- Scope: the scenario picker (decision 010)

## Context
Decision 010 lists four scenarios: Standard Boss, Pinnacle Boss, Uber Pinnacle Boss, plus Mapping, and says a scenario
sets only PoB's "Is the enemy a Boss?" box (values None, Boss, Pinnacle, Uber; Modules/ConfigOptions.lua:2086, PoB
2.67.2). Task 102 inferred that Mapping means "None" (cross-area C10); no record said it. Asked, the owner answered that
Mapping stays at Pinnacle.

## Decision
- Mapping sets the box to Pinnacle, like the Pinnacle Boss scenario.

## Consequences
- In milestone 1, Mapping and Pinnacle Boss give the same numbers; what else Mapping means comes with later work.
- `src/autobuilder/analysis/scenarios.py` maps the four scenarios to PoB's values.
