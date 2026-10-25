---
type: interaction
status: draft
pob_refs: [HitSpeed, Speed, SkillTriggerRate, HitChance, ProjectileCount, ActiveTotemLimit, conditionEnemyColdExposure, enemySpeed]
source: "wiki Hit rev 1650022, Ailment rev 1673310, Charge rev 1700592, Exposure rev 1673498; PoB 2.67.2 CalcOffence.lua, CalcTriggers.lua, ConfigOptions.lua; mechanics-modeler-uptime.md, mechanics-researcher-uptime.md, skill-gem-analyst-uptime.md, pob-coverage-auditor-uptime.md (task 027)"
last_confirmed_patch: "3.29.x"
---

How often a "x% chance on hit" or "when hit" effect is actually up on the enemy (or on you). PoB drops the chance: the Eye of Malice 25% exposure becomes a checkbox with 100% uptime. Calling it a risk without hit rate x duration was wrong (user correction 2026-10-25, tasks/021 log). Uptime comes from p, hits on one target per use (m), uses per second (V) and the duration (d); fast skills (Worb) are about 100%, slow single-hit skills are not. Do not apply this to ignite, bleed, poison or impale chance: PoB already expects those.

Pipeline: [[Damage calculation#Resistance, exposure and penetration]] - meta model: it times a chance-on-hit effect and acts at the step of that effect, e.g. Eye of Malice exposure (25%) lowers resistance in the resistance step; the uptime only scales how often that step's bonus is up

```interaction
id: chance-on-hit-uptime
mechanic: "A chance-on-hit effect with chance p and duration d is up on a target when at least one earlier hit inside the last d seconds applied it (the applying hit does not benefit from its own debuff, wiki Hit rev 1650022); uptime depends on hit rate on ONE target, not on the config checkbox"
family: uptime
pipeline_step: ["Damage calculation#Resistance, exposure and penetration"]
pipeline_why: "meta model: it times a chance-on-hit effect and acts at the step of that effect, e.g. Eye of Malice exposure (25%) lowers resistance in the resistance step; the uptime only scales how often that step's bonus is up"
target: enemy
related: [exposure, freeze, shock, chill, power-charges, frenzy-charges, flask-uptime]
pob:
  measured: config
  how: "PoB drops the chance. Exposure chance only sets a CanApply flag (CalcOffence.lua:4269-4277); the effect is the checkbox conditionEnemyColdExposure = 100% uptime when ticked (ConfigOptions.lua:1973-1981). Shock/chill/freeze chance only gates >0 (CalcOffence.lua:5399, 5430). Withered and Blind are config only. Uses/s = output.HitSpeed if set else output.Speed (CalcOffence.lua:2275-2294, 2473-2485); triggered skills use output.SkillTriggerRate which becomes Speed (CalcTriggers.lua:799-822); TotalDPS = AverageDamage x (HitSpeed or Speed) x dpsMultiplier (CalcOffence.lua:3801). ProjectileCount is NOT in TotalDPS except for SequentialProjectiles (CalcOffence.lua:805, 817). Precedent for a chance x hit-rate model: culling 1-(1-crit)^hitRate (CalcOffence.lua:3300-3305). PoB already expects ignite/bleed/poison chance (CalcOffence.lua:5030-5040, 4446-4457, 4727) and impale chance (5600-5622): do not apply this note to them"
  config:
    - {var: conditionEnemyColdExposure, default: false, ref: "Modules/ConfigOptions.lua:1973-1981", class: b}
    - {var: conditionEnemyShocked, default: false, ref: "Modules/ConfigOptions.lua:1943", class: b}
    - {var: conditionEnemyChilled, default: false, ref: "Modules/ConfigOptions.lua:1899", class: b}
    - {var: multiplierWitheredStackCount, default: 0, ref: "Modules/ConfigOptions.lua:1839", class: c}
    - {var: conditionEnemyBlinded, default: false, ref: "Modules/ConfigOptions.lua:1860", class: b}
    - {var: enemySpeed, default: 700, ref: "Modules/ConfigOptions.lua:2362 (boss presets 2318-2320); read only at CalcDefence.lua:2963-2965, so we must apply it ourselves", class: b}
  unparsed: []
model:
  proposed_kind: on_hit_uptime
  inputs:
    from_pob: [HitSpeed, Speed, SkillTriggerRate, HitChance, "ActiveTotemLimit or TotemsSummoned (totems, not in TotalDPS)", "effect duration d (PoB / vault note)"]
    from_scenario: ["m = hits per use on ONE target (Worb from Models/Winter Orb projectile overlap = 4; FR from Models/Projectiles hitting a single target; shotgun rule = 1 for simultaneous projectiles, e.g. EK)", "E = 1000/enemySpeed enemy hits per s on you (class b ASSUMPTION; no pinnacle hit-rate source found)"]
  params: {threshold_warn_u: 0.95, threshold_warn_error_share: 0.01, tick_box_u: 0.99, enemy_speed_ms_default: 700}
  formula: "V = uses/s on the target (sum over ALL skills hitting it: CoC Cyclone 8.92 + EK 8.93 = 17.85/s; DoT-only skills have no hits, p never rolls); m hits per use on that target (never also multiply the hand-set gem count when m comes from a model; totems x active totem count); P = 1-(1-p)^m; n = ceil(V*d)-1 earlier uses inside d. REFRESH/independent instances: u = 1-(1-p)^(m*n); random timing: u = 1-exp(-p*H*d), H = m*V (take min of regular and Poisson for irregular own hits). NO-REAPPLY: u = n/(n+1/P); random: u = d/(d+1/(p*H)). COOLDOWN c: a = ceil(V*c)-1, k = max(n-a,0), u = [min(a,n) + (1-(1-P)^k)/P] / [a + 1/P]; Poisson c<d: u = [c + (1-exp(-lambda*(d-c)))/lambda] / [c + 1/lambda], c>=d: u = d/(c + 1/lambda), lambda = p*H. WHEN HIT (Poisson): u = 1-exp(-p*E*d) refresh, d/(d+1/(p*E)) no-reapply; blocked hits count, evaded do not. Floor u to a whole percent. FEED: u >= 0.99 -> tick the PoB box; else blend DPS = u*DPS_on + (1-u)*DPS_off from two PoB runs (hit damage exact in expectation; use u_t for damage over time; never blend EHP or time-to-kill). WARN (proposal): u < 0.95 OR (1-u)*(DPS_on-DPS_off) > 1% of DPS. DISPLAY: case, timing, p, m, V, H, d, n, u, DPS on/off/blended, error if ticked. Minimum rate for u 0.95 at p 0.25, d 4, m 1: V > 2.75/s (Poisson 3.00/s)"
  calibration: "no norm found; worked: Worb HitSpeed 6.45 volleys/s x 4 = 25.8 hits/s -> Eye of Malice (d 4) u about 100% (floor 99%); 1.5 uses/s single hit (n 5) u = 76% -> warn + blend (base form 82% is optimistic); The Pandemonius 1 s chill at E 0.5/s u = 39% -> warn. The task 021 log figure '5.1 volleys/s, about 15 hits/s' was wrong (stages clamp 11, cast speed adds, 6 projectiles; skill-gem-analyst-uptime.md)"
providers:
  - {kind: unique, name: "Eye of Malice", slot: Helmet, role: applies, target: enemy, text: "25% chance to inflict Cold Exposure on Hit; 25% chance to inflict Fire Exposure on Hit (exposure -10% resist, 4 s default)", source: "Data/Uniques/helmet.lua:1448-1450; Modules/ModParser.lua:848-851,4847-4850; Modules/CalcOffence.lua:503; see [[Exposure]]", pob: config}
  - {kind: mastery, name: "Cold Mastery (effect 13267)", slot: tree, role: applies, target: enemy, text: "10% Chance to Inflict Cold Exposure on Hit with Cold Damage", source: "TreeData/3_29/tree.lua:54766", pob: config}
  - {kind: support, name: "Awakened Cold Penetration Support", slot: any, role: applies, target: enemy, text: "L5: 10% chance to inflict Cold Exposure on hit (Awakened Fire / Lightning Penetration likewise)", source: "Data/Skills/sup_dex.lua:1394; sup_str.lua:2260; sup_int.lua:4617", pob: partial}
  - {kind: notable, name: "Corrosive Elements", slot: tree, role: applies, target: enemy, text: "Cold/Fire/Lightning Skills have a 25% chance to apply <type> Exposure on Hit", source: "TreeData/3_29/tree.lua:87065 (node 2306); Data/ModCache.lua:14741", pob: config}
  - {kind: gem, name: "freeze chance providers", slot: any, role: applies, target: enemy, text: "chance to Freeze on hit (PoB gates on chance > 0 only, no uptime); providers listed in [[Freeze]]", source: "Modules/CalcOffence.lua:5430; vault Freeze.md", pob: config}
  - {kind: gem, name: "shock chance providers", slot: any, role: applies, target: enemy, text: "chance to Shock on hit (PoB gates on chance > 0 only, no uptime); providers listed in [[Shock]]", source: "Modules/CalcOffence.lua:5399; vault Shock.md", pob: config}
  - {kind: unique, name: "The Pandemonius", slot: Amulet, role: applies, target: enemy, text: "Chill Enemy for 1 s when Hit (30% reduced Action Speed; when-hit needs an enemy to hit you, so E, not your hit rate)", source: "Data/Uniques/amulet.lua:585; Data/ModCache.lua:14718 (unparsed, PoB does not model it); wiki The Pandemonius rev 1675036; see [[Chill]]", pob: partial}
  - {kind: unique, name: "Icetomb", slot: Body Armour, role: applies, target: enemy, text: "20% chance to Freeze Enemies for 1 second when they Hit you", source: "Data/Uniques/body.lua:1018 (variant 3); Data/ModCache.lua:6316; see [[Freeze]]", pob: partial, variant: "variant 3"}
  - {kind: support, name: "Hypothermia Support", slot: any, role: applies, target: enemy, text: "+20% chance to freeze CHILLED enemies (the chance gates only; the enemy must already be chilled)", source: "Data/SkillStatMap.lua:1055-1056; Data/Skills/sup_dex.lua:2335-2382; see [[Freeze]]", pob: partial}
  - {kind: unique, name: "Malachai's Loop", slot: shield, role: sustains, target: self, text: "20% chance on Hit to gain a Power Charge (charges last 10 s, refreshed on every gain, at most 1 per skill use: use uses/s, not hits)", source: "PoB Data/Uniques/shield.lua:669-674 (variant 4); wiki Charge rev 1700592; see [[Power charges]]", pob: partial}
  - {kind: unique, name: "Replica Tulfall", slot: Wand, role: sustains, target: self, text: "50% chance to gain a Power Charge when you Hit a Frozen Enemy (needs the enemy frozen as well: multiply the freeze uptime)", source: "Data/Uniques/wand.lua:438; see [[Power charges]]", pob: none}
makes_redundant: []
conflicts:
  - {with: "Elemental Equilibrium (keystone)", effect: "hits remove exposure to the hit element, so exposure from your own element is lost; the uptime of the other-element exposure is a separate model", source: "TreeData/3_29/tree.lua:62108; see [[Exposure]]"}
conditions:
  - {text: "applies only where PoB drops the chance: exposure flags, shock/chill/freeze chance (gate only), Withered and Blind (config), curse on hit, charges and Onslaught on hit, when-hit effects; NOT ignite, bleed, poison, impale chance (PoB already expects them)", source: "CalcOffence.lua:5030-5040, 4446-4457, 4727, 5600-5622; pob-coverage-auditor-uptime.md"}
  - {text: "an on-hit effect needs a hit that lands; blocked hits do not apply on-hit effects but do trigger when-hit effects of the defender; evaded hits trigger neither", source: "wiki Hit rev 1650022"}
  - {text: "same-ailment instances have independent timers, only the strongest applies; a new elemental ailment does not refresh the old one but covers to now+D when equal or stronger, so 1-(1-p)^n is exact for equal-strength re-applications", source: "wiki Ailment rev 1673310"}
  - {text: "durations (refresh unless noted): Exposure 4 s; Shock 2 s; Chill 2 s; Freeze 0.06 s per 1% of ailment threshold max 3 s (Icetomb 1 s); Scorch, Brittle, Sap 4 s; Hextouch = linked hex duration with -35% (L1) to -18% (L40) less curse duration; item curse-on-hit = hex at gem level 1 no supports: 8 s, Temporal Chains 5 s; Maim, Hinder, Blind, Covered in Ash 4 s; Intimidate, Unnerve 4 s (item text); Onslaught 4 s refreshed on gain; charges 10 s, all charges reset on every gain, global on you", source: "wiki Exposure rev 1673498, Shock rev 1606037, Chill rev 1596635, Freeze rev 1630938, Scorch rev 1673547, Brittle rev 1553576, Sapped rev 1660590, Maim rev 1702496, Hinder rev 1660573, Blind rev 1697260, Covered in Ash rev 1673503, Onslaught rev 1493254, Charge rev 1700592; PoB Modules/ModParser.lua:3383, Data/Skills/sup_int.lua:1507-1566, Data/ModCache.lua:3635, 3665"}
  - {text: "Withered: 2 s per stack, NOT refreshed, up to 15 stacks; apply 1-(1-p)^n per stack (steady stack count about hits per 2 s, cap 15), not per debuff", source: "wiki Withered rev 1702206"}
  - {text: "debuffs on enemies are per target; buffs and charges on you are global", source: "wiki Buff rev 1701074; Charge rev 1700592"}
uptime:
  Mapping:       {value: model, config: {conditionEnemyColdExposure: "model: tick only when u >= 0.99, else blend two PoB runs"}, reasoning: "trash packs: hit rate on ONE target is high for Worb (HitSpeed 6.45 x 4 = 25.8 hits/s, u about 100%) and CoC EK (17.85 uses/s); slow single-hit skills and when-hit effects need the model", source: "skill-gem-analyst-uptime.md; mechanics-modeler-uptime.md"}
  Pinnacle Boss: {value: model, config: {conditionEnemyColdExposure: "model: same rule; when-hit effects use E = 1000/enemySpeed (class b ASSUMPTION, boss presets ConfigOptions.lua:2318-2320)"}, reasoning: "bosses are one target, so m and V as above; phases without hits cut V; no pinnacle hit-rate source found, so every when-hit uptime stays an assumption", source: "Modules/ConfigOptions.lua:2318-2320, 2362; mechanics-researcher-uptime.md"}
seeds: [Worb, EK, FR]
sources:
  - {ref: "https://www.poewiki.net/wiki/Hit (rev 1650022)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Ailment (rev 1673310)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Charge (rev 1700592)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Exposure (rev 1673498)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcOffence.lua:805,817,2275-2294,2473-2485,3300-3305,3801,4269-4277,4446-4457,4727,5030-5040,5399,5430,5600-5622; Modules/CalcTriggers.lua:799-822; Modules/ConfigOptions.lua:1839,1860,1899,1943,1973-1981,2318-2320,2362; Modules/ModParser.lua:3383", kind: pob, patch: "3.29"}
  - {ref: "user correction 2026-10-25, tasks/021-generator-v1.md log (Eye of Malice 25% called a risk without hit rate x duration)", kind: user, patch: "3.29"}
not_verified:
  - "whether re-applying Exposure refreshes its duration (wiki silent; only 'strongest per element applies'; the model assumes equal-strength re-application covers to now+D)"
  - "whether re-applying the same curse refreshes its timer (wiki silent; only 'a different curse expires the oldest')"
  - "refresh behaviour for Maim, Hinder, Blind, Intimidate, Unnerve, Covered in Ash"
  - "whether sibling projectiles of the same volley benefit from each other's application (assumed not)"
  - "Worb 4 vs 5 hits per volley at 6 projectiles and 2.6 m (vault model 4; community norm covers 5 projectiles only)"
  - "the 1% DPS error budget is a proposal, not a sourced number"
  - "enemy hit rate on the player (no pinnacle hit-rate source found; E is an assumption)"
  - "server-tick rounding of effect durations and non-trigger internal cooldowns"
open_questions:
  - "Confirm the thresholds: warn at u < 0.95, error budget 1% of DPS, tick the PoB box only at u >= 0.99?"
```
