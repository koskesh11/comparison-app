---
type: interaction
status: draft
pob_refs: [ElementalResistMaxIsHighestResistMax, FireResistMax, ColdResistMax, LightningResistMax]
source: "PoB 2.67.2 CalcDefence.lua:574-590 / ModParser.lua:4846; item-analyst, tree-ascendancy-analyst (task 027); tasks/reports/021-gate1.md N10"
last_confirmed_patch: "3.29.x"
---

Melding of the Flesh (jewel) and the Reliquarian notable of the same name cap all three elemental resistances at your highest maximum elemental resistance. The big resistance and max-res malus is the price; the line only pays off if one element has a high maximum from another source. Never "fix" the malus: it is the item.

```interaction
id: max-res-equalise
mechanic: "Elemental Resistances are capped by your highest Maximum Elemental Resistance instead: fire, cold and lightning max all become the highest one"
family: defence
target: self
related: [skill-cost-from-es]
pob:
  measured: full
  how: "ModParser.lua:4846 flag ElementalResistMaxIsHighestResistMax; CalcDefence.lua:575-590 finds the highest elemental max and sets all three ResistMax to it (OVERRIDE) before the per-element loop at 591+, so max-res bonuses count. No red lines on either variant"
  config: []
  unparsed: []
model: null
providers:
  - {kind: jewel, name: "Melding of the Flesh (Cobalt Jewel, Current variant 2, Limited to 1)", slot: jewel, role: enables, target: self, text: "-(70-80)% all Elemental Resistances; -(4-6)% to all maximum Elemental Resistances; Elemental Resistances are capped by your highest Maximum Elemental Resistance instead", source: "PoB Data/Uniques/jewel.lua:440-442; CalcDefence.lua:574-590; 021-gate1 N10", pob: full}
  - {kind: ascendancy, name: "Melding of the Flesh 2768 (Reliquarian)", slot: tree, role: enables, target: self, text: "-5% to all maximum Elemental Resistances; Elemental Resistances are capped by your highest Maximum Elemental Resistance instead", source: "tree-ascendancy-analyst; TREE L22306", pob: full}
  - {kind: ascendancy, name: "Valako, Storm's Embrace 32249 (Chieftain)", slot: tree, role: scales, target: self, text: "Modifiers to Maximum Fire Resistance also apply to Maximum Cold and Lightning Resistances", source: "tree-ascendancy-analyst; TREE L16105", pob: full}
  - {kind: unique, name: "Kaltenhalt / Kaltensoul / Seablister / Aegis Aurora / Brine Crown", slot: shield, role: scales, target: self, text: "+5/+5/+3/+5/+3% to maximum Cold Resistance (single-element highest max)", source: "PoB Data/Uniques/shield.lua:336,352,870,946; helmet.lua:1086", pob: full}
  - {kind: unique, name: "Rise of the Phoenix", slot: shield, role: scales, target: self, text: "+8%/+5% maximum Fire Resistance", source: "PoB Data/Uniques/shield.lua:1041-1042", pob: full}
  - {kind: unique, name: "Agnerod South", slot: staff, role: scales, target: self, text: "+5% maximum Lightning Resistance", source: "PoB Data/Uniques/staff.lua:57", pob: full}
  - {kind: unique, name: "Divination Distillate", slot: flask, role: scales, target: self, text: "+6%/+4% all max elemental res during Effect", source: "PoB Data/Uniques/flask.lua:91-92", pob: full}
  - {kind: notable, name: "Winter Prowler 38683", slot: tree, role: scales, target: self, text: "+2% Cold Maximum Resistance", source: "tree-ascendancy-analyst; TREE L88852", pob: full}
  - {kind: mastery, name: "Cold Mastery effect 33129", slot: tree, role: scales, target: self, text: "+1% Cold DoT Multiplier per 4% Overcapped Cold Resistance (overcap synergy)", source: "tree-ascendancy-analyst; TREE L54782", pob: partial}
  - {kind: tattoo, name: "Honoured Tattoo of the Makanga", slot: tree, role: scales, target: self, text: "+2% to all maximum Resistances (per-element Makanga +1%)", source: "tree-ascendancy-analyst; TAT L889", pob: full}
makes_redundant:
  - {provider: "Saffell's Frame (+4% all maximum Resistances)", when: "Melding equalise active", why: "already raises ALL maxes, so it gains nothing from equalisation (it still adds its +4%)", source: "item-analyst; shield.lua:1064"}
conflicts:
  - {with: "Loreweave (Your Maximum Resistances are (76-78)%)", effect: "sets max by OVERRIDE; the Melding block reads Override first, so Loreweave's value becomes the highest; not run, reading only", source: "item-analyst; body.lua:1101; CalcDefence.lua:579"}
conditions:
  - {text: "useless unless some element has a highest max above 75 from another source; the FR source of the highest max was not isolated", source: "item-analyst (seed pin)"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "Static EHP effect while worn", source: "build-strategist table"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "Static EHP effect while worn", source: "build-strategist table"}
seeds: [FR]
sources:
  - {ref: "PoB CalcDefence.lua:574-590, ModParser.lua:4846", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/Uniques/jewel.lua:440-442", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/021-gate1.md N10", kind: discovery, patch: "3.29"}
not_verified:
  - "Which source gives the FR build its highest maximum resistance"
  - "Loreweave interaction (not run)"
  - "Sums of caps for the actual seed (computed by the engine, not here)"
open_questions:
  - "None."
```
