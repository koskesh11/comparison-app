# 002 The generator is frozen, not merged

- Date: 2026-10-26, confirmed in grilling round 24 (2026-10-27)
- Decided by: owner
- Status: accepted
- Scope: the generator branch, the frozen/* tags, engine/

## Context
The generator lived on its own branch (`task-035-fireball-starter`, about 26,000 lines). Task 035 stopped mid-review
(2 HIGH, 17 MEDIUM findings); the generated Fireball wore a 173-Str body armour at 74 Str because the generator never
read PoB's requirement output; 13 files were over 400 lines; it added a second way of calling PoB.

## Decision
The generator is not merged, now or later. Its heads are kept as git tags `frozen/generator-035`,
`frozen/generator-035-t14` and `frozen/generator-035-tree`. Pieces may be ported later, with their tests, through the
checks (004, 006); the branch is never merged. Frozen with it: the audit suggestions and both apply-and-save buttons
(round 2). The key-number tiles stay.

## Consequences
- The PoB access layer has to be right first: the analyzer and a later generator both sit on it.
- The tags are the only record of the frozen work; they stay until the history clean-up before any going public.
