# 007 Fresh AI reviewers, only where decided

- Date: 2026-10-27 (grilling rounds 19-21, 26, 29)
- Decided by: owner
- Status: accepted
- Scope: code reviews

## Context
A reviewer that did not write the code finds what the author misses. The first project's six review departments and
four gates stood in for checks that did not exist.

## Decision
- One read-only reviewer definition (Read, Grep, Glob, Bash; no edits). Every brief carries the evidence rule and the
  task's current "Done when".
- Reviews run only where the owner decided:
  - **Area review** (round 21), for large code: first a map built by tools (imports, calls across files, Python-Lua
    calls, public functions); then one reviewer per area of about 1,000-2,500 lines with the map and the neighbours'
    interfaces; then a cross-area pass over the map and the area reports; every verdict cites file:line and is checked
    by re-opening the lines.
  - **Cold review** at each milestone and before going public: a fresh reviewer with no project history gets a clean
    copy of the repo only, must explain the structure and run the tests.
- Every reviewer Claude starts is named to the owner before it runs: which, what for, time box (008).

## Consequences
- Anything a test or check can verify is a test or check, not a review step.
