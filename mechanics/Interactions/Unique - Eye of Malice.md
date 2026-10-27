---
type: interaction
status: draft
pob_refs: [TotalDPS, FullDPS, EnergyShield, Evasion, ColdExposure, FireExposure, ColdResist]
source: "PoB 2.67.2 Data/Uniques/helmet.lua:1445-1450, Data/ModCache.lua:1901/1160/7329/7331/18380, CalcPerform.lua:396-408 and 3629-3657, CalcOffence.lua:503 and 4264-4273, ConfigOptions.lua:1973-1978, Data.lua:245; poewiki Eye of Malice rev 1578021, Exposure; vault Exposure, Chance on hit uptime; headless Worb probes (task 027 batch 2c, item-analyst-worb.md)"
last_confirmed_patch: "3.29.x"
---

Eye of Malice is a package for a negative-resistance stack: 25% chance to inflict Cold and Fire Exposure on hit, and "Nearby Enemies have 50% increased Fire and Cold Resistances" - a downside that is the point, because increased resistance multiplies a negative sum (Worb Pinnacle effective cold resistance -27 -> -40.5, Mapping -77 -> -115.5). Plus 499% increased Evasion and Energy Shield and two resistances, 4 white sockets.
In Worb the Eye is the only exposure source and it also arms Mastermind of Discord's extra -25 (only added when an exposure exists), so removing the helmet drops the exposure side by -35 in total: -33.11% Pinnacle / -33.18% Mapping TotalDPS. PoB applies the "Nearby" line with no distance gate (the wiki radius is 3 metres), so its +9.22% / +17.38% is an upper value for a skill cast at range.
Pipeline: [[Damage calculation#Resistance, exposure and penetration]] - exposure sets the enemy resistance base, the +50% INC multiplies the summed base, in that order

```interaction
id: unique-eye-of-malice
mechanic: "Unique package: 25% chance to inflict Cold/Fire Exposure on hit and +50% increased enemy Fire and Cold resistance (the point of the item on a negative-resistance stack), plus 499% increased Evasion and Energy Shield"
family: ailment
pipeline_step: ["Damage calculation#Resistance, exposure and penetration"]
pipeline_why: "exposure and curses add to the enemy resistance base, then increased enemy resistance multiplies that sum (CalcOffence.lua:503), so a negative base gets more negative"
target: enemy
related: [exposure, chance-on-hit-uptime, elemental-equilibrium, curse-application, penetration, defences, energy-shield-hybrid, max-resistances]
pob:
  measured: partial
  how: "Parse: all six lines parse, extra = nil (499% is a live parse: EvasionAndEnergyShield INC 499, local; the Nearby line is two EnemyModifier LIST FireResist INC 50 / ColdResist INC 50 with no tag and flags 0, ModCache.lua:18380). The exposure chance sets Condition CanApplyColdExposure (CalcPerform.lua:396-408) and skillFlags.applyColdExposure (CalcOffence.lua:4264-4273); the -10 comes from the config box (ConfigOptions.lua:1973-1978, mod ColdExposure BASE -10 gated by CanApplyColdExposure). The exposure block (CalcPerform.lua:3629-3657) takes the smallest exposure, adds ExtraExposure (Tree:61259 Mastermind of Discord -25, only when an exposure exists) and sets enemy ColdResist BASE -35 'Config'. The Nearby line has NO config gate and NO distance gate in PoB; it lands in enemyDB INC (CalcOffence.lua:503: resist = sum BASE x max(1 + INC/100, 0), floor -200 Data.lua:245). Enemy ColdResist in Worb (Pinnacle): BASE 50 boss -37 Frostbite -35 exposure (-10 box, -25 Mastermind) -5 Tree:42649 = -27; INC 50 -> effective -40.5. Mapping -77 -> -115.5. Without the Eye +8 (Pinnacle) / -42 (Mapping), no INC. Whole-item removal Worb (Pinnacle / Mapping): TotalDPS 1,343,497.51 -> 898,721.89 (-33.11%) / 1,934,211.10 -> 1,292,384.84 (-33.18%), FullDPS 4,493,609.43 / 6,461,924.22; ES 2318 -> 1938 (-16.39%), Evasion 1482 -> 78 (-94.74%), EHP -8.55% / -13.97%; resistances stay 75 each (35/24 are overcap); no unmet requirement. PoB keeps the helmet socket group (Immortal Call L8, Cast when Damage Taken L6, Frost Shield L20, Vaal Cold Snap L20) after the item is removed (CalcSetup.lua:1605-1608), so the removal delta is not a game fact."
  config:
    - {var: conditionEnemyColdExposure, default: false, ref: "Modules/ConfigOptions.lua:1976-1978", class: b}
    - {var: conditionEnemyFireExposure, default: false, ref: "Modules/ConfigOptions.lua:1973-1975", class: b}
    - {var: enemyIsBoss, default: "Pinnacle (file default)", ref: "Modules/ConfigOptions.lua:2086", class: b}
  unparsed: []
model: null
providers:
  - {kind: unique, name: "Eye of Malice", slot: Helmet, role: sustains, target: self, text: "499% increased Evasion and Energy Shield ((400-500)); DPS 0, ES -13.68%, Evasion -78.95%, EHP -7.56% Pinnacle / -11.70% Mapping when removed", source: "Data/Uniques/helmet.lua:1445; live parse", pob: full}
  - {kind: unique, name: "Eye of Malice", slot: Helmet, role: sustains, target: self, text: "+35% Fire Resistance (0.00%, overcap)", source: "Data/Uniques/helmet.lua:1446; ModCache.lua:1901", pob: full}
  - {kind: unique, name: "Eye of Malice", slot: Helmet, role: sustains, target: self, text: "+24% Cold Resistance (0.00%, overcap)", source: "Data/Uniques/helmet.lua:1447; ModCache.lua:1160", pob: full}
  - {kind: unique, name: "Eye of Malice", slot: Helmet, role: applies, target: enemy, text: "25% chance to inflict Cold Exposure on Hit: -35.84% Pinnacle / -23.70% Mapping TotalDPS (enemy cold base -27 -> +8 / -77 -> -42); also gates Mastermind's -25", source: "Data/Uniques/helmet.lua:1448; ModCache.lua:7329; CalcPerform.lua:396-408 and 3629-3657", pob: config}
  - {kind: unique, name: "Eye of Malice", slot: Helmet, role: applies, target: enemy, text: "25% chance to inflict Fire Exposure on Hit: 0.00% for Winter Orb (Worb deals no fire damage; only the Flame Golem minion, 217 -> 364 DPS without the Eye, noise); box unticked in Worb.xml", source: "Data/Uniques/helmet.lua:1449; ModCache.lua:7331; ConfigOptions.lua:1973-1975", pob: config}
  - {kind: unique, name: "Eye of Malice", slot: Helmet, role: abuses, target: enemy, text: "Nearby Enemies have 50% increased Fire and Cold Resistances: an UPSIDE on a negative stack, -9.22% Pinnacle / -17.38% Mapping TotalDPS when removed (effective cold -40.5 -> -27 / -115.5 -> -77); PoB has no 3 m gate, so these are upper values", source: "Data/Uniques/helmet.lua:1450; ModCache.lua:18380; CalcOffence.lua:503; poewiki Eye of Malice rev 1578021", pob: partial}
package:
  seed: Worb
  slot: Helmet
  base: "Callous Mask, 4 white sockets, quality 20"
  xml_item_id: 17
  variant: "none noted in the evidence"
  removal: "TotalDPS -33.11% Pinnacle / -33.18% Mapping (parts: cold exposure line -35.84% / -23.70%, Nearby +50% line -9.22% / -17.38%; they multiply, so the parts do not add) - in-memory removal; PoB keeps the emptied slot's gems active (CalcSetup.lua:1605-1608), so the in-game loss is larger: if the helmet group (Immortal Call L8, Cast when Damage Taken L6, Frost Shield L20, Vaal Cold Snap L20) is lost, EHP -26.72% Pinnacle / -37.04% Mapping (helmet + group EHP -32.89% / -44.36%); Vaal Cold Snap alone is 876,711 TotalDPS with the Eye (586,469 without), outside FullDPS"
  lost_with_item:
    - "Cold exposure source: the ticked box conditionEnemyColdExposure stops doing anything AND Mastermind of Discord's -25 stops being added (exposure no longer exists): exposure side -35 in total"
    - "Nearby +50% enemy Fire/Cold resistance multiplier"
    - "ES 2318 -> 1938, Evasion 1482 -> 78, EHP -8.55% / -13.97%"
    - "helmet socket group (4 sockets) in the game; conditions CanApplyColdExposure, CanApplyFireExposure, UsingHelmet off; multipliers HelmetItem, SocketedGemsInHelmet 4 -> 0, UniqueItem 3 -> 2"
  downsides_that_are_the_point:
    - "Nearby Enemies have 50% increased Fire and Cold Resistances: not a drawback for Worb because the resist stack is negative (-27 / -77 before the multiplier); wiki: multiplies negative resistances, a monster at -30% gets -45%. It would hurt a build with positive enemy resistance"
  foulborn: "none: ModFoulbornMap grep = no hit; wiki Foulborn unique item rev 1702126 does not list it"
  obtainability: "poewiki Eye of Malice rev 1578021: introduced 3.9.0; 3.14.0 several drop-restricted uniques became core uniques (this page lists no restriction); cargo: drop_enabled 1, is_drop_restricted 0, drop_level 73, required level 45; random drop. Patch 3.29"
makes_redundant:
  - {provider: "Other cold exposure sources", when: "stacked on the Eye", why: "the smallest exposure value wins, so a second cold exposure source is redundant on the exposure value, but not on Mastermind's -25 gate", source: "CalcPerform.lua:3629-3657"}
conflicts:
  - {with: "Elemental Equilibrium", effect: "removes the cold exposure on every cold hit; measured -35.84% / -23.70% with the box ticked, same numbers as the Eye's exposure line because the Eye is Worb's only exposure source (Worb.xml does not allocate EE, node 39085 absent)", source: "vault Elemental Equilibrium; item-analyst-worb.md"}
  - {with: "Resist-reduction curses (Frostbite)", effect: "stack: sources add into the base, the INC multiplies the sum", source: "CalcOffence.lua:503"}
conditions:
  - {text: "The 50% increased enemy resistance helps only while the summed enemy resistance base is negative; PoB has no distance gate, the wiki says 'The Nearby radius is 3 metre', so it applies in game only when the target is within 3 m of the player", source: "CalcOffence.lua:503; poewiki Eye of Malice rev 1578021"}
  - {text: "Exposure needs the 25% chance to land at least once per duration; the -10 comes from the config box", source: "CalcPerform.lua:396-408; ConfigOptions.lua:1976-1978"}
uptime:
  Mapping:       {value: high, config: {conditionEnemyColdExposure: true}, reasoning: "chance on hit uptime (Worb worked example): V 6.45/s, d 4 s, n = ceil(25.8) - 1 = 25, lower bound m = 1 (packs): 1 - 0.75^25 = 99.92%; without the wand V 6.30 n 25 m 3: above 99.9999%. Above the 80% rule, box ticked, no notice (= Worb.xml)", source: "vault Chance on hit uptime"}
  Pinnacle Boss: {value: high, config: {conditionEnemyColdExposure: true}, reasoning: "m = 4.43 hits per volley (golden 4): u = 1 - 0.75^100 above 99.9999%. The Nearby +50% line is on in PoB regardless, but in game only within 3 m of the player", source: "vault Chance on hit uptime; vault Winter Orb projectile overlap"}
seeds: [Worb]
sources:
  - {ref: "https://www.poewiki.net/wiki/Eye_of_Malice (rev 1578021)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Data/Uniques/helmet.lua, Data/ModCache.lua, Modules/CalcPerform.lua, Modules/CalcOffence.lua, Modules/ConfigOptions.lua, Modules/Data.lua", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/partial/b2c/item-analyst-worb.md (headless Worb probes, SC/out/w1.json, w2.json)", kind: pob, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: the 3 m Nearby gate in play (Winter Orb is cast at range; PoB applies the line unconditionally)"
  - "NOT VERIFIED: whether Frostbite's -37 in the wiki matches PoB's L20 value"
open_questions:
  - "Should the generator treat the Nearby +50% line as a benefit only when the summed enemy resistance base is negative, and cap its value for ranged skills?"
```
