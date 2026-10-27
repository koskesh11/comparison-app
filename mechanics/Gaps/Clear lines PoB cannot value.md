---
type: gap
status: draft
source: "PoB 2.67.2 Data/ModCache.lua (lines quoted), Classes/PassiveTree.lua:862, headless node check of tree nodes 42068, 7069, 61627 (task 027 batch 4d, B3); wiki Chain rev 1596628, Fork rev 1702252"
last_confirmed_patch: "3.29.x"
---

Chain, fork and chain-range lines that PoB parses with leftover text. PoB drops any passive line whose parse has leftover text (Classes/PassiveTree.lua:862: `if mod.list and not mod.extra`), so the audit would show the node as less useful than it is, or show it as wasted. Headless check (in memory): Follow-Through 42068 and Split Shot 7069 add 0 mods, Ricochet 61627 keeps only "Skills Chain +1 times". Used by [[Clear - chain, pierce, fork and area]].

- Follow-Through 42068: ModCache.lua:18719 = mod ChainRemaining PerStat with leftover '   , up to a maximum of 100% '; second line form ModCache.lua:23175 = {nil, 'each remaining Chain, up to a maximum of 100% '}.
- Split Shot 7069: ModCache.lua:18763 = ProjectileCount BASE 50 with leftover ' for an additional  when Forking ' (a wrong stat plus leftover, dropped).
- Ricochet 61627 second line: ModCache.lua:18758 = ChainCountMax BASE 30 with leftover ' to be able to when colliding with terrain '.
- Chaining range: ModCache.lua:5259 and 8196 = {{}, ' Chaining range '} (15% and 30% increased).
- Projectile Fork angle: ModCache.lua:10274 (50% increased) and 10408 (50% reduced) = ProjectileCount INC with leftover ' Fork angle '.
- Greater Fork Support: stat chance_to_fork_extra_projectile_% (Data/Skills/sup_dex.lua:2127) has no entry in Data/SkillStatMap.lua.

Rule: value these nodes by their counted lines only and list the dropped line as "check yourself"; a flat PoB result is not zero value. Also see [[Cluster jewel notables PoB cannot parse]] (same Follow-Through line as a cluster notable).

```gap
# PoB leaves these chain / fork / range lines unparsed or half-parsed. The audit shows them as "can't measure, check yourself", never as wasted.
patterns:
  - { match: "each remaining Chain",                  why: "Follow-Through: damage per remaining chain; the line has leftover text and PoB drops it" }
  - { match: "when Forking",                          why: "Split Shot / Greater Fork: chance for an additional projectile when forking; leftover text, dropped" }
  - { match: "when colliding with terrain",           why: "Ricochet: chance to chain from terrain; leftover text, dropped" }
  - { match: "Chaining range",                        why: "chain distance is not modelled" }
  - { match: "Fork angle",                            why: "fork angle is not modelled; PoB maps the line to ProjectileCount INC with leftover text and drops it" }
```

**Evidence per pattern (PoB source lines, kept out of the player text; moved 2026-10-26, task 027 merge).**
- "each remaining Chain": ModCache.lua:18719, 23175
- "when Forking": ModCache.lua:18763
- "when colliding with terrain": ModCache.lua:18758
- "Chaining range": ModCache.lua:5259, 8196: empty mod list
- "Fork angle": ModCache.lua:10274, 10408
