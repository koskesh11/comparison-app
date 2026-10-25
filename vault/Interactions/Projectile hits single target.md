---
type: interaction
status: draft
pob_refs: [ProjectileCount, AreaOfEffectRadius, skillPart, count, enemyRadius, ShrapnelBallistaProjectileOverlap, FullDPS]
source: "vault Models (user-verified 0.6, Winter Orb overlap, Fireball overlap); wiki Projectile rev 1642414 (shotgun prevention); PoB 2.67.2 CalcOffence/ConfigOptions/act_int.lua; tree-ascendancy-analyst"
last_confirmed_patch: "3.29.x"
---

Several projectiles of one cast reach one enemy, but PoB counts one hit (Winter Orb: one per volley, Forbidden Rite part 1: one projectile) or multiplies by a hand-set count. How many really land is geometry plus shotgun prevention (only one collision per simultaneous set; explosions are not limited). This decides how much a projectile-count source is worth on a boss.

Pipeline: none - no damage step: it sets how many hits land on one boss per cast, a hit-count multiplier outside the per-hit order; the per-hit chain in PoB is unchanged and the count is a hand-set input

The numbers live in existing vault models, not here: [[Projectiles hitting a single target]] (user-verified 0.6 hit fraction, Forbidden Rite + Greater Volley), [[Winter Orb projectile overlap]] (line overlap, count 5 is hand-set), [[Fireball explosion overlap]]. Use those; this note only records providers, PoB coverage and uptime.

```interaction
id: projectile-hits-single-target
mechanic: "Of the projectiles of one cast, only some hit a single boss: collisions are capped by shotgun prevention, explosions overlap by geometry; user-verified ~60% of projectiles hit for Forbidden Rite / Fireball style AoE explosions"
family: projectile
pipeline_step: []
pipeline_why: "no damage step: it sets how many hits land on one boss per cast, a hit-count multiplier outside the per-hit order; the per-hit chain in PoB is unchanged and the count is a hand-set input"
target: enemy
related: [returning-projectiles, coc-trigger]
pob:
  measured: partial
  how: "no generic overlap model; SequentialProjectiles sets dpsMultiplier = ProjectileCount (CalcOffence.lua:803-806); config ShrapnelBallistaProjectileOverlap for one skill (ConfigOptions.lua:627); Winter Orb = one hit per volley (act_int.lua:20963-21010, CalcActiveSkill.lua:636-655); Forbidden Rite part 2 = ProjectileCount + 1 (act_int.lua:7414-7416), ProjectileCount shown but not multiplied (CalcOffence.lua:1089-1096)"
  config:
    - {var: enemyRadius, default: "preset Medium 3 u", ref: "ConfigOptions.lua:777-800", class: b}
    - {var: ShrapnelBallistaProjectileOverlap, default: 1, ref: "ConfigOptions.lua:627", class: c}
    - {var: "count (gem count, hand-set, e.g. Winter Orb 5)", default: 1, ref: "Modules/Calcs.lua:254-255", class: c}
  unparsed: []
model:
  proposed_kind: parallel_projectile_single_target_hits
  inputs: {from_pob: [ProjectileCount, AreaOfEffectRadius, skillPart, count], from_scenario: [enemy_radius_u]}
  params: {hit_fraction: 0.6}
  formula: "see vault/Models/Projectiles hitting a single target.md (hit_fraction 0.6 user-verified 2026-10-22; Forbidden Rite v4: 6 x 0.6 = 3.6, golden 4 rounded down) and vault/Models/Winter Orb projectile overlap.md (golden 4 hits at count 5)"
  calibration: "user-verified 0.6 (blind-test reveal 2026-10-22); Winter Orb spacing 1.4 m calibrated, not measured"
providers:
  - {kind: gem, name: "Greater Volley (support)", slot: any, role: scales, target: enemy, text: "extra projectiles parallel to the main one; Forbidden Rite explosions land in a line", source: "PoB Data/Skills/sup_dex.lua:2285-2286 (via vault Models/Projectiles hitting a single target)", pob: partial}
  - {kind: gem, name: "Forbidden Rite", slot: any, role: abuses, target: enemy, text: "projectiles only explode at end of path; PoB part 2 multiplies by ProjectileCount + 1", source: "PoB Data/Skills/act_int.lua:7414-7416, 7625", pob: partial}
  - {kind: gem, name: "Winter Orb", slot: any, role: abuses, target: enemy, text: "3 projectiles at gem level 20+ land in a rough line and explode; PoB counts one hit per volley", source: "PoB Data/Skills/act_int.lua:20963-21010; vault Models/Winter Orb projectile overlap", pob: partial}
  - {kind: unique, name: "Mystic Refractor", slot: "Weapon 1 (wand)", role: scales, target: self, text: "Skills fire (2-3) additional Projectiles; Projectiles cannot continue after colliding with targets (Pagan Wand, Variant Current; Worb sample roll 3)", source: "PoB Data/Uniques/wand.lua:214,218", pob: full}
  - {kind: ascendancy, name: "Ascendant/Deadeye 34567", slot: any, role: scales, target: self, text: "Skills fire an additional Projectile", source: "PoB TreeData/3_29/tree.lua:20154", pob: full}
  - {kind: notable, name: "Split Shot 7069", slot: any, role: scales, target: self, text: "50% additional Projectile when Forking", source: "PoB TreeData/3_29/tree.lua:82616", pob: full}
  - {kind: keystone, name: "Kineticism 40561", slot: any, role: blocks, target: self, text: "Projectiles cannot Pierce, Fork or Chain", source: "PoB TreeData/3_29/tree.lua:85655", pob: full}
  - {kind: keystone, name: "Point Blank 42178", slot: any, role: blocks, target: self, text: "Projectile ATTACK hits deal more damage at start of movement; no effect on spells such as Winter Orb", source: "PoB TreeData/3_29/tree.lua:68890", pob: full}
makes_redundant: []
conflicts: []
conditions:
  - {text: "valid for a lone target with the cursor or CoC target on the boss; adds nearby make projectiles pick other enemies (Winter Orb)", source: "vault Models/Winter Orb projectile overlap.md; wiki Forbidden Rite (via vault model)"}
  - {text: "shotgun prevention: only one of simultaneously created projectiles collides with the same target; sequential projectiles (Ice Spear, Barrage) are unaffected; it only limits collisions, not all hits (explosions)", source: "wiki Projectile rev 1642414"}
uptime:
  Mapping:       {value: low, config: {}, reasoning: "packs spread the hits (strategist: low-partial); overlap on one target matters for big enemies only; use the geometry models, not PoB", source: "build-strategist.md; vault Models"}
  Pinnacle Boss: {value: model, config: {count: "model: hit count of the vault model (golden 4, rounded down)"}, reasoning: "overlap on the lone boss is the whole question; the model replaces the hand-set gem count", source: "vault Models/Projectiles hitting a single target.md; Winter Orb projectile overlap.md"}
seeds: [Worb, FR, EK]
sources:
  - {ref: "https://www.poewiki.net/wiki/Projectile (rev 1642414)", kind: wiki, patch: "3.29"}
  - {ref: "vault/Models/Projectiles hitting a single target.md (user-verified 0.6)", kind: discovery, patch: "3.29"}
  - {ref: "Modules/CalcOffence.lua:803-806, 1089-1096; Modules/ConfigOptions.lua:627, 777-802", kind: pob, patch: "3.29"}
not_verified:
  - "EK (Ethereal Knives) projectile overlap: no model exists yet"
  - "tree-ascendancy-analyst found no tree provider for single-target overlap itself (geometry only)"
  - "Winter Orb spacing 1.4 m is calibrated, not measured; Forbidden Rite x_dist unit unverified (see vault model)"
open_questions: []
```
