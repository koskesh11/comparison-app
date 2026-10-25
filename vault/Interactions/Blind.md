---
type: interaction
status: draft
pob_refs: [conditionEnemyBlinded, overrideBuffBlinded, Condition:Blinded, BlindEffect, BlindEffectMod, Accuracy, Evasion, EvadeChance, AccuracyHitChance]
source: "poewiki Blind rev 1697260, Blind Support rev 1681720, Buff rev 1701074 (fetched 2026-10-25); PoB 2.67.2 CalcPerform.lua / CalcDefence.lua / CalcOffence.lua / CalcSetup.lua / ConfigOptions.lua / ModParser.lua / ModCache.lua / SkillStatMap.lua / Data/Skills / Data/Uniques / TreeData 3_29; tasks/reports/027-evidence/mechanics-researcher-uptime.md and pob-coverage-auditor-uptime.md"
last_confirmed_patch: "3.29.x"
---

Blind is a debuff on the enemy: 20% less Accuracy Rating and 20% less Evasion Rating (since 3.16.0) for a base 4 s, scaled by "increased Blind Effect". It matters twice: the blinded enemy hits you less often with attacks (spells always hit, so Blind does nothing against a caster monster) and your own attacks hit it more often if its lower Evasion was holding your hit chance below 100%. PoB applies the 20/20 penalty once the enemy is blinded, but a chance to Blind on hit is NOT parsed (the text is left over in ModCache), so only the config tick, "Nearby Enemies are Blinded" lines, and a few parsed lines turn it on. Blind is not an ailment. Uptime of chance-on-hit sources: [[Chance on hit uptime]]; the other debuffs of this family are [[Intimidate and Unnerve]] and [[Maim and Hinder]].

Pipeline: [[Damage calculation#Hit chance]] - enemy Evasion x 0.8 enters your attack hit chance (CalcOffence.lua:2233-2234), so Blind only adds DPS when your hit chance is below 100% (many builds sit at the cap and gain nothing); the main value is [[Receiving damage#Preventing the hit]] (enemy Accuracy x 0.8 into your evade chance, CalcDefence.lua:1093) which only works if the build has Evasion and the enemy attacks rather than casts.

```interaction
id: blind
mechanic: "Blinded enemy has 20% less Accuracy Rating and 20% less Evasion Rating (x (1 + increased Blind Effect), rounded down), base duration 4 s; reduces its chance to hit with ATTACKS (not spells), raises your attack hit chance only while below 100%; not an ailment; wiki also says it reduces the enemy's critical strike confirmation (not modelled by PoB)"
family: ailment
target: enemy
related: [chance-on-hit-uptime, intimidate-unnerve, maim-hinder, curse-limit]
pipeline_step: ["Damage calculation#Hit chance", "Receiving damage#Preventing the hit", "Defences#Evasion"]
pipeline_why: "Blind multiplies the ENEMY's Accuracy and Evasion by 0.8 (PoB CalcPerform.lua:857-865 on the enemy actor): enemy Evasion feeds the player's attack hit chance (hit-chance step, only below 100%), enemy Accuracy feeds the player's evade chance (preventing-the-hit step, Evasion defence). It is not a damage multiplier, so a build with 100% hit chance and no evasion gets no value from it."
pob:
  measured: partial
  how: "The effect is calculated once enemyDB has the Blind flag: CalcPerform.lua:857-865 (doActorMisc for the enemy, CalcPerform.lua:3625) adds Accuracy MORE and Evasion MORE of -floor(20 x (1 + inc BlindEffect)); an override caps it at the config value (overrideBuffBlinded). The flag comes from Condition:Blinded (CalcSetup.lua:75) which is set by the config tick (ConfigOptions.lua:1860-1862) or a parsed line ('Nearby Enemies are Blinded' ModCache.lua:18331, '... while Physical Aegis is not depleted' :18333, 'Enemies near corpses affected by your curses are Blinded' ModParser.lua:2184, Searching Eye jewel ModParser.lua:4363). Uses: enemy Evasion in your hit chance (CalcOffence.lua:2233-2234), enemy Accuracy in your evade chance (CalcDefence.lua:1093-1107), 'increased Blind Effect' as EnemyModifier BlindEffect INC (SkillStatMap.lua:505, ModParser.lua:2248-2249, ModCache e.g. :4352), crit vs Blinded (SkillStatMap.lua:662). NOT modelled: any chance to Blind on hit (ModCache.lua:3587, 3612-3614, 5145-5146, 7238-7239 leave the text unparsed; global_chance_to_blind_on_hit_% has no SkillStatMap entry), Blind duration, the enemy critical strike reduction, blind-induced miss of spells (none)."
  config:
    - {var: conditionEnemyBlinded, default: false, ref: "Modules/ConfigOptions.lua:1860", class: b}
    - {var: overrideBuffBlinded, default: "unset (max effect)", ref: "Modules/ConfigOptions.lua:1863 (only shown when the tick is on; strongest source applies)", class: c}
  unparsed:
    - "Blind Support: global_chance_to_blind_on_hit_% 10 (Data/Skills/sup_dex.lua:388-404), blind_duration_+% not mapped"
    - "chance-to-Blind-on-hit lines: Dark Seer, Moonsorrow, Retaliation Charm, Maloney's Mechanism, Kondo's Pride, Grasping Nightshade, Blind Chance / Dazzling Strikes / Saboteur tree nodes (Data/ModCache.lua:3587, 3612-3614, 5145, 6302, 7238-7239)"
    - "Curse Mastery 'Non-Cursed Enemies you inflict Non-Aura Curses on are Blinded for 4 seconds' (Data/ModCache.lua:18447)"
model:
  proposed_kind: on_hit_uptime
  inputs: {from_pob: [HitSpeed, Speed, SkillTriggerRate, HitChance, AccuracyHitChance, EvadeChance], from_scenario: ["m = hits per use on ONE target", "d = 4 s (wiki Blind rev 1697260); Blind Support duration scaling not parsed", "E = enemy attacks per s on you (class b assumption) for the defensive value"]}
  params: {duration_s: 4, accuracy_less_pct: 20, evasion_less_pct: 20, refresh_on_reapply: "not verified (both readings kept)"}
  formula: "Use the formulas of [[Chance on hit uptime]] with p = line chance, d = 4: u = Blind uptime. Offence value: only if AccuracyHitChance < 100 in PoB's run without Blind; blend two PoB runs (box off / on) with weight u on your attack DPS; floor u to a whole percent; tick the box only at u >= 0.99. Defence value: enemy attack hits on you are scaled by (1 - evadeChance(Blind)) for the share u of the time; never blend EHP or time-to-kill (parent note). Effect = floor(20 x (1 + inc Blind Effect)) per stat (CalcPerform.lua:864-865), e.g. Blind Mastery 40% gives 28."
  calibration: "no norm found; the 20/20 values are wiki Blind rev 1697260 (3.16.0) and PoB CalcPerform.lua:864-865"
providers:
  - {kind: support, name: "Blind Support", slot: any, role: applies, target: enemy, text: "10% chance to Blind on hit; supports any hit skill (spells gain no benefit because they cannot miss); quality +0-10% increased Blind Effect since 3.23.0", source: "Data/Skills/sup_dex.lua:388-404; wiki Blind Support rev 1681720", pob: none}
  - {kind: gem, name: "Vaal Blade Flurry", slot: any, role: applies, target: enemy, text: "100% chance to Blind on hit during the Vaal hit sequence; increased Blind Effect stat mapped as a debuff", source: "Data/Skills/act_dex.lua:2135-2152; Data/SkillStatMap.lua:505-507", pob: partial}
  - {kind: unique, name: "The Dark Seer", slot: Mace, role: applies, target: enemy, text: "7-10% Global chance to Blind Enemies on hit; Enemies Blinded by you have Malediction; Unaffected by Blind", source: "Data/Uniques/mace.lua:440-451; Data/ModCache.lua:3587", pob: none}
  - {kind: unique, name: "Eclipse Solaris", slot: Wand, role: applies, target: enemy, text: "Nearby Enemies are Blinded; (120-140)% increased Critical Strike Chance against Blinded Enemies", source: "Data/Uniques/wand.lua:94-95; Data/ModCache.lua:18331", pob: full}
  - {kind: unique, name: "The Ghastly Theatre", slot: Shield, role: applies, target: enemy, text: "Nearby Enemies are Blinded while Physical Aegis is not depleted", source: "Data/Uniques/shield.lua:847; Modules/ModParser.lua:4851; Data/ModCache.lua:18333", pob: config}
  - {kind: unique, name: "Retaliation Charm", slot: Amulet, role: applies, target: enemy, text: "(10-20)% chance to Blind on Hit with Attacks; (25-40)% increased Damage and (30-50)% increased Crit Chance against Blinded Enemies (variant 1: (40-50)% chance to Blind on Critical Strike); Blind you inflict is Reflected to you", source: "Data/Uniques/amulet.lua:953-959", pob: partial, variant: "variants 1,2"}
  - {kind: unique, name: "Grasping Nightshade", slot: Tincture, role: applies, target: enemy, text: "25% chance to Blind on Hit with Melee Weapons; (25-35)% increased Effect of Blind from Melee Weapons", source: "Data/Uniques/tincture.lua:21-22; Modules/ModParser.lua:2249", pob: partial}
  - {kind: unique, name: "Moonsorrow", slot: Wand, role: applies, target: enemy, text: "Socketed gems supported by Level 5-20 Blind; 10% chance to Blind Enemies on hit", source: "Data/Uniques/wand.lua:196-205", pob: none}
  - {kind: notable, name: "Dazzling Strikes", slot: tree, role: applies, target: enemy, text: "20% chance to Blind Enemies on Hit with Attacks; 20% increased Blind Effect; 50% increased Critical Strike Chance against Blinded Enemies", source: "TreeData/3_29/tree.lua:64212-64222", pob: partial}
  - {kind: mastery, name: "Blind Mastery", slot: tree, role: scales, target: enemy, text: "40% increased Blind Effect (option); small nodes Blind Chance 10% / Critical Strikes against Blinded Enemies 25%", source: "TreeData/3_29/tree.lua:64238-64248, 64170-64199; Modules/ModParser.lua:2248", pob: full}
  - {kind: ascendancy, name: "Saboteur (Born in the Shadows)", slot: tree, role: applies, target: enemy, text: "25% chance to Blind Enemies on Hit; you cannot be Blinded", source: "TreeData/3_29/tree.lua:21160", pob: none}
  - {kind: mastery, name: "Curse Mastery", slot: tree, role: applies, target: enemy, text: "Non-Cursed Enemies you inflict Non-Aura Curses on are Blinded for 4 seconds", source: "TreeData/3_29/tree.lua:36760; Data/ModCache.lua:18447", pob: none}
makes_redundant:
  - {provider: "chance-to-Blind lines", when: "a 'Nearby Enemies are Blinded' source is equipped", why: "the aura-like sources keep the debuff on at all times, so extra chance adds nothing but still adds Blind Effect scaling", source: "Data/ModCache.lua:18331"}
conflicts:
  - {with: "Resolute Technique / Unwavering Stance on the target side", effect: "Blind's penalty has no effect on chance to hit / evasion chance if Resolute Technique ('Hits can't be Evaded') or Unwavering Stance ('Cannot Evade Enemy Attacks') is involved; the rating value still changes", source: "wiki Blind rev 1697260"}
  - {with: "spell casters (monsters and your own spells)", effect: "spells have no chance to hit, so Blind does nothing against monsters that cast and does not help spell hit chance", source: "wiki Blind Support rev 1681720"}
  - {with: "Born in the Shadows / Soul of Garukhan / Second Sight", effect: "Cannot be Blinded on the character; existing Blind is not removed, Second Sight 'You are Blind' is removed immediately (for blind on YOU, not the enemy)", source: "wiki Blind rev 1697260"}
conditions:
  - {text: "Blinded: 20% less Accuracy Rating and 20% less Evasion Rating (3.16.0; before that Blind reduced hit chance); base duration 4 s; lowers visual light radius to its minimum", source: "https://www.poewiki.net/wiki/Blind rev 1697260 (patch 3.16.0)"}
  - {text: "the penalty to evade/hit chance is lost against Resolute Technique or Unwavering Stance; the Accuracy/Evasion rating numbers still change", source: "wiki Blind rev 1697260"}
  - {text: "Blinding a target also reduces its effective critical strike chance by reducing its chance to succeed critical strike confirmation rolls (forum post 2012, cited on the wiki; PoB does not model it)", source: "wiki Blind rev 1697260 (reference Mark_GGG, 2012-11-05)"}
  - {text: "PoB rounds each stat down: floor(20 x (1 + inc Blind Effect/100)); the override can only lower it", source: "Modules/CalcPerform.lua:859-865"}
uptime:
  Mapping:       {value: model, config: {conditionEnemyBlinded: "ON for 'Nearby Enemies are Blinded' sources; model for chance-on-hit sources (tick only at u >= 0.99, else blend)"}, reasoning: "worth it only if the build has evasion (defence) or a hit chance below 100% (offence); on packs the hit rate on one target is high for fast skills", source: "vault Interactions/Chance on hit uptime; Modules/CalcPerform.lua:857-865"}
  Pinnacle Boss: {value: model, config: {conditionEnemyBlinded: "model: same rule; bosses are single targets"}, reasoning: "one target, so hit-rate maths decides chance sources; whether a boss can be blinded and whether it hits mostly with attacks or spells is not documented", source: "vault Interactions/Chance on hit uptime; wiki Blind Support rev 1681720"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Blind (rev 1697260)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Blind_Support (rev 1681720)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Buff (rev 1701074)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcPerform.lua:857-865,3625; Modules/CalcDefence.lua:1093-1107,1557-1558; Modules/CalcOffence.lua:2233-2234; Modules/CalcSetup.lua:75,676; Modules/ConfigOptions.lua:1860-1864; Modules/ModParser.lua:2184,2248-2249,4363,4851; Data/SkillStatMap.lua:505,662; Data/ModCache.lua:3587,3612-3614,5145,7238,18331-18333,18447", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/mechanics-researcher-uptime.md (row Blind) and pob-coverage-auditor-uptime.md (Q3)", kind: discovery, patch: "3.29"}
not_verified:
  - "whether re-applying Blind refreshes the 4 s timer, adds a second timer or is ignored: Blind is not an ailment, so the ailment replacement rule is not stated for it; no wiki, Buff-page or patch note statement found (GGG forum threads are behind Cloudflare)"
  - "how Blind Support's blind_duration_+% scales the 4 s base (stat has no SkillStatMap entry; quality changed to Blind Effect in 3.23.0)"
  - "the exact hit-chance formula effect of -20% enemy evasion on specific monsters (PoB reads enemyDB Evasion, which depends on the monster table; not traced per boss)"
  - "enemy attack versus spell share of pinnacle bosses (defensive value)"
  - "whether the crit-confirmation reduction from the 2012 forum post still holds in 3.29 (wiki cites only the old post)"
  - "whether Blind duration is affected by the 4 s 'for 4 seconds' text of Curse Mastery or Searching Eye (only text read)"
open_questions:
  - "Should the generator count Blind as offence only when a build's hit chance is below 100%, and as defence only with Evasion, or always treat it as the parent uptime model with both values?"
```
