---
type: interaction
status: draft
pob_refs: [CostESInsteadOfManaOrLife, ESCost, ESPerSecondCost, ESHasCost, ESCostWarning, ESCostEfficiency, CostEfficiency, ManaCostEfficiency]
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
related: [max-res-equalise, arcane-surge, mana-cost-efficiency]
pob:
  measured: full
  how: "ModParser.lua:5312 flag CostESInsteadOfManaOrLife; CalcOffence.lua:1763-1790 (comment 'Whispers of Infinity' at 1766), 1872: mana+life costs (upfront and per second) summed into ES cost, mana/life zeroed; affordability Calcs.lua:407-421 compares ESCost with the ES pool (warning Build.lua:2022-2030). Sustained ES drain vs recharge is NOT computed. ES pass after the conversion: the mana and life cost (post support multiplier) is added to the ES base (CalcOffence.lua:1763-1790), then ONLY ESCost/Cost increased and less/more and ESCostEfficiency/CostEfficiency apply (1811-1846), then flat Cost (totalCost) is added. Mana-specific mods do NOT follow the cost. Headless probe on Worb.xml, Winter Orb base cost 10, flag 'Skills Cost Energy Shield instead of Mana or Life': no extra mod ES 10; +50% Mana Cost Efficiency ES 10 (mana-only: 7 without the flag); +50% Cost Efficiency ES 7; +50% ES Cost Efficiency ES 7; +100% increased Mana Cost ES 10; 20% reduced Mana Cost ES 10; 20% less Mana Cost ES 10; +5 to Total Mana Cost ES 15. Wiki: 'energy shield costs are not affected by modifiers specific for their original cost, such as Inspiration Support. Generic cost modifiers like Tireless do apply.' (Whispers of Infinity rev 1605628)"
  config: []
  unparsed: []
model: null
providers:
  - {kind: unique, name: "Whispers of Infinity (Seaglass Amulet, Current variant 2)", slot: amulet, role: enables, target: self, text: "Skills Cost Energy Shield instead of Mana or Life; (40-60)% reduced maximum Mana; +(50-100) max ES; (10-15)% faster start of ES Recharge; added attack chaos per 100 max mana", source: "PoB Data/Uniques/amulet.lua:1411-1416; ModParser.lua:5312", pob: full, variant: "Current (pre-3.27.0 variant 1 had +(200-400) ES; the seed pin's +460 ES is outside both ranges)"}
  - {kind: keystone, name: "Eldritch Battery 56075", slot: tree, role: enables, target: self, text: "Spend Energy Shield before Mana for Skill Mana Costs; ES protects Mana instead of Life; 50% less ES Recharge Rate", source: "tree-ascendancy-analyst; TREE L67101 (tattoo TAT L455)", pob: partial}
  - {kind: keystone, name: "Chaos Inoculation 11455", slot: tree, role: enables, target: self, text: "Maximum Life becomes 1, immune to chaos; no cost effect itself; enabler for the Whispers + CI seed", source: "tree-ascendancy-analyst; TREE L74130", pob: full}
  - {kind: keystone, name: "Zealot's Oath 63425", slot: tree, role: sustains, target: self, text: "Life Regeneration is applied to Energy Shield instead", source: "tree-ascendancy-analyst; TREE L26697 (tattoo TAT L4882)", pob: full}
  - {kind: notable, name: "Sanctuary of Thought 29026 (Hierophant)", slot: tree, role: scales, target: self, text: "20% of Maximum Mana as Extra Max ES", source: "tree-ascendancy-analyst; TREE L15927", pob: full}
  - {kind: mastery, name: "Mana Mastery effect 12119", slot: tree, role: blocks, target: self, text: "15% increased Mana Cost Efficiency: mana-specific, does NOT reduce the ES cost under Whispers (PoB probe: 10 -> 10)", source: "PoB TreeData/3_29/tree.lua:24354-24357; headless probe 2026-10-26 on Worb.xml; wiki Whispers of Infinity rev 1605628", pob: none}
  - {kind: notable, name: "Arcane Conservation 60085", slot: tree, role: blocks, target: self, text: "20% increased Mana Cost Efficiency of Spells: mana-specific, does NOT reduce the ES cost under Whispers (same probe)", source: "PoB TreeData/3_29/tree.lua:59080-59092; headless probe 2026-10-26", pob: none}
  - {kind: notable, name: "Contemplative Meditation 20261", slot: tree, role: scales, target: self, text: "20% increased Cost Efficiency (generic): divides the converted ES cost (probe: +50% Cost Efficiency 10 -> 7)", source: "PoB TreeData/3_29/tree.lua:33859-33872; CalcOffence.lua:1811; headless probe 2026-10-26", pob: full}
  - {kind: notable, name: "Tireless 65108", slot: tree, role: scales, target: self, text: "10% increased maximum Life; 10% increased Cost Efficiency (generic); named by the wiki as a modifier that applies to the ES cost", source: "PoB TreeData/3_29/tree.lua:27846-27858; wiki Whispers of Infinity rev 1605628", pob: full}
  - {kind: notable, name: "Life and Cost Efficiency 7374 / 3533 / 11088", slot: tree, role: scales, target: self, text: "5% increased maximum Life; 5% increased Cost Efficiency (generic)", source: "PoB TreeData/3_29/tree.lua:27792-27834", pob: full}
makes_redundant:
  - {provider: "mana-based reservation and mana regen providers", when: "Whispers of Infinity worn", why: "max mana -40-60% and costs paid from ES: mana pool and regen no longer fund skills (reservation still uses the mana pool)", source: "build-strategist redundancy list; 021-gate1 N10"}
  - {provider: "Inspiration (support), Mana Mastery 12119, Arcane Conservation 60085, Openness 20968, 'reduced / less Mana Cost' lines", when: "Whispers of Infinity worn", why: "mana-specific cost mods do not apply to the ES cost (PoB probe, wiki); only generic Cost Efficiency, ES Cost Efficiency and flat total cost do", source: "headless probe 2026-10-26 on Worb.xml; wiki Whispers of Infinity rev 1605628; PoB CalcOffence.lua:1811-1846"}
conflicts:
  - {with: "Blood Magic 57279, Sanguimancy 8982, Life Mastery effect 38454, Cannibalistic Rite 56359, Attack Mastery 19500", effect: "pay costs in Life instead", source: "tree-ascendancy-analyst"}
  - {with: "The Agnostic 19732", effect: "removes all ES: hard conflict", source: "tree-ascendancy-analyst"}
conditions:
  - {text: "ES cost per use must be below the ES pool; sustained cost per second must be matched by recharge/regen (not checked by PoB)", source: "Calcs.lua:407-421"}
  - {text: "reduced or less cost lines: since 3.29.0 the tree and uniques use Cost Efficiency (wiki Cost, version row 3.29.0), which divides the ES cost at CalcOffence.lua:1836 after increased and less/more; Cost Efficiency of 100% or more would make the cost 2,147,483,647 in game (wiki)", source: "wiki Cost rev 1703053; PoB CalcOffence.lua:1811-1840"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "Always while worn; sustainability is partial: ES spent per cast must be regenerated or recharged, PoB compares cost to pool per use only", source: "build-strategist table; Calcs.lua:407-421"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "Same, plus boss damage delays ES recharge, so the real margin is lower than PoB's", source: "build-strategist table"}
seeds: [FR]
sources:
  - {ref: "PoB ModParser.lua:5312, CalcOffence.lua:1763-1790, 1872, Calcs.lua:407-421, Build.lua:2022-2030", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/Uniques/amulet.lua:1411-1416", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/021-gate1.md N10", kind: discovery, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Whispers_of_Infinity (rev 1605628)", kind: wiki, patch: "3.29"}
not_verified:
  - "Whispers + CI combined in PoB (CalcOffence.lua:1766 was read only as a comment line)"
  - "Other pool converters (Waxen Soul, The Covenant, Prism Guardian) convert to Life, not ES; not checked against PoB"
  - "wiki Whispers of Infinity (3.27.0, undocumented): costs over time (link skills, Bladefall) cost DOUBLE when paid in ES; PoB's ESPerSecondCost for link skills not checked against that"
  - "Mana Mastery 12119 and Arcane Conservation 60085 were listed in the first version of this note as acting on the ES cost: corrected here by PoB probe and wiki; if the user has the in-game number, compare"
open_questions:
  - "None."
```
