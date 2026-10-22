---
type: model
status: draft
pob_refs: [Fireball, SupportGreaterMultipleProjectiles]
superseded_by_pob:
source: https://www.poewiki.net/wiki/Fireball
last_confirmed_patch: "?"
---

```model
applies_to: { skill: Fireball, part: Explosion }
inputs:
  from_pob: [AreaOfEffectRadius, ProjectileCount, enemyRadius]
  from_vault: { gmp_spread_angle_deg: null }   # TODO
  from_scenario: [cast_distance, scenario]
scenarios:
  single_target_no_adds: { overlaps: 1 }
  pack:  { overlaps: derived }
  wall:  { overlaps: derived }
derived:
  spacing: "cast_distance * spread_angle_rad"
  radius_needed_for_k_neighbours: "k * spacing - enemyRadius"
  overlaps: "1 + 2 * k"
solve:
  required_increased_aoe: "(radius_needed / base_radius)^2 - 1"
multiplies: hit_damage_only     # not ignite
modifiers:
  pierce_chain_fork: "explosion happens at final collision, remove those projectiles from overlap"
```

PoB has no overlap option for Fireball. Extra explosions only count if projectiles exploded on other enemies or a wall:
[[Pinnacle Boss]] = 1 overlap, [[Mapping]] = geometry.
