---
type: interaction
status: draft
pob_refs: [Battlemage, MainHandWeaponDamageAppliesToSpells, DealNoPhysical, DealNoFire, DealNoLightning, DealNoChaos, DealNoCold, PhysicalHitAverage, FireHitAverage, TotalDPS, FullDPS]
source: "PoB 2.67.2 Modules/CalcOffence.lua:585-594, 1932-1935 and 3351-3356, Modules/ModParser.lua:5542, Classes/Item.lua:2298-2324, Data/ModCache.lua:14358, Data/Uniques (staff, bow, helmet, mace), Data/ModFoulborn.lua:186, TreeData/3_29/tree.lua:16529-16539; poewiki Battlemage rev 1579100, Spellblade Support rev 1701035, Nycta's Lantern rev 1494670, Instruments of Virtue rev 1631183, Disintegrator, Ephemeral Edge rev 1683357, Kongor's Undying Rage rev 1674934 (fetched 2026-10-26); evidence tasks/reports/027-evidence/b5c-pca.md section A, b5c-mr.md section A, b5c-ia3.md, b5c-ia4.md (task 027 lane 5c)"
last_confirmed_patch: "3.29.x"
---

Battlemage is a keyword: the damage of the main-hand weapon is added to your spells (wiki rev 1579100: "Gain Added Spell Damage equal to the Damage of Your Main Hand Weapon", since 3.13.0). It matters for building because eight sources exist (six uniques, one Foulborn mod, one Inquisitor notable) and the value depends on the weapon's damage types matching damage the build is allowed to deal.
PoB models it (CalcOffence.lua:585-594): Weapon 1 only, every damage type, floor of each min and max, spell flag, scaled by the spell's damage effectiveness like any added damage. Two sources do not stack (MAX 100).
The trap is damage-type locks: added damage of a type the skill cannot deal is worth 0. Measured on the golden builds (PoB removal deltas, not game facts): with Nycta's Lantern in Weapon 1 the Battlemage line is worth +20.9% FullDPS on Ethereal Knives in CoC EK Assa (the sceptre's physical part only, Brutality blocks the fire part) and 0 in Worb as built (Bitter Frost, node 12128, blocks every non-cold type); with Bitter Frost deallocated in memory it is +4.1% (Pinnacle) / +6.7% (Mapping) FullDPS on Winter Orb.
Do not confuse with the warcry Battlemage's Cry (granted by Martyr of Innocence): PoB shares no flag between them. Packages: [[Unique - Nycta's Lantern]] (sceptre), [[Inquisitor ascendancy]] (Instruments of Virtue).

Pipeline: [[Damage calculation#Flat damage]] - the weapon's per-type min and max become BASE spell damage; [[Damage calculation#Damage effectiveness]] - multiplied by the spell's effectiveness (Winter Orb 0.8, Ethereal Knives 2.5 in PoB)

```interaction
id: battlemage
mechanic: "Battlemage (keyword, 3.13.0): the main-hand weapon's damage (per type, after its local increases, quality and local added damage) is added to your spells as base damage, scaled by damage effectiveness in PoB; main hand only, two sources do not stack, added damage of a type the build cannot deal is worth 0"
family: buff
pipeline_step: ["Damage calculation#Flat damage", "Damage calculation#Damage effectiveness"]
pipeline_why: "PoB adds Spell-flagged BASE <type>Min/Max mods from Weapon 1's weaponData; they enter the hit as added damage times damage effectiveness (CalcOffence.lua:3351-3356) and then go through the normal increased / more pools; types the skill cannot deal are dropped (canDeal)"
target: self
related: [unique-nyctas-lantern, ascendancy-inquisitor, damage-calculation, spell-projectile-supports]
pob:
  measured: full
  how: "ModParser.lua:5542 parses the keyword into flag Battlemage + MainHandWeaponDamageAppliesToSpells MAX 100 (ModCache.lua:14358). CalcOffence.lua:585-594: if the skill has flag Battlemage and Weapon 1 has weaponData, for every damage type add BASE <type>Min/Max = floor(weaponData1 value x pct/100) with ModFlag.Spell, source Battlemage. weaponData1 = base + local flat added, x local increases and quality (Classes/Item.lua:2298-2324). Summed as addedMin x damageEffectiveness x addedMult at CalcOffence.lua:3351-3356. Types blocked by a DealNo flag are dropped (CalcOffence.lua:1932-1935). Measured as PoB removal/swap deltas (rows in the conditions and uptime lines)."
  config: []
  unparsed: []
model: null
providers:
  - {kind: unique, name: "Disintegrator (Maelstrom Staff)", variant: "1-5, i.e. also Current", slot: weapon (main hand staff), role: enables, target: self, text: "Battlemage", source: "Data/Uniques/staff.lua:228 (block from :202); Data/ModCache.lua:14358; wiki Battlemage rev 1579100 (since 3.13.0)", pob: full}
  - {kind: unique, name: "Martyr of Innocence (Highborn Staff)", variant: "all", slot: weapon (main hand staff), role: enables, target: self, text: "Battlemage (last line; the item also grants the unrelated Level 15 Battlemage's Cry skill)", source: "Data/Uniques/staff.lua:529 (block from :510); wiki items cargo (Battlemage since 3.13.0, Cry since 3.25.0)", pob: full}
  - {kind: unique, name: "Wing of the Wyvern (Imperial Bow)", variant: "all", slot: weapon (main hand bow), role: enables, target: self, text: "Battlemage (a bow in Weapon 1 supplies the weapon damage)", source: "Data/Uniques/bow.lua:612 (block from :599); wiki items cargo (release 3.27.0)", pob: full}
  - {kind: unique, name: "Cadigan's Crown (Runic Crown)", variant: "all", slot: helmet, role: enables, target: self, text: "Battlemage (the item also says Never deal Critical Strikes)", source: "Data/Uniques/helmet.lua:1738; wiki items cargo (release 3.15.0)", pob: full}
  - {kind: unique, name: "Nycta's Lantern (Crystal Sceptre)", variant: "5 (Current only; variants 1-4 lack it)", slot: "weapon (main hand; wiki says it also works from the off-hand with a stronger main-hand weapon)", role: enables, target: self, text: "Battlemage", source: "Data/Uniques/mace.lua:595 (block from :573); wiki Nycta's Lantern rev 1494670 (3.19.0); wiki Spellblade Support rev 1701035", pob: full}
  - {kind: unique, name: "Cadigan's Authority (Platinum Sceptre)", variant: "all", slot: weapon (main hand sceptre), role: enables, target: self, text: "Battlemage (Kingsmarch unique)", source: "Data/Uniques/mace.lua:701 (block from :691); wiki items cargo (release 3.26.0)", pob: full}
  - {kind: foulborn, name: "Foulborn Kongor's Undying Rage (Terror Maul)", variant: "Foulborn roll; mod MutatedUniqueTwoHandMace6KeystoneBattlemage replaces 'Hits can't be Evaded'; plain Kongor's (mace.lua:837) has no Battlemage", slot: weapon (main hand two-hand mace), role: enables, target: self, text: "Battlemage", source: "Data/ModFoulborn.lua:186; Data/ModFoulbornMap.lua:369-372; wiki Kongor's Undying Rage rev 1674934", pob: full}
  - {kind: ascendancy, name: "Instruments of Virtue 19417 (Inquisitor; Battlemage line)", slot: tree, role: enables, target: self, text: "Battlemage; also 10% more Attack Damage per non-instant spell cast in 8 s, up to 30% (that half is not Battlemage)", source: "TreeData/3_29/tree.lua:16529-16539 (name at 16529, stat Battlemage at 16535); wiki Instruments of Virtue rev 1631183; vault Inquisitor ascendancy.md", pob: full}
  - {kind: ascendancy, name: "Nycta's Lantern ascendancy notable (Scavenger, Legacy of Phrecia 3.25.3d)", slot: tree, role: enables, target: self, text: "Battlemage (wiki only; AscendancyCustomAscendant35)", source: "wiki Battlemage keyword sources via cargo, Nycta's Lantern ascendancy rev 1535547; not in PoB TreeData/3_29/tree.lua (grep 'Battlemage' finds only Instruments of Virtue)", pob: none}
  - {kind: mod, name: "Settlers runesmithing weapon enchant (VillageKeystoneBattlemage)", slot: weapon enchant, role: enables, target: self, text: "Battlemage (historical Settlers content; only existing enchanted weapons remain per wiki Runesmithing rev 1579237)", source: "PoB Data/ModItemExclusive.lua:8184 (lead re-check 10:35: grep finds the id there; Data/ModImplicit.lua named in b5c-mr does not exist); no unique in Data/Uniques uses it", pob: partial}
makes_redundant: []
conflicts:
  - {with: "Bitter Frost (keystone, node 12128), 'Cannot deal non-Cold Damage'", effect: "sets DealNoPhysical/Fire/Lightning/Chaos: the added physical and fire are dropped, Battlemage is worth 0 on a cold-only skill. PoB removal/swap delta on golden build Worb, Winter Orb: Battlemage line removed with Nycta's Lantern in Weapon 1 = 0.00% FullDPS and TotalDPS, Pinnacle and Mapping; with node 12128 deallocated in memory (counterfactual, not the real build): +4.1% Pinnacle (5,921,395 vs 5,689,290) / +6.7% Mapping (8,782,615 vs 8,229,609) FullDPS", source: "TreeData/3_29/tree.lua:56299-56306; b5c-ia3.md Worb rows N1, N2, N1', N2'; b5c-ia4.md Worb tables"}
  - {with: "Brutality support (DealNoFire, source Skill:SupportBrutality)", effect: "the fire half of Nycta's Lantern (87-169) is created but not dealt on Ethereal Knives; only the physical part counts. PoB removal/swap delta on golden build CoC EK Assa, Ethereal Knives: FullDPS +20.9% Pinnacle (2,176,132 vs 1,799,269) and +20.9% Mapping (2,547,197 vs 2,107,567), physical share only; the same swap also loses FullDPS through hit chance (see the Nycta note), so this is the Battlemage line alone", source: "b5c-ia3.md EK rows N1, N2; b5c-ia4.md section 4 and values table; CalcOffence.lua:1932-1935"}
  - {with: "any DealNo / 'Cannot deal non-X' source (Avatar of Fire, Void Manipulation, Voracious Flame, Roiling Tempest, Bitter Frost)", effect: "added damage of every blocked type is worth 0; the weapon's type mix must match what the skill may deal. PoB trap observed in b5c-pca.md: Battlemage added PhysicalMinBase 0 -> 16 on Worb but TotalDPS stayed 1,435,203.83 (DealNoPhysical true, PhysicalHitAverage 0)", source: "b5c-pca.md section A 'Live trap'; vault Avatar of Fire.md; CalcOffence.lua:1932-1935"}
  - {with: "off-hand weapon, dual wield", effect: "only itemList['Weapon 1'] is read; an off-hand weapon's damage is never counted (the Battlemage mod itself may sit on an off-hand Nycta's Lantern, wiki rev 1701035)", source: "CalcOffence.lua:587; b5c-pca.md section A; wiki Spellblade Support rev 1701035"}
  - {with: "Heralds", effect: "Battlemage cannot add damage to Heralds; it adds only to spells that deal spell damage", source: "wiki Battlemage rev 1579100"}
  - {with: "global added damage on the weapon (Disintegrator's per-charge added physical, Ephemeral Edge's conditional line)", effect: "wiki: not weapon-local, so not copied to spells; PoB counts only weaponData1 (local), which agrees", source: "wiki Disintegrator page; wiki Ephemeral Edge rev 1683357; Classes/Item.lua:2298-2324"}
  - {with: "Spellblade Support", effect: "not a conflict: they add; Spellblade takes one-hand melee main hand damage (x0.6 when dual wielding in PoB), Battlemage takes any main hand incl. two-handers and bows", source: "wiki Battlemage rev 1579100 and Spellblade Support rev 1701035; CalcOffence.lua:597-612"}
conditions:
  - {text: "a real weapon in the main hand (Weapon 1 with weaponData); unarmed does not count; weapon swap uses the active set only", source: "CalcOffence.lua:586-587; b5c-pca.md section A"}
  - {text: "spells only (ModFlag.Spell); attacks never get it; triggered and totem spells get it in PoB by code trace (no trigger or totem test at line 587), not live-tested", source: "CalcOffence.lua:585-594; b5c-pca.md section A"}
  - {text: "weapon value = final weapon numbers: base + local added, x local physical / elemental increases and quality, rounded; global increases apply later like any added damage", source: "Classes/Item.lua:2298-2324"}
  - {text: "multiplied by the spell's damage effectiveness in PoB: Winter Orb 0.8 (Pagan Wand 20-37 physical became PhysicalMinBase 16 / MaxBase 29.6), Ethereal Knives 2.5 (Nycta physical 116-172 became +290 to +430 base per hit); whether the game applies effectiveness is not verified", source: "CalcOffence.lua:3351-3356; b5c-pca.md section A; b5c-ia3.md EK summary"}
  - {text: "added types must be dealable by the skill and build: DealNo flags and canDeal drop the rest", source: "CalcOffence.lua:1932-1935; b5c-ia3.md"}
  - {text: "two sources do not stack in PoB (MAX 100, not additive); the wiki is silent on stacking", source: "ModParser.lua:5542; b5c-pca.md section A"}
uptime:
  Mapping:       {value: pob, config: {}, reasoning: "static keyword on a worn item or allocated notable; no PoB config box. Use PoB's own number with the real skill and damage-type locks (golden EK Ethereal Knives line +20.9% FullDPS; Worb 0 as built, +6.7% if Bitter Frost were off; PoB removal/swap deltas)", source: "CalcOffence.lua:585-594; b5c-ia3.md; b5c-ia4.md"}
  Pinnacle Boss: {value: pob, config: {}, reasoning: "same as Mapping; no scenario condition (golden EK +20.9%, Worb 0 as built, +4.1% with Bitter Frost off; PoB removal/swap deltas)", source: "CalcOffence.lua:585-594; b5c-ia3.md; b5c-ia4.md"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Battlemage (rev 1579100)", kind: wiki, patch: "3.13"}
  - {ref: "https://www.poewiki.net/wiki/Spellblade_Support (rev 1701035)", kind: wiki, patch: "3.22"}
  - {ref: "https://www.poewiki.net/wiki/Nycta%27s_Lantern (rev 1494670)", kind: wiki, patch: "3.19"}
  - {ref: "https://www.poewiki.net/wiki/Instruments_of_Virtue (rev 1631183)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Kongor%27s_Undying_Rage (rev 1674934)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Ephemeral_Edge (rev 1683357)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcOffence.lua:585-594, 1932-1935, 3351-3356; Modules/ModParser.lua:5542; Classes/Item.lua:2298-2324; Data/ModCache.lua:14358; Data/Uniques; Data/ModFoulborn.lua:186; TreeData/3_29/tree.lua:16529-16539", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b5c-pca.md, b5c-mr.md, b5c-ia3.md, b5c-ia4.md (task 027 lane 5c)", kind: discovery, patch: "3.29"}
not_verified:
  - "game-side damage effectiveness scaling: PoB multiplies the weapon damage by the spell's effectiveness; the wiki is silent, no game test"
  - "triggered, totem, trap and mine spells in the game: PoB gives them Battlemage by code trace (CalcOffence.lua:587 has no condition), not live-tested; the wiki is silent"
  - "minion spells: PoB minions have an empty Weapon 1 (CalcActiveSkill.lua:722) unless they use the item; code trace only, wiki silent"
  - "local increases on the weapon in the game: PoB uses the final weapon damage (local increases, quality, local added); the wiki says main-hand-specific added damage counts but is silent on increases"
  - "whether the game adds all five damage types of the weapon to a spell that cannot deal them (PoB adds all, then drops blocked types); wiki silent"
  - "an off-hand Nycta's Lantern in PoB: by code any item can carry the flag and only Weapon 1 is read, but only the main-hand swap was measured (b5c-ia3.md)"
  - "wiki-only sources: the Nycta's Lantern ascendancy notable (Legacy of Phrecia) is not in PoB 3_29 and its availability in current leagues is unknown; the Settlers enchant is data only"
  - "no GGG patch-note re-read for silent Battlemage changes after 3.13.0 (wiki history has only the 3.13.0 row)"
  - "the headless deltas are PoB removal/swap deltas on the golden builds, not game facts; Worb +4.1% / +6.7% is a counterfactual with Bitter Frost deallocated in memory"
open_questions:
  - "Should the generator offer a Battlemage source only when the weapon's damage types intersect the skill's dealable types (EK physical yes, Worb cold-only no), using PoB's removal delta as the gate, or also show the unlocked what-if (Worb without Bitter Frost +4.1% / +6.7%)?"
  - "Does the user want Battlemage valued on triggered spells (CoC Ethereal Knives) as PoB shows (+20.9% FullDPS), given the game behaviour for triggered spells is not documented?"
```
