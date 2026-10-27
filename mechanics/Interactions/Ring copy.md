---
type: interaction
status: draft
pob_refs: [ItemCondition, CorruptedItem, HunterItem, CrusaderItem, ShaperItem, ElderItem, SynapticRingEquipped, CryonicRingEquipped, TotalEnergyShield, TotalEHP]
source: "PoB 2.67.2 Modules/CalcSetup.lua:1189-1227 and 1275-1307, Classes/ModStore.lua:690-713, Modules/ModParser.lua:1594-1595, 1632-1633, 3138 and 5497, Data/ModCache.lua:6565, 19104, 23047-23048, TreeData/3_29/tree.lua:15504, 15526, 71529, 77825; poewiki Kalandra's Touch rev 1627114, Corruption's Embrace and Esh of the Storm pages (via b5c-mr.md section C); evidence tasks/reports/027-evidence/b5c-pca.md C, b5c-mr.md C, b5c-ia1.md 2-4, b5c-ia4.md (task 027 lane 5c)"
last_confirmed_patch: "3.29.x"
---

Kalandra's Touch copies the opposite ring. The copy itself is in [[Unique - Kalandra's Touch]]; this note is the other half: how conditions that look at the rings, at an item count, at an influence count or at a corrupted count read a copy. PoB hard-codes the copy by item name (CalcSetup.lua:1189-1227), copies every non-SocketedIn mod, adds the other ring's corrupted and influence flags to the item multipliers and adds +1 to the other ring's base-type counter.
PoB and the wiki agree on the count conditions (influence, corrupted) and disagree on one: the Evasion and Energy Shield Mastery "both Equipped Rings have an Explicit Evasion Modifier" (PoB true, wiki: does not apply). RESOLVED (user, 2026-10-26): PoB is correct - the copied ring counts as a second ring with an explicit Evasion modifier, so the Evasion and Energy Shield Mastery applies (+376 ES measured); the wiki footnote (rev 1627114, uncited) is not followed.
Why it matters for building: a copied ring is a second full instance of every line, a second Hunter/Crusader/Shaper/Elder/corrupted item for count thresholds (Bound By Destiny, Shadowstitch, Corruption's Embrace), and a second base-type ring for Esh of the Storm and Tul of the Blizzard; whether the game does the same for each of these is the open part.

Pipeline: [[Damage calculation#Flat damage]] - the copied ring's damage lines enter the same pools as the original's; [[Defences#Resistance caps]] - copied resistances count towards the cap; [[Defences#Energy shield]] - the mastery condition below adds an increased maximum energy shield term

```interaction
id: ring-copy
mechanic: "Kalandra's Touch reflects the opposite ring: PoB copies its mods and properties; conditions on 'both rings', ring base type, influence count and corrupted count read the copy as a second instance of that ring (the Evasion and Energy Shield Mastery is the one case where the wiki says the game does not; the user decided for PoB, 2026-10-26)"
family: resource
pipeline_step: ["Damage calculation#Flat damage", "Defences#Resistance caps", "Defences#Energy shield"]
pipeline_why: "the copy adds ordinary mods to the item mod database at gear aggregation, so they act in the same pools as the original ring's mods; the conditions below only decide whether ring-count or item-count lines are switched on"
target: self
related: [unique-kalandras-touch, defences]
pob:
  measured: partial
  how: "copy: Modules/CalcSetup.lua:1189-1227 (item name match 'Kalandra's Touch'; other ring = Ring 1 <-> Ring 2; skipped when the other ring is also a Kalandra's Touch :1191; mods from modList or slotModList[KT slot number] :1193; SocketedIn-tagged mods dropped :1194-1198; scale 1 = `local scale = 1` CalcSetup.lua:1051, b5c-ia1.md 2; flags CorruptedItem/ShaperItem/ElderItem/WarlordItem/HunterItem/CrusaderItem/RedeemerItem +1 and Non<flag> -1 :1207-1212; ShaperOrElderItem :1213-1215; '<OtherRingBaseName>Equipped' +1 :1216-1220; only ExtraSkill mods of KT itself kept :1222-1227). KT itself is still counted by the generic counters (CalcSetup.lua:1275-1307: UniqueItem, its own corrupted/influence flags :1292-1297, its own base counter :1304-1306). Conditions: ModStore.lua:698-713 ItemCondition; bothSlots replaces a KT in either slot by the other slot's item (:701-702), single-slot ItemCondition replaces a KT in the checked slot by the opposite ring (:707-711). The item line 'Reflects opposite Ring' stays unparsed (ModCache.lua:19104; display pattern ModParser.lua:3138 needs the word 'your' and never matches) and the copy does not depend on it. Headless deltas are on two sample builds only (conditions list); PoB model, not game facts."
  config: []
  unparsed:
    - "Kalandra's Touch: 'Reflects opposite Ring' -> Data/ModCache.lua:19104 {nil,'Reflects opposite Ring '} (leftover by design; effect coded by name in CalcSetup.lua:1189-1227)"
model: null
providers:
  - {kind: unique, name: "Kalandra's Touch", variant: "no variants", slot: "ring (slot 1 or 2)", role: enables, target: self, text: "Reflects opposite Ring; PoB copies the opposite ring's mods, corrupted/influence flags and base-type count (details and package in unique-kalandras-touch)", source: "Data/Uniques/ring.lua:1638-1642; Modules/CalcSetup.lua:1189-1227", pob: partial}
makes_redundant: []
conflicts:
  - {with: "Kalandra's Touch in the extra ring slot of The Unseen Hand", effect: "wiki: cannot reflect a ring in that slot and cannot be reflected from it; PoB has no extra ring slot (CalcSetup.lua:1190 maps only Ring 1 <-> Ring 2)", source: "poewiki Kalandra's Touch rev 1627114 (no source cited on the wiki); CalcSetup.lua:1190"}
  - {with: "slot-specific ring bonuses (Sibyl's Lament, Penumbra Ring style 'Left Ring slot:' lines)", effect: "wiki: the bonus is not granted twice; PoB copies from slotModList[KT slot number] so slot-tagged lines resolve from the KT slot, whether a 'Left Ring slot:' line is doubled or dropped was not checked", source: "poewiki Kalandra's Touch rev 1627114 (Mark_GGG quote, b5c-mr.md C3); Classes/Item.lua:2222-2250 and CalcSetup.lua:1193 via b5c-pca.md C"}
conditions:
  - text: "'20% increased Maximum Energy Shield if both Equipped Left and Right Rings have an Explicit Evasion Modifier' - Evasion and Energy Shield Mastery, effect 47151 on mastery nodes 11032 (name tree.lua:71504, line :71529) and 1215 (name :77800, line :77825)"
    pob_reading: "TRUE with Kalandra's Touch + one ring that has an explicit evasion line, in either slot order; false when that ring has no evasion line or the other slot is empty. ItemCondition bothSlots, itemSlot ring, searchCond 'explicit evasion' (ModCache.lua:6565; ModParser.lua:1632-1633); ModStore.lua:701-702 replaces KT by the other ring in both slots, KT's own text is never searched. PoB removal/swap delta on Winter Orb Elementalist (3.26 sample), main skill Winter Orb (gem count 5), synthetic test rings (E = +80 Evasion Rating rare, N = ES-only rare), mastery 1215 allocated: E + KT gives ES 7,448 -> 7,824 (+376) and +20 to the increased-ES sum, FullDPS +61,008 (Pinnacle) / +77,177 (Mapping), TotalEHP +994 / +3,880; identical to the control with two real evasion rings (E + E2); E + N and N + KT give 0. Re-run with PoB's own rebuild order identical (b5c-ia4.md 2)."
    wiki_reading: "NOT FOLLOWED (user decision 2026-10-26). NOT applied: 'Kalandra's Touch reflecting a ring does not count as the item itself gaining modifiers ... the mastery does not apply when Kalandra's Touch is reflecting a ring with an evasion modifier' (footnote 'Modifiers not gained', rev 1627114, no inline citation; first appears rev 1389818 on 2023-11-03, moved into a footnote rev 1438733). The footnote quotes the pre-3.23.0 mastery wording ('Evasion Modifiers'); 3.23.0 changed it to 'Explicit', so whether the claim was tested before or after is unknown."
    agree: false
    direction: "RESOLVED (user, 2026-10-26): PoB is correct - the copied ring counts as a second ring with an explicit Evasion modifier, so the Evasion and Energy Shield Mastery applies (+376 ES measured); the wiki footnote (rev 1627114, uncited) is not followed; the ES +376 and the FullDPS/EHP rows above stand"
    source: "b5c-ia1.md 4; b5c-ia4.md 2; b5c-mr.md C4; ModStore.lua:698-705; tree.lua:71529, 77825"
  - text: "'Your Hits ignore Enemy Monster Lightning Resistances if all Equipped Rings are Synaptic Rings' - Esh of the Storm (Breachlord bloodline notable, node 6344, tree.lua:15504, name :15497)"
    pob_reading: "TRUE with a Synaptic Ring + KT: SynapticRingEquipped = 2 (the real ring counts 1 at CalcSetup.lua:1304-1306, the copy adds +1 at :1216-1220); MultiplierThreshold 2 (ModCache.lua:23048). Live in b5c-pca.md C with the Synaptic ring + KT: 2; Synaptic + Synaptic: 2; Synaptic + other ring: 1. KT's own base ('Ring', ring.lua:1639) is counted under its own key, not Synaptic."
    wiki_reading: "silent: the wiki states 'all equipped rings are the Synaptic Ring base' and does not say how KT counts (b5c-mr.md C3)"
    agree: unknown
    source: "tree.lua:15504; ModCache.lua:23048; CalcSetup.lua:1216-1220, 1304-1306; b5c-pca.md C; b5c-mr.md C3"
  - text: "'Your Hits ignore Enemy Monster Cold Resistances if all Equipped Rings are Cryonic Rings' - Tul of the Blizzard (node 48711, tree.lua:15526, name :15518)"
    pob_reading: "same mechanism by code (CryonicRingEquipped, MultiplierThreshold 2, ModCache.lua:23047); KT + Cryonic Ring = 2; not run live separately"
    wiki_reading: "silent on KT (same as Esh of the Storm)"
    agree: unknown
    source: "tree.lua:15526; ModCache.lua:23047; CalcSetup.lua:1216-1220; b5c-pca.md C"
  - text: "'N <influence> Items are Equipped' thresholds (Hunter, Crusader, Shaper, Elder, Warlord, Redeemer) - Bound By Destiny (Data/Uniques/Special/BoundByDestiny.lua:5-16, '2 Elder/Shaper/Hunter/Warlord Items' tiers; the sample jewel rolled '10% of Elemental Damage taken as Chaos Damage if 4 Hunter Items are Equipped') and 'per Shaper/Elder Item Equipped' lines (Data/Uniques/body.lua:1237, 1251; gloves.lua:984-986)"
    pob_reading: "the copy counts as one more item of each influence the opposite ring has (CalcSetup.lua:1207-1212; Elder or Shaper also ShaperOrElderItem :1213-1215). KT's own influence is none. PoB removal/swap delta on SRS CI Guardian Giga Build (3.27 sample), main skill Summon Raging Spirit of Enormity (6 spirits), Pinnacle: removing KT takes HunterItem 4 -> 3 and CrusaderItem 2 -> 1 (the other ring is a Hunter + Crusader rare), the Bound By Destiny line drops out and TotalEHP falls 997,954 -> 504,693 (-493,261); with KT present, removing only that jewel line costs 466,287 TotalEHP (531,667 vs 997,954) = about 94.5% of the removal delta; Mapping: no change (38,567,836 both). Cause in the sample: with the line the elemental-taken-as conversions total 100% so Cold/Lightning hits become 0 (b5c-ia1.md 3c)."
    wiki_reading: "AGREES: 'Kalandra's Touch will copy the corrupted/uncorrupted state and influence(s) of the opposite ring, which is relevant for effects that depend on equipment properties such as Shadowstitch and Bound by Destiny' (rev 1627114; patch 3.26.0 'now copies the influence(s) of the reflected ring'); the wiki test used Forbidden Rite vs Gravicius with The Eternity Shroud, Shaper rings (two Shaper rings vs Shaper ring + KT: both 52 casts). The rev-1389818-era text said the opposite, reversed in 3.26.0. The 'Hunter count' case itself (a Bound By Destiny threshold through the copy) is not tested on the wiki or in the game here."
    agree: true
    source: "CalcSetup.lua:1207-1215; BoundByDestiny.lua:5-16; b5c-ia1.md 3c; b5c-mr.md C2"
  - text: "'N Corrupted Items are Equipped' / 'per Corrupted Item Equipped' / 'per Uncorrupted Item Equipped' - Corruption's Embrace (Trialmaster bloodline notable 61092, tree.lua:14375-14385: 4/6/8 Corrupted Items), Shadowstitch (body.lua:1476, lines :1488-1490), two jewels 'With 5 Corrupted Items Equipped' (jewel.lua:1389, 1513), ring lines per corrupted/uncorrupted item (ring.lua:1566-1567)"
    pob_reading: "the copy adds +1 CorruptedItem (and -1 NonCorruptedItem) when the opposite ring is corrupted (CalcSetup.lua:1207-1212). By code, KT's own corrupted flag is still read by the generic counter (CalcSetup.lua:1292-1297), so a corrupted KT would count itself in PoB (code reading, not run; the data file KT has no corrupted flag, ring.lua:1638-1642)."
    wiki_reading: "AGREES for the copy: 'a Kalandra's Touch reflecting a corrupted ring in the opposite ring slot will count as a corrupted item' (Corruption's Embrace page); 'The corrupted/influence state of Kalandra's Touch itself is ignored' and 'A corrupted Kalandra's Touch will not be counted' (rev 1627114 / Corruption's Embrace page). PoB differs only for a corrupted KT itself, by code reading."
    agree: "copy yes; a corrupted KT itself: PoB would count it, wiki says ignored (code reading only)"
    source: "CalcSetup.lua:1207-1212, 1292-1297; tree.lua:14375-14385; b5c-mr.md C2, C3"
  - text: "'if your opposite Ring is a Shaper/Elder Item' - Mark of the Shaper / Mark of the Elder (Data/Uniques/ring.lua:836-837, 850-851)"
    pob_reading: "single-slot ItemCondition (ModParser.lua:1594-1595). With KT as the opposite ring, ModStore.lua:707-711 swaps KT for the other slot, so the check tests the Mark ring itself, not KT's reflected copy. Code trace only, not run."
    wiki_reading: "not covered in the evidence (the wiki influence copy text is about equipment properties, not this line)"
    agree: unknown
    source: "ModStore.lua:707-711; ModParser.lua:1594-1595; b5c-pca.md C"
  - text: "rarity and base counters: KT is always a Unique (Hidden Potential-type 'per Unique Item' lines); the copy does not copy sockets or gems; only 4 tree nodes (the mastery on 11032 and 1215, Esh, Tul) use the 'both rings' / 'all rings' wording in 3.29, no item does"
    pob_reading: "UniqueItem +1 by KT's own rarity (CalcSetup.lua:1278-1290); SocketedIn-tagged mods dropped (CalcSetup.lua:1194-1198); grep of tree.lua, Data/Uniques, ModItemExclusive, ModJewel, ModFoulborn for 'both rings', 'both equipped', 'opposite ring', 'equipped rings' finds only these (b5c-pca.md C)"
    wiki_reading: "AGREES: 'The rarity of Kalandra's Touch is always considered to be unique'; 'will not gain a socket by reflecting an Unset Ring, nor copy a gem socketed in it' (Mark_GGG quotes in rev 1627114)"
    agree: true
    source: "CalcSetup.lua:1194-1198, 1278-1290; b5c-pca.md C; b5c-mr.md C2, C3"
uptime:
  Mapping:       {value: pob, config: {}, reasoning: "static gear aggregation: the copy and every count condition are on whenever the two rings are worn; use PoB's number", source: "Modules/CalcSetup.lua:1189-1227"}
  Pinnacle Boss: {value: pob, config: {}, reasoning: "same as Mapping; the SRS Bound By Destiny line only matters in the Pinnacle EHP scenario because of the enemy damage profile PoB uses there (b5c-ia1.md 3c), not because of uptime", source: "Modules/CalcSetup.lua:1189-1227; b5c-ia1.md 3c"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Kalandra%27s_Touch (rev 1627114)", kind: wiki, patch: "3.27"}
  - {ref: "PoB Modules/CalcSetup.lua, Classes/ModStore.lua, Modules/ModParser.lua, Data/ModCache.lua, TreeData/3_29/tree.lua, Data/Uniques/ring.lua", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b5c-pca.md C, b5c-mr.md C, b5c-ia1.md 2-4, b5c-ia4.md", kind: discovery, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: Esh of the Storm and Tul of the Blizzard with Kalandra's Touch in the game (PoB counts KT as the other ring's base, CalcSetup.lua:1216-1220; wiki silent)"
  - "NOT VERIFIED: a Bound By Destiny 'N Hunter Items are Equipped' threshold reached through the copy in the game (PoB counts it; the wiki test only covers Shaper counts on The Eternity Shroud)"
  - "NOT VERIFIED: 'Left Ring slot:' / 'Right Ring slot:' lines on a copy - whether PoB doubles or drops them (copy reads slotModList[KT slot], CalcSetup.lua:1193; not run)"
  - "NOT VERIFIED: a corrupted Kalandra's Touch itself in PoB (code reading of CalcSetup.lua:1292-1297 only)"
  - "NOT VERIFIED: Mark of the Shaper / Mark of the Elder with KT as the opposite ring (code trace only)"
  - "Test rings in the mastery row are synthetic (no claim that '+X to Evasion Rating' is a rollable ring mod); all deltas are PoB removal/swap deltas on two sample builds, not game facts"
open_questions: []
```
