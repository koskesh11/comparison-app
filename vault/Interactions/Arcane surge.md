---
type: interaction
status: draft
pob_refs: [SupportArcaneSurge, buffArcaneSurge, ArcaneSurgeEffect, ArcaneSurgeManaRegen, ArcaneSurgeCastSpeed, AffectedByArcaneSurge, ManaCost, ManaCostRaw]
source: "PoB 2.67.2 sup_int.lua:218-270 / ConfigOptions.lua:1013 / CalcPerform.lua:712-731, 2324 / CalcActiveSkill.lua:809; skill-gem-analyst, tree-ascendancy-analyst (task 027); tasks/reports/021-gate1.md I8; headless Worb.xml and Fireball seed probes (task 027 batch 4b)"
last_confirmed_patch: "3.29.x"
---

Arcane Surge support tracks the mana the supported spell spends and grants a timed buff when a threshold is reached. PoB models it as always on: an enabled Arcane Surge support turns the buff on by itself (probe: condition true and cast speed up with the config tick unset), and the config tick is only for sources without the gem. The 400-mana threshold and the 4 s duration are not modelled, so PoB shows the buff as 100% up. Rule: [[Arcane Surge support needs mana spent]] (it checks the main group only).

Pipeline: [[Damage calculation#More and less]], [[Damage calculation#Hit rate]] - the buff is 35% more spell damage (its own multiplier, not in the increased pool) and +20% cast speed (speed effect, no per-hit step); PoB shows both whenever an enabled Arcane Surge support (or the config tick) exists, so the step is correct only while the buff is actually up

```interaction
id: arcane-surge
mechanic: "Supported spell tracks mana spent; at the threshold (400 at L20, 15 at L1) you gain Arcane Surge for 4 s: 35% more spell damage, +20% cast speed, +30% mana regeneration (L20)"
family: buff
pipeline_step: ["Damage calculation#More and less", "Damage calculation#Hit rate"]
pipeline_why: "the buff is 35% more spell damage (its own multiplier, not in the increased pool) and +20% cast speed (speed effect, no per-hit step); PoB shows both whenever an enabled Arcane Surge support (or the config tick) exists, so the step is correct only while the buff is actually up"
target: self
related: [skill-cost-from-es, golem-buffs, mana-cost-efficiency, inspiration-charges, channelling]
pob:
  measured: config
  how: "statMap sup_int.lua:218-245 (Damage MORE Spell gated on Condition AffectedByArcaneSurge; cast speed and mana regen use MAX across sources); condition AffectedByArcaneSurge is set by (a) the support gem itself: its statMap mods carry a GlobalEffect Buff tag 'Arcane Surge' (sup_int.lua:228-233), CalcActiveSkill.lua:809 turns the tag into a buff entry and CalcPerform.lua:2324 sets the condition for every enabled supported skill, then CalcPerform.lua:712-731 adds the cast speed and regen; (b) config buffArcaneSurge (ConfigOptions.lua:1013-1014); (c) granted lines (ModParser.lua:892, 1717). Measured 2026-10-26: Worb with the config tick unset, AffectedByArcaneSurge = true; Fireball seed with Arcane Surge L20 added and the tick unset: condition nil -> true, Speed 5.0267 -> 5.44, ManaCost 37 -> 49, TotalDPS 251,999.68 -> 368,533.70. 400-mana threshold and 4 s duration (4000 ms constant) are NOT modelled"
  config:
    - {var: buffArcaneSurge, default: false, ref: "ConfigOptions.lua:1013-1014", class: c}
  unparsed: []
model:
  proposed_kind: arcane_surge_uptime
  inputs: {from_pob: [ManaCost, Speed, Repeats (Spell Echo)], from_scenario: []}
  params: {threshold_L20: 400, threshold_L1: 15, duration_s: 4}
  formula: "LABELLED MODEL (not verified in game). uses_per_second r = Speed / Repeats; mana spent per use C = PoB ManaCost (final cost incl. the support's own 30% manaMultiplier and Inspiration's net about -21%, not -34%; channelling: one use per tick, wiki Channelling skill rev 1647943); uses to proc n = ceil(threshold / C); time between procs T = n / r; uptime = min(1, duration / T) with duration 4 s (increased skill effect duration changes it, wiki Arcane Surge Support rev 1700912, not in PoB). Worb (Brine King off, saved AS L20): C 10, r 9.568 -> n 40, T 4.18 s, uptime 95.7%; with Inspiration L20 added: C 8 -> n 50, T 5.23 s, uptime 76.5%. Fireball Elementalist seed (Arcane Surge L20 added in PoB to the Fireball group, Spell Echo Repeats 2): ManaCost 37 -> 49, Speed 5.44, r 2.72 -> n 9, T 3.31 s, uptime 100% (3.58 s, still 100%, at the buff-off speed 5.0267). Worked DPS (PoB TotalDPS, Worb): buff always on 1,343,497.51 vs off 941,181.68 (both Arcane Surge gems disabled); weighted at 95.7% = 1,326,117; with Inspiration: on 1,733,757.68, off 1,214,561.11, weighted at 76.5% = 1,611,975"
  calibration: "no numeric norm found (searched: wiki Arcane Surge Support rev 1700912, version rows end at 3.26.0, only the qualitative line 'It is common to use a low-leveled Arcane Surge Support to make this effect easier to proc'; wiki Arcane Surge, Cost, Channelling skill; PoB sup_int.lua, ModParser, CalcPerform; one web search found no uptime figures). Threshold from sup_int.lua:251,270 (L1 15, L20 400). Not verified in game: whether the counter keeps the remainder after a proc, and whether a refresh while the buff is up restarts the counter"
providers:
  - {kind: support, name: "Arcane Surge", slot: any, role: enables, target: self, text: "L20: threshold 400 mana spent, 4 s buff, 35% more spell damage, +20% cast speed, +30% mana regen, manaMultiplier 30; gate requires Spell; rejects Herald of Ice, Cyclone, Glacial Hammer; accepts Winter Orb, Frost Bomb, Frostbite, Hexblast, Ice Nova, Forbidden Rite", source: "PoB sup_int.lua:218-270; skill-gem-analyst", pob: partial}
  - {kind: notable, name: "Arcane Capacitor 51108", slot: tree, role: applies, target: self, text: "10% chance to gain Arcane Surge when you Kill an Enemy; 10% inc Effect of Arcane Surge per 200 Mana spent Recently (max 50%)", source: "tree-ascendancy-analyst; TREE L24305", pob: partial}
  - {kind: notable, name: "Arcane Heroism 20533", slot: tree, role: scales, target: self, text: "30% increased Effect of Arcane Surge on you; 10% chance to gain Arcane Surge when you Hit a Unique enemy", source: "tree-ascendancy-analyst; TREE L86974", pob: partial}
  - {kind: notable, name: "Arcane Adept 15990", slot: tree, role: applies, target: self, text: "Gain Arcane Surge after Channelling for 1 second (Winter Orb is channelled)", source: "tree-ascendancy-analyst; TREE L86324", pob: partial}
  - {kind: notable, name: "Hierophant small nodes 44797 / 33167", slot: tree, role: scales, target: self, text: "20% increased Effect of Arcane Surge on you", source: "tree-ascendancy-analyst; TREE L15641", pob: full}
  - {kind: jewel, name: "Hypnotic Gaze of the Lich 14588 (3 Hypnotic Eye jewels)", slot: tree, role: scales, target: self, text: "Arcane Surge also grants 20% of Damage taken Recouped as Mana and 20% increased Mana Cost Efficiency; the Cost Efficiency lowers the mana per cast and so slows the next Arcane Surge", source: "PoB TreeData/3_29/tree.lua:13279-13291; CalcPerform.lua:727", pob: partial}
  - {kind: tattoo, name: "Honoured Tattoo of the Flood", slot: tree, role: applies, target: self, text: "Gain Arcane Surge on Hit with Spells", source: "tree-ascendancy-analyst; TAT L806", pob: partial}
makes_redundant:
  - {provider: "Arcane Surge support L20 in a second group", when: "the main spell group already holds a working Arcane Surge", why: "Worb has a second Arcane Surge L1 in the Frostblink group (threshold 15 vs 400 mana); its purpose is an inference, unverified: pin it as seeded, do not level or drop it", source: "tasks/reports/021-gate1.md I8; engine/audit.lua:181; sup_int.lua:251,270"}
conflicts:
  - {with: "Arcane Surge on a skill type it rejects (Herald of Ice, Cyclone, Glacial Hammer)", effect: "no buff from that link", source: "skill-gem-analyst (support gate)"}
  - {with: "Whispers of Infinity, Eldritch Battery, Lifetap, Blood Magic (cost paid in ES / life)", effect: "the supported skill's cost no longer counts as mana spent: no Arcane Surge from that skill (a second Arcane Surge on a mana-paying skill, or a non-spending source such as Arcane Adept 15990, is needed)", source: "wiki Arcane Surge Support rev 1700912; wiki Cost rev 1703053"}
conditions:
  - {text: "a support only affects gems in its own link group; the Worb day-1 snapshot has Arcane Surge + Frostbite in the GLOVES group, Winter Orb in a separate group", source: "skill-gem-analyst (gem-link-groups)"}
  - {text: "PoB shows the 35% more spell damage and 20% cast speed whenever an enabled Arcane Surge support exists, even with buffArcaneSurge unticked; the tick matters only for sources without the gem (tree nodes, tattoo). Replaces the earlier pob-coverage-auditor reading '+0 until ticked', which the probe contradicts", source: "headless probes 2026-10-26 (Fireball seed: Speed 5.0267 -> 5.44 with the tick unset); CalcActiveSkill.lua:809; CalcPerform.lua:712-731, 2324"}
  - {text: "reduced cost lowers the mana counted: the threshold counts mana actually spent on upfront costs, so every cost reduction (Inspiration, Mana Cost Efficiency, Cost Efficiency) makes the buff slower to gain; increases (Archmage, Fevered Mind) make it faster (wiki: 'Increases to mana cost ... may make it easier to spend the required mana'; Inspiration page: 'lower mana costs result in better usage' of charges, i.e. the counter runs on the final cost)", source: "wiki Arcane Surge Support rev 1700912 (Skill functions and interactions); wiki Inspiration Support rev 1681590; PoB CalcOffence.lua:1811-1840 (final cost)"}
  - {text: "only mana counts: 'It explicitly checks for spent mana, so any spent life or energy shield (e.g. Blood Magic, Eldritch Battery) do not contribute towards the threshold, even if the skill had a mana cost originally'; Whispers of Infinity and Lifetap are the same case (the cost is ES / life); a spell cast with too little mana (From Below): the negative part is not counted", source: "wiki Arcane Surge Support rev 1700912 (page version rows run to 3.26.0); wiki Cost rev 1703053 ('Eldritch Battery ... still paying a mana cost, but not spending mana'); wiki Mana rev 1673464"}
  - {text: "PoB does not count mana spent at all: the buff is on whenever the gem or the config buffArcaneSurge exists, so PoB's ManaCost (with Inspiration or Cost Efficiency) has no effect on the buff", source: "PoB ConfigOptions.lua:1013-1014; CalcPerform.lua:712-731, 2324"}
  - {text: "the Arcane Surge gem raises the supported skill's ManaCost by its manaMultiplier 30 (Worb Winter Orb 8 without the gem -> 10 with it), which makes the 400-mana threshold easier to reach; Inspiration L20 (net about -21%, its own manaMultiplier 20) lowers it again to 8", source: "sup_int.lua:218-270 (manaMultiplier 30); sup_str.lua:4663 (manaMultiplier 20); headless Worb probe (batch 4b researcher, 8 -> 10 not re-run)"}
uptime:
  Mapping:       {value: model, config: {buffArcaneSurge: "not needed while an enabled Arcane Surge support exists; tick only for gem-less sources (tree, tattoo)"}, reasoning: "continuous casting: uptime = min(1, 4 s / T) from the model; Worb 95.7%, 76.5% with Inspiration; PoB shows 100%", source: "model above; build-strategist table"}
  Pinnacle Boss: {value: model, config: {buffArcaneSurge: "same; real uptime drops with any pause in casting longer than the 4 s buff"}, reasoning: "high during rotations (model), PoB still shows 100%", source: "model above; build-strategist table"}
seeds: [Worb]
sources:
  - {ref: "PoB Data/Skills/sup_int.lua:218-270; Modules/ConfigOptions.lua:1013-1014; CalcPerform.lua:712-731", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/021-gate1.md I8, N12", kind: discovery, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Arcane_Surge_Support (rev 1700912), Mana (rev 1673464), Cost (rev 1703053), Channelling_skill (rev 1647943)", kind: wiki, patch: "3.29"}
not_verified:
  - "Winter Orb mana per cast at L20 in the user's build (comes from PoB output)"
  - "Arcane Surge duration vs real uptime on the seed"
  - "Purpose of the second Arcane Surge L1 in the Worb Frostblink group (inference)"
  - "whether the wiki's 'mana spent' counter uses the cost after Cost Efficiency rounding (inferred from the Inspiration page example, not stated for Arcane Surge)"
  - "the Arcane Surge Support wiki page has no dated row for the spent-mana rule; patch for the rule unverified (page version rows end at 3.26.0)"
  - "Arcane Surge uptime numbers (T 4.18 s / 5.23 s, 95.7% / 76.5%) assume one channelling tick per cast at PoB's Speed; the tick rate is not probed"
open_questions:
  - "Is the Worb Arcane Surge L1 in the Frostblink group intentional (cheap proc)? Only the user can say."
```
