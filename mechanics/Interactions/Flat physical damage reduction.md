---
type: interaction
status: draft
pob_refs: [BasePhysicalDamageReduction, PhysicalDamageReduction, PhysicalMaximumHitTaken, DamageReductionMax, PhysicalTakenDotMult, TotalEHP]
source: "poewiki Damage reduction rev 1605942, Armour rev 1625574 (fetched 2026-10-26); PoB 2.67.2 ModParser.lua / CalcDefence.lua / Data/ModExplicit.lua; headless probes on 3.29\\Ninja Builds\\CoC EK Assa.xml and 3.29\\Worb.xml (b1b-mechanics-researcher.md section A, b1b-pob-coverage-auditor.md flat-dr)"
last_confirmed_patch: "3.29.x"
---

"N% additional Physical Damage Reduction" is flat physical damage reduction: it is added to the armour reduction and the sum is capped at 90 (DamageReductionMax). PoB parses and counts it with no config tick; the physical max hit follows it. It also reduces physical damage over time in PoB, which armour never does. Without it the seed's 7,000 physical max hit needs about 24.8k armour; with 15% it needs about 12.6k ([[Armour and physical max hit]], derived table). Related: [[Endurance charges]], [[Defences]].

Pipeline: [[Receiving damage#Armour and damage reduction]] - flat reduction is summed with the armour reduction on the same hit, after damage-taken-as and resistance, before damage-taken modifiers; the sum is capped at 90 and Overwhelm subtracts afterwards

```interaction
id: flat-physical-damage-reduction
mechanic: "N% additional Physical Damage Reduction adds to the armour reduction of a physical hit; the sum is capped at 90 (Overwhelm subtracts after the cap); the flat part also reduces physical damage over time, armour does not"
family: defence
pipeline_step: ["Receiving damage#Armour and damage reduction", "Defences#Physical damage reduction cap"]
pipeline_why: "wiki Damage reduction: additional reduction is additive with the amount calculated from armour, cap 90 applies after other modifiers; armour acts after damage-taken-as and resistance, before damage-taken modifiers"
target: self
related: [armour-phys-max-hit, endurance-charges, physical-taken-as-elemental, damage-over-time-multiplier]
pob:
  measured: full
  how: "parse: form '^([%+%-]?[%d%.]+)%%? additional' = BASE (Modules/ModParser.lua:83) + name 'physical damage reduction' = PhysicalDamageReduction (ModParser.lua:264; '... from hits' = PhysicalDamageReductionWhenHit :265); live parse of '+10% additional Physical Damage Reduction', '10% additional ...', '7% additional ...' = PhysicalDamageReduction BASE 10/10/7, no leftover text. Use: BasePhysicalDamageReduction = min(max(0, Sum(BASE)), DamageReductionMax) (CalcDefence.lua:1538-1539), cap 90 from Data/Misc.lua:69 via Data.lua:243; hit path totalDR = min(max, armourDR + flatDR) (CalcDefence.lua:2036, 158-161); max hit uses it as flatDR in the quadratic (3231-3232, 3252-3254). DoT: TakenDotMult uses BasePhysicalDamageReduction (CalcDefence.lua:1970-1971, read in the installed file) so PoB reduces physical DoT by the flat part. Not config-gated; only SelfIgnore...DamageReduction flags switch it off (3231, 3233). PoB leaves out: Overwhelm is subtracted after the cap but is an enemy-side input; physical only (elemental max hits unchanged in the probes)."
  config: []
  unparsed: []
model: null
providers:
  - {kind: mod, name: "Suffix of the Watchman / Sentry / Keeper / Protector / Conservator", slot: body armour, role: scales, target: self, text: "4% / 5% / 6% / 7% / 8% additional Physical Damage Reduction (ilvl 45/58/67/77/86); weights str_armour 1000, str_int_armour 500, str_dex 500, str_dex_int 300, none on helmet/gloves/boots/belt/ring/amulet/weapon", source: "Data/ModExplicit.lua:1714-1718", pob: full}
  - {kind: mod, name: "Bench craft 'of Craft'", slot: body armour, role: scales, target: self, text: "2% / 3% additional Physical Damage Reduction (lvl 40 / 60), body armour and shield; same mod group as the suffix row, do not stack on one item", source: "Data/ModMaster.lua:242-243", pob: full}
  - {kind: mod, name: "Endurance charges", slot: any, role: scales, target: self, text: "4% physical (and 4% elemental) damage reduction per charge, max 3; counted only with useEnduranceCharges (see Endurance charges)", source: "Data/Misc.lua:75-76; Modules/ConfigOptions.lua:912-914; vault Endurance charges", pob: config}
  - {kind: unique, name: "Longtooth Talisman (amulet base)", slot: amulet, role: scales, target: self, text: "(4-6)% additional Physical Damage Reduction (implicit)", source: "Data/Bases/amulet.lua:633-638", pob: full}
  - {kind: mod, name: "Organic Ring (ring base)", slot: ring, role: scales, target: self, text: "3% additional Physical Damage Reduction / Cannot roll Modifiers of Non-Physical Damage Types", source: "Data/Bases/ring.lua:383-387", pob: full}
  - {kind: unique, name: "The Will of Uul-Netol", slot: ring, role: scales, target: self, text: "3% additional Physical Damage Reduction", source: "Data/Uniques/ring.lua:1782", pob: full}
  - {kind: mod, name: "Hardening Uulgraft", slot: graft, role: scales, target: self, text: "(1-3)% additional Physical Damage Reduction", source: "Data/Bases/graft.lua:28-33", pob: full}
  - {kind: unique, name: "Eyes of the Greatwolf", slot: amulet, variant: "variant 12", role: scales, target: self, text: "(4-6)% additional Physical Damage Reduction", source: "Data/Uniques/amulet.lua:500", pob: full}
  - {kind: unique, name: "The Red Trail", slot: boots, role: scales, target: self, text: "10% additional Physical Damage Reduction while stationary (Gorgon's Gaze: 5% while moving)", source: "Data/Uniques/boots.lua:88; Data/Uniques/helmet.lua:1523", pob: config}
  - {kind: unique, name: "Circle of Ambition / Circle of Guilt", slot: ring, role: scales, target: self, text: "4% additional Physical Damage Reduction while affected by Herald of Purity", source: "Data/Uniques/ring.lua:288,366", pob: config}
  - {kind: unique, name: "Watcher's Eye", slot: jewel, role: scales, target: self, text: "(5-8)% additional Physical Damage Reduction while affected by Determination (legacy line, see open_questions)", source: "Data/Uniques/Special/WatchersEye.lua:5", pob: config}
  - {kind: keystone, name: "Veteran's Awareness", slot: jewel, role: scales, target: self, text: "20% additional Physical Damage Reduction while affected by a Non-Vaal Guard Skill (and +10% to all Elemental Resistances and maximum Elemental Resistances; 20% more Damage taken if a Non-Vaal Guard Buff was lost Recently)", source: "TreeData/3_29/tree.lua:85671", pob: config}
makes_redundant: []
conflicts:
  - {with: "Basalt Flask", effect: "not a provider: 3.29 text is '20% more Armour' (scales armour only), wiki and PoB agree", source: "Data/Bases/flask.lua:319-328; poewiki Basalt Flask rev 1488337"}
  - {with: "Suffix of the Watchman and bench 'of Craft'", effect: "same mod group ReducedPhysicalDamageTaken: only one applies per item", source: "Data/ModExplicit.lua:1714-1718; Data/ModMaster.lua:242-243"}
  - {with: "damage over time", effect: "wiki sentence 'Damage reduction can mitigate damage over time, though it can only be gained from armour against hits' is ambiguous; PoB applies the flat part to DoT; the vault gap DoT flat damage reduction stays open", source: "poewiki Damage reduction rev 1605942; Modules/CalcDefence.lua:1970-1971"}
conditions:
  - {text: "the sum with armour reduction is clamped to 90; the flat part alone is clamped first", source: "Modules/CalcDefence.lua:1538, 2036; Data/Misc.lua:69"}
  - {text: "Sacred Chainmail (the seed body base) is str_int_armour: the suffix can roll at weight 500; it costs the suffix slot", source: "Data/ModExplicit.lua:1714-1718; Data/Bases/body.lua:1005-1009"}
  - {text: "Veteran's Awareness: PoB shows the bonus whenever a non-Vaal guard is active (the guard has its own uptime) and the 20% more damage taken penalty only if LostNonVaalBuffRecently is ticked (default off)", source: "Modules/ConfigOptions.lua:1265; Modules/CalcPerform.lua:3334-3337"}
uptime:
  Mapping:
    value: always
    config: {useEnduranceCharges: "only for the charge row; model by the Endurance charges note"}
    reasoning: "gear, base and tree lines are always on; conditional rows (stationary, Herald of Purity, Determination, guard) follow their own condition; PoB counts all of them as a plain additive number"
    source: "Modules/CalcDefence.lua:1538; vault Endurance charges"
  Pinnacle Boss:
    value: always
    config: {}
    reasoning: "same lines; the boss hit size does not change the flat part, so against large hits the flat reduction is worth relatively more than armour (armour is A/(A+5D)); the physical max hit does not use the configured boss hit"
    source: "Modules/CalcDefence.lua:3235-3261; vault Armour and physical max hit"
seeds: [Worb, EK, Fireball]
sources:
  - {ref: "https://www.poewiki.net/wiki/Damage_reduction (rev 1605942)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Armour (rev 1625574)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/ModParser.lua:83,264-265; Modules/CalcDefence.lua:158-161,1538-1539,1970-1971,2036,3231-3254; Modules/Data.lua:243; Data/Misc.lua:69 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b1b-mechanics-researcher.md (A); b1b-pob-coverage-auditor.md (flat-dr, measurements)", kind: discovery, patch: "3.29"}
not_verified:
  - "measured effect of +10% additional Physical DR (probe, one change, rolled back): Worb PhysicalMaximumHitTaken 16,310 to 18,165 (+1,855), TotalEHP 76,837 to 81,890; EK 7,538 to 8,557 (+1,019), TotalEHP 145,259 to 155,185; elemental max hits unchanged; this is the auditor's run, not re-run here"
  - "whether Sacred Chainmail ilvl and the suffix slot are free in the final item (only PoB spawn weights were read)"
  - "drop and obtainability of Longtooth Talisman, Hardening Uulgraft and Eyes of the Greatwolf in the current league (obtainability step not run)"
  - "Organic Ring: what 'Modifiers of Non-Physical Damage Types' blocks for a fire caster"
  - "the other lines of The Will of Uul-Netol, Eyes of the Greatwolf, Gorgon's Gaze and The Red Trail were not read"
  - "flat reduction against damage over time in the game itself (the wiki sentence is ambiguous); no hit rate or uptime measured"
  - "the wiki rule was fetched by the researcher; the auditor did not fetch the wiki"
open_questions:
  - "Flat physical reduction against damage over time: PoB reduces physical DoT by it (CalcDefence.lua:1970-1971); the wiki sentence does not say so plainly. Which reading should the generator use for DoT taken?"
  - "Watcher's Eye lines: the wiki says the old Watcher's Eye modifiers no longer roll since 3.25.0 (Damage taken as rev 1618416) while PoB's Special file still lists them. Treat the row as legacy or live?"
```
