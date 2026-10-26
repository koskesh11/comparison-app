---
type: interaction
status: draft
pob_refs: [Str, Dex, Evasion, FireResist, ColdResist, FullDPS, TotalDPS]
source: "task 027 batch 2c item-analyst-fr.md (removal delta, seed AutoBuilder/FR CoC Occu Three Dragons v4.xml, belt item id 1, PoB 2.67.2, game 3.29); item text from the seed XML and PoB Data/Uniques/belt.lua:542-552; CalcPerform.lua:1578-1599; ModParser.lua:5269-5270; ModCache.lua:17565,17570; vault Gaps/Mageblood flasks"
last_confirmed_patch: "3.29.x"
---

Package note for Mageblood (Heavy Belt) in the FR v4 seed. The point of the item is "Leftmost 4 Magic Utility Flasks constantly apply their Flask Effects to you": four utility flasks (Quicksilver, Bismuth, Sapphire, Topaz in the seed) are on all the time, at the price that they cannot be used or removed. The belt also carries Strength, Dexterity and fire and cold resistance. The audit blind spot (PoB re-adds the saved flasks) is in the gap note [[Mageblood flasks]], not repeated here. Per-line values are NOT MEASURED: the evidence has only the whole-item removal.
Flask mechanics: [[Flask uptime]], [[Offensive utility flasks]], [[Defensive utility flasks]].

Pipeline: [[Receiving damage#Resistances]] - the always-on flask effects (and the belt's own fire and cold resistance) enter as ordinary modifiers; the per-flask pipeline steps are NOT VERIFIED (flask effect values were not read).

```interaction
id: unique-mageblood
mechanic: "Unique package: Mageblood keeps the leftmost four Magic Utility Flasks permanently active (they cannot be used or removed), plus Strength, Dexterity and fire and cold resistance that meet gem requirements"
family: buff
target: self
pipeline_step: ["Receiving damage#Resistances"]
pipeline_why: "the flask effects and the belt resistances are ordinary modifiers applied to the player; which pipeline step each flask hits depends on the flask and was not traced"
related: [flask-uptime, offensive-utility-flasks, defensive-utility-flasks, life-mana-flasks, max-resistances]
pob:
  measured: partial
  how: "Removal delta only (in memory, belt id 1 emptied): FullDPS 57,001,026 -> 57,000,967 (-0.0001%), Cyclone TotalDPS -0.04%. PoB still applies all 5 flasks because every Flask slot is ticked active (Mageblood only adds the 4 magic utility flasks to env.flasks, Modules/CalcPerform.lua:1578-1599; env.flasks unchanged in the run), so the real loss (4 flasks, must be used by hand, uptime) is NOT in the number. Other changes: Str 159 -> 126, Dex 128 -> 85 (UNMET Dex for 6 gems: Cyclone 98, Arctic Armour 98, Withering Step 98, Temporal Chains 100, Greater Volley 111, Mark On Hit 111), Evasion 336 -> 325, +24% fire and +18% cold resistance (still capped), condition UniqueItemInBelt. A headless removal delta is not a game fact: it is PoB's single-enemy model with all flasks ticked."
  config: []
  unparsed:
    - "Mageblood: 'Magic Utility Flasks cannot be Used' -> nil (Data/ModCache.lua:17565)"
    - "Mageblood: 'Magic Utility Flask Effects cannot be removed' -> nil (Data/ModCache.lua:17570)"
model: null
package:
  seed: "AutoBuilder/FR CoC Occu Three Dragons v4.xml"
  slot: Belt
  base: "Heavy Belt"
  xml_item_id: 1
  variant: "none (no Variant lines in the XML); XML wording 'Leftmost 4' = top roll of PoB's (2-4) (belt.lua:551); the +35 Strength line is the XML's single implicit (Implicits: 1)"
  removal: "FullDPS -0.0001% (57,001,026 -> 57,000,967), Cyclone -0.04%, Dex 128 -> 85 leaves the Dex requirement of 6 gems unmet - in-memory removal; PoB keeps the emptied slot's gems active and keeps applying all 5 flasks, so the in-game loss is larger"
  lost_with_item:
    - "the four always-on utility flasks (Quicksilver, Bismuth, Sapphire, Topaz in the seed): not in PoB's number, since PoB applies them whether ticked or not"
    - "Str 159 -> 126, Dex 128 -> 85: Dex requirement of 6 gems unmet (Cyclone 98, Arctic Armour 98, Withering Step 98, Temporal Chains 100, Greater Volley 111, Mark On Hit 111)"
    - "Evasion 336 -> 325"
    - "+24% fire resistance, +18% cold resistance (still capped, no output change)"
    - "condition UniqueItemInBelt"
  downsides_that_are_the_point:
    - "Magic Utility Flasks cannot be Used; Magic Utility Flask Effects cannot be removed: the flasks are a permanent buff instead of an activated one (no manual timing, no removal by effects); both lines unparsed in PoB, per-line value NOT MEASURED"
  foulborn: "not Foulborn in the seed (a Foulborn version says 'Rightmost', vault gap note)"
  obtainability: "NOT VERIFIED: no source in the evidence (PoB belt.lua:542-552 shows no Source line); wiki not fetched for this note"
providers:
  - {kind: unique, name: "Mageblood", slot: Belt, role: enables, target: self, text: "Leftmost 4 Magic Utility Flasks constantly apply their Flask Effects to you (PoB picks the first N magic utility flasks in slot order, ticked or not; roll 2-4)", source: "Data/Uniques/belt.lua:551; Modules/ModParser.lua:5269-5270; Modules/CalcPerform.lua:1578-1599", pob: partial}
  - {kind: unique, name: "Mageblood", slot: Belt, role: blocks, target: self, text: "Magic Utility Flasks cannot be Used", source: "Data/Uniques/belt.lua:550; Data/ModCache.lua:17565", pob: none}
  - {kind: unique, name: "Mageblood", slot: Belt, role: blocks, target: self, text: "Magic Utility Flask Effects cannot be removed", source: "Data/Uniques/belt.lua:552; Data/ModCache.lua:17570", pob: none}
  - {kind: unique, name: "Mageblood", slot: Belt, role: sustains, target: self, text: "+35 to Strength and +44 to Dexterity (seed XML; per-line value NOT MEASURED; Dex 128 -> 85 without the belt leaves 6 gems unmet)", source: "Data/Uniques/belt.lua:546-547", pob: full}
  - {kind: unique, name: "Mageblood", slot: Belt, role: sustains, target: self, text: "+24% to Fire Resistance and +18% to Cold Resistance (seed XML; still capped without the belt, no output change)", source: "Data/Uniques/belt.lua:548-549", pob: full}
makes_redundant: []
conflicts: []
conditions:
  - {text: "Only MAGIC utility flasks count; the leftmost N in slot order are chosen, so flask slot order decides which flasks are permanent", source: "Modules/CalcPerform.lua:1578-1599; vault Gaps/Mageblood flasks.md"}
  - {text: "Audit caveat: PoB re-adds each saved flask from itemsTab.items, so a calc override of a Mageblood flask does not replace it; test by swapping the flask in place", source: "Modules/CalcPerform.lua:1582-1593; vault Gaps/Mageblood flasks.md"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "constantly applied by the item text; PoB applies the 4 magic utility flasks without any tick", source: "Data/Uniques/belt.lua:551; Modules/CalcPerform.lua:1578-1599"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "same; PoB also keeps all 5 flasks on (every Flask slot ticked) so the number does not show the real loss", source: "Modules/CalcPerform.lua:1578-1599; item-analyst-fr.md"}
seeds: [FR]
sources:
  - {ref: "tasks/reports/027-evidence/partial/b2c/item-analyst-fr.md (removal deltas, Mageblood)", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/Uniques/belt.lua:542-552; Modules/CalcPerform.lua:1578-1599; Modules/ModParser.lua:5269-5270", kind: pob, patch: "3.29"}
not_verified:
  - "Per-line values: only the whole-item removal was run, NOT MEASURED per line"
  - "What each of the four flasks is worth (flask effect values not read; names from the removal-delta text)"
  - "Obtainability, price, wiki revision"
open_questions:
  - "Which four flasks should be the leftmost? The generator needs the user's preference between the seed's Quicksilver / Bismuth / Sapphire / Topaz and offensive options."
```
