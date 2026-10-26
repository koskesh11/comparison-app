---
type: interaction
status: draft
pob_refs: [CurseLimit, PowerChargesMax, CritChance, FullDPS, TotalDPS, ShockDuration, ManaReserved, Speed]
source: "task 027 batch 2c item-analyst-fr.md (removal deltas, seed AutoBuilder/FR CoC Occu Three Dragons v4.xml, ring item id 4, PoB 2.67.2, game 3.29); item text from the seed XML and PoB Data/Uniques/ring.lua:639-647; CalcPerform.lua:3216"
last_confirmed_patch: "3.29.x"
---

Package note for Anathema (Moonstone Ring) in the FR v4 seed. The point of the item is "Your Curse Limit is equal to your maximum Power Charges": with 7 maximum Power Charges the seed runs 5 curses (Assassin's Mark, Punishment, Despair, Temporal Chains, Enfeeble); without the ring the limit is 1 and only Enfeeble stays. The other lines (cast speed, Intelligence, Discipline aura effect) come on top. Per-line values are NOT MEASURED: the evidence has only the whole-item removal.
Mechanic of the point line: [[Curse limit]]; Marked enemy feeds crit chance and the CoC trigger rate ([[CoC trigger]]).

Pipeline: [[Damage calculation#Critical strike]] - the measured knock-on of the extra curses is the Marked condition (Assassin's Mark) raising crit chance; the other curses' pipeline steps are NOT VERIFIED here.

```interaction
id: unique-anathema
mechanic: "Unique package: Anathema sets the curse limit to maximum Power Charges (7 in the seed), which keeps five curses on the enemy instead of one, plus cast speed, Intelligence and 20% more Discipline aura effect"
family: buff
target: self
pipeline_step: ["Damage calculation#Critical strike"]
pipeline_why: "measured knock-on of losing the limit: Assassin's Mark (Marked) is dropped, crit chance 100 -> 98.43; Punishment, Despair, Temporal Chains steps not traced in the evidence"
related: [curse-limit, power-charges, assassins-mark, curse-application, coc-trigger, critical-strike-chance, aura-effect, determination-grace, shock, energy-shield-hybrid]
pob:
  measured: partial
  how: "Removal delta only (in memory, ring id 4 emptied): FullDPS 57,001,026 -> 31,580,237 (-44.60%), FR skill DPS -44.63%, Cyclone TotalDPS -32.99%. Curse limit 7 -> 1 (CurseLimitIsMaximumPowerCharges, Modules/CalcPerform.lua:3216; PowerChargesMax 7), so only Enfeeble stays of the five curses. Enemy condition Marked lost: CritChance 100 -> 98.43, CoC trigger rate 7.524 -> 7.406/s, Shock/Freeze chance 100 -> 83.4, ShockDuration 2.667 -> 2.0 s. Int 386 -> 343 (requirements still met, need 293). Discipline +20% aura effect lost: ES 17,116 -> 16,759, Mana 523 -> 509, ManaReserved 517 -> 504. 12% cast speed lost. A headless removal delta is not a game fact: it is PoB's single-enemy model, no per-line split was run."
  config: []
  unparsed:
    - "Anathema: '10% chance to gain a Power Charge when you Cast a Curse Spell' is not in ModCache (NOT VERIFIED whether PoB parses it; the curse limit reads maximum Power Charges, not current charges)"
model: null
package:
  seed: "AutoBuilder/FR CoC Occu Three Dragons v4.xml"
  slot: "Ring 1"
  base: "Moonstone Ring"
  xml_item_id: 4
  variant: "none (no Variant lines in the XML); XML is Corrupted; the Discipline line is the XML's single implicit (Implicits: 1), not the +ES implicit of ring.lua:643; XML +45 Intelligence and 10% Power Charge chance differ from the PoB ranges (30-40, 10-20) - NOT VERIFIED why (corruption or older roll)"
  removal: "FullDPS -44.60% (57,001,026 -> 31,580,237) - in-memory removal; PoB keeps the emptied slot's gems active, so the in-game loss is larger (the evidence names no socket group of this ring)"
  lost_with_item:
    - "curse limit 7 -> 1: Assassin's Mark, Punishment, Despair, Temporal Chains lost; only Enfeeble stays"
    - "enemy Marked: CritChance 100 -> 98.43, CoC trigger 7.524 -> 7.406/s, Shock/Freeze chance 100 -> 83.4, ShockDuration 2.667 -> 2.0 s"
    - "Int 386 -> 343 (requirements still met)"
    - "Discipline +20% aura effect (ES 17,116 -> 16,759, Mana 523 -> 509, ManaReserved 517 -> 504)"
    - "12% increased Cast Speed"
  downsides_that_are_the_point: []
  foulborn: "not Foulborn"
  obtainability: "NOT VERIFIED: no source in the evidence (PoB ring.lua:639-647 shows no Source line); wiki not fetched for this note"
providers:
  - {kind: unique, name: "Anathema", slot: "Ring 1", role: enables, target: self, text: "Your Curse Limit is equal to your maximum Power Charges (curse limit 1 -> 7 in the seed)", source: "Data/Uniques/ring.lua:647; Modules/CalcPerform.lua:3216", pob: full}
  - {kind: unique, name: "Anathema", slot: "Ring 1", role: scales, target: self, text: "10% chance to gain a Power Charge when you Cast a Curse Spell (seed XML wording; PoB range 10-20%)", source: "Data/Uniques/ring.lua:646", pob: none}
  - {kind: unique, name: "Anathema", slot: "Ring 1", role: scales, target: self, text: "12% increased Cast Speed (per-line value NOT MEASURED; part of the whole-item delta)", source: "Data/Uniques/ring.lua:645", pob: full}
  - {kind: unique, name: "Anathema", slot: "Ring 1", role: sustains, target: self, text: "+45 to Intelligence (seed XML; per-line value NOT MEASURED; Int 386 -> 343 without the ring, requirements still met)", source: "Data/Uniques/ring.lua:644", pob: full}
  - {kind: unique, name: "Anathema", slot: "Ring 1", role: scales, target: self, text: "Discipline has 20% increased Aura Effect (XML implicit; per-line value NOT MEASURED; whole-item delta shows ES -357, Mana -14, ManaReserved -13)", source: "tasks/reports/027-evidence/partial/b2c/item-analyst-fr.md; seed XML item id 4 (line not in Data/Uniques/ring.lua:643-647)", pob: partial}
makes_redundant: []
conflicts: []
conditions:
  - {text: "Curse limit equals maximum Power Charges, not current charges, so the ring works without gaining a charge; the build needs maximum Power Charges (7 in the seed)", source: "Modules/CalcPerform.lua:3216; item-analyst-fr.md (PowerChargesMax 7)"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "curse limit is a static output; the curses themselves still need their own application (curse-application)", source: "Modules/CalcPerform.lua:3216"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "same; boss curse effect and curse-immunity are not modelled by the evidence", source: "Modules/CalcPerform.lua:3216"}
seeds: [FR]
sources:
  - {ref: "tasks/reports/027-evidence/partial/b2c/item-analyst-fr.md (removal deltas, Anathema)", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/Uniques/ring.lua:639-647; Modules/CalcPerform.lua:3216", kind: pob, patch: "3.29"}
not_verified:
  - "Per-line values: only the whole-item removal was run, NOT MEASURED per line"
  - "Whether PoB parses '10% chance to gain a Power Charge when you Cast a Curse Spell'"
  - "Obtainability, price, corruption state origin of the Discipline implicit and the +45 Int roll"
  - "Pipeline steps of Punishment, Despair, Temporal Chains and Enfeeble"
open_questions:
  - "Is the Discipline aura-effect line a Vaal corrupted implicit the user chose, or an item roll? The generator needs to know whether it can be reproduced."
```
