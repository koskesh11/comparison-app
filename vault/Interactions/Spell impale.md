---
type: interaction
status: draft
pob_refs: [ImpaleChance, ImpaleEffect, ImpaleStacksMax, multiplierImpalesOnEnemy, ImpaleDPS, ImpaleModifier]
source: "PoB 2.67.2 ModParser.lua / CalcOffence.lua; item-analyst, skill-gem-analyst, tree-ascendancy-analyst (task 027)"
last_confirmed_patch: "3.29.x"
---

Impale normally comes from attacks. Spells can impale only through a few sources (Entropic Devastation, Bladefall of Impaling, Replica Heartbreaker); no tree node gives spell impale. The impale needs physical damage on the hit. In the EK sample ImpaleDPS is 49% of total (strategist/seed draft).

```interaction
id: spell-impale
mechanic: "Spell crits (or spell hits) inflict Impale; each Impale stores 10% of the physical hit (scaled by effect) and lasts a number of hits; needs physical damage"
family: buff
target: enemy
related: [coc-trigger, power-charges]
pob:
  measured: full
  how: "ModParser.lua:3904 (Critical Strikes with Spells inflict Impale -> ImpaleChance 100, Spell flag, CriticalStrike condition), 581 (chance to impale on spell hit); CalcOffence.lua:5596-5600, 3502-3510 (needs canDeal.Physical), Data.lua:268 (stored 10%), 1639-1655 (duration), 5614 (armour reduction); stack count CalcPerform.lua:3387-3391 defaults to 5"
  config:
    - {var: multiplierImpalesOnEnemy, default: unset (forced to ImpaleStacksMax = 5), ref: "ConfigOptions.lua:1651", class: b}
  unparsed: []
model: null
providers:
  - {kind: unique, name: "Entropic Devastation (Assassin's Mitts)", slot: gloves, role: enables, target: enemy, text: "Critical Strikes with Spells inflict Impale; (30-50)% increased Effect of Impales inflicted with Spells; grants Call of Steel", source: "PoB Data/Uniques/gloves.lua:1141-1144; ModParser.lua:3904, 582-585", pob: full}
  - {kind: unique, name: "Watcher's Eye (Pride)", slot: jewel, role: scales, target: enemy, text: "Impales you inflict last 2 additional Hits while using Pride (the 25% attack impale line does not apply to spells)", source: "PoB Data/Uniques/Special/WatchersEye.lua:91-92; ModParser.lua:884", pob: full, requires: ["Pride active"]}
  - {kind: gem, name: "Bladefall of Impaling", slot: gem, role: enables, target: enemy, text: "spell_impale_on_crit_%_chance 100 (only gem with spell impale)", source: "PoB act_dex.lua:2696-2754; SkillStatMap.lua:1719-1721", pob: full}
  - {kind: unique, name: "Replica Heartbreaker", slot: dagger, role: enables, target: enemy, text: "20% chance to Impale on Spell Hit; 20% inc Impale Effect", source: "PoB Data/Uniques/dagger.lua:195-196; ModParser.lua:581", pob: full}
  - {kind: notable, name: "Savage Skewering 6783", slot: tree, role: scales, target: enemy, text: "15% increased Impale Effect (not Attack-scoped)", source: "tree-ascendancy-analyst; TREE L61169", pob: full}
  - {kind: notable, name: "Brutal Skewering 39904", slot: tree, role: scales, target: enemy, text: "Impales you inflict last 1 additional Hit", source: "tree-ascendancy-analyst; TREE L43388", pob: full}
  - {kind: notable, name: "Deliberate Brutality 56146", slot: tree, role: scales, target: enemy, text: "Impales gain 50% increased Effect once 1 s of Duration has expired", source: "tree-ascendancy-analyst; TREE L54417", pob: full}
  - {kind: unique, name: "Woespike", slot: ring, role: scales, target: enemy, text: "(20-30)% chance on Melee Hit for the Strongest Impale to last 1 additional Hit; (40-50)% less Impale Duration", source: "PoB Data/Uniques/ring.lua:1821-1822 (variant 2)", pob: full}
  - {kind: support, name: "Impale", slot: any, role: blocks, target: enemy, text: "requires an Attack skill; cannot be linked to a spell, so spell impale and the support are mutually exclusive on one skill", source: "PoB sup_dex.lua:2472-2519; skill-gem-analyst", pob: full}
makes_redundant: []
conflicts:
  - {with: "Impale support on a spell", effect: "gate requires Attack; Winter Orb / Hexblast / Forbidden Rite / Fireball rejected", source: "skill-gem-analyst (sup_dex.lua:2472)"}
conditions:
  - {text: "hit must deal physical damage", source: "CalcOffence.lua:5596-5600"}
  - {text: "attack-only impale lines (Bane of Hope, Great Old One's Tentacles, Woespike chance) do not apply to spells", source: "item-analyst"}
uptime:
  Mapping:       {value: high, config: {multiplierImpalesOnEnemy: "unset = 5 stacks (optimistic on packs: stacks are consumed per hit, 8 s base duration)"}, reasoning: "High if the source is crit-based (Entropic Devastation) and crit is ~100%", source: "build-strategist table"}
  Pinnacle Boss: {value: partial, config: {multiplierImpalesOnEnemy: "PoB default 5 is fine for a continuous single target"}, reasoning: "Stacks need hits to build", source: "build-strategist table"}
seeds: [EK]
sources:
  - {ref: "PoB ModParser.lua:3904, 581-585; CalcOffence.lua:5596-5614", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/Uniques/gloves.lua:1141-1144, WatchersEye.lua:91-92", kind: pob, patch: "3.29"}
not_verified:
  - "Whether spell-hit impale gets ImpaleModifier applied to TotalDPS: CalcOffence.lua:6155 reads the main-hand attack path, spell path not traced"
  - "Watcher's Eye condition 'while using Pride' vs 'affected by' in PoB not re-checked"
  - "Whether a spell-hit impale scales with the Impale support effect (support requires Attack)"
open_questions:
  - "None; EK ImpaleDPS share (49%) should be re-measured with a headless run before it is used as a number."
```
