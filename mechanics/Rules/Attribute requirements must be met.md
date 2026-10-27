---
type: rule
kind: validity
status: verified
pob_refs: [Str, ReqStr, Dex, ReqDex, Int, ReqInt]
source: user (CoC EK Assa audit, Physique/Alacrity/Trickery)
last_confirmed_patch: 3.29.0
---

```rule
applies: always
require:
  - { stat: Str, op: ">=", ref: ReqStr }
  - { stat: Dex, op: ">=", ref: ReqDex }
  - { stat: Int, op: ">=", ref: ReqInt }
```

PoB still calculates gems/items you can't equip. A node that "does nothing" may be the one holding a requirement.
