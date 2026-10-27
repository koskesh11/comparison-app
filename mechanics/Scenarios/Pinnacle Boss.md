---
type: scenario
status: draft
pob_refs: [enemyIsBoss=Pinnacle]
scenario: single_target_no_adds
cast_distance_m: null
walls: false
freeze_assumable: false
pob_config:
  multiplierChannelling: 3      # seconds channelled on a boss (Focused Channelling caps at ~2.5 s)
conditional_config:      # applied by engine/audit.py apply_conditional_config (tasks/003 A3)
  conditionOnConsecratedGround: { value: true, only_if: build_has_consecrated_ground_source }   # e.g. Bottled Faith; never granted to builds without a source
---

Uses PoB's Pinnacle boss config for enemy stats. Adds only what PoB lacks: lone target, no walls, freeze not assumed.

Consecrated ground counts as ON during the fight only for builds that have a source of it (e.g. Bottled Faith); builds without one never get it. A source is an equipped item, allocated node or enabled gem whose text says it creates consecrated ground; the audit shows the source it used, or "not applied (build has no source)".
