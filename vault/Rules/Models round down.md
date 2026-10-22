---
type: rule
kind: convention
status: verified
pob_refs: []
source: user
last_confirmed_patch: 3.29.0
---

```rule
applies: models
round: down
```

PoE rounds values down. Every number a vault Model produces (hits, overlaps, multipliers) is rounded down
to a whole number before it's used — e.g. Winter Orb 4.42 expected hits → 4.
