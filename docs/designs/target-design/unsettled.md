<!-- Reference part of ../target-design.md: Appendix A. Unsettled technical points. -->

## Appendix A. Unsettled technical points

These are design points I could not settle from reading the code. None needs an owner decision; each is resolved by a
spike or a measurement inside the step named.

- **A1. The vector catalogue (step 22).** The extraction method is proven by the 2026-10-26 prototype (`Tabulate` rows on the
  main skill's mod list and the enemy's). Not settled: the split of "base damage" into the skill's own base, added flat
  damage and conversion / gain-as (the prototype reads only min / max base and the totals); how the defence vectors are read;
  which of a difference's vectors it is listed under when it moves several (the design says the one it moves most);
  and the exact wording of "next step's value" (marginal value), which may reuse PoB's power report (`powerReportJSON`,
  frozen with the tree search and restorable from the tag).
- **A2. Concurrency (step 16).** The design says one job at a time, two sessions per job. Today the pool has two engines
  behind one global lock and the intended model is not written anywhere; I inferred this one from the comparison needing
  both builds at once. `ctypes` releases the GIL during a call ([ctypes documentation](https://docs.python.org/3/library/ctypes.html)),
  so two states could run on two threads, but nothing here was measured and nothing in the design depends on it.
- **A3. The compare entry (step 22).** The target is loaded twice: as a second `BuildSession` (for the vectors) and as PoB's
  compare entry inside your engine (for tree paths and PoB's power rows, about 195 MB of Lua heap). Whether the entry
  can go once the target has its own session is not known.
- **A4. Endpoint effects (step 14).** The `effect` of each endpoint in section 4.8 is my reading of the Lua. The check in
  `call` may show that some are wrong (for example `applyChangesJSON` also restores skills and config).
- **A5. Lua write roots (step 7).** After apply-and-save leaves, the Lua sandbox probably no longer needs the imports folder
  as a write root (Python saves imports). Tightening it is untested, so the design keeps today's roots.
- **A6. Which tests really boot PoB (steps 6 to 20).** I classified them by reading and by `grep`; the runner today guesses
  by imports. Each file is re-checked when it moves, and a wrong marker shows up as a skip or a failure.
- **A7. Wire names (steps 16 to 19).** The design says `own` / `target` where the code says `player` / `guide`. Recorded
  fixtures and the pinned golden keys use the old names, so the rename is its own commit with regenerated fixtures.
- **A8. Strict style policy (step 19).** I believe styles set through an element's `style` object pass `style-src 'self'`
  and the `style` attribute does not; it is verified in the browser, not assumed.
- **A9. Fonts (step 19).** Five static font files or two variable ones; the licence file must travel with them.
- **A10. JavaScript lint.** None at first (`node --check` plus the safety test). Add Biome or ESLint when the UI grows past
  about 2,000 lines or gains many interactive widgets, as the audit suggests.
- **A11. Package name and Python floor.** `autobuilder` and `>=3.12` are my choices; renaming either is mechanical. Mypy,
  ruff, pytest and import-linter all support 3.14 (their PyPI pages list it on 2026-10-27).
- **A12. Line budgets.** All `~` numbers in section 2 are estimates; the file-size check will say if one is wrong.

This document's links were checked with `curl -sIL` on 2026-10-27; all 31 answered HTTP 200 directly.
