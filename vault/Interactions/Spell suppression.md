---
type: interaction
status: draft
pob_refs: [SpellSuppressionChance, SpellSuppressionEffect, EffectiveSpellSuppressionChance, SuppressionChanceCap, SuppressionEffect, TotalEHP, PhysicalMaximumHitTaken, ElementalMaximumHitTaken, enemyDamageType]
source: "poewiki Spell suppression rev 1675604 (fetched 2026-10-26); PoB 2.67.2 CalcDefence.lua / Data.lua / ModParser.lua / ConfigOptions.lua; TreeData/3_29/tree.lua (b1-mechanics-researcher.md)"
last_confirmed_patch: "3.29.x"
---

Spell suppression is a chance to take 40% less damage from a spell hit (and from the ailments it inflicts); characters have no base chance, it stacks to 100% and is not avoidance, so on-hit effects still fire. PoB counts it in two different ways: TotalEHP uses the expected value, but the maximum hit credits it ONLY at 100% effective chance (and for the default damage type Average only half of the 40%), so 60-90% suppression shows 0 in PhysicalMaximumHitTaken / ElementalMaximumHitTaken while TotalEHP counts it. Related: [[Defences]], [[Block]], [[Armour and physical max hit]].
Impact: EK - its 10% chance (probable Dagger Mastery, not decomposed) is about 0 on max hit and about 4% of spell damage in TotalEHP (0.10 x 40%); going to 100% would cut every spell hit by 40% in max hit (Spell category; half of it under Average). Fireball Elementalist - the ascendancy gives no suppression node; a useful level needs about 8-10 nodes or gear pieces plus Dexterity for Magebane, and the max hit gains only at 100% (or EHP only); for the 7,000 physical goal it contributes nothing, because suppression is spells only and the goal is a physical hit.
Pipeline: [[Receiving damage#Spell suppression]] - a flat 40% off each suppressed spell hit, applied after resistances and damage reduction but before stun and block, so it multiplies with them; [[Defences#Spell suppression chance]] holds chance, effect and caps

```interaction
id: spell-suppression
mechanic: "Chance to take 40% less damage from a spell hit and the ailments it inflicts (no base chance, stackable to 100%, effect raised by 'Prevent +N% of Suppressed Spell Damage'); PoB credits it in maximum hit only at 100% effective chance"
family: defence
pipeline_step: ["Receiving damage#Spell suppression", "Defences#Spell suppression chance"]
pipeline_why: "wiki: spell suppression occurs toward the end of mitigation, after resistances and damage reduction, but before stun and block (a more/less row of damage-taken step 7); it is a flat 40% off per suppressed spell hit, so it multiplies with armour and resistance, and it is not avoidance (on-hit effects still fire)"
target: self
related: [block, armour-phys-max-hit, max-resistances, endurance-charges]
pob:
  measured: partial
  how: "CalcDefence.lua:1137-1178: SpellSuppressionChance = min(sum BASE 'SpellSuppressionChance' or override, Data.lua:250 SuppressionChanceCap 100); SpellSuppressionEffect = max(Data.lua:251 SuppressionEffect 40 + sum 'SpellSuppressionEffect', 0) (1147); EffectiveSpellSuppressionChance 0 if the enemy has CannotBeSuppressed (1149); lucky/unlucky flags (1150-1176). ModParser: 'to suppress spell damage' -> SpellSuppressionChance (360), '(to) amount of suppressed spell damage prevented' -> SpellSuppressionEffect (361-362), 'prevent +N% of suppressed spell damage while on full energy shield' (3022, Condition FullEnergyShield). (a) TotalEHP: expected value, suppressionEffect = 1 - chance x effect/100 (CalcDefence.lua:2814-2829). (b) MAXIMUM HIT: spellSuppressMult = EffectiveSpellSuppressionChance == 100 and (1 - effect/100) or 1, and for the default damage type Average only half of it, (1 - effect/100/2) (CalcDefence.lua:2068-2076, goes into AfterReductionTakenHitMulti used by max hit at 3219). Gap already noted: no suppression factor on spell-inflicted ailment DPS (vault Receiving damage#Spell suppression; DoT multiplier 1971)."
  config:
    - {var: enemyDamageType, default: "nil, code default 'Average'", ref: "Modules/CalcDefence.lua:1684; Modules/ConfigOptions.lua:2353 (Spell / Projectile Spell vs Average)", class: b}
    - {var: EHPUnluckyWorstOf, default: 1, ref: "Modules/ConfigOptions.lua:226 (1 = Average)", class: b}
  unparsed: []
model: null
providers:
  - {kind: keystone, name: "Magebane", slot: tree, role: enables, target: self, text: "Dexterity provides no inherent bonus to Evasion Rating; +1% Chance to Suppress Spell Damage per 15 Dexterity", source: "TreeData/3_29/tree.lua:55362", pob: full}
  - {kind: notable, name: "Reflexes", slot: tree, role: applies, target: self, text: "+10% chance to Suppress Spell Damage, +100 Evasion, 30% increased Evasion", source: "TreeData/3_29/tree.lua:56805", pob: full}
  - {kind: notable, name: "Instinct", slot: tree, role: applies, target: self, text: "+12% chance to Suppress Spell Damage; Recover 50 Energy Shield when you Suppress Spell Damage", source: "TreeData/3_29/tree.lua:72353", pob: full}
  - {kind: notable, name: "Inveterate", slot: tree, role: scales, target: self, text: "Prevent +3% of Suppressed Spell Damage; +15% chance to Suppress", source: "TreeData/3_29/tree.lua:78842", pob: full}
  - {kind: notable, name: "Entrench", slot: tree, role: applies, target: self, text: "+12% chance to Suppress; Life Flasks gain 3 Charges when you Suppress Spell Damage", source: "TreeData/3_29/tree.lua:70889", pob: full}
  - {kind: notable, name: "Void Barrier / Revenge of the Hunted", slot: tree, role: applies, target: self, text: "+10% chance to Suppress Spell Damage while on Full Energy Shield / while on Full Life", source: "TreeData/3_29/tree.lua:71564,72617", pob: config, requires: ["Full Energy Shield or Full Life condition set"]}
  - {kind: mastery, name: "Dagger Mastery", slot: tree, role: applies, target: self, text: "+10% chance to Suppress Spell Damage for each Dagger you're Wielding (EK wields a dagger)", source: "TreeData/3_29/tree.lua:68998", pob: full}
  - {kind: mastery, name: "Evasion Mastery", slot: tree, role: applies, target: self, text: "+15% chance to Suppress Spell Damage if Equipped Helmet, Body Armour, Gloves, and Boots all have Evasion Rating", source: "TreeData/3_29/tree.lua:56710", pob: full}
  - {kind: ascendancy, name: "Trickster Spellbreaker", slot: tree, role: scales, target: self, text: "Prevent +15% of Suppressed Spell Damage while on Full Energy Shield; 50% chance for ES recharge to start when you Suppress (Trickster only)", source: "TreeData/3_29/tree.lua:84042", pob: config, requires: ["Full Energy Shield condition set"]}
  - {kind: mod, name: "N% chance to Suppress Spell Damage (item, jewel, crafted)", slot: evasion armour pieces, role: applies, target: self, text: "wiki: rolled randomly on evasion armour; crafted at the bench", source: "https://www.poewiki.net/wiki/Spell_suppression rev 1675604", pob: full}
  - {kind: keystone, name: "Acrobatics", slot: tree, role: blocks, target: self, text: "Modifiers to Chance to Suppress Spell Damage instead apply to Chance to Dodge Spell Hits at 50% of their value (PoB: SpellSuppressionChance OVERRIDE 0; dodge cap Data.lua:248 = 75)", source: "TreeData/3_29/tree.lua:80903; Modules/ModParser.lua:2210-2212", pob: full}
makes_redundant: []
conflicts:
  - {with: "Acrobatics", effect: "removes suppression chance (converted to spell dodge at 50%)", source: "TreeData/3_29/tree.lua:80903; Modules/ModParser.lua:2210-2212"}
  - {with: "Magebane", effect: "Dexterity gives no Evasion Rating (the price of the per-15-Dexterity suppression)", source: "TreeData/3_29/tree.lua:55362"}
  - {with: "chance above 100", effect: "wasted (SuppressionChanceCap 100); 'Prevent +N%' raises the effect rather than the chance", source: "Modules/Data.lua:250; Defences#Spell suppression chance"}
conditions:
  - {text: "spells only: not attacks, not damage over time", source: "https://www.poewiki.net/wiki/Spell_suppression rev 1675604; Modules/CalcDefence.lua:1971"}
  - {text: "max hit credits suppression only when EffectiveSpellSuppressionChance == 100 (half the effect under damage type Average)", source: "Modules/CalcDefence.lua:2068-2076"}
  - {text: "chance mods with conditions (full ES, full life, hit recently, moving) count in PoB only when the condition is set; config checkboxes not individually verified", source: "b1-mechanics-researcher.md"}
uptime:
  Mapping:
    value: always
    config: {}
    reasoning: "passive chance from tree, mastery and gear; conditional lines follow their condition"
    source: "b1-mechanics-researcher.md"
  Pinnacle Boss:
    value: always
    config: {enemyDamageType: "Spell / Projectile Spell vs Average changes the max-hit credit"}
    reasoning: "always as a stat but useful only if the boss hits are spells; for max hit PoB credits it only at 100% chance (60-90% shows 0 in PhysicalMaximumHitTaken / ElementalMaximumHitTaken while TotalEHP counts it)"
    source: "Modules/CalcDefence.lua:2068-2076,2814-2829"
seeds: [EK, Fireball]
sources:
  - {ref: "https://www.poewiki.net/wiki/Spell_suppression (rev 1675604, 2026-07-20); version rows 3.16.0 introduced, 3.19.0 item values reduced / passives increased, 3.27.0 now prevents 40% (previously 50%)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcDefence.lua:1137-1178,2068-2076,2814-2829; Modules/Data.lua:248,250,251; Modules/ModParser.lua:360-362,2210-2212,3022 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "TreeData/3_29/tree.lua (scan of every node whose stats contain 'Suppress'; ascendancy hits only Trickster, Raider, Warden, Reliquarian, Ascendant)", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b1-mechanics-researcher.md", kind: discovery, patch: "3.29"}
not_verified:
  - "per-node condition config names (full ES, full life, hit recently, moving)"
  - "tree location and distance of Reflexes / Instinct from the Witch and Shadow starts (not mapped); Assassin and Elementalist have no suppression node in the 3.29 tree (researcher's scan)"
  - "cargo list of all spawnable suppression mods and their tiers (templated wiki query not run)"
  - "EK's 10% source (probable Dagger Mastery, not decomposed); the Worb sample shows 0"
  - "boss spell-vs-attack mix: undocumented in the evidence"
  - "the 'Modifiers to Chance to Suppress Spell Damage also apply to Chance to Defend with N% of Armour' node line has a parser (ModParser.lua:3863 feeding ArmourDefense, CalcDefence.lua:1601-1609) but was not measured"
open_questions:
  - "PoB credits suppression in maximum hit only at 100% chance, while the game rolls per hit (a PoB modelling choice, not verified against the game): should the engine follow PoB's max hit, the expected value (TotalEHP), or show both?"
```
