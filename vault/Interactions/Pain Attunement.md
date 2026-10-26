---
type: interaction
status: draft
pob_refs: [Condition:LowLife, conditionLowLife, LowLifePercentage, LifeUnreservedPercent, LifeReserved, Condition:HavePainAttunement, CombinedDPS, FullDPS, enemyIsBoss]
source: "poewiki Pain Attunement rev 1605415, Low life rev 1596639, Chaos Inoculation rev 1634768, Ignite rev 1598418, Version 3.14.0 rev 1649134 (fetched 2026-10-26); PoB 2.67.2 TreeData 3_29 tree.lua, Data/ModCache.lua, Modules/CalcPerform.lua, ModDB.lua, ConfigOptions.lua, Data/Uniques; headless runs on EK, Worb, FR and the Fireball seed (scratchpad b3c/D_run_*.json)"
last_confirmed_patch: "3.29.x"
---

Pain Attunement (PA) is a keystone: 30% more Spell Damage while on Low Life. Low Life means 50% or less of maximum Life (3.14.0, before that below 35%); PoB sets it only from reserved Life, the config tick 'Are you always on Low Life?' or Coward's Legacy, so allocating PA changes nothing in PoB until the build reserves at least 50% of its Life. When up it is a clean x1.30 on hit damage (measured +24.9% to +30.4% on four seeds, the spread is explained below). The price is the Life pool: reserving 50% Life cut TotalEHP by 28% to 33% on Worb and the Fireball seed. EK and FR run Chaos Inoculation (Life 1), where the wiki says Low Life only exists with Coward's Legacy; see [[Chaos Inoculation]] for that conflict.

Pipeline: [[Damage calculation#More and less]] - PA is a MORE modifier on Damage with flag Spell and a Condition tag, so it joins the product of all other more-modifiers of the skill (each layer's product is rounded to the nearest percent, ModList.lua:126-148 and ModDB.lua:171-197: Worb's player layer 1.12 x 1.30 = 1.456 becomes 1.46, exactly +30.36% on the hit; EK's layer 1.28 x 1.21 = 1.55 becomes 1.28 x 1.21 x 1.30 = 2.01, +29.7%; so the delta is not exactly 30.0%). The gate (Low Life) is a state of the character, not a hit property: see [[Receiving damage#Life]].

Measured (headless, in memory, nothing saved; PA added as the custom line 'Pain Attunement' = keystone only, path cost not included; Low Life forced with config conditionLowLife = true; enemy level from env.enemyLevel: 85 at None, 84 at Pinnacle; Worb with Aspect of the Brine King left out, Winter Orb gem count 5 as in the file):

| Seed | metric | scenario | base | PA, no Low Life | PA + Low Life | delta |
|---|---|---|---|---|---|---|
| EK | CombinedDPS | Pinnacle | 15,084,434 | 15,084,434 | 19,639,503 | +30.20% |
| EK | CombinedDPS | None | 14,370,752 | 14,370,752 | 18,692,871 | +30.08% |
| Worb | CombinedDPS | Pinnacle | 1,343,498 | 1,343,498 | 1,751,340 | +30.36% |
| Worb | CombinedDPS | None | 1,934,211 | 1,934,211 | 2,521,376 | +30.36% |
| FR | FullDPS | Pinnacle | 57,001,026 | 57,001,026 | 73,910,217 | +29.66% |
| FR | FullDPS | None | 67,300,152 | 67,300,152 | 87,265,080 | +29.67% |
| Fireball (not a validator seed) | CombinedDPS | Pinnacle | 285,468 | 285,468 | 361,063 | +26.48% |
| Fireball (not a validator seed) | CombinedDPS | None | 390,510 | 390,510 | 487,576 | +24.86% |

- FR: CombinedDPS of the main skill (Cyclone, an attack) is unchanged; the +29.7% is in FullDPS, in the Cast On Critical Strike spell Forbidden Rite (56.83M -> 73.74M, +29.75%). EK: Ethereal Knives +29.68%, Full Impale DPS +30.74%, Cyclone 0%.
- Fireball is +26.5% instead of +30% because its CombinedDPS adds ignite: hits +30.0% (TotalDPS 251,999.7 -> 327,594.9), ignite DPS 33,468.6 -> 33,468.6 (+0.000%). PA is 'Spell Damage', a hit-specific modifier; the wiki Ignite page says such modifiers never directly affect ignite DPS (rev 1598418) and PoB agrees. Same for bleed and poison. Builds whose damage is mostly ailments get far less than +30%.
- Low Life threshold, tested on Worb (Life 4306, reserve line 'Reserves N% of Life'): 49% reserved -> unreserved 51% -> Low Life false, +0.00%; 50% reserved -> unreserved 50% -> Low Life true, +30.36%. Matches the wiki and Data.lua:240 (LowPoolThreshold 0.5, CalcPerform.lua:570).
- Price of the reservation, same line 'Reserves 50% of Life' (a stand-in for Arrogance-type reservation, not a real source): Worb TotalEHP 76,837 -> 52,014 (Pinnacle, -32.3%) and 81,163 -> 54,695 (None, -32.6%), physical max hit 16,310 -> 11,310; Fireball TotalEHP 12,065 -> 8,692 (Pinnacle, -28.0%), 7,806 -> 5,627 (None, -27.9%). The reservation alone moves DPS by 0.00%. Mana freed by the move from mana to life reservation (Arrogance) is not in these numbers.
- CI seeds (EK, FR): the custom line 'Reserves 1% of Life' gives Low Life true (Life 1, unreserved 0%) and the full +30.2% / +29.7%; PoB therefore accepts a reservation under CI. The wiki says the only way to Low Life with CI is Coward's Legacy and that a Life of 1 counts as full Life (Low life rev 1596639); whether a Life reservation can exist under CI in the game is not documented (see [[Chaos Inoculation]]).

```interaction
id: pain-attunement
mechanic: "Keystone: 30% more Spell Damage when on Low Life (3.29). Low Life = life at 50% or less of maximum (since 3.14.0; previously below 35%); the condition is checked when damage is calculated, not snapshotted (wiki). PoB: Damage MORE 30 with flag Spell and tag Condition LowLife; Low Life is set only from reserved Life (unreserved/max <= 50%), the config tick, or items that grant it; hits only, ailment damage (ignite, bleed, poison) is not scaled"
family: buff
target: self
related: [chaos-inoculation, receiving-damage, ignite, damage-calculation]
pipeline_step: ["Damage calculation#More and less"]
pipeline_why: "PA is parsed to Damage MORE 30 with ModFlag.Spell and a Condition tag (Data/ModCache.lua:8399), so while Condition:LowLife is set it multiplies the skill's more-product (ModList.lua:122-154 and ModDB.lua:164-198, each layer's product rounded to the nearest percent) before crit and enemy mitigation; it does not touch the hit's base, conversion or increased pool."
pob:
  measured: config
  how: "Keystone PA = ModCache.lua:18501 (Keystone LIST + Condition:HavePainAttunement), merged by modLib.mergeKeystones (CalcPerform.lua:1291-1292, ModTools.lua:249-255); effect = ModCache.lua:8399 (flags=2 Spell, MORE 30, tag Condition LowLife). Condition:LowLife is set at CalcPerform.lua:570-571 when (Life - reserved)/Life <= LowLifePercentage (default 0.5, Data.lua:240, CalcPerform.lua:77-78; a Low Life mastery line 'count as on Low Life while at 55% of maximum Life or below' = ModCache.lua:22838 changes it) and by the config tick (ConfigOptions.lua:177-178); Coward's Legacy flags it only while AffectedByVulnerability (ModParser.lua:4133). Measured: PA without Low Life = 0.00% on all seeds; PA + Low Life = +24.9% to +30.4% (table above). NOT modelled: current-life Low Life (a hit that takes you below 50% for a moment), the Petrified Blood gem (display-only statMap, Data/Skills/act_str.lua:8600-8602), uptime of a Low Life that is not permanent reservation."
  config:
    - {var: conditionLowLife, default: false, ref: "Modules/ConfigOptions.lua:177-178 (box shown only when the build uses a LowLife condition, Classes/ConfigTab.lua:401-410; tooltip ConfigOptions.lua:61-65 says reservation of the unreserved percentage makes it automatic)", class: b}
    - {var: enemyIsBoss, default: "Pinnacle (enemy level 84; None = 85)", ref: "headless env.enemyLevel; Modules/ConfigOptions.lua:2086", class: b}
  unparsed:
    - "Petrified Blood gem 'Your life cannot be raised above low life other than by flasks': stat cannot_recover_above_low_life_except_flasks is Display Only in PoB (Data/Skills/act_str.lua:8600-8602), no Condition:LowLife is set; the old wiki Pain Attunement page lists Petrified Blood as a Low Life source (rev 1605415)"
model: null
providers:
  - {kind: keystone, name: "Pain Attunement", slot: tree, role: applies, target: self, text: "30% more Spell Damage when on Low Life (standalone keystone between Witch and Shadow, distance 7 from both)", source: "TreeData/3_29/tree.lua:62454, 62458; Data/ModCache.lua:8399, 18501; wiki Pain Attunement rev 1605415", pob: config}
  - {kind: unique, name: "Crown of Thorns", slot: Helmet, role: applies, target: self, text: "Pain Attunement (keystone line on a Vine Circlet with +25 Physical Damage taken from Attack Hits)", source: "Data/Uniques/helmet.lua:449-460; wiki cargo items", pob: config}
  - {kind: unique, name: "Martyr's Crown", slot: Helmet, role: applies, target: self, text: "Pain Attunement; PoB data marks it 'No longer obtainable'", source: "Data/Uniques/helmet.lua:462-472", pob: config}
  - {kind: unique, name: "Skin of the Lords", slot: Body Armour, role: applies, target: self, text: "Random keystone list includes Pain Attunement (wiki cargo items query: stat text lists the keystones)", source: "wiki cargo items query 2026-10-26 (stat text lists the random keystones)", pob: partial}
  - {kind: tattoo, name: "Pain Attunement tattoo (Hinekora keystone tattoo)", slot: tree, role: applies, target: self, text: "keystone tattoo with the same 30% more Spell Damage line", source: "Data/TattooPassives.lua:1827-1845", pob: partial}
  - {kind: mod, name: "Crucible weapon tree node", slot: weapon, role: applies, target: self, text: "WeaponTreeKeystonePainAttunement: Pain Attunement spawns on wand, staff, sceptre, dagger, claw weapon trees", source: "Data/Crucible.lua:1342", pob: partial}
  - {kind: support, name: "Arrogance Support", slot: any, role: enables, target: self, text: "supported reservation skill reserves Life instead of Mana (stat base_skill_reserve_life_instead_of_mana); 50% of Life reserved = Low Life", source: "Data/Skills/sup_str.lua:300-318; Data/SkillStatMap.lua:175; Modules/CalcPerform.lua:561-571; wiki Low life rev 1596639", pob: partial}
  - {kind: unique, name: "Prism Guardian", slot: Shield, role: enables, target: self, text: "Socketed Gems Cost and Reserve Life instead of Mana, 30% increased Reservation Efficiency", source: "Data/Uniques/shield.lua:998-1012; Data/ModCache.lua:20779; wiki Low life rev 1596639", pob: partial}
  - {kind: unique, name: "Coward's Legacy", slot: Belt, role: enables, target: self, text: "You count as on Low Life while you are Cursed with Vulnerability: the only Low Life source under Chaos Inoculation (wiki)", source: "Data/Uniques/belt.lua:189-200; Modules/ModParser.lua:4133; Data/ModCache.lua:22840; wiki Low life rev 1596639", pob: partial}
  - {kind: mastery, name: "Life Mastery (55% line)", slot: tree, role: scales, target: self, text: "You count as on Low Life while at 55% of maximum Life or below: only 45% of Life needs to be reserved (added in 3.21.0)", source: "Data/ModCache.lua:22838; Modules/CalcPerform.lua:77-78; wiki Low life rev 1596639 (Version history 3.21.0)", pob: full}
  - {kind: gem, name: "Petrified Blood", slot: any, role: enables, target: self, text: "your life cannot be raised above low life other than by flasks (named by the wiki as a Low Life source); PoB does not set the condition", source: "wiki Pain Attunement rev 1605415; Data/Skills/act_str.lua:8582-8602", pob: none}
makes_redundant: []
conflicts:
  - {with: "Chaos Inoculation", effect: "Life 1 counts as full Life; Low Life exists only with Coward's Legacy (wiki); PoB lets a reservation or the config tick set Low Life under CI, which may be a phantom", source: "wiki Low life rev 1596639, Chaos Inoculation rev 1634768; Modules/CalcPerform.lua:82-86, 570-571; headless EK/FR 'Reserves 1% of Life' = Low Life true"}
  - {with: "a normal Life pool (EHP)", effect: "reserving 50% of Life to reach Low Life cut TotalEHP 28-33% on Worb and the Fireball seed; the trade is DPS x1.30 on hits against EHP x0.68-0.72", source: "headless Worb/Fireball 'Reserves 50% of Life' (scratchpad b3c/D_cost_*.json)"}
  - {with: "ailment-based damage (ignite, bleed, poison)", effect: "PA is a Spell Damage modifier and does not scale ailment DPS: Fireball ignite stayed 33,468.6 while hits rose 30%", source: "wiki Ignite rev 1598418; headless Fireball D_dot_Fireball.json"}
conditions:
  - {text: "Low Life = life at 50% or less of maximum; the threshold was below 35% until 3.14.0 ('a single 50% reservation will now put you into a Low state')", source: "wiki Low life rev 1596639; wiki Version 3.14.0 rev 1649134 (patch 3.14.0, 2021-04-16); Modules/Data.lua:240"}
  - {text: "the condition is checked when damage is calculated: on hit, or when a damage-over-time effect is created; a spell that pushes you into Low Life by its own cost (Lifetap, Sacrifice) benefits at once; no snapshot", source: "wiki Pain Attunement rev 1605415"}
  - {text: "PoB raises Low Life only when the unreserved share of Life is at or below the threshold (49% reserved = false, 50% = true, measured on Worb)", source: "Modules/CalcPerform.lua:570-571; headless Worb D_run_Worb.json PA+reserve49%/50%"}
  - {text: "bonus is 30% since 0.9.9 (25% before)", source: "wiki Pain Attunement rev 1605415 (Version history)"}
uptime:
  Mapping:       {value: always, config: {conditionLowLife: "true, or at least 50% of Life reserved (45% with the Life mastery line)"}, reasoning: "Low Life from a permanent Life reservation is a static state, so PA is up for the whole map; without reservation or config PA is 0 in PoB. Current-life Low Life (damage taken) is not modelled and not sourced", source: "Modules/CalcPerform.lua:570-571; headless: PA without Low Life = 0.00% on four seeds"}
  Pinnacle Boss: {value: always, config: {conditionLowLife: "same", enemyIsBoss: "Pinnacle (level 84)"}, reasoning: "the reservation state does not change with the boss; enemy level only moves the base DPS (EK +30.20% at Pinnacle vs +30.08% at None); the EHP cost is paid in every fight, the benefit is hit damage only", source: "headless EK/Worb/FR/Fireball, Pinnacle and None rows"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Pain_Attunement (rev 1605415)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Low_life (rev 1596639)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Version_3.14.0 (rev 1649134): 'The Low threshold for Life, Mana and Energy Shield is now 50% or below (previously below 35%)'", kind: patch_notes, patch: "3.14.0"}
  - {ref: "https://www.poewiki.net/wiki/Ignite (rev 1598418)", kind: wiki, patch: "3.29"}
  - {ref: "wiki cargo passive_skills: 'stat text' = '30% more Spell Damage when on Low Life', is keystone = 1 (global passive stat, not an item-local mod)", kind: wiki, patch: "3.29"}
  - {ref: "PoB TreeData/3_29/tree.lua:62454-62458; Data/ModCache.lua:8399, 18501, 22838-22840; Modules/CalcPerform.lua:77-78, 561-571, 1291-1292; Modules/ModTools.lua:249-255; Classes/ModDB.lua:164-198; Classes/ModList.lua:122-154; Modules/ConfigOptions.lua:61-65, 177-178; Classes/ConfigTab.lua:401-410; Modules/Data.lua:240", kind: pob, patch: "3.29"}
not_verified:
  - "whether the game counts current life (damage taken) as Low Life for PA beyond reservation; the wiki says 'life is at 50% or lower' without separating reserved from current, and PoB models reservation and the config tick only"
  - "whether a Life reservation can exist under Chaos Inoculation in the game (PoB: yes, Life 1 reserved 1 = unreserved 0%); the wiki says Coward's Legacy is the only way"
  - "whether PA scales damage over time that is not an ailment (Vortex-type spell DoT): the wiki says it does at creation; the Fireball ignite is not affected in PoB and the wiki Ignite page agrees, but no seed has a spell DoT to test"
  - "Prism Guardian, Arrogance and the tattoo/Crucible providers were not run headless; their reservation or keystone effect is read from the data files only"
  - "which unique item carries the item-exclusive mod ids KeystonePainAttunementUnique__1 and DivergentPainAttunement (Data/ModItemExclusive.lua:5177, 8659); Divergent probably a Foulborn-type variant, not traced"
  - "Skin of the Lords keystone pool in the 3.29 data (wiki cargo lists Pain Attunement, PoB uniques file not read for it)"
open_questions:
  - "For a CI seed, should the generator treat Pain Attunement as available only with Coward's Legacy (wiki) or also with any Life reservation (PoB)?"
```
