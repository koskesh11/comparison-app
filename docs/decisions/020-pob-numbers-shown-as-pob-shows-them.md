# 020 PoB's numbers are shown the way PoB shows them

- Date: 2026-10-27 (task 102 review)
- Decided by: Claude (the owner said "just do"; he approved the task 102 report with this call in it)
- Status: accepted
- Scope: how the app formats numbers

## Context
The first app truncated every number toward zero (engine/display.py:13), and the target design planned the same rule
for everything (docs/designs/target-design/file-tree.md:81, :229). PoB's Calcs tab rounds half up at a set precision
(Modules/CalcFormat.lua:12-13 and Modules/Common.lua:709-713, PoB 2.67.2). A chain shown with truncated numbers would
not match the Calcs tab the owner checks it against. The game's own rounding is already part of PoB's calculation.

## Decision
- A value that comes from PoB is shown with PoB's rule and precision.
- A number the app works out itself is rounded down where the game rounds down (for example "4 hits, rounded down").
- Python and the browser code share one set of test cases for both rules.

## Consequences
- The truncation rule in the target design's file tree is replaced by these two rules.
- docs/analyzer-checklist.md's "rounded down where the game rounds down" applies to the app's own numbers.
