---
type: interaction
status: draft
pob_refs: [CostESInsteadOfManaOrLife, ESCost, ESPerSecondCost, ESHasCost, ESCostWarning]
source: "PoB 2.67.2 ModParser.lua:5312 / CalcOffence.lua:1763-1790 / Calcs.lua:407-421; item-analyst, tree-ascendancy-analyst (task 027); tasks/reports/021-gate1.md N10"
last_confirmed_patch: "3.29.x"
---

Whispers of Infinity turns every skill's mana (and life) cost into an ES cost and cuts max mana by 40-60%. That "downside" is the point of the item: never "fix" it by adding mana. PoB checks only the cost per use against the ES pool, not how much ES is spent per second versus recharge. Rules: [[Total skill cost must be sustainable]], [[Reservation must fit the pool]].

Pipeline: [[Receiving damage#Energy shield]] - skill costs are paid from the energy shield pool, so each use drains the same ES that protects against hits; recharge only helps between uses

```interaction
id: skill-cost-from-es
mechanic: "Skills Cost Energy Shield instead of Mana or Life (Whispers of Infinity; also Eldritch Battery keystone spends ES before mana)"
family: resource
pipeline_step: ["Receiving damage#Energy shield"]
pipeline_why: "skill costs are paid from the energy shield pool, so each use drains the same ES that protects against hits; recharge only helps between uses"
target: self
related: [max-res-equalise, arcane-surge]
pob:
  measured: full
  how: "ModParser.lua:5312 flag CostESInsteadOfManaOrLife; CalcOffence.lua:1763-1790 (comment 'Whispers of Infinity' at 1766), 1872: mana+life costs (upfront and per second) summed into ES cost, mana/life zeroed; affordability Calcs.lua:407-421 compares ESCost with the ES pool (warning Build.lua:2022-2030). Sustained ES drain vs recharge is NOT computed"
  config: []
  unparsed: []
model: null
providers:
  - {kind: unique, name: "Whispers of Infinity (Seaglass Amulet, Current variant 2)", slot: amulet, role: enables, target: self, text: "Skills Cost Energy Shield instead of Mana or Life; (40-60)% reduced maximum Mana; +(50-100) max ES; (10-15)% faster start of ES Recharge; added attack chaos per 100 max mana", source: "PoB Data/Uniques/amulet.lua:1411-1416; ModParser.lua:5312", pob: full, variant: "Current (pre-3.27.0 variant 1 had +(200-400) ES; the seed pin's +460 ES is outside both ranges)"}
  - {kind: keystone, name: "Eldritch Battery 56075", slot: tree, role: enables, target: self, text: "Spend Energy Shield before Mana for Skill Mana Costs; ES protects Mana instead of Life; 50% less ES Recharge Rate", source: "tree-ascendancy-analyst; TREE L67101 (tattoo TAT L455)", pob: partial}
  - {kind: keystone, name: "Chaos Inoculation 11455", slot: tree, role: enables, target: self, text: "Maximum Life becomes 1, immune to chaos; no cost effect itself; enabler for the Whispers + CI seed", source: "tree-ascendancy-analyst; TREE L74130", pob: full}
  - {kind: keystone, name: "Zealot's Oath 63425", slot: tree, role: sustains, target: self, text: "Life Regeneration is applied to Energy Shield instead", source: "tree-ascendancy-analyst; TREE L26697 (tattoo TAT L4882)", pob: full}
  - {kind: notable, name: "Sanctuary of Thought 29026 (Hierophant)", slot: tree, role: scales, target: self, text: "20% of Maximum Mana as Extra Max ES", source: "tree-ascendancy-analyst; TREE L15927", pob: full}
  - {kind: mastery, name: "Mana Mastery effect 12119", slot: tree, role: scales, target: self, text: "15% Mana Cost Efficiency (applies to the cost that becomes ES)", source: "tree-ascendancy-analyst; TREE L24357", pob: full}
  - {kind: notable, name: "Arcane Conservation 60085", slot: tree, role: scales, target: self, text: "20% Mana Cost Efficiency for Spells", source: "tree-ascendancy-analyst; TREE", pob: full}
makes_redundant:
  - {provider: "mana-based reservation and mana regen providers", when: "Whispers of Infinity worn", why: "max mana -40-60% and costs paid from ES: mana pool and regen no longer fund skills (reservation still uses the mana pool)", source: "build-strategist redundancy list; 021-gate1 N10"}
conflicts:
  - {with: "Blood Magic 57279, Sanguimancy 8982, Life Mastery effect 38454, Cannibalistic Rite 56359, Attack Mastery 19500", effect: "pay costs in Life instead", source: "tree-ascendancy-analyst"}
  - {with: "The Agnostic 19732", effect: "removes all ES: hard conflict", source: "tree-ascendancy-analyst"}
conditions:
  - {text: "ES cost per use must be below the ES pool; sustained cost per second must be matched by recharge/regen (not checked by PoB)", source: "Calcs.lua:407-421"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "Always while worn; sustainability is partial: ES spent per cast must be regenerated or recharged, PoB compares cost to pool per use only", source: "build-strategist table; Calcs.lua:407-421"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "Same, plus boss damage delays ES recharge, so the real margin is lower than PoB's", source: "build-strategist table"}
seeds: [FR]
sources:
  - {ref: "PoB ModParser.lua:5312, CalcOffence.lua:1763-1790, 1872, Calcs.lua:407-421, Build.lua:2022-2030", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/Uniques/amulet.lua:1411-1416", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/021-gate1.md N10", kind: discovery, patch: "3.29"}
not_verified:
  - "Whispers + CI combined in PoB (CalcOffence.lua:1766 was read only as a comment line)"
  - "Other pool converters (Waxen Soul, The Covenant, Prism Guardian) convert to Life, not ES; not checked against PoB"
open_questions:
  - "None."
```
