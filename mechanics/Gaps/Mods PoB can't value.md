---
type: gap
status: draft
source: CoC EK Assa audit (wasted-mod test)
last_confirmed_patch: 3.29.0
---

```gap
# PoB calculates these as if they don't matter (always-on flasks, unmodelled mechanics).
# The audit shows them as "can't measure — check yourself", never as wasted.
patterns:
  - { match: "increased Duration",           slot: "Flask", why: "PoB assumes 100% flask uptime" }
  - { match: "reduced Duration",             slot: "Flask", why: "PoB assumes 100% flask uptime" }
  - { match: "Flask Charge",                                why: "PoB assumes 100% flask uptime" }
  - { match: "Used when Charges reach full",                why: "PoB assumes 100% flask uptime" }
  - { match: "increased Recovery rate",      slot: "Flask", why: "recovery timing not modelled" }
  - { match: "Corrupted Blood",                             why: "Corrupted Blood not modelled" }
  - { match: "Travel Skills",                               why: "movement skills not modelled" }
  - { match: "Smoke Cloud",                                 why: "not modelled" }
  - { match: "Charge Recovery",              slot: "Flask", why: "PoB assumes 100% flask uptime" }
  - { match: "Maximum Charges",              slot: "Flask", why: "PoB assumes 100% flask uptime" }
  - { match: "Grants Level",                                why: "granted skill: PoB only values it if the skill is set up in the skills tab" }
  - { match: "Modifier magnitudes",                         why: "PoB applies it when the item loads by scaling the item's other lines; removing this line alone shows no change" }
  - { match: "Creates Consecrated Ground",                  why: "PoB gives the line no value; it only feeds the config 'Are you on Consecrated Ground?'. Pinnacle Boss turns that on when the build has this source (regen, e.g. FR CoC v4 ES regen 1,266.5 -> 2,250.6/s)" }
```

**Evidence per pattern (PoB source lines, kept out of the player text; moved 2026-10-26, task 027 merge).**
- "Modifier magnitudes": Classes/Item.lua:1206

Add patterns here when the audit flags something as wasted that actually matters in game.
