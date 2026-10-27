---
type: interaction
status: draft
pob_refs: [enemyIsBoss, enemyLevel, AilmentThreshold, monsterAilmentThresholdTable, enemyThreshold, FreezeDurationMod, ShockEffectMod, ChillEffectMod]
source: "PoB 2.67.2 Modules/CalcOffence.lua:5328-5343, ConfigOptions.lua, Data/Misc.lua tables; poewiki Ailment rev 1673310, Freeze rev 1630938, Shock rev 1606037 (fetched 2026-10-24); script on Data/Misc.lua by mechanics-modeler 2026-10-24; vault Models/Own shock effect"
last_confirmed_patch: "3.29.x"
---

The ailment threshold T is the number every non-damaging ailment is measured against: freeze duration (0.06 s per 1% of T in one hit), shock and chill strength ((D/T)^0.4), and the 5% / 0.3 s minimums. The wiki only says T is "typically equal to the monster's maximum life, reduced for especially high-life monsters" (3.15.0 rebalance); PoB multiplies the level table by its own boss factors. This note is shared by [[Freeze]], [[Shock]], [[Chill]]; the vault already carries the PoB chain in [[Own shock effect]]. The boss factors are PoB data that could not be checked against the wiki.

Pipeline: [[Damage calculation#Ailments from hits]] - the threshold is the divisor of every non-damaging ailment (freeze duration, shock and chill strength), so a bigger boss threshold shrinks them in the ailments-from-hits step

```interaction
id: enemy-ailment-threshold
mechanic: "T = monsterAilmentThresholdTable[level] x 7.68 (any boss) x mapLevelBossLifeMult x mapLevelBossAilmentMult x enemy Life more x AilmentThreshold more (config Boss +488%, Pinnacle/Uber +404%); wiki: roughly the monster's maximum life, reduced for especially high-life monsters (3.15.0), maximum about 800 million"
family: ailment
pipeline_step: ["Damage calculation#Ailments from hits"]
pipeline_why: "the threshold is the divisor of every non-damaging ailment (freeze duration, shock and chill strength), so a bigger boss threshold shrinks them in the ailments-from-hits step"
target: enemy
related: [freeze, shock, chill, shatter, elemental-ailment-count]
pob:
  measured: partial
  how: "enemyThreshold built at CalcOffence.lua:5328-5343 and used for the chill / shock / scorch / brittle / sap effect tables (breakdown only); freeze prints only a stale text line (5410-5411) and never applies the boss multiplier; no output key, the number must be reconstructed from Data/Misc.lua:15,471-474 and ConfigOptions.lua:2122,2157,2191"
  config:
    - {var: enemyIsBoss, default: "Pinnacle (list index 3: None / Boss / Pinnacle / Uber)", ref: "Modules/ConfigOptions.lua:2086", class: b}
    - {var: enemyLevel, default: "84 in the golden Worb.xml", ref: "Modules/ConfigOptions.lua (enemy level)", class: b}
    - {var: ailmentMode, default: "AVERAGE", ref: "Modules/ConfigOptions.lua:210", class: b}
  unparsed: []
model:
  proposed_kind: enemy_ailment_threshold
  inputs:
    from_pob: [enemyIsBoss, enemyLevel, "Data/Misc.lua monsterAilmentThresholdTable", "map level multipliers (Data/Misc.lua:471-474)", "enemy Life more", "AilmentThreshold more"]
    from_scenario: [enemyIsBoss, enemyLevel]
  params: {boss_mult: 7.68, standard_boss_more: 4.88, pinnacle_uber_more: 4.04}
  formula: "T = table[level] * (7.68 if boss else 1) * mapLifeMult * mapBossAilmentMult * LifeMore * AilmentThresholdMore; computed T (script on Misc.lua): level 84: Pinnacle/Uber 6,349,995, Standard Boss 7,408,328, no boss 35,295; level 85: 6,741,575 / 7,865,171 / 38,853; level 83: 5,473,455 / 6,385,697 / 32,017. Consumers: freeze d = 6*(D/T)*FreezeDurationMod seconds (min 0.3 s needs D >= T/(20*FreezeDurationMod)); shock/chill E = 50*(D/T)^0.4*effectMod"
  calibration: "no community or wiki norm for boss thresholds; PoB's own table and multipliers are the only source (Standard Boss T is HIGHER than Pinnacle in PoB: +488% vs +404%); wiki Shock page has only a 2020 playtest estimate for Sirus (about 25M, 35% of life)"
providers: []
makes_redundant: []
conflicts:
  - {with: "PoB freeze breakdown text vs PoB code", effect: "text says T is 'about equal to Life except on bosses where it is about half of their life' (CalcOffence.lua:5411) but the code multiplies by 7.68 and +404% / +488% (5333-5343); the text is stale", source: "Modules/CalcOffence.lua:5411 vs 5333-5343"}
  - {with: "wiki vs PoB boss multipliers", effect: "the wiki documents NO boss multiplier for standard, pinnacle or uber bosses; PoB's 7.68 / 488% / 404% and map multipliers come from PoB developers' data and could not be checked", source: "https://www.poewiki.net/wiki/Ailment rev 1673310; Modules/ConfigOptions.lua:2122,2157,2191"}
conditions:
  - {text: "wiki: threshold is typically equal to maximum life, reduced for especially high-life monsters; maximum about 800 million (YouTube source); 3.15.0 rebalanced it, reducing it for particularly tough endgame bosses", source: "https://www.poewiki.net/wiki/Ailment rev 1673310; Freeze version history 3.15.0"}
  - {text: "PoB boss multipliers: enemyThreshold = table[level] x (isBoss and 7.68 or 1) x mapLife(Boss)Mult x enemyDB Life more x mapBossAilmentMult x AilmentThreshold more; config adds AilmentThreshold MORE 488 (Boss) / 404 (Pinnacle, Uber)", source: "Modules/CalcOffence.lua:5333-5343; Modules/ConfigOptions.lua:2122,2157,2191; Data/Misc.lua:15,471-474"}
uptime:
  Mapping:
    value: pob
    config: {enemyIsBoss: "None for packs; the saved Pinnacle threshold still applies if the scenario sets no enemyIsBoss"}
    reasoning: "static enemy property, not an uptime; no-boss T is tiny (35,295 at level 84), so almost any crit freezes or shocks a pack monster"
    source: "Modules/CalcOffence.lua:5333-5343; vault Models/Own shock effect (Scenario notes set no enemyIsBoss, so Mapping still uses the saved Pinnacle threshold)"
  Pinnacle Boss:
    value: pob
    config: {enemyIsBoss: "Pinnacle (default), enemyLevel as set"}
    reasoning: "use PoB's own threshold; the freeze and shock models take T from here"
    source: "Modules/ConfigOptions.lua:2086,2157; Data/Misc.lua:471-474"
seeds: [Worb, FR]
sources:
  - {ref: "https://www.poewiki.net/wiki/Ailment (rev 1673310, 2026-07-11)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Shock (rev 1606037), Sirus estimate", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcOffence.lua:5328-5343,5410-5411; Modules/ConfigOptions.lua:2086,2122,2157,2191; Data/Misc.lua:15,471-474 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "wiki Freeze version history 3.15.0 (threshold rebalance)", kind: patch_notes, patch: "3.29"}
not_verified:
  - "exact ailment-threshold numbers for real pinnacle/uber bosses in 3.29 (wiki only has the Sirus estimate; PoB uses its own multipliers)"
  - "the generic boss threshold (already UNVERIFIED in vault Models/Own shock effect)"
  - "side finding: vault Models/Own shock effect lists Pinnacle T 6,349,995 (level 84) next to Standard 7,865,171 and None 38,853 (level 85 values), a mixed-level list; level 84 values here are Pinnacle 6,349,995, Standard 7,408,328, None 35,295"
open_questions:
  - "Which enemy level and boss tier should the Pinnacle Boss scenario pin (PoB default Pinnacle, golden Worb level 84)?"
```
