---
type: rule
kind: tradeoff
status: draft
pob_refs: [SupportCastOnCriticalStrike, SupportAwakenedCastOnCriticalStrike, ManaPerSecondCost, cyclone_movement_speed_+%_final, cyclone_area_of_effect_+%_per_additional_melee_range]
source: CoC EK Assa audit (Cyclone 1/0 vs 20/20), user correction
last_confirmed_patch: 3.29.0
---

```rule
when:
  linked_support_any: [SupportCastOnCriticalStrike, SupportAwakenedCastOnCriticalStrike]
tradeoff:
  subject: triggering_attack_gem_level
  show: [mana_margin, dps, qol]
  qol:
    Cyclone:
      level:   { stat: cyclone_movement_speed_+%_final, note: "-30% at 1, -20% at 20 (+14% channel move speed)" }
      quality: { stat: cyclone_area_of_effect_+%_per_additional_melee_range, note: "only with extra melee range" }
```

Not "always level 1". Trigger attack damage barely matters, so the choice is
**mana margin vs quality of life** (Cyclone: move speed from levels, AoE from quality if you have melee range).
CoC EK Assa: 20/20 = +14% channel move speed, 0 AoE (no extra range), mana margin +22/s → +13/s.
