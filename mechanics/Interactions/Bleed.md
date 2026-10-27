---
type: interaction
status: draft
pob_refs: [BleedChanceOnHit, BleedChanceOnCrit, BleedStacksMax, BleedStackPotential, BleedRollAverage, BleedDuration, BleedDPS, BaseBleedDPS, BleedFaster, CannotBleed, conditionEnemyMoving, conditionEnemyBleeding, overrideBleedStackPotential, multiplierBleedsOnEnemy, multiplierRuptureStacks, NoExtraBleedDamageToMovingEnemy, ailmentMode]
source: "poewiki Bleeding rev 1700575 (2026-08-11), Ailment rev 1673310, Version 3.25.0 rev 1698361 (fetched 2026-10-25); PoB 2.67.2 CalcOffence.lua / CalcSetup.lua / Data.lua / ModParser.lua / ConfigOptions.lua / Data/ModCache.lua; PoB Data/Uniques, TreeData/3_29/tree.lua, Data/Skills/sup_str.lua, sup_dex.lua"
last_confirmed_patch: "3.29.x"
---

Bleed is a physical damage-over-time ailment from ATTACK hits only (wiki: there is no global chance to bleed and no spell bleed). It deals 70% of the hit's flat physical damage per second for 5 s while the target stands still, and three times that while the target moves or the bleed is Aggravated; only the strongest bleed deals damage unless Crimson Dance (8 bleeds at half damage). Armour does not reduce it. PoB calculates expected stacks and DPS, assuming a STATIONARY enemy unless you tick it; it has no Aggravate mechanic at all. Related: [[Ignite]], [[Poison]], [[Impale]] (stacks and bleed interplay), [[Chance on hit uptime]] (not for the bleed DPS), [[Fight length]].

Pipeline: [[Damage calculation#Ailments from hits]] and [[Damage calculation#Damage over time]] - bleed starts from the unmitigated flat physical damage and ignores armour, so it works against high-armour bosses for attack builds with flat physical damage and DoT multiplier, and does not for spell builds.

```interaction
id: bleed
mechanic: "Attack hits with a chance to bleed inflict physical damage over time: 70% of the hit's flat physical damage per second for 5 s (x3 while the target moves or the bleed is Aggravated); only the strongest bleed deals damage unless Crimson Dance (8, at 35% each); not reduced by armour; attacks only, no global or spell chance to bleed"
family: ailment
target: enemy
related: [ignite, poison, impale, chance-on-hit-uptime, fight-length]
pipeline_step: ["Damage calculation#Ailments from hits", "Damage calculation#Damage over time"]
pipeline_why: "Bleed is a separate base DPS from the hit's flat physical damage (after conversion, before hit modifiers); armour never applies, only physical damage reduction and damage taken; it scales with the DoT multiplier pool, and the target's movement triples it, which is a scenario input not a build stat"
pob:
  measured: partial
  how: "needs an attack with physical damage (skillFlags.attack, CannotBleed) CalcOffence.lua:4217-4222; chance on hit/crit (crit is NOT 100%); expected stacks = hit chance x bleed chance x dpsMultiplier x duration x hit rate (x active totems) CalcOffence.lua:4444-4458; maxStacks = BleedStacksMax, base 1 (CalcSetup.lua:51), Crimson Dance 8 (ModParser.lua:2331-2334); duration 5 s (Data.lua:262-263) x duration mods / bleed-faster CalcOffence.lua:4436-4441; roll average 50% unless stack potential > 1 CalcOffence.lua:4488-4495; base 70% (Data.lua:262; skill override bleedBasePercent) CalcOffence.lua:4568-4572; enemy physical damage reduction and taken mods (no armour) CalcOffence.lua:4581-4586; 'moving' +200% more bleed damage only when the enemy has Condition Moving (CalcSetup.lua:639; default false); BleedDPS in TotalDotDPS then CombinedDPS CalcOffence.lua:6252-6256, capped Data.lua:261. NOT computed: Aggravate Bleeding (no mechanic; the 'chance to Aggravate' mods are unparsed, Data/ModCache.lua:3601,5136,6290,7227), how often the target moves"
  config:
    - {var: conditionEnemyMoving, default: false, ref: "Modules/ConfigOptions.lua:1797 (shown only with a bleed chance; x3 bleed damage; also what Aggravate would be worth)", class: b}
    - {var: conditionEnemyBleeding, default: false, ref: "Modules/ConfigOptions.lua:1812 (for 'against Bleeding Enemies' payoffs, not the bleed DPS)", class: b}
    - {var: overrideBleedStackPotential, default: 0, ref: "Modules/ConfigOptions.lua:1815 (replaces the computed stack potential)", class: c}
    - {var: multiplierBleedsOnEnemy, default: 0, ref: "Modules/ConfigOptions.lua:1657 (only with Crimson Dance; sets the current bleed count)", class: c}
    - {var: multiplierRuptureStacks, default: 0, ref: "Modules/ConfigOptions.lua:1821 (only with Rupture Support; 4 stacks of more bleed damage, 3 s)", class: c}
    - {var: conditionSingleBleed, default: false, ref: "Modules/ConfigOptions.lua:1818 (Blood Sap Tincture: single bleed)", class: c}
    - {var: ailmentMode, default: "AVERAGE", ref: "Modules/ConfigOptions.lua:210", class: b}
  unparsed:
    - "Bloodletting (node 26294): 10% chance to Aggravate Bleeding on targets you Hit with Attacks: Data/ModCache.lua:3601 (empty parse)"
    - "Gladiator (Ascendant, node 34774): 25% chance to Aggravate Bleeding on targets you Hit with Attacks: Data/ModCache.lua:7228 (empty parse; the combined Gladiator lines 7229-7231 are also not parsed into mods)"
model: null
providers:
  - {kind: support, name: "Chance to Bleed Support", slot: any, role: applies, target: enemy, text: "25% chance to cause Bleeding with Attacks (bleed_on_hit_with_attacks_%); more Damage with Bleeding (10% at L1 in 3.25.0); attack skills only", source: "Data/Skills/sup_str.lua:1223-1244; wiki Version 3.25.0 rev 1698361", pob: full}
  - {kind: support, name: "Rupture Support", slot: any, role: scales, target: enemy, text: "Critical Strikes which inflict Bleeding also inflict Rupture (more bleed damage, faster bleeds, 3 s, up to 4 stacks)", source: "Data/Skills/sup_dex.lua:3575; Modules/ModParser.lua:2643; Modules/ConfigOptions.lua:1821; wiki Version 3.25.0", pob: config}
  - {kind: unique, name: "Haemophilia", slot: Gloves, role: applies, target: enemy, text: "Attacks have 25% chance to cause Bleeding", source: "Data/Uniques/gloves.lua:572", pob: full}
  - {kind: unique, name: "Jack, the Axe", slot: Axe, role: applies, target: enemy, text: "25% chance to cause Bleeding on Hit (local to the weapon); variant 2 +(25-35)% to Damage over Time Multiplier for Bleeding from Hits with this Weapon", source: "Data/Uniques/axe.lua:96-97", pob: full}
  - {kind: unique, name: "The Blood Reaper", slot: Axe, role: applies, target: enemy, text: "50% chance to cause Bleeding on Hit", source: "Data/Uniques/axe.lua:235", pob: full}
  - {kind: unique, name: "Replica Bloodplay", slot: Dagger, role: applies, target: enemy, text: "30% chance to cause Bleeding on Hit", source: "Data/Uniques/dagger.lua:62", pob: full}
  - {kind: unique, name: "Voidheart", slot: Ring, role: applies, target: enemy, text: "Melee Attacks cause Bleeding (variant 1) / (30-50)% chance to cause Bleeding (variant 2)", source: "Data/Uniques/ring.lua:160-161", pob: full, variant: "variants 1 and 2"}
  - {kind: unique, name: "Farrul's Pounce", slot: Gloves, role: applies, target: enemy, text: "Attacks always inflict Bleeding while you have Cat's Stealth", source: "Data/Uniques/gloves.lua:543", pob: partial}
  - {kind: unique, name: "Usurper's Penance", slot: Helmet, role: applies, target: enemy, text: "Attacks have 15% chance to cause Bleeding; +4% to Damage over Time Multiplier for Bleeding per Frenzy Charge; Bleeding you inflict deals Damage 4% faster per Frenzy Charge", source: "Data/Uniques/helmet.lua:148-151", pob: full}
  - {kind: keystone, name: "Crimson Dance", slot: tree, role: scales, target: enemy, text: "You can inflict Bleeding on an Enemy up to 8 times; your Bleeding does not deal extra Damage while the Enemy is moving and cannot be Aggravated; 50% less Damage with Bleeding (wiki: 35% of the hit per stack, 280% extra at 8 stacks)", source: "TreeData/3_29/tree.lua:43772-43776 (node 17818); Modules/ModParser.lua:2326-2327,2331-2334; Data/ModCache.lua:22782", pob: full}
  - {kind: notable, name: "Bloodletting", slot: tree, role: scales, target: enemy, text: "10% chance to Aggravate Bleeding on targets you Hit with Attacks (3.25.0, replaced 40% increased Attack Damage against Bleeding Enemies); Aggravated bleeding always deals damage as though the target moves", source: "TreeData/3_29/tree.lua:41619 (node 26294); wiki Version 3.25.0", pob: none}
  - {kind: ascendancy, name: "Gladiator (Ascendant)", slot: tree, role: scales, target: enemy, text: "25% chance to Aggravate Bleeding on targets you Hit with Attacks; Gain 50% Chance to Block from Equipped Shield instead of the Shield's value; Inherent Bonuses from Dual Wielding are doubled", source: "TreeData/3_29/tree.lua:18346-18352 (node 34774); wiki Version 3.25.0", pob: none}
makes_redundant: []
conflicts:
  - {with: "Crimson Dance vs Aggravate", effect: "Crimson Dance's bleeds never deal extra moving damage and cannot be Aggravated, so Bloodletting / Gladiator / Jagged Technique do nothing for it", source: "TreeData/3_29/tree.lua:43772-43776; wiki Bleeding rev 1700575"}
  - {with: "Bloodlust (support)", effect: "increases melee damage against bleeding enemies but prevents the supported skill from causing bleeding", source: "wiki Bleeding rev 1700575 'Other'"}
  - {with: "Elemental Overload + Perfect Agony (keystones)", effect: "wiki: the combination prevents damaging ailments from hits entirely", source: "wiki Bleeding rev 1700575; PoB Modules/ModParser.lua:2237"}
conditions:
  - {text: "wiki quote: \"Potential damage from one bleed application is based on the base physical damage of attack that caused it: 70% per second if the target is standing still (reduced to 10% if an enemy monster applied it). If the target is moving or are affected by Aggravated Bleeding, bleeding deals additional damage equal to twice the base, for a total of 3 times the base damage (210% per second)\"", source: "wiki Bleeding rev 1700575; PoB Modules/Data.lua:262, Modules/CalcSetup.lua:639"}
  - {text: "wiki quote: \"The base duration of bleed is 5 seconds.\" and \"By default, only the strongest (the highest damage-per-second) bleed application will actually deal damage at any given time.\"", source: "wiki Bleeding rev 1700575; PoB Modules/Data.lua:263"}
  - {text: "wiki quote: \"Bleed damage is not reduced by armour, but will be reduced by any other sources of physical mitigation, such as endurance charges or Immortal Call.\" PoB uses the enemy PhysicalDamageReduction mod, not armour", source: "wiki Bleeding rev 1700575; PoB Modules/CalcOffence.lua:4581-4586"}
  - {text: "wiki quote: \"Critical strikes that deal physical damage will not automatically cause bleeding. All physical damage hits must successfully roll chance to bleed to cause bleeding.\" Crit bleeds gain the +50% DoT multiplier", source: "wiki Bleeding rev 1700575; PoB Modules/CalcSetup.lua:604"}
  - {text: "Aggravate (added 3.25.0): all bleeds on the target are aggravated together; the chance is rolled once before the bleed, so a hit that bleeds and aggravates at once does not aggravate its own bleed; the extra damage does not stack with the moving bonus", source: "wiki Bleeding rev 1700575 'Aggravate'; wiki Version 3.25.0 rev 1698361"}
uptime:
  Mapping:
    value: pob
    config: {conditionEnemyMoving: "scenario input (class b): PoB default is a stationary target (70%); pack monsters are not measured here, do not assume x3", conditionEnemyBleeding: "model: box state by the uptime rule (user rule 2026-10-25: u >= 80% ticked, no notice; 50-80% ticked + user informed with u; < 50% unticked + warning with u) (see chance-on-hit-uptime)"}
    reasoning: "PoB expects bleed from chance, hit rate and 5 s duration (CalcOffence.lua:4444-4458) so packs with fast attacks keep it up; how long a pack stands still is not sourced; short pack life cuts the 5 s window (see [[Fight length]])"
    source: "Modules/CalcOffence.lua:4444-4458,6252-6256; Modules/ConfigOptions.lua:1797; vault Interactions/Fight length"
  Pinnacle Boss:
    value: pob
    config: {conditionEnemyMoving: "scenario input: stationary phases deal 70%, moving or aggravated 210%; no source for boss movement time was found", conditionEnemyBleeding: "model as above"}
    reasoning: "one target, so stacks = chance x attack rate x 5 s; PoB's default is the lower (stationary) value; Aggravate would lift it toward x3 but PoB cannot count it, so an aggravate build is under-reported by PoB"
    source: "Modules/CalcSetup.lua:639; Data/ModCache.lua:3601"
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Bleeding (rev 1700575, 2026-08-11)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Ailment (rev 1673310, 2026-07-11)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Version_3.25.0 (rev 1698361): Aggravate, Rupture, Bloodletting, Gladiator, Crimson Dance neighbours", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcOffence.lua:4217-4222,4432-4458,4488-4495,4568-4586,6252-6256; Modules/CalcSetup.lua:51,604,639; Modules/Data.lua:261-263; Modules/ConfigOptions.lua:210,1657,1797,1812,1815,1818,1821; Modules/ModParser.lua:2237,2326-2334,2643; Data/ModCache.lua:3601,5136,6290,7228-7231,14391,22782 (PoB 2.67.2)", kind: pob, patch: "3.29"}
not_verified:
  - "how often pack monsters and each pinnacle boss are moving; nothing in PoB data or on the wiki gives a movement fraction, so the 70% / 210% choice is the user's scenario input"
  - "the wiki Bleeding page says there is no global chance to bleed or spell bleed; 3.25.0 and 3.28.0 notes show Chance to Bleed Support can support minion skills, and the page may be older than that: not re-checked against current skills"
  - "wiki 'attack lands' condition for infliction carries a {{Citation needed}} tag (blocked, dodged or evaded attacks)"
  - "PoB applies the enemy PhysicalDamageReduction mod to bleed; whether bosses in game have a physical reduction that applies to bleed other than armour is not sourced"
  - "per-item scope (local vs global) of weapon 'chance to cause Bleeding' lines: cargo shows local_chance_to_bleed_on_hit_% on weapon mods (Modifier:BleedOnHitGainedDexMasterVendorItemUpdated~), unique lines were not checked one by one"
  - "no seed uses bleed; Haemophilia / Usurper's Penance variants were read from PoB item text only"
open_questions:
  - "Do you want a moving-fraction scenario input for bleed (stationary 70% versus moving 210%)? PoB has only the tick; no sourced default exists"
```
