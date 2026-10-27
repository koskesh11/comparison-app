# 017 Failure modes 1-9 live in docs/analyzer-checklist.md

- Date: 2026-10-27 (task 103)
- Decided by: Claude (the owner approved bringing the failure modes back as a checklist, grilling round 28)
- Status: accepted
- Scope: judging what the analyzer reports

## Context
The first project collected nine ways a build analysis goes wrong ("no change in PoB is not no value", config gaps, a
mod's effect depends on the build, ...). They are game-analysis knowledge, not code rules, and they lived in agent
prompts, where nobody outside the studio could read them.

## Decision
- They live in `docs/analyzer-checklist.md`, published, so Claude, the reviewer and a cold reviewer with a clean copy
  of the repo all read the same list.
- Not in CLAUDE.md (private, so a cold reviewer would not see it) and not in the mechanics notes (data the app loads).
- Any item a program can check becomes a test of the analyzer's output; the checklist then names that test.

## Consequences
- The reviewer definition points to the checklist for every review of reported game numbers.
