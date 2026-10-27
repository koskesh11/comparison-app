# Merge checklist (M12)

What no program checks, gone through on every merge into main (decision 006). `tools/merge_to_main.py` refuses a merge
whose message does not answer every item on its own line, as `A1: yes - <how>`, `A1: n/a - <why>` or `A1: no - <why>`;
a `no` stops the merge.

- A1 Each new file sits in the folder (row) that matches its job, and its name says what it does.
- A2 Every number the change shows names its PoB output key or its mechanics note (decision 013).
- A3 No constant PoB already knows is typed in (S9), and no value is defined in two places.
- A4 Nothing from the frozen list came in: the generator, apply-and-save, audit suggestions, pricing (ROADMAP "Not now").
- A5 Every change to a build in PoB goes through `recalculate()` and is undone on every path, errors included.
- A6 Text the user reads comes from the code that computes the value (S8), not from a copy.
- A7 Where the change touches items or the tree, the PoB-access facts hold (S3: cluster jewel nodes from
  `spec.subGraphs`; an emptied slot keeps its gems; ticked flasks stay on after a removal).
- A8 The task card's Done when is met, each item with its evidence (file:line, command output or a PoB number).
- A9 docs/ARCHITECTURE.md still matches the code (layers, endpoints, checks, tests).
- A10 For a change that reports game numbers, docs/analyzer-checklist.md was gone through.
