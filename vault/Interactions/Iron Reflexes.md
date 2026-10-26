---
type: interaction
status: draft
pob_refs: [IronReflexes, NoDexBonusToEvasion, Armour, Evasion, EvadeChance, PhysicalDamageReduction, PhysicalMaximumHitTaken, ConfiguredNotHitChance, TotalEHP, conditionHaveArborix, enemyIsBoss]
source: "poewiki Iron Reflexes rev 1605890 (fetched 2026-10-26; version history ends 0.11.2, text equals tree.lua); PoB 2.67.2 CalcDefence.lua / CalcPerform.lua / ModParser.lua / ConfigOptions.lua / Data/ModCache.lua / TreeData 3_29; headless runs on EK, FR and the Fireball seed (scratchpad b3c/F_run.py, evidence b3c/tree-ascendancy-analyst-F.md)"
last_confirmed_patch: "3.29.x"
---

Iron Reflexes (keystone, node 10661, TreeData/3_29/tree.lua:56282-56286: "Converts all Evasion Rating to Armour. Dexterity provides no bonus to Evasion Rating") turns the whole evasion rating into armour and removes the Dexterity-to-evasion bonus. The trade is evade chance for physical damage reduction: it pays only where physical hits dominate the damage you take and your base evasion is large. On the seeds it is a large gain on EK (13.2k evasion becomes armour) and almost nothing on FR and the Fireball seed (336 and 26 evasion). Related: [[Defences]] (evasion and armour formulas, caps), [[Receiving damage]].

Pipeline: [[Defences#Armour formula]] - PoB adds the base evasion (gear plus flat) to the armour total before the armour multipliers, with the Armour AND Evasion AND "Armour and Evasion" AND Defences modifier groups applied, so the wiki formula and PoB agree; the evade-chance layer ([[Defences#Evasion]]) then reads Evasion = 0.

How PoB applies it: the line parses to two flags, NoDexBonusToEvasion and IronReflexes (Data/ModCache.lua:14783, Modules/ModParser.lua:2240). CalcDefence.lua:846 reads IronReflexes; per gear slot the evasion base goes to armour with calcLib.mod(Armour, Evasion, ArmourAndEvasion, Defences) (CalcDefence.lua:937-939), the global flat evasion does the same (CalcDefence.lua:998-1001), and nothing is left in `evasion`. CalcPerform.lua:532 skips the Dexterity "increased Evasion" when NoDexBonusToEvasion is set.

Measured (headless, in memory, nothing saved; keystone only - node 10661 force-allocated alone, path cost not included; enemy level from the headless run, env.enemyLevel = env.enemy.level: 85 at None, 84 at Pinnacle):

| Seed | boss | Armour | Evasion | EvadeChance | Physical max hit | TotalEHP | ConfiguredNotHitChance |
|---|---|---|---|---|---|---|---|
| EK | None (85) | 658 -> 13897 | 14082 -> 0 | 62 -> 0 | 7538 -> 10339 (+37.2%) | 71911 -> 302152 (+320.2%) | 45.49 -> 21 |
| EK | Pinnacle (84) | 658 -> 13897 | 14082 -> 0 | 63 -> 0 | 7538 -> 10339 (+37.2%) | 145259 -> 148852 (+2.5%) | 45.88 -> 21 |
| FR | None (85) | 0 -> 334 | 336 -> 0 | 0 | 38594 -> 38713 (+0.3%) | 102318 -> 111160 (+8.6%) | 5 |
| FR | Pinnacle (84) | 0 -> 334 | 336 -> 0 | 0 | 33307 -> 33410 (+0.3%) | 273342 -> 282337 (+3.3%) | 5 |
| Fireball seed (NOT VIABLE) | None / Pinnacle | 2827 -> 2848 | 26 -> 0 | 0 | 5142 -> 5145 | 7806 / 12065 unchanged | 0 |

- EK physical damage reduction against the PoB reference hit: 27% -> 88% (None) and 23% -> 76% (Pinnacle); PhysicalTakenHit 793.5 -> 130.4 (None) and 1449.5 -> 451.8 (Pinnacle). DPS keys (TotalDPS, CombinedDPS, FullDPS) are unchanged on all three seeds.
- Why EK None jumps +320% and Pinnacle only +2.5%: the None preset deals 100% physical (see [[Chaos Inoculation]], same EK/FR runs), so the physical gain is the whole EHP; the Pinnacle mix contains elemental and chaos damage that armour does not reduce, and the 63% evade chance is lost at the same time. Read the physical max hit (+37.2%) as the honest hit-size number.
- EK arithmetic: 13897 armour = 658 + 13239, so 94% of the 14082 evasion rating comes back as armour; the missing 843 was not decomposed (Dex 181 normally gives floor(181/5) = 36% increased Evasion, which IR removes, and the armour and evasion modifier groups differ).
- What it does not do: evade chance only protected against attacks (EK is a spell build), so on EK the real loss is smaller than the 62-63% suggests; on an attack build the lost evade chance is a real cost that the armour must out-earn.

What PoB leaves out or differs from the wiki:
- The wiki says armour gained from evasion equipment counts as "Armour from" that equipment for effects like Prospero's Protection or Unbreakable. PoB adds the converted evasion to `armour` but only real armour to `gearArmour` (CalcDefence.lua:925-939), so a slot-keyed armour effect may not see it. Not tested.
- Armour only reduces physical hit damage and is capped (see [[Defences#Physical damage reduction cap]]); the 88% above is below that cap only because of the reference hit size.

```interaction
id: iron-reflexes
mechanic: "Converts all Evasion Rating to Armour (flat gear and global evasion enter the armour total with the Armour, Evasion, Armour-and-Evasion and Defences modifiers); Dexterity gives no bonus to Evasion Rating; evade chance becomes 0"
family: defence
target: self
related: [defences, receiving-damage, chaos-inoculation]
pipeline_step: ["Defences#Armour formula", "Defences#Evasion"]
pipeline_why: "Iron Reflexes moves the evasion pool into the armour term of the armour formula (CalcDefence.lua:937-939, 998-1001) and zeroes the evasion term, so the evade-chance layer disappears and physical hit reduction grows; it changes which layer of the defence pipeline carries the rating, not the incoming damage."
pob:
  measured: full
  how: "Data/ModCache.lua:14783 gives flags NoDexBonusToEvasion and IronReflexes (Modules/ModParser.lua:2240); CalcDefence.lua:846 reads the flag, 937-939 (per slot) and 998-1001 (global) add evasion to armour; CalcPerform.lua:532 drops the Dexterity evasion bonus. Measured headless on EK, FR and the Fireball seed (node 10661 alone, None and Pinnacle): EK Armour 658 -> 13897, Evasion 14082 -> 0, physical max hit 7538 -> 10339, TotalEHP +320.2% (None) / +2.5% (Pinnacle), EvadeChance 62-63 -> 0; FR +334 armour, +0.3% physical max hit; DPS unchanged. Not modelled: the wiki rule that converted armour counts as armour from the equipment for slot-keyed effects (Prospero's Protection, Unbreakable)."
  config:
    - {var: conditionHaveArborix, default: false, ref: "Modules/ConfigOptions.lua:1664-1667 (a tick adds Condition:HaveIronReflexes and the Keystone line for Arborix's 16 s / 8 s version; without it the unique's keystone is not modelled)", class: c}
    - {var: enemyIsBoss, default: "Pinnacle (list index 3)", ref: "Modules/ConfigOptions.lua:2086 (decides the enemy damage mix TotalEHP uses: None is 100% physical)", class: b}
    - {var: EHPUnluckyWorstOf, default: "Average", ref: "Modules/ConfigOptions.lua:226 (makes evade, dodge, block and suppression rolls unlucky in the EHP)", class: c}
  unparsed: []
model: null
providers:
  - {kind: keystone, name: "Iron Reflexes 10661", slot: tree, role: enables, target: self, text: "Converts all Evasion Rating to Armour. Dexterity provides no bonus to Evasion Rating", source: "TreeData/3_29/tree.lua:56282-56286; Data/ModCache.lua:14783; Modules/ModParser.lua:2240", pob: full}
  - {kind: tattoo, name: "Iron Reflexes tattoo (keystone tattoo)", slot: tree, role: enables, target: self, text: "replaces a tree node with the Iron Reflexes keystone (Limited to 1 Keystone Tattoo)", source: "Data/TattooPassives.lua:1235-1240", pob: full}
  - {kind: unique, name: "Arborix", slot: Bow, role: enables, target: self, text: "variants 4 and 5: Iron Reflexes (permanent); variants 1-3: Every 16 seconds you gain Iron Reflexes for 8 seconds (50% uptime by the text), 30% more Damage with Arrow Hits at Close Range while you have Iron Reflexes, 30% increased Attack, Cast and Movement Speed and Far Shot while you do not", source: "Data/Uniques/bow.lua:28-32; Data/ModCache.lua:15461, 17272; Modules/ConfigOptions.lua:1664-1667; Modules/ModParser.lua:1916-1917, 5475", pob: config}
  - {kind: unique, name: "Grelwood Shank", slot: Sword, role: enables, target: self, text: "Iron Reflexes while stationary (condition Stationary)", source: "Data/Uniques/sword.lua:160; Data/ModCache.lua:17273; Modules/ModParser.lua:5288", pob: partial}
  - {kind: mod, name: "You have Iron Reflexes while at maximum Frenzy Charges", slot: any, role: enables, target: self, text: "keystone while Frenzy Charges are at maximum (owning item not traced)", source: "Data/ModItemExclusive.lua:6490; Data/ModCache.lua:22905", pob: partial}
  - {kind: mod, name: "Hellscape upside: Iron Reflexes (body armour)", slot: Body Armour, role: enables, target: self, text: "Scourge upside granting the keystone", source: "Data/ModScourge.lua:104; Data/ModCache.lua:17272", pob: full}
  - {kind: mod, name: "Crucible weapon tree: Iron Reflexes", slot: Weapon, role: enables, target: self, text: "weapon tree keystone (dagger, claw, sword and others by weight key)", source: "Data/Crucible.lua:1374", pob: full}
  - {kind: mod, name: "increased Armour / Armour and Evasion / Global Defences, flat Armour and flat Evasion", slot: any, role: scales, target: self, text: "all of them feed the converted pool; increased Evasion only helps through the evasion part, increased Armour helps both parts (wiki summary)", source: "Modules/CalcDefence.lua:937-939, 998-1001; wiki Iron Reflexes rev 1605890", pob: full}
  - {kind: mod, name: "Evade chance, Dexterity bonus to Evasion, Evasion-keyed effects", slot: any, role: blocks, target: self, text: "evade chance becomes 0 (EK 62-63% -> 0), the Dexterity increased-Evasion bonus is removed, effects that need Evasion Rating have nothing to scale", source: "headless EK run; Modules/CalcPerform.lua:532; Modules/CalcDefence.lua:869", pob: full}
makes_redundant:
  - {provider: "Evade chance sources and Evasion-only increases (increased Evasion Rating mods, Grace-type evasion, Dexterity-to-evasion)", when: "Iron Reflexes allocated", why: "evade chance is 0 and Evasion Rating is 0; increased Evasion still counts for the converted base (wiki and PoB) but nothing else of the evasion layer does", source: "headless EK run (EvadeChance 62 -> 0); Modules/CalcDefence.lua:937-939; wiki Iron Reflexes rev 1605890"}
conflicts:
  - {with: "attack-evasion builds that rely on evade chance and Ghost Dance-type effects", effect: "evade chance is lost; armour only reduces physical hits", source: "headless EK run; wiki Iron Reflexes rev 1605890"}
conditions:
  - {text: "permanent while allocated; item versions need their condition (Arborix 8 of 16 seconds, Grelwood Shank while stationary, maximum Frenzy Charges)", source: "Data/Uniques/bow.lua:28-29; Data/ModCache.lua:17273, 22905"}
  - {text: "Armour only reduces physical hit damage and is capped; the gain is zero against elemental and chaos damage", source: "wiki Iron Reflexes rev 1605890; Defences note, section Physical damage reduction cap"}
uptime:
  Mapping:       {value: always, config: {enemyIsBoss: "None / map monsters (env.enemyLevel 85 in the headless run)"}, reasoning: "permanent while allocated; PoB's None preset deals 100% physical, so EK shows +320% EHP and +37.2% physical max hit; real map monsters deal elemental hits too, which armour does not touch (not verified)", source: "headless EK/FR/Fireball seed; Chaos Inoculation note (None enemy mix)"}
  Pinnacle Boss: {value: pob, config: {enemyIsBoss: "Pinnacle (default; env.enemyLevel 84 in the headless run)"}, reasoning: "use PoB's physical max hit (EK +37.2%, FR +0.3%) and TotalEHP (EK +2.5%, FR +3.3%); the Pinnacle damage mix has elemental and chaos shares armour cannot reduce, and the evade chance (EK 63%) is lost", source: "headless EK/FR/Fireball seed"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Iron_Reflexes (rev 1605890; version history ends 0.11.2)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcDefence.lua:846, 869, 925-939, 998-1001; Modules/CalcPerform.lua:532; Modules/ModParser.lua:1916-1917, 2223-2224, 2240, 5288, 5475; Modules/ConfigOptions.lua:226, 1664-1667, 2086; Data/ModCache.lua:14783, 15461, 17272-17273, 22905; Data/TattooPassives.lua:1235-1240; Data/Uniques/bow.lua:28-32; Data/Uniques/sword.lua:160; Data/ModScourge.lua:104; Data/Crucible.lua:1374; TreeData/3_29/tree.lua:56282-56286", kind: pob, patch: "3.29"}
  - {ref: "headless runs EK, FR, Fireball seed (scratchpad b3c/F_run.py, F_show.py; evidence b3c/tree-ascendancy-analyst-F.md)", kind: discovery, patch: "3.29"}
not_verified:
  - "whether converted armour counts as armour from that equipment for slot-keyed effects (Prospero's Protection, Unbreakable) in the game: the wiki says yes (citing a video); PoB's gearArmour excludes it (CalcDefence.lua:925-939); no test of those items was run"
  - "which Arborix variants are current in 3.29 and whether the 16 s / 8 s version really gives 50% uptime: read from the unique text only; PoB models it as a tick (conditionHaveArborix), not as a time share"
  - "the owner of 'You have Iron Reflexes while at maximum Frenzy Charges' (Data/ModItemExclusive.lua:6490) was not traced"
  - "EK TotalEHP +320% at None is PoB's 100% physical enemy mix, not a prediction for maps"
  - "wiki page has no version row after 0.11.2; the conversion formula text was not re-tested in game"
  - "enemy level 85 (None) and 84 (Pinnacle) are env.enemyLevel from the headless run; why None is one level higher was not traced"
open_questions:
  - "Should the generator reject Iron Reflexes for spell/ES seeds whose evasion comes only from a body armour base, or accept it whenever physical max hit rises?"
```
