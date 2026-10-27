# 006 Programs enforce the code rules

- Date: 2026-10-27 (grilling rounds 16-22)
- Decided by: owner; limits are Claude's to manage (round 21)
- Status: accepted; the checks themselves are a later task
- Scope: src/ and its tests

## Context
The first project knew the rules (layers, one-way dependencies, small files) but nothing enforced them, so feature
pressure won. On 2026-10-27 there was no CI, no pre-commit config, no linter or type-checker config and no git hooks.
The owner: "a way to enforce all these rules and practices in this project at all times, always."

## Decision
- Code rules are checks (programs), not prose. A check blocks by default.
- Hand-written source never goes over 400 lines, with no exemptions: a file that needs more is doing two jobs and is
  split. Only files we do not write are exempt, each listed with its reason (vendor files such as PoB's runtime
  definitions, generated files, data and fixtures).
- Claude manages the limits and reports every change to them.
- Fast checks (linter, import rules, sizes) run on every commit; slow ones (type checker, full tests) run when merging
  into main, through a local merge script; GitHub checks are added before going public.
- An architecture checklist is gone through on every merge.

## Consequences
- The checks for `src/` come right after task 102 (roadmap). Their exact tools are decided there.
- The global ECC rules on this machine (for example "files under 800 lines", "80 % coverage", black + isort) do not
  apply here where the checks say otherwise.
