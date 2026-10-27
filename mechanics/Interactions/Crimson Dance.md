---
type: interaction
status: draft
pob_refs: [BleedStacksMax, Condition:HaveCrimsonDance, Condition:NoExtraBleedDamageToMovingEnemy, Condition:CannotAggravate, Condition:Moving, conditionEnemyMoving, multiplierBleedsOnEnemy, BleedStackPotential, BleedDPS, BleedChance]
source: "poewiki Crimson Dance rev 1625594 (fetched 2026-10-26; introduced 3.0.0, no later change listed); PoB 2.67.2 CalcOffence.lua, CalcSetup.lua, CalcPerform.lua, ModParser.lua, ConfigOptions.lua, Data/ModCache.lua, Data/Uniques, TreeData/3_29/tree.lua; headless measurements on EK, Worb, FR and the Fireball file, tasks 027 batch 3c (pob-coverage-auditor-E.md)"
last_confirmed_patch: "3.29.x"
---

Crimson Dance (keystone) trades the bleed's strength for stacks. Tree text (TreeData/3_29/tree.lua:43772, node 17818): "You can inflict Bleeding on an Enemy up to 8 times / Your Bleeding does not deal extra Damage while the Enemy is moving and cannot be Aggravated / 50% less Damage with Bleeding". Wiki: every stack is 35% of the flat physical attack damage per second, 280% at 8 stacks; plain [[Bleed]] is 70% per second, one stack, and x3 while the enemy moves. So it beats a stationary single bleed from 2 stacks and a moving single bleed from 6 stacks, and only an ATTACK build with a high hit rate ever reaches 8. Related: [[Damage over time multiplier]], [[Ignite]], [[Poison]].

Pipeline: [[Damage calculation#Damage over time]] - PoB applies the 50% less as a MORE on bleed damage and lifts the stack cap from 1 to 8; the weighted-average stack count (hit rate x chance x duration) feeds BleedDPS at the DoT step, and the 'moving' triple is a +200% MORE removed by the keystone (CalcSetup.lua:639).

Measured headless, in memory only (E_run.py; enemy level from env.enemyLevel: 85 at None, 84 at Pinnacle). No seed allocates Crimson Dance; keystone force-allocated alone ('keystone only, path cost not included'):
- EK: main skill TotalDPS unchanged (7,728,444.7 Pinnacle, 7,331,707.3 None), but FullDPS 15,136,639.0 -> 15,140,082.8 (+3,443.8, +0.023%) and 14,420,419.0 -> 14,423,862.8: EK is NOT zero, its Cyclone (the Cast on Critical Strike attack, BleedChance 26, Best Bleed DPS 1,566.2) gets 8 stacks: Best Bleed DPS 1,566.2 -> 5,010.0 (x3.20).
- Worb, FR and the Fireball file: 0 changed output keys at both enemy levels (no bleed chance on any skill).
- What-if only, not a seed: FR with a custom line '100% chance to cause Bleeding on Hit': BleedDPS 470.9 (enemy stationary, default) -> 1,413.9 when the config box 'Is the enemy Moving?' is ticked; with Crimson Dance 1,790.2 whether the box is ticked or not (x3.80 over the stationary bleed, +26.6% over the moving one); equal at None and Pinnacle. FR TotalDPS stays 166,643.3 (the Cyclone hit); CombinedDPS 166,643.3 -> 168,433.6.

```interaction
id: crimson-dance
mechanic: "Bleeding can stack up to 8 times on an enemy; each stack is 35% of the hit's flat physical damage per second (50% less than the normal 70%); the bleed deals no extra damage while the enemy moves (normally x3) and cannot be Aggravated; attack hits only"
family: ailment
target: enemy
related: [bleed, damage-over-time-multiplier, ignite, poison, enemy-ailment-threshold]
pipeline_step: ["Damage calculation#Damage over time", "Damage calculation#More and less"]
pipeline_why: "PoB overrides BleedStacksMax with 8 (CalcOffence.lua:4434), adds 50% less Damage for the Bleed keyword (a MORE, ModCache.lua:10319) and sets Condition:NoExtraBleedDamageToMovingEnemy so the base +200% MORE while the enemy moves (CalcSetup.lua:639) is switched off; the stack-weighted bleed DPS then enters the damage-over-time step."
pob:
  measured: partial
  how: "Keystone lines parse (Data/ModCache.lua:22782 BleedStacksMax OVERRIDE 8 + Condition:HaveCrimsonDance; 23000 Condition:NoExtraBleedDamageToMovingEnemy + Condition:CannotAggravate; 10319 Damage MORE -50 with Bleed keyword 4194304; the node name entry is 14823); ModParser.lua:2327-2334. Consumers: CalcOffence.lua:4434-4436 (maxStacks = Override BleedStacksMax), 4444-4458 stack potential (see the Bleed note), CalcSetup.lua:639 (+200% MORE Bleed damage while enemy has Condition:Moving unless NoExtraBleedDamageToMovingEnemy), CalcPerform.lua:1194 (minions get the +200% unconditionally on the Moving condition, no Crimson Dance exception), CalcSections.lua:980 (Max Bleed Stacks). Condition:CannotAggravate has NO consumer in Modules (grep), and every 'chance to Aggravate Bleeding' line is unparsed (Data/ModCache.lua:3601, 5136, 6290, 7227-7228 have empty mod lists), so aggravate is not modelled at all. Measured by force-allocating node 17818 alone (E_run.py) and by a what-if custom line on FR. NOT modelled: aggravate, enemy movement over time (a single tick box), the wiki 35% per stack beyond the two MORE mods."
  config:
    - {var: conditionEnemyMoving, default: false, ref: "Modules/ConfigOptions.lua:1797 (shown only if the build has BleedChance; sets Condition:Moving on the enemy; Crimson Dance makes it irrelevant)", class: b}
    - {var: multiplierBleedsOnEnemy, default: 0, ref: "Modules/ConfigOptions.lua:1657 (shown only with Condition:HaveCrimsonDance; sets the current stack count if not maximum, implies Bleeding)", class: c}
  unparsed:
    - "every 'chance to Aggravate Bleeding on targets you Hit with Attacks' line (Data/ModCache.lua:3601, 5136, 6290, 7227-7228): empty mod list"
model: null
providers:
  - {kind: keystone, name: "Crimson Dance", slot: tree, role: applies, target: enemy, text: "You can inflict Bleeding on an Enemy up to 8 times; Your Bleeding does not deal extra Damage while the Enemy is moving and cannot be Aggravated; 50% less Damage with Bleeding", source: "TreeData/3_29/tree.lua:43772 (node 17818); Data/ModCache.lua:14823", pob: full}
  - {kind: unique, name: "Sanguine Gambol", slot: Dagger, role: applies, target: enemy, text: "You have Crimson Dance if you have dealt a Critical Strike Recently; 50% chance to Cause Bleeding on Critical Strike", source: "Data/Uniques/dagger.lua:136-148; Data/ModCache.lua:22888 (Condition CritRecently)", pob: full}
  - {kind: unique, name: "Farrul's Pounce", slot: Gloves, role: applies, target: enemy, text: "You have Crimson Dance while you have Cat's Stealth; Attacks always inflict Bleeding while you have Cat's Stealth", source: "Data/Uniques/gloves.lua:535-545; Data/ModCache.lua:22889 (Condition AffectedByCat'sStealth)", pob: partial}
  - {kind: mod, name: "chance to Aggravate Bleeding (Bloodletting, Gladiator and other nodes)", slot: tree, role: blocks, target: enemy, text: "the keystone makes the bleed unable to be Aggravated; PoB does not parse Aggravate at all, so these lines show nothing with or without the keystone", source: "TreeData/3_29/tree.lua:43772-43776; Data/ModCache.lua:3601", pob: none}
  - {kind: mod, name: "chance to cause Bleeding with attacks (any source)", slot: any, role: enables, target: enemy, text: "no bleed chance, no stacks: EK gets +0.023% FullDPS from its Cyclone only; seeds without a bleed chance get 0", source: "Modules/CalcOffence.lua:4197-4222; E_run.py measurements", pob: full}
makes_redundant:
  - {provider: "Aggravate Bleeding sources", when: "Crimson Dance allocated", why: "Crimson Dance's bleed cannot be Aggravated (tree text); PoB has no model either way", source: "TreeData/3_29/tree.lua:43772-43776; Data/ModCache.lua:3601"}
  - {provider: "the config box 'Is the enemy Moving?'", when: "Crimson Dance allocated", why: "the keystone removes the moving bonus, so ticking the box changes nothing (measured on FR: 1,790.2 with and without)", source: "Modules/CalcSetup.lua:639; E_run.py what-if"}
conflicts:
  - {with: "plain bleed against a moving enemy", effect: "plain bleed is x3 while the target moves; the keystone's 8 x 50% = x4 at most, so it is only +26.6% over a moving single bleed in PoB (FR what-if) and x3.80 over a stationary one", source: "E_run.py FR what-if; Modules/CalcSetup.lua:639; wiki Crimson Dance rev 1625594"}
  - {with: "low hit rate or low bleed chance", effect: "stack count follows hit rate x chance x duration (BleedStackPotential); below 2 stacks the 50% less makes the keystone worse than no keystone against a stationary enemy", source: "Modules/CalcOffence.lua:4444-4458; tree text"}
  - {with: "spell and DoT builds", effect: "bleed needs attack hits; spells and totem-less DoT never bleed (wiki Bleed note)", source: "Modules/CalcOffence.lua:4197-4222"}
conditions:
  - {text: "wiki: Crimson Dance bleeding may deal damage alongside regular bleeding from a party member or minion; a single player can use both types only if the keystone is lost or gained periodically (Farrul's Pounce)", source: "wiki Crimson Dance rev 1625594"}
  - {text: "the +200% moving bonus applies to bleeds when the enemy has Condition:Moving; the keystone flag turns it off for the player's bleed only, minion bleed keeps it", source: "Modules/CalcSetup.lua:639; Modules/CalcPerform.lua:1194"}
uptime:
  Mapping:       {value: pob, config: {enemyIsBoss: "None / map monsters (enemy level 85 in the runs)", conditionEnemyMoving: "irrelevant with the keystone"}, reasoning: "permanent keystone; PoB's stack weighted average is the number; map monsters mostly move, which is exactly the case the keystone ignores", source: "Modules/CalcOffence.lua:4434-4458; E_run.py"}
  Pinnacle Boss: {value: pob, config: {enemyIsBoss: "Pinnacle (default; enemy level 84 in the runs)"}, reasoning: "permanent keystone; use PoB's BleedDPS; the share of the fight a boss stands still or moves is not sourced, which decides plain bleed versus the keystone", source: "Modules/CalcOffence.lua:4434-4458; Modules/ConfigOptions.lua:1797"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Crimson_Dance (rev 1625594)", kind: wiki, patch: "3.29"}
  - {ref: "PoB TreeData/3_29/tree.lua:43772; Data/ModCache.lua:3601,10319,14823,22782,22888-22889,23000; Modules/ModParser.lua:2327-2334; Modules/CalcOffence.lua:4197-4222,4434-4458; Modules/CalcSetup.lua:639; Modules/CalcPerform.lua:1194; Modules/ConfigOptions.lua:1657,1797; Modules/CalcSections.lua:980; Data/Uniques/dagger.lua:136-148, gloves.lua:535-545", kind: pob, patch: "3.29"}
  - {ref: "tasks 027 batch 3c: scratchpad b3c/E/E_run.py, bleedsrc.py, summary.txt (headless, nothing saved)", kind: discovery, patch: "3.29"}
not_verified:
  - "how long a pinnacle boss stands still or moves (decides plain bleed x3 versus Crimson Dance): no source"
  - "whether Aggravate Bleeding (Bloodletting, Gladiator, Jagged Technique) is worth more than Crimson Dance in the game: PoB has no aggravate model"
  - "the source of EK's Cyclone BleedChance 26 (skillModList Tabulate of BleedChance returned no rows; the value is in the output only)"
  - "whether minions of a Crimson Dance player bleed with the keystone (CalcPerform.lua:1194 gives minions the moving triple with no exception)"
  - "the wiki page does not mention 'cannot be Aggravated'; that part is the tree text only"
  - "Farrul's Pounce and Sanguine Gambol: how long 'crit recently' / Cat's Stealth is up (not measured)"
open_questions:
  - "Does the generator treat 'enemy moving' as always true on map packs and false on a stationary boss, or ask the user?"
```
