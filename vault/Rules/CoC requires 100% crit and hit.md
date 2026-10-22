---
type: rule
kind: hard_constraint
status: draft
pob_refs: [SupportCastOnCriticalStrike, SupportAwakenedCastOnCriticalStrike, Resolute Technique]
source: user (expert rule)
last_confirmed_patch: 3.29.0
---

```rule
when:
  linked_support_any: [SupportCastOnCriticalStrike, SupportAwakenedCastOnCriticalStrike]
evaluate_on: triggering_attack
require:
  - { stat: CritChance, op: ">=", value: 100 }
  - { stat: HitChance,  op: ">=", value: 100, against: scenario }
forbid:
  - { keystone: "Resolute Technique", reason: "never crits" }
```

No exceptions. Checked on the attack that triggers CoC. Hit chance vs the chosen scenario (e.g. [[Pinnacle Boss]]).
