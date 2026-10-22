---
type: gap
status: draft
source: "PoB 2.67.2 (3.29) source, file:line below; engine/audit.lua; headless test on FR CoC v4 (in memory, 2026-10-21)"
last_confirmed_patch: "3.29.x"
---

```gap
# Stopgap for an audit blind spot: with Mageblood the audit can't remove or edit flask lines.
# Live right away: gap patterns load regardless of status.
patterns:
  - match: "Magic Utility Flasks constantly apply their Flask Effects"
    slot: "Belt"
    why: "PoB keeps these flasks on whether ticked or not; unticking does nothing - test by swapping the flask"
  - match: "increased effect"
    slot: "Flask"
    why: "with Mageblood the audit can't remove flask lines (PoB re-adds the saved flask); not wasted - test by swapping the flask"
  - match: "during Effect"
    slot: "Flask"
    why: "with Mageblood this flask is always on; the audit can't remove the line (PoB re-adds the saved flask) - test by swapping the flask"
```

PoB paths are relative to `%APPDATA%\Path of Building Community`.

**Mageblood (3.29 wording):** "Leftmost (2-4) Magic Utility Flasks constantly apply their Flask Effects to you" (`Data/Uniques/belt.lua:551`); the Foulborn version says "Rightmost". Parsed in `Modules/ModParser.lua:5269-5270`. The belt pattern matches both.

**Why the audit is blind here:**
- PoB picks the first N MAGIC utility flasks in slot order and never checks whether the flask is ticked (`Modules/CalcPerform.lua:1578-1599`).
- It re-adds each of them from the saved item (`itemsTab.items[slot.selItemId]`, `CalcPerform.lua:1582-1593`). The audit's calc override (repSlotName / repItem) therefore can't replace or edit those flasks. v4 test: override Sapphire -> Silver gave a phantom second flask (Cyclone 9.75/s, cold res total 168).
- `engine/audit.lua:233` skips unticked flasks, but Mageblood still applies them.

**Working method (verified headless):** replace `build.itemsTab.items[id]` in place, calculate, restore. That is an engine fix for engineering; these patterns only relabel lines that show no change.

**Side effect:** the patterns apply to every build, also without Mageblood. A flask line with "increased effect" or "during Effect" that shows no change is then labelled "can't measure" with Mageblood wording instead of "wasted". Remove the two flask patterns once the engine fix lands.
