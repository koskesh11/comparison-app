---
type: interaction
status: draft
pob_refs: [ESCost, ManaCost, CostESInsteadOfManaOrLife, Mana, ManaReserved, ManaUnreserved, EnergyShield, Speed, FullDPS, TotalDPS]
source: "task 027 batch 2c item-analyst-fr.md (removal deltas, seed AutoBuilder/FR CoC Occu Three Dragons v4.xml, amulet item id 5, PoB 2.67.2, game 3.29); item text from the seed XML and PoB Data/Uniques/amulet.lua:1404-1416; ModCache.lua:19916"
last_confirmed_patch: "3.29.x"
---

Package note for Whispers of Infinity (Seaglass Amulet) in the FR v4 seed. The point of the item is "Skills Cost Energy Shield instead of Mana or Life" together with "51% reduced maximum Mana" and "8 to 25 Added Attack Chaos Damage per 100 Maximum Mana": the cost of every cast is paid from the ES pool and the small mana pool is mostly reserved. Per-line values are NOT MEASURED: the evidence has only the whole-item removal.
Mechanic of the point line: [[Skill cost from ES]].

Pipeline: [[Receiving damage#Energy shield]] - the skill cost becomes an ES drain (ESCost) taken from the same pool that absorbs hits; the added chaos damage per 100 maximum mana enters at [[Damage calculation#Flat damage]].

```interaction
id: unique-whispers-of-infinity
mechanic: "Unique package: Whispers of Infinity makes every skill cost Energy Shield instead of mana, cuts maximum mana by 51% (kept mostly reserved) and adds chaos damage to attacks per 100 maximum mana, on top of +460 maximum ES and 9% attack speed"
family: resource
target: self
pipeline_step: ["Receiving damage#Energy shield", "Damage calculation#Flat damage"]
pipeline_why: "the cost is paid from the ES pool (ES is the damage-absorbing layer); the per-100-mana chaos line is a flat added damage that only attack skills (Cyclone) use"
related: [skill-cost-from-es, mana-cost-efficiency, reservation-efficiency, energy-shield-hybrid, coc-trigger, es-recovery-keystones]
pob:
  measured: partial
  how: "Removal delta only (in memory, amulet id 5 emptied): FullDPS 57,001,026 -> 42,129,796 (-26.09%), FR skill DPS -25.88%, Cyclone TotalDPS 166,643 -> 3,909 (-97.65%). Cost paid from ES is parsed (CostESInsteadOfManaOrLife, ModCache.lua:19916): without the item ESCost 6/cast and 45.144 ES/s become ManaCost 6 and 42.066 mana/s. Other changes: ES 17,116 -> 14,541, Mana 523 -> 953 (the 51% reduced max mana is gone) with ManaReserved 517 -> 926 and ManaUnreserved 6 -> 27, mana regen 14.3 -> 26/s, ES regen 2250.6 -> 1929.4, attack speed 9% (Speed 7.524 -> 7.011, CoC trigger 7.524 -> 7.018/s), 'Allocates Tranquility' lost, added attack chaos damage per 100 max mana lost (Cyclone), condition UniqueItemInAmulet. No unmet requirements. A headless removal delta is not a game fact: it is PoB's single-enemy model, no per-line split was run."
  config: []
  unparsed:
    - "Whispers of Infinity: '8 to 25 Added Attack Chaos Damage per 100 Maximum Mana' as an exact string is not in ModCache.lua (NOT VERIFIED); the Cyclone -97.65% shows the effect works"
model: null
package:
  seed: "AutoBuilder/FR CoC Occu Three Dragons v4.xml"
  slot: Amulet
  base: "Seaglass Amulet"
  xml_item_id: 5
  variant: "none (no Variant lines in the XML); PoB lists Pre 3.27.0 and Current (amulet.lua:1406-1407). XML +460 maximum ES is outside both PoB ranges (200-400 and 50-100) and the 'faster start of Energy Shield Recharge' line is absent - NOT VERIFIED why; XML is Corrupted"
  removal: "FullDPS -26.09% (57,001,026 -> 42,129,796), Cyclone -97.65% - in-memory removal; PoB keeps the emptied slot's gems active, so the in-game loss is larger (the evidence names no socket group of this amulet)"
  lost_with_item:
    - "skills cost ES instead of mana: ESCost 6/cast and 45.144 ES/s become ManaCost 6 and 42.066 mana/s"
    - "ES 17,116 -> 14,541, ES regen 2250.6 -> 1929.4"
    - "51% reduced max mana gone: Mana 523 -> 953, ManaReserved 517 -> 926, ManaUnreserved 6 -> 27, mana regen 14.3 -> 26/s"
    - "9% increased Attack Speed: Speed 7.524 -> 7.011, CoC trigger 7.524 -> 7.018/s"
    - "Allocates Tranquility (crafted implicit): allocation lost"
    - "added attack chaos damage per 100 maximum mana (Cyclone)"
    - "condition UniqueItemInAmulet"
  downsides_that_are_the_point:
    - "51% reduced maximum Mana: the small mana pool (523) is the base of the item, it is mostly reserved (ManaReserved 517) and paid skill costs come from ES instead; per-line value NOT MEASURED"
  foulborn: "not Foulborn"
  obtainability: "PoB Source line: drops from Incarnation of Dread in Moment of Reverence (Data/Uniques/amulet.lua:1408, PoB 2.67.2, 3.29); wiki not fetched, price NOT VERIFIED. 'Allocates Tranquility' is {crafted} in the XML (an anoint/enchant on this copy, craft source NOT VERIFIED)"
providers:
  - {kind: unique, name: "Whispers of Infinity", slot: Amulet, role: enables, target: self, text: "Skills Cost Energy Shield instead of Mana or Life (ESCost 6/cast and 45.144 ES/s in the seed)", source: "Data/Uniques/amulet.lua:1416; Data/ModCache.lua:19916", pob: full}
  - {kind: unique, name: "Whispers of Infinity", slot: Amulet, role: scales, target: self, text: "8 to 25 Added Attack Chaos Damage per 100 Maximum Mana (seed XML wording; per-line value NOT MEASURED)", source: "Data/Uniques/amulet.lua:1412", pob: partial}
  - {kind: unique, name: "Whispers of Infinity", slot: Amulet, role: sustains, target: self, text: "+460 to maximum Energy Shield (seed XML; PoB variant ranges 50-100 / 200-400; per-line value NOT MEASURED, whole item ES -2,575)", source: "Data/Uniques/amulet.lua:1413-1414", pob: full}
  - {kind: unique, name: "Whispers of Infinity", slot: Amulet, role: blocks, target: self, text: "51% reduced maximum Mana (Mana 523 with the item, 953 without; per-line value NOT MEASURED)", source: "Data/Uniques/amulet.lua:1415", pob: full}
  - {kind: unique, name: "Whispers of Infinity", slot: Amulet, role: scales, target: self, text: "9% increased Attack Speed (XML implicit; whole item: Speed 7.524 vs 7.011 without; per-line value NOT MEASURED)", source: "seed XML item id 5 (line not in Data/Uniques/amulet.lua:1411)", pob: full}
  - {kind: unique, name: "Whispers of Infinity", slot: Amulet, role: enables, target: self, text: "{crafted} Allocates Tranquility (XML implicit; the allocation is lost with the item, its effect NOT MEASURED)", source: "seed XML item id 5; item-analyst-fr.md", pob: partial}
makes_redundant: []
conflicts: []
conditions:
  - {text: "Costs are paid from ES only while the item is worn; with ES 17,116 and ES regen 2250.6 the seed pays 45.144 ES/s", source: "item-analyst-fr.md (ESCost 6/cast, 45.144 ES/s)"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "static cost conversion and pool change; PoB uses the item's lines directly", source: "Data/ModCache.lua:19916"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "same; ES drain per second is the same, the pinnacle fight-length interaction is not run", source: "Data/ModCache.lua:19916"}
seeds: [FR]
sources:
  - {ref: "tasks/reports/027-evidence/partial/b2c/item-analyst-fr.md (removal deltas, Whispers of Infinity)", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/Uniques/amulet.lua:1404-1416; Data/ModCache.lua:19916", kind: pob, patch: "3.29"}
not_verified:
  - "Per-line values: only the whole-item removal was run, NOT MEASURED per line"
  - "PoB parse of '8 to 25 Added Attack Chaos Damage per 100 Maximum Mana' as an exact ModCache string"
  - "Why the XML values (+460 ES) differ from the PoB variant ranges and where the 9% attack speed comes from"
  - "Wiki obtainability, price and the Tranquility craft source"
open_questions:
  - "Is the 460 ES roll from corruption? The generator needs to know whether a copy like this can be sourced."
```
