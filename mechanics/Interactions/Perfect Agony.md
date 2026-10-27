---
type: interaction
status: draft
pob_refs: [DotMultiplierIsCritMultiplier, NoCritMultiplier, AilmentsOnlyFromCrit, AilmentsAreNeverFromCrit, CritMultiplier, CritChance, IgniteChanceOnHit, IgniteChanceOnCrit, IgniteChance, ShockChance, ailmentMode, conditionEnemyShocked, Condition:CritRecently]
source: "poewiki Perfect Agony rev 1699073 (fetched 2026-10-26; 3.25.0 rework); PoB 2.67.2 CalcOffence.lua, ModParser.lua, ModTools.lua, ConfigOptions.lua, Data/ModCache.lua, Data/Uniques, TreeData/3_29/tree.lua; headless measurements on EK, Worb, FR and the Fireball file, tasks 027 batch 3c (pob-coverage-auditor-E.md)"
last_confirmed_patch: "3.29.x"
---

Perfect Agony (keystone) turns the crit multiplier into the damage over time multiplier of ailments and takes it away from hits. Tree text (TreeData/3_29/tree.lua:80922, node 23407): "Damage over Time Multiplier for Ailments is equal to Critical Strike Multiplier / Critical Strikes do not deal extra Damage / Non-Critical Strikes cannot inflict Ailments". It only pays when most of the damage IS an ailment ([[Ignite]], [[Bleed]], [[Poison]]) and the crit chance is near 100%; on a hit build it costs 79-91% of the DPS (measured below). Related: [[Damage over time multiplier]], [[Critical strike multiplier]], [[Shock]].

Pipeline: [[Damage calculation#Critical strike]] - PoB sets the hit crit multiplier to 1 (CalcOffence.lua:3204) so the crit step no longer multiplies hit damage; the ailment base is then multiplied at [[Damage calculation#Damage over time]] by 1 + crit multiplier (an OVERRIDE of DotMultiplier, CalcOffence.lua:4185-4195), and [[Damage calculation#Ailments from hits]] only counts ailment chance on crit (4290-4294).

Measured headless, in memory only, keystone force-allocated alone ('keystone only, path cost not included'); enemy level from the run's env.enemyLevel: 85 at None, 84 at Pinnacle. Pinnacle / None, TotalDPS and FullDPS:
- Fireball file (NOT VIABLE, not a validator seed; crit 21.15%, ignite from the build): TotalDPS 251,999.7 -> 180,853.7 (-28.2%) / 323,573.3 -> 241,379.8 (-25.4%); FullDPS 285,468.3 -> 227,862.2 (-20.2%) / 390,510.5 -> 327,178.7 (-16.2%); IgniteDPS 33,468.6 -> 47,008.6 (+40.5%) / 66,937.2 -> 85,798.9 (+28.2%); IgniteChanceOnHit 25 -> 0; IgniteChance 89.35 -> 63.60; ShockChance and ChillChance 100 -> 21.15; CritMultiplier 2.86 -> 1.
- FR (crit 100%, no DoT): TotalDPS 166,643.3 -> 28,149.2 (-83.1%) / 194,966.9 -> 34,385.7 (-82.4%); FullDPS 57,001,026 -> 8,652,487 (-84.8%) / 67,300,152 -> 10,618,800 (-84.2%). Nothing to gain: 100% crit already inflicts everything, the loss is the whole crit multiplier (5.92 -> 1).
- EK: TotalDPS 7,728,444.7 -> 793,474.8 (-89.7%) / 7,331,707.3 -> 793,474.8 (-89.2%); FullDPS 15,136,639 -> 1,385,862 (-90.8%) / 14,420,419 -> 1,431,808 (-90.1%). Its Cyclone bleed rises (Best Bleed DPS 1,566.2 -> 5,189.5) but that is tiny against the loss.
- Worb (Aspect of the Brine King left out, Winter Orb x5): TotalDPS 1,343,497.5 -> 275,023.7 (-79.5%) / 1,934,211.1 -> 415,820.9 (-78.5%); ShockChance 100 -> 93.39.

Risk 'non-crits cannot inflict ailments' on the Fireball file: the crit chance (21.15%) becomes the chance per hit to ignite, shock or chill. PoB still shows a full 40% shock bonus because the file's config box 'Is the enemy Shocked' is ticked (enemy DamageTaken INC 40 with the box, 0 without); with the box unticked Pinnacle TotalDPS is 129,181.2 under Perfect Agony (179,999.8 without it), with the box ticked 180,853.7. Shock uptime from the vault model: Speed 5.03 casts/s, Shock duration 3 s (PoB ShockDuration), p = 0.2115, m = 1 hit per cast on one target (assumption, Fireball has 5 projectiles): n = ceil(5.03 x 3) - 1 = 15, u = 1-(1-0.2115)^15 = 97%, so the box is right (see [[Chance on hit uptime]]).

```interaction
id: perfect-agony
mechanic: "Damage over Time Multiplier for Ailments equals your Critical Strike Multiplier (all other DoT multiplier, generic or conditional, is ignored; all crit multiplier sources count); Critical Strikes deal no extra damage; Non-Critical Strikes cannot inflict any ailment, damaging or not; ailments spread or proliferated without a hit are not blocked (wiki); Elemental Overload makes every hit count as a non-crit, so together no ailment from hits at all"
family: buff
target: self
related: [damage-over-time-multiplier, critical-strike-multiplier, critical-strike-chance, ignite, bleed, poison, shock, chance-on-hit-uptime]
pipeline_step: ["Damage calculation#Critical strike", "Damage calculation#Damage over time", "Damage calculation#Ailments from hits"]
pipeline_why: "PoB forces the hit crit multiplier to 1 (CalcOffence.lua:3204), then replaces the ailment DotMultiplier with the skill's crit multiplier (OVERRIDE, 4185-4195) which the ignite/bleed/poison DoT multipliers use (5149, 4531, 4832) instead of DotMultiplier + type multiplier, and sets every ailment's ChanceOnHit to 0 (4290-4294); so it acts on the crit step, the ailment-from-hit step and the DoT-multiplier step at once."
pob:
  measured: full
  how: "Keystone line parses in Data/ModCache.lua:15014 (DotMultiplierIsCritMultiplier), 14832 (NoCritMultiplier), 18441 (AilmentsOnlyFromCrit); the keystone name entry is ModCache.lua:18571 (Keystone LIST 'Perfect Agony' + Condition:HavePerfectAgony), merged by modLib.mergeKeystones (ModTools.lua:248-259); ModParser.lua:2324, 3564, 3686. Consumers: NoCritMultiplier -> CritMultiplier = 1 (CalcOffence.lua:3204-3205); DotMultiplierIsCritMultiplier -> DotMultiplier OVERRIDE = (Sum CritMultiplier or Override-100) + enemy SelfCritMultiplier, flag Ailment, condition CriticalStrike, per hand (4185-4195); AilmentsOnlyFromCrit -> <ailment>ChanceOnHit = 0 for Bleed, Poison, Ignite, Chill, Freeze, Shock, Scorch, Brittle, Sap (4290-4294, Data.lua:419); AilmentsAreNeverFromCrit with AilmentsOnlyFromCrit -> ChanceOnCrit = 0 (4299-4303). Ignite chance weights the crit share by 1-(1-crit)^igniteStacks (5183). Measured by force-allocating node 23407 alone on EK, FR, Worb and the Fireball file at None and Pinnacle (E_run.py), flags DotMultiplierIsCritMultiplier/NoCritMultiplier/AilmentsOnlyFromCrit all true. NOT modelled: a ticked ailment config box (conditionEnemyShocked, Chilled, Frozen, Ignited ...) still applies in full, although only crits can inflict it."
  config:
    - {var: ailmentMode, default: "AVERAGE", ref: "Modules/ConfigOptions.lua:210 (CRIT = crits only; the keystone forces crit-only anyway, CalcOffence.lua:4290)", class: c}
    - {var: conditionEnemyShocked, default: "false in the code, ticked in the Fireball file (hand-set)", ref: "Modules/ConfigOptions.lua:1943 (forced shock/DamageTaken regardless of crit chance)", class: c}
  unparsed: []
model: null
providers:
  - {kind: keystone, name: "Perfect Agony", slot: tree, role: applies, target: self, text: "Damage over Time Multiplier for Ailments is equal to Critical Strike Multiplier; Critical Strikes do not deal extra Damage; Non-Critical Strikes cannot inflict Ailments", source: "TreeData/3_29/tree.lua:80922 (node 23407); Data/ModCache.lua:18571", pob: full}
  - {kind: unique, name: "Replica Atziri's Acuity", slot: Gloves, role: applies, target: self, text: "You have Perfect Agony if you've dealt a Critical Strike recently", source: "Data/Uniques/gloves.lua:40; Data/ModCache.lua:22917 (Condition CritRecently)", pob: full}
  - {kind: flask, name: "Coralito's Signature", slot: Flask, role: applies, target: self, text: "Grants Perfect Agony during effect (variant 1, Pre 3.15.0 only; the current variant has no Perfect Agony)", source: "Data/Uniques/flask.lua:163; Data/ModCache.lua:16654 (Condition UsingFlask)", pob: full, variant: "variant 1 (Pre 3.15.0)"}
  - {kind: support, name: "Increased Critical Damage Support", slot: any, role: scales, target: self, text: "crit multiplier now scales the ailment DoT multiplier only (hit damage no longer gets it); EK, FR and Worb all carry it", source: "Data/Skills/sup_int.lua:3685; Modules/CalcOffence.lua:4185-4195", pob: full}
  - {kind: unique, name: "Marylene's Fallacy", slot: Amulet, role: scales, target: self, text: "+(210-240)% Global Critical Strike Multiplier (variants 4, 5), 40% less Critical Strike Chance; the wiki suggests it for single-stack ailments (ignite, plain bleed): one crit is enough, the multiplier is the DoT multiplier", source: "Data/Uniques/amulet.lua:855-866; wiki Perfect Agony rev 1699073", pob: full}
  - {kind: keystone, name: "Elemental Overload", slot: tree, role: blocks, target: self, text: "Ailments never count as being from Critical Strikes: together with Perfect Agony no ailment can be inflicted by a hit", source: "Modules/ModParser.lua:2237; Modules/CalcOffence.lua:4299-4303; wiki Perfect Agony rev 1699073", pob: full}
  - {kind: support, name: "Critical Strike Affliction Support", slot: any, role: blocks, target: self, text: "its ailment DoT multiplier from crits has no effect while Perfect Agony is allocated (wiki); in PoB the keystone's DotMultiplier OVERRIDE replaces the sum (5149, 4531)", source: "Data/Skills/sup_dex.lua:1458-1470; wiki Perfect Agony rev 1699073", pob: partial}
makes_redundant:
  - {provider: "Critical Strike Affliction Support", when: "Perfect Agony allocated", why: "wiki: no effect; PoB takes the OVERRIDE and ignores every other DotMultiplier source", source: "wiki Perfect Agony rev 1699073; Modules/CalcOffence.lua:5149"}
  - {provider: "'% chance to Ignite/Bleed/Poison/Shock/Chill on Hit' lines (the on-hit part)", when: "Perfect Agony allocated", why: "non-crits cannot inflict ailments: only the on-crit part works; measured IgniteChanceOnHit 25 -> 0 (Fireball file), 10 -> 0 (Worb), ChillChanceOnHit 100 -> 0 (EK)", source: "Modules/CalcOffence.lua:4290-4294; E_run.py measurements"}
conflicts:
  - {with: "hit-damage builds (EK, FR, Worb)", effect: "the whole crit multiplier is lost for hits: TotalDPS -79.5% (Worb) to -89.7% (EK) at Pinnacle; only an ailment-damage build gains (Fireball file IgniteDPS +40.5% but TotalDPS -28.2%, FullDPS -20.2%)", source: "E_run.py measurements; Modules/CalcOffence.lua:3204"}
  - {with: "Elemental Overload (keystone)", effect: "no ailments from hits at all (hits never count as crits for ailments, non-crits cannot inflict)", source: "wiki Perfect Agony rev 1699073; Modules/CalcOffence.lua:4299-4303"}
  - {with: "crit chance below 100%", effect: "chance per hit to apply any ailment = crit chance (Fireball file: 21.15% shock/chill, ignite 89.35 -> 63.60 by PoB's stack formula)", source: "E_run.py (FB); Modules/CalcOffence.lua:5183"}
  - {with: "ticked ailment config boxes", effect: "PoB keeps a ticked shock/chill/freeze box at full effect; with Perfect Agony and crit chance < 100% the box is only right if the uptime model says so (Fireball file 97%)", source: "Modules/ConfigOptions.lua:1943; E_shock.py"}
conditions:
  - {text: "all sources of critical strike multiplier (generic, local, conditional) feed the ailment DoT multiplier; every other DoT multiplier source is ignored", source: "wiki Perfect Agony rev 1699073 (forum 3532389 #13, #14); Modules/CalcOffence.lua:4185-4195"}
  - {text: "the stat also stops non-damaging ailments (shock, chill, freeze, scorch, brittle, sap) from non-crit hits", source: "wiki Perfect Agony rev 1699073; Modules/CalcOffence.lua:4290-4294"}
  - {text: "spread and proliferation (Ignite Proliferation Support, Master Toxicist) are not blocked, they are not inflicted by hits; PoB has no model for either", source: "wiki Perfect Agony rev 1699073 (forum 3532389 #33)"}
  - {text: "version history: before 3.25.0 the keystone gave 50% of crit multiplier to ailment DoT and 30% less damage with hits; the PoB code for that older form (CritMultiplierAppliesToDegen, 4176-4183) is still there but the 3_29 keystone does not use it", source: "wiki Perfect Agony rev 1699073 (3.25.0 row); Modules/CalcOffence.lua:4176-4183; TreeData/3_29/tree.lua:80922"}
uptime:
  Mapping:       {value: pob, config: {enemyIsBoss: "None / map monsters (enemy level 85 in the runs)"}, reasoning: "permanent keystone; use PoB's numbers (hit DPS lost, ailment DPS from crits). Packs die to the hit, so the ailment gain rarely repays the lost crit multiplier unless the build is an ailment build with crit chance near 100%", source: "E_run.py measurements; Modules/CalcOffence.lua:3204, 4185-4195"}
  Pinnacle Boss: {value: pob, config: {enemyIsBoss: "Pinnacle (default; enemy level 84 in the runs)"}, reasoning: "permanent keystone; ailment boxes (shock, chill) stay ticked in PoB: check them with the Chance on hit uptime model (Fireball file shock 97% at p 0.2115, 15 earlier casts in 3 s)", source: "E_run.py; E_shock.py; vault Chance on hit uptime"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Perfect_Agony (rev 1699073)", kind: wiki, patch: "3.29"}
  - {ref: "PoB TreeData/3_29/tree.lua:80922; Data/ModCache.lua:14832,15014,16654,18441,18571,22917; Modules/ModParser.lua:2237,2324,3564,3686; Modules/CalcOffence.lua:3204,4176-4195,4290-4303,5149,5183; Modules/ModTools.lua:248-259; Modules/ConfigOptions.lua:210,1943; Data/Uniques/gloves.lua:40, flask.lua:163, amulet.lua:855-866; Data/Skills/sup_dex.lua:1458", kind: pob, patch: "3.29"}
  - {ref: "tasks 027 batch 3c: scratchpad b3c/E/E_run.py, E_shock.py, summary.txt (headless, nothing saved)", kind: discovery, patch: "3.29"}
not_verified:
  - "whether the game's shock effect for crit-only shock matches PoB's hand-set effect box (ticked box = 40% DamageTaken in the Fireball file): PoB takes the config value, not a value from the hit"
  - "the exact PoB meaning of IgniteChance 63.60 under Perfect Agony (crit share over 'igniteStacks', CalcOffence.lua:5183 formula read, stack count not printed)"
  - "Critical Strike Affliction Support having no effect in PoB was not measured (only the wiki statement and the OVERRIDE read)"
  - "Replica Atziri's Acuity and Coralito's Signature: how often 'crit recently' / the flask is up (not measured; flask uptime belongs to the Flask uptime note)"
  - "Foulborn variants and the Impossible Escape jewel for this keystone: not checked"
  - "the Fireball file is not a viable build (name says so); its numbers only show the ailment mechanics"
open_questions:
  - "Should the generator ever offer Perfect Agony to a hit build? PoB measures -79% to -91% on all three seeds; it only paid on ailment damage with crit near 100% (none of the seeds)"
```
