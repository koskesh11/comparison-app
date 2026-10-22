---
type: rule
kind: validity
status: verified
pob_refs: [node.depends, Mastery]
source: user (Deep Thoughts / Mana Mastery)
last_confirmed_patch: 3.29.0
---

```rule
applies: tree_change
when_removing: last allocated Notable in a mastery's group
also_remove: that Mastery
then_check: all validity rules
```

Removing a notable can remove a mastery, and the mastery's effect (reservation, cost efficiency...) with it.
