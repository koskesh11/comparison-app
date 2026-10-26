---
type: interaction
status: draft
pob_refs: [ElementalAegisValue, FireAegisDisplay, sharedElementalAegis, Multiplier:AllocatedNotable, FireMaximumHitTaken, TotalEHP]
source: "poewiki Primal Aegis rev 1649363, Bastion of Elements rev 1579851, Ascendancy class rev 1697030; PoB 2.67.2 ModParser.lua, CalcSetup.lua, CalcDefence.lua, Data/Skills/other.lua, TreeData/3_29/tree.lua; b1-tree-ascendancy-analyst.md, b1-pob-coverage-auditor.md M3 (task 027 batch 1)"
last_confirmed_patch: "3.29.x"
---

Primal Aegis is not a passive of its own in 3.29: it is the skill that the Elementalist ascendancy notable Bastion of Elements (4917, 2 points) triggers, so it is one pick, not two. The Aegis takes elemental damage from hits before other resources; its value is 75 per allocated notable (tree, ascendancy and cluster notables), and it restores to full after 5 s without elemental hit damage. PoB counts it as a static full pool in elemental max hit and EHP and leaves out the 5 s delay and depletion. Physical and chaos are untouched, and the other Aegis skills are disabled.
Pipeline: [[Receiving damage#Guard and Aegis]] - the Aegis absorbs before ward, energy shield, mana and life (CalcDefence.lua:282-298), and it adds to the pool in [[Defences#Effective HP]].
Impact EK: the Assassin cannot take Bastion (Elementalist only), no effect. Impact Fireball: Bastion adds an elemental-only buffer to elemental max hit and EHP and nothing to the 7,000 physical max hit goal or to Life and ES. Measured on Worb (add Bastion plus its path node 6052): elemental max hit 47,619 to 67,029 (+19,410), TotalEHP 76,837 to 108,339 (+31,502) at 36 notables (pool 2,700), TotalDPS +0.9% from the path node. The cost is 2 of the 8 ascendancy points, and it competes with DPS notables such as Shaper of Storms, which the user kept.

```interaction
id: elementalist-aegis-bastion
mechanic: "Bastion of Elements (Elementalist ascendancy notable) triggers Level 20 Primal Aegis: an elemental-damage shield of 75 per allocated notable that takes elemental hit damage before other resources and restores after 5 s without elemental hit damage"
family: defence
pipeline_step: ["Receiving damage#Guard and Aegis", "Defences#Effective HP"]
pipeline_why: "the Aegis is taken ahead of ward, energy shield, mana and life (PoB order aegis, ward, ES, MoM, life) and enlarges the elemental hit pool; physical and chaos do not use it"
target: self
related: [energy-shield-hybrid, mind-over-matter, shock]
pob:
  measured: partial
  how: "ModParser.lua:2838 gives ElementalAegisValue MAX 75 x Multiplier AllocatedNotable (CalcSetup.lua:778-779 from PassiveSpec.lua:1455-1456, counts every allocated Notable node); pool read CalcDefence.lua:2463, 2467-2470; absorbed in hits :288-293; added to each elemental TotalHitPool (3178-3179, only when isElemental) and to EHP (2638-2651). Not counted: the 5 s restore delay and depletion (static full pool, same shape as the vault gap Guard absorb static pool). No enabling needed: the mod sits in the player modDB (grep GlobalEffect Classes/ModStore.lua: no match). 'Other Aegis Skills are Disabled' parses to DisableSkill SkillType.Aegis + EnableSkill Primal Aegis (ModParser.lua:2835-2837)"
  config: []
  unparsed:
    - "Bastion of Elements: Cannot take Reflected Elemental Damage (ModCache not read)"
model: null
providers:
  - {kind: ascendancy, name: "Bastion of Elements 4917 (Elementalist)", slot: tree, role: applies, target: self, text: "Triggers Level 20 Primal Aegis when Allocated / Primal Aegis can take 75 Elemental Damage per Allocated Notable Passive Skill / Other Aegis Skills are Disabled / Cannot take Reflected Elemental Damage; gated by small node 6052, so 2 points", source: "TreeData/3_29/tree.lua:50006-50020; Modules/ModParser.lua:2835-2838; wiki Bastion of Elements rev 1579851", pob: partial}
  - {kind: gem, name: "Primal Aegis (hidden triggered skill)", slot: tree, role: applies, target: self, text: "no cost, cast time 1; aegis_unique_shield_max_value_per_allocated_notable 75, aegis_recharge_delay_ms 5000", source: "Data/Skills/other.lua:3436-3466; wiki Primal Aegis rev 1649363", pob: partial}
  - {kind: notable, name: "Every allocated notable (tree, ascendancy, cluster)", slot: tree, role: scales, target: self, text: "+75 elemental pool each", source: "wiki Primal Aegis rev 1649363; Modules/CalcSetup.lua:778-779", pob: full}
  - {kind: unique, name: "Invictus Solaris / Vix Lunaris / Perepiteia / Magna Eclipsis", slot: any, role: blocks, target: self, text: "the other Aegis items (Fire, Cold, Lightning and Elemental Aegis) are disabled by Bastion", source: "wiki Bastion of Elements rev 1579851 (Mechanics list)", pob: partial}
makes_redundant: []
conflicts:
  - {with: "Other Aegis skills", effect: "disabled while Bastion of Elements is allocated", source: "TreeData/3_29/tree.lua:50006-50020; Modules/ModParser.lua:2835-2837"}
  - {with: "Other Elementalist ascendancy notables (ascendancy point budget)", effect: "8 points in total (wiki Ascendancy class rev 1697030); every Elementalist notable is gated by one small node, so 2 points each: Mastermind of Discord 61259, Shaper of Storms 27038, Shaper of Flames 53123, Bastion 4917, Bringer of Ruin 258, Liege 56461, Shaper of Winter 40810; Heart of Destruction 57197 needs Mastermind plus small node 19595 (2 more). The Worb seed (Mastermind, Shaper of Storms, Liege, Heart) uses exactly 8, so Bastion means dropping one of the four", source: "TreeData/3_29/tree.lua (ascendancy edges via scratchpad ascedges.py); wiki Ascendancy class rev 1697030"}
conditions:
  - {text: "elemental hits only; the first hit that depletes it is absorbed up to the remaining pool; restore needs 5 s without elemental hit damage and the delay cannot be interrupted while depleted; counts as damage taken for recoup and Cast when Damage Taken", source: "wiki Primal Aegis rev 1649363"}
uptime:
  Mapping:       {value: partial, config: {}, reasoning: "continuous elemental pressure from packs keeps it empty because the restore needs 5 s without elemental hit damage; PoB shows the full pool anyway", source: "wiki Primal Aegis rev 1649363; Modules/CalcDefence.lua:3178-3179"}
  Pinnacle Boss: {value: partial, config: {}, reasoning: "the first big elemental hit meets a full pool, later hits only after 5 s without elemental hit damage; no PoB model for later hits", source: "wiki Primal Aegis rev 1649363"}
seeds: [Fireball]
sources:
  - {ref: "https://www.poewiki.net/wiki/Primal_Aegis (rev 1649363; 3.13.0 introduced, 3.14.0 100 to 75 per notable, 3.22.0 Ruthless-only change)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Bastion_of_Elements (rev 1579851)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Ascendancy_class (rev 1697030)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/ModParser.lua:2835-2838; Modules/CalcSetup.lua:778-779; Modules/CalcDefence.lua:282-298,2463-2470,3178-3179,2638-2651; Data/Skills/other.lua:3436-3466; Data/ModCache.lua:18680,22313 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "b1-pob-coverage-auditor.md M3 (Worb, Bastion 4917 plus path node 6052 added with AllocNode and rolled back; Worb base: Fire/Cold/Lightning max hit 47,619, Physical 16,310, Chaos 16,866, TotalEHP 76,837, TotalDPS 1,343,498; with Bastion: 67,029 each, Physical 16,852 (+542 from the path node), Chaos 16,866, sharedElementalAegis 2,700 = 75 x 36 notables, TotalEHP 108,339, TotalDPS 1,355,601)", kind: pob, patch: "3.29"}
not_verified:
  - "No PoB run with Bastion allocated in the Fireball build; the Fireball statements are a source chain, not a measured delta (the Worb run is a different build)"
  - "Number of allocated notables in the Fireball build: the analyst's illustration was 30 notables = 2,250; Worb measured 36 = 2,700"
  - "Whether the trigger of Primal Aegis (ExtraSkill level 20, ModCache.lua:22313) needs a skill slot in PoB"
  - "Cannot take Reflected Elemental Damage parse, and how often reflect occurs in the user's content"
  - "Sustained hits inside the 5 s recharge delay are not modelled by PoB (not read in code)"
  - "Ascendancy point cost is not enforced by AllocNode in the headless probe (Worb already has 8 allocated)"
open_questions:
  - "Fireball seed: DPS (Shaper of Storms, which needs the shocked config tick) or elemental-only max hit (Bastion) for the ascendancy points? The user kept Shaper of Storms and declined Bastion in the Worb seed; the Fireball decision is open"
```
