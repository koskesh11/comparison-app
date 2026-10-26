---
type: interaction
status: draft
pob_refs: [Kalandra's Touch, ItemCondition, TotalDPS, TotalEHP]
source: "PoB 2.67.2 Data/Uniques/ring.lua:1638-1642, Modules/CalcSetup.lua:1189-1226, Modules/ModStore.lua:699-712, Modules/ModParser.lua:1632-1633 and 3139, Data/ModCache.lua:19104; poewiki Kalandra's Touch rev 1627114; b2c-item-analyst-leaguestart.md (task 027 batch 2c)"
last_confirmed_patch: "3.29.x"
---

Kalandra's Touch is a ring that reflects the opposite ring: PoB copies every mod of the other ring (implicits, enchantment, influence multipliers) except SocketedIn-tagged ones (CalcSetup.lua:1189-1226). On its own it is blank; the value is a second copy of the best ring, so the price follows that ring.
The effect is code, not a mod: the line "Reflects opposite Ring" is an unparsed leftover by design (ModCache.lua:19104; ModParser.lua:3139 "Display only"). The copied mods act at their usual pipeline steps.
PoB and the wiki disagree on one case: the 'both Equipped Rings have an Explicit Evasion Modifier' mastery. PoB applies it through Kalandra's Touch (+376 ES measured on Winter Orb Elementalist); the wiki footnote says it does not, but cites no source (open questions).
The copy also carries the influence of the copied ring: in the SRS CI Guardian sample the copied Hunter influence is the 4th Hunter item, and the Bound By Destiny line behind it is worth 466k of the 493k TotalEHP delta (PoB, Pinnacle; game NOT VERIFIED).
Uniques are packages: every line is valued; the downside that is the point is that it is blank without a strong ring.

Pipeline: [[Damage calculation#Flat damage]] - no step of its own; the copied ring's mods act at their usual steps (here flat damage as an example); [[Defences#Resistance caps]] - copied resistances count to the cap

```interaction
id: unique-kalandras-touch
mechanic: "Unique package: a ring that reflects the opposite ring's mods (second copy of the best ring in the other ring slot)"
family: resource
pipeline_step: ["Damage calculation#Flat damage", "Defences#Resistance caps"]
pipeline_why: "the item has no mods of its own; the copied mods enter the same pools as the original ring's mods (flat damage, resistances, ...) at gear aggregation"
target: self
related: [damage-calculation, defences, ring-copy]
pob:
  measured: partial
  how: "Modules/CalcSetup.lua:1189-1226 copies every mod of the opposite ring (modList or slotModList) except SocketedIn-tagged ones, scaled by `scale`; adds the other ring's corrupted / influence multipliers (1206-1213) and the '<RingBase>Equipped' multiplier (1216-1218); own ExtraSkill implicits still apply (1223-1226). Modules/ModStore.lua:699-712 (ItemCondition) treats Kalandra's slot as the opposite ring; ModStore.lua:699-706 (bothSlots) replaces Kalandra with the other ring in BOTH slots, so 'both rings have X modifiers' (ModParser.lua:1632-1633) is TRUE in PoB. Wiki rev 1627114 says the mastery does not apply when Kalandra's reflects a ring with that modifier. scale = 1 for the copy (`local scale = 1` CalcSetup.lua:1051, only changed in other branches, copy at :1202 ScaleAddMod(modCopy, scale); b5c-ia1.md section 2). Removal measured on 2 samples (package.removal); the other 2 samples hold it only in inactive item sets."
  config: []
  unparsed: ["Kalandra's Touch: 'Reflects opposite Ring' -> Data/ModCache.lua:19104 {nil,'Reflects opposite Ring '} (leftover by design; effect coded in CalcSetup.lua:1189-1226)"]
model: null
providers:
  - {kind: unique, name: "Kalandra's Touch", variant: "no variants", slot: ring (slot 1 or 2), role: enables, target: self, text: "Reflects opposite Ring (cargo local_ring_duplicate_other_ring); the second line 'Mirrored' is a status line, not a provider", source: "Data/Uniques/ring.lua:1638-1642; Modules/CalcSetup.lua:1189-1226; Modules/ModParser.lua:3139; Data/ModCache.lua:19104", pob: partial}
package:
  seed: none
  slot: "Ring (slot 1 or 2)"
  base: "NOT VERIFIED (the evidence does not name the base; PoB lines Data/Uniques/ring.lua:1638-1642)"
  variant: "none"
  removal: "PoB removal delta, whole item (slot emptied, in-memory; a ring has no sockets, so no gem group stays active), b5c-ia1.md section 3. Sample 3.27/SRS CI Guardian Giga Build.xml (item 28 in Ring 1, active item set 1; opposite ring = rare Bone Ring, Hunter + Crusader influence), skill Summon Raging Spirit of Enormity (6 spirits): Pinnacle FullDPS 70,514,022 -> 64,514,893 (-8.5%), Mapping 99,194,728 -> 90,755,649 (-8.5%); TotalEHP Pinnacle 997,954 -> 504,693 (-49%), Mapping 38,567,836 -> 36,769,893 (-4.7%); ES 12,549 -> 11,869; Str/Dex -30 each leaves 2 gems unmet (Vaal Haste Dex 155>131, Shield Charge Str 155>135). Per copied line (FullDPS Pinnacle, share the copy adds, not additive): Minions deal 41% increased Damage 3,275,322, Minions 15% increased Attack and Cast Speed 3,123,581; minion movement speed and +15% all ele res 0. Sample 3.26/Winter Orb Elementalist.xml (item 6 in Ring 2, active item set 1; opposite ring = rare Diamond Ring with 7% inc Spell Damage per Power Charge, +30% Global Crit Multiplier, +47 ES, +47% Cold res, +46% Lightning res, 17% inc Damage; usePowerCharges ticked, 10 charges), skill Winter Orb (5 gems, 10 stages): Pinnacle FullDPS 14,451,311 -> 12,719,203 (-12.0%), Mapping 18,389,382 -> 16,140,455 (-12.2%); TotalEHP Pinnacle 78,128 -> 31,564 (-60%; Cold 90 -> 48 and Lightning 90 -> 44 fall under the cap with the -60 resistance penalty ticked), Mapping 77,433 -> 75,689 (-2.3%); per copied line (FullDPS Pinnacle share): 7% inc Spell Damage per Power Charge 844,857, +30% Global Crit Multiplier 845,627, 17% increased Damage 205,104. Re-run with PoB's own rebuild order (b5c-ia4.md section 2): identical to the digit. Headless single-enemy deltas, not game facts. Samples 3.26/CoC/Occu CoC FR YT.xml (item 73, only in item set 5) and RF Pohx.xml (item 166, only in item set 9) hold the item in an inactive set: not measured."
  influence_copy: "PoB adds the opposite ring's influence flags to the item multipliers (CalcSetup.lua:1207-1211). SRS CI Guardian sample: removing Kalandra's Touch changes HunterItem 4 -> 3 and CrusaderItem 2 -> 1, so the jewel Bound By Destiny (10% of Elemental Damage taken as Chaos Damage if 4 Hunter Items are Equipped) drops out. Pinnacle TotalEHP: 997,954 with the line, 531,667 with Kalandra's Touch kept and the line removed (the line is worth 466,287 EHP), 504,693 with Kalandra's Touch removed (the line then changes nothing); the other ~27k of the 493k delta is the ES/Str/Dex part. Mapping: no change (38,567,836 in all three). b5c-ia1.md section 3c. Wiki rev 1627114 and patch 3.26.0 say the game copies the influence of the reflected ring and name Bound By Destiny (b5c-mr.md C2); no game test for this exact jewel: NOT VERIFIED."
  downsides_that_are_the_point: ["blank on its own: needs a second strong ring; value = 2x the best ring and its price", "wiki rev 1627114: no benefit in both ring slots; does not reflect the extra ring slot of The Unseen Hand; no socket or gem copy; left / right-slot bonuses are not doubled"]
  foulborn: "none (no Kalandra entry in Data/ModFoulbornMap.jsonc)"
  obtainability: "cargo drop_enabled 1, is_drop_restricted 0, drop_level 60, req 1, release 3.19.0; added to the core drop pool in 3.20.0 (wiki rev 1627114); 2x Reflection of the Heart (divination card); 'technically cannot be chanced'; 3.26.0 copies the influence of the reflected ring; 3.27.0 wording 'opposite'; patch 3.29"
makes_redundant:
  - {provider: "a second best-in-slot ring", when: "the opposite ring is the one wanted twice", why: "the ring is copied", source: "Modules/CalcSetup.lua:1189-1226"}
conflicts:
  - {with: "slot-specific ring bonuses (e.g. Sibyl's Lament / Penumbra style)", effect: "left / right-slot bonuses are not doubled", source: "poewiki Kalandra's Touch rev 1627114"}
  - {with: "rings whose paired effects cancel each other (Snakepit / Shavronne's Revelation style)", effect: "chain and fork disabled when both are copied", source: "poewiki Kalandra's Touch rev 1627114"}
  - {with: "The Unseen Hand extra ring slot", effect: "cannot reflect it", source: "poewiki Kalandra's Touch rev 1627114"}
conditions:
  - {text: "needs another ring in the opposite slot; rarity is always unique; anointment is copied from the other ring, the item itself cannot be anointed", source: "poewiki Kalandra's Touch rev 1627114"}
uptime:
  Mapping:       {value: pob, config: {}, reasoning: "inherits the copied ring's conditions; the copy itself is static", source: "Modules/CalcSetup.lua:1189-1226"}
  Pinnacle Boss: {value: pob, config: {}, reasoning: "same as Mapping; inherits the copied ring's conditions", source: "Modules/CalcSetup.lua:1189-1226"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Kalandra%27s_Touch (rev 1627114)", kind: wiki, patch: "3.27"}
  - {ref: "PoB Data/Uniques/ring.lua, Modules/CalcSetup.lua, Modules/ModStore.lua, Modules/ModParser.lua, Data/ModCache.lua", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b2c-item-analyst-leaguestart.md", kind: discovery, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: which side the game takes in the mastery conflict (PoB measured, wiki claim uncited, no game test)"
  - "NOT VERIFIED: current availability of drop level 60 in early maps"
  - "NOT VERIFIED: that the game counts the copied Hunter influence for 'N Hunter Items are Equipped' (Bound By Destiny); wiki and the 3.26.0 patch note say influence is copied, PoB applies it, no game test"
  - "NOT VERIFIED: Esh of the Storm / Tul of the Blizzard ('all Equipped Rings are Synaptic / Cryonic Rings'): PoB counts Kalandra's Touch as the copied ring's base type (CalcSetup.lua:1217-1220; live: Synaptic ring + Kalandra's Touch = 2, b5c-pca.md C); the wiki does not say"
  - "Winter Orb Elementalist Mapping TotalEHP moves only -2.3% on removal while Pinnacle moves -60%; the cause (enemy damage profile in PoB's model) was not traced"
open_questions:
  - "CONFLICT PoB vs wiki, mastery 'Evasion and Energy Shield Mastery' (effect 47151, TreeData/3_29/tree.lua:71529): '20% increased Maximum Energy Shield if both Equipped Left and Right Rings have an Explicit Evasion Modifier'. PoB measured (b5c-ia1.md section 4, Winter Orb Elementalist, skill Winter Orb, mastery node 1215 allocated): evasion ring + Kalandra's Touch gives ES 7,448 -> 7,824 (+376, +20% increased ES), identical to two real evasion rings; a ring without an evasion line gives 0 (cases B, D); FullDPS +61,008 Pinnacle / +77,177 Mapping. Reason in code: ModStore.lua:698-705 replaces Kalandra's Touch by the other ring for the bothSlots condition. Wiki rev 1627114 footnote: the mastery does not apply when Kalandra's Touch reflects a ring with an evasion modifier. Which reading should the engine use?"
  - "The wiki claim has no cited source (b5c-mr.md C4): it first appears in rev 1389818 (2023-11-03, summary 'Mechanics', no reference; absent in rev 1389810) and was moved into a footnote in rev 1438733 (2024-04-27); no patch note, GGG post or linked test found. It quotes the pre-3.23.0 mastery wording ('Evasion Modifiers'; 3.23.0 changed it to 'Explicit'), so a test made before 3.23.0 may not describe the 3.29 text. Only a game test settles it; until then PoB may overstate by the +376 ES (+20% increased ES) shown above for a build that takes this mastery with Kalandra's Touch."
```
