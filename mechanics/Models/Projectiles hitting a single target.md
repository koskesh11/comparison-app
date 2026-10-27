---
type: model
status: verified
verified_by: user, 2026-10-22 (blind-test reveal)
pob_refs: [ForbiddenRite, ForbiddenRiteAltX, SupportGreaterVolley, ProjectileCount, AreaOfEffectRadius, EnemyRadius, skillPart, FullDPS]
superseded_by_pob:
source: "PoB 2.67.2 (3.29) Data/Skills/act_int.lua, Data/Skills/sup_dex.lua, Modules/ConfigOptions.lua, Modules/Calcs.lua; poewiki Forbidden Rite (text since 2021-08-29 / 3.15, unchanged in the 2026-07-26 revision), Greater Volley Support, Trigger (API, 2026-10-22); pathofexile.com forum thread 3155643 (3.15, 2021-07-31); headless runs on FR CoC v4 (in memory, 2026-10-22)"
last_confirmed_patch: "3.29.x"
---

```model
proposed_kind: parallel_projectile_single_target_hits   # not in models.py KINDS; no "kind:" so the app skips this note
hit_fraction: 0.6   # USER-VERIFIED 2026-10-22: ~60% of all projectiles hit a boss for FR, Fireball and other
                    # skills with an AoE explosion. Authoritative; the geometry params below are reference only
                    # (department estimate was 4 of 6 = 67%: close, slightly high). v4: 6 x 0.6 = 3.6 hits.
applies_to: { skill: ["Forbidden Rite", "Forbidden Rite of Soul Sacrifice"], support: "Greater Volley" }   # list + support: engine must accept both first
multiplies: [FullDPS]                  # FR's share only, via feed_pob (never the whole FullDPS)
inputs: { from_pob: [ProjectileCount, AreaOfEffectRadius, skillPart, count], from_scenario: [enemy_radius_u] }
units: "PoB radius units, 10 = 1 m (models.py UNITS_PER_METRE)"
params:
  secondary_hits: 1          # SOLID (wiki FR): "on single target, two projectiles will hit the enemy"; extra projectiles only add to the cursor projectile
  points_per_side: 4         # SOLID: sup_dex.lua:2285; 5 projectiles = centre + 2 per side (wiki Volley fill order)
  spacing_u: 7.36            # UNVERIFIED: x_dist 80 (sup_dex.lua:2286), read as world units at 250/23 per radius unit; plausible 1.84-8
  enemy_radius_u: 3          # PoB preset Medium (its default, ConfigOptions.lua:777-800), "most humanoid bosses (Maven, Shaper, Izaro)"; Large 5, Huge 11
  aim_offset_spacings: 0     # CoC targets the crit enemy (wiki Trigger), so the centre projectile lands on the boss
solve:
  reach_u: "AreaOfEffectRadius + enemy_radius_u"   # hit rule as PoB act_int.lua:1121-1122 (AoE overlaps the enemy circle)
  primary_hits: "count of i in 0..P-1 with abs((i - (P-1)/2 + aim_offset_spacings) * spacing_u) <= reach_u"
  expected: "primary_hits + secondary_hits"
  hits: "floor(expected)"
  feed_pob: { skillPart: 1, count: hits }    # replaces BOTH PoB's part-2 multiplier (P + 1) and any hand-set count
  valid_for: "P <= 1 + 2 * points_per_side (9); lone target; FR triggered by CoC or cursor on the boss"
results_v4:
  inputs: { P: 5, AreaOfEffectRadius: 9, reach_u: 12 }
  calibrated: { hits: 4, FullDPS: 38056232 }
  range: { hits: [2, 6], FullDPS: [19111438, 57001026] }
scenarios:
  single_target_boss: "as solved (v4: 4 hits on a Medium boss)"
  large_boss: "enemy_radius_u 5 -> 4 hits (marginal: 6 if spacing_u <= 7.0)"
  huge_boss: "enemy_radius_u 11 -> 6 hits"
  pack: "cursor target as solved; each other enemy 1 secondary (up to 7 + quality x 0.1, act_int.lua:7612) plus AoE overlaps; not modelled"
  other_projectile_sources: "GMP, helmet enchant, Rain of Splinters, Dying Sun use FR's own 'expanding ring' pattern (wiki), not this line; not modelled"
```

**Gap:** PoB has no "hits on one target" for Forbidden Rite. Part 1 counts one projectile. Part 2 multiplies by ProjectileCount + 1 (`Data/Skills/act_int.lua:7414-7416`; Soul Sacrifice `7570-7572`). Players also set the gem count by hand: FullDPS = TotalDPS x count (`Modules/Calcs.lua:254-255`). Paths are relative to `%APPDATA%\Path of Building Community`.

**Geometry:** Greater Volley fires extra projectiles parallel to the main one, from points beside you (wiki Greater Volley). FR's projectiles only explode, at the end of their path (`act_int.lua:7625`). So the 5 explosions land in a line across the shot: 0, ±s, ±2s. An explosion hits if its radius reaches the enemy circle (PoB's own rule). v4: reach = 9 + 3 = 12 u. At s = 7.36 u, ±1 hit and ±2 miss (14.7 u). That gives 3 primaries + 1 secondary = **4**.

**Sensitivity (offset 0, r = 3, R = 9):**

| Hits | Spacing | Note |
|---|---|---|
| 6 | ≤ 6.0 u | |
| 4 | 6.0–12 u | Holds at 7.36 and at the 8 u reading |
| 2 | > 12 u | |

- Bigger area: 6 hits once AreaOfEffectRadius ≥ 12.
- Random landing (±0.5 spacing, the Winter Orb convention): 4.26 → still **4**.

**Corroboration (anecdotal, 3.15):** forum 3155643 (loloppe, 2021-07-31) tested poison on hit in PvP against a player-sized target. It got about 4 stacks per cast "no matter how many projectiles", and the author advises "at least 4 projectiles". The sources there were Rain of Splinters, Dying Sun and the enchant, not Greater Volley. A 3.15 guide (pobarchives 7QjMVfRd, behind Cloudflare, only seen as a search snippet) says that with GMP or Greater Volley, one or two projectiles always miss. Both fit 4–5 of 6.

**v4 FullDPS (headless, part 1, count = hits):**

| Hits | FullDPS | Note |
|---|---|---|
| 2 | 19,111,438 | |
| 3 | 28,583,835 | |
| **4** | **38,056,232** | Calibrated, −33.2% vs saved |
| 5 | 47,528,629 | |
| 6 | 57,001,026 | Same as part 2 with count 1 (as saved) |

- FR is 9,472,397 per hit. Cyclone stays at 166,643.

**UNVERIFIED:**
1. The unit of x_dist. 80 in radius units would put projectiles 8 m apart, which can't be right: Ghostly Artillery's "row of cannons" has x_dist 60.
2. Whether FR's homing (wiki: projectiles "bend towards targeted enemies") pulls the outer pair in. If it does, the count is 6.
3. Whether Greater Volley keeps the parallel line or FR's own ring pattern. Also the layout for an even P.
4. Pinnacle hitbox radii: PoB gives only the presets. Sirus and the Incarnations as Medium is an assumption.
5. Whether exactly 1 secondary hits a lone boss.

v2 and v3 have not been re-run with this geometry.

**Engine risks (fix before adding the kind):**
- apply_models multiplies the whole FullDPS by hits / count (`engine/models.py:79-82`). That also scales Cyclone's share, and on a part-2 build it stacks: 57.0M x 6.
- A list in applies_to.skill never matches today, because models.py compares one string.
- groupCount overrides the gem count (`Modules/Calcs.lua:119`).
- Sidebar and calcs-tab parts can differ (`Modules/CalcActiveSkill.lua:251-262`).

Related: [[FR CoC Cyclone - skills and supports]], [[Winter Orb projectile overlap]], [[Own shock effect]], [[Models round down]].
