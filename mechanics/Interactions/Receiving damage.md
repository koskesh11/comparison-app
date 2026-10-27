---
type: interaction
status: draft
pob_refs: ["NotHitChance", "TakenHit", "TakenDotMult", "DamageTakenAs", "AvoidAllDamageFromHitsChance", "BlockChance", "SuppressionChance", "TotalEHP", "NumberOfDamagingHits"]
source: "poewiki Receiving damage rev 1702582, Damage taken as 1618416, Avoidance 1675590, Resistance 1659347, Armour 1625574, Damage reduction 1605942, Spell suppression 1675604, Block 1648970, Guard skill 1660806, Energy shield 1673450, Mana before Life 1700557, Damage over time 1702687, Recovery 1618351; PoB 2.67.2 CalcDefence.lua; evidence mechanics-researcher-receiving-defences.md, pob-coverage-auditor-calc-order.md"
last_confirmed_patch: "3.29.x"
---

This is the foundation for judging whether a defensive interaction works: every heading is one step of the wiki's incoming order, so other notes can link e.g. [[Receiving damage#Block]]. The wiki page has no version table and was edited live in 2026 (rev 1618349 on 2026-02-24 grouped suppression with the damage-taken modifiers, rev 1648064 on 2026-04-24 moved avoidance to step 6.3), so the order is the current text and not tied to a patch. Outgoing damage is [[Damage calculation]], per-layer formulas and caps are [[Defences]]. Wiki steps without their own heading (4 Cannot take damage, 8 Being stunned, 9 Combining damage, 11 Final damage taken) are wiki-only in the evidence; PoB code for them was not traced.

Order differences wiki vs PoB: (1) the wiki splits avoidance into four positions (prevention before the hit, damage avoidance after the hit and before resistance, suppression as a 'more/less' row, block last after stun and combining); PoB treats evade, dodge, avoid, suppression and block as independent expected-value multipliers (CalcDefence.lua:1689-1693, 2799-2836). The average is equal; what triggers (on-hit vs when-block effects, stun, recoup) is not. This last sentence is an inference from the code, not a wiki statement. (2) The 3.29.0 wiki makes avoid-all additive with avoid-type; PoB multiplies. (3) Armour is evaluated on the configured hit, not the hit that arrives. (4) 'Damage conversion' on the defender side is called 'damage taken as' and sits at step 5 (the wiki's offensive conversion is step 3).

## Preventing the hit

Rule: Only evasion of attacks, projectile avoidance and (Acrobatics) spell dodge stop the hit itself, so no on-hit or when-hit effects fire. Evasion is tested a second time against attack crits (a pass downgrades the crit to a normal hit).

Wiki step: 1 Preventing the hit; 2 Before being hit; 3 evasion of the crit. Quote (Receiving damage rev 1702582 (no version table; live-edited 2026); Dodge rev 1595031 (attack dodge removed 3.16.0)):

> These are the only defensive mechanics that prevent hits entirely. Other forms of mitigation cannot undo the hit, even if they reduce damage taken to 0.

PoB: Modules/CalcDefence.lua:1085-1107, 1182-1189, 1583, 1689-1693, 1701-1704 - DIFFERS. PoB multiplies evade, dodge, avoid-all and projectile avoidance into NotHitChance as plain expected-value percentages; no evasion entropy, so the long-run chance is the same but not the short run. EHPUnluckyWorstOf can square the chances (CalcDefence.lua:1699-1706). Wiki-internal inconsistency: it lists 'spell dodge' generally, the Dodge page says Acrobatics only.

Gap: [[Evasion entropy]].

Why it matters for building: Prevention keeps on-hit effects off; avoidance and block do not (the hit still landed).

## Damage taken as

Rule: Incoming type X is shifted to type Y before any mitigation. All shifts are computed simultaneously with no double shift, and only the final type's mitigation applies (physical taken as fire gets no armour). The wiki calls this 'damage taken as', not conversion; offensive conversion is [[Damage calculation#Conversion]].

Wiki step: 5 Damage taken as. Quote (Damage taken as rev 1618416 (same rule: Receiving damage rev 1702582 step 5)):

> The shifted portion of the damage does not retain its original damage type, meaning that it will not get mitigated twice; only the final damage type applies.

PoB: Modules/CalcDefence.lua:84-100, 166-176, 1851-1912 - MATCH. Shift tables (DamageTakenAs + DamageFromHitsTakenAs) are applied to the enemy hit before resist and armour; each resulting type gets its own mitigation. DoT has its own table without the FromHits mods (1858).

Why it matters for building: Taken-as vs conversion: it changes which resistance and which armour rule applies to the hit, so a cap on fire resist can matter for a physical hit.

## Immunity and avoidance

Rule: Immunities and 'cannot take X' zero the damage (6.1, 6.2). Damage avoidance ('avoid X damage from hits') reduces that damage to 0 AFTER the hit landed and BEFORE resistance; hard cap 75%.

Wiki step: 6.1 Cannot take X / 6.2 Immunities / 6.3 Damage avoidance. Quote (Avoidance rev 1675590; patch 3.29.0 (official notes: avoid-all additive with avoid-type damage; separate bug fix for some sources not capped at 75%; see [[Avoidance additive 3.29.0]])):

> Avoiding all damage from hits does not prevent or undo the hit; on-hit/when-hit effects will still occur for both the attacker and defender.

PoB: Modules/CalcDefence.lua:1031-1045, 1575-1585, 1689-1693, 2829-2836, 2935 - DIFFERS. PoB keeps AvoidAllDamageFromHitsChance as its own factor in NotHitChance while the per-type EHP path reads only Avoid<Type>DamageChance + projectile, so the two never add; the official 3.29.0 notes say avoid-all is additive with specific-type avoidance (no types or sources named). The 75 cap for projectile avoidance is PoB-only (the wiki states it for damage avoidance). Whether ModParser adds avoid-all into each type was not checked (ModParser.lua:386-387).

Gap: [[Avoidance additive 3.29.0]].

Why it matters for building: Avoid-all plus avoid-type: additive in the official 3.29.0 notes, multiplicative in PoB's not-hit path; whether PoB understates a build that stacks both depends on how EHP combines the two paths (unverified).

## Resistances

Rule: Fire/cold/lightning/chaos only: damage x (1 - resist). Default max 75%, hard cap 90%, floor -200%; penetration subtracts from the capped value. Applies to hits and DoT.

Wiki step: 6.4 Resistance (attacker penetration applied here). Quote (Resistance rev 1659347; patch 3.6.0 (cap 90), 3.16.0 (floor -200), 3.17.0 (reduction cap 100%)):

> Resistances have a default maximum of 75%. [...] Maximum resistance can be increased with sources of +#% to Maximum [Type] Resistance(s), up to a hard limit of 90%.

PoB: Modules/CalcDefence.lua:580-630, 1747-1752, 2005-2023 - MATCH. resMult = 1 - (resist - enemyPen)/100; enemy pen comes from config enemy<Type>Pen; hit resist (ResistWhenHit) and DoT resist (ResistOverTime) can differ.

Map modifiers: [[Map modifiers]] lower the player's maximum resistances at this step.

Why it matters for building: Resistance comes before armour: armour sees the resisted damage (CalcDefence.lua:2030). Caps live in [[Defences#Resistance caps]].

## Armour and damage reduction

Rule: Armour reduction is calculated on the hit after shifts and resistances; extra damage reduction adds to it; per damage type; the sum is capped at 90%, then Overwhelm-type effects subtract.

Wiki step: 6.5 Damage reduction (armour for physical + additive extra DR). Quote (Armour rev 1625574 (Damage reduction rev 1605942); patch 3.16.0):

> In the order of damage mitigation, damage reduction from armour is calculated after damage shifts and resistances (if applicable), but before modifiers to damage taken and spell suppression.

PoB: Modules/CalcDefence.lua:1535-1536, 2011-2037 - DIFFERS. Formula matches (armour/(armour + 5 x damage)), but 'damage' is the single CONFIGURED enemy hit per type (config or boss preset, crit averaged in, 1735-1822), not the real hit distribution; EHP assumes that one size repeatedly.

Gap: [[Armour vs one configured hit]].

Why it matters for building: Armour is only as good as the hit size configured: vs many small hits it is far better than the EHP number shows, vs one huge hit far worse. Formula in [[Defences#Armour formula]].

## Damage taken modifiers

Rule: Order inside: (1) flat 'damage taken from hits', (2) the additive increased/reduced sum, (3) each more/less independently. The wiki documents no cap on this product.

Wiki step: 7 Modifying damage taken. Quote (Receiving damage rev 1702582 (no version table; live-edited 2026) (suppression grouping edit rev 1618349, 2026-02-24)):

> Flat modifiers are applied first, then the sum of all increases/reductions, and lastly all more or less multipliers independently

PoB: Modules/CalcDefence.lua:1905-1960, 2009, 2102-2111 - MATCH. TakenHit = max(damage x baseMult + takenFlat, 0) x takenMult x spellSuppressMult (+ impale); flat taken is read at 2009. The offensive-side counterpart (enemy flat taken) is the OMITS in [[Damage calculation#Damage taken]].

Map modifiers: [[Map modifiers]] raise what is taken here through monster damage, curses on the player and Rust.

Why it matters for building: Reduced damage taken is additive across sources, 'less' is multiplicative: stack different kinds.

## Spell suppression

Rule: Per spell hit, chance to take 40% less damage from the hit and from ailments it inflicts. Applied after resistance and damage reduction, before stun and block.

Wiki step: 7 Modifying damage taken (suppression is a 'more/less' row of step 7). Quote (Spell suppression rev 1675604; patch 3.27.0 (50% -> 40%), 3.19.0, 3.16.0 (introduced)):

> Spell suppression occurs toward the end of mitigation, after resistances and damage reduction, but before stun and block.

PoB: Modules/CalcDefence.lua:1137-1178, 2072, 2105, 2816-2825 - DIFFERS. Effect size and order-independent multiplication match. The wiki says suppression also cuts the DPS of ailments the suppressed spell inflicted; PoB's DoT multiplier (CalcDefence.lua:1971) has no suppression factor.

Gap: [[Suppression on ailments]].

Why it matters for building: Suppression is a flat 40% off per suppressed hit, not avoidance: the hit lands, on-hit effects still fire. Chance and effect in [[Defences#Spell suppression chance]].

## Block

Rule: Block rolls AFTER all mitigation and damage-taken modifiers, preventing all damage (or all but 'damage taken from blocked hits' %). Hits only, never DoT. 'When you block' effects fire before the damage applies.

Wiki step: 10 Blocking the damage (after stun and combining damage). Quote (Receiving damage rev 1702582 (no version table; live-edited 2026); Block rev 1648970 (patch 3.24.0, 3.25.0)):

> Block or spell block rolls to prevent all damage, or a percentage of damage with modifiers like Glancing Blows.

PoB: Modules/CalcDefence.lua:679-785, 2799 - DIFFERS. ORDER differs: PoB multiplies every damage type by blockEffect = 1 - BlockChance x BlockEffect/100 as an independent expected-value factor; same average damage, but the wiki puts block last, so block never reduces what stun or recoup see.

Why it matters for building: Block removes the whole hit after armour and resist were already applied; it matters for on-hit triggers and recoup, not just the damage number. Chance and caps in [[Defences#Block chance]].

## Guard and Aegis

Rule: Allies, Frost Shield, Aegis and Guard buffs each take their share of the remaining damage before your pools; multiplicative, not additive. Non-Vaal Guards share a cooldown.

Wiki step: 12.1 Applying damage: other entities / effects. Quote (Receiving damage rev 1702582 (no version table; live-edited 2026); Guard skill rev 1660806 (patch 3.7.0)):

> Buffs that intercept a percentage of damage, such as most Guard skills.

PoB: Modules/CalcDefence.lua:224-243, 266-310, 2423-2453 - DIFFERS. Pool ORDER matches (allies, aegis, guard, shared guard, ward). But guard is a static absorb pool: no duration, no cooldown, always full.

Gap: [[Guard absorb static pool]].

Why it matters for building: A guard skill's EHP is a snapshot of a full buff; fights longer than its duration or cooldown are overstated.

## Energy shield

Rule: ES absorbs before life (or mana with Eldritch Battery). Chaos bypasses ES by default; the other mitigation steps act on the damage before it reaches ES.

Wiki step: 12.2b Energy shield (before the resource it protects). Quote (Receiving damage rev 1702582 (no version table; live-edited 2026); Energy shield rev 1673450 (patch 3.16.0, 3.5.0)):

> Damage is taken from energy shield before the resource that it protects (life by default, or mana if using Eldritch Battery).

PoB: Modules/CalcDefence.lua:322-341, 2325-2342 - MATCH. ES absorbs (1 - bypass) of the remaining damage; chaos bypass comes from mods (ChaosNotBypassEnergyShield), not hard-coded.

Why it matters for building: ES is not 'extra life' vs chaos unless the bypass is removed; recharge numbers are in [[Defences#Energy shield]].

## Mana before life

Rule: A percentage of the remaining damage (after ES) is removed from mana (Mind over Matter, Ivory Tower); capped at 100%. Applies to DoT.

Wiki step: 12.2c Mana before life. Quote (Receiving damage rev 1702582 (no version table; live-edited 2026); Mana before Life rev 1700557 (3.19.0: 30 -> 40%; 3.0.0: DoT)):

> #% of the remaining damage is removed from mana, if granted by an effect such as Mind over Matter or The Ivory Tower.

PoB: Modules/CalcDefence.lua:343-347, 2346-2420 - MATCH. MoM after ES (343-347), min(sum, 100) (2350, 2391), shared pool plus per-type DamageTakenFromManaBeforeLife.

Why it matters for building: Mana is a second HP pool but it also pays skill costs: a mana-margin trade-off, not free EHP.

## Life

Rule: Whatever remains is removed from life; at 0 you die. Life-loss prevention (Petrified Blood, Progenesis) acts on the life part only and is multiplicative between effects.

Wiki step: 12.2d Life (and 12.2e life-loss prevention). Quote (Receiving damage rev 1702582 (no version table; live-edited 2026)):

> The remaining damage is removed from Life. Life does not protect any other resource. If all Life is removed, you die.

PoB: Modules/CalcDefence.lua:~245, ~350-400 - MATCH. calcLifeHitPoolWithLossPrevention handles LifeLossBelowHalfPrevented; pool figures use LifeRecoverable. Line numbers marked ~ were read approximately in the evidence.

Why it matters for building: Prevention pushes part of the loss to later, which only helps if there is time to recover.

## Damage over time taken

Rule: DoT takes resistance, additive damage reduction, taken inc/more, then MoM, ES, life. It skips evasion, armour, ward, block and suppression of the hit.

Wiki step: Damage over time section. Quote (Receiving damage rev 1702582 (no version table; live-edited 2026); Damage over time rev 1702687 (3.0.0)):

> Damage over Time generally follows the same principle, however this damage source doesn't hit, which means that it ignores evasion, armour, ward, and other mechanics limited to hits.

PoB: Modules/CalcDefence.lua:1858, 1956-1972, 3373 - DIFFERS. TakenDotMult = (1 - resistOverTime) x (1 - BaseDR) x (1 + inc) x more. PoB applies the flat Base<Type>DamageReduction to DoT (1965); the wiki says damage reduction can mitigate DoT but only 'gained from armour against hits', so this is unverified against the game.

Gap: [[DoT flat damage reduction]].

Why it matters for building: Armour does nothing vs DoT; flat damage reduction may or may not, so do not count DoT EHP from armour mods.

## Recovery

Rule: Over-time recovery and loss are separate events per 33 ms server frame; recovery is calculated first, then DoT loss. Leech, regeneration and ES recharge are recovery, not mitigation.

Wiki step: Recovery page (not in the order list). Quote (Recovery rev 1618351; Leech rev 1642429; no version noted):

> When recovery and loss occur at the same time, over time, recovery is calculated first.

PoB: Modules/CalcDefence.lua:2904-2966 (EHP outputs contain no recovery) - OMITS. TotalEHP and NumberOfDamagingHits ignore regeneration, leech, flasks and recovery speed (gain-on-block / suppress is included, 2804-2837).

Gap: [[EHP ignores recovery]].

Map modifiers: [[Map modifiers]] cut recovery here (Smothering, Stasis).

Why it matters for building: Two builds with equal EHP differ hugely if one out-recovers DoT; judge deficits by duration, not by pool size.

```interaction
id: receiving-damage
mechanic: "Order in which an incoming hit or damage over time is mitigated and applied, as the wiki lists it: prevention, damage taken as, avoidance, resistance, armour, damage-taken modifiers, suppression, block, guard, ES, mana, life"
family: pipeline
target: self
pob:
  measured: partial
  how: "CalcDefence.lua: calcs.reducePoolsByDamage (pool order 190-345), NotHitChance (1689-1693), TakenHit / TakenDotMult (1956-2111), EHP (2613-2966); one wiki-order heading per step with file:line and MATCH / DIFFERS / OMITS"
  config: []
  unparsed: []
providers: []
uptime: {}
sources:
  - {"ref": "https://www.poewiki.net/wiki/Receiving_damage (rev 1702582)", "kind": "wiki", "patch": "3.29"}
  - {"ref": "https://www.poewiki.net/wiki/Avoidance (rev 1675590)", "kind": "wiki", "patch": "3.29"}
  - {"ref": "Modules/CalcDefence.lua (PoB 2.67.2)", "kind": "pob", "patch": "3.29"}
  - {"ref": "tasks/reports/027-evidence/mechanics-researcher-receiving-defences.md; pob-coverage-auditor-calc-order.md", "kind": "discovery", "patch": "3.29"}
not_verified:
  - "Order steps 4 (Cannot take damage) and 9 (Combining damage): wiki-only, PoB code not traced."
  - "Sacrifice of Blood's Blood Barrier: wiki-only; not found in the CalcDefence.lua pool order."
  - "Projectile-avoidance cap 75: PoB-only; the wiki states the cap for damage avoidance only."
  - "Whether ModParser adds avoid-all into each type (ModParser.lua:386-387) was not checked."
  - "Spell suppression cutting spell-inflicted ailment DPS: wiki-only; PoB DoT multiplier has no suppression term."
  - "The wiki order is a live-edited community page citing 2013-2022 forum posts; no official 3.29 patch note was checked."
  - "Whether PoB's flat damage reduction on DoT matches the game is unverified."
steps:
  - {"id": "receiving-damage-1", "heading": "Preventing the hit", "wiki_order": 1, "pob_ref": "Modules/CalcDefence.lua:1085-1107, 1182-1189, 1583, 1689-1693, 1701-1704", "pob_status": "differs"}
  - {"id": "receiving-damage-2", "heading": "Damage taken as", "wiki_order": 2, "pob_ref": "Modules/CalcDefence.lua:84-100, 166-176, 1851-1912", "pob_status": "match"}
  - {"id": "receiving-damage-3", "heading": "Immunity and avoidance", "wiki_order": 3, "pob_ref": "Modules/CalcDefence.lua:1031-1045, 1575-1585, 1689-1693, 2829-2836, 2935", "pob_status": "differs"}
  - {"id": "receiving-damage-4", "heading": "Resistances", "wiki_order": 4, "pob_ref": "Modules/CalcDefence.lua:580-630, 1747-1752, 2005-2023", "pob_status": "match"}
  - {"id": "receiving-damage-5", "heading": "Armour and damage reduction", "wiki_order": 5, "pob_ref": "Modules/CalcDefence.lua:1535-1536, 2011-2037", "pob_status": "differs"}
  - {"id": "receiving-damage-6", "heading": "Damage taken modifiers", "wiki_order": 6, "pob_ref": "Modules/CalcDefence.lua:1905-1960, 2009, 2102-2111", "pob_status": "match"}
  - {"id": "receiving-damage-7", "heading": "Spell suppression", "wiki_order": 7, "pob_ref": "Modules/CalcDefence.lua:1137-1178, 2072, 2105, 2816-2825", "pob_status": "differs"}
  - {"id": "receiving-damage-8", "heading": "Block", "wiki_order": 8, "pob_ref": "Modules/CalcDefence.lua:679-785, 2799", "pob_status": "differs"}
  - {"id": "receiving-damage-9", "heading": "Guard and Aegis", "wiki_order": 9, "pob_ref": "Modules/CalcDefence.lua:224-243, 266-310, 2423-2453", "pob_status": "differs"}
  - {"id": "receiving-damage-10", "heading": "Energy shield", "wiki_order": 10, "pob_ref": "Modules/CalcDefence.lua:322-341, 2325-2342", "pob_status": "match"}
  - {"id": "receiving-damage-11", "heading": "Mana before life", "wiki_order": 11, "pob_ref": "Modules/CalcDefence.lua:343-347, 2346-2420", "pob_status": "match"}
  - {"id": "receiving-damage-12", "heading": "Life", "wiki_order": 12, "pob_ref": "Modules/CalcDefence.lua:~245, ~350-400", "pob_status": "match"}
  - {"id": "receiving-damage-13", "heading": "Damage over time taken", "wiki_order": 13, "pob_ref": "Modules/CalcDefence.lua:1858, 1956-1972, 3373", "pob_status": "differs"}
  - {"id": "receiving-damage-14", "heading": "Recovery", "wiki_order": 14, "pob_ref": "Modules/CalcDefence.lua:2904-2966 (EHP outputs contain no recovery)", "pob_status": "omits"}
pipeline_step: [self]
```
