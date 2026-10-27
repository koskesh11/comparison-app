---
type: gap
status: draft
source: "task 027 batch 4e A2 (tasks/reports/027-evidence/partial/b4e/A2-map-modifiers.md); PoB 2.67.2 grep of Modules/ and Classes/, 2026-10-26; poewiki Reflect rev 1702966 (3.29.0 Thorns)"
last_confirmed_patch: "3.29.x"
---

# Map thorns damage taken (gap, prose only, no mod pattern)

PoB cannot calculate the damage a player takes from Thorns (Punishing / Mirrored map mods since 3.29.0, Rare monsters). See [[Map modifiers]] for the thorns tick model and per-seed numbers.

- `grep -rin thorns Modules Classes` returns nothing (only Data/Skills/spectre.lua:2428 "MonsterLightningThorns", a spectre skill).
- Reflected damage the player takes has a multiplier only: CalcDefence.lua:1950-1956 builds `<Type>TakenReflect` from ReflectedDamageTaken mods, and CalcDefence.lua:1925/1958 forces `AnyTakenReflect = false` ("this needs a rework as well"), so the Reflect taken section (CalcSections.lua:2094) never shows.
- No config option feeds a reflect amount (ConfigOptions.lua only has Misty Reflection 546-548 and Molten Shell 769-773, which are the player's own reflects).
- Punishing / Mirrored: Data/ModMap.lua:189-202 hold the pre-3.29 percentages, apply is empty, and neither is in the Prefix list (405-422).

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap has no mod pattern.
