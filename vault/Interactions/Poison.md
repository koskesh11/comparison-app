---
type: interaction
status: draft
pob_refs: [PoisonChanceOnHit, PoisonChanceOnCrit, ChaosPoisonChance, PoisonStacks, TotalPoisonDPS, PoisonDPS, PoisonDuration, PoisonStackLimit, AdditionalPoisonStacks, AdditionalPoisonChance, CannotMultiplePoison, PhysicalCanPoison, FireCanPoison, ColdCanPoison, LightningCanPoison, conditionEnemyPoisoned, multiplierPoisonOnEnemy, conditionNonPoisonedOnly]
source: "poewiki Poison rev 1700788 (2026-08-15), Ailment rev 1673310, Version 3.27.0 rev 1674443, Version 3.28.0 rev 1648325 (fetched 2026-10-25); PoB 2.67.2 CalcOffence.lua / Data.lua / ModParser.lua / ConfigOptions.lua; PoB Data/Uniques, TreeData/3_29/tree.lua, Data/Skills/sup_dex.lua; wiki cargo mod_stats"
last_confirmed_patch: "3.29.x"
---

Poison is a stacking chaos damage-over-time ailment: each poisoning hit adds one stack worth 30% of the hit's flat physical and chaos damage per second for 2 s, with no stack limit. Hits poison only with a chance to poison (crits do not poison on their own). Its strength is the number of stacks, which is hit rate x chance x 2 s, so it is the ailment that rewards fast hits and extra poisons per hit, and the one that weak single hits cannot feed. PoB computes the expected stacks and the DPS itself; the enemy-Poisoned condition and "per Poison on enemy" payoffs are config only. Related: [[Ignite]], [[Bleed]], [[Damage type can ailment]], [[Chance on hit uptime]] (do not apply it to the poison DPS, only to payoffs), [[Fight length]].

Pipeline: [[Damage calculation#Ailments from hits]] and [[Damage calculation#Damage over time]] - poison starts from the unmitigated flat physical plus chaos damage, scales with the DoT multiplier pool and is reduced only by chaos resistance and chaos damage taken, so it works for a hit-rate build and does not for a slow single-hit build.

```interaction
id: poison
mechanic: "Hits with a chance to poison (physical and chaos damage by default) add a poison stack: chaos damage over time of 30% of the hit's flat physical + chaos damage per second for 2 s; stacks without limit; one stack per hit unless an effect adds more; crits do not poison on their own; mitigated only by chaos resist and chaos damage taken"
family: ailment
target: enemy
related: [ignite, bleed, damage-type-can-ailment, chance-on-hit-uptime, fight-length]
pipeline_step: ["Damage calculation#Ailments from hits", "Damage calculation#Damage over time"]
pipeline_why: "Poison is a separate base DPS from the hit's flat physical and chaos damage (after conversion, before hit modifiers); crit multiplier, penetration and double damage never reach it; stacks add, so hit rate x chance x duration sets the DPS, and the enemy's chaos resistance applies when the damage is dealt"
pob:
  measured: partial
  how: "poison chance on hit/crit CalcOffence.lua:4203-4227 (no crit bonus; chaos-only extra chance 4716-4717); skill needs canDeal.Chaos, i.e. not 'deals no chaos' (CalcOffence.lua:1934,4686); source damage = chaos + physical + fire/cold/lightning only with a *CanPoison flag CalcOffence.lua:4776-4819; additional poisons per hit 4720-4723; expected stacks = hit chance x chance x additional x dpsMultiplier x quantity x duration x hit rate, then the PoisonStackLimit cap CalcOffence.lua:4726-4745; duration 2 s (Data.lua:264-265) x duration mods / poison-faster mod CalcOffence.lua:4708-4712; base 30% (Data.lua:264) CalcOffence.lua:4843-4845; chaos resist and taken mods CalcOffence.lua:4848-4859; TotalPoisonDPS = single poison DPS x stacks CalcOffence.lua:4894-4897, in TotalDotDPS then CombinedDPS CalcOffence.lua:6252-6256, capped at Data.lua:261. NOT computed: enemy 'Poisoned' condition and 'per Poison on enemy' counts from stacks (config only), poison from a single slow hit within the first 2 s"
  config:
    - {var: conditionEnemyPoisoned, default: false, ref: "Modules/ConfigOptions.lua:1824 (needed by 'against Poisoned Enemies' payoffs, not by the poison DPS)", class: b}
    - {var: multiplierPoisonOnEnemy, default: 0, ref: "Modules/ConfigOptions.lua:1827 (count of poisons for 'per Poison' mods; also implies Poisoned; when 0 PoB assumes a non-Poisoned enemy for Low Tolerance style mods, CalcOffence.lua:4744-4745)", class: c}
    - {var: conditionNonPoisonedOnly, default: false, ref: "Modules/ConfigOptions.lua:1830 (limits to a single poison, e.g. Low Tolerance)", class: c}
    - {var: ailmentMode, default: "AVERAGE", ref: "Modules/ConfigOptions.lua:210", class: b}
  unparsed: []
model: null
providers:
  - {kind: unique, name: "Cospri's Will", slot: "Body Armour", role: applies, target: enemy, text: "Always Poison on Hit against Cursed Enemies (variants 1, 3); 60% chance against Cursed Enemies (variant 2); needs a curse on the enemy", source: "Data/Uniques/body.lua:290-293", pob: full, variant: "variants 1 and 3"}
  - {kind: unique, name: "Snakebite", slot: Gloves, role: applies, target: enemy, text: "Attacks have 60% chance to Poison while at maximum Frenzy Charges (variants 2, 3); +5% to Damage over Time Multiplier for Poison per Frenzy Charge (variant 3); attacks only", source: "Data/Uniques/gloves.lua:1106-1108", pob: full, variant: "variants 2 and 3"}
  - {kind: unique, name: "Betrayal's Sting", slot: Ring, role: scales, target: enemy, text: "(25-40)% chance to inflict an additional Poison on the same Target when you inflict Poison", source: "Data/Uniques/ring.lua:1654; Modules/CalcOffence.lua:4720-4723 (AdditionalPoisonChance, capped at +1)", pob: full}
  - {kind: unique, name: "Fleshrender", slot: Sword, role: scales, target: enemy, text: "Inflict (2-3) additional Poisons on the same Target; Cannot Poison Enemies with at least 12 Poisons on them", source: "Data/Uniques/sword.lua:104-105; Modules/CalcOffence.lua:4720-4745 (PoisonStackLimit)", pob: full}
  - {kind: unique, name: "The Consuming Dark", slot: Dagger, role: applies, target: enemy, text: "Your Chaos Damage has 60% chance to Poison Enemies (variant 3); variants 1-2 'Your Chaos Damage Poisons Enemies'", source: "Data/Uniques/dagger.lua:96-98; Modules/CalcOffence.lua:4716-4717 (ChaosPoisonChance)", pob: full, variant: "variant 3"}
  - {kind: unique, name: "Volkuur's Guidance", slot: Gloves, role: enables, target: enemy, text: "Your Fire / Cold / Lightning Damage can Poison (by variant); 20% chance to Poison on Hit with that element's skills; 50% less Poison Duration", source: "Data/Uniques/gloves.lua:867-873; Modules/CalcOffence.lua:4793-4811", pob: full}
  - {kind: unique, name: "Festering Resentment", slot: Dagger, role: enables, target: enemy, text: "Triggered Spells Poison on Hit; All Damage with Triggered Spells can Poison (spells poison only through this kind of line)", source: "Data/Uniques/dagger.lua:349-351", pob: full}
  - {kind: support, name: "Chance to Poison Support", slot: any, role: applies, target: enemy, text: "40% chance to Poison on Hit; supports any skill that hits (Damage or Attack)", source: "Data/Skills/sup_dex.lua:2766-2781", pob: full}
  - {kind: support, name: "Lethal Dose Support", slot: any, role: scales, target: enemy, text: "+2 additional Poisons applied vs non-poisoned enemies (only while the enemy has no poison); more Poison damage (the NonPoisonedOnly condition is set by PoB when the computed stacks are below the extra count, CalcOffence.lua:4744-4745)", source: "Data/Skills/sup_dex.lua:2586-2612; Modules/CalcOffence.lua:4744-4745", pob: full}
  - {kind: notable, name: "Septic Spells", slot: tree, role: applies, target: enemy, text: "20% chance to Poison on Hit with Spell Damage (the only tree source of spell poison; small 'Chance to Poison with Spells' nodes give 10-15%)", source: "TreeData/3_29/tree.lua:87513 (node 38399), 74028 (node 5018), 74084", pob: full}
  - {kind: ascendancy, name: "Infused Toxins (Assassin)", slot: tree, role: enables, target: enemy, text: "All Damage from Hits can Poison (added 3.27.0, behind Toxic Delivery)", source: "TreeData/3_29/tree.lua:83519 (node 21192); Modules/ModParser.lua:3917-3921; wiki Version 3.27.0 rev 1674443", pob: full}
  - {kind: ascendancy, name: "Toxic Delivery (Assassin)", slot: tree, role: scales, target: enemy, text: "Poison you inflict with Critical Strikes deals 20% more Damage (3.27.0, was 25%); Recover 0.5% of Life per Poison affecting Enemies you Kill", source: "TreeData/3_29/tree.lua:83350,83352 (node 19598); wiki Version 3.27.0 rev 1674443", pob: partial}
makes_redundant: []
conflicts:
  - {with: "Elemental Overload + Perfect Agony (keystones)", effect: "wiki: the combination prevents damaging ailments from hits entirely", source: "wiki Poison rev 1700788; PoB Modules/ModParser.lua:2237"}
  - {with: "Fleshrender / Viper Strike of the Mamba", effect: "Fleshrender stops poisoning at 12 poisons; Viper Strike of the Mamba 'Cannot inflict multiple Poisons in the same Hit' (3.28.0) blocks additional-poison stats on that skill", source: "Data/Uniques/sword.lua:104; Modules/ModParser.lua:3985; wiki Version 3.28.0 rev 1648325"}
conditions:
  - {text: "wiki quote: \"Poison is a stacking debuff. Each application or 'stack' of poison deals chaos damage over time until its duration expires. There is no limit to the number of poison stacks a target can have. A single 'hit' can apply a maximum of one poison stack, therefore having more than 100% chance to poison grants no additional benefit.\" (exceptions: extra-poison effects such as Lethal Dose, Betrayal's Sting, Fleshrender)", source: "wiki Poison rev 1700788; PoB Modules/CalcOffence.lua:4720-4723"}
  - {text: "wiki quote: \"The base damage per second dealt by a single poison is based on 30% of the combined flat physical and chaos damage of the hit.\" (3.15.0: up from 20%, 50% more); base duration 2 s (Viper Strike 4 s)", source: "wiki Poison rev 1700788, Version 3.15.0; PoB Modules/Data.lua:264-265"}
  - {text: "critical strikes with physical or chaos damage have no inherent chance to poison (unlike ignite, freeze, shock); crit poison gets the +50% DoT multiplier", source: "wiki Poison rev 1700788; PoB Modules/CalcSetup.lua:604"}
  - {text: "weapon 'chance to Poison' modifiers are local to the weapon; cargo: base_chance_to_poison_on_hit_% (global, Modifier:ChanceToPoisonUnique~~1) versus local_chance_to_poison_on_hit_%_during_flask_effect (flask, local); 'Your X damage can Poison' lines have no local_ prefix", source: "wiki Poison rev 1700788 (Dual Wielding); wiki cargo mod_stats 2026-10-25"}
  - {text: "the wiki 'Removal, immunity' list is about poison on YOU (Viper's Scales, Living Blade, corrupted 'Cannot be Poisoned', Chaos Inoculation); no enemy poison immunity or boss rule is documented on the page", source: "wiki Poison rev 1700788"}
uptime:
  Mapping:
    value: pob
    config: {conditionEnemyPoisoned: "model: tick only when the poison is up >= 0.99 of the time (see chance-on-hit-uptime); multiplierPoisonOnEnemy: use PoB's PoisonStacks output as the count for per-Poison payoffs"}
    reasoning: "PoB expects poison from chance, hit rate and 2 s duration (CalcOffence.lua:4727-4731); fast skills (Worb 6.45 volleys/s, CoC 17.85 uses/s per the uptime notes) fill the stacks within 2 s; packs that die in under 2 s get no ramp, see [[Fight length]]"
    source: "Modules/CalcOffence.lua:4726-4745,6252-6256; vault Interactions/Chance on hit uptime, Fight length"
  Pinnacle Boss:
    value: pob
    config: {conditionEnemyPoisoned: "model as above", multiplierPoisonOnEnemy: "PoB PoisonStacks output; boss chaos resist applies through PoisonEffMult"}
    reasoning: "one target collects every hit, so stacks = chance x hit rate on that target x 2 s; the stacks are not capped except by PoisonStackLimit (Fleshrender 12); boss chaos resistance and damage taken reduce each stack (PoisonEffMult)"
    source: "Modules/CalcOffence.lua:4848-4859,4894-4897"
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Poison (rev 1700788, 2026-08-15)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Ailment (rev 1673310, 2026-07-11)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Version_3.27.0 (rev 1674443): Infused Toxins, Toxic Delivery; Version_3.28.0 (rev 1648325): Viper Strike of the Mamba, Low Tolerance", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcOffence.lua:1934,4203-4227,4686-4745,4776-4859,4894-4897,6252-6256; Modules/Data.lua:261,264-265; Modules/CalcSetup.lua:604; Modules/ConfigOptions.lua:210,1824,1827,1830; Modules/ModParser.lua:2237,3917-3921,3985 (PoB 2.67.2)", kind: pob, patch: "3.29"}
not_verified:
  - "CONFLICT inside the wiki Poison page: it says only physical and chaos damage poison by default, but also 'the hit must deal at least one point of chaos damage, otherwise ... incapable of being poisoned'. PoB lets a physical-only hit poison (canDeal.Chaos only means 'not deals-no-chaos', CalcOffence.lua:4686). Not tested in game"
  - "whether more than one 'additional poison' source stacks in game as PoB sums them (AdditionalPoisonChance capped at +1, AdditionalPoisonStacks added)"
  - "the scope (local vs global) of every unique's 'chance to Poison' line was not checked per item; the wiki says weapon chance-to-poison modifiers are local"
  - "enemy chaos resistance for bosses in PoB's poison effect multiplier versus the wiki statement that only the defender's chaos damage taken mitigates it"
  - "Septic Spells and the small 'Chance to Poison with Spells' nodes were read from the tree text only; spell poison is not otherwise sourced in the 3.29 data checked"
open_questions: []
```
