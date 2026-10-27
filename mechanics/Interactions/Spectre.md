---
type: interaction
status: draft
pob_refs: [Minion.TotalDPS, FullDPS, SkillDPS, ActiveSpectreLimit, ActiveMinionLimit, Multiplier:SummonedMinion, Duration, skillMinionSkill, raiseSpectreEnableBuffs, raiseSpectreEnableCurses, conditionSummonedSpectreInPast8Sec, conditionUsedMinionSkillRecently, meatShieldEnemyNearYou]
source: "poewiki Raise Spectre rev 1702628 (fetched 2026-10-26); PoB 2.67.2 Data/Skills/act_int.lua, Data/Spectres.lua, Data/Minions.lua, Modules/CalcPerform.lua, Calcs.lua, ConfigOptions.lua, ModParser.lua, TreeData/3_29/tree.lua, Data/Uniques; evidence skill-gem-analyst, pob-coverage-auditor, item-analyst (task 027 batch 2b); headless runs on 3.27/SRS CI Guardian Giga Build.xml (in memory, never saved)"
last_confirmed_patch: "3.29.x"
---

Raise Spectre raises permanent Spectres from corpses; WHICH spectre you raise is the main choice (its own skill, life and aura). The limit is 1 / 2 / 3 at gem level 1 / 13 / 25 plus other sources, and with several Raise Spectre gems the total is the highest limit of any one gem, not the sum. PoB counts one spectre's TotalDPS per gem times the FIRST Raise Spectre gem's hand-set count, never caps by the limit, and (default on) gives the spectres' aura skills to the player and every minion. Number alive and uptime come from the model [[Minion alive count]]; general minion rules are in [[Minions]].

Pipeline: [[Damage calculation#Increased and reduced]], [[Damage calculation#More and less]] - spectre damage runs through the minion actor's own pools (MinionModifier mods), not the player's; [[Damage calculation#Hit rate]] - the number of spectres enters only after the per-minion hit rate (FullDPS = minion TotalDPS x gem count, Calcs.lua:179-180).

```interaction
id: raise-spectre
mechanic: "Raise Spectre: permanent Spectres of corpses, limit 1/2/3 at gem level 1/13/25 plus other sources (highest limit of any one gem, not the sum); PoB counts one spectre's TotalDPS per gem x the FIRST gem's hand-set count, never caps by the limit, and shares spectre auras with the player and all minions when raiseSpectreEnableBuffs is on"
family: uptime
target: self
related: [minions, animate-guardian, absolution, golem-buffs]
pipeline_step: ["Damage calculation#Increased and reduced", "Damage calculation#More and less", "Damage calculation#Hit rate"]
pipeline_why: "Spectre damage runs through the minion actor's own increased/more pools (CalcPerform.lua:1247-1253), not the player's; the number of spectres enters only after the per-minion hit rate (FullDPS = minion TotalDPS x gem count, Calcs.lua:179-180)"
pob:
  measured: partial
  how: "Per-spectre rate only. One entry per Raise Spectre gem, each with its own spectre id (build.spectreList); FullDPS = that spectre's TotalDPS x the count of the FIRST Raise Spectre gem of the group, so per-gem counts cannot differ (Calcs.lua:122-136,180; FIRST gem count 2 gave +34.2% FullDPS and count 2 on all three rows); limit = max over gems, written to Multiplier:SummonedMinion once (CalcPerform.lua:1443-1457,1494) and shown as ActiveSpectreLimit (Data.lua:1158), but never caps the count (a 5th and 6th gem with limit 4: FullDPS +27.8%, no warning); limit mods are worth 0 in FullDPS (+2 Spectres: limit 4 -> 6, change 0.000%). Measured on the SRS CI Guardian build: limit by effective gem level 5 / 12 -> 2, 13 / 24 -> 3, 25 / 34 / 40 -> 4 (3 from the gem + 1 from Death Attunement, Tree:19897 in the 3.27 tree); cast speed 2.54/s; Duration nil (permanent); ESCost 44, ManaCost 0."
  config:
    - {var: "gem count (count of the FIRST Raise Spectre gem applies to all spectre rows)", default: 1, ref: "Modules/Calcs.lua:122-136", class: c}
    - {var: raiseSpectreEnableBuffs, default: true, ref: "Modules/ConfigOptions.lua:588-590", class: b}
    - {var: raiseSpectreEnableCurses, default: true, ref: "Modules/ConfigOptions.lua:591-594 (the sample file stores false; flipping it changed nothing, no cursing spectre in the scene)", class: b}
    - {var: conditionSummonedSpectreInPast8Sec, default: false, ref: "Modules/ConfigOptions.lua:595-597; read only by the line 'Raised Zombies and Spectres gain Adrenaline for 8 seconds when Raised' (Modules/ModParser.lua:4458-4461)", class: b}
    - {var: conditionUsedMinionSkillRecently, default: false, ref: "Modules/ConfigOptions.lua:1537-1540; auto-set only for non-permanent minion skills (Modules/CalcPerform.lua:253-255), Raise Spectre is permanentMinion (act_int.lua:15020)", class: b}
    - {var: meatShieldEnemyNearYou, default: false, ref: "Modules/ConfigOptions.lua:543-545", class: b}
    - {var: "raiseSpectreBladeVortexBladeCount / raiseSpectreKaomFireBeamTotemStage / raiseSpectreEnableSummonedUrsaRallyingCry / raiseSpectreEnableSlashingHorrorEnrage / raiseSpectreEnableSanguimancerDemonLowLife", default: "0 / 0 / unticked / unticked / unticked", ref: "Modules/ConfigOptions.lua:598-612 (shown only when the spectre carries that skill; code only, not in the test scene)", class: b}
    - {var: skillMinionSkill, default: "PoB's own skill order, index not the skillList order of Data/Spectres.lua", ref: "m3.json E4 (minion-skills.md section 4)", class: c}
  unparsed:
    - "Raise Spectre: stat movement_velocity_cap (-53) and display_minion_monster_type have no Data/SkillStatMap.lua entry"
    - "Wraithlord: 'You cannot have Non-Spectre Minions'"
    - "Bitterbind Point: 'Your Raised Spectres also gain Arcane Surge'"
    - "Soul's Wick: Base Duration of 20 seconds and 'Spectres do not travel between Areas'"
    - "Midnight Bargain: 'Cannot be used with Chaos Inoculation'"
model:
  proposed_kind: minion_alive_count
  inputs: {from_pob: [Minion.TotalDPS, ActiveSpectreLimit, "gem count"], from_scenario: ["death rate lambda (class b)", "resummon delay tau (corpse availability, class b)", "hit fraction h (class b)"]}
  params: {limit_rule: "highest limit of any one gem, not the sum (wiki rev 1702628; CalcPerform.lua:1443-1457)", resummon_delay_tau: "orb until the next area, a new Raise Spectre can replace an orb but needs a corpse (wiki 3.27.0)"}
  formula: "alive = min(hand-set count of the first gem x number of gems, ActiveSpectreLimit) x u; spectres of all gems summed, then capped at ActiveSpectreLimit; set the first gem's count to floor(alive / number of gems) or use the group count (model: [[Minion alive count]], case b)"
  calibration: "no norm found for lambda, tau or h (model note searched 3 times, 2026-10-26)"
providers:
  - {kind: gem, name: "Raise Spectre", slot: any, role: enables, target: self, text: "permanent Spectres; limit 1/2/3 at gem level 1/13/25; spectre level 28 / 56 / 78 at L1 / L13 / L25 (L30 85, L40 95); +55% active minion movement speed final, +30% minion elemental resistance; quality +1% elemental resistance per 1% (Q0 -> 20 on Forged Frostbearer: Lightning res 75 -> 83, DPS and Life unchanged)", source: "Data/Skills/act_int.lua:14998-15077; wiki Raise Spectre rev 1702628; minion-skills.md section 2", pob: partial}
  - {kind: gem, name: "Raise Spectre of Transience", slot: any, role: enables, target: self, text: "temporary variant: 30 s base duration (55.209 s with the build's DurationMod 1.84), limit 4 at L1 as a fixed column (7 in the sample: 6 from the skill + 1 Death Attunement), quality +0.05 spectres per 1%; Multiplier:SummonedMinion 14 -> 17; PoB shows the Duration but nothing expires", source: "Data/Skills/act_int.lua:15078-; minion-skills.md section 2 (m2.json E3)", pob: partial}
  - {kind: notable, name: "Death Attunement", slot: tree, role: enables, target: self, text: "+1 to Maximum number of Spectres, Raised Zombies and Skeletons: ActiveSpectreLimit 4 -> 5 measured, Spectre-row DPS 0.00% (the limit never scales DPS in PoB; real gain is one more spectre once the gem count is raised)", source: "TreeData/3_29/tree.lua:38554 (node 19897 in 3.27); tree.md section 2", pob: full}
  - {kind: unique, name: "The Dark Monarch", slot: Helmet, role: enables, target: self, text: "variant 4: Maximum number of Raised Spectres is Doubled (ActiveSpectreLimit MORE 100); +1 to Level of all Minion Skill Gems; cannot have other minions; boss drop (Incarnation of Dread)", variant: "variant 4", source: "Data/Uniques/helmet.lua:826-881 (lines 847, 856); items.md section 1a", pob: partial}
  - {kind: unique, name: "Wraithlord", slot: Helmet, role: enables, target: self, text: "+1 to maximum number of Raised Spectres per socketed Ghastly Eye Jewel (4 abyssal sockets, up to +4); +(1-2) to Level of all Minion Skill Gems; You cannot have Non-Spectre Minions (not enforced by PoB); boss drop (Nightmare of Catarina)", variant: "variant 3 (Current)", source: "Data/Uniques/helmet.lua:790,793,796,798; items.md section 2b", pob: partial}
  - {kind: unique, name: "Bones of Ullr", slot: Boots, role: scales, target: self, text: "+1 to Level of all Raise Spectre Gems (also Raise Zombie): moves the limit tier (13 / 25) and the spectre level; random drop", source: "Data/Uniques/boots.lua:457-458; items.md section 2b", pob: full}
  - {kind: gem, name: "Raise Spectre: Forged Frostbearer", slot: any, role: enables, target: self, text: "Metadata/Monsters/LeagueCrucible/Cold/Pyromaniac (Data/Spectres.lua:3904); bare Raise Spectre L21 Q20 (spectre level 78): best skill Ice Mortar, Minion.TotalDPS 285,750, Life 38,252; named in the wiki's popular DPS spectres", variant: "spectre choice", source: "Data/Spectres.lua:3904; minion-skills.md section 4 (m3.json E4); wiki Raise Spectre rev 1702628", pob: partial}
  - {kind: gem, name: "Raise Spectre: Wretched Defiler", slot: any, role: enables, target: self, text: "Metadata/Monsters/Revenant/RevenantMapBossStandalone_AtlasUber (Data/Spectres.lua:3931); best skill Lightning Projectile, TotalDPS 271,938, Life 88,800; wiki popular DPS (endgame)", variant: "spectre choice", source: "Data/Spectres.lua:3931; minion-skills.md section 4; wiki Raise Spectre rev 1702628", pob: partial}
  - {kind: gem, name: "Raise Spectre: Perfect Hydra", slot: any, role: enables, target: self, text: "Metadata/Monsters/LeagueAzmeri/SpecialCorpses/Hydra/HydraHigh_ (Data/Spectres.lua:4308); best skill Barrage, TotalDPS 155,038, Life 19,581 (0.33 casts/s, PoB ignores that behaviour); its Hatred aura (+20% physical as extra cold, 16% more cold) goes to the player and to every other minion: Turtle 92,430 -> 80,897, Guardian 185,862 -> 182,281, Warrior 103,098 -> 94,184 in the sample, and raiseSpectreEnableBuffs off is +4.67% FullDPS", variant: "spectre choice", source: "Data/Spectres.lua:4308; coverage-minion-skills.md sections 2 and 6 (e8.json, e10.json); wiki Raise Spectre rev 1702628", pob: config}
  - {kind: gem, name: "Raise Spectre: Perfect Forest Warrior", slot: any, role: enables, target: self, text: "Metadata/Monsters/LeagueAzmeri/SpecialCorpses/VikingHigh (Data/Spectres.lua:6662); bare best skill Cyclone TotalDPS 213,533, Life 68,308; in the sample group (Meat Shield + Minion Life) Default Attack 103,097.80, Life 116,970; wiki: Onslaught + culling; in user builds (2 <Spectre id=> entries)", variant: "spectre choice", source: "Data/Spectres.lua:6662; minion-skills.md sections 2 and 4", pob: partial}
  - {kind: gem, name: "Raise Spectre: Perfect Guardian Turtle", slot: any, role: enables, target: self, text: "Metadata/Monsters/LeagueAzmeri/SpecialCorpses/TurtleHigh (Data/Spectres.lua:6506); bare Default Attack 92,430, Life 102,462 (sample group Life 175,454); Determination aura is the point (utility); in user builds (2 entries)", variant: "spectre choice", source: "Data/Spectres.lua:6506; minion-skills.md sections 2 and 4", pob: partial}
  - {kind: gem, name: "Raise Spectre: Perfect Judgemental Spirit", slot: any, role: enables, target: self, text: "Metadata/Monsters/LeagueAzmeri/SpecialCorpses/GoddessHigh (Data/Spectres.lua:5590); bare best skill Mortar TotalDPS 153,169, Life 46,220 (sample group Life 79,146); Discipline aura; in the SRS CI Giga Build (user-build counts: see not_verified)", variant: "spectre choice", source: "Data/Spectres.lua:5590; minion-skills.md sections 2 and 4", pob: partial}
makes_redundant:
  - {provider: "Spectre limit from gem level (3 at L25)", when: "Death Attunement, Wraithlord or Queen's Decree (Data/Uniques/sword.lua:943-952) already gives the wanted count", why: "the limit is a sum of sources; levels past 25 add no spectre, only spectre level (L30 85, L40 95)", source: "Data/Skills/act_int.lua:15060; TreeData/3_29/tree.lua:38554"}
  - {provider: "A second or third Raise Spectre gem for the limit", when: "always", why: "the total allowed is the highest limit of any one gem, not the sum; extra gems add rows (more spectre types) but not slots", source: "wiki Raise Spectre rev 1702628; Modules/CalcPerform.lua:1443-1457"}
  - {provider: "Separate per-gem counts", when: "more than one Raise Spectre gem in a group", why: "the first Raise Spectre gem's count applies to all spectre rows, so a different count per gem cannot be set", source: "Modules/Calcs.lua:122-136; coverage-minion-skills.md section 2"}
conflicts:
  - {with: "The Dark Monarch", effect: "cannot have minions other than the doubled type: not parsed, PoB keeps other minions counted", source: "Data/Uniques/helmet.lua:854-865; items.md section 1b"}
  - {with: "Wraithlord", effect: "You cannot have Non-Spectre Minions (Animate Guardian, Absolution, Summon Raging Spirit): not parsed, not enforced", source: "Data/Uniques/helmet.lua:798; items.md section 2b"}
  - {with: "Chains of Command", effect: "You cannot have Non-Animated, Non-Manifested Minions: no Spectres; not enforced by PoB", source: "Data/Uniques/body.lua:968"}
  - {with: "Midnight Bargain", effect: "Cannot be used with Chaos Inoculation: not parsed, PoB accepts it on a CI build (the SRS CI sample)", source: "Data/Uniques/wand.lua:154-164; items.md section 2b"}
conditions:
  - {text: "Limits are output-only: counts over the limit are not capped (5 spectres with limit 4: FullDPS +27.8%); the generator must cap count at ActiveSpectreLimit itself", source: "Modules/CalcPerform.lua:1436-1457,1494; coverage-minion-skills.md section 2 (e6.json five_spectres_limit4)"}
  - {text: "Spectre level is the effective gem level's row of the gem table; changing one of three gems does not change the limit (max rule); all three gems changed together do", source: "Data/Skills/act_int.lua:15047; minion-skills.md section 2 (m2.json E1)"}
  - {text: "raiseSpectreEnableBuffs is on by default: spectre aura skills (Hydra Hatred, Judgemental Spirit Discipline, Turtle Determination) are applied to the player and all other minions, so a spectre choice changes the other rows; judge it with whole-build FullDPS, never the isolated minion DPS", source: "Modules/ConfigOptions.lua:588-590; coverage-minion-skills.md sections 2 and 6"}
  - {text: "conditionUsedMinionSkillRecently is auto-set only for non-permanent minions (Modules/CalcPerform.lua:253-255): with Raise Spectre as the evaluated skill it stays off; ticked it gives Turtle +16.2%, Warrior +14.2%, Spirit +14.2% in the sample, and the real character has it true if it casts any non-permanent minion skill", source: "Modules/CalcPerform.lua:253-255; coverage-minion-skills.md sections 2 and 4"}
  - {text: "conditionSummonedSpectreInPast8Sec does nothing without a mod that reads it; with the Adrenaline-on-raise line as a custom mod it is +14.11% FullDPS (Raise Spectre rows +14.0 to +23.4%)", source: "Modules/ConfigOptions.lua:595-597; Modules/ModParser.lua:4458-4461; coverage-minion-skills.md section 2 (e10.json)"}
  - {text: "When Spectres die they become Orb Spectres (cannot use skills, cannot be targeted) until the next area; a new Raise Spectre can replace an orb but needs a corpse", source: "wiki Raise Spectre rev 1702628 (3.27.0)"}
  - {text: "Per-skill DPS of a spectre ignores AI, uptime and cooldown behaviour; the measured top bare DPS is Slave Driver (TemplarSlaveDriver) Lightning Surge 432,311, above the six listed choices (list in h-overflow.md; popularity could not be ranked, poe.ninja does not expose the spectre)", source: "minion-skills.md section 4 (m3.json E4)"}
uptime:
  Mapping:       {value: model, config: {"gem count": "first gem count = floor(min(wanted, ActiveSpectreLimit) / gems)", raiseSpectreEnableBuffs: "keep on only if the chosen spectre's aura is wanted"}, reasoning: "permanent; spectres return from orbs at the next area; corpse availability for re-raising unknown; PoB assumes all counted spectres attack at once", source: "wiki Raise Spectre rev 1702628 (3.27.0); Minion alive count model case b"}
  Pinnacle Boss: {value: model, config: {enemyIsBoss: Pinnacle, "gem count": "as above x survival share u"}, reasoning: "one area per fight, so a dead Spectre stays an orb for the whole fight; Pinnacle -> None changes the Turtle row +34.2%, Warrior +40.2%, Spirit +39.6% (defences, no uptime); no survival norm found", source: "wiki Raise Spectre rev 1702628 (3.27.0); coverage-minion-skills.md section 4 (enemyIsBoss row)"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Raise_Spectre (rev 1702628, fetched 2026-10-26)", kind: wiki, patch: "3.29"}
  - {ref: "Data/Skills/act_int.lua:14998-15077; Data/Spectres.lua:3904,3931,4308,5590,6506,6662; Data/Data.lua:1158; Modules/CalcPerform.lua:253-255,1436-1457,1494; Modules/Calcs.lua:116-137,179-180; Modules/ConfigOptions.lua:543-545,588-612,1537-1540; Modules/ModParser.lua:626-627,4458-4461 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "TreeData/3_29/tree.lua:38554; Data/Uniques/{helmet,boots,wand,body}.lua lines in the providers", kind: pob, patch: "3.29"}
  - {ref: "poe.ninja Allflame search 2301-20261025-55679: no spectre dimension exposed (one character inspected)", kind: discovery, patch: "3.29"}
not_verified:
  - "popularity ranking of spectres: poe.ninja exposes no spectre dimension (one character inspected); the six choices come from the wiki's editorial popular-DPS list and the user builds"
  - "user-build usage counts: the table in minion-skills.md section 4 says Forest Warrior in 3 user builds and Turtle in 2, the entry count says VikingHigh 2, TurtleHigh 2, GoddessHigh 1; the two do not agree"
  - "why Perfect Hydra's Hatred lowers the Turtle / Warrior / Guardian rows (-12.5% / -8.6% / -1.9%) in PoB; in game Hatred is a pure gain, so treat the sign as build-specific and measure the whole build"
  - "whether the real game counts casting Raise Spectre as 'used a Minion Skill recently'"
  - "spectre corpse acquisition, resummon downtime and the Orb Spectre return are not modelled by PoB and have no norm"
  - "Raise Zombie resummon facts (wiki page not fetched, Cloudflare)"
  - "the Dark Monarch doubling size and Wraithlord limit values were read from parse output; the +2 Spectres probe (limit 4 -> 6) measured 0.000% change"
  - "3.29 availability of boss-drop and league-origin items"
open_questions:
  - "Which spectre-choice ranking should the generator use before the user calibrates (wiki list, PoB bare DPS, or the user's own builds)?"
  - "Should the generator tick conditionUsedMinionSkillRecently whenever the build casts a non-permanent minion skill (Absolution, Summon Raging Spirit), since FullDPS evaluates Raise Spectre with the condition off?"
  - "Which h / lambda / tau should the generator assume for Spectres until the user calibrates?"
```
