---
type: interaction
status: draft
pob_refs: [conditionEnemyMaimed, conditionEnemyHindered, Condition:Maimed, Condition:Hindered, PhysicalDamageTaken, DamageTakenOverTime, BleedChance, MovementSpeed]
source: "poewiki Maim rev 1702496, Hinder rev 1660573, Wither rev 1681920, Maim Support rev 1681952, Buff rev 1701074 (fetched 2026-10-25); PoB 2.67.2 CalcSetup.lua / ConfigOptions.lua / ModParser.lua / ModCache.lua / SkillStatMap.lua / Data/Skills / Data/Uniques / TreeData 3_29; tasks/reports/027-evidence/mechanics-researcher-uptime.md and pob-coverage-auditor-uptime.md"
last_confirmed_patch: "3.29.x"
---

Maim (applied by attacks) and Hinder (applied by spells) are two separate debuffs that each give the enemy 30% reduced movement speed for a default 4 s; they do not stack with themselves, but an enemy can have both. For a damage build the slow itself is worth nothing in PoB: PoB only counts the DAMAGE side effects, namely Maim Support's +10% physical damage taken, "damage against Maimed / Hindered enemies" lines, bleed chance against Maimed, and "Maimed enemies take increased damage over time". Each of those is behind one checkbox (conditionEnemyMaimed, conditionEnemyHindered), and chance-to-Maim lines are not parsed at all. Chance-on-hit uptime: [[Chance on hit uptime]]; Hinder from the Wither skill: [[Wither]]; other debuffs: [[Intimidate and Unnerve]], [[Blind]].

Pipeline: [[Damage calculation#Damage taken]] - Maim Support's "Maimed enemies take 10% increased Physical damage" is an increased-damage-taken term gated on the Maimed condition, so it only adds physical damage; the movement slow, the real defensive value (a slowed enemy cannot reach you), is not in any DPS step and PoB has no output for it.

```interaction
id: maim-hinder
mechanic: "Maim (attacks) and Hinder (spells): 30% reduced movement speed for 4 s by default, separate debuffs that coexist; multiple maims do not stack, only the strongest Hinder applies; damage side effects in PoB: Maim Support +10% physical damage taken, bleed chance and DoT-taken increases vs Maimed, 'damage against Hindered' lines"
family: ailment
target: enemy
related: [chance-on-hit-uptime, wither, blind, intimidate-unnerve, curse-limit]
pipeline_step: ["Damage calculation#Damage taken", "Damage calculation#Damage over time", "Damage calculation#Ailments from hits", "Damage calculation#Increased and reduced"]
pipeline_why: "PoB models neither the slow nor the duration; only the condition-gated damage terms count: Maim Support PhysicalDamageTaken INC 10 under Condition Maimed (damage taken), 'Enemies Maimed by you take #% increased Damage Over Time' (damage over time), chance_to_bleed_on_hit_%_vs_maimed (ailments from hits) and 'against Maimed / Hindered enemies' multipliers such as Singularity (increased and reduced). The movement slow has no step; it only matters for survival, which PoB does not compute from it."
pob:
  measured: config
  how: "Only the condition exists: config ticks conditionEnemyMaimed (ConfigOptions.lua:1851-1853) and conditionEnemyHindered (:1854-1856), shown only if some modifier mentions the condition (ifEnemyCond). Effects behind the tick: Maim Support PhysicalDamageTaken INC (Data/Skills/sup_str.lua:3590-3592, GlobalEffect Debuff + Condition Maimed), bleed chance vs Maimed (Data/SkillStatMap.lua:1007-1009), 'Enemies Maimed by you take #% increased Damage Over Time' (Modules/ModParser.lua:4364), 'against hindered / maimed enemies' tags (ModParser.lua:1970-1972), Searching Eye jewel: Maimed targets cannot crit and take more crit chance hits (ModParser.lua:3084-3088). CalcSetup.lua:64 puts MovementSpeed INC -30 on the Maimed actor, but no DPS output reads enemy movement speed (not exhaustively searched); there is NO equivalent for Hinder. Chance-to-Maim lines are unparsed (ModCache.lua:3637, 5159, 6324-6327, 7263, 14174-14182, 'Attacks with this Weapon Maim on hit' :14248, 'Enemies near your Banner are Maimed' :15360) and global_maim_on_hit has no SkillStatMap entry. Duration is not modelled."
  config:
    - {var: conditionEnemyMaimed, default: false, ref: "Modules/ConfigOptions.lua:1851", class: b}
    - {var: conditionEnemyHindered, default: false, ref: "Modules/ConfigOptions.lua:1854", class: b}
  unparsed:
    - "all 'x% chance to Maim on Hit' lines, Innsbury Edge 'Attacks with this Weapon Maim on hit', Banner Mastery 'Enemies near your Banner are Maimed' (Data/ModCache.lua:3637, 6324-6327, 14248, 15360)"
    - "Vaal Rain of Arrows: global_maim_on_hit and maim_effect_+% 150 (Data/Skills/act_dex.lua:12640-12660; no Data/SkillStatMap.lua entry)"
model:
  proposed_kind: on_hit_uptime
  inputs: {from_pob: [HitSpeed, Speed, SkillTriggerRate, HitChance], from_scenario: ["m = hits per use on ONE target", "d = 4 s (wiki Maim rev 1702496, Hinder rev 1660573)", "attack skill for Maim, spell skill for Hinder"]}
  params: {duration_s: 4, movement_speed_reduced_pct: 30, maim_support_phys_taken_pct: 10, refresh_on_reapply: "Maim: not verified; Hinder from Wither: refreshed while channelling (wiki); both readings kept"}
  formula: "Use the formulas of [[Chance on hit uptime]] with p = line chance, d = 4: u = uptime. Damage value: Maim Support adds 10% increased physical damage taken while maimed, so physical damage factor = 1 + 0.10 x u (additive with other increased damage taken); damage-vs-Hindered lines (Singularity 60-100%) multiply the matching hits by (1 + x x u). Blend two PoB runs (box off / on) with weight u, floor u to a whole percent, tick the box only at u >= 0.99. Do not model the slow: no step uses it."
  calibration: "no norm found; 4 s, 30%, 10% from wiki Maim rev 1702496, Hinder rev 1660573, Maim Support rev 1681952 and Data/Skills/sup_str.lua:3598-3599"
providers:
  - {kind: support, name: "Maim Support", slot: any, role: applies, target: enemy, text: "attack skills: 30% chance to Maim on hit; Maimed enemies take 10% increased Physical Damage (since 3.15.0); supported skills deal 10-19% more Physical Damage; quality 0-20% increased Effect of Maim (since 3.23.0)", source: "Data/Skills/sup_str.lua:3577-3606; wiki Maim Support rev 1681952", pob: config}
  - {kind: gem, name: "Vaal Rain of Arrows", slot: any, role: applies, target: enemy, text: "global_maim_on_hit with 150% increased Maim effect", source: "Data/Skills/act_dex.lua:12640-12660", pob: none}
  - {kind: unique, name: "Innsbury Edge", slot: Sword, role: applies, target: enemy, text: "Attacks with this Weapon Maim on hit (local to the weapon, 100%)", source: "Data/Uniques/sword.lua:211; Data/ModCache.lua:14248", pob: none}
  - {kind: unique, name: "The Crimson Storm", slot: Bow, role: applies, target: enemy, text: "50% chance to Maim Enemies on Critical Strike with Attacks", source: "Data/Uniques/bow.lua:90; Data/ModCache.lua:10093", pob: none}
  - {kind: unique, name: "Taproot", slot: Dagger, role: applies, target: enemy, text: "(15-20)% chance to Maim on Hit; 0.5% of Attack Damage Leeched as Life against Maimed Enemies", source: "Data/Uniques/dagger.lua:252-253; Modules/ModParser.lua:1971", pob: partial}
  - {kind: notable, name: "Dismembering", slot: tree, role: applies, target: enemy, text: "20% chance to Maim Enemies on Critical Strike with Attacks", source: "TreeData/3_29/tree.lua:41038; Data/ModCache.lua:6324", pob: none}
  - {kind: mastery, name: "Dual Wielding Mastery", slot: tree, role: applies, target: enemy, text: "20% chance to Maim Enemies with Main Hand Hits (and 20% chance to Blind with Off Hand Hits)", source: "TreeData/3_29/tree.lua:54079-54080; Data/ModCache.lua:6325-6326", pob: none}
  - {kind: mastery, name: "Banner Mastery", slot: tree, role: applies, target: enemy, text: "Enemies near your Banner are Maimed", source: "TreeData/3_29/tree.lua:24685; Data/ModCache.lua:15360", pob: none}
  - {kind: gem, name: "Wither", slot: any, role: applies, target: enemy, text: "Hinder (30% reduced movement speed at L1) while channelling, refreshed constantly while channelling; duration scales with skill effect duration", source: "Data/Skills/act_int.lua:21232-21275; wiki Wither rev 1681920", pob: config}
  - {kind: unique, name: "Singularity", slot: Mace, role: abuses, target: enemy, text: "Nearby Enemies are Hindered, with 25% reduced Movement Speed; (60-100)% increased Damage with Hits and Ailments against Hindered Enemies", source: "Data/Uniques/mace.lua:634-636; Data/ModCache.lua:18340; Modules/ModParser.lua:1970", pob: full}
  - {kind: mastery, name: "Curse Mastery", slot: tree, role: applies, target: enemy, text: "Enemies you Curse are Hindered, with 15% reduced Movement Speed (needs a curse on the target)", source: "TreeData/3_29/tree.lua:36775; Data/ModCache.lua:15378", pob: partial}
  - {kind: unique, name: "The Felbog Fang", slot: Amulet, role: applies, target: enemy, text: "Enemies Cursed by you are Hindered if 25% of Curse Duration expired", source: "Data/Uniques/amulet.lua:527; Data/ModCache.lua:15288; Modules/ModParser.lua:4037", pob: partial, variant: "variants 1,2"}
makes_redundant:
  - {provider: "a second Hinder source", when: "one Hinder is already on (Singularity or Wither channel)", why: "only the strongest Hinder takes effect; the extra source adds nothing unless it carries a damage condition the first lacks", source: "wiki Hinder rev 1660573"}
conflicts:
  - {with: "Maim vs Hinder", effect: "different debuffs, an enemy can have both at once", source: "wiki Maim rev 1702496 (patch 2.2.0); Hinder rev 1660573"}
  - {with: "Maim by minions vs player", effect: "'Enemies Maimed by you take increased Damage Over Time' stacks only while the maim is applied by the same entity", source: "wiki Maim rev 1702496"}
conditions:
  - {text: "Maim: 30% reduced movement speed, default duration 4 s, applied by attacks; multiple maims do not stack", source: "https://www.poewiki.net/wiki/Maim rev 1702496 (introduced 2.2.0)"}
  - {text: "Hinder: 30% reduced movement speed and 4 s by default (items, gems and flasks may specify another value and duration); only the strongest Hinder takes effect; applied by spells", source: "https://www.poewiki.net/wiki/Hinder rev 1660573 (introduced 2.1.0)"}
  - {text: "the Hinder from Wither does not stack and its duration is constantly refreshed while channelling; skill effect duration modifiers apply to both Wither debuffs", source: "https://www.poewiki.net/wiki/Wither rev 1681920"}
uptime:
  Mapping:       {value: model, config: {conditionEnemyMaimed: "ON only for 'nearby/always' sources, else model", conditionEnemyHindered: "ON for Singularity (nearby) or while channelling Wither; model otherwise"}, reasoning: "chance-to-Maim or hit-conditional sources depend on hit rate on one target; nearby-aura sources are on whenever enemies are in range", source: "vault Interactions/Chance on hit uptime; Data/ModCache.lua:18340"}
  Pinnacle Boss: {value: model, config: {conditionEnemyMaimed: "model: same rule", conditionEnemyHindered: "model: same rule; Singularity nearby needs the boss in its range"}, reasoning: "one target, so hit-rate maths decides chance sources; whether bosses are affected by Maim or Hinder (movement speed debuffs) is not documented", source: "vault Interactions/Chance on hit uptime; wiki Hinder rev 1660573"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Maim (rev 1702496)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Hinder (rev 1660573)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Wither (rev 1681920)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Maim_Support (rev 1681952)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcSetup.lua:64; Modules/ConfigOptions.lua:1851-1856; Modules/ModParser.lua:1970-1972,3084-3088,4037,4362-4364; Data/SkillStatMap.lua:1007-1009; Data/Skills/sup_str.lua:3577-3606; Data/ModCache.lua:3637,6324-6327,10093,14174-14182,14248,15288,15360,15378,18340", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/mechanics-researcher-uptime.md (rows Maim, Hinder) and pob-coverage-auditor-uptime.md", kind: discovery, patch: "3.29"}
not_verified:
  - "whether re-applying Maim refreshes its 4 s timer, starts a second timer, or is ignored: the wiki says only 'multiple maims do not stack'; the source of that line is a Mark_GGG Reddit comment (not fetched here)"
  - "whether re-applying Hinder refreshes in general: the wiki says refreshed while channelling for Wither only; other Hinder sources and the 4 s default are not stated"
  - "how the Maim Support mod reaches the enemy in PoB (GlobalEffect Debuff + Condition Maimed on the skill modList) and whether the config tick alone is enough; the path through the enemy modDB was not traced"
  - "whether any PoB output uses enemy MovementSpeed (CalcSetup.lua:64 adds -30% for Maimed; only a partial search was made)"
  - "whether bosses are immune to or partly resistant to the movement slow (no source)"
  - "whether Vaal Rain of Arrows' maim chance (global_maim_on_hit) is 100% (stat has no value in the gem table)"
open_questions:
  - "Should the generator ignore the movement slow completely (no PoB step) or treat Singularity-style always-on Hinder as a defensive QoL line shown outside DPS?"
```
