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
related: [damage-calculation, ascendancy-inquisitor, spell-projectile-supports]
pob:
  measured: full
  how: "Data/ModCache.lua:14358 parses the keystone line into flag Battlemage + MainHandWeaponDamageAppliesToSpells MAX 100 (ModParser.lua:5542). Modules/CalcOffence.lua:585-593: if flag Battlemage and Weapon 1 has weaponData, for every damage type adds BASE <type>Min/Max = floor(weaponData1 value x MainHandWeaponDamageAppliesToSpells/100) flagged Spell; summed as added damage at CalcOffence.lua:3351-3356 (addedMin x damageEffectiveness x addedMult). Removal delta not measured (no headless run)."
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
  removal: "NOT MEASURED"
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
  - "NOT VERIFIED: removal delta (no headless run); the 227-268 average is arithmetic from PoB base + ranges, not a PoB output"
  - "NOT VERIFIED: how much of the fire line Battlemage copies when the spell is not a fire skill (PoB copies all types regardless of the spell)"
  - "NOT VERIFIED: the physical roll enters weaponData1 only from the weapon's local increases (global physical increases not run)"
  - "NOT VERIFIED: the flag name Battlemage is shared with Battlemage's Cry (CalcOffence.lua:587 skillModList:Flag(nil,'Battlemage')); whether PoB's Battlemage's Cry also sets it"
  - "No interaction note exists for the Battlemage keystone (proposed: 'Battlemage and weapon damage on spells'); Inquisitor 'Battlemage of Virtue' and Battlemage's Cry are different sources, no id invented for the keystone"
open_questions: []
```
