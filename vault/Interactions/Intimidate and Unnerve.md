---
type: interaction
status: draft
pob_refs: [conditionEnemyIntimidated, conditionEnemyUnnerved, Condition:Intimidated, Condition:Unnerved, DamageTaken, Party:Intimidated, Party:Unnerved]
source: "poewiki Intimidate rev 1702396, Unnerve rev 1673508, Buff rev 1701074 (fetched 2026-10-25); PoB 2.67.2 CalcSetup.lua / ConfigOptions.lua / ModParser.lua / ModCache.lua / Data/Skills / Data/Uniques / TreeData 3_29; tasks/reports/027-evidence/mechanics-researcher-uptime.md and pob-coverage-auditor-uptime.md"
last_confirmed_patch: "3.29.x"
---

Intimidate makes the enemy take 10% increased ATTACK damage and Unnerve 10% increased SPELL damage (both are debuffs on the enemy; neither affects damage over time, even from an attack or spell). PoB models each as a fixed +10% increased damage taken (attack or spell flag) behind one checkbox, so a generator can see the value only when the box is ticked. The wording trap: "x% chance to Intimidate/Unnerve for 4 seconds on Hit" lines are NOT parsed by PoB at all (ModCache leaves the text unused), while "Nearby Enemies are Intimidated", "Enemies you Curse are Unnerved" and the block/warcry lines ARE parsed. Chance-on-hit sources need the uptime maths of [[Chance on hit uptime]]. Do not pair Intimidate with a spell build or Unnerve with an attack build: Grattus Signet gives the wrong half to each skill type.

General rule (user 2026-10-25): the method in [[Chance on hit uptime]] "General method" (source line, PoB hit-rate fields, duration, uptime per scenario, value when up, config box state) applies to this effect in every build. Worked examples (EK, Worb, FR v2): no Intimidate source in any of the three (checked: items, 128/132/133 passives, gems, modDB dump; 027-debuff-uptime.md section 2; near miss: the Shield Mastery option listed in providers is not taken); what-if p 10%, d 4 s (all ticked, no notice): u = 99% any hit, 97% EK / 98% FR v2 for the Cyclone attack; value when up: only Cyclone attack hits gain 10% in EK and FR v2, knives, Forbidden Rite and Winter Orb are spells so 0; Worb 0; the Intimidated box is shown and unticked = correct (FR v2 has conditionEnemyUnnerved ticked, source unknown, see not_verified).

Pipeline: [[Damage calculation#Damage taken]] - both are a flat +10% in the increased-damage-taken term of the enemy, flagged Attack or Spell; they are not "more" multipliers and add to the other increased damage taken sources, so a build with large Hit-taken increases gets a smaller relative gain.

```interaction
id: intimidate-unnerve
mechanic: "Intimidated enemies take 10% increased Attack damage, Unnerved enemies take 10% increased Spell damage; hits only (not damage over time); one effect per debuff regardless of source count; default duration 4 s from the item text (the wiki pages give none)"
family: ailment
target: enemy
related: [chance-on-hit-uptime, maim-hinder, curse-limit, wither]
pipeline_step: ["Damage calculation#Damage taken"]
pipeline_why: "Both debuffs are an increased-damage-taken term on the enemy (PoB modDB DamageTaken INC 10 with ModFlag.Attack or ModFlag.Spell under Condition Intimidated / Unnerved, CalcSetup.lua:65-68), applied after the hit is built, so they belong to the damage-taken step; a skill of the wrong damage type (spell vs attack) gets nothing."
pob:
  measured: config
  how: "The effect is calculated once the condition is on: CalcSetup.lua:65 DamageTaken INC 10 (ModFlag.Attack) under Condition Intimidated, :67 the same with ModFlag.Spell under Unnerved; the Party: variants (:66, :68) count a party member's debuff once. The condition itself comes from a config tick (ConfigOptions.lua:1982 conditionEnemyIntimidated, :2003 conditionEnemyUnnerved) or from a parsed provider line (ModParser.lua:2598, 5068-5082, ModCache.lua:15379, 18341-18345). 'x% chance to Intimidate/Unnerve Enemies for 4 seconds on Hit' is unparsed (ModCache.lua:3635, 3665 and the other percent rows leave the text ' to Intimidate Enemies'; ModCache wording (pob-coverage-auditor, 027-debuff-uptime.md section 5): most chance-to-X lines are {{}, '<leftover>'} (empty mod list, leftover kept as extra, ModParser.lua:7002-7006; Item.lua:1325/1344/1352), only a few are truly {nil, ...} (ModCache.lua:14399 'Blind Enemies on Hit', 17254 'Intimidate Enemies for 4 seconds on Hit', 14097-14098); either way no mod; only the always/conditional wordings parse as EnemyModifier Condition flags (ModParser.lua:2598, 4362-4363, 5067-5082, 6516).); the gem stats chance_to_intimidate_on_hit_% / chance_to_unnerve_on_hit_% have no SkillStatMap entry (grep of Data/SkillStatMap.lua: 0 hits)."
  config:
    - {var: conditionEnemyIntimidated, default: false, ref: "Modules/ConfigOptions.lua:1982", class: b}
    - {var: conditionEnemyUnnerved, default: false, ref: "Modules/ConfigOptions.lua:2003", class: b}
  unparsed:
    - "Awakened Melee Physical Damage: chance_to_intimidate_on_hit_% 10 (Data/Skills/sup_str.lua:3728-3760) and Awakened Controlled Destruction: chance_to_unnerve_on_hit_% (Data/Skills/sup_int.lua:1228-1262) not in Data/SkillStatMap.lua"
    - "Cleaving / Fearsome Warrior / Two Hand Mastery: '15% chance to Intimidate ... on Hit with Attacks', '25% chance to Intimidate nearby Enemies for 4 seconds on Melee Kill', 'Ruthless Hits Intimidate Enemies for 4 seconds' (Data/ModCache.lua:5157, 7262, 19838)"
    - "Grattus Signet: 'Attacks inflict Unnerve on Critical Strike for 4 seconds / Spells inflict Intimidate on Critical Strike for 4 seconds' (Data/ModCache.lua:14224-14225, 21848)"
model:
  proposed_kind: on_hit_uptime
  inputs: {from_pob: [HitSpeed, Speed, SkillTriggerRate, HitChance], from_scenario: ["m = hits per use on ONE target", "d = 4 s from the item text (Data/ModCache.lua:3635, 3665); not on the wiki pages", "for on-block or on-kill sources: blocks per s of the enemy or kills per s, class b assumption"]}
  params: {duration_s: 4, refresh_on_reapply: "not verified (both readings kept: refresh u = 1-(1-p)^(m*n); no reapply u = n/(n+1/P))", effect_pct: 10}
  formula: "Use the formulas of [[Chance on hit uptime]] with p = the line's chance, d = 4: u = uptime of the debuff. The damage factor on matching hits = 1 + 0.10 x u (increased damage taken, additive with the other taken-increases); floor u to a whole percent, box state by the user rule 2026-10-25: u >= 80% ticked, no notice; 50% <= u < 80% ticked and the user is informed with u; u < 50% unticked, warning with u (optional display: blend of two PoB runs). 'Nearby Enemies are Intimidated/Unnerved', 'Enemies you Curse are Unnerved' (needs the curse up, see curse-limit), 'Enemies Taunted by your Warcries are Intimidated' and 'Permanently Intimidate on Block' are not chance rolls: use the box with the condition each needs (curse, taunt + warcry used recently, blocked recently)."
  calibration: "no norm found; value when up: Intimidate '10% increased attack damage' taken, not DoT (wiki Intimidate rev 1702396, patch 3.1.0; 4 s only from item text); Unnerve rev 1673508; PoB CalcSetup.lua:65-68; 027-debuff-uptime.md section 4 (mechanics-researcher)"
providers:
  - {kind: gem, name: "Intimidating Cry", slot: any, role: applies, target: enemy, text: "warcry; with 'Enemies Taunted by this Warcry are Intimidated' the debuff only lasts while the taunt is on (overwriting the taunt removes it)", source: "Data/Skills/act_str.lua:7337-7380 (enemies_taunted_by_your_warcies_are_intimidated); wiki Intimidating Cry rev 1682136; Modules/ModParser.lua:5070", pob: partial}
  - {kind: support, name: "Awakened Melee Physical Damage Support", slot: any, role: applies, target: enemy, text: "10% chance to Intimidate on hit from level 5; 'legacy = true' in PoB data (obtainability not verified)", source: "Data/Skills/sup_str.lua:3728-3760", pob: none}
  - {kind: support, name: "Awakened Controlled Destruction Support", slot: any, role: applies, target: enemy, text: "chance to Unnerve on hit (10% from level 5); 'legacy = true' in PoB data (obtainability not verified)", source: "Data/Skills/sup_int.lua:1228-1262", pob: none}
  - {kind: mastery, name: "Shield Mastery (effect 10059)", slot: tree, role: applies, target: enemy, text: "option: Intimidate Enemies for 4 seconds on Block while holding a Shield (mastery 45558 is allocated in EK, Worb and FR v2 but this option is not selected)", source: "TreeData/3_29/tree.lua:34630; tree-ascendancy-analyst, 027-debuff-uptime.md section 2", pob: none}
  - {kind: unique, name: "Belt of the Deceiver", slot: Belt, role: applies, target: enemy, text: "Nearby Enemies are Intimidated (variant 2)", source: "Data/Uniques/belt.lua:127; Data/ModCache.lua:18341", pob: full, variant: "variant 2"}
  - {kind: unique, name: "The Anticipation", slot: Shield, role: applies, target: enemy, text: "Permanently Intimidate Enemies on Block (needs a recent block; also +Armour if you've Blocked Recently)", source: "Data/Uniques/shield.lua:38; Modules/ModParser.lua:5068 (Condition BlockedRecently)", pob: config}
  - {kind: unique, name: "Al Dhih", slot: Claw, role: applies, target: enemy, text: "Trigger Level 1 Intimidating Cry on Hit (variants 4-5); the cry only helps if its taunt condition holds", source: "Data/Uniques/claw.lua:80; Data/ModCache.lua:22180", pob: partial, variant: "variants 4,5"}
  - {kind: unique, name: "Grattus Signet", slot: Ring, role: applies, target: enemy, text: "Attacks inflict Unnerve on Critical Strike for 4 seconds; Spells inflict Intimidate on Critical Strike for 4 seconds (each half gives the debuff for the OTHER damage type than the skill that applied it)", source: "Data/Uniques/ring.lua:593-594; Data/ModCache.lua:14224", pob: none}
  - {kind: notable, name: "Haunting Shout", slot: tree, role: applies, target: enemy, text: "Enemies Taunted by your Warcries are Intimidated", source: "TreeData/3_29/tree.lua:86420-86427; Modules/ModParser.lua:5070", pob: partial}
  - {kind: ascendancy, name: "First to Strike, Last to Fall (Champion) / Ascendant Champion option", slot: tree, role: applies, target: enemy, text: "Your Hits permanently Intimidate Enemies that are on Full Life (only the first hit while full life)", source: "TreeData/3_29/tree.lua:50378-50384, 18370-18381; Modules/ModParser.lua:2598 (Condition ChampionIntimidate)", pob: config}
  - {kind: notable, name: "Master of Fear / Doedre's Apathy", slot: tree, role: applies, target: enemy, text: "Enemies you Curse are Unnerved (needs a curse on the target; Doedre's Apathy also lets Temporal Chains affect Hexproof)", source: "TreeData/3_29/tree.lua:87826-87834, 89178-89186; Data/ModCache.lua:15379", pob: partial}
  - {kind: mastery, name: "Rage Mastery", slot: tree, role: applies, target: enemy, text: "Nearby Enemies are Intimidated while you have Rage", source: "TreeData/3_29/tree.lua:23775; Modules/ModParser.lua:5080", pob: config}
  - {kind: notable, name: "Fearsome Warrior", slot: tree, role: applies, target: enemy, text: "25% chance to Intimidate nearby Enemies for 4 seconds on Melee Kill", source: "TreeData/3_29/tree.lua:86730-86738; Data/ModCache.lua:7262 (unparsed)", pob: none}
makes_redundant:
  - {provider: "a second source of the same debuff", when: "one source is already always on (e.g. Nearby Enemies are Intimidated)", why: "only one effect of Intimidate or Unnerve applies; extra chance adds nothing (a debuff of the same name does not stack)", source: "wiki Buff rev 1701074: multiple copies of the same buff do not stack, only the strongest counts"}
conflicts:
  - {with: "Spell builds and Intimidate / attack builds and Unnerve", effect: "Intimidate only raises ATTACK damage taken and Unnerve only SPELL damage taken; a spell build gets nothing from Intimidate and an attack build nothing from Unnerve", source: "wiki Intimidate rev 1702396; Unnerve rev 1673508; Modules/CalcSetup.lua:65-68"}
  - {with: "damage over time", effect: "neither debuff increases damage over time taken, even if the damage comes from an attack or spell that uses attack/spell modifiers for its DoT", source: "wiki Intimidate rev 1702396 (mechanics); Unnerve rev 1673508 (Mark_GGG, 2020-03-11)"}
conditions:
  - {text: "Intimidate: 10% increased Attack damage taken. Unnerve: 10% increased Spell damage taken (introduced 3.8.0). Intimidate was 10% increased damage before 3.1.0, then attack damage only", source: "https://www.poewiki.net/wiki/Intimidate rev 1702396 (3.1.0); https://www.poewiki.net/wiki/Unnerve rev 1673508 (3.8.0)"}
  - {text: "Default duration is 4 seconds: from item text only ('Intimidate Enemies for 4 seconds on Hit', 'Unnerve ... 4 seconds'); the wiki pages carry no duration", source: "Data/ModCache.lua:3635, 3665, 17253-17255, 22367; Lethal Pride text on wiki Intimidate rev 1702396 ('10% chance to Intimidate Enemies for 4 seconds on hit')"}
  - {text: "the debuff is on the target, not global; it is hidden but not removed when a boss is untargetable and expires normally", source: "wiki Buff rev 1701074"}
uptime:
  Mapping:       {value: model, config: {conditionEnemyIntimidated: "ON for always-on providers (Nearby Enemies, Rage Mastery with rage, Anticipation with blocks); model for chance-on-hit providers", conditionEnemyUnnerved: "ON for curse providers while the curse is up; model otherwise"}, reasoning: "always-on and condition-bound sources are about 100% on a pack; chance-on-hit sources follow hit rate on one target (see Chance on hit uptime)", source: "vault Interactions/Chance on hit uptime; Data/ModCache.lua:15379, 18341"}
  Pinnacle Boss: {value: model, config: {conditionEnemyIntimidated: "ticked if a parsed always-on source exists or u >= 50% (user rule 2026-10-25: 50-80% with a notice, < 50% unticked + warning)", conditionEnemyUnnerved: "ticked if the curse stays on the boss (curse-limit) and u >= 50% (user rule 2026-10-25: 50-80% with a notice, < 50% unticked + warning)"}, reasoning: "one target, so hit-rate maths decides chance sources; whether bosses can be intimidated or unnerved at all is not stated", source: "vault Interactions/Chance on hit uptime; wiki Intimidate rev 1702396 (no boss exception listed)"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Intimidate (rev 1702396)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Unnerve (rev 1673508)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Buff (rev 1701074)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Intimidating_Cry (rev 1682136)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcSetup.lua:65-68; Modules/ConfigOptions.lua:1982,2003; Modules/ModParser.lua:2598,5068-5082; Data/ModCache.lua:3635,3665,14224,15379,17253-17255,18341-18346,19838,22367; Data/Skills/sup_str.lua:3728-3760; Data/Skills/sup_int.lua:1228-1262; Data/Skills/act_str.lua:7337-7380", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-debuff-uptime.md (sections 2-5: sources in EK/Worb/FR, what-if uptime, value when up, ModCache wording; skill-gem-analyst, mechanics-researcher, pob-coverage-auditor, tree-ascendancy-analyst)", kind: discovery, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/mechanics-researcher-uptime.md (rows Intimidate, Unnerve) and pob-coverage-auditor-uptime.md", kind: discovery, patch: "3.29"}
not_verified:
  - "refresh on re-apply is not documented on the Intimidate or Unnerve pages (027-debuff-uptime.md section 4); whether re-applying Intimidate or Unnerve refreshes the 4 s duration, starts a second timer, or is ignored: neither wiki page nor the Buff page says; the model keeps both readings (searched wiki Debuff/Buff, Duration, Linger, Ailment: no statement; GGG forum threads are behind Cloudflare)"
  - "the 4 s base duration is from PoB item text only, not the wiki"
  - "whether bosses (pinnacle or map) can be intimidated or unnerved (wiki lists no exception; no test)"
  - "whether Grattus Signet works as the text reads (Unnerve from attacks, Intimidate from spells); only the item text was read"
  - "Awakened Melee Physical Damage and Awakened Controlled Destruction are marked legacy in PoB data; whether they drop in 3.29 is not checked"
  - "whether the PoB attack/spell flag on DamageTaken excludes damage over time exactly as the wiki says (CalcSetup.lua:65-68 flags only; the DoT path was not traced)"
  - "what sets FR v2 conditionEnemyUnnerved (box ticked, no source found; 027-debuff-uptime.md Not verified)"
  - "the Party: variants (CalcSetup.lua:66, 68) are party-play only; not needed for solo builds"
open_questions:
  - "Is a chance-on-hit Intimidate or Unnerve line worth the slot at u below 50%, or should the generator only count always-on and condition-bound sources?"
```
