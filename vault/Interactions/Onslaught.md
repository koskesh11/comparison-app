---
type: interaction
status: draft
pob_refs: [buffOnslaught, Condition:Onslaught, Onslaught, OnslaughtEffect, BuffEffectOnSelf, KilledRecently, CriticalStrike, Fortified, Speed, MovementSpeed]
source: "wiki Onslaught rev 1493254, Charge rev 1700592; PoB 2.67.2 ConfigOptions.lua, CalcPerform.lua, CalcSetup.lua, ModParser.lua, Data/ModCache.lua, Data/Uniques, TreeData/3_29/tree.lua, Data/Skills/act_dex.lua; mechanics-researcher-uptime.md, build-strategist.md (task 027)"
last_confirmed_patch: "3.29.x"
---

Onslaught is a non-stackable buff worth 20% increased attack, cast and movement speed. It lasts 4 seconds when a source does not say otherwise and is refreshed when gained again; skill duration does not change it. PoB applies the full 20% (times effect) whenever its Onslaught condition is true, and sets that condition from a config tick or from "gain Onslaught on kill / crit / when hit" lines, dropping the chance and the duration. So the number is right while the buff is up and says nothing about how often it is up.

Pipeline: [[Damage calculation#Hit rate]] - Onslaught raises hits per second, which multiplies the damage per hit (TotalDPS = AverageDamage x hit speed) instead of acting inside the per-hit steps; the movement and evasion parts are outside the damage steps. For [[Chance on hit uptime]] style models it acts on V (uses per second).

```interaction
id: onslaught
mechanic: "Onslaught: +20% increased Attack, Cast and Movement Speed (non-stackable buff, 4 s by default, refreshed on regain, not scaled by skill duration, scaled by Onslaught/buff effect); PoB applies it as a flag from a config tick or from parsed 'gain Onslaught' lines without chance or duration"
family: buff
target: self
related: [endurance-charges, frenzy-charges, fortify, chance-on-hit-uptime, flask-uptime, rampage]
pipeline_step: ["Damage calculation#Hit rate"]
pipeline_why: "Onslaught is 20% increased attack/cast speed: it raises hits per second, the Hit rate step (DPS = average damage per hit x hits per second, CalcOffence.lua:3801); it is worth its % only on hit DPS and does not change damage per hit"
pob:
  measured: config
  how: "CalcSetup.lua:82 defines the Onslaught flag behind Condition:Onslaught; CalcPerform.lua:682-711 adds Speed INC (attack and cast) and MovementSpeed INC of floor(20 x (1 + OnslaughtEffect/BuffEffectOnSelf inc)) and, for Silver Flasks only, the flask effect (689-707). Condition:Onslaught is set by ConfigOptions buffOnslaught (1010-1012) or by parsed item/tree lines: 'on Kill' needs KilledRecently (ModCache.lua:22866), 'on Critical Strike' needs CriticalStrike (22864), 'while at maximum Endurance Charges' needs the StatThreshold (22913), 'while Fortified' needs Fortified (22912), 'per Endurance Charge when Hit' needs the Endurance multiplier (22871). Chance (for example 10%) and duration (2 to 20 s) are dropped; 'Vaal skill' and 'Culling Strike' lines set the flag without a condition (ModCache.lua:22858, 22860). Minions: minionBuffOnslaught (ConfigOptions.lua:1016-1018)"
  config:
    - {var: buffOnslaught, default: false, ref: "Modules/ConfigOptions.lua:1010-1012", class: b}
    - {var: conditionKilledRecently, default: false, ref: "Modules/ConfigOptions.lua:1281", class: b}
    - {var: buffFortification, default: false, ref: "Modules/ConfigOptions.lua:1039-1041", class: b}
    - {var: useEnduranceCharges, default: false, ref: "Modules/ConfigOptions.lua:912-914", class: b}
    - {var: conditionUsedWarcryRecently, default: false, ref: "Modules/ConfigOptions.lua:1569", class: b}
  unparsed:
    - "Frenzy of Onslaught (gem): frenzy_consume_charges_to_onslaught_for_ms_per_charge 1000 is not in SkillStatMap.lua (no 'onslaught' key)"
    - "Rotgut: Consumes Frenzy Charges on use, Gain Onslaught for 1/2/3 seconds per Frenzy Charge consumed: ModCache.lua:14776 returns nil for the combined text; the 'per Frenzy Charge consumed' lines (16152-16157) set the flag only with the Multiplier tag"
    - "'grant Onslaught to nearby Enemies on Kill' (Extractor Mentis): parsed as a self flag with a BASE value 5 (ModCache.lua:9883), not a verified enemy effect"
model:
  proposed_kind: onslaught_uptime
  inputs: {from_pob: [Speed, HitSpeed, OnslaughtEffect], from_scenario: ["events per second R (kills/s, crits/s, hits taken/s, warcries per second)", "chance p and duration d of the provider (d = 4 s unless the line says otherwise)"]}
  params: {default_duration_s: 4, speed_pct_base: 20}
  formula: "u = 1-(1-p)^(R*d) for refresh-on-regain chance sources (Onslaught 'can be refreshed from gaining the buff again', wiki rev 1493254); deterministic sources (p = 100%) with gap g between events: u = min(1, d/g). Feed: u >= 0.99 tick buffOnslaught; else blend DPS = u x DPS_on + (1-u) x DPS_off from two PoB runs (never blend EHP). Conditional sources inherit the uptime of their condition (max Endurance Charges -> [[Endurance charges]], Fortified -> [[Fortify]], low life -> scenario)"
  calibration: "no norm found; the wiki gives the 4 s default and the refresh rule only, no kill or crit rate for maps or bosses"
providers:
  - {kind: unique, name: "Ahn's Heritage", slot: shield, role: enables, target: self, text: "You have Onslaught while at maximum Endurance Charges (also -1 maximum Endurance Charges)", source: "Data/Uniques/shield.lua:6-20; ModCache.lua:22913", pob: config}
  - {kind: unique, name: "Daresso's Defiance", slot: body, role: enables, target: self, text: "You gain Onslaught for 5 seconds per Endurance Charge when Hit (variants 3-6); 100% increased Effect of Onslaught on you (variants 5-6); gain an Endurance Charge on Kill, lose all when Hit", source: "Data/Uniques/body.lua:819-840; ModCache.lua:22871-22872", pob: partial}
  - {kind: unique, name: "Kongor's Undying Rage", slot: mace, role: applies, target: self, text: "You gain Onslaught for 4 seconds on Critical Strike (variants 3,4; 2 seconds in variants 1,2)", source: "Data/Uniques/mace.lua:854-855; ModCache.lua:22852, 22864", pob: config, variant: "variants 3,4"}
  - {kind: unique, name: "Perseverance", slot: belt, role: enables, target: self, text: "You have Onslaught while Fortified; Melee Hits which Stun Fortify", source: "Data/Uniques/belt.lua:652-663; ModCache.lua:22912", pob: config}
  - {kind: unique, name: "Dreadbeak", slot: sword, role: enables, target: self, text: "You have Onslaught while on Low Life", source: "Data/Uniques/sword.lua:395; ModCache.lua:22915", pob: config}
  - {kind: unique, name: "Rotgut", slot: flask, role: applies, target: self, text: "Gain Onslaught for 1 (variants 1,2), 2 (variant 3) or 3 (variant 4) seconds per Frenzy Charge consumed on use", source: "Data/Uniques/flask.lua:293-301; ModCache.lua:16152-16158", pob: partial}
  - {kind: unique, name: "Mutewind Pennant", slot: shield, role: applies, target: self, text: "Gain Onslaught for 4 seconds when you Warcry (variants 2-4)", source: "Data/Uniques/shield.lua:409-410", pob: config}
  - {kind: notable, name: "Lead By Example 36655", slot: tree, role: applies, target: self, text: "When you Warcry, you and nearby Allies gain Onslaught for 4 seconds", source: "TreeData/3_29/tree.lua:86432-86441; Modules/ModParser.lua:4175", pob: config}
  - {kind: notable, name: "Graceful Assault 18703 (cluster)", slot: tree, role: scales, target: self, text: "30% increased Effect of Onslaught on you; 10% chance to gain Onslaught for 4 seconds on Kill; 30% increased Armour and Evasion Rating during Onslaught", source: "TreeData/3_29/tree.lua:62294-62306; ModCache.lua:8264, 8172", pob: partial}
  - {kind: ascendancy, name: "Vaal Caress 16994 (Reliquarian option)", slot: tree, role: applies, target: self, text: "You gain Onslaught for 20 seconds on using a Vaal Skill; +2 to Level of all Vaal Skill Gems", source: "TreeData/3_29/tree.lua:19036-19044; ModCache.lua:22858", pob: partial}
  - {kind: unique, name: "Relentless Fury", slot: axe, role: applies, target: self, text: "You gain Onslaught for 3 seconds on Culling Strike; 100% chance to Avoid being Chilled during Onslaught", source: "Data/Uniques/axe.lua:125-126; ModCache.lua:22860-22861", pob: partial}
  - {kind: gem, name: "Frenzy of Onslaught", slot: any, role: applies, target: self, text: "Melee strike that gives a frenzy charge and (per stat) consumes charges for 1000 ms of Onslaught per charge", source: "Data/Skills/act_dex.lua:8272-8321", pob: none}
makes_redundant:
  - {provider: "kill-based Onslaught chances (Graceful Assault 10%)", when: "a deterministic source is worn (Ahn's Heritage at maximum Endurance Charges, Perseverance while Fortified, buffOnslaught ticked for another reason)", why: "Onslaught does not stack, so a second source only adds uptime, not another 20%; extra Onslaught effect lines still add through OnslaughtEffect", source: "wiki Onslaught rev 1493254: 'non-stackable buff'"}
conflicts:
  - {with: "Daresso's Defiance", effect: "you lose all Endurance Charges when Hit while the same item pays Onslaught per charge when Hit, so the Onslaught seconds are worth what the charges were before the hit", source: "Data/Uniques/body.lua:834-838"}
conditions:
  - {text: "default duration of buffs that grant Onslaught is 4 seconds; regaining refreshes it; skill duration modifiers do not change it", source: "wiki Onslaught rev 1493254: 'Buffs that grant Onslaught by default have a 4 second duration. This duration can be refreshed from the gaining the buff again from a buff source. Onslaught duration cannot be modified by skill duration modifiers.' (patch 3.29; page version history: 3.20.0 became a buff)"}
  - {text: "Onslaught Effect and buff effect modifiers scale the 20%; a Silver Flask source also scales with flask effect and duration", source: "wiki Onslaught rev 1493254; PoB CalcPerform.lua:688-707"}
  - {text: "in Ruthless mode Onslaught gives no movement speed", source: "wiki Onslaught rev 1493254 (Ruthless section)"}
  - {text: "a source can state its own duration (2 to 20 s); the 4 s default applies only where it is silent", source: "Data/Uniques/{mace,ring,shield,axe}.lua lines cited in providers; wiki Onslaught rev 1493254"}
uptime:
  Mapping:       {value: model, config: {buffOnslaught: "true only if u >= 0.99 (deterministic sources whose condition is up: Ahn's at max charges, Perseverance while Fortified) else blend", conditionKilledRecently: "true when kill-based sources are assumed; PoB then counts the full 20% and ignores chance and duration"}, reasoning: "kill and crit chance sources with a 4 s window: u = 1-(1-p)^(R*4) with R the kill or crit rate; the rate is a scenario input (not measured here). Condition-based sources inherit their condition's uptime. PoB's own number is the 100% case", source: "wiki Onslaught rev 1493254; Modules/ConfigOptions.lua:1010, 1281; build-strategist.md method"}
  Pinnacle Boss: {value: model, config: {buffOnslaught: "true for conditions that hold on a boss (maximum Endurance Charges via 'count as max', Fortified via melee hits, low life); kill-based sources = none (no kills on a lone boss)"}, reasoning: "crit-based sources use the crit rate on the boss (Chance on hit uptime), when-hit sources use E = 1000/enemySpeed (class b assumption); warcry sources depend on the warcry cooldown (not sourced here)", source: "Modules/ConfigOptions.lua:2318-2320, 2362; mechanics-researcher-uptime.md row 'Onslaught'"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Onslaught (rev 1493254)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Charge (rev 1700592)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcPerform.lua:682-711, CalcSetup.lua:82, ConfigOptions.lua:1010-1018, 1281, ModParser.lua:888, 4019, 4175, 4186", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/ModCache.lua:3689-3692, 8172, 8264, 16152-16161, 22849-22916", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/Uniques/{shield,body,mace,belt,sword,flask,axe}.lua, TreeData/3_29/tree.lua:19036, 62294, 86432, Data/Skills/act_dex.lua:8272", kind: pob, patch: "3.29"}
not_verified:
  - "kill rate, crit rate and hit-taken rate for maps and pinnacle bosses (no source); warcry cooldown for the warcry-based providers"
  - "wiki 4 s default is quoted from a 2013 Daniel_GGG forum post cited by the wiki, not from a patch note; individual unique items state their own durations"
  - "whether the Onslaught flag plus 'Combat' condition applies when buffOnslaught is off but a parsed condition is true (PoB code read, not run)"
  - "current-league availability and the variant that is current for Kongor's Undying Rage, Daresso's Defiance, Rotgut"
  - "Frenzy of Onslaught: effect only read from the stat id in PoB data, wiki gem text not read"
open_questions:
  - "Is the generator allowed to tick buffOnslaught for a kill- or crit-chance source when u >= 0.99, or only for deterministic sources? (suggested: model threshold as in Chance on hit uptime)"
```
