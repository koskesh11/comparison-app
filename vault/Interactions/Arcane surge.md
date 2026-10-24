---
type: interaction
status: draft
pob_refs: [SupportArcaneSurge, buffArcaneSurge, ArcaneSurgeEffect, ArcaneSurgeManaRegen, ArcaneSurgeCastSpeed, AffectedByArcaneSurge]
source: "PoB 2.67.2 sup_int.lua:218-270 / ConfigOptions.lua:1013 / CalcPerform.lua:712-731; skill-gem-analyst, tree-ascendancy-analyst (task 027); tasks/reports/021-gate1.md I8"
last_confirmed_patch: "3.29.x"
---

Arcane Surge support tracks the mana the supported spell spends and grants a timed buff when a threshold is reached. PoB models it as an on/off config tick only: the 400-mana threshold and 4 s duration are not modelled, and the support gem alone does not turn the buff on. Rule: [[Arcane Surge support needs mana spent]] (it checks the main group only).

```interaction
id: arcane-surge
mechanic: "Supported spell tracks mana spent; at the threshold (400 at L20, 15 at L1) you gain Arcane Surge for 4 s: 35% more spell damage, +20% cast speed, +30% mana regeneration (L20)"
family: buff
target: self
related: [skill-cost-from-es, golem-buffs]
pob:
  measured: config
  how: "statMap sup_int.lua:218-245 (Damage MORE Spell gated on Condition AffectedByArcaneSurge; cast speed and mana regen use MAX across sources); condition set by config buffArcaneSurge (ConfigOptions.lua:1013-1014 -> CalcPerform.lua:712-731) or granted lines (ModParser.lua:892, 1717); the support gem does not turn it on. 400-mana threshold and 4 s duration (4000 ms constant) are NOT modelled"
  config:
    - {var: buffArcaneSurge, default: false, ref: "ConfigOptions.lua:1013-1014", class: c}
  unparsed: []
model:
  proposed_kind: arcane_surge_uptime
  inputs: {from_pob: [mana cost per cast, cast rate], from_scenario: []}
  params: {threshold_L20: 400, threshold_L1: 15, duration_s: 4}
  formula: "uptime = f(mana per cast / threshold, cast rate, 4 s duration); cost inputs: Focused Channelling extra cost per second, Inspiration -34% final, Whispers of Infinity (cost paid from ES)"
  calibration: "no norm found; thresholds sup_int.lua:251, 270"
providers:
  - {kind: support, name: "Arcane Surge", slot: any, role: enables, target: self, text: "L20: threshold 400 mana spent, 4 s buff, 35% more spell damage, +20% cast speed, +30% mana regen, manaMultiplier 30; gate requires Spell; rejects Herald of Ice, Cyclone, Glacial Hammer; accepts Winter Orb, Frost Bomb, Frostbite, Hexblast, Ice Nova, Forbidden Rite", source: "PoB sup_int.lua:218-270; skill-gem-analyst", pob: partial}
  - {kind: notable, name: "Arcane Capacitor 51108", slot: tree, role: applies, target: self, text: "10% chance to gain Arcane Surge when you Kill an Enemy; 10% inc Effect of Arcane Surge per 200 Mana spent Recently (max 50%)", source: "tree-ascendancy-analyst; TREE L24305", pob: partial}
  - {kind: notable, name: "Arcane Heroism 20533", slot: tree, role: scales, target: self, text: "30% increased Effect of Arcane Surge on you; 10% chance to gain Arcane Surge when you Hit a Unique enemy", source: "tree-ascendancy-analyst; TREE L86974", pob: partial}
  - {kind: notable, name: "Arcane Adept 15990", slot: tree, role: applies, target: self, text: "Gain Arcane Surge after Channelling for 1 second (Winter Orb is channelled)", source: "tree-ascendancy-analyst; TREE L86324", pob: partial}
  - {kind: notable, name: "Hierophant small nodes 44797 / 33167", slot: tree, role: scales, target: self, text: "20% increased Effect of Arcane Surge on you", source: "tree-ascendancy-analyst; TREE L15641", pob: full}
  - {kind: tattoo, name: "Honoured Tattoo of the Flood", slot: tree, role: applies, target: self, text: "Gain Arcane Surge on Hit with Spells", source: "tree-ascendancy-analyst; TAT L806", pob: partial}
makes_redundant:
  - {provider: "Arcane Surge support L20 in a second group", when: "the main spell group already holds a working Arcane Surge", why: "Worb has a second Arcane Surge L1 in the Frostblink group (threshold 15 vs 400 mana); its purpose is an inference, unverified: pin it as seeded, do not level or drop it", source: "tasks/reports/021-gate1.md I8; engine/audit.lua:181; sup_int.lua:251,270"}
conflicts:
  - {with: "Arcane Surge on a skill type it rejects (Herald of Ice, Cyclone, Glacial Hammer)", effect: "no buff from that link", source: "skill-gem-analyst (support gate)"}
conditions:
  - {text: "a support only affects gems in its own link group; the Worb day-1 snapshot has Arcane Surge + Frostbite in the GLOVES group, Winter Orb in a separate group", source: "skill-gem-analyst (gem-link-groups)"}
  - {text: "PoB shows +0 spell damage and +0 cast speed until buffArcaneSurge is ticked", source: "pob-coverage-auditor (CalcPerform.lua:712-731)"}
uptime:
  Mapping:       {value: high, config: {buffArcaneSurge: true}, reasoning: "Tick it if the build casts the supported skill continuously; the real buff needs mana spent and lasts 4 s", source: "build-strategist table"}
  Pinnacle Boss: {value: high, config: {buffArcaneSurge: true}, reasoning: "High during rotations, same tick", source: "build-strategist table"}
seeds: [Worb]
sources:
  - {ref: "PoB Data/Skills/sup_int.lua:218-270; Modules/ConfigOptions.lua:1013-1014; CalcPerform.lua:712-731", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/021-gate1.md I8, N12", kind: discovery, patch: "3.29"}
not_verified:
  - "Winter Orb mana per cast at L20 in the user's build (comes from PoB output)"
  - "Arcane Surge duration vs real uptime on the seed"
  - "Purpose of the second Arcane Surge L1 in the Worb Frostblink group (inference)"
open_questions:
  - "Is the Worb Arcane Surge L1 in the Frostblink group intentional (cheap proc)? Only the user can say."
```
