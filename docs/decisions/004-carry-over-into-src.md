# 004 Carry code over into src/, checked at the door

- Date: 2026-10-27 (grilling rounds 20-23; replaces decision 4 of 2026-10-26, "restructure, don't rewrite")
- Decided by: owner
- Status: accepted
- Scope: src/, engine/, gui/, the backup folder

## Context
The first plan moved working files into new folders step by step. Rounds 20-21 showed the value lies in carrying over
only what the analyzer needs, each piece checked on the way in; a new repo would add only a clean history, which can be
made once before going public.

## Decision
- In this repo, a new `src/` folder where every check applies from its first file (006).
- `engine/` and `gui/` stay frozen and runnable as reference. Code comes back only when the analyzer needs it, ported
  with its tests and through the checks; frozen files are deleted one by one once ported. An import rule stops `src/`
  from importing `engine/`.
- Before any of this, a full dated backup was made: `old-project-2026-10-27/` next to this repo, read-only, ignored by
  git (task 044). Nothing writes into it.
- The carry-over set is reviewed first with the method in 007 (task 102).

## Consequences
- No ratchet baseline is needed: old code is not checked, new code is clean from the start (round 22).
- The UI is rewritten as part of the analyzer.
