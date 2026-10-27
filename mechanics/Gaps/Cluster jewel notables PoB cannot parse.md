---
type: gap
status: draft
source: "PoB 2.67.2 Data/ModCache.lua (lines quoted), headless p_pool.py over the 3.29 cluster notable pool (task 027 batch 4c, tree-ascendancy-analyst)"
last_confirmed_patch: "3.29.x"
---

# Cluster jewel notables: lines PoB drops or half-parses (gap, prose only, no mod pattern)

Of 308 cluster nodes in the 3.29 pool, 55 carry a flagged line (36 with an unparsed line, 19 with a partial parse): the chance-to-charge, chance-to-ailment, totem, mine, brand, minion and spread lines. The damage and speed lines of the same notables ARE counted, so the notable is never worth zero in PoB, only less than in game. Examples with the exact ModCache form:

- Follow-Through (Medium Projectile Damage): ModCache.lua:23175 = {nil, 'each remaining Chain, up to a maximum of 100% '}; the chain bonus is not counted.
- Shrieking Bolts (Medium Projectile Damage): '10% chance to Taunt Enemies on Projectile Hit' parses as ProjectileCount BASE 10 with a leftover (ModCache.lua:3649); PoB drops lines with a leftover, nothing is added.
- Blast-Freeze (Large Cold, Medium Non-damaging Ailments): freeze spread, ModCache.lua:15623 = {nil, ...}.
- Mage Hunter (ModCache.lua:6361), Stormrider (:3712): chance to gain a Power Charge not counted; Thaumophage (:3629) Hinder, Disorienting Display (:3615) Blind, Cremator / Smoking Remains (:17019, :3673), Hex Breaker / Enduring Focus (:19386, :7320).

Rule: when the generator picks a cluster notable, value it by the counted lines only and list the unparsed line as "check yourself" (see [[Mods PoB can't value]]); do not treat a flat PoB result as zero value. Full list: run the p_pool.py pool dump (task 027 batch 4c scratchpad). Linked from: [[Cluster jewels]].

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap has no mod pattern.
