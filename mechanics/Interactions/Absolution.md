---
type: interaction
status: draft
pob_refs: [Minion.TotalDPS, FullDPS, SkillDPS, ActiveSentinelOfAbsolutionLimit, ActiveMinionLimit, Multiplier:SummonedMinion, Duration, DurationSecondary, skillMinionSkill, absolutionSkillDamageCountedOnce, conditionUsedMinionSkillRecently, minionsUsePowerCharges, minionsUseFrenzyCharges]
source: "poewiki Absolution rev 1682183 (fetched 2026-10-26); PoB 2.67.2 Data/Skills/act_str.lua, Data/Minions.lua, Data/SkillStatMap.lua, Modules/CalcPerform.lua, Calcs.lua, ConfigOptions.lua, ModParser.lua, TreeData/3_29/tree.lua, Data/Uniques; evidence skill-gem-analyst, pob-coverage-auditor, item-analyst, tree-ascendancy-analyst (task 027 batch 2b); headless runs with an in-memory Absolution group (L20 Q0) added to 3.27/SRS CI Guardian Giga Build.xml (never saved; no user build has an Absolution gem)"
last_confirmed_patch: "3.29.x"
---

Absolution is a player blast (spell stats, 50% physical converted to lightning) that also summons up to 3 Sentinels of Absolution for 15 s from the corpse of a debuffed non-unique enemy, or with 25% chance when it hits a rare or unique. PoB's default sentinel skill is the Melee attack (skill 1), which the wiki says cannot normally be used; skill 2, the real spell, is 1.96 times higher. PoB counts one sentinel times the hand-set count and multiplies the blast by the same count unless absolutionSkillDamageCountedOnce is ticked. Number alive and uptime come from the model [[Minion alive count]]; general minion rules are in [[Minions]].

Pipeline: [[Damage calculation#Increased and reduced]], [[Damage calculation#More and less]] - sentinel damage runs through the minion actor's own pools (MinionModifier mods), the blast through the player's; [[Damage calculation#Hit rate]] - the number of sentinels enters only after the per-minion hit rate (FullDPS = minion TotalDPS x gem count, Calcs.lua:179-180).

```interaction
id: absolution
mechanic: "Absolution: player blast plus up to 3 temporary Sentinels of Absolution (15 s base) from corpses; PoB measures sentinel skill 1 (Melee, unusable per wiki) by default while the real spell is skill 2 (x1.96), counts one sentinel x the hand-set count, and multiplies the blast by that count too unless the 'count skill damage once' box is ticked"
family: uptime
target: self
related: [minions, animate-guardian, raise-spectre, culling-strike]
pipeline_step: ["Damage calculation#Increased and reduced", "Damage calculation#More and less", "Damage calculation#Hit rate"]
pipeline_why: "Sentinel damage runs through the minion actor's own increased/more pools (CalcPerform.lua:1247-1253), the blast through the player's spell pools; the number of sentinels enters only after the per-minion hit rate (FullDPS = minion TotalDPS x gem count, Calcs.lua:179-180)"
pob:
  measured: partial
  how: "Per-sentinel rate only. Limit = base_max_number_of_absolution_sentinels 3 (act_str.lua:42) -> ActiveSentinelOfAbsolutionLimit (SkillStatMap.lua:2021-2023); both minion types of the gem use the same key (max, not sum); limit is output-only and never caps the count (doubled limit 3 -> 6: FullDPS 0.000%); FullDPS = sentinel TotalDPS x gem count (Calcs.lua:179-180), no uptime, no refresh, no corpse model; the blast row is x count too (Calcs.lua:255), and the box absolutionSkillDamageCountedOnce sets the count to 1 only AFTER the minion row was added (Calcs.lua:204-210), so it fixes the blast and the sentinel row stays x count. Measured at effective gem level 24 (L20 Q0, DurationMod 1.84): blast TotalDPS 35,456.33; Duration 5.544 s (debuff), DurationSecondary 27.621 s (sentinel); Speed 3.32 casts/s; ESCost 29, ManaCost 0; sentinel level 78, Life 18,114; skill 1 'Default Attack' 212,521.66 at 3.64/s, skill 2 'Absolution' 416,990.83 at 5.616/s (x1.96), skill 3 'Empowered Absolution' 12,814.82 at 0.1665/s (6 s cooldown; PoB never adds skills 2 and 3 together)."
  config:
    - {var: skillMinionSkill, default: "1 (Melee / Default Attack)", ref: "PoB minion-skill index on the gem; skill 2 = the real spell (m3.json E5)", class: c}
    - {var: absolutionSkillDamageCountedOnce, default: false, ref: "Modules/ConfigOptions.lua:759-761; read side Modules/Calcs.lua:204-210", class: b}
    - {var: "gem count (socket group gem count)", default: 1, ref: "Modules/Calcs.lua:116-137 (hand-set; 3 equals the limit but is not derived from it)", class: c}
    - {var: conditionUsedMinionSkillRecently, default: "auto true when Absolution is the evaluated skill", ref: "Modules/CalcPerform.lua:253-255 (Absolution is not permanentMinion, act_str.lua:28-33); config Modules/ConfigOptions.lua:1537-1540", class: b}
    - {var: "minionsUsePowerCharges / minionsUseFrenzyCharges / minionsUseEnduranceCharges", default: false, ref: "Modules/ConfigOptions.lua:976-984 (sentinel +18.4% / +16.4% / 0 in the sample, blast 0)", class: b}
    - {var: "minionbuffUnholyMight / minionbuffChaoticMight / minionBuffOnslaught", default: false, ref: "Modules/ConfigOptions.lua:1016-1036 (sentinel +6.9% / +12.1% / 0)", class: b}
  unparsed:
    - "Absolution: absolution_blast_chance_to_summon_on_hitting_rare_or_unique_% (25), base_max_number_of_vaal_absolution_sentinels, absolution_blast_shockwave_every_x_beams, spell_maximum_action_distance_+%, display_minion_monster_type have no Data/SkillStatMap.lua entry"
    - "The Dark Monarch: 'Cannot have Minions other than Sentinels of Absolution'"
    - "Wraithlord and Chains of Command: 'cannot have' minion lines"
model:
  proposed_kind: minion_alive_count
  inputs: {from_pob: [Minion.TotalDPS, ActiveSentinelOfAbsolutionLimit, DurationSecondary, "gem count"], from_scenario: ["corpse availability per pack (class b)", "hit chance on the boss (class b)", "hit fraction h (class b)"]}
  params: {limit: ActiveSentinelOfAbsolutionLimit, duration_field: DurationSecondary, absolution_per_kill_in_maps: 1, absolution_per_cast_vs_boss: "0.25 x HitChance (act_str.lua:44; not parsed by PoB)"}
  formula: "alive = min(limit, sentinels summoned per second x DurationSecondary); in maps kills keep sentinels at the limit, on a single boss only the 25% hit chance summons; set the gem count to floor(alive), tick absolutionSkillDamageCountedOnce when count > 1, set skillMinionSkill = 2 (model: [[Minion alive count]], case a)"
  calibration: "no norm found for corpse supply, h or lambda (model note searched 3 times, 2026-10-26)"
providers:
  - {kind: gem, name: "Absolution", slot: any, role: enables, target: self, text: "blast (50% physical to lightning, area 25 + level bonus) plus up to 3 Sentinels for 15 s, debuff 3 s (3.28.0), cast time 0.65 s (3.29.0); sentinel level 12 / 70 / 72 / 90 / 100 at L1 / L20 / L21 / L30 / L40; by effective level: L1 (eff 5) blast 9,538, sentinel skill-1 DPS 72,110; L20 (eff 24) 35,456 / 212,522; L21 (eff 25) 38,495 / 230,461; L30 (eff 34) 71,182 / 430,269; limit 3 at all levels; quality +2% minion cooldown recovery per 1% (Empowered skill 12,815 -> 17,941 DPS at Q20, none on skill 1)", source: "Data/Skills/act_str.lua:8-102; Data/Minions.lua:864-889; wiki Absolution rev 1682183; minion-skills.md section 3", pob: partial}
  - {kind: gem, name: "Absolution of Inspiring", slot: any, role: enables, target: self, text: "variant gem with limit 2 instead of 3 (constant base_max_number_of_absolution_sentinels 2); not measured", source: "Data/Skills/act_str.lua:104-; minion-skills.md section 3", pob: partial}
  - {kind: unique, name: "The Dark Monarch", slot: Helmet, role: enables, target: self, text: "variant 8: Maximum number of Sentinels of Absolution is Doubled (ActiveSentinelOfAbsolutionLimit MORE 100, limit 3 -> 6, FullDPS 0.000% in PoB); +1 to Level of all Minion Skill Gems; cannot have other minions; boss drop", variant: "variant 8", source: "Data/Uniques/helmet.lua:826-881 (lines 847, 864-865); Modules/ModParser.lua:637; coverage-minion-skills.md section 3", pob: partial}
  - {kind: foulborn, name: "Alpha's Howl (Foulborn)", slot: Helmet, role: scales, target: self, text: "+2 to Level of Socketed Minion Gems: lifts blast damage and sentinel level, local, only with Absolution socketed in the helmet", variant: "replaces '+2 to Level of Socketed Aura Gems'", source: "Data/ModFoulborn.lua:8; Data/ModFoulbornMap.jsonc:340; Data/Uniques/helmet.lua:204", pob: full}
  - {kind: unique, name: "Ashes of the Stars", slot: Amulet, role: scales, target: self, text: "+1 to Level of all Skill Gems; +(20-30)% Quality of all Skill Gems; whether PoB turns the Absolution quality (minion cooldown recovery) into a sentinel cooldown effect is not verified; boss drop (Eater of Worlds Uber)", source: "Data/Uniques/amulet.lua:88-89; items.md section 2c", pob: partial}
  - {kind: unique, name: "The Hungry Loop", slot: Ring, role: scales, target: self, text: "consumed support mods (Minion Damage, Minion Life, Minion Speed, Awakened Minion Damage) apply to the gem in the ring's one socket; measured with Minion Speed on the Summon Raging Spirit group: minion Speed +10.46%; not run with Absolution", source: "Data/Uniques/ring.lua:679-686; Data/ModItemExclusive.lua:5734-5737,5870; items.md section 2c", pob: partial}
  - {kind: unique, name: "Doryani's Prototype", slot: "Body Armour", role: blocks, target: self, text: "Deal no Non-Lightning Damage: the blast keeps 50% physical after the 50% conversion, so half of the blast may be dealt as nothing unless more is converted; sentinels are minions and the flag is player-only (derived, not measured)", source: "Data/Uniques/body.lua:976; items.md section 2c", pob: full}
  - {kind: unique, name: "Algor Mortis", slot: Gloves, role: scales, target: enemy, text: "Enemies in your Chilling Areas take (25-35)% increased Lightning Damage (the blast is lightning after conversion); needs conditionEnemyInChillingArea", source: "Data/Uniques/gloves.lua:929-930; Modules/ConfigOptions.lua:2039; items.md section 2c", pob: config}
  - {kind: ascendancy, name: "Mindless Aggression (Necromancer)", slot: tree, role: scales, target: self, text: "Minions have 20% more Maximum Life; Minions deal 10% more Damage: sentinel +10.69% DPS, +20.00% Life", source: "TreeData/3_29/tree.lua:57569; tree.md section 2", pob: full}
  - {kind: ascendancy, name: "Unnatural Strength (Necromancer)", slot: tree, role: scales, target: self, text: "Minions have Unholy Might: sentinel +9.04% DPS", source: "TreeData/3_29/tree.lua:57590; tree.md section 2", pob: full}
  - {kind: notable, name: "Fearsome Force", slot: tree, role: scales, target: self, text: "Minions have 60% increased Critical Strike Chance and +20% Critical Strike Multiplier: sentinel +8.64% DPS (second copy in the sample)", source: "TreeData/3_29/tree.lua:29954; tree.md section 2", pob: full}
  - {kind: notable, name: "Gravepact", slot: tree, role: scales, target: self, text: "+7% Chaos Resistance; Minions have 8% chance to deal Double Damage: sentinel +8.55% DPS", source: "TreeData/3_29/tree.lua:36165; tree.md section 2", pob: full}
makes_redundant:
  - {provider: "Sentinel limit above 3 (Dark Monarch doubling, +limit mods) as a DPS source", when: "always in PoB", why: "limit mods change the output field only; sentinels alive are never derived from it (limit 3 -> 6: FullDPS 0.000%), so the app must raise the count itself", source: "Modules/CalcPerform.lua:1436-1457; coverage-minion-skills.md section 3"}
  - {provider: "Absolution gem count above 1 with the box unticked", when: "count > 1", why: "the blast row is multiplied by the count too although it cannot shotgun: count 3 over-counts the blast by 2 x 35,456 plus its culling share; the box removes 78,791.8 FullDPS in the sample, the sentinel row stays x count", source: "Modules/Calcs.lua:204-210,255; coverage-minion-skills.md section 3 (e6.json)"}
conflicts:
  - {with: "The Dark Monarch (other variants)", effect: "cannot have minions other than the doubled type: not parsed, so PoB keeps the Spectres and Guardian counted next to Sentinels of Absolution", source: "Data/Uniques/helmet.lua:854-865; items.md section 1b"}
  - {with: "Wraithlord", effect: "You cannot have Non-Spectre Minions: sentinels are not Spectres; not parsed, not enforced", source: "Data/Uniques/helmet.lua:798; items.md section 2c"}
  - {with: "Chains of Command", effect: "You cannot have Non-Animated, Non-Manifested Minions: no Sentinels; not enforced by PoB", source: "Data/Uniques/body.lua:968; items.md section 2c"}
  - {with: "Spell Totem or Spell Cascade support", effect: "the config box tooltip says not to tick 'count skill damage once' with them", source: "Modules/ConfigOptions.lua:759"}
conditions:
  - {text: "Sentinels are summoned from the corpse of a non-unique enemy that dies while debuffed (debuff 3 s base), or refresh the duration and life of an existing one at the maximum; 25% chance to summon when the blast hits a rare or unique (PoB ignores the 25%)", source: "wiki Absolution rev 1682183; Data/Skills/act_str.lua:7,44"}
  - {text: "Sentinels have a melee attack that cannot normally be used, and two spells: AbsolutionMinion (no cooldown) and AbsolutionMinionEmpowered (6 s cooldown). PoB's default skill 1 is the melee; the generator must set skillMinionSkill = 2 (x1.96 against skill 1)", source: "wiki Absolution rev 1682183; minion-skills.md section 3 (m3.json E5)"}
  - {text: "Limits are output-only: counts over the limit are not capped; the count 3 here is hand-set and equals the limit only by assumption", source: "Modules/CalcPerform.lua:1436-1457; coverage-minion-skills.md section 3"}
  - {text: "conditionUsedMinionSkillRecently is auto true while Absolution (not permanent) is the evaluated skill, so the sentinel row has it already; in the same FullDPS the permanent Animate Guardian / Raise Spectre rows evaluate without it", source: "Modules/CalcPerform.lua:253-255; coverage-minion-skills.md sections 3 and 4"}
  - {text: "Disciples (cluster, 'Summoned Sentinels have 25% increased Cooldown Recovery Rate') is parsed for Herald of Purity, Dominating Blow and Absolution (ModParser.lua:1173) but CDR is not in TotalDPS; 'Sentinels of Purity' lines on Circle of Guilt / Circle of Ambition are scoped to Herald of Purity and do nothing here", source: "Modules/ModParser.lua:1171-1173; tree.md section 2; items.md section 2c"}
uptime:
  Mapping:       {value: model, config: {skillMinionSkill: 2, "gem count": "floor(alive) up to the limit", absolutionSkillDamageCountedOnce: "tick when count > 1"}, reasoning: "kills of debuffed non-unique enemies keep the sentinels at the limit; 15 s base (27.621 s in the sample build) against pack gaps; PoB holds the limit alive by assumption", source: "wiki Absolution rev 1682183; Minion alive count model (absolution_per_kill_in_maps)"}
  Pinnacle Boss: {value: model, config: {enemyIsBoss: Pinnacle, skillMinionSkill: 2, "gem count": "from 0.25 x HitChance per cast"}, reasoning: "no non-unique corpses on a single boss, so sentinels come only from the 25% chance on hitting a rare or unique boss, which PoB does not parse; Pinnacle -> None changes the sentinel row +38.9% and the blast +41.8% (defences, no uptime); no norm found", source: "Data/Skills/act_str.lua:44; wiki Absolution rev 1682183; coverage-minion-skills.md section 4 (enemyIsBoss row)"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Absolution (rev 1682183, fetched 2026-10-26; 3.28.0 duration and debuff, 3.29.0 cast time)", kind: wiki, patch: "3.29"}
  - {ref: "Data/Skills/act_str.lua:7-103; Data/Minions.lua:864-909; Data/SkillStatMap.lua:2021-2023; Modules/CalcPerform.lua:253-255,1436-1457; Modules/Calcs.lua:116-137,179-180,204-210,255; Modules/ConfigOptions.lua:759-761,976-984,1016-1036,1537-1540; Modules/ModParser.lua:637,1171-1173 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "TreeData/3_29/tree.lua:29954,36165,57569,57590; Data/Uniques/{helmet,amulet,ring,body,gloves}.lua lines in the providers; Data/ModFoulborn.lua:8", kind: pob, patch: "3.29"}
  - {ref: "https://poe-vault.com GhazzyTV's Absolution Necromancer Gear, Jewels & Flasks (Settlers of Kalguur, 2025-06-12, tagged Out Of Date) and a French 3.29 summary, via search text only", kind: discovery, patch: "3.25-3.29"}
not_verified:
  - "no user build has an Absolution gem: every number comes from an in-memory group on the SRS CI Guardian build, not from a real Absolution build"
  - "sentinel alive count and uptime (corpse supply, 25% chance on a boss, refresh) are neither modelled by PoB nor measured; the Minion alive count model's Absolution inputs are unverified"
  - "whether PoB turns the Absolution quality (minion cooldown recovery) into a cooldown effect on sentinels outside the Empowered skill"
  - "the Empowered spell's real share of sentinel damage (6 s cooldown) and whether it is added to skill 2 in game; PoB never adds them"
  - "Doryani's Prototype half-blast effect, Hungry Loop on Absolution, Dark Monarch doubling size: derived from parse output, not measured"
  - "Ascended / Vaal Sentinel of Absolution (base_max_number_of_vaal_absolution_sentinels 1) is not modelled"
  - "3.29 availability of league-origin and boss-drop items; the Settlers gear guide is tagged Out Of Date"
  - "tree valuations are on the SRS CI Guardian build, in memory; nodes marked 'second copy' are already allocated there"
open_questions:
  - "Which Absolution minion skill should the generator measure: skill 2 only, or skill 2 plus the Empowered skill 3? PoB's default skill 1 is the unusable melee; this needs a rule in the engine's gem handling (hand to the lead)"
  - "Which sentinel count should the generator assume on a single Pinnacle boss, given only the 25% chance on hit summons there?"
  - "Should the generator tick absolutionSkillDamageCountedOnce automatically whenever the count is above 1?"
```
