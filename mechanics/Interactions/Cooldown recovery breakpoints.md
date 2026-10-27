---
type: interaction
status: draft
pob_refs: [CooldownRecovery, TriggerRateCap, SkillTriggerRate, EffectiveSourceRate, FullDPS]
source: "PoB 2.67.2 CalcTriggers.lua:91-134, 563-590, 812-814; Data/Skills/sup_dex.lua:699-731, sup_int.lua:1280-1315; TreeData/3_29/tree.lua; Data/ModJewelAbyss.lua, ModExplicit.lua, ModVeiled.lua, Uniques; poewiki Delirious Bloodline rev 1592181, Bloodline ascendancy class rev 1700682; headless EK probes (task 027 batch 4d)"
last_confirmed_patch: "3.29.x"
---

Cooldown Recovery from every slot is summed into one percentage on the triggered spell, and that sum sets the tick-rounded cooldown of the Cast On Critical Strike trigger. The sum only pays in steps: 14, 52 and 128% (0.15 s cooldown in 33 ms ticks = 7.58, 10.10, 15.15 triggers per second; 6.06 below 14%). Missing a step by 1% costs the whole step; going past it buys nothing until the attack rate passes the next cap. Rules: [[CoC requires 100% crit and hit]], [[Trigger attack under the CoC cap]]; formula and breakpoints: [[CoC trigger]]; the cap formula itself: [[Trigger rate cap and cooldown]].
The cap reads the TRIGGERED spell's modifiers (Ethereal Knives), not the attack's (Cyclone): a Cooldown Recovery line that applies only to the attack, to Movement Skills, Traps, Warcries, Guard, Stance, Brand Recall or minions does not count (Movement Skills +30%: Cyclone sum 80, Ethereal Knives 50, cap unchanged).
The DPS cost of dropping below a step is PoB's SkillTriggerRate, a simulation of 1000 source attacks (CalcTriggers.lua:91-134, 814), not the TriggerRateCap ratio. EK: 53 -> 50 gives cap -25% (10.10 -> 7.58) but SkillTriggerRate -39.7% and FullDPS -39.5% (pure CDR row 9,158,813 vs 15,136,639), because the 8.92/s attack is faster than the lower cap and the 33 ms cooldown alignment wastes attacks. Emptying the Grim Iridescence socket (8,928,368) also removes +10 Dex/Int, flat physical to spells and +36 ES, which is a further -2.5%.

Pipeline: [[Damage calculation#Hit rate]] - the summed cooldown recovery sets the trigger cooldown, hence the maximum rate at which the triggered spell hits; a wasted trigger is a lost hit, it adds no damage per hit

```interaction
id: cooldown-recovery-breakpoint
mechanic: "Sum of increased Cooldown Recovery Rate on the triggered spell sets n = ceil(0.15 / (1+CDR) / 0.033) ticks; cap = 1 / (n x 0.033) = 6.06 / 7.58 / 10.10 / 15.15 per s at <14 / 14-51 / 52-127 / 128-354 percent; the real loss below a breakpoint is PoB's SkillTriggerRate simulation, larger than the cap ratio when the attack is faster than the cap"
family: trigger
pipeline_step: ["Damage calculation#Hit rate"]
pipeline_why: "cooldown recovery lowers the trigger cooldown, which raises how many triggered hits per second can land; it adds no damage per hit"
target: self
related: [coc-trigger, forbidden-jewels]
pob:
  measured: partial
  how: "Full for the sum and the rate: TriggerRateCap = 1 / tick-rounded cooldown with icdr = calcLib.mod(triggered spell skillModList, skillCfg, 'CooldownRecovery') (CalcTriggers.lua:563, 580-590, tick 0.033 Data.lua:237-238); SkillTriggerRate for CoC = calcMultiSpellRotationImpact over 1000 source attacks (CalcTriggers.lua:91-134, 814), not min(cap, source) (that branch, line 799, is for ignoresTickRate skills). Wrapping calcLib.mod showed every CooldownRecovery call feeding the cap uses skillName Ethereal Knives. Partial because the generator-side constraint (sum >= breakpoint across slots) is ours, and the simulation is not tested in game. Headless EK (in memory, no config tick): sum 53 -> cap 10.10, SkillTriggerRate 8.93, FullDPS 15,136,639; custom -3% (sum 50) -> 7.58, 5.39, 9,158,813; Forbidden pair out (sum 3) -> 6.06, 4.47, 7,607,891. Sweep 0/13/14/30/51/52/60/100/127/128/200 matches the bands. Tabulate CooldownRecovery INC: 3 @ Item:24 (Grim Iridescence), 50 @ Tree:51462 (granted passive), no BASE/MORE/OVERRIDE."
  config: []
  unparsed: []
model:
  proposed_kind: cdr_breakpoint_constraint
  inputs: {from_pob: [CooldownRecovery, TriggerRateCap, SkillTriggerRate, EffectiveSourceRate, FullDPS], from_scenario: []}
  params:
    tick_s: 0.033
    cooldown_s: 0.15
    breakpoints_pct: {rate_6_06: "below 13.64", rate_7_58: "13.64 to 51.51 (integer sums 14..51)", rate_10_10: "51.52 to 127.27 (integer sums 52..127)", rate_15_15: "127.28 to 354.54 (integer sums 128..354)", rate_30_30: "354.55 and up (not tested)"}
    ek_baseline: {cdr_sum: 53, breakpoint: 52, slack: 1, source_rate_per_s: 8.92, cap_per_s: 10.10, full_dps: 15136639}
    ek_removal_table:
      - {removed: "custom 3% reduced Cooldown Recovery line (CDR-only probe)", cdr: 50, trigger_rate_cap: 7.576, skill_trigger_rate: 5.388, full_dps: 9158813, also_removed: "nothing else; Grim's other mods stay"}
      - {removed: "Grim Iridescence socket emptied (Belt Abyssal Socket 2, item 24)", cdr: 50, trigger_rate_cap: 7.576, skill_trigger_rate: 5.388, full_dps: 8928368, also_removed: "+10 Dex and Int (Dex 181 -> 162, Int 362 -> 343), 10-12 flat physical to spells, +36 ES (ES 5189 -> 5006)"}
      - {removed: "Grim socket emptied, then a generic +2% Cooldown Recovery line added", cdr: 52, trigger_rate_cap: 10.101, skill_trigger_rate: 8.930, full_dps: 14754726, also_removed: "Grim's Dex/Int, flat physical, ES stay removed (-2.5% vs baseline)"}
      - {removed: "Forbidden Flame socket 12613 emptied", cdr: 3, trigger_rate_cap: 6.061, skill_trigger_rate: 4.469, full_dps: 7607891, also_removed: "the Like Clockwork grant (env.grantedPassives[51462] false); the jewel has no other mod"}
      - {removed: "Forbidden Flesh socket 2311 emptied", cdr: 3, trigger_rate_cap: 6.061, skill_trigger_rate: 4.469, full_dps: 7607891, also_removed: "the Like Clockwork grant (pair rule)"}
      - {removed: "both Forbidden sockets emptied", cdr: 3, trigger_rate_cap: 6.061, skill_trigger_rate: 4.469, full_dps: 7607891, also_removed: "the Like Clockwork grant"}
      - {removed: "both Forbidden sockets emptied, custom +50% as stand-in", cdr: 53, trigger_rate_cap: 10.101, skill_trigger_rate: 8.930, full_dps: 15136639, also_removed: "nothing; restores baseline"}
      - {removed: "Awakened CoC L5 swapped in for CoC L20 (adds +22 on the triggered spell)", cdr: 75, trigger_rate_cap: 10.101, skill_trigger_rate: 8.930, full_dps: 15647707, also_removed: "swap: spell damage -10% -> -7% less; this row ADDS 22, nothing removed"}
      - {removed: "Awakened CoC L5 + Forbidden Flame emptied", cdr: 25, trigger_rate_cap: 7.576, skill_trigger_rate: 5.388, full_dps: 9467190, also_removed: "the Like Clockwork grant"}
      - {removed: "Awakened CoC L5 + Forbidden Flame + Grim emptied", cdr: 22, trigger_rate_cap: 7.576, skill_trigger_rate: 5.388, full_dps: 9229036, also_removed: "the Like Clockwork grant and Grim (+10 Dex/Int, flat physical to spells, +36 ES)"}
      - {removed: "Cooldown Recovery support L3 as 7th gem (probe only)", cdr: 93, trigger_rate_cap: 10.101, skill_trigger_rate: 8.930, full_dps: 15136639, also_removed: "adds 40; EK ManaCost 18 -> 35; needs a 7th link (the group has 6 gems)"}
    sim_by_source_rate: "source 8.0/s: band 6.06 -> 4.00, band 7.58 -> 6.30; source 8.92/s: 4.47 / 5.39 / 8.93; source 11.0/s at the 10.10 band -> 8.30; a source at or under the cap of the band triggers at the source rate (7.0/s at the 7.58 band = 7.01)"
  formula: "cap = 1 / (ceil(0.15 / (1 + CDR/100) / 0.033) x 0.033). Safe side: attack rate x hit x crit <= cap of the band reached. Below the breakpoint the DPS loss is the SkillTriggerRate ratio of PoB's simulation, not cap_low / cap_high. Use PoB's SkillTriggerRate and FullDPS for the number; this model only says WHERE the steps are (sum >= 14, 52, 128)."
  calibration: "no norm found for in-game behaviour of a source faster than the cap; breakpoints reproduce PoB output at every integer sum tested"
providers:
  - {kind: ascendancy, name: "Like Clockwork (Saboteur 51462)", slot: tree, role: scales, target: self, text: "50% increased Cooldown Recovery Rate; Nearby Enemies have 10% reduced Cooldown Recovery Rate", source: "TreeData/3_29/tree.lua:84689-84698", pob: full}
  - {kind: unique, name: "Forbidden Flame + Forbidden Flesh (pair, Shadow)", slot: jewel, role: scales, target: self, text: "grants Like Clockwork; emptying either socket drops the 50% (probe: sum 53 -> 3)", source: "PoB CalcSetup.lua:1401-1416; headless EK removal rows", pob: partial, variant: "pair is user-pasted text, not in Data/Uniques"}
  - {kind: jewel, name: "Grim Iridescence (rare Hypnotic Eye abyss jewel, item 24)", slot: belt abyssal socket, role: scales, target: self, text: "2% increased Cooldown Recovery Rate (x belt effect 1.97 = 3 in the build); the jewel also gives +10 Dex/Int, 10-12 physical to spells, +36 ES; abyss prefixes Facilitating 2% (ilvl 75) and Expediting 3% (ilvl 86), fixed rolls, scaled by the host item's effect", source: "build item 24; headless EK Tabulate (3 @ Item:24); Data/ModJewelAbyss.lua:513-514; poewiki List of abyss jewel prefix modifiers rev 1490090 (added 3.14.0)", pob: full, variant: "rare jewel, no variant list"}
  - {kind: ascendancy, name: "Ascendant Saboteur choice 58827", slot: tree, role: scales, target: self, text: "15% increased Cooldown Recovery Rate (with 30% increased Area of Effect, 20% chance for 50% more Area Damage, 25% chance to Blind)", source: "TreeData/3_29/tree.lua:21150-21160", pob: full}
  - {kind: ascendancy, name: "Delirious Bloodline 46704", slot: tree, role: scales, target: self, text: "15% increased Cooldown Recovery Rate; the bloodline shares ascendancy points with the main class", source: "TreeData/3_29/tree.lua:14177-14185; poewiki Delirious Bloodline rev 1592181, Bloodline ascendancy class rev 1700682", pob: full}
  - {kind: support, name: "Awakened Cast On Critical Strike", slot: any, role: scales, target: self, text: "base_spell_cooldown_speed_+% 10 (L1) to 22 (L5) on the triggered spell; -7% less spell damage at L5; probe source Skill:SupportCastOnCritTriggeredPlus 22", source: "PoB Data/Skills/sup_dex.lua:699-731; headless EK swap row", pob: full}
  - {kind: support, name: "Cooldown Recovery (support gem)", slot: any, role: scales, target: self, text: "30% (L1), 35, 40 (L3, naturalMaxLevel 3) ... 72% (L15); mana multiplier 50% (EK ManaCost 18 -> 35); takes one support slot", source: "PoB Data/Skills/sup_int.lua:1280-1315; Data/Gems.lua:15604-15618; headless EK probe", pob: full}
  - {kind: tattoo, name: "Tattoo of the Tasalio Makanga", slot: tree, role: scales, target: self, text: "8% increased Cooldown Recovery Rate", source: "PoB Data/TattooPassives.lua:4039", pob: full}
  - {kind: unique, name: "The Torrent's Reclamation (Cloth Belt)", slot: belt, role: scales, target: self, text: "(15-20)% increased Cooldown Recovery Rate (Greater Harbinger of Time)", source: "PoB Data/Uniques/belt.lua:335-349 (line 348); ModCache.lua:5266", pob: full}
  - {kind: unique, name: "Glimpse of Chaos (Vaal Mask)", slot: helmet, role: scales, target: self, text: "corrupted implicit variant 9 'Cooldown Recovery': (8-12)% increased Cooldown Recovery Rate", source: "PoB Data/Uniques/helmet.lua:1474-1511 (variant list 1488, line 1509); Data/ModItemExclusive.lua:4169", pob: full, variant: "variant 9 (Cooldown Recovery); choose it explicitly, not the first Variant line"}
  - {kind: foulborn, name: "Asenath's Mark, Foulborn (Iron Circlet)", slot: helmet, role: scales, target: self, text: "(10-15)% increased Cooldown Recovery Rate", source: "PoB Data/ModFoulbornMap.jsonc:645-646; Data/ModFoulborn.lua:304; Data/Uniques/helmet.lua:357-371", pob: full, variant: "replaces '(10-15)% increased Attack Speed' (IncreasedAttackSpeedUniqueIntHelmet2)"}
  - {kind: mod, name: "Shaper / Crusader influenced belt suffix", slot: belt, role: scales, target: self, text: "'of Shaping': (10-15)% ilvl 75, (16-20)% ilvl 84 (weight 800); 'of the Crusade': (10-15)% ilvl 75, (16-20)% ilvl 84 (weight 250); one suffix per belt (group GlobalCooldownRecovery)", source: "PoB Data/ModExplicit.lua:2109-2110, 3158-3159", pob: full}
  - {kind: mod, name: "Shaper / Crusader influenced boots suffix", slot: boots, role: scales, target: self, text: "'of Shaping' (10-15)% ilvl 80; 'of the Crusade' (6-10)% ilvl 75 and (11-15)% ilvl 80; Maven 'of Elevated Shaping' / 'of the Elevated Crusade' (16-20)% ilvl 90 (spawn weight 0)", source: "PoB Data/ModExplicit.lua:1776, 2787-2788, 3993, 4017", pob: full}
  - {kind: mod, name: "Veiled belt suffix 'of the Order'", slot: belt, role: scales, target: self, text: "(13-16)% increased Cooldown Recovery Rate, ilvl 60 (weight 1500); bench 'of Craft' (6-8)% / (9-12)%", source: "PoB Data/ModVeiled.lua:91; Data/ModMaster.lua:510-511", pob: full}
makes_redundant:
  - {provider: "Any CDR source past the next breakpoint", when: "attack rate x hit x crit is below the cap of the band already reached (EK: 8.92 < 10.10)", why: "PoB gives no extra triggers until the source passes the next cap; slack above the breakpoint is free to trade away", source: "headless EK sweep, sums 52..127 all give 10.101 / 8.930 / 15,136,639"}
conflicts:
  - {with: "Movement Skills / throwing Traps / Warcry / Guard / Retaliation / Stance / Brand Recall / minion Cooldown Recovery", effect: "tagged to other skills, does not reach the triggered spell's cap", source: "headless EK probe (Movement Skills +30: Cyclone 80, Ethereal Knives 50, cap 7.5758 unchanged); tree.lua:69980-70002, 74767-74813, 75588-75631, 26634, 33379-33457, 42815, 49366-49387, 31764-31801, 45015-45035, 63434-63468, 15792, 21678"}
  - {with: "Bloodline vs regular ascendancy points", effect: "the Delirious notable costs ascendancy points that the Saboteur picks (Like Clockwork, Ascendant choice) also need", source: "poewiki Bloodline ascendancy class rev 1700682"}
  - {with: "Cast On Critical Strike (plain) vs Awakened Cast On Critical Strike", effect: "same support slot; Awakened adds cooldown recovery and -7% instead of -10% less spell damage but must be obtained and levelled", source: "PoB Data/Skills/sup_dex.lua:699-731; headless EK swap row (FullDPS 15,647,707)"}
conditions:
  - {text: "RULE: sum of Cooldown Recovery that applies to the triggered spell >= breakpoint; slack = sum - breakpoint. A swap that drops the sum below it costs the SkillTriggerRate ratio (PoB simulation), not the cap ratio. EK: breakpoint 52 (exact 51.52), sum 53, slack 1; 53 -> 50 means FullDPS -39.5% (cap alone says -25%)", source: "headless EK removal rows; CalcTriggers.lua:91-134, 814"}
  - {text: "attack rate x hit x crit must be <= the cap of the band reached, else the simulation loses more than the cap ratio; the 128% breakpoint only matters when the source passes 10.10/s", source: "headless EK sweep (SkillTriggerRate 8.930 at the 10.10 and 15.15 bands); CalcTriggers.lua:91-134"}
  - {text: "Forbidden Flame and Flesh must both be worn for the 50% (an emptied socket removes the grant)", source: "CalcSetup.lua:1401-1416; headless EK rows Flame / Flesh emptied"}
  - {text: "only unconditional Cooldown Recovery, or lines tagged to the triggered spell, reach the cap", source: "CalcTriggers.lua:563; headless EK Movement Skills probe"}
uptime:
  Mapping:       {value: pob, config: {}, reasoning: "PoB's Cooldown Recovery lines on the EK build carry no scenario condition, so the band is the same; the scenario only moves the attack rate, which PoB takes from its own output", source: "headless EK Tabulate (3 @ Item:24, 50 @ Tree:51462); CalcTriggers.lua:563"}
  Pinnacle Boss: {value: pob, config: {}, reasoning: "Same band, same PoB number; no scenario-specific CDR source was found in the build", source: "headless EK Tabulate; CalcTriggers.lua:563"}
seeds: [EK]
sources:
  - {ref: "PoB Modules/CalcTriggers.lua, Modules/Data.lua:237-238, Data/Skills/sup_dex.lua, sup_int.lua, Data/Gems.lua, Data/ModJewelAbyss.lua, ModExplicit.lua, ModVeiled.lua, ModFoulborn(Map), Data/Uniques, TreeData/3_29/tree.lua (2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Delirious_Bloodline (rev 1592181)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Bloodline_ascendancy_class (rev 1700682)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/List_of_abyss_jewel_prefix_modifiers (rev 1490090)", kind: wiki, patch: "3.29"}
  - {ref: "vault Interactions/CoC trigger.md (formula and breakpoints)", kind: discovery, patch: "3.29"}
not_verified:
  - "The -39.7% SkillTriggerRate loss below a breakpoint is PoB simulation (CalcTriggers.lua:91-134), not tested in game"
  - "Whether the game accepts a Cooldown Recovery support gem on a CoC-triggered spell (PoB accepts it: CoC Triggered adds SkillType.Cooldown, sup_dex.lua:590; probe added it as 7th gem)"
  - "Higher gem levels of Cooldown Recovery (L4-L15) need +gem levels; obtainability not checked"
  - "Awakened CoC drop and level cap (naturalMaxLevel read from data only)"
  - "Obtainability in 3.29 of The Torrent's Reclamation (no Source line in PoB), Shaper/Crusader/Maven belt and boots suffixes, veiled and bench belt crafts, Glimpse of Chaos: PoB data only"
  - "Asenath's Mark Foulborn replaced line is from ModFoulbornMap.jsonc:645-646; 'Asenath's Chant' has the same line in ModFoulbornMap.lua:40 but no jsonc entry, so its replaced line is unverified"
  - "Abyss prefix Expediting 3% on a x1.97 belt would show 5 (3 x 1.97 = 5.91 truncated), computed, not probed"
  - "Whether attack-speed conditions in the EK build differ between Mapping and Pinnacle Boss (source rate 8.92 is the PoB default config)"
  - "Fractional CDR: sums are integers in this build (Grim 2% x 1.97 shown as 3); exact threshold 51.52"
  - "Other global CDR sources not listed (The Flow Untethered, The Sands of Time, Scourge belt upsides, Balance of Terror with Temporal Chains, Saboteur's charms, Bound by Destiny): see tasks/reports/027-batch4d.md"
open_questions:
  - "Should the generator treat the breakpoint as a hard minimum (sum >= 52) or let the optimiser trade it against DPS elsewhere (at 53 -> 50 the loss is -39.5% FullDPS)?"
```
