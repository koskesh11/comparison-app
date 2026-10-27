---
type: interaction
status: draft
pob_refs: [ConvertSpellSuppressionToSpellDodge, SpellSuppressionChance, SpellDodgeChance, SpellDodgeChanceMax, EffectiveSpellDodgeChance, SpellNotHitChance, ConfiguredNotHitChance, TotalEHP, FireMaximumHitTaken, enemyIsBoss]
source: "poewiki Acrobatics rev 1577377 (fetched 2026-10-26; redesign 3.16.0, no later row; text equals tree.lua); Dodge rev 1595031 and Spell suppression rev 1675604 as quoted in the Defences note; PoB 2.67.2 CalcDefence.lua / CalcSetup.lua / ModParser.lua / Data/ModCache.lua / TreeData 3_29; headless runs on EK, FR and the Fireball seed (scratchpad b3c/F_run.py, evidence b3c/tree-ascendancy-analyst-F.md)"
last_confirmed_patch: "3.29.x"
---

Acrobatics (keystone, node 54307, TreeData/3_29/tree.lua:80903-80907) is the 3.16.0 redesign: "Modifiers to Chance to Suppress Spell Damage instead apply to Chance to Dodge Spell Hits at 50% of their value. Maximum Chance to Dodge Spell Hits is 75%". Your suppression drops to 0 and half of every suppression modifier becomes a chance to avoid the spell hit entirely. It is the only source of spell dodge in the game (wiki). The trade: an avoid chance (raises effective HP over many hits, does nothing for the size of the hit that kills you) in place of a guaranteed 40% reduction on every spell hit once suppression is at 100% (raises the maximum hit). The phase variant (Phase Acrobatics) is not on the 3_29 tree (grep 0 hits in tree.lua); PoB maps the unique mod "Phase Acrobatics" to this same keystone. Related: [[Defences]] (suppression and dodge caps), [[Receiving damage]].

Pipeline: [[Receiving damage#Spell suppression]] - PoB turns the suppression layer into the avoidance layer: SpellSuppressionChance is overridden to 0 and SpellDodgeChance gets (uncapped suppression sum) / 2; the dodge then enters SpellNotHitChance (CalcDefence.lua:1691-1692) as an independent factor, like the other avoid chances in [[Defences#Damage avoidance]]; limits in [[Defences#Spell suppression chance]].

How PoB applies it: the line parses to flag ConvertSpellSuppressionToSpellDodge plus SpellSuppressionChance OVERRIDE 0 (Data/ModCache.lua:18280, Modules/ModParser.lua:2210-2213); "Maximum Chance to Dodge Spell Hits is 75%" is SpellDodgeChanceMax OVERRIDE 75 (Data/ModCache.lua:17639, ModParser.lua:2222), the same as the base 75 (CalcSetup.lua:30) but an override, so no other mod can raise the cap. CalcDefence.lua:1137-1146 reads the raw (uncapped) BASE sum of SpellSuppressionChance, adds half of it as SpellDodgeChance, then reports suppression 0; CalcDefence.lua:1182-1196 caps dodge at the maximum.

Measured (headless, in memory, nothing saved; keystone only - node 54307 force-allocated alone, path cost not included; enemy level from the headless run: 85 at None, 84 at Pinnacle):

| Seed | boss | suppression -> dodge | SpellNotHitChance | TotalEHP | max hits |
|---|---|---|---|---|---|
| EK (suppression 10) | None | 10 -> 0 / 0 -> 5 | 21 -> 24.95 | 71911 -> 73174 (+1.8%) | unchanged |
| EK | Pinnacle | 10 -> 0 / 0 -> 5 | 21 -> 24.95 | 145259 -> 148032 (+1.9%) | unchanged |
| FR (suppression 0) | None / Pinnacle | 0 / 0 | unchanged | unchanged | unchanged |
| Fireball seed (suppression 0, NOT VIABLE) | None / Pinnacle | 0 / 0 | unchanged | unchanged | unchanged |

Hypothetical suppression (added with a custom line 'chance to Suppress Spell Damage' so the seed reaches the stated total; this is not a gear option, it shows where the trade turns):

| Seed | total suppression | suppression alone: TotalEHP, fire max hit | with Acrobatics: dodge, TotalEHP, fire max hit |
|---|---|---|---|
| EK | 100 | +22.6% (None and Pinnacle), 24714 -> 30893 (+25.0%) | 50, +53.8% (None) / +54.6% (Pinnacle), 24714 (unchanged) |
| EK | 150 | same as 100 (capped at 100, 40% prevented) | 75 (cap), +114.8% (None) / +117.0% (Pinnacle), unchanged |
| FR | 100 | +25.0%, 350850 -> 438563 (+25.0%) | 50, +33.3%, 350850 (unchanged) |
| Fireball seed | 100 | +24.9% (None) / +25.0% (Pinnacle), 18532 -> 23165 (+25.0%) | 50, +33.3%, 18532 (unchanged) |

- Reading: at 100% suppression Acrobatics wins on TotalEHP (+33% against +25% on FR and the Fireball seed) but loses the max-hit gain (suppression raises the fire max hit by 25%, dodge by 0). Above 100% total suppression it wins clearly because the raw sum converts: 150 becomes 75 dodge while suppression alone is capped at 100. At a low total (EK's 10) the keystone is nearly neutral (+1.8%) because the allocation also removes the suppression itself.
- DPS keys are unchanged on all seeds.

What PoB leaves out or does inconsistently (by code, not measured unless stated):
- PoB's dodge is averaged into the EHP; a pinnacle one-shot is not smoothed by an avoid chance (the wiki order puts dodge before block and mitigation; PoB multiplies independent factors, see [[Receiving damage]]).
- Effects keyed on suppression read the overridden value: 'critical strike chance is increased by chance to suppress spell damage' uses output.SpellSuppressionChance (CalcOffence.lua:752-756), 0 under Acrobatics; life/ES gained on suppress use EffectiveSpellSuppressionChance (CalcDefence.lua:2816-2837). 'Suppression applies to ailment avoidance' reads the raw BASE sum (CalcPerform.lua:874, 887, 898), so it still counts. The game's behaviour for these was not checked.

```interaction
id: acrobatics
mechanic: "Modifiers to Chance to Suppress Spell Damage instead apply to Chance to Dodge Spell Hits at 50% of their value; suppression chance becomes 0; maximum Chance to Dodge Spell Hits is 75%; spell dodge prevents the whole spell hit and rolls independently per hit"
family: defence
target: self
related: [defences, receiving-damage]
pipeline_step: ["Receiving damage#Spell suppression", "Defences#Damage avoidance"]
pipeline_why: "Acrobatics replaces the suppression layer (40% less damage per hit at 100% chance, order: after resistance, before block) with an avoidance layer: PoB overrides SpellSuppressionChance to 0 (CalcDefence.lua:1137-1146) and adds half the raw suppression sum as SpellDodgeChance, which multiplies into SpellNotHitChance (CalcDefence.lua:1691-1692); the max hit is therefore not raised by dodge, the expected damage is."
pob:
  measured: full
  how: "Data/ModCache.lua:18280 (flag ConvertSpellSuppressionToSpellDodge + SpellSuppressionChance OVERRIDE 0), 17639 (SpellDodgeChanceMax OVERRIDE 75); CalcDefence.lua:1137-1146 (dodge = raw suppression sum / 2), 1182-1196 (cap, EffectiveSpellDodgeChance), 1691-1692 (SpellNotHitChance), 2816-2837 (suppression in the EHP); CalcSetup.lua:30 (base max 75). Measured headless on EK, FR, Fireball seed (node 54307 alone, None and Pinnacle): EK suppression 10 -> 0, dodge 0 -> 5, TotalEHP +1.8% / +1.9%; FR and Fireball seed unchanged (0 suppression); hypothetical totals via custom line: 100 suppression -> 50 dodge gives EK +53.8% / +54.6% EHP versus +22.6% for suppression alone, FR and Fireball +33.3% versus +25.0%; max hit gain of suppression (+25.0%) is lost. Not modelled: in-game ordering of dodge before block, effects keyed on suppression after the override (crit chance from suppression, life or ES on suppress)."
  config:
    - {var: enemyIsBoss, default: "Pinnacle (list index 3)", ref: "Modules/ConfigOptions.lua:2086 (enemy damage mix and level used by the EHP)", class: b}
    - {var: EHPUnluckyWorstOf, default: "Average", ref: "Modules/ConfigOptions.lua:226 (makes dodge and suppression rolls unlucky in the EHP; PoB has DodgeChanceIsUnlucky at CalcDefence.lua:1192-1194)", class: c}
  unparsed: []
model: null
providers:
  - {kind: keystone, name: "Acrobatics 54307", slot: tree, role: enables, target: self, text: "Modifiers to Chance to Suppress Spell Damage instead apply to Chance to Dodge Spell Hits at 50% of their value; Maximum Chance to Dodge Spell Hits is 75%", source: "TreeData/3_29/tree.lua:80903-80907; Data/ModCache.lua:17639, 18280; Modules/ModParser.lua:2210-2213, 2222", pob: full}
  - {kind: tattoo, name: "Acrobatics tattoo (keystone tattoo)", slot: tree, role: enables, target: self, text: "replaces a tree node with the Acrobatics keystone (Limited to 1 Keystone Tattoo)", source: "Data/TattooPassives.lua:36-41", pob: full}
  - {kind: unique, name: "Hyrri's Ire", slot: Body Armour, role: enables, target: self, text: "Acrobatics (variants 1 and 2 of the PoB unique)", source: "Data/Uniques/body.lua:342; Data/ModCache.lua:11970", pob: full, variant: "variants 1, 2"}
  - {kind: unique, name: "The Perfect Form", slot: Body Armour, role: enables, target: self, text: "Acrobatics, with Arctic Armour has no Reservation and Evasion Rating increased by overcapped Cold Resistance", source: "Data/Uniques/body.lua:436-443; Data/ModCache.lua:11970", pob: full}
  - {kind: mod, name: "Phase Acrobatics (item mod text 'Acrobatics')", slot: any, role: enables, target: self, text: "PoB maps the Phase Acrobatics unique mod to this keystone; there is no Phase Acrobatics node in the 3_29 tree (0 matches in tree.lua)", source: "Data/ModItemExclusive.lua:5172, 5183; TreeData/3_29/tree.lua (grep 'Phase Acrobatics': 0)", pob: full}
  - {kind: mod, name: "Crucible weapon tree and Hellscape upside: Acrobatics", slot: Weapon, role: enables, target: self, text: "weapon tree keystone and Scourge body armour upside", source: "Data/Crucible.lua:1346; Data/ModScourge.lua:836", pob: full}
  - {kind: mod, name: "+#% chance to Suppress Spell Damage (tree, gear, jewels, Dexterity-style thresholds)", slot: any, role: scales, target: self, text: "every point of raw suppression becomes half a point of dodge, including points above the 100% cap; the conditional ones (boots, helmet and gloves with evasion; dagger count) count only when their condition holds", source: "Modules/CalcDefence.lua:1137-1144; Modules/ModParser.lua:360, 4005-4015", pob: full}
  - {kind: mod, name: "Suppression-keyed effects (Spell Suppression Effect, crit chance from suppression, life or ES on suppress, suppressed recently)", slot: any, role: blocks, target: self, text: "they read the overridden 0: the effect size and the 'on suppress' gains have nothing to scale from under Acrobatics", source: "Modules/CalcOffence.lua:752-756; Modules/CalcDefence.lua:1147, 2816-2837; Modules/ModParser.lua:4000-4002", pob: partial}
makes_redundant:
  - {provider: "Suppression effect modifiers and the 100% suppression cap discipline (chance above 100% is wasted without Acrobatics)", when: "Acrobatics allocated", why: "suppression chance is 0 so the prevented-damage effect has nothing to act on, and the over-100% sum now converts to dodge up to the 75% cap", source: "Modules/CalcDefence.lua:1137-1146; measured EK 150 total suppression -> 75 dodge"}
conflicts:
  - {with: "builds that sit at 100% suppression for the 40% damage reduction and a higher maximum hit", effect: "Acrobatics trades the guaranteed reduction (fire max hit +25%) for an avoid chance (max hit +0%); EHP is higher at 100% suppression (+33% against +25%) but a single large spell hit is not softened", source: "headless FR and Fireball seed hypothetical totals; Modules/CalcDefence.lua:2072-2075"}
  - {with: "very low suppression (EK 10%)", effect: "the keystone removes 10% suppression and adds 5% dodge: +1.8% EHP, not worth a keystone point on its own", source: "headless EK run"}
conditions:
  - {text: "spell dodge applies to spell hits only (not attacks, not damage over time); it rolls independently per hit and happens before block and other mitigation", source: "wiki Acrobatics rev 1577377"}
  - {text: "dodge is capped at 75%; PoB overrides the cap to 75 so a higher maximum from another mod is ignored", source: "Data/ModCache.lua:17639; Modules/CalcDefence.lua:1184"}
uptime:
  Mapping:       {value: always, config: {enemyIsBoss: "None / map monsters (env.enemyLevel 85 in the headless run)"}, reasoning: "permanent while allocated; the benefit is the converted suppression: EK +1.8% EHP at 10 suppression, +53.8% at a hypothetical 100; FR and the Fireball seed gain nothing at their 0 suppression", source: "headless EK/FR/Fireball seed"}
  Pinnacle Boss: {value: pob, config: {enemyIsBoss: "Pinnacle (default; env.enemyLevel 84 in the headless run)"}, reasoning: "use PoB's TotalEHP and SpellNotHitChance, but remember dodge leaves the max hit untouched: against a boss spell that one-shots, suppression at 100% raises the survivable hit by 25% and dodge does not", source: "headless EK/FR/Fireball seed"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Acrobatics (rev 1577377; redesign row 3.16.0)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcDefence.lua:1137-1196, 1691-1692, 2072-2075, 2816-2837; Modules/CalcSetup.lua:30; Modules/CalcOffence.lua:752-756; Modules/CalcPerform.lua:874, 887, 898; Modules/ModParser.lua:360, 2210-2213, 2222, 4000-4015; Modules/Data.lua:248-251; Modules/ConfigOptions.lua:226, 2086; Data/ModCache.lua:11970, 17639, 18280; Data/TattooPassives.lua:36-41; Data/Uniques/body.lua:342, 436-443; Data/ModItemExclusive.lua:5172, 5183; Data/Crucible.lua:1346; Data/ModScourge.lua:836; TreeData/3_29/tree.lua:80903-80907", kind: pob, patch: "3.29"}
  - {ref: "headless runs EK, FR, Fireball seed (scratchpad b3c/F_run.py, F_show.py; evidence b3c/tree-ascendancy-analyst-F.md)", kind: discovery, patch: "3.29"}
not_verified:
  - "whether the game converts the uncapped suppression sum (PoB: 150 total -> 75 dodge) or only the capped 100%: the wiki says 'modifiers', PoB reads the raw BASE sum"
  - "whether Hyrri's Ire variants 1 and 2 are still current in 3.29 and which Phase Acrobatics unique still exists: read from PoB data files only"
  - "the hypothetical totals (100 and 150 suppression) come from a custom line, not from real gear; no seed or obtainable setup was checked for reaching them"
  - "how the game treats suppression-keyed effects (crit chance from suppression, life or ES on suppress) under Acrobatics; PoB's handling was read from code only"
  - "the wiki page for Acrobatics is older (rev 1577377) than other keystone pages; its text equals the 3_29 tree line, no later change was found"
  - "suppression effect 40% is PoB data (Modules/Data.lua:251) and the Defences note's wiki quote (patch 3.27.0); not re-fetched here"
  - "enemy level 85 (None) and 84 (Pinnacle) are env.enemyLevel from the headless run; why None is one level higher was not traced"
open_questions:
  - "Should the generator ever pick Acrobatics for an ES/CI spell seed whose suppression is below ~60%, or only for builds that can pass 100% suppression?"
```
