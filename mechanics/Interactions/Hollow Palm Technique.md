---
type: interaction
status: draft
pob_refs: [Condition:Unencumbered, Condition:DualWielding, Speed, PhysicalMin, PhysicalMax, BlockChance, Dex, DisableWeapons]
source: "poewiki Hollow Palm Technique rev 1576516 (fetched 2026-10-26; last row 3.15.0); PoB 2.67.2 CalcPerform.lua, CalcSetup.lua, CalcActiveSkill.lua, ModParser.lua, Data/ModCache.lua, Data/Misc.lua, Data/ClusterJewels.lua, Data/Uniques, TreeData/3_29/tree.lua; headless measurements on EK, Worb, FR and the Fireball file, tasks 027 batch 3c (pob-coverage-auditor-E.md)"
last_confirmed_patch: "3.29.x"
---

Hollow Palm Technique is the unarmed keystone, and the only one of the four that is not on the passive tree: PoB's spec has no node 60069 (measured), the keystone comes from a cluster jewel ("Adds Hollow Palm Technique": One With Nothing, a Small Cluster Jewel unique). Tree text (TreeData/3_29/tree.lua:85683, node 60069): "You count as Dual Wielding while you are Unencumbered / 40% more Attack Speed with Melee Skills while you are Unencumbered / Adds 14 to 20 Attack Physical Damage to Melee Skills per 10 Dexterity while you are Unencumbered"; reminder: Unencumbered = no Gloves, no Main Hand Item, no Off Hand Item. It needs a melee build with bare hands and no gloves: no current seed fits (all four wear a weapon, an off-hand and gloves), so the measured effect is 0 everywhere. [[Bleed]], [[Ignite]], [[Poison]] and [[Damage over time multiplier]] are not touched; it is hit and attack-speed only.

Pipeline: [[Damage calculation#Flat damage]] - the 14-20 physical per 10 Dexterity is a flat added attack damage to melee skills (PoB PerStat Dex div 10, flag Melee, keyword Attack, ModParser.lua:2443-2444) that enters before the increased pool; the 40% (x1.1 dual-wield, x1.54 together) is a More on attack speed ([[Damage calculation#Hit rate]]).

Measured headless, in memory only (E_run.py; enemy level from env.enemyLevel: 85 at None, 84 at Pinnacle). The keystone is added by a custom line 'Hollow Palm Technique' (the node is not allocatable; ModCache.lua:16991 turns it into the Keystone entry; 'keystone only, path cost not included'):
- EK, Worb, FR, Fireball file: 0 changed output keys at both levels (flag Unencumbered false, weapon1 type Dagger/Wand).
- What-if only, FR stripped in memory (Weapon 1, Weapon 2 and Gloves removed; the stripped build itself is far worse: TotalDPS 7,472.2 at Pinnacle vs 166,643.3, crit chance 100 -> 6.3): adding the keystone raises TotalDPS 7,472.2 -> 12,861.1 (+72.1%) at Pinnacle and 10,354.7 -> 17,573.9 (+69.7%) at None; FullDPS 415,725.5 -> 630,149.3 (+51.6%) and 608,376.1 -> 916,521.2 (+50.7%); Speed 4.356 -> 6.696 (x1.537 = 1.4 x 1.1); BlockChance 1 -> 21, SpellBlockChance 6 -> 10 (dual-wield inherent bonus); added physical 140-200 per hit at Dex 104 (10 steps of 14-20). The what-if delta is the keystone alone; whether an unarmed build can be good is another question.

```interaction
id: hollow-palm-technique
mechanic: "While Unencumbered (no gloves, no main hand, no off hand): you count as dual wielding, 40% more attack speed with melee skills, adds 14-20 attack physical damage to melee skills per 10 Dexterity; wiki: unarmed attacks then alternate main hand and off hand"
family: buff
target: self
related: [bleed, ignite, poison, damage-over-time-multiplier, accuracy-and-hit-chance]
pipeline_step: ["Damage calculation#Flat damage", "Damage calculation#Hit rate"]
pipeline_why: "PoB turns the condition into mods on the player: PhysicalMin/Max BASE per 10 Dex with the Melee flag (ModParser.lua:2443-2444) join the flat damage step, the 40% is a MORE on Speed for melee attacks (ModCache.lua:9425) in the hit-rate step, and Condition:DualWielding adds the inherent dual-wield 10% more attack speed and 20% block (CalcSetup.lua:635-638, Data/Misc.lua:81, 88)."
pob:
  measured: partial
  how: "All three lines parse (Data/ModCache.lua:9425 Speed MORE 40, flags Attack, SkillType 20 = Melee, Condition Unencumbered; 12465 PhysicalMin/Max BASE 14/20 PerStat Dex div 10, flags Melee 256, keyword Attack 65536, Condition Unencumbered; 22835 Condition:DualWielding FLAG, Condition Unencumbered); keystone entry 16991 (Keystone LIST); cluster grant 13624 (JewelData clusterJewelKeystone). The condition: CalcPerform.lua:151-156 sets Unencumbered only if weaponData1.type is 'None' and there is no Weapon 2 item and no Gloves item; CalcPerform.lua:3472-3478 sets it too for DisableWeapons (The Dancing Dervish manifest) when no gloves. DualWielding condition comes from the keystone flag or from weaponData1 and weaponData2 both having a type (CalcPerform.lua:221-222). Added damage per Dex: PerStat on the player's total Dex (E_run.py: 140-200 at Dex 104). NOT modelled / unverified: the wiki says unarmed attacks alternate main hand and off hand; PoB runs an off-hand pass only if weaponData2 has a type (CalcActiveSkill.lua:326-334), which an empty off hand does not give, so PoB probably counts only the main-hand pass (not measured)."
  config: []
  unparsed: []
model: null
providers:
  - {kind: jewel, name: "Cluster jewel keystone 'Hollow Palm Technique'", slot: jewel, role: applies, target: self, text: "Adds Hollow Palm Technique (cluster jewel keystone list); the node is not part of the allocatable tree", source: "Data/ClusterJewels.lua:885-894; Data/ModCache.lua:13624; TreeData/3_29/tree.lua:85683", pob: full}
  - {kind: unique, name: "One With Nothing", slot: Small Cluster Jewel, role: applies, target: self, text: "Adds Hollow Palm Technique", source: "Data/Uniques/jewel.lua:506-510", pob: full}
  - {kind: unique, name: "Replica Perfect Form", slot: Body Armour, role: applies, target: self, text: "Hollow Palm Technique (variant 3, Pre 3.23.0 only; the current variant 4 has Versatile Combatant)", source: "Data/Uniques/body.lua:445-466", pob: full, variant: "variant 3 (Pre 3.23.0)"}
  - {kind: unique, name: "The Dancing Dervish", slot: Sword, role: enables, target: self, text: "Manifested Dancing Dervishes disable both weapon slots: PoB treats the player as unarmed and Unencumbered when no gloves are worn", source: "Data/Uniques/sword.lua:773; Modules/CalcPerform.lua:3472-3478", pob: partial}
  - {kind: mod, name: "Dexterity (attributes, tree, gear)", slot: any, role: scales, target: self, text: "each 10 Dex adds 14-20 physical attack damage to melee skills while Unencumbered", source: "Modules/ModParser.lua:2443-2444", pob: full}
makes_redundant:
  - {provider: "Dual wielding weapon-pair requirements", when: "Hollow Palm Technique active", why: "the keystone grants the Dual Wielding condition itself (inherent 10% more attack speed and 20% block in PoB) without weapons", source: "Modules/CalcSetup.lua:635-638; Data/Misc.lua:81, 88"}
  - {provider: "gloves, weapons and shield slots", when: "Hollow Palm Technique active", why: "the keystone only works with all three empty; their stats are lost, the keystone's gains are not weighed against that in PoB", source: "Modules/CalcPerform.lua:151-156; wiki Hollow Palm Technique rev 1576516"}
conflicts:
  - {with: "any glove, weapon or off-hand item (shield)", effect: "Unencumbered is false, all three mods inactive (measured: 0 change on EK, Worb, FR, Fireball file)", source: "Modules/CalcPerform.lua:151-156; E_run.py"}
  - {with: "spell and DoT skills", effect: "40% more attack speed and added damage apply to melee ATTACK skills only", source: "Data/ModCache.lua:9425, 12465"}
  - {with: "shield-based defences (block, spell block, armour of the shield)", effect: "Unencumbered means no off-hand, so no shield; the DW block bonus of 20% replaces it only in part", source: "Modules/CalcSetup.lua:637-638; E_run.py (block 1 -> 21)"}
conditions:
  - {text: "Unencumbered = no gloves, no main hand and no off hand item; unarmed attacks count as dual wielding (wiki, fixed in 3.10.1c) and alternate hands", source: "wiki Hollow Palm Technique rev 1576516 (3.10.1c, 3.15.0 rows)"}
  - {text: "3.15.0: attack speed 60% -> 40% more; 'Added Attack Physical per 10 Dexterity' became '14 to 20 Attack Physical Damage to Melee Skills per 10 Dexterity'", source: "wiki Hollow Palm Technique rev 1576516"}
uptime:
  Mapping:       {value: always, config: {enemyIsBoss: "None / map monsters (enemy level 85 in the runs)"}, reasoning: "permanent while the three slots stay empty; the condition comes from gear, not from a config box", source: "Modules/CalcPerform.lua:151-156"}
  Pinnacle Boss: {value: always, config: {enemyIsBoss: "Pinnacle (default; enemy level 84 in the runs)"}, reasoning: "same: gear condition, no uptime loss", source: "Modules/CalcPerform.lua:151-156"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Hollow_Palm_Technique (rev 1576516)", kind: wiki, patch: "3.29"}
  - {ref: "PoB TreeData/3_29/tree.lua:85683; Data/ModCache.lua:9425,12465,13624,16991,22835; Modules/ModParser.lua:1629,2443-2444,5617; Modules/CalcPerform.lua:151-156,221-222,3472-3478; Modules/CalcSetup.lua:635-638; Modules/CalcActiveSkill.lua:326-334; Data/Misc.lua:81,88; Data/ClusterJewels.lua:885-894; Data/Uniques/jewel.lua:506-510, body.lua:445-466, sword.lua:773", kind: pob, patch: "3.29"}
  - {ref: "tasks 027 batch 3c: scratchpad b3c/E/E_run.py, summary.txt (headless, nothing saved)", kind: discovery, patch: "3.29"}
not_verified:
  - "whether PoB runs an off-hand pass for unarmed attacks with the keystone (inferred from CalcActiveSkill.lua:326-334, not measured); the wiki says attacks alternate hands"
  - "the what-if number (+72.1% at Pinnacle) is for a stripped FR with a crit chance of 6%, not a real build; no unarmed seed exists"
  - "Rigwald's Curse and other unarmed/off-hand interactions from the wiki version history: not checked in PoB"
  - "which cluster jewel sizes can carry the keystone and the passive count they cost: only the unique One With Nothing was read"
  - "the Unencumbered condition on The Dancing Dervish: only the CalcPerform special case was read, not whether the unique's line parses to DisableWeapons"
open_questions:
  - "Is an unarmed melee seed wanted for the generator? Without gloves and weapons the build loses their whole stat budget, which PoB does not weigh"
```
