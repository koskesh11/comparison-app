---
type: interaction
status: draft
pob_refs: [FireResist, ColdResist, LightningResist, ChaosResist, ElementalResist, FireExposure, ColdExposure, LightningExposure, ExtraExposure, ExposureEffect, ColdPenetration, FirePenetration, LightningPenetration, ElementalPenetration, ChaosPenetration, CannotElePenIgnore, HitsInvertEleResChance, enemyIsBoss, EnemyMaxResist]
source: "poewiki Resistance penetration rev 1673467, Resistance rev 1659347, Exposure rev 1673498; PoB 2.67.2 CalcOffence.lua / CalcPerform.lua / ConfigOptions.lua / ModParser.lua / Data.lua (headless measurements M5, task 027 batch 1, b1-pob-coverage-auditor.md)"
last_confirmed_patch: "3.29.x"
---

Resistance penetration lowers the enemy's effective resistance for one hit by N points AFTER the maximum-resistance cap, with no floor; it applies to hits only, never to damage over time or ailments. Curses and exposure instead lower the uncapped resistance BEFORE the cap, so they are partly absorbed while the enemy is above its cap and penetration is not. Below the cap and with an unchanged resistance multiplier one point of penetration equals one point of exposure or curse. Related: [[Exposure]], [[Curse limit]], [[Damage over time multiplier]].

Pipeline: [[Damage calculation#Resistance, exposure and penetration]] - order inside the step: base + curses + exposure into the enemy resist sum, x (1 + increased enemy resist), clamp to [-200, max res], subtract penetration, then (1 - that value) multiplies the hit.

Impact (arithmetic from the PoB formula, not measured on a Fireball build): EK "CoC EK Assa" = 0, because all its damage is physical (probe: Physical avg 88,858, all other types 0, pen 0) so elemental penetration and exposure change nothing; PoB's physical analog is enemy armour (CalcOffence.lua:3512-3524), not measured here. Fireball Elementalist at Pinnacle (enemy elemental res 50, ConfigOptions.lua:2162): DPS x (1 - (R - p)) / (1 - R) with R = resist after curses/exposure. 30 penetration at R 50 = x1.6; fire exposure -10 plus Mastermind of Discord -25 gives R 15 = x1.70 alone (needs a real exposure source and the box ticked); 30 penetration on top of that is a further x1.35 (1.15/0.85). Exposure + Mastermind and penetration are multiplicative, each later point worth less. Against the 500k target (last run TotalDPS 252k needs x1.98) the evidence says to put Mastermind + an exposure source before more penetration; Eye of Malice only helps cold (Worb), not fire at a positive total.

```interaction
id: penetration
mechanic: "Resistance penetration lowers a hit's effective enemy resistance by N points after the cap, R_t = min(r_t, m_t) - p_t, with no minimum (wiki rev 1673467); hits only, cannot apply to damage over time; curses and exposure act on the uncapped value before the cap (Resistance rev 1659347)"
family: defence
pipeline_step: ["Damage calculation#Resistance, exposure and penetration"]
pipeline_why: "penetration is the last operation of the resist step (after curses and exposure in the resist sum, after the clamp to [-200, max res]) and before the damage-taken mods; it is a property of the hit, so DoT and ailment damage skip it"
target: enemy
related: [exposure, curse-limit, damage-calculation, damage-over-time-multiplier]
pob:
  measured: full
  how: "hit path only: pen = Sum(BASE, <Type>Penetration, ElementalPenetration) (CalcOffence.lua:3555-3564), effectiveResist = (resist - pen) * useResChance (3591), effMult *= 1 - effectiveResist/100 (3593), no floor after penetration. calcResistForType (CalcOffence.lua:494-507): Override first (495); max resist 75 (data.misc.EnemyMaxResist, Data.lua:259) raised by the config enemy-resist box up to MaxResistCap 90 (Data.lua:246) unless enemyMaxResist (496); else Sum(BASE, <Type>Resist [+ ElementalResist]) * max(calcLib.mod(enemyDB, <Type>Resist, ElementalResist), 0) (503); return max(min(resist, maxResist), ResistFloor -200) (506; ResistFloor Data.lua:245). Every BASE mod sits in the sum: config enemy resist box (ConfigOptions.lua:2251-2259), curses (Skill:Frostbite -37 measured), exposure (CalcPerform.lua:3631-3657: strongest exposure + ExtraExposure, scaled by ExposureEffect inc), tree ElementalResist. Curses and exposure therefore STACK additively in PoB (Worb: config exposure -35 + Frostbite -37 + enemy 50 + tree -5 = -27 summed). DoT and ailment paths call calcResistForType(type, dotCfg) without pen (CalcOffence.lua:4851, 5192, 5202, 5225, 5713, 5755, 5830), matching the wiki. Flags: Ignore<Type>Resistance / IgnoreElementalResistances / ChanceToIgnore... make the resist 0 and discard pen (CalcOffence.lua:3495-3503; ModParser.lua:2909,3264,3581,4529); CannotElePenIgnore removes penetration AND ignore (ModParser.lua:4206; CalcOffence.lua:3584-3586); HitsInvertEleResChance inverts the capped resist before pen: ((resist - pen)(1-inv) + (-resist - pen)inv) (ModParser.lua:2473,3582; CalcOffence.lua:3589). Physical has no resist: armour / PhysicalDamageReduction (CalcOffence.lua:3512-3524)."
  config:
    - {var: enemyIsBoss, default: "Pinnacle (list index 3)", ref: "Modules/ConfigOptions.lua:2086 (enemy base resist: None 0 at 2092-2095, Boss 40 elemental / 25 chaos at 2128, Pinnacle 50 / 30 at 2162-2165, Uber higher at 2198)", class: b}
    - {var: conditionEnemyFireExposure, default: false, ref: "Modules/ConfigOptions.lua:1973-1981 (exposure side only; no config box gates penetration itself; exposure per [[Exposure]])", class: b}
  unparsed:
    - "none seen for the penetration lines checked (Heart of Ice 'Damage Penetrates 6% Cold Resistance', Cold/Elemental Penetration supports, Bloodbond, Khatal's Weeping); conditional lines such as 'Damage Penetrates N% Cold Resistance against Chilled Enemies' parse with Condition tags and were not enumerated"
model: null
providers:
  # seed: Worb
  - {kind: notable, name: "Heart of Ice", slot: tree, role: scales, target: enemy, text: "30% increased Cold Damage / Damage Penetrates 6% Cold Resistance (Worb: ColdPenetration 6, source Tree:8833)", source: "TreeData/3_29/tree.lua:54725-54737", pob: full}
  # alternatives (at most 12)
  - {kind: support, name: "Cold Penetration Support", slot: any, role: scales, target: enemy, text: "supported hits penetrate enemy cold resistance (stat base_reduce_enemy_cold_resistance_% -> ColdPenetration)", source: "Data/Skills/sup_dex.lua:1313; Data/SkillStatMap.lua:805-807", pob: full}
  - {kind: support, name: "Awakened Cold Penetration Support", slot: any, role: scales, target: enemy, text: "cold penetration plus base_inflict_cold_exposure_on_hit_%_chance (the exposure part needs the box)", source: "Data/Skills/sup_dex.lua:1371", pob: partial}
  - {kind: support, name: "Fire Penetration Support / Lightning Penetration Support", slot: any, role: scales, target: enemy, text: "supported hits penetrate enemy fire / lightning resistance", source: "Data/Skills/sup_str.lua:2202; Data/Skills/sup_int.lua:4423", pob: full}
  - {kind: support, name: "Elemental Penetration Support (via Bloodbond)", slot: any, role: scales, target: enemy, text: "reduce_enemy_elemental_resistance_% -> ElementalPenetration (Bloodbond socketed)", source: "Data/Skills/other.lua:1723; Data/SkillStatMap.lua:814; Data/Uniques/body.lua:1341-1342", pob: full}
  - {kind: unique, name: "Khatal's Weeping", slot: Amulet, role: scales, target: enemy, text: "Damage Penetrates (0-20)% Elemental Resistances; variants with 10% Fire Resistance", source: "Data/Uniques/amulet.lua:1190,1356", pob: full}
  - {kind: unique, name: "Augyre", slot: Mace, role: scales, target: enemy, text: "Socketed Gems are Supported by Level 15 Cold Penetration", source: "Data/Uniques/mace.lua:333", pob: full}
  - {kind: unique, name: "Agnerod East", slot: Staff, role: scales, target: enemy, text: "Damage Penetrates (8-10)% Elemental Resistances while you are Chilled", source: "Data/Uniques/staff.lua:410", pob: config}
  - {kind: unique, name: "Atziri's Promise", slot: Flask, role: scales, target: enemy, text: "During Effect, Damage Penetrates (5-8)% Resistance of each Element for which your Uncapped Elemental Resistance is highest", source: "Data/Uniques/flask.lua:493", pob: config}
  - {kind: unique, name: "Abhorrent Interrogation", slot: Gloves, role: blocks, target: enemy, text: "Your Hits cannot Penetrate or ignore Elemental Resistances (CannotElePenIgnore)", source: "Data/Uniques/gloves.lua:912; Modules/ModParser.lua:4206", pob: full}
  - {kind: ascendancy, name: "Mastermind of Discord (Elementalist)", slot: tree, role: scales, target: enemy, text: "Exposure you inflict applies an extra -25% to the affected Resistance (exposure side: lowers the resist sum, not penetration; needs an exposure source and the box)", source: "TreeData/3_29/tree.lua:49969; Modules/ModParser.lua:2675", pob: full}
  - {kind: unique, name: "Eye of Malice", slot: Helmet, role: scales, target: enemy, text: "Nearby Enemies have 50% increased Fire and Cold Resistances; multiplies a negative resist sum (more negative) and hurts on a positive one; multiplies exposure/curse points x1.5 but not penetration", source: "Data/Uniques/helmet.lua:1450; Modules/CalcOffence.lua:503", pob: full}
makes_redundant: []
conflicts:
  - {with: "Abhorrent Interrogation (unique gloves)", effect: "Your Hits cannot Penetrate or ignore Elemental Resistances: removes all elemental penetration sources above", source: "Data/Uniques/gloves.lua:912; Modules/ModParser.lua:4206"}
  - {with: "Eye of Malice (increased enemy resistance)", effect: "enemy resist = sum x 1.5 (measured mod 1.5): every exposure or curse point is worth 1.5 points, a penetration point 1.0; on Worb (sum -27, effective -40.5) +10 extra cold exposure gave +10.24% TotalDPS vs +10 cold penetration +6.83%; on a positive total the same line hurts", source: "Modules/CalcOffence.lua:503 vs 3591; Data/Uniques/helmet.lua:1450; b1-pob-coverage-auditor.md M5"}
  - {with: "enemy resistance above the cap (75, up to 90 with the config box)", effect: "exposure and curses are absorbed by the overcap, penetration is not (pen is subtracted after the clamp); formula from CalcOffence.lua:506,3591, no Worb/EK case reaches the cap (Worb effective -40.5, EK 50 < 75)", source: "Modules/CalcOffence.lua:506,3591; Resistance rev 1659347"}
conditions:
  - {text: "penetration applies to hits only; it cannot apply to damage over time", source: "https://www.poewiki.net/wiki/Resistance_penetration rev 1673467"}
  - {text: "effective resistance may be negative with no game-imposed minimum; the -200% cap applies to actual resistances, not to effective resistance", source: "https://www.poewiki.net/wiki/Resistance_penetration rev 1673467"}
  - {text: "Penetration applies to the capped resistance value (75% capped enemy with 30% penetration is hit as 45%); curses and exposure directly affect the uncapped value; cap -200% from 3.16.0, reduced-resistance cap 100% from 3.17.0", source: "https://www.poewiki.net/wiki/Resistance rev 1659347 (Version refs)"}
  - {text: "physical damage has no resistance step: enemy armour / PhysicalDamageReduction applies instead", source: "Modules/CalcOffence.lua:3512-3524"}
uptime:
  Mapping:
    value: always
    config: {enemyIsBoss: "None = enemy base resist 0 (ConfigOptions.lua:2092-2095), so each point is worth a smaller relative DPS gain; flask / Chilled / crit-conditional lines follow their own condition"}
    reasoning: "penetration is a stat on the hit, always on; only the conditional lines (Agnerod East while Chilled, Atziri's Promise during flask effect) depend on their condition"
    source: "Modules/CalcOffence.lua:3555-3564,3591; Modules/ConfigOptions.lua:2092-2095"
  Pinnacle Boss:
    value: always
    config: {enemyIsBoss: "Pinnacle (default, enemy elemental res 50, chaos 30; ConfigOptions.lua:2162-2165)"}
    reasoning: "wiki efficacy I = p/(1 - min(r,m)): 10 penetration at res 50 = +20%, at res 15 = +11.8%, at res -40.5 = +6.8% (Worb measured); Pinnacle is where penetration gives the most per point unless exposure and curses already drove the total down"
    source: "https://www.poewiki.net/wiki/Resistance_penetration rev 1673467; Modules/ConfigOptions.lua:2128,2162; b1-pob-coverage-auditor.md M5"
seeds: [Worb]
sources:
  - {ref: "https://www.poewiki.net/wiki/Resistance_penetration (rev 1673467)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Resistance (rev 1659347)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Exposure (rev 1673498)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcOffence.lua:494-507,3495-3503,3512-3524,3555-3593; Modules/CalcPerform.lua:3631-3657; Modules/ConfigOptions.lua:2086,2128,2162-2165,2251-2259; Data.lua:245,246,259; Modules/ModParser.lua:2473,3582,4206 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "headless measurement M5 on Worb (Aspect of the Brine King left out), task 027 batch 1, 2026-10-26: base 1,343,498; +10 cold penetration 1,435,204 (+6.83%); +10 extra cold exposure 1,481,057 (+10.24%)", kind: pob, patch: "3.29"}
not_verified:
  - "in-game stacking of a curse and exposure (PoB adds both as BASE into the resist sum, measured); no wiki quote found: the wiki only says both 'directly affect uncapped resistance values' (Resistance rev 1659347) and that only the strongest exposure per element applies (Exposure rev 1673498)"
  - "meaning of m_min(min, modDB:Override(nil,'ExposureMin')) when no ExposureMin exists (CalcPerform.lua:3655); PoB runs (see Exposure)"
  - "whether PoB's enemy resist INC multiplier (CalcOffence.lua:503) is the game's rule for monsters: the wiki states 'increased/reduced resistance are multiplicative against your uncapped resistances' for players (Resistance rev 1659347); the monster case rests on Eye of Malice's text only"
  - "Uber Pinnacle enemy resist numbers (ConfigOptions.lua:2198 not opened)"
  - "real map-monster base resistance: PoB's None = 0, the real value (about 0 plus map mods) was not looked up"
  - "the evidence's arithmetic check of M5 uses effective -46.5 -> -61.5 (1.615/1.465 = +10.2%) while the same file gives the base effective resist as -40.5 (sum -27 x 1.5); the measured +6.83% / +10.24% are PoB outputs, the hand arithmetic is not reconciled"
  - "the Fireball numbers (x1.6, x1.70, x1.35) are arithmetic from CalcOffence.lua:3591-3593, not measured on a Fireball build"
  - "weapon-local sources such as Ahn's Might (sword.lua:601, 'Attacks with this Weapon Penetrate 30% Elemental Resistances') and tincture.lua:42 were seen but not examined (attacks only)"
open_questions:
  - "Which Fireball seed build and config should the generator assume for the exposure box and enemy resistance (box state by the uptime rule), since the order Mastermind + exposure source before more penetration depends on it?"
```
