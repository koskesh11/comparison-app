---
type: rule
kind: validity
status: verified
pob_refs: [ManaUnreserved, LifeUnreserved]
source: CoC EK Assa audit
last_confirmed_patch: 3.29.0
---

```rule
applies: always
require:
  - { stat: ManaUnreserved, op: ">=", value: 0 }
  - { stat: LifeUnreserved, op: ">=", value: 0 }
```

PoB keeps auras active even when over-reserved. In game they won't fit.
