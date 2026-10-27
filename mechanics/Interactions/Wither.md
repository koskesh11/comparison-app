---
type: interaction
status: draft
pob_refs: [multiplierWitheredStackCount, Condition:CanWither, WitherEffectStack, WitherEffect, ChaosDamageTaken]
source: "poewiki Withered rev 1702206, Wither rev 1681920, Buff rev 1701074, Withering Touch Support rev 1682005 (fetched 2026-10-25); PoB 2.67.2 CalcPerform.lua / ConfigOptions.lua / ModParser.lua / Data/Skills; tasks/reports/027-evidence/mechanics-researcher-uptime.md and pob-coverage-auditor-uptime.md"
last_confirmed_patch: "3.29.x"
---

Withered is a stacking debuff on the enemy: 6% increased chaos damage taken per stack, up to 15 stacks, each stack with its own 2 s timer that a new stack does NOT refresh (wiki). PoB takes the stack count only from a config number; it never works out how many stacks your hit rate keeps up, so a chaos build gets 0 stacks (or a hand-set 15) instead of a modelled count. Unlike a plain on/off debuff the uptime is a stack COUNT, S = min(15, chance x hits per s on ONE target x duration); the on-hit chance maths is in [[Chance on hit uptime]]. Hinder from the Wither skill is in [[Maim and Hinder]].

Pipeline: [[Damage calculation#Damage taken]] - Withered adds a ChaosDamageTaken INC term on the enemy, so it only helps chaos damage and only after the stacks exist; the hit that applies a stack does not benefit from it. Whether it also raises chaos damage over time taken is not stated by the wiki (see not_verified).

```interaction
id: wither
mechanic: "Withered: enemy takes 6% increased Chaos Damage per stack (floor(6 x (1 + effect))), up to 15 stacks; every stack has its own 2 s duration (base) that is NOT refreshed by new stacks; stack count = applications in the last 2 s (cap 15); chaos damage only (hits and damage over time)"
family: ailment
target: enemy
related: [chance-on-hit-uptime, maim-hinder, curse-limit, flask-uptime]
pipeline_step: ["Damage calculation#Damage taken"]
pipeline_why: "Withered is a stacking increased-chaos-damage-taken debuff on the enemy (PoB enemyDB ChaosDamageTaken INC per WitheredStack, limit 15; CalcPerform.lua:848), so it acts in the damage-taken step on chaos hits and chaos DoT, after the hit damage is built. The stack count, not a checkbox, is the unknown."
pob:
  measured: config
  how: "The per-stack value is calculated: a source with CanWither sets WitherEffectStack = floor(6 x (1 + WitherEffect inc / 100)) (CalcPerform.lua:2756-2763), and the enemy gets ChaosDamageTaken INC 'effect' x Multiplier WitheredStack, limit 15 (CalcPerform.lua:846-849). The stack COUNT is only the config number multiplierWitheredStackCount (ConfigOptions.lua:1839-1841, shown only when Condition:CanWither is set); default 0 = no effect. No link from hit rate, chance or duration to the stack count (pob-coverage-auditor-uptime.md Q3, CalcPerform.lua:848). Self-withering has its own config (ConfigOptions.lua:1231)."
  config:
    - {var: multiplierWitheredStackCount, default: 0, ref: "Modules/ConfigOptions.lua:1839 (ifFlag Condition:CanWither; count, no placeholder)", class: c}
  unparsed:
    - "Grasping Nightshade: 'Melee Weapon Hits Inflict (2-3) Withered Debuffs for 2 seconds' parses to CanWither (ModParser.lua:4197) but the number of stacks per hit (2-3) is not used; stacks are the config count only"
model:
  proposed_kind: stack_count_uptime
  inputs: {from_pob: [HitSpeed, Speed, SkillTriggerRate, HitChance, WitherEffectStack], from_scenario: ["m = hits per use on ONE target (see projectile-hits-single-target)", "d = 2 s base per stack; Withered you Inflict expires 10% slower (Chaos Damage and Withered Expiry Rate small, tree.lua:41194-41198) gives d / 0.9 by the wiki Buff expiration example", "stacks per application: 1 (Grasping Nightshade 2-3, Unlight Extant up to 15 at once for 5-7 s)"]}
  params: {max_stacks: 15, base_duration_s: 2, base_effect_pct_per_stack: 6}
  formula: "H = m x V (hits per s on the target, all skills that carry the source). Expected stacks from a chance source S = min(15, p x H x s_per_hit x d) (Poisson mean; the cap makes the true mean slightly lower, so use the minimum as an upper bound); an always-on source (100% chance, or a periodic source such as Withering Presence every 1 s) S = min(15, applications per s x d). Per-stack value e = floor(6 x (1 + inc effect)) (CalcPerform.lua:2762). Chaos damage taken inc = floor(S) x e. Feed: tick multiplierWitheredStackCount = floor(S) (PoE rounds down); S >= 14.5 means the cap is reached and ticking 15 is exact. Do not model it as 1-(1-p)^n of one debuff: each stack is a separate debuff."
  calibration: "no norm found; the stack rate of the Wither skill (one stack per channel tick?) is not documented, see not_verified"
providers:
  - {kind: gem, name: "Wither", slot: any, role: applies, target: enemy, text: "channelled spell: hinders (30% reduced movement speed at L1) and inflicts Withered periodically in an area while channelling; 6% chaos damage taken, base stack duration 2 s", source: "Data/Skills/act_int.lua:21232-21275 (chaos_damage_taken_+% 6, active_skill_withered_base_duration_ms 2000, castTime 0.28); wiki Wither rev 1681920", pob: config}
  - {kind: support, name: "Withering Touch Support", slot: any, role: applies, target: enemy, text: "attack skills: 25% chance to inflict Withered on hit for 2 s; 10-29% of physical damage as extra chaos", source: "Data/Skills/sup_dex.lua:4991-5030 (withered_on_hit_chance_% 25, support_withered_base_duration_ms 2000); Data/SkillStatMap.lua:2201-2203; wiki Withering Touch Support rev 1682005", pob: config}
  - {kind: support, name: "Hextoad Support", slot: any, role: applies, target: enemy, text: "hex-linked toad explodes and inflicts Withered on hit, 100% chance for 2 s (triggered skill)", source: "Data/Skills/sup_int.lua:3108-3125 (withered_on_hit_for_2_seconds_%_chance 100); Data/SkillStatMap.lua:2207-2209", pob: config}
  - {kind: gem, name: "Withering Step", slot: any, role: applies, target: enemy, text: "Elusive + Phasing buff: monsters that enter the area are Withered, base stack duration 3 s", source: "Data/Skills/act_dex.lua:17315-17345 (slither_wither_stacks, active_skill_withered_base_duration_ms 3000)", pob: config}
  - {kind: unique, name: "Abhorrent Interrogation", slot: Gloves, role: applies, target: enemy, text: "(20-25)% chance to inflict Withered for 2 seconds on Hit; enemies take increased elemental damage for each Withered inflicted", source: "Data/Uniques/gloves.lua:909-911; Modules/ModParser.lua:4196, 4205", pob: config}
  - {kind: unique, name: "Unlight Extant", slot: Wand, role: applies, target: enemy, text: "Chaos Skills inflict up to 15 Withered Debuffs on Hit for (5-7) seconds; cannot inflict Wither on targets that are not on Full Life", source: "Data/Uniques/wand.lua:483-484; Modules/ModParser.lua:4203", pob: config}
  - {kind: unique, name: "Grasping Nightshade", slot: Tincture, role: applies, target: enemy, text: "Melee Weapon Hits Inflict (2-3) Withered Debuffs for 2 seconds", source: "Data/Uniques/tincture.lua:23; Modules/ModParser.lua:4197", pob: config}
  - {kind: unique, name: "Replica Innsbury Edge", slot: Sword, role: applies, target: enemy, text: "Inflict Withered for 2 seconds on Hit with this Weapon", source: "Data/Uniques/sword.lua:225; Modules/ModParser.lua:4202", pob: config}
  - {kind: unique, name: "Blackflame", slot: Ring, role: scales, target: enemy, text: "Withered does not expire on Enemies Ignited by you (removes the 2 s limit while the enemy burns; the stack cap 15 stays)", source: "Data/Uniques/ring.lua:130", pob: none}
  - {kind: ascendancy, name: "Withering Presence (Occultist)", slot: tree, role: applies, target: enemy, text: "Every second, inflict Withered on nearby Enemies for 15 seconds; 15% more Chaos Damage; +60% Chaos Resistance", source: "TreeData/3_29/tree.lua:44325-44336; Modules/ModParser.lua:2962", pob: config}
  - {kind: ascendancy, name: "Nature's Reprisal (Pathfinder)", slot: tree, role: applies, target: enemy, text: "25% chance to inflict Withered for 2 seconds on Hit; 50% increased Effect of Withered", source: "TreeData/3_29/tree.lua:83772-83780", pob: config}
  - {kind: notable, name: "Corruption / Ghastly Gaze of the Lich", slot: tree, role: scales, target: enemy, text: "20% increased Effect of Withered (Corruption); Unholy Might you grant also applies 20% Increased Effect of Withered (jewel node)", source: "TreeData/3_29/tree.lua:41275, 13315; Modules/ModParser.lua:493, 3081", pob: full}
makes_redundant:
  - {provider: "Several weak Withered sources", when: "one source already keeps 15 stacks (S >= 14.5)", why: "the cap is 15 stacks, extra chance adds nothing; increased Effect of Withered still scales each stack (breakpoints at multiples of about 16.67%)", source: "wiki Withered rev 1702206"}
conflicts:
  - {with: "Wither (skill) and Hinder", effect: "the Hinder part of Wither does not stack (only the strongest Hinder applies); its duration is refreshed while channelling; the Withered stacks are separate", source: "wiki Wither rev 1681920; Hinder rev 1660573"}
  - {with: "Unlight Extant", effect: "applies only to targets on Full Life, so it is a first-hit burst, not a sustained source", source: "Data/Uniques/wand.lua:484"}
conditions:
  - {text: "each Withered stack has its own independent duration (base 2 s) that is NOT refreshed when new stacks are applied; maximum 15 stacks", source: "https://www.poewiki.net/wiki/Withered rev 1702206 (patch 3.29, 3.29.0 only changes the debuff bar display)"}
  - {text: "x% increased Effect of Withered works per stack and only reaches breakpoints at multiples of 16.67% (0% = 6, 17% = 7, 34% = 8, 50% = 9, 100% = 12 per stack); PoB uses floor(6 x (1 + effect/100)), the same table", source: "wiki Withered rev 1702206; Modules/CalcPerform.lua:2762"}
  - {text: "stacks apply from a hit and the hit that applies a stack does not benefit from its own debuff; the status is per target, not global", source: "wiki Hit rev 1650022 (via Chance on hit uptime); Buff rev 1701074"}
  - {text: "Withered you Inflict expires 10% slower (small node): by the wiki Buff expiration example this is equal to more buff duration (50% slower = 2 times slower = 100% more duration)", source: "TreeData/3_29/tree.lua:41194-41198; wiki Buff rev 1701074"}
uptime:
  Mapping:       {value: model, config: {multiplierWitheredStackCount: "model: floor(min(15, p x H x d)) per source; hand-set 15 is exact only for Wither skill channelling or Withering Presence at high hit rate"}, reasoning: "packs: hit rate on one target is high for fast skills, so S often reaches the cap; a slow single-hit skill keeps few stacks (S = p x H x 2 s). Wither skill itself keeps stacks for as long as you channel, which is per-pack short", source: "vault Interactions/Chance on hit uptime; wiki Withered rev 1702206"}
  Pinnacle Boss: {value: model, config: {multiplierWitheredStackCount: "model: same formula; phases without hits drop stacks within 2 s (no refresh)"}, reasoning: "one target, so m and V as in Chance on hit uptime; the 2 s per-stack life without refresh makes the count fall to 0 about 2 s after the last application, unlike a refreshed debuff", source: "wiki Withered rev 1702206; Buff rev 1701074 (debuffs on untargetable bosses are hidden, not removed, and expire normally)"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Withered (rev 1702206)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Wither (rev 1681920)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Buff (rev 1701074)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Withering_Touch_Support (rev 1682005)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcPerform.lua:846-849,2756-2763; Modules/ConfigOptions.lua:1231,1839; Modules/ModParser.lua:493,2962,4196-4205; Data/SkillStatMap.lua:2201-2209", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/mechanics-researcher-uptime.md and pob-coverage-auditor-uptime.md (rows Withered, Q3)", kind: discovery, patch: "3.29"}
not_verified:
  - "how many Withered stacks the Wither skill adds per channel tick (wiki says 'periodically'; PoB castTime 0.28 s and base_skill_effect_duration 500 ms are PoB data, no stack rate); if it is one stack per 0.28 s the steady state would be about 7 stacks at base speed (hypothesis, not tested)"
  - "how Withered's ChaosDamageTaken INC combines with other increased chaos damage taken and with the Wither-style 'more' sources in the enemy damage-taken bucket (CalcPerform.lua:848 shows INC under ChaosDamageTaken; the final combination in CalcOffence was not traced)"
  - "whether Blackflame's 'does not expire on Ignited enemies' keeps all stacks or only the old ones (PoB data has no parse for it)"
  - "whether the Chaos Mastery option '5% chance when you inflict Withered to inflict up to 15 Withered Debuffs instead' (tree.lua:41355-41358) is parsed (not looked up in ModParser)"
  - "whether Withered raises chaos damage over time taken (wiki says 'chaos damage taken'; PoB uses the ChaosDamageTaken INC, which PoB applies to hits and DoT alike? not traced)"
  - "whether pinnacle bosses or any boss phase are immune to or reduce Withered (no source found)"
  - "the S = min(15, p x H x d) estimate is a Poisson mean, not tested in game"
open_questions:
  - "Is a hand-set 15 stacks acceptable for a Wither-skill channel build on bosses, or should the stack count be modelled from the channel tick rate once that is measured?"
```
