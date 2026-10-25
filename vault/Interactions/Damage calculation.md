---
type: interaction
status: draft
pob_refs: ["AccuracyHitChance", "HitChance", "CritChance", "CritMultiplier", "AverageHit", "AverageDamage", "ScaledDamageEffect", "EnemyPhysicalDamageReduction", "enemy<Type>Resist"]
source: "poewiki Receiving damage rev 1702582 (outgoing part), Damage 1551019, Damage conversion 1673519, Damage effectiveness 1660645, Critical strike 1698799, Accuracy 1612031, Resistance 1659347, Armour 1625574; PoB 2.67.2 CalcOffence.lua / CalcDefence.lua; evidence mechanics-researcher-damage-calc.md, pob-coverage-auditor-calc-order.md"
last_confirmed_patch: "3.29.x"
---

This is the foundation for judging whether an outgoing-damage interaction works: every heading is one step of the wiki order, so other notes can link e.g. [[Damage calculation#More and less]]. The wiki holds the whole order on one page, Receiving damage (rev 1702582, edited live in 2026, so this is the current text and not tied to a patch). Each step gives the rule, the wiki quote, how PoB matches it and why it matters for a build. The incoming order is [[Receiving damage]], the per-layer numbers are [[Defences]].

Order differences wiki vs PoB: (1) the wiki rolls damage AFTER the crit; PoB has no sequence there, it averages min/max after the crit multiplier, so averages agree but max-hit views do not. (2) The wiki treats Conversion and Gain as extra as ONE step (gain first per source type); the headings are split here for linking. (3) The wiki puts hit chance first; PoB multiplies it in at the end (AverageDamage = AverageHit x HitChance, CalcOffence.lua:3796). (4) PoB multiplies resistance, armour and damage-taken in one product (commutative), so only the flat damage-taken step, which PoB omits, changes a number. (5) Armour is evaluated on the average hit; the game rolls per hit.

## Hit chance

Rule: Attack hits only (spells and minion attacks skip it). Chance to hit = 1.25 x accuracy / (accuracy + (evasion/5)^0.9), clamped 5..100%; accuracy is checked a second time for the crit (a failed check downgrades the crit to a normal hit).

Wiki step: 1 Preventing the hit (evasion of attacks), again at the crit. Quote (Accuracy rev 1612031; Receiving damage rev 1702582 step 1; patch 3.7.0 (new formula, no 95% cap), 3.27.0 (minion attacks always hit)):

> Accuracy is compared against the target's evasion to determine whether an attack hits or misses ... accuracy is checked a second time when attack hits attempt to deal a critical strike.

PoB: Modules/CalcOffence.lua:2174-2249, 3146; Modules/CalcDefence.lua:58-64 - MATCH. Expected-value hit chance (rounded to whole %); crit chance is multiplied by it (CalcOffence.lua:3146). Enemy evasion and block come from config or the monster table.

Why it matters for building: Hit chance multiplies average damage and crit chance, so accuracy is worth nothing on spells but real on attacks vs evasive bosses.

## Flat damage

Rule: Base damage is the weapon (attacks) or the gem (spells); added damage is every other flat source. They are summed before any multiplier.

Wiki step: 3 Calculating unmitigated damage: flat damage (base + added). Quote (Damage rev 1551019 (same list: Receiving damage rev 1702582); no version noted):

> Base_Damage: The primary damage of the skill. This is either specified in the skill itself (and increases with the level of the skill gem), or is determined by the damage of your weapon (in the case of most Attacks).

PoB: Modules/CalcOffence.lua:3351-3356; Classes/Item.lua:2296-2320 - MATCH. Local weapon mods are folded into the weapon first and rounded per item (Item.lua:2308-2309). The effectiveness path to the gem data was not traced line by line.

Why it matters for building: Local flat on the weapon and added flat from elsewhere are two different scalings (weapon x base multiplier vs added x effectiveness).

## Damage effectiveness

Rule: Base and added flat damage are each scaled by the skill's effectiveness. Gain as extra is not scaled by it.

Wiki step: 3 Calculating unmitigated damage: flat damage (inside the same step). Quote (Damage effectiveness rev 1660645; patch 0.11.1):

> Damage effectiveness exists for both base damage and added damage. It does not directly affect Gain #% of X damage as extra Y damage, which is a type of conversion.

PoB: Modules/CalcOffence.lua:3351, 3355-3356 - MATCH. Multiplies only the non-weapon added flat damage (addedMult at 3354); weapon damage uses baseMultiplier instead.

Why it matters for building: Flat added damage is worth little on low-effectiveness skills; gain as extra bypasses effectiveness, so compare them per skill.

## Conversion

Rule: Fixed order Physical -> Lightning -> Cold -> Fire -> Chaos, no backward steps, chain conversion allowed. Converted-to above 100% is scaled to 100%: skill sources take precedence, gear and passive sources are scaled to the remainder. The wiki treats this and Gain as extra as ONE step.

Wiki step: 3 Calculating unmitigated damage: damage conversion (converted to). Quote (Damage conversion rev 1673519; no version noted for player rules):

> In this scaling, conversion modifiers from skills take precedence, and will not be scaled down if possible; afterwards, non-skill sources of conversion will be scaled down to the remaining percentage.

PoB: Modules/CalcOffence.lua:1939-1986, 70-90, 3410-3411 - MATCH. buildConversionTable: skill conversion first, skill >100% zeroes global, else global scaled to the remainder, each destination rounded to whole %. Recursion only from earlier types.

Why it matters for building: Conversion moves damage to a later type and takes its tags along; more than 100% converted-to silently loses the gear part first.

## Gain as extra

Rule: Per source type, gain-as-extra is computed before converted-to, so it reads the full source and is not reduced by conversion. 'Non-Chaos as Extra Chaos' applies once per type the damage passes through.

Wiki step: 3 Calculating unmitigated damage: damage conversion (same wiki step as Conversion). Quote (Damage conversion rev 1673519; no version noted):

> Gain as Extra is calculated on the source damage before it gets converted away by Converted to, and is thus not affected by it.

PoB: Modules/CalcOffence.lua:1953, 1977-1982, 83-87, 982-1031 - MATCH. Gain is taken from the source after its own inc/more (recursive call CalcOffence.lua:86) and never reduces the source. Gain-as-random is an averaged split, not a roll.

Why it matters for building: Gain as extra stacks with 100% conversion (source stays whole); it is not scaled by effectiveness, unlike added flat.

## Increased and reduced

Rule: All increased and reduced modifiers of the same type add together. Converted damage uses the modifiers of its original type and every type it passed through, once each.

Wiki step: 3 Calculating unmitigated damage: damage multipliers (increased / reduced). Quote (Receiving damage rev 1702582 (Damage conversion rev 1673519 agrees); no version noted):

> In this step, the calculation of converted damage includes modifiers for its original type, and any type it was converted through.

PoB: Modules/CalcOffence.lua:71, 86, 105-113 - MATCH. typeFlags accumulate through the conversion recursion and pick the inc mod names; inc is additive per bucket (112).

Why it matters for building: Increased is one additive pool (10% + 10% = 20%); converted damage keeps source-type inc, so physical inc still helps converted-to-fire damage.

## More and less

Rule: Each more/less source is its own multiplier; they multiply with each other and with the increased pool.

Wiki step: 3 Calculating unmitigated damage: damage multipliers (more / less). Quote (Receiving damage rev 1702582 (Damage rev 1551019: 110% * 110% = 121%); no version noted):

> All more and less modifiers are independent and therefore multiplicative.

PoB: Modules/CalcOffence.lua:113-132, 3440-3446 - MATCH. Type more is multiplicative (113); generic then type-specific Min/Max more/inc follow (131-132); allMult combines conversion, double damage, Ruthless Blow, Fist of War and warcry (3440-3446).

Why it matters for building: Increased vs more: 2 x 10% more = +21%, 2 x 10% increased = +20% in one pool; a 'more' line is worth more the more increased you already have.

## Critical strike

Rule: Crit chance = (base + additional) x (1 + increased) x more, rolled per skill use; a crit multiplies hit damage by the multiplier (player default 150%). DoT never crits. Luck re-rolls the chance.

Wiki step: 3 Calculating unmitigated damage: critical strikes. Quote (Critical strike rev 1698799; patch 3.6.0 (no crit chance caps), 2.2.0 (multiplier additive)):

> A critical strike is a type of hit that multiplies its damage by its critical strike multiplier.

PoB: Modules/CalcOffence.lua:3041-3270, 3796 - MATCH. Chance rounded to 0.01 (3105-3111), lucky (3118-3124), bifurcate (3126-3128), multiplied by AccuracyHitChance (3146); crit is just a multiplier before enemy mitigation (3449 vs 3489+).

Why it matters for building: Crit multiplier sits before enemy resist and armour, so crit damage meets higher armour reduction; ailments from DoT get only the +50% DoT crit multi, not the hit multiplier.

## Damage roll

Rule: Each damage type rolls its own range between minimum and maximum (both scaled by all earlier steps); lucky/unlucky rolls twice and keeps higher/lower. Does not touch crit or ailment rolls.

Wiki step: 3 Calculating unmitigated damage: rolling for damage (AFTER crit in the wiki). Quote (Receiving damage rev 1702582 (Damage rev 1551019 'Damage variance'); no version noted):

> The hit rolls for damage, in the range calculated by applying multipliers to the hit's minimum and maximum flat damage. Each damage type rolls its damage independently.

PoB: Modules/CalcOffence.lua:3465-3486, 3511 - MATCH. ORDER differs on paper only: PoB has no sequence for variance, it averages min/max (lucky/unlucky change the roll count) after the crit multiplier is in allMult. Armour and resistance act on the average (3511); min/max are display only.

Gap: [[Armour vs one configured hit]].

Why it matters for building: Averages hide per-hit variance: armour vs the average hit differs from armour vs real rolls (see the Armour step gap).

## Double damage

Rule: Double and triple damage apply after the other offensive modifiers and are a separate multiplier, not part of more.

Wiki step: 3 Calculating unmitigated damage: doubling / tripling. Quote (Receiving damage rev 1702582; no version noted):

> Modifiers that double or triple damage apply after other offensive damage modifiers.

PoB: Modules/CalcOffence.lua:3277-3298, 3440-3446 - MATCH. ScaledDamageEffect (chance computed 3281-3286) enters allMult; hits only.

Why it matters for building: Double damage does not scale with crit chance and is not available to DoT or ailments.

## Resistance, exposure and penetration

Rule: Elemental and chaos only. Exposure lowers the uncapped resistance; penetration is subtracted from the CAPPED value, with no floor for penetration. Hits only.

Wiki step: 6.4 Damage mitigation: resistance (penetration applied here). Quote (Resistance rev 1659347 (formula Resistance penetration rev 1673467; Exposure rev 1673498); patch 3.6.0 (cap 90), 3.16.0 (floor -200), 3.17.0 (reduction cap 100%)):

> Penetration applies to capped resistance value, so an enemy with 75% capped resistances against a hit with 30% penetration will take damage as if they had 45% resistances.

PoB: Modules/CalcOffence.lua:494-508, 3497-3503, 3555-3597; Modules/CalcPerform.lua:~3631 - MATCH. effectiveResist = (resist - pen) x useResChance, no floor; exposure enters as enemy resist mods; DoT cfg excludes penetration.

Why it matters for building: Penetration beats raw 'less resist' only while the enemy is at its cap; exposure and curses beat penetration vs low-resist enemies. See [[Exposure]].

## Armour against hits

Rule: Armour mitigates hits only, per damage type it applies to, after damage-taken-as and resistances, before damage-taken modifiers. Reduction = armour / (armour + 5 x damage).

Wiki step: 6.5 Damage mitigation: damage reduction (armour, physical hits). Quote (Armour rev 1625574; patch 3.16.0 (formula improved). The wiki prints no explicit current coefficient; 5 comes from PoB and the wiki rule of thumb):

> In the order of damage mitigation, damage reduction from armour is calculated after damage shifts and resistances (if applicable), but before modifiers to damage taken and spell suppression.

PoB: Modules/CalcOffence.lua:3510-3523; Modules/CalcDefence.lua:67-72 - DIFFERS. Same formula, but PoB feeds it the AVERAGE hit of that damage type in that pass (crit pass = crit average), not the rolled hit; result goes into the physical resist slot with the enemy physical reduction cap.

Gap: [[Armour vs one configured hit]].

Why it matters for building: Armour vs not-DoT: a big slow hit is reduced less than many small ones, so an average-based number can over- or understate by the hit-size spread.

## Damage taken

Rule: After mitigation: flat 'damage taken from hits' first, then the summed increased/reduced, then each more/less independently.

Wiki step: 7 Modifying damage taken (flat -> increased/reduced -> more/less). Quote (Receiving damage rev 1702582 (Damage taken rev 1673455 agrees); no version noted):

> Flat modifiers are applied first, then the sum of all increases/reductions, and lastly all more or less multipliers independently

PoB: Modules/CalcOffence.lua:3492-3493, 3562, 3572-3597 - OMITS. Inc/more taken match (effMult = (1+inc) x more x (1-resist), 3580-3597), but the flat step has no counterpart (grep FlatDamageTaken / DamageTakenFromHits in CalcOffence.lua: empty). Order inside the product is commutative, so only the flat part changes a number.

Gap: [[Flat damage taken from hits]].

Why it matters for building: Enemy 'increased damage taken' (Hexblast, Shock) is additive, not 'more'; a flat taken-from-hits mod is invisible to PoB's enemy side.

## Ailments from hits

Rule: Ignite, poison and bleed start from the hit's FLAT damage (after conversion), not from the mitigated hit; hit-only modifiers (crit multiplier, penetration, double damage, luck) do not apply. Shock, chill and freeze size from the post-mitigation hit.

Wiki step: 3 Calculating unmitigated damage: damaging ailments (separate base DPS calculation); non-damaging ailments after mitigation. Quote (Receiving damage rev 1702582 (Ignite rev 1598418, Poison rev 1700788, Bleeding rev 1700575); Ignite 3.17.0 (90%), Poison 3.15.0 (30%), Bleed 3.0.0 / 3.25.0):

> While damaging ailments are applied by hits, they have a separate base DPS calculation, starting from the flat damage of a hit. Hit-specific offensive modifiers will not apply to this calculation, nor will the defender's mitigation.

PoB: Modules/CalcOffence.lua:143-155, 4256-4345, 4520-4565, 4820-4840, 5076-5152 - DIFFERS. Source damage is unmitigated (matches the wiki), but PoB then applies enemy resist and taken-mods in the DoT multiplier (5192-5230), and ignite assumes the MIDDLE of the damage roll (50%) unless stack potential >1.

Gap: [[Ailments from hits source damage]].

Why it matters for building: A hit that kills nothing still ignites for full flat damage: ailment builds scale with flat damage and DoT multiplier, not crit multiplier or penetration.

## Damage over time

Rule: DoT does not hit: no evasion, armour, crit, luck, penetration or conversion at the source. The DoT multiplier is its own additive pool. Resistance and damage-taken apply when the damage is taken; base DPS snapshots.

Wiki step: Damage over time section (hits skip evasion, armour, ward, block). Quote (Damage over time rev 1702687 (Receiving damage rev 1702582 'Damage over time'); patch 3.0.0 (rework)):

> Damage over time does not hit. Because of this, damage over time cannot deal double damage or triple damage, or deal a critical strike.

PoB: Modules/CalcOffence.lua:4531, 4581-4583, 4832, 5149, 5725 - MATCH. DoT multi = 1 + (DotMultiplier + type multi)/100; resist without penetration; bleed uses only the enemy PhysicalDamageReduction. The receiving-side flat reduction on DoT is a separate question, see [[Receiving damage#Damage over time taken]].

Why it matters for building: Damage over time multiplier is a different pool from increased and more; hit crit multi never reaches DoT.

## Hit rate

Rule: DPS = average damage per hit x hits per second; speed buffs (attack/cast speed, Onslaught, frenzy charges) act here, not in the damage per hit.

Wiki step: Damage page toy formula with Hit_Rate (Damage rev 1551019; mechanics-researcher-damage-calc.md).

PoB: TotalDPS = AverageDamage x (HitSpeed or Speed) x dpsMultiplier x quantityMultiplier (Modules/CalcOffence.lua:3801); uses per second CalcOffence.lua:2275-2294 / 2473-2485; triggered skills use SkillTriggerRate (Modules/CalcTriggers.lua:799-822) - MATCH. Source: tasks/reports/027-evidence/pob-coverage-auditor-uptime.md.

Why it matters for building: A speed buff is worth its % only on hit DPS; DoT-only skills gain nothing from cast speed except via application rate. How often a buff is up is [[Chance on hit uptime]].

```interaction
id: damage-calculation
mechanic: "Order of operations for an outgoing hit and damage over time, in the wiki's order: hit chance, flat damage, conversion, increased and more, crit, roll, double damage, then enemy mitigation and ailments"
family: pipeline
target: enemy
pob:
  measured: partial
  how: "CalcOffence.lua calcDamage / buildConversionTable / hit and ailment sections; one wiki-order heading per step, each with file:line and MATCH / DIFFERS / OMITS"
  config: []
  unparsed: []
providers: []
uptime: {}
sources:
  - {"ref": "https://www.poewiki.net/wiki/Receiving_damage (rev 1702582)", "kind": "wiki", "patch": "3.29"}
  - {"ref": "https://www.poewiki.net/wiki/Damage_conversion (rev 1673519)", "kind": "wiki", "patch": "3.29"}
  - {"ref": "Modules/CalcOffence.lua, Modules/CalcDefence.lua (PoB 2.67.2)", "kind": "pob", "patch": "3.29"}
  - {"ref": "tasks/reports/027-evidence/mechanics-researcher-damage-calc.md; pob-coverage-auditor-calc-order.md", "kind": "discovery", "patch": "3.29"}
not_verified:
  - "Flat damage-taken step: no PoB counterpart found (grep empty); wiki mechanic only (mechanics-researcher-damage-calc.md open item 1)."
  - "Effectiveness path from gem data to MinBase/MaxBase not traced line by line (open item 2)."
  - "The wiki Armour page prints no explicit current coefficient (5); it comes from PoB CalcDefence.lua:71 and the wiki rule of thumb (open item 3)."
  - "Receiving damage has no version table: 'no version noted' is not 'never changed' (open item 4)."
  - "Exposure application in CalcPerform.lua (~3631) is approximate in the evidence."
steps:
  - {"id": "damage-calculation-1", "heading": "Hit chance", "wiki_order": 1, "pob_ref": "Modules/CalcOffence.lua:2174-2249, 3146", "pob_status": "match"}
  - {"id": "damage-calculation-2", "heading": "Flat damage", "wiki_order": 2, "pob_ref": "Modules/CalcOffence.lua:3351-3356", "pob_status": "match"}
  - {"id": "damage-calculation-3", "heading": "Damage effectiveness", "wiki_order": 3, "pob_ref": "Modules/CalcOffence.lua:3351, 3355-3356", "pob_status": "match"}
  - {"id": "damage-calculation-4", "heading": "Conversion", "wiki_order": 4, "pob_ref": "Modules/CalcOffence.lua:1939-1986, 70-90, 3410-3411", "pob_status": "match"}
  - {"id": "damage-calculation-5", "heading": "Gain as extra", "wiki_order": 5, "pob_ref": "Modules/CalcOffence.lua:1953, 1977-1982, 83-87, 982-1031", "pob_status": "match"}
  - {"id": "damage-calculation-6", "heading": "Increased and reduced", "wiki_order": 6, "pob_ref": "Modules/CalcOffence.lua:71, 86, 105-113", "pob_status": "match"}
  - {"id": "damage-calculation-7", "heading": "More and less", "wiki_order": 7, "pob_ref": "Modules/CalcOffence.lua:113-132, 3440-3446", "pob_status": "match"}
  - {"id": "damage-calculation-8", "heading": "Critical strike", "wiki_order": 8, "pob_ref": "Modules/CalcOffence.lua:3041-3270, 3796", "pob_status": "match"}
  - {"id": "damage-calculation-9", "heading": "Damage roll", "wiki_order": 9, "pob_ref": "Modules/CalcOffence.lua:3465-3486, 3511", "pob_status": "match"}
  - {"id": "damage-calculation-10", "heading": "Double damage", "wiki_order": 10, "pob_ref": "Modules/CalcOffence.lua:3277-3298, 3440-3446", "pob_status": "match"}
  - {"id": "damage-calculation-11", "heading": "Resistance, exposure and penetration", "wiki_order": 11, "pob_ref": "Modules/CalcOffence.lua:494-508, 3497-3503, 3555-3597", "pob_status": "match"}
  - {"id": "damage-calculation-12", "heading": "Armour against hits", "wiki_order": 12, "pob_ref": "Modules/CalcOffence.lua:3510-3523", "pob_status": "differs"}
  - {"id": "damage-calculation-13", "heading": "Damage taken", "wiki_order": 13, "pob_ref": "Modules/CalcOffence.lua:3492-3493, 3562, 3572-3597", "pob_status": "omits"}
  - {"id": "damage-calculation-14", "heading": "Ailments from hits", "wiki_order": 14, "pob_ref": "Modules/CalcOffence.lua:143-155, 4256-4345, 4520-4565, 4820-4840, 5076-5152", "pob_status": "differs"}
  - {"id": "damage-calculation-15", "heading": "Damage over time", "wiki_order": 15, "pob_ref": "Modules/CalcOffence.lua:4531, 4581-4583, 4832, 5149, 5725", "pob_status": "match"}
  - {"id": "damage-calculation-16", "heading": "Hit rate", "wiki_order": 16, "pob_ref": "Modules/CalcOffence.lua:3801, 2275-2294, 2473-2485; Modules/CalcTriggers.lua:799-822", "pob_status": "match"}
pipeline_step: [self]
```
