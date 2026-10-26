---
type: interaction
status: draft
pob_refs: [GrantedAscendancyNode, grantedPassives, ForbiddenFlame, ForbiddenFlesh, CooldownRecovery, TriggerRateCap, SkillTriggerRate]
source: "PoB 2.67.2 ModParser.lua:5540, CalcSetup.lua:1273 / 1401-1417, Data/Uniques/Special/Generated.lua:549-595, ItemsTab.lua:39-42 / 1728-1771, ModCache.lua:13819-13820; poewiki Forbidden Flame rev 1675689, Forbidden Flesh rev 1675688, Like Clockwork rev 1619150; headless EK probes (task 027 batch 4c)"
last_confirmed_patch: "3.29.x"
---

Forbidden Flame (Crimson Jewel, Searing Exarch) and Forbidden Flesh (Cobalt Jewel, Eater of Worlds) are corrupted uniques, limited to 1 each. Each carries "Requires Class <class>" and "Allocates <ascendancy notable> if you have the matching modifier on <the other jewel>". Wear both with the same class and the same notable and you get that notable without spending points or being in that ascendancy (wiki: any ascendancy of the class; a notable you already have is not doubled).
In the EK seed the pair grants Saboteur's Like Clockwork (50% increased Cooldown Recovery Rate): CooldownRecovery 3 -> 53 lifts the CoC trigger cap from 6.06 to 10.10 per second; FullDPS 15,136,639 -> 7,607,891 without it (-49.7%). The pair is one unit: either jewel alone does nothing. Generator: place both or neither; the allocation lives in env.allocNodes, not in the build's saved node list, so a tree reader will not see it.

Pipeline: [[Damage calculation#Hit rate]] - the granted node is a normal allocated passive; for the EK seed its cooldown recovery moves the CoC trigger-rate cap (hit rate of the triggered spell)

```interaction
id: forbidden-jewels
mechanic: "Forbidden Flame + Forbidden Flesh (both Requires Class X, same notable named on both, each Limited to 1): allocate that ascendancy notable of class X for free; PoB grants it to env.allocNodes when both are equipped and the class matches the build's base class"
family: buff
pipeline_step: ["Damage calculation#Hit rate"]
pipeline_why: "the granted passive is an ordinary allocated node; Like Clockwork's 50% cooldown recovery raises the 0.15 s CoC cooldown breakpoint (trigger rate cap), which is the hit-rate step of the triggered Ethereal Knives"
target: self
related: [coc-trigger, timeless-jewels, cluster-jewels, radius-jewel]
pob:
  measured: full
  how: "ModParser.lua:5540 turns 'Allocates N if you have the matching modifier on Forbidden Flame/Flesh' into GrantedAscendancyNode {name, side} (ModCache.lua:13819-13820 holds the Like Clockwork forms: name='like clockwork', side='flame'/'flesh'); CalcSetup.lua:1273 stores item.classRestriction in itemModDB.conditions['ForbiddenFlame'/'ForbiddenFlesh']; CalcSetup.lua:1401-1417 pairs two GrantedAscendancyNode entries with the same name and opposite sides, looks the node up in tree.ascendancyMap (PassiveTree.lua:588, lower-case name) and adds it to env.allocNodes + env.grantedPassives only if BOTH conditions equal env.spec.curClassName. ItemsTab.lua:39-42, 1728-1771 only auto-adds the counterpart jewel in the UI. Measured 2026-10-26 on CoC EK Assa.xml (jewels 9 Flame socket 12613, 11 Flesh socket 2311, class Shadow, ascendancy Assassin): base FullDPS 15,136,639.02, TotalDPS 7,728,444.68, CombinedDPS 15,084,434.17, Life 1, EnergyShield 5189, Mana 1201, ManaUnreserved 107, TotalEHP 145,258.59, Speed 8.9297, TriggerRateCap 10.1010, CooldownRecovery INC 53, grantedPassives[51462] true. Flame removed (socket emptied in memory): FullDPS 7,607,890.67, TotalDPS 3,868,082.70, CombinedDPS 7,549,751.77, Life/ES/Mana/ManaUnreserved/TotalEHP unchanged, Speed 4.4693, TriggerRateCap 6.0606, CooldownRecovery 3, granted false, condition ForbiddenFlame nil. Flesh given Requires Class Witch in memory: identical to Flame removed (granted false, condition ForbiddenFlesh 'Witch'), so PoB checks the class on both jewels. Both removed: same numbers as Flame removed. No Saboteur node is in build.spec.allocNodes in any state (the grant exists only in the calc env)"
  config: []
  unparsed: []
model: null
providers:
  - {kind: unique, name: "Forbidden Flame", slot: jewel, role: enables, target: self, text: "Crimson Jewel, corrupted, Limited to 1, 'Requires Class Shadow', 'Allocates Like Clockwork if you have the matching modifier on Forbidden Flesh'", source: "Builds 3.29/Ninja Builds/CoC EK Assa.xml item 9 (lines 341-352); PoB Generated.lua:549-595; ModCache.lua:13819", pob: full}
  - {kind: unique, name: "Forbidden Flesh", slot: jewel, role: enables, target: self, text: "Cobalt Jewel, corrupted, Limited to 1, 'Requires Class Shadow', 'Allocates Like Clockwork if you have the matching modifier on Forbidden Flame'", source: "Builds 3.29/Ninja Builds/CoC EK Assa.xml item 11 (lines 380-391); PoB Generated.lua:549-595; ModCache.lua:13820", pob: full}
  - {kind: ascendancy, name: "Like Clockwork (Saboteur notable 51462, granted)", slot: tree, role: scales, target: self, text: "50% increased Cooldown Recovery Rate; Nearby Enemies have 10% reduced Cooldown Recovery Rate (wiki: 3.28.0 raised 40 -> 50%, introduced 3.21.0)", source: "PoB TreeData/3_29/tree.lua:84689-84698; ModCache.lua:10157, 18376; poewiki Like Clockwork rev 1619150", pob: partial}
  - {kind: jewel, name: "Grim Iridescence (rare Hypnotic Eye in Darkness Enthroned, belt abyssal socket 2)", slot: belt, role: scales, target: self, text: "2% increased Cooldown Recovery Rate, raised to 3 by the belt's 97% increased Effect of Socketed Abyss Jewels; it is the 3% that carries 50 + 3 = 53 over the 52% CoC breakpoint", source: "CoC EK Assa.xml items 24, 25; ModParser.lua:847; headless probe (CDR 53 -> 50, cap 10.1010 -> 7.5758 without it)", pob: full}
makes_redundant: []
conflicts:
  - {with: "a notable of the class that is already allocated", effect: "no extra effect; the pair cannot double up a notable (wiki). PoB sets env.allocNodes[node] once, so the same holds", source: "poewiki Forbidden Flame rev 1675689 (Mechanics); CalcSetup.lua:1410-1411"}
  - {with: "a second Forbidden Flame or Flesh", effect: "Limited to 1 per title: a second copy is disabled (jewelLimitWarning) unless the 'Ignore Jewel Limits' config is ticked", source: "CalcSetup.lua:862-871; ConfigOptions.lua:249"}
conditions:
  - {text: "both jewels worn, each with the SAME notable name and opposite side; one jewel alone grants nothing (probe: Flame removed -> granted false)", source: "CalcSetup.lua:1401-1417; headless probe 2026-10-26"}
  - {text: "'Requires Class' must equal the build's base class (Shadow for an Assassin), not the ascendancy; PoB drops the grant if either jewel names another class (probe: Flesh set to Witch -> granted false)", source: "CalcSetup.lua:1273, 1409; headless probe 2026-10-26"}
  - {text: "the granted notable may belong to any ascendancy of the class (Assassin may get Saboteur's Like Clockwork); Scion gets Ascendant notables; Reliquarian and Luminary notables cannot roll; Tawhoa, Forest's Strength was removed in 3.25.0 (existing jewels still work)", source: "poewiki Forbidden Flame rev 1675689 (Mechanics, Version history 3.25.0)"}
  - {text: "each jewel sits in an allocated jewel socket (CalcSetup skips items in unallocated sockets)", source: "CalcSetup.lua:848-849"}
  - {text: "pairing by notable name is read from the code only (matchedName table); a pair with two different notables was not probed", source: "CalcSetup.lua:1402-1417"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "worn equipment: the granted passive and its 50% cooldown recovery are permanent", source: "CalcSetup.lua:1401-1417"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "same; the Like Clockwork enemy line (10% reduced cooldown recovery for nearby enemies) is parsed as an EnemyModifier (ModCache.lua:18376); whether PoB's boss uses it is unverified", source: "ModCache.lua:18376"}
seeds: [EK]
sources:
  - {ref: "PoB Modules/CalcSetup.lua:1273, 1401-1417; Modules/ModParser.lua:5540; Data/Uniques/Special/Generated.lua:549-595", kind: pob, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Forbidden_Flame (rev 1675689; version history 3.17.0 introduced, 3.18.0 hidden notable variants, 3.19.0 notable renames, 3.25.0 Tawhoa removed)", kind: wiki, patch: "3.25.0"}
  - {ref: "https://www.poewiki.net/wiki/Forbidden_Flesh (rev 1675688)", kind: wiki, patch: "3.25.0"}
  - {ref: "https://www.poewiki.net/wiki/Like_Clockwork (rev 1619150; 3.28.0 40 -> 50%)", kind: wiki, patch: "3.28.0"}
not_verified:
  - "pairing of two different notables (code-read only, not probed)"
  - "the seven hidden-ascendancy notable variants (Nine Lives, Harness the Void, Fury of Nature, Fatal Flourish, Indomitable Resolve, Searing Purity, Unleashed Potential; Uber Exarch / Uber Eater drops, wiki 3.18.0): whether Generated.lua rolls them is not checked"
  - "whether PoB uses the enemy half of Like Clockwork (10% reduced cooldown recovery on nearby enemies); no calc reader was searched"
  - "trade price and availability of a matching pair for a given notable (not a PoB question)"
  - "whether the EK pasted jewels (no variant lines in the build XML) round-trip through the item DB variants: Generated.lua writes 'Requires Class' + 'Allocates' per variant, the XML holds the resolved lines"
open_questions:
  - "Is a class-matched pair with a notable other than Like Clockwork wanted for the generator (which Shadow notables are worth a pair for a non-CoC seed)? Only the user can say what to prefer"
```
