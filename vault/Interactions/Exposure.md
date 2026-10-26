---
type: interaction
status: draft
pob_refs: [conditionEnemyFireExposure, conditionEnemyColdExposure, conditionEnemyLightningExposure, FireExposureChance, ColdExposureChance, LightningExposureChance, ExtraExposure, ExposureEffect, ExposureMin, HasColdExposure]
source: "poewiki Exposure rev 1673498, Elemental Equilibrium rev 1605611 (fetched 2026-10-24); PoB 2.67.2 CalcPerform.lua / CalcOffence.lua / ConfigOptions.lua / ModParser.lua; PoB Data/Skills, Data/Uniques, TreeData/3_29/tree.lua"
last_confirmed_patch: "3.29.x"
---

Exposure is a debuff that lowers one elemental resistance on the enemy: -10% by default when the player or a skill inflicts it, lasting 4 s unless a skill sets another duration. Only the strongest exposure per element applies; different elements coexist. PoB takes the strongest per element, applies the debuff automatically for socketed debuff skills (Frost Bomb), and for on-hit chance sources (tree, items) only when the matching config box is ticked. Elemental Equilibrium is the main conflict: the wiki and PoB disagree on same-element on-hit exposure and both readings stay visible below. Related: [[Own shock effect]], [[Freeze]], [[Chill]]. Providers beyond the seed set: see tasks/reports/027-research.md.

Pipeline: [[Damage calculation#Resistance, exposure and penetration]] - exposure lowers the enemy's elemental resistance (strongest per element), so it applies to hits, DoT and ailments of that element (penetration is hits only and is subtracted after the cap); exposure is partly absorbed while the enemy's uncapped resistance is above its cap

```interaction
id: exposure
mechanic: "Exposure lowers one elemental resistance on the enemy: -10% by default (overrides: Elemental Equilibrium -25% per element not dealt, Scorching Ray -25% fire, Frost Bomb -15% cold, Wave of Conviction -15%); only the strongest exposure per element applies, different elements coexist; default duration 4 s"
family: ailment
pipeline_step: ["Damage calculation#Resistance, exposure and penetration"]
pipeline_why: "exposure lowers the enemy's elemental resistance (strongest per element), so it applies to hits, DoT and ailments of that element (penetration is hits only and is subtracted after the cap); exposure is partly absorbed while the enemy's uncapped resistance is above its cap"
target: enemy
related: [freeze, chill, shock, elemental-ailment-count]
pob:
  measured: config
  how: "per element the single strongest exposure mod is taken (smallest value) from enemy <Element>Exposure mods (CalcPerform.lua:3638-3643), then ExtraExposure BASE added (3646-3648), scaled by ExposureEffect inc (3650-3653); sets enemy <Element>Resist and Condition:Has<El>Exposure; skill debuffs (Frost Bomb, Wave of Conviction) are automatic (GlobalEffect Debuff); chance sources (tree, items) only count when the config box conditionEnemy<El>Exposure is ticked (-10%); 'Exposure you inflict applies at least -N%' -> ExposureMin OVERRIDE (ModParser.lua:4316)"
  config:
    - {var: conditionEnemyFireExposure, default: false, ref: "Modules/ConfigOptions.lua:1973-1981 (check, ifFlag applyFireExposure, -10 resist)", class: b}
    - {var: conditionEnemyColdExposure, default: false, ref: "Modules/ConfigOptions.lua:1973-1981 (ifFlag applyColdExposure)", class: b}
    - {var: conditionEnemyLightningExposure, default: false, ref: "Modules/ConfigOptions.lua:1973-1981 (ifFlag applyLightningExposure)", class: b}
  unparsed:
    - "Eye of Malice: PoB handles both exposure-on-hit lines (ModParser.lua:848-851) and the resist INC (4847-4850); no red line"
model: null
providers:
  # seed: Worb day-1 poe.ninja snapshot (Frost Bomb is NOT in Worb.xml; lead re-check batch 3c)
  - {kind: gem, name: "Frost Bomb", slot: any, role: applies, target: enemy, text: "L20: Cold Exposure -15% cold res (GlobalEffect Debuff 'Frost Bomb', 5 s debuff from pulses); also 25% chance to freeze and -75% life regeneration on enemies; counted automatically by PoB", source: "Data/Skills/act_int.lua:7756,7768-7771; Modules/CalcPerform.lua:3629-3657", pob: full}
  - {kind: mastery, name: "Cold Mastery (effect 13267)", slot: tree, role: applies, target: enemy, text: "10% Chance to Inflict Cold Exposure on Hit with Cold Damage (applies -10% Cold Res for 4 s); Worb day-1 snapshot uses node 60170 -> 13267, user's Worb.xml uses effect 26782 (frozen seconds) instead", source: "TreeData/3_29/tree.lua:54766", pob: config}
  - {kind: notable, name: "Heraldry", slot: tree, role: applies, target: enemy, text: "Cold/Fire/Lightning Exposure while affected by Herald of Ice/Ash/Thunder (Worb runs Herald of Ice)", source: "TreeData/3_29/tree.lua:87855 (node 28551)", pob: config, requires: [Herald of Ice]}
  - {kind: unique, name: "Eye of Malice", slot: Helmet, role: applies, target: enemy, text: "25% chance to inflict Cold Exposure on Hit; 25% chance to inflict Fire Exposure on Hit; Nearby Enemies have 50% increased Fire and Cold Resistances (the 'downside' only costs while enemy resistance is positive: PoB resist = (base + exposure) x (1 + inc), so with negative totals it makes them MORE negative; which side wins for a given enemy is not run)", source: "Data/Uniques/helmet.lua:1448-1450; Modules/ModParser.lua:848-851,4847-4850; Modules/CalcOffence.lua:503", pob: config}
  # alternatives (at most 12)
  - {kind: support, name: "Awakened Cold Penetration Support", slot: any, role: applies, target: enemy, text: "L5: 39% cold penetration and 10% chance to inflict Cold Exposure on hit (the only on-hit exposure support gem; Awakened Fire / Lightning Penetration likewise)", source: "Data/Skills/sup_dex.lua:1394; sup_str.lua:2260; sup_int.lua:4617", pob: partial}
  - {kind: gem, name: "Hydrosphere", slot: any, role: applies, target: enemy, text: "water_sphere_cold_lightning_exposure_% -10: cold and lightning exposure on drenched enemies", source: "Data/Skills/act_int.lua:8939", pob: partial}
  - {kind: gem, name: "Scorching Ray / Pyroclast Mine", slot: any, role: applies, target: enemy, text: "fire res -25 max (Scorching Ray); fire exposure -15 (Pyroclast Mine; 3.27.0 aura -15 / -25 Sabotage)", source: "Data/Skills/act_int.lua:15712,14798", pob: partial}
  - {kind: notable, name: "Corrosive Elements", slot: tree, role: applies, target: enemy, text: "Cold/Fire/Lightning Skills have a 25% chance to apply <type> Exposure on Hit", source: "TreeData/3_29/tree.lua:87065 (node 2306); Data/ModCache.lua:14741", pob: config}
  - {kind: ascendancy, name: "Mastermind of Discord (Elementalist)", slot: tree, role: scales, target: enemy, text: "Exposure you inflict applies an extra -25% to the affected Resistance; Regenerate 1% of Mana per second if you've inflicted Exposure Recently (Worb ascendancy)", source: "TreeData/3_29/tree.lua:49969 (node 61259); wiki Version 3.22.0", pob: full}
  - {kind: mastery, name: "Elemental Mastery (effect 48385)", slot: tree, role: scales, target: enemy, text: "Exposure you inflict applies at least -18% to the affected Resistance (ExposureMin OVERRIDE; floor, not additive)", source: "TreeData/3_29/tree.lua:19266; Modules/ModParser.lua:4316; wiki Version 3.21.0", pob: full}
  - {kind: unique, name: "Tulborn", slot: Wand, role: scales, target: enemy, text: "Cold Exposure you inflict applies an extra -12% to Cold Resistance (ExtraExposure)", source: "Data/Uniques/wand.lua:394; Modules/ModParser.lua:2675", pob: full, variant: "variant 4"}
  - {kind: unique, name: "Starlight Chalice", slot: Flask, role: applies, target: enemy, text: "Inflict Fire, Cold and Lightning Exposure on nearby Enemies when used (+(20-30)% inc Effect of Non-Damaging Ailments during Effect)", source: "Data/Uniques/flask.lua:569-570", pob: config}
  - {kind: mastery, name: "Lightning Mastery (effect 64241)", slot: tree, role: abuses, target: enemy, text: "60% increased Critical Strike Chance against enemies with Lightning Exposure", source: "TreeData/3_29/tree.lua:43023", pob: config}
  - {kind: keystone, name: "Elemental Equilibrium", slot: tree, role: blocks, target: enemy, text: "Hits that deal Elemental Damage remove Exposure to those Elements and inflict 25% Exposure to the other Elements; conflicts with single-element builds because it removes the exposure of your own element", source: "TreeData/3_29/tree.lua:62108 (node 39085); wiki Elemental Equilibrium rev 1605611", pob: partial}
makes_redundant: []
conflicts:
  - {with: "Elemental Equilibrium (wiki) vs Elemental Equilibrium (PoB)", effect: "READING WIKI: EE applies before regular on-hit exposure, so a hit that removes fire exposure can still inflict fire exposure with Eye of Malice or an eldritch glove implicit. READING PoB: with EE active and the enemy flagged HitBy<Element>Damage, PoB skips the whole exposure block for that element, so an on-hit exposure source of the SAME element is suppressed. Both stay visible; not resolved", source: "https://www.poewiki.net/wiki/Elemental_Equilibrium rev 1605611 vs Modules/CalcPerform.lua:3629-3636"}
  - {with: "Eye of Malice resist INC vs exposure", effect: "the +50% enemy Fire/Cold resistance multiplies (base + exposure); the effect depends on the enemy's total resistance", source: "Modules/CalcOffence.lua:503; Data/Uniques/helmet.lua:1450"}
conditions:
  - {text: "enemy-inflicted exposure is -25% generally; the player's default is -10%; if a skill sets the exposure duration, skill effect duration modifiers apply; exposure from hits only (EE: not DoT, not blocked hits)", source: "https://www.poewiki.net/wiki/Exposure rev 1673498; Elemental Equilibrium rev 1605611"}
  - {text: "PoB conditions HasXExposure are set on the enemy for 'against enemies with X exposure' mods (ModParser.lua:2001; CalcPerform.lua:3654); config box needs a source: chance>0 sets skillFlags.applyXExposure (CalcOffence.lua:4269-4277; CalcPerform.lua:399-406)", source: "Modules/CalcOffence.lua:4269-4277; Modules/CalcPerform.lua:399-406,3654"}
uptime:
  Mapping:
    value: partial
    config: {conditionEnemyFireExposure: "ON only if a source exists", conditionEnemyColdExposure: "ON only if a source exists (Frost Bomb is automatic) (chance sources: box state by the uptime rule of user 2026-10-25, see [[Chance on hit uptime]]: u >= 80% ticked, no notice; 50-80% ticked + user informed with u; < 50% unticked + warning with u)", conditionEnemyLightningExposure: "ON only if a source exists"}
    reasoning: "partial-high where the source is an on-hit chance (Eye of Malice 25%) or a debuff skill; the config box needs a source; -10% default"
    source: "build-strategist table (tasks/reports/027-research.md); Modules/ConfigOptions.lua:1973-1981"
  Pinnacle Boss:
    value: high
    config: {conditionEnemyColdExposure: "ON only if a source exists (chance sources: box state by the uptime rule of user 2026-10-25, see [[Chance on hit uptime]]: u >= 80% ticked, no notice; 50-80% ticked + user informed with u; < 50% unticked + warning with u); Frost Bomb cast on the boss is high; on-hit % sources effectively high in a long fight"}
    reasoning: "skill/curse-like debuffs are high; a 25% on-hit chance is hit often on a boss; exposure lasts 4 s so continuous hits are needed"
    source: "build-strategist table (tasks/reports/027-research.md); https://www.poewiki.net/wiki/Exposure rev 1673498"
seeds: [Worb]
sources:
  - {ref: "https://www.poewiki.net/wiki/Exposure (rev 1673498, 2026-07-13)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Elemental_Equilibrium (rev 1605611, 2026-01-14)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcPerform.lua:3629-3658; Modules/ConfigOptions.lua:1973-1981; Modules/ModParser.lua:848-853,2675,4316 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "wiki Version 3.6.0 (introduced), 3.21.0 (at least -18%), 3.22.0 (Mastermind of Discord), 3.25.0, 3.26.0, 3.27.0", kind: patch_notes, patch: "3.29"}
not_verified:
  - "'partly absorbed while uncapped resistance is above the cap' follows from the cap/penetration order in Damage calculation but has no direct quote"
  - "whether PoB's m_min(min, modDB:Override(nil, 'ExposureMin')) is nil-safe when no ExposureMin exists (CalcPerform.lua:3655); PoB evidently runs"
  - "exact exposure durations per provider; Wave of Conviction and Frost Bomb numbers beyond the PoB data rows"
  - "stacking of the 'extra -x%' mods against the 'at least -18%' floor (PoB read only through 021-gate1 N10)"
  - "The Flame of Hope bow (Inflict Fire Exposure on Hit against Enemies with...; condition line truncated in the evidence, Data/Uniques/bow.lua:210-212) and The Grey Wind axe (Fire Exposure at maximum Rage, axe.lua:198) were not read in full"
  - "whether exposure and a curse's resistance reduction overlap in PoB (take the lower)"
open_questions:
  - "Elemental Equilibrium: should the engine follow the wiki (same-element on-hit exposure still applies after EE) or PoB's number?"
```
