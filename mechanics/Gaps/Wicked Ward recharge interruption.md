---
type: gap
status: draft
source: "poewiki Wicked Ward rev 1597145 (as quoted in vault Interactions Energy shield recovery keystones); PoB 2.67.2 Data/ModCache.lua:15437, 9418, TreeData/3_29/tree.lua:61731, Data/TattooPassives.lua:4810 (task 027 batch 3)"
last_confirmed_patch: "3.29.x"
---

# Wicked Ward: PoB models only the downside (gap, prose only, no mod pattern)

**Lines.** The keystone (TreeData/3_29/tree.lua:61731) and its tattoo (Data/TattooPassives.lua:4810) carry two stats: "Energy Shield Recharge is not interrupted by Damage if Recharge began Recently" and "40% less Energy Shield Recharge Rate".

**PoB.** The second line parses (`EnergyShieldRecharge` MORE -40, Data/ModCache.lua:9418). The first does not: `c["Energy Shield Recharge is not interrupted by Damage if Recharge began Recently"]={nil,"..."}` (Data/ModCache.lua:15437, the combined tries at 15438-15439 are nil too). PoB has no output for "recharge interrupted by damage" at all (see [[Energy shield recovery keystones]]), so the keystone looks like a pure 40% recharge cut: Fireball seed ES recharge 604 -> 362 per second.

**Consequence.** A PoB-only search never picks Wicked Ward, and one that did would show it as a loss. Whether it is a gain depends on how often the build is hit while the ES recharges (the benefit window is 4 s after a recharge began, per the vault note); that is a fight-pattern question PoB cannot answer. Treat the benefit as unmeasured, not as zero.

**No item pattern.** No unique in Data/Uniques carries the line (grep 'not interrupted by Damage' over Data/Uniques, ModFoulbornMap.lua and ModItemExclusive.lua returns nothing; elsewhere it appears only in ModCache.lua, ModScalability.lua, StatDescriptions, TattooPassives.lua and the tree files), and tree lines never reach the audit's wasted-mod test (engine/audit.lua `equippedItems` walks item slots only), so a gap block would never fire.

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap has no item mod line to match.
