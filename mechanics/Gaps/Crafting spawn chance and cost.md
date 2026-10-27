---
type: gap
status: draft
source: "task 027 batch 4e A3 (vault/Interactions/Crafting methods and obtainability.md); PoB 2.67.2 Classes/Item.lua, Data/ModMaster.lua, Data/Essence.lua; engine/gen_spawn_chance.py:21, 67-79; poewiki Essence rev 1700895, Crafting Bench rev 1700860, Fossil rev 1702302, Recombinator rev 1701130"
last_confirmed_patch: "3.29.x"
---

# Crafting spawn chance and cost (gap, prose only, no mod pattern)

PoB counts every finished mod line on an item the same way. Classes/Item.lua keeps a crafted/custom/fractured flag per line but does not weigh it. PoB's craft UI lists essences (Data/Essence.lua) and bench rows (Data/ModMaster.lua) but shows no spawn chance, cost or unlock. A grep of Modules/ and Classes/ for 'weightKey' finds only per-mod weight data, no probability code.

- The generator's rare_chance (weight / pool total) covers natural mods only. Essence and bench mods are removed by the callers (gen_validate.py:355, gen_gear_pool.py:265, tools/gen_rare_chances.py:117). Fossils, Harvest, Recombinator, Eldritch, influence exalts and Awakener's Orb are not modelled.
- Example from the note: Warlock Boots with FireResist4 pretended as an essence mod gives 1 in 69,737 today and 1 in 59,880 with the essence mod group removed from the draw pool (x1.16).
- Open numbers are not on the wiki pages read: Harvest "more common" factor, bench reroll selection rules (3.29.0), Eldritch Exalted Orb draw weights, Recombinator predictable success formula. Fossil stacking is marked disputed by the wiki (Fossil rev 1702302).
- The pool has no item-level filter (gen_spawn_chance.py:67-79), so the essence tier caps (35/45/60/75) are not applied.

Details, providers and seed findings: see [[Crafting methods and obtainability]]. This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap has no mod pattern.
