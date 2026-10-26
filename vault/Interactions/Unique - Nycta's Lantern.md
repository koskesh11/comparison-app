---
type: interaction
status: draft
pob_refs: [Battlemage, MainHandWeaponDamageAppliesToSpells, TotalDPS, CombinedDPS]
source: "PoB 2.67.2 Data/Uniques/mace.lua:573-595, Data/Bases/mace.lua:434-444, Modules/CalcOffence.lua:585-593 and 3351-3356, Modules/ModParser.lua:5542, Data/ModCache.lua lines per provider; poewiki Nycta's Lantern rev 1494670, Battlemage rev 1579100; b2c-item-analyst-leaguestart.md (task 027 batch 2c)"
last_confirmed_patch: "3.29.x"
---

Nycta's Lantern is a Crystal Sceptre that grants the Battlemage keystone: the main-hand weapon's damage is added to spells (wiki rev 1579100: "Gain Added Spell Damage equal to the Damage of Your Main Hand Weapon"). The sceptre's own rolls (150-200% increased Physical, 76-98 to 161-176 Fire) are therefore spell damage; by arithmetic from PoB's base and ranges about 227 (low roll) to 268 (high roll) average added per cast before effectiveness (not a PoB run).
PoB models it (CalcOffence.lua:585-593), main hand only, all damage types, scaled by damage effectiveness like added damage. The item has no spell-damage mods since 3.19.0 and needs 59 Str / 85 Int.
Uniques are packages: every line is valued; the item has no downside in the text, only gates (main hand, requirements).

Pipeline: [[Damage calculation#Flat damage]] - weapon damage becomes added spell damage; [[Damage calculation#Damage effectiveness]] - scaled by the spell's effectiveness like any added damage

```interaction
id: unique-nyctas-lantern
mechanic: "Unique package: a sceptre that grants Battlemage - its own main-hand damage (increased physical and added fire rolls) is added to spells"
family: buff
pipeline_step: ["Damage calculation#Flat damage", "Damage calculation#Damage effectiveness"]
pipeline_why: "Battlemage adds the weapon's min / max damage per type as BASE flat damage to the spell, which is scaled by damage effectiveness and then by the normal increased / more pools"
target: self
related: [damage-calculation, ascendancy-inquisitor, spell-projectile-supports, battlemage]
pob:
  measured: full
  how: "Data/ModCache.lua:14358 parses the keystone line into flag Battlemage + MainHandWeaponDamageAppliesToSpells MAX 100 (ModParser.lua:5542). Modules/CalcOffence.lua:585-593: if flag Battlemage and Weapon 1 has weaponData, for every damage type adds BASE <type>Min/Max = floor(weaponData1 value x MainHandWeaponDamageAppliesToSpells/100) flagged Spell; summed as added damage at CalcOffence.lua:3351-3356 (addedMin x damageEffectiveness x addedMult). Added damage is scaled by the spell's damage effectiveness in PoB (Winter Orb 0.8, Ethereal Knives 2.5, b5c-ia3.md section 3, b5c-pca.md section A); whether the game does the same is NOT VERIFIED. CalcOffence.lua:1932-1934 canDeal drops damage types the skill cannot deal, so the fire half is lost under Brutality (Ethereal Knives) and every non-cold type is lost under Bitter Frost (Worb). Measured in the golden builds, see package.removal."
  config: []
  unparsed: []
model: null
providers:
  - {kind: unique, name: "Nycta's Lantern", variant: "5 (Current)", slot: weapon (main hand sceptre), role: scales, target: self, text: "Implicit: 30% increased Elemental Damage", source: "Data/Uniques/mace.lua:573-595; Data/ModCache.lua:8271", pob: full}
  - {kind: unique, name: "Nycta's Lantern", variant: "5 (Current)", slot: weapon (main hand sceptre), role: scales, target: self, text: "(150-200)% increased Physical Damage (local; raises the weapon damage Battlemage copies)", source: "Data/Uniques/mace.lua:573-595; Data/ModCache.lua:5538", pob: full}
  - {kind: unique, name: "Nycta's Lantern", variant: "5 (Current)", slot: weapon (main hand sceptre), role: scales, target: self, text: "Adds (76-98) to (161-176) Fire Damage (local weapon damage that Battlemage copies)", source: "Data/Uniques/mace.lua:573-595 (live ModParser, roll-specific line not in ModCache)", pob: full}
  - {kind: unique, name: "Nycta's Lantern", variant: "5 (Current)", slot: weapon (main hand sceptre), role: enables, target: self, text: "Battlemage (keystone)", source: "Data/ModCache.lua:14358; Modules/ModParser.lua:5542; Modules/CalcOffence.lua:585-593", pob: full}
package:
  seed: none
  slot: "Weapon (main hand)"
  base: "Crystal Sceptre (phys 35-52, crit 8, rate 1.25, req 41 / 59 Str / 85 Int, implicit 30% increased Elemental Damage)"
  variant: "5 = Current (variants 1-4 keep older mods; reworked 3.19.0)"
  removal: "PoB swap deltas (Nycta's Lantern, variant 5, replaces the golden build's main hand in memory; the gem group of the old main hand stays slotted and enabled; b5c-ia3.md section 3, EK numbers re-run in b5c-ia4.md sections 4 and 5, which supersede IA3's stale EK main-skill TotalDPS). Golden build Worb (skill Winter Orb; replaced Mystic Refractor, Pagan Wand), Pinnacle / Mapping: whole swap TotalDPS -3.6% / -3.6% (1,343,498 -> 1,295,765; 1,934,211 -> 1,865,492; +3 projectiles and 10% cast speed lost), FullDPS 6,717,488 -> 6,478,827 / 9,671,056 -> 9,327,459. The Battlemage line alone is 0.00% (swap with and without the line identical): the build allocates Bitter Frost (node 12128, 'Cannot deal non-Cold Damage', TreeData/3_29/tree.lua:56299-56306), all DealNoPhysical / Fire / Lightning / Chaos flags carry source Tree:12128. Counterfactual with Bitter Frost deallocated in memory (not the real build): Battlemage line alone Winter Orb TotalDPS +4.1% / +6.7% (1,184,076 vs 1,137,843; 1,755,852 vs 1,645,870), FullDPS +232,104 / +553,006 (+4.1% / +6.7%), and the whole swap is only +0.4% Pinnacle on Winter Orb against that base. Golden build CoC EK Assa (skill Ethereal Knives, physical CoC-triggered spell; replaced Armageddon Stinger, Imperial Skean): Battlemage line alone FullDPS +20.9% / +20.9% (2,176,132 vs 1,799,269; 2,547,197 vs 2,107,567); it is physical only (weaponData Physical 116-172 x damageEffectiveness 2.5 = +290 to +430 per hit; the Fire 87-169 is not dealt because the Brutality support sets DealNoFire). SWAP COST OF THAT BUILD, not of Nycta: the dagger-to-sceptre swap loses 85.6% FullDPS Pinnacle (15,148,519 -> 2,176,132) and 82.3% Mapping (14,431,692 -> 2,547,197); Ethereal Knives TotalDPS 7,728,445 -> 1,098,266 (-85.8%) / 7,331,707 -> 1,280,762 (-82.5%). Cause (verified chain, b5c-ia4.md section 4): the dagger's crafted 'Hits can't be Evaded' makes Cyclone (the CoC source attack) hit 100%, the sceptre gives it 46% Pinnacle / 51% Mapping hit chance (CalcOffence.lua:2230-2231); the CoC trigger rate multiplies the source attack rate by hit chance (CalcTriggers.lua:739-756) and by crit chance, which already includes hit chance (CalcOffence.lua:3146; CalcTriggers.lua:761-781), so 6.3 x 0.46 x 0.46 = 1.333 triggers/s vs 8.93; Ethereal Knives also drops level 23 -> 21 and 17 -> 16 projectiles (the dagger's +1 spell levels). Whether the game applies the evade loss once or twice is NOT VERIFIED. Headless deltas, not game facts."
  downsides_that_are_the_point: []
  inert_lines: ["50% increased Light Radius (ModCache.lua:10248, no damage effect, no provider written)"]
  foulborn: "none for this item (no Nycta entry in ModFoulbornMap.jsonc / ModFoulborn.lua); MutatedUniqueTwoHandMace6KeystoneBattlemage (ModFoulborn.lua:186) is another item"
  obtainability: "cargo drop_enabled 1, is_drop_restricted 0, drop_level null, req 41, release 0.10.3; rework 3.19.0 (wiki rev 1494670: 'Now grants Battlemage'); patch 3.29"
makes_redundant:
  - {provider: "flat spell damage on gear / added-damage supports for the same hit", when: "Nycta's is the main-hand weapon", why: "the weapon damage is already added to the spell", source: "Modules/CalcOffence.lua:585-593"}
conflicts:
  - {with: "off-hand or non-weapon main hand", effect: "only Weapon 1 is read (itemList['Weapon 1'])", source: "Modules/CalcOffence.lua:587"}
  - {with: "Heralds", effect: "Battlemage cannot add damage to Heralds; it needs a skill that deals spell damage", source: "poewiki Battlemage rev 1579100"}
conditions:
  - {text: "main-hand sceptre with weaponData, spells only; sceptre requirement 59 Str / 85 Int (PoB shows unmet requirements)", source: "Modules/CalcOffence.lua:587; Data/Bases/mace.lua:443"}
  - {text: "stacks with Spellblade Support (not redundant with it)", source: "poewiki Battlemage rev 1579100"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "static keystone on a worn weapon; spells use their own cast rate, the weapon hit rate is irrelevant", source: "Modules/CalcOffence.lua:585-593"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "same as Mapping; no scenario condition", source: "Modules/CalcOffence.lua:585-593"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Nycta%27s_Lantern (rev 1494670)", kind: wiki, patch: "3.19"}
  - {ref: "https://www.poewiki.net/wiki/Battlemage (rev 1579100)", kind: wiki, patch: "3.13"}
  - {ref: "PoB Data/Uniques/mace.lua, Data/Bases/mace.lua, Modules/CalcOffence.lua, Modules/ModParser.lua", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b2c-item-analyst-leaguestart.md", kind: discovery, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: the 227-268 average is arithmetic from PoB base + ranges, not a PoB output (the run used PoB's computed weaponData1: Physical 116-172, Fire 87-169 at default rolls and normalised quality)"
  - "NOT VERIFIED: whether the game scales Battlemage's added damage by the spell's damage effectiveness (PoB does: CalcOffence.lua:3351-3356); wiki rev 1579100 says only 'added spell damage equal to the damage of your main hand weapon'"
  - "NOT VERIFIED: whether the game applies the 'Hits can't be Evaded' loss once or twice to the CoC trigger rate (PoB squares the hit chance); Nycta in EK would need a hit-chance fix first"
  - "NOT VERIFIED: how much of the fire line Battlemage copies when the spell is not a fire skill (PoB copies all types regardless of the spell)"
  - "NOT VERIFIED: the physical roll enters weaponData1 only from the weapon's local increases (global physical increases not run)"
  - "NOT VERIFIED: the flag name Battlemage is shared with Battlemage's Cry (CalcOffence.lua:587 skillModList:Flag(nil,'Battlemage')); whether PoB's Battlemage's Cry also sets it"
  - "The keystone mechanic has its own note [[battlemage]]; Instruments of Virtue 19417 (Inquisitor) is another source of it (TreeData/3_29/tree.lua:16529-16539), Battlemage's Cry is an unrelated skill"
open_questions: []
```
