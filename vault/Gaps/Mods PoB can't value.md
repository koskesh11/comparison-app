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
```

Add patterns here when the audit flags something as wasted that actually matters in game.
