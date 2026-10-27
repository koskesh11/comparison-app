---
type: gap
status: draft
source: "poewiki Guard skill rev 1660806; PoB 2.67.2; pob-coverage-auditor-calc-order.md (R6) (task 027 evidence)"
last_confirmed_patch: "3.29.x"
---

# Guard skills are a static, always-full absorb pool in PoB (gap, prose only, no mod pattern)

The wiki order puts Guard buffs at step 12.1 before ward, ES, mana and life; non-Vaal Guards share a cooldown and the cooldown does not recover while a Guard buff is active. PoB gets the order right but treats Guard (Molten Shell etc.) as a static absorb pool: no duration, no cooldown, always full (CalcDefence.lua:224-243, 266-310, 2423-2453).

- EHP with a Guard is a snapshot of the full buff; in a fight longer than the guard's duration or cooldown the benefit is smaller.
- Rule: give the guard's uptime in the fight (cooldown vs fight length) next to the EHP; see [[Fight length]].

Linked from: [[Receiving damage#Guard and Aegis]].

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap has no mod pattern.
