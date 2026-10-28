# 026 Build stages: each build as saved, or a stage the owner picks

- Date: 2026-10-28 (grilling, docs/history/2026-10-28-grilling-stages-and-learning.md, part 1)
- Decided by: owner
- Status: accepted; supersedes decision 018's "both builds exactly as saved" for the choice of stage only
- Scope: loading your build and the target, the page's stage dropdowns (cards 112-113)

## Context
Guides and many builds carry several stages (PoB "loadouts": "Level 28", "4 Stone 95", "Endgame"), each a tree, an
item set, a skill set and a config set with the same title, switched together by PoB (Modules/Build.lua:359-416).
Decision 018 compared both builds exactly as saved, so a guide could only be compared on the stage its author saved.
Of the owner's 64 builds, 13 have several sets; the three variety builds have 7-11 stages each, and one (Phys Dot
Elementalist) is saved with a mix: tree "90 self cast", items, skills and config "90".

## Decision
- Both builds get a stage dropdown like PoB's, listing the stages exactly as PoB lists them; a build with one stage
  shows none.
- Both dropdowns start on the stage saved in the file, every time; no choice is remembered.
- Switching a stage switches all four sets with PoB's own functions, in memory, and reruns the whole comparison. No
  file is ever changed.
- A build saved with mixed stages is not compared. The app says which parts are mixed and offers two ways: fix it in
  PoB and save, or "sort it for me" (pick one of the mixed stages; the app switches all four parts in memory).
- Main skills that do no hit (auras, curses, minions, damage over time) get no special handling in milestone 1.

## Consequences
- Everything else in decision 018 holds: no leave-out, no models, the settings of the chosen stage as saved.
- The target's stage switch runs on PoB's CompareEntry, which has the same four tabs; that it switches the same way is
  to be confirmed when it is built (card 112).
