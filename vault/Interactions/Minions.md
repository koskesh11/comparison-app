---
type: interaction
status: draft
pob_refs: [Minion.TotalDPS, FullDPS, SkillDPS, ActiveMinionLimit, ActiveSpectreLimit, ActiveRagingSpiritLimit, ActiveSentinelOfAbsolutionLimit, ActiveGolemLimit, SummonedMinionsPerCast, Duration, DurationMod, Speed, feedingFrenzyFeedingFrenzyActive, multiplierSummonedMinion, conditionMinionsDiedRecently]
source: "poewiki Minion rev 1703018, Raise Spectre rev 1702628, Summon Raging Spirit rev 1681790, Animate Guardian rev 1681757, Absolution rev 1682183 (fetched 2026-10-26); PoB 2.67.2 Modules/CalcPerform.lua, CalcOffence.lua, Calcs.lua, CalcDefence.lua, ModParser.lua, ConfigOptions.lua, Data/Skills, Data/Minions.lua, Data/SkillStatMap.lua, Data/Uniques, TreeData/3_29/tree.lua; evidence skill-gem-analyst-minions.md (task 027 batch 2); headless run on the user's SRS CI Guardian Giga Build (not saved)"
last_confirmed_patch: "3.29.x"
---

A minion is a separate actor with its own modifier database: only "Minions have/deal ..." mods, support-gem stats, auras and a few copies of player values (accuracy, strength, a share of resistances) reach it, so player damage, crit, speed and defence mods do nothing for it. PoB shows TotalDPS for ONE minion and multiplies it only by the hand-set gem count in FullDPS; the minion limit, duration, summon rate, deaths, AI and targeting are computed or ignored but never reduce DPS. Measured on the SRS CI Guardian build: gem count 6 to 5 costs 16.67% of FullDPS, the Pinnacle boss setting costs 28.9% of minion DPS (defences only), and the summon rate times duration (24.86 alive) exceeds the limit 6, so the limit binds.

Pipeline: [[Damage calculation#Increased and reduced]], [[Damage calculation#More and less]] - minion damage runs through the minion actor's own pools (MinionModifier mods); [[Damage calculation#Hit rate]] - the number of minions enters only after the per-minion hit rate (FullDPS = minion TotalDPS x gem count, Calcs.lua:179-180).

```interaction
id: minions
mechanic: "Minions are separate actors with their own modDB: only 'Minions have/deal ...' (MinionModifier) mods, support-gem stats, auras and a few copies of player values reach them; damage of one minion is TotalDPS, the number alive is a hand-set gem count in FullDPS"
family: uptime
target: self
related: [golem-buffs, totems, channelling, fight-length, chance-on-hit-uptime, culling-strike]
pipeline_step: ["Damage calculation#Increased and reduced", "Damage calculation#More and less", "Damage calculation#Hit rate"]
pipeline_why: "Minion damage runs through the minion actor's own increased/more pools (MinionModifier mods, CalcPerform.lua:1247-1253), not the player's; the number of minions enters only after the per-minion hit rate (FullDPS = minion TotalDPS x gem count, Calcs.lua:179-180)"
pob:
  measured: partial
  how: "Per-minion rate only. Minion actor gets a fresh ModDB (CalcPerform.lua:1297-1300) filled from minion data (1153-1243) and MinionModifier mods (1247-1253); TotalDPS is one minion (CalcOffence.lua:3801); FullDPS multiplies by the hand-set gem count (Calcs.lua:116-137,179-180); limits are computed (CalcOffence.lua:1057-1059) but do not scale DPS; summonSpeed (CalcOffence.lua:4097) is computed and unused; no duration, death, respawn, AI or targeting model (grep aggro/minionAI/ai_ over the Calc*.lua and ConfigOptions.lua: 0 lines)"
  config:
    - {var: feedingFrenzyFeedingFrenzyActive, default: false, ref: "Modules/ConfigOptions.lua:447", class: b}
    - {var: multiplierSummonedMinion, default: "maximum", ref: "Modules/ConfigOptions.lua:1139 (only 'per minion' mods; measured no DPS effect)", class: b}
    - {var: conditionMinionsDiedRecently, default: false, ref: "Modules/ConfigOptions.lua:1320", class: b}
    - {var: conditionUsedMinionSkillRecently, default: false, ref: "Modules/ConfigOptions.lua:1537", class: b}
    - {var: minionsConditionFullLife, default: false, ref: "Modules/ConfigOptions.lua:198", class: b}
    - {var: raiseSpectreEnableBuffs, default: true, ref: "Modules/ConfigOptions.lua:588", class: b}
    - {var: "gem count (socket group gem count)", default: 1, ref: "Modules/Calcs.lua:116-137", class: c}
  unparsed: []
model:
  proposed_kind: minion_count_alive
  inputs:
    from_pob: [Minion.TotalDPS, ActiveMinionLimit, SummonedMinionsPerCast, Speed, Duration, summonSpeed]
    from_scenario: ["hit fraction against the target (class b)", "minion death rate per fight (class b)", "resummon policy (class b)"]
  params: {}
  formula: "alive = min(ActiveMinionLimit, summonSpeed x Duration) for duration minions (SRS, Sentinels, Relics), ActiveMinionLimit or 1 for permanent minions; real DPS = Minion.TotalDPS x alive x u, u = share of the fight the minions are alive and attacking; set the SRS-type gem count to floor(alive), not by hand. Round down."
  calibration: "no norm found for u (searched once; discovery only: forum SRS calculator assumes 0.5 s idle then full-lifetime attacks)"
providers:
  - {kind: gem, name: "Animate Guardian", slot: any, role: enables, target: self, text: "permanent Animated Guardian minion wearing your animated items; L20 38% more minion life and damage; if it dies it cannot be re-summoned in that area", source: "Data/Skills/act_str.lua:464-528; wiki Animate Guardian rev 1681757", pob: full}
  - {kind: gem, name: "Raise Spectre", slot: any, role: enables, target: self, text: "permanent Spectres of corpses; limit 1/2/3 at gem level 1/13/25; minion level 70 at L20; dead Spectres return as orbs on area change", source: "Data/Skills/act_int.lua:14998-15060; wiki Raise Spectre rev 1702628", pob: partial}
  - {kind: gem, name: "Absolution", slot: any, role: enables, target: self, text: "player blast (spell stats) plus up to 3 Sentinels of Absolution for 15 s from corpses; 25% to summon on rare/unique hit", source: "Data/Skills/act_str.lua:8-81; Data/Minions.lua:864", pob: partial}
  - {kind: gem, name: "Summon Raging Spirit", slot: any, role: enables, target: self, text: "up to 20 spirits for 5 s base; quality adds a chance for an extra spirit (not parsed by PoB)", source: "Data/Skills/act_int.lua:19349-19398; Data/SkillStatMap.lua (no entry for the quality stat)", pob: partial}
  - {kind: support, name: "Minion Damage Support", slot: any, role: scales, target: self, text: "L20 39% more minion damage, 25% less minion life", source: "Data/Skills/sup_int.lua:4801-4845; Data/SkillStatMap.lua:2048", pob: full}
  - {kind: support, name: "Minion Life Support", slot: any, role: scales, target: self, text: "L20 49% more minion life", source: "Data/Skills/sup_int.lua:4917-4958", pob: full}
  - {kind: support, name: "Feeding Frenzy Support", slot: any, role: scales, target: self, text: "L20 44% more minion damage while the Puppet Master buff is up (5.9 s); aggressive aggro range", source: "Data/Skills/sup_int.lua:2473-2515; Modules/ConfigOptions.lua:447", pob: config}
  - {kind: ascendancy, name: "Mindless Aggression (Necromancer)", slot: tree, role: scales, target: self, text: "Minions have 20% more Maximum Life; Minions deal 10% more Damage", source: "TreeData/3_29/tree.lua:57569", pob: full}
  - {kind: ascendancy, name: "Unnatural Strength (Necromancer)", slot: tree, role: scales, target: self, text: "Minions have Unholy Might", source: "TreeData/3_29/tree.lua:57590; Modules/ModParser.lua:4511", pob: full}
  - {kind: notable, name: "Death Attunement", slot: tree, role: scales, target: self, text: "+1 maximum Spectres, Raised Zombies and Skeletons", source: "TreeData/3_29/tree.lua:38554", pob: full}
  - {kind: unique, name: "Tavukai", slot: Amulet, role: scales, target: self, text: "Summon Raging Spirit +(20-30)% duration; Summoned Raging Spirits deal (25-40)% increased damage and have (25-40)% increased maximum life, and take 20% of max life per second as chaos damage", variant: "variant 2 (Current)", source: "Data/Uniques/amulet.lua:1134-1140", pob: full}
  - {kind: unique, name: "The Dark Monarch", slot: Helmet, role: scales, target: self, text: "Maximum number of Summoned Raging Spirits (or Raised Spectres, or Sentinels of Absolution) is Doubled; cannot have other minions", variant: "variants 3, 4, 8", source: "Data/Uniques/helmet.lua:854-865", pob: full}
  - {kind: foulborn, name: "Alpha's Howl (Foulborn)", slot: Helmet, role: scales, target: self, text: "+2 to Level of Socketed Minion Gems", variant: "replaces '+2 to Level of Socketed Aura Gems'", source: "Data/ModFoulborn.lua:8; Data/ModFoulbornMap.jsonc:340; Data/Uniques/helmet.lua:201-203", pob: full}
makes_redundant:
  - {provider: "Spectre limit from gem level (Raise Spectre 3 at L25)", when: "Death Attunement or Wraithlord already gives the wanted count", why: "the limit is a sum of sources; extra levels past 25 add no spectre, only monster level", source: "Data/Skills/act_int.lua:15060; TreeData/3_29/tree.lua:38554"}
conflicts:
  - {with: "Chains of Command", effect: "You cannot have Non-Animated, Non-Manifested Minions: no SRS, Spectres or Absolution sentinels", source: "Data/Uniques/body.lua:964-966"}
  - {with: "The Dark Monarch", effect: "cannot have minions other than the doubled type", source: "Data/Uniques/helmet.lua:854-865"}
  - {with: "Minion Damage Support", effect: "25% less minion life accompanies the damage", source: "Data/SkillStatMap.lua:2048"}
  - {with: "Necromantic Aegis", effect: "all bonuses of the equipped shield go to the minions instead of the player", source: "TreeData/3_29/tree.lua:47831"}
conditions:
  - {text: "Feeding Frenzy damage needs the Puppet Master buff (granted on minion hit); PoB only has the config tick", source: "Data/Skills/sup_int.lua:2473; Modules/ConfigOptions.lua:447"}
  - {text: "Animate Guardian cannot be summoned again in that area after it dies; Spectres become orbs until the next area", source: "wiki Animate Guardian rev 1681757 (3.26.0); wiki Raise Spectre rev 1702628 (3.27.0)"}
  - {text: "support gem stats are copied to ALL minions of the supported skill, not to the minion's own skills one by one", source: "wiki Minion rev 1703018 'Support gems'"}
uptime:
  Mapping:       {value: model, config: {gem count: "set to floor(alive) from min(ActiveMinionLimit, summonSpeed x Duration)", multiplierSummonedMinion: "only per-minion mods"}, reasoning: "packs absorb spirits and sentinels (sentinels need corpses from the pack), minions return at area change; PoB assumes all counted minions attack at once", source: "Modules/Calcs.lua:179-180; wiki Minion rev 1703018"}
  Pinnacle Boss: {value: model, config: {enemyIsBoss: Pinnacle, gem count: "as above x survival share"}, reasoning: "one area per fight (a dead Guardian or Spectre stays dead), spirits idle/travel and spread poorly on a single target, no norm found; PoB Pinnacle config already costs 28.9% of minion DPS in the sample build (defences) but no uptime", source: "headless run2; wiki Animate Guardian 3.26.0; wiki Raise Spectre 3.27.0"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Minion (rev 1703018, fetched 2026-10-26); Raise_Spectre rev 1702628; Summon_Raging_Spirit rev 1681790; Animate_Guardian rev 1681757; Absolution rev 1682183", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcPerform.lua:1153-1253,1297-1352,1436-1505,1946-1964; Modules/CalcOffence.lua:1057-1061,1505,3801,4097; Modules/Calcs.lua:116-137,179-205; Modules/CalcDefence.lua:666-669; Modules/ModParser.lua:626-639,1066-1175,6955-6967; Modules/ConfigOptions.lua:198-208,447,1139,1320,1537 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "Data/Skills/act_str.lua:8-528; Data/Skills/act_int.lua:14998-15060,19349-19398; Data/Skills/sup_int.lua:2473,4658,4801,4868,4917,5027,5088; Data/Minions.lua:202,605,864; Data/SkillStatMap.lua:1989,2006,2021,2046-2049,2072-2080; TreeData/3_29/tree.lua:14832,14852,14895,21753,38554,47831,57290,57569,57590", kind: pob, patch: "3.29"}
  - {ref: "Data/Uniques/{amulet,helmet,body,boots,jewel}.lua; Data/ModFoulborn.lua:8,15,159,197,343; Data/ModFoulbornMap.jsonc:191,340,342,360,809", kind: pob, patch: "3.29"}
  - {ref: "https://poe.ninja/poe1/api/builds/2301-20261025-55679/search?overview=allflame&type=exp (decoded locally; main-skill counts)", kind: discovery, patch: "3.29"}
  - {ref: "https://www.pathofexile.com/forum/view-thread/884148 ; https://poe-vault.com/guides/summon-raging-spirit-guardian (search result text only)", kind: discovery, patch: "3.23-3.29"}
not_verified:
  - "league-start popularity: the snapshot is the whole league; the week-13 / week-1 timemachine variants could not be mapped"
  - "whether PoB 2.67.2 minion attackTime already reflects the 3.29.0 'Non-Spectre Minions no longer pause while attacking' change"
  - "why removing Awakened Minion Damage raised the SRS minion Life by only 19.16% (constantStat says 25% less); Awakened gems carry legacy = true at sup_int.lua:4878 and their 3.29 obtainability was not checked"
  - "how 'Increases and Reductions to Minion Damage also affect you' (Spiritual Aid) is implemented in PoB"
  - "Absolution sentinel count and uptime inputs (corpse availability) are not modelled and not measured; no headless run with Absolution or Holy Relic as the damage skill"
  - "item-analyst not consulted: unique variants, current-league availability and Foulborn drop rules are unchecked; only text lines were read"
  - "sentinel / golem / relic life-pool redirects (CalcPerform.lua:1255-1274, e.g. spectreLifePool 'takenFromSpectresBeforeYou') were read but not measured"
  - "mana cost per second of the summon skill (SRS ManaCost output 0 in the CI sample build) and minion reservations were not evaluated"
open_questions:
  - "Should the generator set the hand-set gem count of SRS-type skills from floor(min(limit, summonSpeed x Duration)) instead of copying the template's count?"
  - "Which uptime u should the generator assume for permanent minions (Animate Guardian, Spectres) in a Pinnacle fight where a death is permanent for the fight?"
```
