---
type: rule
kind: hard_constraint
status: draft
pob_refs: [SupportArcaneSurge, ManaCost, AffectedByArcaneSurge, CostESInsteadOfManaOrLife]
source: "PoB 2.67.2 (3.29) data and source, chain below; found by GATE 4 on tasks/003 (v4 swap 'Increased Critical Damage -> Arcane Surge')"
last_confirmed_patch: 3.29.0
---

```rule
# `when_support_linked` gates the rule on a linked support without making it a protected swap anchor
# (unlike `when: linked_support_any`, which audit.py treats as an anchor).
when_support_linked: [SupportArcaneSurge]
evaluate_on: main_skill
require:
  - { stat: ManaCost, op: ">", value: 0 }   # 0 when costs are paid in ES/life (e.g. Whispers of Infinity)
reject: new_breaks_only
```

Arcane Surge Support only grants its buff after you **spend mana** on the supported skill. If the build pays its
costs with something else, the support's "more spell damage" never turns on, but PoB still counts it.
Paths relative to `%APPDATA%\Path of Building Community` (PoB 2.67.2).
- Gem text: "Gain Arcane Surge after Spending a total of {0} Mana on Upfront Costs and Effects of a Supported Skill"
  (`Data/StatDescriptions/gem_stat_descriptions.lua:4624`, stat `support_arcane_surge_gain_buff_on_mana_use_threshold`).
- Whispers of Infinity: "Skills Cost Energy Shield instead of Mana or Life" (`Data/Uniques/amulet.lua:1416`); PoB then
  reports ManaCost 0 (FR CoC v4 headless: Cyclone and FR ManaCost 0, ESCost 6 / 149).
- PoB applies the support's buff whenever the supported skill is enabled, with no mana check
  (`Modules/CalcPerform.lua:2311-2324` sets `AffectedByArcaneSurge`; the more-damage line needs only that condition,
  `Data/Skills/sup_int.lua:235`).
- Effect without this rule: FR CoC v4 swap "Increased Critical Damage -> Arcane Surge" +2.5% DPS, source build
  "Greater Volley -> Arcane Surge" +65.9%, both counting a buff the build can't get.
- Checked on the main skill. In CoC builds that is the attack; with a global cost change (Whispers) attack and spell pay
  the same way. UNVERIFIED: a build with another Arcane Surge source (the support's more damage works with any Arcane
  Surge) is over-blocked; Eldritch Battery keeps ManaCost > 0, so it is not blocked (whether ES-paid mana costs count
  as "mana spent" is UNVERIFIED).
