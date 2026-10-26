---
type: gap
status: draft
source: "PoB 2.67.2 ModParser.lua:4044-4049, Data/ModCache.lua:14324, CalcPerform.lua:2169-2170, TreeData/3_29/tree.lua:85942; headless modLib.parseMod (task 027 batch 4b)"
last_confirmed_patch: "3.29.x"
---

```gap
# Purposeful Harbinger: PoB's patterns end in "up to N%", this line says "up to a maximum of N%", so it parses to nothing.
patterns:
  - match: "for each Herald affecting you, up to a maximum of"
    why: "PoB adds 0 aura effect for this line; the real effect is +8% increased aura effect on you per Herald affecting you, max +40%. A build with Herald(s) in the aura slot is under-counted; add it by hand or do not credit it, label it 'not counted by PoB'"
```

**Evidence per pattern (PoB source lines, kept out of the player text; moved 2026-10-26, task 027 merge).**
- "for each Herald affecting you, up to a maximum of": Data/ModCache.lua:14324 stores {nil, <line>}

Research: [[Aura effect and aura count]]. PoB paths are relative to `%APPDATA%\Path of Building Community`.

**Evidence (re-checked 2026-10-26).**
- Cluster notable Purposeful Harbinger (node 51870, `TreeData/3_29/tree.lua:85942`) reads "Auras from your Skills have 8% increased Effect on you for each Herald affecting you, up to a maximum of 40%".
- `Data/ModCache.lua:14324`: `c["Auras from your Skills have 8% increased Effect on you for each Herald affecting you, up to a maximum of 40%"]={nil,"Auras from your Skills have 8% increased Effect on you for each Herald affecting you, up to a maximum of 40% "}`: no mod, the whole line is the leftover, so it shows red.
- `Modules/ModParser.lua:4044-4049` has two patterns for the same effect (`SkillAuraEffectOnSelf` INC with Multiplier Herald, `globalLimit`), both ending in `up to (%d+)%%`. "up to a maximum of 40%" does not fit them. Headless `modLib.parseMod` also returned nil (batch 4 probe).
- The Herald multiplier it would scale by exists (`Modules/CalcPerform.lua:2169-2170`, +1 per distinct herald), so the fix on PoB's side would only be the pattern.

**Effect of the gap.**
- Up to +40% increased aura effect on you (+8% per Herald) is missing from the build's aura numbers.
- The effect scales only the self copy ("on you"), so it does nothing for an aura supported by Generosity (see [[Aura effect and aura count]]).
- Rule: until PoB parses it, add the effect by hand (per Herald, capped at 40%) or do not credit it; never show it as "wasted".

UNVERIFIED: which cluster jewel size and slot carries the notable (only the notable-to-id map `Data/ClusterJewels.lua:602-880` was read).
