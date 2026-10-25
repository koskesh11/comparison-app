---
type: interaction
status: draft
pob_refs: [LifeLeech, LifeLeechRate, LifeLeechGainRate, LifeLeechInstances, LifeLeechDuration, MaxLifeLeechInstance, MaxLifeLeechRate, EnergyShieldLeechRate, ManaLeechRate, InstantLifeLeech, CanLeechLifeOnFullLife, Condition:Leeching, conditionLeeching, LeechRateBase]
source: "wiki Leech rev 1642429, Recovery rev 1618351; PoB 2.67.2 CalcOffence.lua, CalcDefence.lua, CalcPerform.lua, CalcSetup.lua, ConfigOptions.lua, ModParser.lua, Data.lua, Data/Misc.lua, Data/Skills, TreeData/3_29/tree.lua, Data/Uniques; mechanics-researcher-receiving-defences.md, pob-coverage-auditor-calc-order.md (task 027)"
last_confirmed_patch: "3.29.x"
---

Leech turns damage dealt by hits into life, mana or energy shield recovered over time: each hit makes an instance worth the hit's damage times the leech percent, at most 10% of the maximum pool per instance, recovered at 2% of the pool per second per instance, all instances together capped at 20% of the pool per second (energy shield 10%). PoB computes the instance size, duration and the capped rate from the hit average and the hit rate, but it does not drop leech at full life, does not count leech in effective HP, and sets the "while Leeching" condition only from a config tick. So the rate is a potential, not a measured recovery.

Pipeline: [[Receiving damage#Recovery]] and [[Defences#Recovery and leech]] - leech is recovery that works over time and is calculated before damage over time loss in the same frame; it is not a mitigation layer and PoB's TotalEHP leaves it out, so judge it by duration against the incoming damage instead of by pool size.

```interaction
id: leech
mechanic: "Leech: each hit that deals damage creates an independent instance = damage x leech%, max 10% of the pool per instance, 2% of the pool per second per instance, total 20% of the pool per second (ES 10%); instances are discarded at full unreserved life unless an overleech source exists; PoB computes size, duration and capped rate but not the full-life discard, not EHP, and sets 'while Leeching' only from config"
family: resource
target: self
related: [onslaught, chance-on-hit-uptime, fight-length]
pipeline_step: ["Receiving damage#Recovery", "Defences#Recovery and leech"]
pipeline_why: "Leech is over-time recovery (wiki Recovery rev 1618351: recovery is calculated before DoT loss in the same frame), capped per instance and in total; PoB shows the rate (CalcOffence.lua:4101-4140) but TotalEHP ignores it (CalcDefence.lua:2904-2966), so it is judged against damage by duration, not as mitigation"
pob:
  measured: partial
  how: "Offence side CalcOffence.lua:3389-3435 and 3613-3689: per damage type leech% (DamageLifeLeech etc.) x damageTypeHitAvg (post-mitigation hit average) summed, capped per instance by MaxLifeLeechInstance = Life x 10% (CalcDefence.lua:1220, Data/Misc.lua:126-128); instance duration = amount / pool / LeechRateBase 0.02 (CalcOffence.lua:3721-3727, Data.lua:260), instances = duration x hitRate; LifeLeechRate = instances x Life x 0.02 x LifeLeechRate mods (4101-4102) limited by MaxLifeLeechRate = Life x 20% (CalcSetup.lua:47, CalcDefence.lua:1221-1227; ES 10% Misc.lua:111, mana 20% Misc.lua:110), times the recovery rate mod (4124-4129); instant leech portions 3729-3748; LifeLeechGainRate adds life on hit (4134-4140). Not modelled: discard at full unreserved life (only the flag CanLeechLifeOnFullLife, ModParser.lua:3008-3009, sets Leeching and LeechingLife, CalcPerform.lua:906-913), leech from damage over time, overkill, leech reaching minions or totems. Leech is not in EHP/TotalEHP (pob-coverage-auditor-calc-order.md R9)"
  config:
    - {var: conditionLeeching, default: false, ref: "Modules/ConfigOptions.lua:1079-1081", class: b}
    - {var: conditionLeechingLife, default: false, ref: "Modules/ConfigOptions.lua:1082-1085", class: b}
    - {var: conditionLeechingEnergyShield, default: false, ref: "Modules/ConfigOptions.lua:1086-1089", class: b}
    - {var: conditionLeechingMana, default: false, ref: "Modules/ConfigOptions.lua:1090-1093", class: b}
  unparsed:
    - "Tanu Ahi: 10% chance to gain Onslaught for 4 Seconds when Leech is removed by Filling Unreserved Life: ModCache.lua:3691 sets an unconditional Onslaught flag with leftover text"
    - "Vaal Pact keystone second line 'Cannot Recover Life other than from Leech' is read only through CannotRecoverLifeOutsideLeech (CalcOffence.lua:3764, 3778)"
model:
  proposed_kind: leech_recovery
  inputs: {from_pob: [LifeLeechInstances, LifeLeechDuration, LifeLeechRate, MaxLifeLeechRate, Life, HitSpeed], from_scenario: ["fraction of the time the pool is below full (leech is discarded at full unreserved life without an overleech source)", "incoming damage per second to compare against (see [[Receiving damage#Damage over time taken]])"]}
  params: {instance_cap_pct: 10, instance_rate_pct_per_s: 2, total_rate_cap_pct_life_mana: 20, total_rate_cap_pct_es: 10}
  formula: "per instance: amount = min(hit x leech%, 10% x pool); duration = amount / (2% x pool) seconds (max 5 s); recovery per second = min(sum over active instances of 2% x pool, 20% x pool) x recovery rate mods; without an overleech source multiply the time-averaged recovery by the share of time the pool is below full. PoB already gives the first parts; add only the full-life share (a scenario input)"
  calibration: "wiki worked examples: 1000 life, 1% leech, one 4000 damage hit = 40 over 2 s; one 40000 damage hit = capped at 100 over 5 s; 25 capped instances want 2500 per second but are limited to 200 per second (Leech rev 1642429)"
providers:
  - {kind: support, name: "Life Leech Support", slot: any, role: applies, target: self, text: "Supports any skill that hits enemies, causing those hits to leech life based on damage dealt; L1 life_leech_from_any_damage_permyriad 200 = 2% of Damage Leeched as Life", source: "Data/Skills/sup_str.lua:3445-3462", pob: full}
  - {kind: support, name: "Energy Leech Support", slot: any, role: applies, target: self, text: "energy_shield_leech_from_any_damage_permyriad; damage while on full Energy Shield (support_energy_shield_leech_damage_+%_on_full_energy_shield_final)", source: "Data/Skills/sup_int.lua:2214-2236", pob: full}
  - {kind: support, name: "Mana Leech Support", slot: any, role: applies, target: self, text: "leeches mana from damage dealt", source: "Data/Skills/sup_dex.lua:2830", pob: full}
  - {kind: ascendancy, name: "Trickster (Ascendant option) 6778", slot: tree, role: applies, target: self, text: "2% of Damage Leeched as Energy Shield; Prevent +6% of Suppressed Spell Damage while on Full Energy Shield; 2% more Damage for each different type of Mastery you have Allocated", source: "TreeData/3_29/tree.lua:20526-20537", pob: full}
  - {kind: ascendancy, name: "Slayer (Ascendant option) 43195", slot: tree, role: enables, target: self, text: "Culling Strike; Life Leech effects are not removed when Unreserved Life is Filled; 30% increased Area of Effect if you've Killed Recently", source: "TreeData/3_29/tree.lua:18212-18221; Modules/ModParser.lua:3008-3009", pob: partial}
  - {kind: ascendancy, name: "Brutal Fervour 10143 (Slayer)", slot: tree, role: scales, target: self, text: "100% increased Maximum Recovery per Life Leech (20% per instance, 10 s per instance); Life Leech effects are not removed when Unreserved Life is Filled; 10% reduced Damage taken while Leeching", source: "TreeData/3_29/tree.lua:59370-59380", pob: partial}
  - {kind: keystone, name: "Vaal Pact 10808", slot: tree, role: abuses, target: self, text: "Life Leech from Melee Damage is Instant; Cannot Recover Life other than from Leech", source: "TreeData/3_29/tree.lua:60119-60126; Modules/ModParser.lua:3179; CalcOffence.lua:3764", pob: partial}
  - {kind: notable, name: "Energy Shield Leech 51219 (small passive)", slot: tree, role: applies, target: self, text: "0.3% of Spell Damage Leeched as Energy Shield (bigger nodes of the cluster give 0.8%)", source: "TreeData/3_29/tree.lua:62761-62766, 62809", pob: full}
  - {kind: unique, name: "Tanu Ahi", slot: gloves, role: sustains, target: self, text: "10% chance to gain Onslaught for 4 Seconds when Leech is removed by Filling Unreserved Life", source: "Data/Uniques/gloves.lua:684; ModCache.lua:3690-3691", pob: partial}
makes_redundant:
  - {provider: "more instances (higher hit rate or more leech%)", when: "the total rate cap of 20% of the pool per second (ES 10%) is already reached", why: "the wiki cap means extra instances add nothing once 10 full instances are active; raise the cap lines instead", source: "wiki Leech rev 1642429: 'The total recovery rate of all life leech instances is limited to 20% of maximum life or mana per second (10% for energy shield).'"}
conflicts:
  - {with: "Vaal Pact", effect: "Cannot Recover Life other than from Leech: regeneration, flasks and life on hit give nothing, so leech is the only life source", source: "TreeData/3_29/tree.lua:60125"}
conditions:
  - {text: "instance size and rate: each instance recovers damage x leech% up to 10% of the maximum pool, at 2% of the pool per second (maximum duration 5 s); all instances stack and apply simultaneously; total recovery rate limited to 20% of the pool per second (ES 10%)", source: "wiki Leech rev 1642429 (rendered; patch 3.29, caps added 3.6.0): 'Each instance Recovers at a rate of 2% of maximum life per second.' / 'The total recovery rate of all life leech instances is limited to 20% of maximum life or mana per second (10% for energy shield).'"}
  - {text: "leech is based on the damage taken by the enemy, not the life removed (overkill counts); leech needs a hit, so damage over time creates no instance; skills used by minions, totems and other proxies leech to that entity", source: "wiki Leech rev 1642429: 'Leech is based on the damage taken by the enemy, not the amount of life removed.' / 'Whenever a character with some source of leech hits a monster, a leech instance is created.'"}
  - {text: "all life leech instances are discarded as soon as the character reaches full unreserved life, unless an overleech source exists (Slayer options, Brutal Fervour, Immortal Ambition, Offering to the Serpent, Soul Drinker, Essentia Sanguis, Petrified Blood)", source: "wiki Leech rev 1642429: 'Additionally all instances of life leech are discarded as soon as the character reaches full unreserved life.'"}
  - {text: "modifiers to 'total Recovery per second from Life Leech' change how fast the cap is reached and do not shorten an instance; 'Maximum Recovery per Life Leech' lengthens it; instant leech is capped by the same per-instance maximum", source: "wiki Leech rev 1642429; PoB CalcOffence.lua:3729-3748, 4101-4129"}
  - {text: "modifiers to recovery rate multiply the pooled over-time recovery after the leech cap (PoB: min(rate, cap) x recovery rate mod)", source: "wiki Recovery rev 1618351: 'They are also unaffected by caps on maximum recovery for specific mechanics, like leech.'; PoB CalcOffence.lua:4124"}
  - {text: "version history: 3.6.0 added the 10% per instance cap and Energy Shield leech; 3.26.0 life and mana leech mods on gear roll as suffixes and weapon physical attack leech mods were rescaled (2 to 4.5% life); 2.0.0 stacking instances, 2% per second, 20% total", source: "wiki Leech rev 1642429 version history (3.26.0, 3.6.0, 2.0.0)"}
uptime:
  Mapping:       {value: partial, config: {conditionLeechingLife: "true only where a Slayer/Brutal Fervour/Immortal Ambition overleech source exists or a 'while Leeching' mod is needed", conditionLeeching: "same"}, reasoning: "leech is discarded at full unreserved life and maps keep many builds at full life; PoB's LifeLeechRate is the capped potential, valid while the pool is below full. Rate needs hits that deal damage (not DoT-only builds)", source: "wiki Leech rev 1642429; Modules/CalcOffence.lua:4101-4140, CalcPerform.lua:906-913"}
  Pinnacle Boss: {value: pob, config: {conditionLeechingLife: "true if the build keeps a leech source active while the boss damages you"}, reasoning: "bosses lower the pool below full, so instances persist; use PoB's LifeLeechRate / EnergyShieldLeechRate (hit rate x average hit); phases without hits give no instances and the leech already created lasts at most 5 s (10 s with Brutal Fervour)", source: "wiki Leech rev 1642429; Modules/CalcOffence.lua:4101-4140; tree.lua:59377"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Leech (rev 1642429)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Recovery (rev 1618351)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcOffence.lua:3389-3435, 3613-3689, 3721-3748, 4101-4140, CalcDefence.lua:1220-1250, CalcSetup.lua:47, CalcPerform.lua:906-913, ConfigOptions.lua:1079-1096, ModParser.lua:574-578, 1733-1736, 2316, 3008-3009, 3179, Data.lua:260, Data/Misc.lua:109-128", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/Skills/sup_str.lua:3445, sup_int.lua:2214, sup_dex.lua:2830, TreeData/3_29/tree.lua:18212, 20526, 59370, 60119, 62761, Data/Uniques/gloves.lua:684", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/mechanics-researcher-receiving-defences.md (R9), pob-coverage-auditor-calc-order.md (R9)", kind: discovery, patch: "3.29"}
not_verified:
  - "the wiki worked examples and caps are rendered values of template variables (#var 10 / 2 / 20); the raw wikitext holds the variables, not the numbers"
  - "PoB's use of minions or totems with leech (wiki: leech goes to the proxy) was not traced"
  - "Chaos Inoculation builds (1 maximum life) were not checked for life leech; only the Energy Leech / ES leech route is listed"
  - "current-league obtainability of Tanu Ahi and the Ascendant options (not checked)"
  - "Ghost Reaver keystone and the Arcane Surge leech node in the tree were not read (ModParser.lua:2316 only)"
  - "which of EK, Worb, FR runs a leech source: none read"
open_questions:
  - "Should the generator treat leech as potential recovery (PoB number) and add the full-life share as a scenario input, or ignore leech for survivability until EHP includes recovery? (suggested: potential with a full-life share, shown separately from EHP)"
```
