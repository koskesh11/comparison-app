---
type: interaction
status: draft
pob_refs: [AffectedByHeraldofPurity, PhysicalDamage, BuffEffect, PhysicalMin, PhysicalMax, ReqDex, TotalDPS, FullDPS, TotalEHP]
source: "CoC EK Assa.xml item id 27 (ring 1, PoB 2.67.2, game 3.29), headless removal and per-line probes (tasks/reports/027-evidence/partial/b2c/item-analyst-ek.md); PoB Data/ModCache.lua:16854 and 12265; poewiki Circle of Guilt rev 1675555"
last_confirmed_patch: "3.29.x"
---

Circle of Guilt is a Synthesised ring whose value in the EK seed is three damage lines, two of which only work while Herald of Purity is active: 69% increased Physical Damage while affected, 60% increased Herald of Purity buff effect, and flat added physical. Together they are 16.6% of FullDPS (product 0.834, matches the whole removal); +17 to all attributes also keeps the body armour Dex requirement met.
The Herald of Purity gem sits in the Entropic Devastation glove sockets, so ring and gloves are coupled: swap the gloves and the Herald must be re-socketed, or the ring loses 15.8% of FullDPS (the two Herald lines). The Sentinel of Purity variant is not on this copy (see the Absolution note).

Pipeline: [[Damage calculation#Increased and reduced]] - the Herald lines add to the increased physical pool and the Herald's buff effect; the added physical is a flat step ([[Damage calculation#Flat damage]]).

```interaction
id: unique-circle-of-guilt
mechanic: "Unique package: Circle of Guilt gives 69% increased Physical Damage while affected by Herald of Purity, 60% increased Herald of Purity buff effect and added physical damage (16.6% of the EK seed's FullDPS together), coupled to the Herald gem in the Entropic Devastation gloves, plus +17 attributes and defence implicits"
family: buff
target: self
pipeline_step: ["Damage calculation#Increased and reduced", "Damage calculation#Flat damage"]
pipeline_why: "the Herald lines are an increased-physical mod and a buff-effect mod gated by the AffectedByHeraldofPurity condition; the added physical is a flat step before the pools"
related: [heralds, aura-conditional-uniques, aura-effect, conversion-gain-as-extra, absolution, minions, unique-entropic-devastation]
pob:
  measured: full
  how: "All lines parse (none red). The conditional lines use the tag Condition AffectedByHeraldofPurity (see the aura-conditional-uniques mechanic), satisfied by an enabled Herald of Purity gem; reservation cost is in the unreserved mana. The Noxious catalyst quality is already in the displayed number (no tags in the seed text, getCatalystScalar returns 1). Seed (headless, in memory): whole removal FullDPS -16.593% (12,624,983), TotalDPS -16.232% (6,473,977); product of the three damage lines 0.834 = -16.6%, matches"
  config: []
  unparsed: []
model: null
providers:
  - {kind: unique, name: "Circle of Guilt", variant: "Physical Damage (selected variant lines)", slot: ring, role: scales, target: self, text: "69% increased Physical Damage while affected by Herald of Purity", source: "live parse PhysicalDamage INC 69 [Condition AffectedByHeraldofPurity] (not in ModCache); per-line removal FullDPS -9.885%, TotalDPS -9.705%", pob: full}
  - {kind: unique, name: "Circle of Guilt", variant: "Buff Effect (selected variant lines)", slot: ring, role: scales, target: self, text: "Herald of Purity has 60% increased Buff Effect", source: "Data/ModCache.lua:16854; per-line removal FullDPS -5.934%, TotalDPS -5.834%", pob: full}
  - {kind: unique, name: "Circle of Guilt", variant: "no variants", slot: ring, role: scales, target: enemy, text: "Adds 10 to 15 Physical Damage", source: "Data/ModCache.lua:12265; per-line removal FullDPS -1.593%, TotalDPS -1.482%", pob: full}
  - {kind: unique, name: "Circle of Guilt", variant: "no variants", slot: ring, role: enables, target: self, text: "+17 to all Attributes (keeps the body armour Dex requirement met)", source: "live parse Str/Dex/Int BASE 17; per-line removal: Str 162, Dex 164 (ReqDex 173 UNMET), Int 345, ES -40, Mana -12, EHP -1.5%, FullDPS -0.002%", pob: full}
  - {kind: unique, name: "Circle of Guilt", variant: "no variants", slot: ring, role: sustains, target: self, text: "+389 to Armour", source: "live parse Armour BASE 389; per-line removal: Armour 658 -> 269, TotalEHP 145,259 -> 140,084 (-3.6%)", pob: full}
  - {kind: unique, name: "Circle of Guilt", variant: "synthesis implicits", slot: ring, role: sustains, target: self, text: "9% increased Evasion Rating; 30% increased Mana Regeneration Rate", source: "Data/ModCache.lua:11855 and 8322; per-line removal: evasion EHP -0.7%, mana regeneration 0", pob: full}
  - {kind: unique, name: "Circle of Guilt", variant: "synthesis implicit", slot: ring, role: scales, target: self, text: "Minions have 6% increased Movement Speed", source: "live parse MinionModifier MovementSpeed INC 6 (not in ModCache); per-line removal 0", pob: full}
package:
  seed: "CoC EK Assa.xml (PoB 2.67.2, game 3.29), item set 1"
  slot: "Ring 1"
  base: "NOT VERIFIED (not in the evidence file)"
  xml_item_id: 27
  variant: "variants selected in the item text: Buff Effect + Physical Damage; Synthesised, Noxious catalyst quality 20; not Foulborn; not Fractured"
  removal: "FullDPS -16.593% (15,136,639 -> 12,624,983), TotalDPS -16.232%, TotalEHP -5.7% - in-memory removal; a ring has no sockets, so nothing extra is lost in game"
  lost_with_item:
    - "Herald of Purity physical lines: 69% increased Physical while affected (-9.885% FullDPS) and 60% Herald buff effect (-5.934%), added physical 10-15 (-1.593%)"
    - "Str/Dex/Int 179/181/362 -> 162/164/345: Dex 164 < ReqDex 173, body armour Cataclysm Shroud requirement UNMET (PoB shows no DPS change for that)"
    - "Armour 658 -> 102, Evasion 14082 -> 13239, ES 5189 -> 5149, Mana 1201 -> 1189 (unreserved 107 -> 105); condition UniqueItemInRing 1 / IronRingEquipped off; RingItem count 2 -> 1"
  downsides_that_are_the_point: []
  foulborn: "none: no Circle of Guilt key in Data/ModFoulbornMap.jsonc, no Foulborn text in wiki rev 1675555. The wiki lists a Fractured version (Circle of Guilt (Fractured)); the seed is not fractured (fractured only locks the +all attributes line)"
  obtainability: "poewiki Circle of Guilt rev 1675555 (patch 3.29): Synthesis league unique (3.6.0), 'This item can only drop from a Synthesis boss' (SynthesisSoulstealerGuardian1-4 per the wiki drop_monsters), 1-3 random Synthesis implicits, 2 random Herald of Purity modifiers (Herald Buff Effect 40-60% since 3.11.0). 3.29.0 version row: non-unique synthesised items cannot be obtained any more; the Bestiary craft 'reroll a Synthesis implicit' works only on Unique items; Reduced Mana Cost implicits can no longer roll. Whether Synthesis bosses are reachable in the current league: NOT VERIFIED. The seed is a near-perfect copy: 60 on Buff Effect is the top of 40-60, 69 physical = 57.5 x 1.2 with Noxious 20, within (40-60)"
makes_redundant: []
conflicts:
  - {with: "Herald of Purity not active (gem removed, unsocketed, or Generosity-supported)", effect: "both Herald lines (15.8% of FullDPS) are off; the condition is never set", source: "aura-conditional-uniques note; CalcPerform.lua:2461-2471"}
conditions:
  - {text: "Herald of Purity sits in the Entropic Devastation glove sockets (group 3) with +1 gem level from those gloves: a gloves swap means re-socketing the Herald", source: "item-analyst-ek.md, Circle of Guilt downsides"}
  - {text: "Dex floor shared with Badge of the Brotherhood (+24) and the Darkness Enthroned abyss jewels (+19): base Dex 181 vs ReqDex 173 (8 spare); removing any one leaves Cataclysm Shroud unmet", source: "item-analyst-ek.md, Cross-item findings 1"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "AffectedByHeraldofPurity is set by the active gem; no uptime model", source: "aura-conditional-uniques note; CalcPerform.lua:2467-2471"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "same as Mapping", source: "aura-conditional-uniques note"}
seeds: [EK]
sources:
  - {ref: "https://www.poewiki.net/wiki/Circle_of_Guilt (rev 1675555)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Data/ModCache.lua:16854, 12265, 11855, 8322", kind: pob, patch: "3.29"}
  - {ref: "headless probes on CoC EK Assa.xml, PoB 2.67.2 (tasks/reports/027-evidence/partial/b2c/item-analyst-ek.md)", kind: pob, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: Synthesis boss availability in the current league"
  - "NOT VERIFIED: whether the unscaled Noxious display in the seed equals the in-game value (it matches the ranges only after x1.2)"
  - "NOT VERIFIED: whether Herald of Purity is also modified by tree nodes or other items (not checked)"
  - "NOT VERIFIED: the ring base name"
open_questions:
  - "Should the generator treat Circle of Guilt's Herald lines as a reason to keep Herald of Purity socketed in the gloves, or move the Herald when the gloves change?"
```
