---
type: model
status: draft
pob_refs: [Fireball, SupportGreaterMultipleProjectiles, ProjectileCount, AreaOfEffectRadius, enemyRadius, skillPart, TotalDPS, IgniteDPS]
superseded_by_pob:
source: "poewiki Fireball (rev 1698987, 3.29.0), Projectile (rev 1642414), Greater Multiple Projectiles Support (rev 1681576), Ignite (rev 1598418), API 2026-10-26; PoB 2.67.2 (3.29) Data/Skills/act_int.lua, Data/Skills/sup_dex.lua, Modules/CalcOffence.lua"
last_confirmed_patch: "3.29.0"
---

Pipeline: [[Damage calculation#Hit rate]] - extra Fireball projectiles change how many hits land per cast (a hits-per-cast factor on TotalDPS), not the damage per hit; GMP's 26% less is already in PoB's per-hit damage.

**What PoB does not count:** PoB counts one hit per cast for any projectile count. ProjectileCount multiplies DPS only for SequentialProjectiles skills (`Modules/CalcOffence.lua:803-806`); Fireball is not one (`Data/Skills/act_int.lua:5788-5808`). GMP L20 is counted only as 26% less projectile damage (`Data/Skills/sup_dex.lua:2160-2161, 2194`).

**Mechanic (sourced chain, verified):**
- Projectile rev 1642414: "When multiple projectiles are created simultaneously, only one of those projectiles can collide with the same target. Projectiles after the first will pass through without colliding." Fireball is listed under "only explode when the projectile is destroyed".
- Fireball rev 1698987 (3.29.0): "Each enemy can only be hit directly by one projectile per cast. However, if an enemy is in range of the explosion effect of more than one projectile from the same cast, and those projectiles each exploded on different enemies or a wall, it will take full damage from each explosion."
- On a lone boss the 4 outer GMP projectiles fan out (wiki GMP rev 1681576: "fan out in an arc") and either miss or pass through without colliding. They explode only on a wall or another enemy. The [[Pinnacle Boss]] scenario has no walls and no adds, so **1 hit per cast, x1.0 on TotalDPS**.
- Why Forbidden Rite differs: Projectile rev 1642414 lists Forbidden Rite among projectiles that "can never collide with enemies", so shotgun prevention never applies to it. The mechanism behind the 0.6 of [[Projectiles hitting a single target]] does not carry over to Fireball.

```model
applies_to: { skill: Fireball, support: "Greater Multiple Projectiles" }   # no "kind:" -> app skips until the engine supports it
proposed_kind: collision_limited_explosion_hits
pipeline_step: ["Damage calculation#Hit rate"]
inputs:
  from_pob: [ProjectileCount, AreaOfEffectRadius, enemyRadius, skillPart, TotalDPS, IgniteDPS]
  from_vault: { gmp_spread_angle_deg: null }   # UNVERIFIED: cursor-dependent (wiki GMP rev 1681576), no number found
  from_scenario: [walls, adds_near_target, cast_distance]
readings:
  B_wiki: { hits_per_cast: 1, source: "wiki Fireball rev 1698987 + Projectile rev 1642414 + Pinnacle Boss scenario (walls: false, no adds)" }
  A_user: { hit_fraction: 0.6, hits_per_cast: "floor(ProjectileCount * 0.6) = 3 at P 5 -> x3.0 on TotalDPS", source: "Projectiles hitting a single target (user, 2026-10-22; calibrated on FR + Greater Volley only)" }
  active: B_wiki        # A_user stays visible until the user rules (open question 1)
solve:
  hits_per_cast: "1 + E, E = outer projectiles that explode on a wall or another enemy within (AreaOfEffectRadius + enemyRadius) of the target"
  hits: "floor(hits_per_cast)"
  tdps_multiplier: "hits / 1"     # PoB counts 1 hit per cast; replaces (never stacks on) any hand-set count
pack_geometry:                    # Mapping only; kept from the first draft, needs gmp_spread_angle_deg
  spacing: "cast_distance * spread_angle_rad"
  radius_needed_for_k_neighbours: "k * spacing - enemyRadius"
  overlaps: "1 + 2 * k"
  required_increased_aoe: "(radius_needed / base_radius)^2 - 1"
scenarios:
  Pinnacle Boss: { walls: false, adds: none, hits: 1, tdps_multiplier: 1.0, range: [1, 1], confidence: high }
  Pinnacle Boss with wall or adds: { hits: "1 + E", range: [1, 5], confidence: low, note: "geometry; not modelled" }
  Mapping: { hits_per_enemy: "1 direct + explosions of projectiles that exploded on neighbours or walls", range: [1, 5], confidence: low, note: "pack_geometry; not modelled" }
ignite:
  multiplier: 1.0       # only the highest-DPS ignite deals damage (wiki Ignite rev 1598418); extra hits add applications, not stacks
  pob_note: "PoB ignite cfg drops ModFlag.Projectile (CalcOffence.lua:4998), so GMP's less does not reduce ignite; wiki GMP rev 1681576 agrees"
multiplies: hit_damage_only
modifiers:
  pierce_chain_fork: "the projectile explodes only when it cannot continue (wiki Fireball rev 1698987), so these projectiles do not explode on the first target"
calibration: "no norm found (forum, reddit, PoB GitHub searched 2026-10-26); mechanism from wiki"
not_verified:
  - "Whether the directly hit enemy also takes that projectile's explosion as a second hit (wiki wording implies one hit; PoB parts 1 and 2 are each one hit)"
  - "Whether Fireball explodes at the end of its range (wiki names only collision and walls)"
  - "GMP spread angle in degrees"
open_questions:
  - "The user's 0.6 says 'FR, Fireball and other AoE-explosion skills'; the wiki says Fireball cannot shotgun a lone target (1 of 5). Was the 0.6 seen on Fireball itself, or only on FR?"
```

Related: [[Projectiles hitting a single target]], [[Winter Orb projectile overlap]], [[Pinnacle Boss]], [[Mapping]], [[Models round down]].
