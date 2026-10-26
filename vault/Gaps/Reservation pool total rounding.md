---
type: gap
status: draft
source: "PoB 2.67.2 CalcPerform.lua:562-566 and 1969-2092, ModStore.lua:317-343; headless Worb probe (task 027 batch 4b, re-run 2026-10-26)"
last_confirmed_patch: "3.29.x"
---

```gap
# No mod line behind this gap: it is a calculation detail (rounding), not an item or passive text PoB fails to read.
# Nothing to match in the audit's wasted-mod test, so the list stays empty on purpose.
patterns: []
```

Research: [[Reservation and reservation efficiency]]. PoB paths are relative to `%APPDATA%\Path of Building Community`.

**Per-skill rounding vs pool total.**
- PoB rounds each skill's percent to 0.01% and adds the percents; the pool total is rounded UP once: `reserved = flat + m_ceil(max * percent / 100)` (`Modules/CalcPerform.lua:562`). `ManaReserved` is capped at the pool (564), `ManaUnreserved = max - reserved` can go negative (566).
- The per-skill `skillData.ManaReservedBase` is rounded up per skill (Worb, Brine King left out: 304 each, 4 skills = 1216) while the pool uses 1214 (re-run: ManaReserved 1214, ManaUnreserved 145).
- Anything that reads the per-skill base (Supreme Ego / Farewell to Flesh "per % reserved" lines) sees that skill's own number floored to a whole percent (`Classes/ModStore.lua:317-343`).
- The game's own rounding direction for the pool total is unverified (wiki says only "whole number").

**Rule.** A fit check uses PoB's `ManaUnreserved` (and `LifeUnreserved`), never a sum of per-skill `ManaReservedBase` or the generator's own arithmetic.
