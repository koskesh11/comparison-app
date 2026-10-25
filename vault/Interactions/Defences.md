---
type: interaction
status: draft
pob_refs: ["EvadeChance", "BlockChance", "SpellBlockChance", "SuppressionChance", "ArmourReduction", "DamageReductionMax", "MaxResistCap", "AvoidChanceCap", "TotalEHP"]
source: "poewiki Defences 1546824, Evasion 1611557, Block 1648970, Spell suppression 1675604, Armour 1625574, Energy shield 1673450, Resistance 1659347, Damage reduction 1605942, Avoidance 1675590, Dodge 1595031, Recovery 1618351, Leech 1642429; PoB 2.67.2 CalcDefence.lua, Data.lua; evidence mechanics-researcher-receiving-defences.md, pob-coverage-auditor-calc-order.md"
last_confirmed_patch: "3.29.x"
---

This is the foundation for judging a defensive interaction by its numbers: every heading is one defence layer with its formula, cap and the PoB line behind it, so other notes can link e.g. [[Defences#Resistance caps]]. The order the layers act in is [[Receiving damage]]; the outgoing side is [[Damage calculation]]. Caps come from PoB's Data.lua and the wiki, never copied: ask PoB for the live values.

Order differences wiki vs PoB: the layers here have no order of their own; where PoB differs from the wiki in order (block last on the wiki vs independent factors in PoB, avoidance additive from 3.29.0 vs multiplicative in PoB, evasion entropy vs average) see [[Receiving damage]]. Effective HP has no wiki counterpart.

## Evasion

Rule: Chance to evade = 1 - accuracy x 1.25 / (accuracy + (evasion/5)^0.9), evade cap 95% (hit chance floor 5%). Attacks only, not spells or DoT. Evasion is a deterministic entropy counter shared by all attackers; a crit is evaded on a separate roll.

Wiki step: Defences: evasion. Quote (Evasion rev 1611557; patch 3.16.0 (formula improved, dodge removed), 3.7.0):

> If resulted entropy value is lower than 100 the hit counts as evade. When the value gets increased to 100 or greater, the check counts as a hit, and entropy value is subtracted by 100.

PoB: Modules/CalcDefence.lua:57-63, 1094-1107; Data.lua:247 - DIFFERS. Formula and 95 cap match; PoB uses a plain expected value, no entropy (grep 'entropy' in CalcDefence.lua: 0 hits).

Gap: [[Evasion entropy]].

Why it matters for building: Evasion is only as good as the enemy's accuracy; one-shot analysis differs from the average.

## Block chance

Rule: Random roll per hit (not entropy). Default max 75%, raisable to a hard cap of 90%. Prevents all damage unless 'damage taken from blocked hits' applies. Spell block and attack block have separate stats.

Wiki step: Defences: block. Quote (Block rev 1648970; patch 3.24.0 (max block cannot exceed 90%), 3.4.0, 3.25.0):

> Maximum block chance (for either attacks or spells) is 75% by default. This cap can be modified, up to a hard cap of 90%.

PoB: Modules/CalcDefence.lua:679-734; Data.lua:249; Data/Misc.lua:70 - MATCH. BlockChanceMax / SpellBlockChanceMax capped at BlockChanceCap 90; base 75.

Why it matters for building: Past 75% needs max-block investment; block does nothing against DoT. Order in [[Receiving damage#Block]].

## Spell suppression chance

Rule: Chance (stackable to 100%) to take 40% less damage from a spell hit. 'Prevent +#% of Suppressed Spell Damage' raises the 40%. Acrobatics converts suppression to spell dodge at 50% (dodge cap 75%).

Wiki step: Defences: spell suppression. Quote (Dodge rev 1595031; Spell suppression rev 1675604 (patch 3.16.0, 3.27.0: 50 -> 40%)):

> The only source of dodge is the Acrobatics keystone, which provides a chance to dodge spell hits from spell suppression modifiers.

PoB: Modules/CalcDefence.lua:1137-1189; Data.lua:248, 250, 251 - MATCH. SuppressionChanceCap 100, SuppressionEffect 40, DodgeChanceCap 75; Acrobatics via suppression/2 -> SpellDodgeChance (1143).

Why it matters for building: Over 100% chance is wasted; extra effect mods raise the 40% instead. Order in [[Receiving damage#Spell suppression]].

## Armour formula

Rule: Physical reduction = A / (A + 5 x D) with D the physical hit after shifts and resistances; a hit far above armour is never reduced by more than A/5. Never vs DoT.

Wiki step: Defences: armour. Quote (Armour rev 1625574; patch 3.16.0):

> When the damage of a hit significantly exceeds Armour, it will never prevent more damage than its value divided by 5

PoB: Modules/CalcDefence.lua:67-72, 2030; Data.lua:243 - DIFFERS. Same formula; D is the configured enemy hit, int-rounded (70-72), capped at DamageReductionMax 90.

Gap: [[Armour vs one configured hit]].

Why it matters for building: Armour is per-hit-size, not a flat percentage: see [[Receiving damage#Armour and damage reduction]].

## Energy shield

Rule: ES takes damage before life; recharge starts after 2 s without damage with delay 200/(100 + r) s; base recharge 33.3% per second; 50% chance to ignore stun while ES > 0.

Wiki step: Defences: energy shield. Quote (Energy shield rev 1673450; patch 3.16.0 (33%/s, was 20%), 3.5.0):

> If the character has any energy shield remaining when damage is taken, even damage from Labyrinth traps, that damage is inflicted on energy shield first.

PoB: Modules/CalcDefence.lua:322-341, 2325-2342 - MATCH. Bypass and pool order verified; the recharge numbers are wiki-only (PoB regen code was not read).

Why it matters for building: Recharge only helps between hits; see [[Receiving damage#Energy shield]] for the order.

## Resistance caps

Rule: Default max 75%, max-res mods up to a hard cap 90%, floor -200%; 'reduced resistances' effect capped 100%; physical has no resistance; applies to hits and DoT.

Wiki step: Defences: resistance. Quote (Resistance rev 1659347; patch 3.6.0, 3.16.0, 3.17.0):

> Resistances have a default maximum of 75%. [...] Maximum resistance can be increased with sources of +#% to Maximum [Type] Resistance(s), up to a hard limit of 90%.

PoB: Modules/CalcDefence.lua:580-630, 1966; Data.lua:245, 246 - MATCH. MaxResistCap 90, ResistFloor -200; DoT uses ResistOverTime.

Why it matters for building: Resist above the cap only counts as overcap buffer vs reduction effects; order in [[Receiving damage#Resistances]].

## Physical damage reduction cap

Rule: Total reduction (armour + additive extra) is clamped to 90 (min 0) after all modifiers, then Crushed / Overwhelm subtract: 100% -> 90, minus 15 -> 85, not 75.

Wiki step: Defences: damage reduction. Quote (Damage reduction rev 1605942; cargo maximum_physical_damage_reduction_% = 90; no version noted):

> if armour calculates 100% physical damage reduction against a certain hit, it will be capped to 90%. If the player is also debuffed for -15% by e.g. Penitent Mask's Crushed, the final reduction will be 85%, not 75%.

PoB: Modules/CalcDefence.lua:2036-2037; Data.lua:243; Data/Misc.lua:69 - MATCH. min(cap, armour + flat) then minus enemyOverwhelm, floored at 0; matches the 85 example.

Why it matters for building: Armour beyond the 90 cap is wasted, but Overwhelm bites into the capped value.

## Damage avoidance

Rule: 'Avoid X damage from hits' is a chance to reduce that damage to 0; hard cap 75%. Projectile avoidance prevents the projectile hit itself.

Wiki step: Defences: avoidance. Quote (Avoidance rev 1675590; patch 3.29.0 (avoid-all additive with avoid-type, cap bug fixed)):

> The chance to avoid damage from hits is hard capped at 75%.

PoB: Modules/CalcDefence.lua:1575-1585, 2829-2836; Data.lua:252 - DIFFERS. 75 cap matches; 3.29.0 additivity is not modelled (see [[Receiving damage#Immunity and avoidance]]). Projectile cap 75 is PoB-only.

Gap: [[Avoidance additive 3.29.0]].

Why it matters for building: Past 75% it is wasted; two different avoid lines add on the 3.29.0 wiki instead of multiplying.

## Ailment avoidance

Rule: 'Chance to avoid X' is a separate roll per ailment; 100% equals 'Cannot be X-ed' (existing stacks stay), unlike immunity, which removes them. Multiplicative with the attacker's chance to inflict. No cap below 100% is stated.

Wiki step: Defences: avoidance (ailments). Quote (Avoidance rev 1675590 (Ailment rev 1673310); no version noted for this paragraph):

> Stacking 100%+ chance to avoid X ailment is functionally identical to having the stat Cannot be X-ed, although the inverse is not true for stats such as the one found on Stormshroud.

PoB: Modules/CalcDefence.lua:1613-1624 - MATCH. AvoidChance floored at 100 minimum; the ailment threshold is a separate mechanic, see [[Enemy ailment threshold]].

Why it matters for building: Avoid chance and ailment threshold are two separate defences; 'cannot be' does not remove an already-applied ailment.

## Recovery and leech

Rule: Over-time recovery is capped per 33 ms frame at the recoverable max; a leech instance gives 10% of max per instance, 2% per second per instance, 20% per second total (ES 10% per second). Leech is based on damage dealt to the enemy.

Wiki step: Defences: recovery (Recovery, Leech pages). Quote (Leech rev 1642429; Recovery rev 1618351; no version noted):

> Leech is based on the damage taken by the enemy, not the amount of life removed.

PoB: Modules/CalcDefence.lua: regen / leech sections not read (EHP outputs 2904-2966) - OMITS. PoB code for recovery was not traced here; the EHP outputs contain no recovery at all (CalcDefence.lua:2904-2966).

Gap: [[EHP ignores recovery]].

Why it matters for building: Recovery speed and leech caps decide whether a deficit is survivable; see [[Receiving damage#Recovery]].

## Effective HP

Rule: PoB's TotalEHP repeats ONE configured enemy hit (summed over types, mitigated per type) until the pools run out, in raw-damage units. It is not a sequence of different hits and not worst-case; maximum hit per type is a separate output.

Wiki step: (no wiki page: PoB-only construct). Quote (none; PoB 2.67.2 only):

> (no wiki quote: EHP is PoB's own model, not a game mechanic)

PoB: Modules/CalcDefence.lua:2613-2784, 2904-2966, 3259-3350 - DIFFERS. numberOfHitsToDie iterates pool depletion; TotalEHP = TotalNumberOfHits x totalEnemyDamageIn (2952); enemyDamageType default 'Average' (1684); no regen, leech or flasks.

Gap: [[EHP ignores recovery]].

Why it matters for building: EHP is a comparison metric under the configured hit, not a survival guarantee; check it against the configured hit size and the recovery gap.

```interaction
id: defences
mechanic: "Per-layer formulas and caps of the defensive layers (evasion, block, suppression, armour, ES, resistance, damage reduction, avoidance, ailment avoidance, recovery) and PoB's Effective HP construct"
family: pipeline
target: self
pob:
  measured: partial
  how: "CalcDefence.lua hitChance / block / suppression / armour / avoidance sections and Data.lua cap constants (243-252); one heading per layer with file:line and MATCH / DIFFERS / OMITS"
  config: []
  unparsed: []
providers: []
uptime: {}
sources:
  - {"ref": "https://www.poewiki.net/wiki/Defences (rev 1546824)", "kind": "wiki", "patch": "3.29"}
  - {"ref": "https://www.poewiki.net/wiki/Avoidance (rev 1675590)", "kind": "wiki", "patch": "3.29"}
  - {"ref": "Modules/CalcDefence.lua, Modules/Data.lua (PoB 2.67.2)", "kind": "pob", "patch": "3.29"}
  - {"ref": "tasks/reports/027-evidence/mechanics-researcher-receiving-defences.md; pob-coverage-auditor-calc-order.md", "kind": "discovery", "patch": "3.29"}
not_verified:
  - "ES recharge numbers (delay 200/(100 + r), 33.3%/s) and leech caps (10% / 2% / 20%): wiki-only, PoB regen and leech code not read."
  - "Projectile-avoidance cap 75: PoB-only."
  - "Evasion entropy and the random start value: wiki-only; PoB uses the expected value."
  - "No cap on the product of damage-taken increases and mores is documented on the wiki."
  - "Effective HP is PoB's own construct: there is no wiki page to quote."
steps:
  - {"id": "defences-1", "heading": "Evasion", "wiki_order": 1, "pob_ref": "Modules/CalcDefence.lua:57-63, 1094-1107", "pob_status": "differs"}
  - {"id": "defences-2", "heading": "Block chance", "wiki_order": 2, "pob_ref": "Modules/CalcDefence.lua:679-734", "pob_status": "match"}
  - {"id": "defences-3", "heading": "Spell suppression chance", "wiki_order": 3, "pob_ref": "Modules/CalcDefence.lua:1137-1189", "pob_status": "match"}
  - {"id": "defences-4", "heading": "Armour formula", "wiki_order": 4, "pob_ref": "Modules/CalcDefence.lua:67-72, 2030", "pob_status": "differs"}
  - {"id": "defences-5", "heading": "Energy shield", "wiki_order": 5, "pob_ref": "Modules/CalcDefence.lua:322-341, 2325-2342", "pob_status": "match"}
  - {"id": "defences-6", "heading": "Resistance caps", "wiki_order": 6, "pob_ref": "Modules/CalcDefence.lua:580-630, 1966", "pob_status": "match"}
  - {"id": "defences-7", "heading": "Physical damage reduction cap", "wiki_order": 7, "pob_ref": "Modules/CalcDefence.lua:2036-2037", "pob_status": "match"}
  - {"id": "defences-8", "heading": "Damage avoidance", "wiki_order": 8, "pob_ref": "Modules/CalcDefence.lua:1575-1585, 2829-2836", "pob_status": "differs"}
  - {"id": "defences-9", "heading": "Ailment avoidance", "wiki_order": 9, "pob_ref": "Modules/CalcDefence.lua:1613-1624", "pob_status": "match"}
  - {"id": "defences-10", "heading": "Recovery and leech", "wiki_order": 10, "pob_ref": "Modules/CalcDefence.lua: regen / leech sections not read (EHP outputs 2904-2966)", "pob_status": "omits"}
  - {"id": "defences-11", "heading": "Effective HP", "wiki_order": 11, "pob_ref": "Modules/CalcDefence.lua:2613-2784, 2904-2966, 3259-3350", "pob_status": "differs"}
pipeline_step: [self]
```
