# 018 Milestone 1 uses both builds exactly as saved

- Date: 2026-10-27 (task 102 review)
- Decided by: Claude (the owner said "just do"; he approved the task 102 report with this call in it)
- Status: accepted
- Scope: the analyzer in milestone 1, and the src/ tests that use the reference builds

## Context
The first app could leave a skill out of the calculation and apply draft models (decision 014 reads Worb with "Aspect
of the Brine King" left out, Winter Orb gem count 5 and a 4-hit model). Decision 011 says the two builds are compared
with the settings saved in them, exactly as they are. The task 102 review found that leaving a skill out needs its own
restore step, a control in the UI and a safe settings file (102-cross-area.md, C2).

## Decision
- In milestone 1 both builds are calculated exactly as saved: no skill left out, no gem count set by hand, no model.
- The src/ tests read Worb as saved. Decision 014's Worb settings apply again when leaving skills out comes back.
- Draft models show only as "if this note is right: X" (013), when the code that reads them exists.

## Consequences
- Decision 014's line on Worb's settings is set aside for src/ until leaving skills out comes back.
- The first app's leave-out code (engine/audit.lua:416-445) stays in engine/ as reference.
