---
type: interaction
status: draft
pob_refs: [IgniteChanceOnHit, IgniteChanceOnCrit, IgniteStacks, IgniteCanStack, IgniteStackPotential, IgniteRollAverage, IgniteDuration, IgniteDurationBase, IgniteBurnFaster, IgniteDPS, TotalIgniteDPS, overrideIgniteStackPotential, conditionEnemyIgnited, ailmentMode, DotDpsCap]
source: "poewiki Ignite rev 1598418 (2025-12-18), Ailment rev 1673310, Version 3.29.0 rev 1699085 (fetched 2026-10-25); PoB 2.67.2 CalcOffence.lua / Data.lua / ModParser.lua / ConfigOptions.lua; PoB Data/Uniques, TreeData/3_29/tree.lua, Data/Skills/sup_int.lua; vault Gaps/Ailments from hits source damage"
last_confirmed_patch: "3.29.x"
---

Ignite is the fire damage-over-time ailment: 90% of the hit's flat fire damage per second for 4 s, strongest ignite only (no stacking) unless a source adds more. It is the opposite of a hit modifier: crit multiplier, penetration and double damage never reach it, the DoT multiplier does. PoB already turns ignite chance into expected stacks and adds the DPS to TotalDotDPS / CombinedDPS, so no uptime model is needed for the DPS itself; only the enemy-is-Ignited condition for payoff mods is a config tick. Related: [[Shock]], [[Damage type can ailment]], [[Elemental ailment count]], [[Scorch, Brittle and Sap]], [[Fight length]], gap [[Ailments from hits source damage]].

Measured on the Fireball seed (scrapped Fireball build, Pinnacle boss, Fireball L20 with effective quality 30, PoB 2.67.2; tasks/reports/027-evidence/b1c-pob-fireball.md): TotalDPS 251,999.68 (hit only), IgniteDPS 33,468.58, FullDPS 285,468.27. The ignite comes from the gem alone (25% on hit, `base_chance_to_ignite_%`, Data/Skills/act_int.lua:5815-5817; poewiki Fireball rev 1698987: 25% at all gem levels since 3.16.0) and 100% on crit; with CritChance 21.15% that is 40.86% per hit (CalcOffence.lua:5014). The output key IgniteChance 89.35 is not the per-hit chance: it weights how likely the strongest ignite present is a crit ignite, because IgniteStackPotential is 8.22 (CalcOffence.lua:5183, calcAilmentDamage 4333-4339). FullDPS keeps only the best ignite across groups (Calcs.lua:265-268), and no config box is needed for the ignite itself.

Pipeline: [[Damage calculation#Ailments from hits]] and [[Damage calculation#Damage over time]] - ignite starts from the unmitigated flat fire damage after conversion and scales with the DoT multiplier pool, so it works for a build with big flat damage and DoT multiplier and does not for one that only has hit-only scaling (crit multiplier, penetration, double damage).

```interaction
id: ignite
mechanic: "Hits with fire damage (or damage allowed to ignite) and a chance to ignite (crits 100%) inflict a fire damage-over-time debuff: 90% of the hit's flat damage per second for 4 s; only the strongest ignite deals damage unless a stacking source exists; calculated from flat damage, so hit-only modifiers (crit multiplier, penetration, double damage) do not apply"
family: ailment
target: enemy
related: [shock, damage-type-can-ailment, elemental-ailment-count, scorch-brittle-sap, poison, bleed, chance-on-hit-uptime, fight-length]
pipeline_step: ["Damage calculation#Ailments from hits", "Damage calculation#Damage over time"]
pipeline_why: "Ignite is a separate base-DPS calculation from the hit's flat damage (after conversion, before hit modifiers); the enemy's fire resist and damage taken apply when it deals damage, and its scaling pool is DoT multiplier, burning/ignite/fire/DoT increased and more, not the crit multiplier"
pob:
  measured: partial
  how: "ignite chance on hit/crit (crit 100% unless CritsDontAlwaysIgnite) CalcOffence.lua:4240-4262; expected stacks = hit chance x ignite chance x dpsMultiplier x duration x hit rate CalcOffence.lua:5030-5040 (cooldown skills use duration / max(cooldown, time)); duration = 4 s x duration mods / burn-rate mod CalcOffence.lua:5022-5029; maxStacks 1 unless IgniteCanStack CalcOffence.lua:5017-5020; roll average 50% unless stack potential > 1, then shifted toward the top CalcOffence.lua:5073-5081; base 90% of source CalcOffence.lua:5184-5186 with Data.lua:266-267; DPS added to TotalDotDPS then CombinedDPS CalcOffence.lua:6252-6256, capped at Data.lua:261. NOT computed: the enemy 'Ignited' CONDITION for payoff mods (config only), real in-game roll of the hit, the ignite lost when the target dies before 4 s"
  config:
    - {var: conditionEnemyIgnited, default: false, ref: "Modules/ConfigOptions.lua:1878 (implies Burning; needed by every 'against Ignited Enemies' payoff, not by the ignite DPS)", class: b}
    - {var: overrideIgniteStackPotential, default: 0, ref: "Modules/ConfigOptions.lua:1881 (only visible with conditionEnemyIgnited; replaces the computed stack potential)", class: c}
    - {var: ailmentMode, default: "AVERAGE", ref: "Modules/ConfigOptions.lua:210 (Average or Crits Only for the ailment base damage)", class: b}
    - {var: multiplierIgniteAppliedRecently, default: 0, ref: "Modules/ConfigOptions.lua:1348 (count for 'per Ignite applied recently' mods)", class: c}
  unparsed:
    - "Shaper of Flames 'Enemies Ignited by you have 40% of Physical Damage they deal converted to Fire': parsed as an enemy modifier only while the Ignited condition is set (ModParser.lua:3531; Data/ModCache.lua:15305), so it needs conditionEnemyIgnited"
model: null
providers:
  - {kind: unique, name: "Rashkaldor's Patience", slot: Amulet, role: applies, target: enemy, text: "Always Freeze, Shock and Ignite (Current); drawback 20% reduced Duration of Elemental Ailments on Enemies", source: "Data/Uniques/amulet.lua:939,943", pob: full, variant: "variant 2 (Current)"}
  - {kind: unique, name: "Emberwake", slot: Ring, role: scales, target: enemy, text: "You can inflict an additional Ignite on each Enemy; 10% chance to Ignite; Ignited Enemies Burn (65-50)% slower; 35% less Burning Damage (Current). Wiki: with two Emberwakes the stacking debuff stacks 2 times, 3 damaging ignites per enemy", source: "Data/Uniques/ring.lua:504-512; Modules/ModParser.lua:3697 (IgniteCanStack + IgniteStacks BASE 1); wiki Ignite rev 1598418", pob: full, variant: "variants 3-5"}
  - {kind: keystone, name: "Voracious Flame", slot: tree, role: scales, target: enemy, text: "You can inflict an additional Ignite on each Enemy; Base Ignite Duration is 1 second; 25% less Damage with Ignite; Cannot deal non-Fire Damage (new in 3.29.0, north of the Witch start)", source: "TreeData/3_29/tree.lua:47294 (node 63903); Data/ModCache.lua:14351,22783; wiki Version 3.29.0 rev 1699085", pob: full}
  - {kind: ascendancy, name: "Shaper of Flames (Elementalist)", slot: tree, role: enables, target: enemy, text: "Hits always Ignite; All Damage can Ignite; Enemies Ignited by you have 40% of Physical Damage they deal converted to Fire (3.26.0 replaced the 'more Damage with Ignites' line)", source: "TreeData/3_29/tree.lua:50130-50138 (node 53123); Modules/ModParser.lua:2796,2810,3531; wiki Version 3.26.0", pob: partial}
  - {kind: support, name: "Combustion Support", slot: any, role: applies, target: enemy, text: "25% chance to Ignite; more fire damage; Ignites apply -10% Fire Resistance", source: "Data/Skills/sup_int.lua:916-942", pob: full, payoff_of: [conditionEnemyIgnited]}
  - {kind: support, name: "Immolate Support", slot: any, role: scales, target: enemy, text: "Supported hits deal added fire damage against Burning enemies (Ignited implies Burning in PoB). Only skills that hit gain; the hit that first ignites gets no bonus unless the enemy already burns", source: "PoB Data/Skills/sup_int.lua:3385-3402 (stats global_minimum/maximum_added_fire_damage_vs_burning_enemies), Data/SkillStatMap.lua:830-835 (FireMin/FireMax BASE, enemy condition Burning), Modules/CalcSetup.lua:73 (Ignited sets Burning), Modules/ConfigOptions.lua:1875-1880 (conditionEnemyBurning, conditionEnemyIgnited); wiki Immolate Support rev 1681953 (3.29)", pob: config, payoff_of: [conditionEnemyIgnited, conditionEnemyBurning]}
  - {kind: support, name: "Elemental Proliferation Support", slot: any, role: applies, target: enemy, text: "20% chance to Freeze, Shock and Ignite", source: "Data/Skills/sup_int.lua:2151,2164", pob: full}
  - {kind: unique, name: "Replica Volkuur's Guidance", slot: Gloves, role: enables, target: enemy, text: "Your Chaos Damage can Ignite; Chaos Skills have 20% chance to Ignite; 50% less Ignite Duration", source: "Data/Uniques/gloves.lua:883-885", pob: full}
  - {kind: unique, name: "Stormfire", slot: Ring, role: enables, target: enemy, text: "Your Lightning Damage can Ignite; Adds (1-3) to (125-145) Lightning Damage to Hits against Ignited Enemies (3.29.0 value)", source: "Data/Uniques/ring.lua:1240-1242; wiki Version 3.29.0 rev 1699085", pob: full, payoff_of: [conditionEnemyIgnited]}
  - {kind: unique, name: "Zerphi's Heart", slot: Amulet, role: enables, target: enemy, text: "Chaos Damage can Ignite, Chill and Shock", source: "Data/Uniques/amulet.lua:1025; Modules/ModParser.lua:3674", pob: full, variant: "variant 2"}
  - {kind: foulborn, name: "Foulborn The Three Dragons", slot: Helmet, role: enables, target: enemy, text: "Your Chaos Damage can Ignite (global flag base_chaos_damage_can_ignite)", variant: "mutation REPLACES the original line 'Your Cold Damage can Ignite but not Freeze or Chill' (ColdIgnitesUniqueHelmetDexInt4_ -> MutatedUniqueHelmetDexInt4ChaosDamageCanIgnite)", source: "Data/ModFoulbornMap.jsonc:347 -> Data/ModFoulborn.lua:122; original Data/Uniques/helmet.lua:1670; wiki cargo stat base_chaos_damage_can_ignite (no local_ prefix = global); vault Gaps/Foulborn The Three Dragons", pob: partial}
  - {kind: ascendancy, name: "Oath of Summer (Raider)", slot: tree, role: blocks, target: enemy, text: "Hits that would Ignite instead Scorch; You can inflict an additional Scorch on each Enemy (3.25.0): turns your ignite into [[Scorch, Brittle and Sap]]", source: "TreeData/3_29/tree.lua:84777-84779 (node 33645); Modules/ModParser.lua:3036 (IgniteCanScorch + CannotIgnite); wiki Version 3.25.0", pob: full}
  - {kind: keystone, name: "Secrets of Suffering", slot: tree, role: blocks, target: enemy, text: "Cannot Ignite, Chill, Freeze or Shock; Critical Strikes inflict Scorch, Brittle and Sapped", source: "TreeData/3_29/tree.lua:85638 (node 57280)", pob: full}
makes_redundant: []
conflicts:
  - {with: "Elemental Focus (support)", effect: "supported skill cannot inflict ailments (no ignite)", source: "Data/SkillStatMap.lua:1059-1066"}
  - {with: "Elemental Overload + Perfect Agony (keystones)", effect: "wiki: the combination prevents damaging ailments from hits entirely (ailments never count as crit, and Perfect Agony makes them use the crit multiplier)", source: "wiki Ignite rev 1598418; PoB Modules/ModParser.lua:2237 (AilmentsAreNeverFromCrit)"}
  - {with: "Voracious Flame vs Emberwake", effect: "PoB adds both IgniteStacks BASE +1 (3 ignites total); the wiki Ignite page (rev 1598418) predates 3.29.0 and does not describe the keystone", source: "Modules/ModParser.lua:3697; wiki Version 3.29.0"}
conditions:
  - {text: "needs a chance to ignite and damage that can ignite (default fire only); crits have an inherent 100% chance but still need ignite-capable damage; 0 DPS ignites are discarded; damage over time such as Righteous Fire does not hit and cannot ignite", source: "wiki Ignite rev 1598418; PoB Modules/CalcOffence.lua:4240-4262"}
  - {text: "wiki quote: \"Ignite's base burning damage is 90% of the flat damage of the hit per second.\" (3.17.0 lowered it from 125%, 3.16.0 raised it from 50%); 360% over the 4 s base duration; ailments inflicted by enemies deal 50% per second (wiki marks that part {{confirm}})", source: "wiki Ignite rev 1598418, footnote Version 3.0.0 / 3.3.0 / 3.16.0 / 3.17.0; PoB Modules/Data.lua:266-267"}
  - {text: "wiki quote: \"By default, ignite does not stack. Multiple ignite debuffs can exist on a target, each with their own independent duration, but only the ignite with the highest damage per second will deal damage at any given moment.\"", source: "wiki Ignite rev 1598418"}
  - {text: "damaging ailments from critical strikes gain +50% DoT multiplier (additive with other DoT multiplier)", source: "wiki Ignite rev 1598418; PoB Modules/CalcSetup.lua:604"}
  - {text: "ignite is not affected by skill effect duration; 'deal Damage x% faster' stats raise DPS and lower duration by the inverse, same damage per ignite", source: "wiki Ignite rev 1598418; PoB Modules/CalcOffence.lua:5022-5029"}
  - {text: "since 3.21.1 elemental ailments other than Freeze are no longer discarded if their duration is below 300 ms", source: "wiki Ignite rev 1598418, Version 3.21.1"}
uptime:
  Mapping:
    value: pob
    config: {conditionEnemyIgnited: "model: box state by the uptime rule (user rule 2026-10-25: u >= 80% ticked, no notice; 50-80% ticked + user informed with u; < 50% unticked + warning with u) (see chance-on-hit-uptime); the ignite DPS itself needs no tick"}
    reasoning: "PoB expects ignite from chance, hit rate and 4 s duration (CalcOffence.lua:5030-5040) and shows IgniteDPS in TotalDotDPS; packs that die before 4 s waste part of it (see [[Fight length]]); payoff mods that need the Ignited condition follow [[Chance on hit uptime]]"
    source: "Modules/CalcOffence.lua:5030-5040,6252-6256; vault Interactions/Chance on hit uptime, Fight length"
  Pinnacle Boss:
    value: pob
    config: {conditionEnemyIgnited: "model: u from the boss hit rate, chance and 4 s duration; crit builds have 100% on crit", ailmentMode: "AVERAGE unless the build ignites only with crits"}
    reasoning: "one target, so the ignite is up as long as one ignite lands per 4 s; the roll average (50%, or toward the top when stack potential > 1) is PoB's, the real strongest-ignite roll is not verified; fight length decides how much of the 4 s ramp counts"
    source: "Modules/CalcOffence.lua:5073-5081; vault Interactions/Fight length"
seeds: [Fireball]
sources:
  - {ref: "https://www.poewiki.net/wiki/Ignite (rev 1598418, 2025-12-18)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Ailment (rev 1673310, 2026-07-11)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Version_3.29.0 (rev 1699085): Voracious Flame; Version_3.26.0 (rev 1674253): Shaper of Flames; Version_3.25.0 (rev 1698361): Oath of Summer", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcOffence.lua:4240-4262,5017-5081,5184-5186,5221-5246,6252-6256; Modules/Data.lua:261,266-267; Modules/CalcSetup.lua:604; Modules/ConfigOptions.lua:210,1348,1878,1881; Modules/ModParser.lua:2237,2796,2810,3036,3531,3697; Data/ModCache.lua:14351,22783 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "vault/Gaps/Ailments from hits source damage.md and vault/Interactions/Damage calculation.md", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b1c-pob-fireball.md (Fireball seed ignite measure; PoB Modules/CalcOffence.lua:4333-4339,5014,5183; Modules/Calcs.lua:265-268; Data/Skills/act_int.lua:5815-5817)", kind: pob, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Fireball (rev 1698987)", kind: wiki, patch: "3.29"}
not_verified:
  - "the in-game roll of the strongest ignite: PoB takes 50% of the damage range (or a top-shifted value when stack potential > 1); the wiki only says the strongest ignite deals damage"
  - "whether the 3.29.0 keystone Voracious Flame stacks with Emberwake in game (PoB adds +1 each; no wiki text yet, the Ignite page predates 3.29.0)"
  - "enemy fire resistance and damage-taken mods applied to the ignite in PoB (CalcOffence.lua DoT multiplier) versus the wiki statement that mitigation is by the defender's fire damage taken only"
  - "ignite lost when the target dies before 4 s: PoB reports DPS, not damage realised; fight length not applied here"
  - "scope (local vs global) of every unique's 'chance to Ignite' line was not checked per item; only Foulborn The Three Dragons was checked (global, wiki cargo)"
open_questions: []
```
