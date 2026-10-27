---
type: interaction
status: draft
pob_refs: [CullPercent, CriticalCullPercent, CullMultiplier, CullingDPS, HitChance, HitSpeed, Speed, enemyIsBoss, Condition:RareOrUnique]
source: "poewiki Culling strike rev 1673452, Culling Strike Support rev 1681692, Cull the Weak Support rev 1682300, Headsman rev 1417684 (fetched 2026-10-25); PoB 2.67.2 CalcOffence.lua / Calcs.lua / ModParser.lua / SkillStatMap.lua / ConfigOptions.lua / Data/Skills / Data/Uniques / TreeData 3_29; tasks/reports/027-evidence/pob-coverage-auditor-uptime.md (precedent culling formula)"
last_confirmed_patch: "3.29.x"
---

Culling strike is an on-hit effect: a hit that leaves the target at 10% of maximum life or less (20% for Headsman, 30-47% but normal/magic only for Cull the Weak) kills it. PoB turns it into a FINAL multiplier on total DPS, 100 / (100 - CullPercent), so a plain 10% cull is +11.1% DPS, and it does not need a config tick. Its approach is the only place PoB itself turns a chance into a hit-rate probability: the crit-only cull is scaled by the chance of at least one crit in a second. What PoB cannot know: whether the boss can be culled, whether the cull lands before the fight ends at the slow end, and that damage over time cannot cull while PoB multiplies it anyway. Related: [[Chance on hit uptime]] (precedent), [[Freeze]] (cull vs Frozen) and [[Shatter]] (the recommended cull for DoT freezers).

Pipeline: [[Damage calculation#More and less]] - PoB applies the cull as a last multiplier on CombinedDPS after all hit, ailment and DoT damage is summed (CalcOffence.lua:6259-6262), so it behaves like a final "more" term but is really a time-to-kill saving of the last 10% of life; that is why it is exact for hit-based fights with a steady hit rate and wrong for pure damage over time.

```interaction
id: culling-strike
mechanic: "A Hit that leaves the target at 10% (Headsman 20%, Cull the Weak 30-47% on normal/magic only) of maximum life or less kills it; fires even if the hit dealt no damage or was fully mitigated, not if the hit was avoided; ignores energy shield and guard; a hit that kills cannot cull; damage over time cannot cull; works on all rarities incl. bosses except scripted deaths; PoB: DPS x 100/(100-CullPercent)"
family: trigger
target: enemy
related: [freeze, shatter, chance-on-hit-uptime, enemy-ailment-threshold, fight-length]
pipeline_step: ["Damage calculation#More and less"]
pipeline_why: "PoB multiplies the summed CombinedDPS (hits, ailments and DoT) by CullMultiplier = 100/(100 - CullPercent) as the very last step of CalcOffence (6259-6262) and once more for FullDPS (Calcs.lua:289-290, 347-350); it is therefore a final more-style multiplier on DPS, not a hit-damage modifier and not an input to the hit."
pob:
  measured: partial
  how: "Calculated, no config: CullPercent = max(regular cull mods, critical cull) (CalcOffence.lua:3300-3310), CullMultiplier = 100/(100 - CullPercent), CullingDPS = CombinedDPS x (bestCull - 1) (CalcOffence.lua:6259-6262); FullDPS takes the best multiplier over all skills, minions and mirages and applies it once to the total (Calcs.lua:202-203, 240-241, 289-290, 347-350). Crit-only cull (Critical Strikes have Culling Strike): criticalCull = min(c, c x (1-(1-CritChance)^hitRate)), hitRate = HitChance x (HitSpeed or Speed) x dpsMultiplier per SECOND (CalcOffence.lua:3300-3305), i.e. the chance of at least one crit in one second. Sources: ModParser.lua:5051-5066 and 3014, Data/SkillStatMap.lua:2217-2224, Culling Strike Support stat kill_enemy_on_hit_if_under_10%_life = 10. Cull the Weak (Data/SkillStatMap.lua:2223-2225) is gated 'enemy not RareOrUnique'; the enemy gets Condition:RareOrUnique from the boss presets (ConfigOptions.lua:2121, 2155) or a tick (:2083). NOT modelled: scripted-death exceptions, phase transitions of bosses, the DoT exclusion (the multiplier covers TotalDotDPS, CalcOffence.lua:6256 before :6262), a hit rate low enough that the last 10% takes more than one hit."
  config:
    - {var: enemyIsBoss, default: "Pinnacle (list index 3)", ref: "Modules/ConfigOptions.lua:2086 (sets Condition:RareOrUnique at :2121 and :2155; Cull the Weak does nothing on a boss)", class: b}
    - {var: conditionEnemyRareOrUnique, default: false, ref: "Modules/ConfigOptions.lua:2083", class: b}
  unparsed:
    - "Eternal Struggle 'Kill Enemies that have 15% or lower Life on Hit if The Searing Exarch is dominant' (Data/Uniques/amulet.lua:1390): no CullPercent parse seen except the generic ModParser.lua:3014 line, which reads 'when Hit by your skills'"
    - "Goblinedge and Relentless Fury 'on Culling Strike' payoffs (life, mana, onslaught, charge duration) have no PoB output"
model: null
providers:
  - {kind: support, name: "Culling Strike Support", slot: any, role: applies, target: enemy, text: "enemies left below 10% life by a hit from the supported skill are slain; quality: recover 0-2% of Life when supported skills Cull (since 3.23.0)", source: "Data/Skills/sup_dex.lua:1550-1572; Data/SkillStatMap.lua:2217-2220; wiki Culling Strike Support rev 1681692", pob: full}
  - {kind: support, name: "Cull the Weak Support", slot: any, role: applies, target: enemy, text: "kills NORMAL and MAGIC enemies that are left below 30-47% of maximum life (gem level 1-15); does nothing against rare, unique and boss enemies", source: "Data/Skills/sup_dex.lua:1515-1548; Data/SkillStatMap.lua:2223-2225; wiki Cull the Weak Support rev 1682300", pob: full}
  - {kind: ascendancy, name: "Headsman (Slayer)", slot: tree, role: applies, target: enemy, text: "Kill Enemies that have 20% or lower Life when Hit by your Skills", source: "TreeData/3_29/tree.lua:59561; Modules/ModParser.lua:3014; wiki Headsman rev 1417684", pob: full}
  - {kind: unique, name: "Marylene's Fallacy", slot: Amulet, role: applies, target: enemy, text: "Critical Strikes have Culling Strike (scaled by PoB's crit-in-one-second formula)", source: "Data/Uniques/amulet.lua:865; Modules/ModParser.lua:5058", pob: full}
  - {kind: unique, name: "Heartbreaker", slot: Dagger, role: applies, target: enemy, text: "Your Spells have Culling Strike", source: "Data/Uniques/dagger.lua:178; Modules/ModParser.lua:5060", pob: full}
  - {kind: unique, name: "Hyrri's Truth", slot: Amulet, role: applies, target: enemy, text: "Bow Attacks have Culling Strike (variant 3)", source: "Data/Uniques/amulet.lua:635; Modules/ModParser.lua:5061", pob: full, variant: "variant 3"}
  - {kind: unique, name: "Oro's Sacrifice", slot: Sword, role: applies, target: enemy, text: "Culling Strike against Burning Enemies (the Replica variant 2: against Frozen Enemies)", source: "Data/Uniques/sword.lua:911, 929; Modules/ModParser.lua:5062-5063", pob: partial, payoff_of: [conditionEnemyBurning, conditionEnemyFrozen]}
  - {kind: unique, name: "Gluttony", slot: Belt, role: applies, target: enemy, text: "You have Culling Strike against Cursed Enemies (variant 2; variant 1: against enemies cursed with Poacher's Mark)", source: "Data/Uniques/belt.lua:360-361; Modules/ModParser.lua:5057", pob: partial, payoff_of: [conditionEnemyCursed]}
  - {kind: flask, name: "Vorana's Preparation", slot: Flask, role: applies, target: enemy, text: "Culling Strike during Effect (flask uptime: see flask-uptime)", source: "Data/Uniques/flask.lua:581; Modules/ModParser.lua:5055", pob: partial}
  - {kind: notable, name: "Wish for Death", slot: tree, role: applies, target: enemy, text: "You have Culling Strike against Cursed Enemies", source: "TreeData/3_29/tree.lua:87843; Modules/ModParser.lua:5057", pob: partial, payoff_of: [conditionEnemyCursed]}
  - {kind: notable, name: "Knife in the Back", slot: tree, role: applies, target: enemy, text: "Critical Strikes have Culling Strike", source: "TreeData/3_29/tree.lua:83287; Modules/ModParser.lua:5058", pob: full}
  - {kind: mastery, name: "Mace Mastery", slot: tree, role: applies, target: enemy, text: "Hits that Stun Enemies have Culling Strike (flag Condition:maceMasteryStunCullSpecced; stun uptime separate)", source: "TreeData/3_29/tree.lua:20903; Modules/ModParser.lua:5066", pob: partial}
makes_redundant:
  - {provider: "Culling Strike Support (10%)", when: "Headsman allocated", why: "PoB and the game take the highest threshold, 20% already includes the 10% (multiple thresholds can proc at once; CullPercent is a MAX)", source: "wiki Culling strike rev 1673452; Modules/CalcOffence.lua:3308"}
  - {provider: "Cull the Weak Support", when: "the target is a rare, unique or boss", why: "it cannot kill them; use Culling Strike or Headsman there", source: "wiki Cull the Weak Support rev 1682300; Data/SkillStatMap.lua:2223-2225"}
conflicts:
  - {with: "pure damage over time builds (ignite, bleed, poison, degen)", effect: "damage over time does not hit, so it cannot cull and cannot reach 10% by itself; PoB still multiplies TotalDotDPS by the cull multiplier", source: "wiki Culling strike rev 1673452 (patch 1.0.2 note); Modules/CalcOffence.lua:6256-6262"}
  - {with: "scripted-death enemies", effect: "no cull on Uber Elder in its final phase, Bestiary beasts, Catarina, Master of Undeath", source: "wiki Culling strike rev 1673452"}
  - {with: "overkill-based effects (Herald of Ash)", effect: "culling is not damage and gives no overkill damage", source: "wiki Culling strike rev 1673452"}
conditions:
  - {text: "fires if the target's CURRENT life is 10% or less of maximum after the hit's damage, even for a hit that deals no damage or is fully mitigated; not if the hit itself is avoided (evasion, dodge); ignores energy shield and guard skills; a hit that kills the target cannot cull", source: "https://www.poewiki.net/wiki/Culling_strike rev 1673452 (patch 3.29)"}
  - {text: "multiple thresholds can proc together (e.g. 30% -> 8% procs Headsman and Culling Strike Support's quality effect); the effects of culling (Goblinedge) need the 10% threshold, not the 20% of Headsman", source: "wiki Culling strike rev 1673452"}
  - {text: "Culling Strike Support quality changed in 3.23.0 from +0-10% damage to recover 0-2% life on cull; before that it also changed in 3.15.0", source: "wiki Culling Strike Support rev 1681692"}
uptime:
  Mapping:       {value: always, config: {enemyIsBoss: "None / map monsters"}, reasoning: "map packs mostly die to normal hit damage, so the final 10% is a small share; a plain cull (10%) works on all rarities, Cull the Weak only on normal and magic; conditional culls (burning, frozen, cursed, crit-only) need their condition up at the moment of the last hit", source: "wiki Culling strike rev 1673452; wiki Cull the Weak Support rev 1682300; Modules/CalcOffence.lua:6259-6262"}
  Pinnacle Boss: {value: pob, config: {enemyIsBoss: "Pinnacle (default)"}, reasoning: "use PoB's CullPercent and CullMultiplier; remove the part on DoT damage by hand if the build is mostly DoT; Cull the Weak adds nothing (boss is RareOrUnique); the wiki lists only Uber Elder's last phase as a scripted exception, nothing for other pinnacle bosses", source: "Modules/ConfigOptions.lua:2121, 2155; Data/SkillStatMap.lua:2223-2225; wiki Culling strike rev 1673452"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Culling_strike (rev 1673452)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Culling_Strike_Support (rev 1681692)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Cull_the_Weak_Support (rev 1682300)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Headsman (rev 1417684)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcOffence.lua:3300-3310,6212-6262; Modules/Calcs.lua:202-203,240-241,289-290,347-350; Modules/ModParser.lua:3014,5051-5066; Data/SkillStatMap.lua:2217-2225; Modules/ConfigOptions.lua:2083,2121,2155; Modules/CalcSections.lua:1469", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/pob-coverage-auditor-uptime.md (Q3: criticalCull is PoB's own hit-rate-to-probability use)", kind: discovery, patch: "3.29"}
not_verified:
  - "whether specific pinnacle bosses (Maven, Sirus, Uber Elder earlier phases, Shaper, Exarch, Eater, Uber Atziri and others) can be culled and whether their phase thresholds interact with the 10%: the wiki lists only Uber Elder's final phase, beasts and Catarina; no per-boss source found"
  - "whether PoB's multiplier applied to damage over time is acceptable for mixed hit + DoT builds (the cull skips the last 10% of life whatever dealt it, but only a hit triggers it): wiki says DoT cannot cull, PoB multiplies TotalDotDPS; both readings kept"
  - "whether PoB's crit-cull window of one second (hitRate is per second) is right for a fight; the wiki gives no model"
  - "per-fight reality of 1/0.9 = +11.1%: it assumes a hit lands after the enemy reaches 10% and does not overkill; slow single-hit skills lose part of it"
  - "whether Headsman's wiki text (rev 1417684, last row 3.22.0) matches the 3.29 node; PoB tree 3_29 shows the 20% line"
  - "Eternal Struggle's 15% cull (needs The Searing Exarch dominant): not parsed as a cull in PoB (only the generic line at ModParser.lua:3014)"
open_questions:
  - "Should the generator count the cull multiplier on bosses at all when the build's DPS is mostly damage over time, or strip the DoT share from the multiplier?"
```
