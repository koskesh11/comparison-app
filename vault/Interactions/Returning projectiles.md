---
type: interaction
status: draft
pob_refs: [ProjectileCount, ReturningProjectile, PierceAllTargets, ProjectileCannotReturn]
source: "wiki Return rev 1660588, Projectile rev 1642414, Nimis rev 1647792, Returning Projectiles Support rev 1681728; Mark_GGG forum 3284453 (2022-06-20); PoB 2.67.2 sup_dex.lua, SkillStatMap.lua, ModCache.lua; user statement 2026-10-24"
last_confirmed_patch: "3.29.x"
---

Nimis and the Returning Projectiles support make projectiles come back. User chose reading B on 2026-10-25 (reading A rejected). PoB maps none of it: the return hit is not counted and neither is the support's damage penalty, so in PoB the support is pure cost (+50% cost) and a PoB DPS sort always drops it.

Winter Orb and Forbidden Rite cannot return (they do not collide with enemies), so this mechanic never applies to the Worb or FR seeds. Overlap of the outbound projectiles: see [[Projectiles hitting a single target]].

```interaction
id: returning-projectiles
mechanic: "Projectiles that collide return once; the return pass may hit the same target again. Reading A (rejected by the user 2026-10-25, was the user's first statement): point blank each projectile hits out and back (~2x), even in a circle. Reading B (wiki): one collision out plus one back per simultaneous set, none if the projectile returned directly from that enemy; AoE explosions are not limited"
family: projectile
target: enemy
related: [projectile-hits-single-target]
pob:
  measured: none
  how: "no modelling: grep of Modules/ and Classes/ finds no handling; 'Projectiles Return to you' stored unparsed (ModCache.lua:18705-18707); SkillStatMap.lua has no entry for support_return_returning_projectiles_damage_+%_final, so the 66-70% less damage is not applied either; Condition ReturningProjectile is set only by Venom Gyre part 2 (act_dex.lua:16306); net PoB effect of the support = +50% cost multiplier (sup_dex.lua:3909-3938)"
  config: []
  unparsed:
    - "Nimis: Projectiles Return to you"
    - "Nimis: Projectiles are fired in random directions"
    - "Shrapnel Specialist 57175: Projectiles have 50% chance to Return to you (ModCache.lua:18764 left unparsed)"
    - "Vengeant Cascade 57006: Returning Projectiles have 150% increased Speed (ModCache.lua:19805 unparsed)"
model:
  proposed_kind: returning_projectile_hits
  inputs:
    from_pob: [ProjectileCount, skillPart, count, "support level (Returning Projectiles)", "PierceCount/ChainCount/ForkCount on the outbound path"]
    from_pob_config: [enemyRadius]
    from_scenario: [distance_u, sequential_sets]
    from_model: aoe_hit_fraction
  params:
    reading: B             # user 2026-10-25. Reading A (~2x at point blank, even in a circle) was rejected by the user 2026-10-25 (it was the user's first statement); kept only as described history in the mechanic text
    return_less: {support_lvl1: 0.70, support_lvl20: 0.66, nimis: 0.0}
    aoe_hit_fraction: 0.6  # explosions only; user-verified fraction of vault Models/Projectiles hitting a single target.md
  formula: "q_dir = 1 if distance_u <= enemy_radius_u else asin(enemy_radius_u / distance_u) / pi (random direction, Nimis). A: out_hits = back_hits = floor(P*q_dir). B: out_hits = sets * (1 if 1-(1-q_dir)^P_per_set >= 0.5 else 0); back_hits = sets * (0 if the outbound projectile returned directly from the target else 1); explosions = floor(P*aoe_hit_fraction*explosions_per_projectile), not shotgun-limited (explosions_per_projectile 1 UNVERIFIED). dps_mult = floor_2dp(out_hits + back_hits*(1-return_less)); feed: multiply only that skill's share of FullDPS by dps_mult / pob_count (engine/models.py:79-85 risk)"
  calibration: "no norm found for either reading; user norm = reading A; wiki/GGG text = reading B. Example (formula only, no sample build has Nimis): P=5, point blank, support lvl 20: A -> 6.70x, B -> 1.00x; Nimis with outbound pierce, B -> 2.00x"
providers:
  - {kind: unique, name: "Nimis", slot: ring, role: enables, target: self, text: "(25-35)% increased Projectile Damage / Projectiles Return to you / Projectiles are fired in random directions; no pierce, no less-damage penalty; ignores Volley/Power Siphon direction", source: "PoB Data/Uniques/ring.lua:747-756; wiki Nimis rev 1647792 (3.20.0)", pob: none}
  - {kind: support, name: "Returning Projectiles (support)", slot: any, role: enables, target: self, text: "Projectiles Return; pierce all targets while returning; 66% less Damage with Hits and Ailments while Returning at lvl 20 (70% at lvl 1); +50% cost; excludes ProjectileCannotReturn", source: "PoB Data/Skills/sup_dex.lua:3909-3938; wiki rev 1681728 (3.26.0 70-66%, 3.23.0 ailments fix)", pob: partial}
  - {kind: foulborn, name: "Xoph's Inception (Foulborn)", slot: weapon, role: enables, target: self, variant: "replaces the line 'Projectiles Pierce all Burning Enemies'", text: "Socketed Gems are Supported by Level 20 Returning Projectiles (carries the penalty)", source: "PoB Data/ModFoulbornMap.jsonc:249; original Data/Uniques/bow.lua:578", pob: partial}
  - {kind: ascendancy, name: "Shrapnel Specialist 57175 (Saboteur)", slot: any, role: applies, target: self, text: "Projectiles have 50% chance to Return to you / Projectiles are fired in random directions", source: "PoB TreeData/3_29/tree.lua:84486; ModCache.lua:18764", pob: none}
  - {kind: notable, name: "Vengeant Cascade 57006", slot: any, role: scales, target: self, text: "Returning Projectiles have 150% increased Speed", source: "PoB TreeData/3_29/tree.lua:82575; ModCache.lua:19805", pob: none}
  - {kind: notable, name: "Selective Precision 24358", slot: any, role: applies, target: self, text: "First and Final shots of Barrage sequences fire Projectiles that Return to you (Barrage only)", source: "PoB TreeData/3_29/tree.lua:64140", pob: none}
  - {kind: unique, name: "Reach of the Council", slot: bow, role: applies, target: self, text: "Arrows fired from the third firing points Return to you (variants 5, 6)", source: "PoB Data/Uniques/bow.lua:420", pob: none}
  - {kind: unique, name: "Relic of the Cycle", slot: bow, role: applies, target: self, text: "Projectiles Return to you from final target (Race Events, not normally obtainable)", source: "PoB Data/Uniques/race.lua:50", pob: none}
  - {kind: gem, name: "Venom Gyre", slot: any, role: applies, target: self, text: "returns natively: projectiles_return + always_pierce + 75% less damage while returning (this stat IS mapped in PoB)", source: "PoB Data/Skills/act_dex.lua:16281; SkillStatMap.lua:1442-1444", pob: full}
makes_redundant:
  - {provider: "Returning Projectiles (support)", when: "Nimis equipped", why: "'A projectile can only return once' and both set projectiles_return; Nimis gives 100% damage returns. Not neutral if linked anyway: pierce on return, 66% less return damage at lvl 20, +50% cost", source: "wiki Return rev 1660588; PoB sup_dex.lua:3909-3938 (inference from same stat id, not one GGG sentence)"}
conflicts:
  - {with: "Winter Orb, Forbidden Rite, Concoction skills, rain-type skills, Spark, Twister, Splitting Steel, Tornado Shot secondary", effect: "cannot return (no collision with enemies / ground-ending); PoB over-accepts Winter Orb and Forbidden Rite for the support (only Splitting Steel carries ProjectileCannotReturn, act_dex.lua:15535, 15615)", source: "wiki Return rev 1660588; wiki Winter Orb; PoB Data/Skills/sup_dex.lua:3916"}
  - {with: "Volley / Power Siphon direction effects", effect: "Nimis 'fired in random directions' overrides them (not Arrow Nova payload location)", source: "wiki Nimis rev 1647792"}
  - {with: "projectile with Chain/Fork left", effect: "chains or forks instead of returning; priority Split > Pierce > Fork > Chain > Return; against a lone enemy it returns immediately", source: "wiki Projectile rev 1642414, Return rev 1660588"}
  - {with: "Mystic Refractor", effect: "'Projectiles cannot continue after colliding with targets' - whether this also stops a return after a collision is NOT verified", source: "PoB Data/Uniques/wand.lua:218"}
conditions:
  - {text: "a projectile can only return once", source: "wiki Return rev 1660588"}
  - {text: "returning projectiles can collide with a previously hit target unless the projectile returned directly from it; of a simultaneous set only one can collide with the same target", source: "wiki Return rev 1660588; Projectile rev 1642414"}
  - {text: "returning does not reset travel distance/duration; typical projectiles travel on 15 m then return", source: "wiki Return rev 1660588"}
uptime:
  Mapping:       {value: partial, config: {}, reasoning: "skill-dependent; pack geometry not modelled", source: "build-strategist.md; mechanics-modeler.md"}
  Pinnacle Boss: {value: model, config: {reading: B}, reasoning: "reading B chosen by the user 2026-10-25 (wiki: shotgun rule per cast, no re-hit when returning from the target): ~1x at point blank, ~2x with outbound pierce; AoE explosions not limited; PoB models neither the extra hit nor the support penalty; explosion clause (B) is not shotgun-limited", source: "wiki Projectile rev 1642414 / Return rev 1660588; user statement 2026-10-24"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Return (rev 1660588, 2026-07-07)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Projectile (rev 1642414, 2026-04-05)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Nimis (rev 1647792)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Returning_Projectiles_Support (rev 1681728)", kind: wiki, patch: "3.29"}
  - {ref: "pathofexile.com forum thread 3284453 (Mark_GGG, 2022-06-20, before the 3.21 return rework): if the target is in the way one returning projectile can hit it, the others will not", kind: forum, patch: "3.20-3.21"}
  - {ref: "pathofexile.com forum thread 3510678 (2024-04, player thread, non-authoritative): 'with Nimis my dps is definitely more than an extra hit' (Ethereal Knives)", kind: discovery, patch: "3.24"}
  - {ref: "Maxroll Fireball CoC Deadeye guide (3.20-3.22, archived, search snippet only): returning AoE fireballs overlap on a boss", kind: discovery, patch: "3.20-3.22"}
  - {ref: "PoB Data/Skills/sup_dex.lua:3909-3938; Data/SkillStatMap.lua:1442-1447; Data/ModCache.lua:18705-18707", kind: pob, patch: "3.29"}
  - {ref: "user answers U1-U6, tasks/027-interaction-database.md log", kind: user, patch: "3.29"}
not_verified:
  - "3.29 in-game behaviour of Nimis on a boss at point blank (no GGG statement after the 3.21 rework; a test or dev statement is needed)"
  - "whether the random-direction circle changes grouping into simultaneous sets"
  - "whether the Discord source of 'cannot be hit by other returning projectiles in the same set' is accurate (unofficial)"
  - "explosions per projectile with return (3.21: Fireball-type explode only after returning)"
  - "whether the support's less damage applies to Nimis returns when both are linked (stat text says yes, no test)"
  - "Relic of the Cycle obtainability (race-only)"
  - "Mystic Refractor 'Projectiles cannot continue after colliding with targets' (wand.lua:218): whether it also stops a return after a collision"
open_questions: []
```
