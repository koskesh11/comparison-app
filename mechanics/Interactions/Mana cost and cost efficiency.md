---
type: interaction
status: draft
pob_refs: [ManaCost, ManaCostRaw, ManaPerSecondCost, ManaRegenRecovery, ManaUnreserved, SupportManaMultiplier, ManaCostEfficiency, CostEfficiency, ESCostEfficiency, LifeCostEfficiency, CostLifeInsteadOfMana, CostESInsteadOfManaOrLife, multiplierChannelling]
source: "PoB 2.67.2 CalcOffence.lua:1692-1900, 5917-5955 / CalcActiveSkill.lua:524 / CalcDefence.lua:1313 / sup_str.lua:4604 / sup_int.lua:2538; wiki Cost rev 1703053, Whispers of Infinity rev 1605628, Inspiration Support rev 1681590; headless probes on Worb.xml (2026-10-26); skill-gem-analyst (task 027 batch 4)"
last_confirmed_patch: "3.29.x"
---

Every skill use pays a cost; PoB computes the per-use cost (ManaCost) and the cost per second (use rate x cost), and the build is only sustainable if the SUM over all skills used together stays below the regeneration. The order matters: support multipliers act first, then increased/less, then Cost Efficiency divides, then flat "total cost" is added; since 3.29.0 the passive-tree and many unique "reduced cost" sources are Cost Efficiency instead. Mana-specific modifiers (Inspiration, Mana Cost Efficiency, "increased Mana Cost") stop working once the cost is paid in Life (Lifetap, Blood Magic) or ES (Whispers of Infinity); only generic Cost Efficiency and flat total cost still apply. Rules: [[Total skill cost must be sustainable]], [[Reservation must fit the pool]]; cost paid in ES: [[Skill cost from ES]]; mana spent counters: [[Arcane surge]], [[Channelling]].

Pipeline: [[Damage calculation#Hit rate]] - cost is not a damage step; the per-use cost has its own order (support multiplier, increased/less, Cost Efficiency, flat) and the cost per second is that cost times the same cast/attack rate that sets the hit rate

```interaction
id: mana-cost-efficiency
mechanic: "Skill cost per use = floor(base x support-multiplier product) -> x (1 + increased) -> x less/more (Inspiration -34%, Focused Channelling up to +100%) -> divided by (1 + Cost Efficiency) -> rounded -> plus flat total cost; cost per second = cost x use rate; mana-specific modifiers do not follow the cost into Life or ES"
family: resource
pipeline_step: ["Damage calculation#Hit rate"]
pipeline_why: "cost is not a damage step; the per-use cost has its own order (support multiplier, increased/less, Cost Efficiency, flat) and the cost per second is that cost times the same cast/attack rate that sets the hit rate"
target: self
related: [skill-cost-from-es, arcane-surge, channelling]
pob:
  measured: partial
  how: "CalcOffence.lua:1692 comment 'may be slightly off due to rounding differences'. Per-use cost: base = round(gem cost / data.costs Divisor, 2) (1721); support multiplier = product of every support manaMultiplier ('SupportManaMultiplier' MORE, CalcActiveSkill.lua:524) floored to 4 digits (1713); finalBaseCost = floor(base x mult) + added no-mult cost (1738); then increased: ceil if the sum is negative else floor (1816-1822); then the 'ManaCost' more/less factor and the generic 'Cost' more/less factor, each ceil if below 1 else floor (1823-1833; Inspiration is a ManaCost MORE, Focused Channelling is a Cost MORE per second channelled, sup_str.lua:4604-4620, sup_int.lua:2538-2552); then divided by calcLib.mod(ManaCostEfficiency, CostEfficiency) (1811, 1836); upfront costs rounded to a whole number (1837-1839, 'round' = nearest); then flat 'Cost' / 'ManaCost' BASE (totalCost) added last (1840); hybrid life/mana mastery splits afterwards (1841-1843). Cost per second for upfront costs = cost x Speed (/ repeats), per trap/totem/cast rate (CalcOffence.lua:5917-5948), output ManaPerSecondCost; sustain margin = ManaRegenRecovery (CalcDefence.lua:1313: regen - degen + recovery) minus the sum of ManaPerSecondCost over skills used together (engine/costs.py:11-13, 137-157). Lifetap / Blood Magic: the post-multiplier mana cost is moved into the Life cost (1743-1754) and the Life pass applies only LifeCost/Cost and LifeCostEfficiency/CostEfficiency mods. NOT modelled: Eldritch Battery spending ES before mana (ModCache.lua:21856 c['Spend Energy Shield before Mana for Skill Mana Costs']={{},nil}; ModParser.lua:2320 maps it to {}), the 'costs over time double when paid in ES' effect of Whispers (wiki), Inspiration / Arcane Surge / Kitava's Thirst 'mana spent' counters. Measured on Worb.xml, Winter Orb L21 (gem cost 4, support product 2.6364): 4 x 2.6364 = 10.5456 -> ManaCost 10 (ManaCostRaw 10.5456), Speed 9.568 -> ManaPerSecondCost 95.68, ManaRegenRecovery 150.8; with Inspiration L20 added to the group: product 3.1636 (x1.2), moreMana 0.66, floor(12.6544) = 12 -> ceil(12 x 0.66) = 8 (ManaCostRaw 8.351904), ManaPerSecondCost 76.544 (net x0.792 of the previous cost, not x0.66); Rue Worb.xml with 3 s channelled: Cost MORE 1.6, 10 x 1.6 = ManaCost 16, ManaPerSecondCost 154.24"
  config:
    - {var: multiplierChannelling, default: 0, ref: "ConfigOptions.lua:1274-1276", class: c}
  unparsed:
    - "Eldritch Battery 56075: Spend Energy Shield before Mana for Skill Mana Costs (ModCache.lua:21856 = {{}, nil}: parsed to nothing, no ES spending of mana costs)"
model: null
providers:
  - {kind: support, name: "Support gem mana multipliers (all supports in the link group)", slot: any, role: scales, target: self, text: "each support has a manaMultiplier per level; PoB multiplies them (product, floored to 4 digits) before any other cost mod. Worb Winter Orb group: 2.6364", source: "PoB CalcActiveSkill.lua:524; CalcOffence.lua:1713; Data/Skills/sup_str.lua:4604-4670", pob: full}
  - {kind: support, name: "Inspiration", slot: any, role: scales, target: self, text: "L20: 34% less Mana Cost (ManaCost MORE) but its own cost multiplier x1.2; net about -21% (Winter Orb 10 -> 8 in PoB). Lost when the cost is paid in Life or ES (wiki: 'not affected by modifiers specific for their original cost, such as Inspiration Support')", source: "PoB Data/Skills/sup_str.lua:4604-4670; wiki Whispers of Infinity rev 1605628; headless probe 2026-10-26", pob: full}
  - {kind: support, name: "Focused Channelling", slot: any, role: scales, target: self, text: "Cost MORE 20% per second channelled, cap 100% (L20 and all levels); needs config multiplierChannelling, else PoB shows cost +0%", source: "PoB Data/Skills/sup_int.lua:2538-2552; ConfigOptions.lua:1274-1276", pob: config}
  - {kind: support, name: "Lifetap", slot: any, role: blocks, target: self, text: "Supported Skills Cost Life instead of Mana: mana-specific cost mods stop applying, generic ones still do (wiki: 'not a conversion mechanic')", source: "wiki Lifetap Support rev 1682175; PoB CalcOffence.lua:1743-1754; ModParser.lua:2277", pob: full}
  - {kind: keystone, name: "Blood Magic 57279", slot: tree, role: blocks, target: self, text: "Skills Cost Life instead of Mana; same PoB path as Lifetap", source: "PoB TreeData/3_29/tree.lua:25714-25720; ModParser.lua:2274-2277", pob: full}
  - {kind: unique, name: "Whispers of Infinity (Seaglass Amulet)", slot: amulet, role: blocks, target: self, text: "Skills Cost Energy Shield instead of Mana or Life; Mana Cost Efficiency, increased/less Mana Cost and Inspiration do not reach the ES cost, generic Cost Efficiency and flat total cost do", source: "wiki Whispers of Infinity rev 1605628; PoB ModParser.lua:5312, CalcOffence.lua:1763-1790; headless probe 2026-10-26", pob: full}
  - {kind: keystone, name: "Eldritch Battery 56075", slot: tree, role: blocks, target: self, text: "Spend Energy Shield before Mana for Skill Mana Costs: still a mana cost (mana-specific mods apply) but not mana spent (no Arcane Surge / Inspiration progress)", source: "wiki Cost rev 1703053; wiki Arcane Surge Support rev 1700912; PoB ModCache.lua:21856", pob: none}
  - {kind: mastery, name: "Mana Mastery effect 12119", slot: tree, role: scales, target: self, text: "15% increased Mana Cost Efficiency", source: "PoB TreeData/3_29/tree.lua:24354-24357", pob: full}
  - {kind: notable, name: "Arcane Conservation 60085", slot: tree, role: scales, target: self, text: "10% increased Cast Speed; 20% increased Mana Cost Efficiency of Spells", source: "PoB TreeData/3_29/tree.lua:59080-59092; wiki Version 3.29.0 (new cluster)", pob: full}
  - {kind: notable, name: "Contemplative Meditation 20261", slot: tree, role: scales, target: self, text: "8% increased Reservation Efficiency of Skills; 20% increased Cost Efficiency (generic: also works when the cost is paid in Life or ES)", source: "PoB TreeData/3_29/tree.lua:33859-33872", pob: full}
  - {kind: notable, name: "Openness 20968", slot: tree, role: scales, target: self, text: "+30 to maximum Mana; 20% increased maximum Mana; 15% increased Mana Cost Efficiency", source: "PoB TreeData/3_29/tree.lua:88358-88366", pob: full}
  - {kind: notable, name: "Tireless 65108", slot: tree, role: scales, target: self, text: "10% increased maximum Life; 10% increased Cost Efficiency (generic)", source: "PoB TreeData/3_29/tree.lua:27846-27858; wiki Whispers of Infinity names Tireless as a generic cost modifier", pob: full}
  - {kind: notable, name: "Life and Cost Efficiency 7374 / 3533 / 11088", slot: tree, role: scales, target: self, text: "5% increased maximum Life; 5% increased Cost Efficiency (generic)", source: "PoB TreeData/3_29/tree.lua:27792-27834", pob: full}
  - {kind: notable, name: "Daring Ideas 15175", slot: tree, role: scales, target: self, text: "25% increased Cost Efficiency of Attacks", source: "PoB TreeData/3_29/tree.lua:88369-88378", pob: full}
  - {kind: unique, name: "Honourhome (Soldier Helmet)", slot: helmet, role: scales, target: self, text: "(30-50)% increased Mana Cost Efficiency (variant 4, Current); older variants had (10-20)% reduced Mana Cost of Skills", source: "PoB Data/Uniques/helmet.lua:1182-1201; wiki Version 3.29.0 (previously 10-20% reduced Mana Cost)", pob: full, variant: "Current (variant 4)"}
  - {kind: jewel, name: "Hypnotic Gaze of the Lich 14588 (3 Hypnotic Eye jewels)", slot: tree, role: scales, target: self, text: "Arcane Surge also grants 20% increased Mana Cost Efficiency (only while Arcane Surge is up, scaled by Arcane Surge effect)", source: "PoB TreeData/3_29/tree.lua:13279-13291; CalcPerform.lua:727", pob: partial}
makes_redundant:
  - {provider: "Inspiration (support) and every mana-specific cost mod", when: "cost is paid in Life (Lifetap, Blood Magic) or ES (Whispers of Infinity)", why: "PoB probes: with the Life or ES cost flag, Mana Cost Efficiency 50% left the cost at 10, generic Cost Efficiency 50% gave 7; the wiki says the same for Whispers", source: "headless probe 2026-10-26 (probe_es.py, probe_life.py); wiki Whispers of Infinity rev 1605628"}
conflicts:
  - {with: "Focused Channelling (support) cost growth vs mana regeneration", effect: "Cost MORE rises 20% per second, cap +100%; per-second cost grows from 95.68 to 191.36 on Worb.xml (see channelling note for the deficit by duration)", source: "PoB sup_int.lua:2538-2552; Channelling note headless numbers"}
conditions:
  - {text: "Cost Efficiency total = sum of all 'increased (Mana) Cost Efficiency' (ManaCostEfficiency + CostEfficiency, INC) times any MORE; formula Cost = ((Base x Support multiplier) + added costs) / (100% + Cost Efficiency %). A reduced Cost Efficiency of 100% or more sets the cost to 2,147,483,647", source: "wiki Cost rev 1703053 (Cost Efficiency section); PoB CalcOffence.lua:1811"}
  - {text: "Cost Efficiency exists in the wiki patch notes from 3.29.0, which converted passive-tree and many unique 'reduced cost' sources; searched Version 3.25.0 to 3.28.0 patch notes: no hit for 'cost efficiency'", source: "wiki Version_3.29.0 (Passive Skill Tree Changes); wiki Cost rev 1703053 version history row 3.29.0"}
  - {text: "Channelling skills pay their upfront cost on each channelling tick (wiki); PoB's cost per second = ManaCost x Speed (Winter Orb 10 x 9.568 = 95.68)", source: "wiki Cost rev 1703053; PoB CalcOffence.lua:5917-5948"}
  - {text: "Mana spent for Arcane Surge / Inspiration / Kitava's Thirst counts only mana really paid: ES-, life-paid and Eldritch Battery costs are mana costs but not mana spent", source: "wiki Mana rev 1673464; wiki Cost rev 1703053; wiki Arcane Surge Support rev 1700912"}
uptime:
  Mapping:       {value: pob, config: {multiplierChannelling: 0}, reasoning: "use PoB's ManaCost and ManaPerSecondCost; the cost mods are permanent; only Hypnotic Eye's Cost Efficiency depends on Arcane Surge being up; Focused Channelling cost grows with the channel length the user sets in the config (default 0 = no growth)", source: "PoB CalcOffence.lua:1811-1840; ConfigOptions.lua:1274-1276; Channelling note uptime"}
  Pinnacle Boss: {value: model, config: {multiplierChannelling: 3}, reasoning: "3 s on a boss: Winter Orb cost 10 -> 16 per tick (Rue Worb.xml has the same setting), per second 95.68 -> 153.09 on Worb.xml (Channelling note); judge the deficit by duration", source: "headless probe 2026-10-26; Channelling note"}
seeds: [Worb, FR]
sources:
  - {ref: "https://www.poewiki.net/wiki/Cost (rev 1703053, 2026-10-12)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Whispers_of_Infinity (rev 1605628)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Inspiration_Support (rev 1681590) and Lifetap_Support (rev 1682175)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Version_3.29.0", kind: patch_notes, patch: "3.29"}
  - {ref: "PoB Modules/CalcOffence.lua:1692-1900, 5917-5955; CalcActiveSkill.lua:524; CalcDefence.lua:1313; Data/Skills/sup_str.lua:4604; sup_int.lua:2538", kind: pob, patch: "3.29"}
not_verified:
  - "Rounding: the wiki Cost example table does not follow its own formula (50-mana skill: 75% -> 30, 100% -> 26, 200% -> 18, the formula gives 28.57, 25, 16.67; 10-mana skill at 200% -> 4, formula 3.33); PoB rounds to nearest after dividing (CalcOffence.lua:1837-1839); the in-game rule is undocumented"
  - "Whether the in-game order is exactly increased -> less -> efficiency -> flat as in PoB (the wiki gives only the efficiency formula and the ordering of base / added / total costs)"
  - "Winter Orb pays its cost once per Speed tick (9.568 per second on Worb.xml): wiki says channelling skills pay each tick, but that the tick rate equals PoB's Speed is an assumption"
  - "Lifetap, Blood Magic path probed with the config flag 'Skills cost life instead of Mana' only, not with the real support gem"
  - "Eldritch Battery: ES-before-mana split of the cost is not in PoB; the share paid from ES vs mana is unknown to PoB"
  - "Whispers of Infinity 'costs over time cost double in ES' (wiki 3.27.0 undocumented note) is not in PoB; not checked in the sustain check"
  - "Worb.xml (golden file) has NO Inspiration gem in any group; the Worb seed brief lists Inspiration, so the day-1 snapshot or another file holds it"
  - "Daring Ideas 15175 is attack-only (its text says 'of Attacks'); that it does not reach Winter Orb or Fireball is an inference, not probed"
  - "Mapping channel length: the proposal said 0.5 s in maps; no source found, so the Mapping config here stays at the default 0"
open_questions:
  - "Does the Worb seed really run Inspiration? Worb.xml and Rue Worb.xml have none in the Winter Orb group."
```
