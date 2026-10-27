---
type: model
status: draft
pob_refs: [WinterOrb, ProjectileCount, AreaOfEffectRadius]
superseded_by_pob:
source: https://www.poewiki.net/wiki/Winter_Orb#Area_of_Effect
last_confirmed_patch: 3.29.0
---

```model
applies_to: { skill: "Winter Orb" }
kind: line_overlap            # projectiles land in a rough line; each overlapping impact hits the target
multiplies: [FullDPS, CombinedDPS, TotalDPS]
params:
  spacing_m: 1.4              # calibrated: 3 projectiles overlap even in the worst line position at base 1.6 m (wiki: "reliably")
  enemy_radius_m: 0.5
  nova_items: ["Sire of Shards", "Black Zenith"]   # circle pattern: every projectile overlaps
```

PoB counts **one hit per volley** (`hitTimeOverride` ignores projectile count).
Projectiles land in a **rough line** (wiki). Where that line sits relative to the target varies, so the
model averages over a uniform offset of ±half a spacing: expected hits = average number of impacts within
radius + enemy radius of the target. With a nova item, all projectiles overlap.

Known (wiki 3.29 + guides): 3 base projectiles at gem level 20+, auto-targets nearby enemies, explodes where
it lands, "3 reliably overlap without AoE", "5 projectiles: 2.6–2.8 m radius optimal", projectile speed only
changes time to impact (3.28). **Not documented:** exact spacing — 1.4 m is calibrated, not measured.
Single target only: with adds nearby, projectiles target other enemies and the boss takes fewer hits.

**Players often model this by hand with the gem's PoB "count"** (Worb: count = 5). The model replaces that
count instead of stacking on it. Worb: 6 projectiles, 2.6 m radius → expected ~4.4 hits (4–5) vs user's count 5.
