---
type: gap
status: draft
source: "poewiki Recovery rev 1618351, Leech rev 1642429; PoB 2.67.2; pob-coverage-auditor-calc-order.md (R9) (task 027 evidence)"
last_confirmed_patch: "3.29.x"
---

# PoB's Effective HP ignores regeneration, leech, flasks and recovery speed (gap, prose only, no mod pattern)

TotalEHP and NumberOfDamagingHits (CalcDefence.lua:2904-2966) contain no regeneration, leech, flask or recovery term; only gain-on-block / gain-on-suppress is included (2804-2837, only if hits > 1 and DisableEHPGainOnBlock is unset). The wiki Recovery page says recovery is applied before DoT loss per 33 ms frame; this ordering is not modelled in EHP.

- Two builds with equal EHP differ if one out-recovers damage over the fight. Deficits must be judged by duration (fight length), not by pool size.
- Rule: pair every EHP figure with the recovery per second from PoB and the fight length ([[Fight length]]); never present EHP as survivability alone.

Linked from: [[Receiving damage#Recovery]], [[Defences#Recovery and leech]], [[Defences#Effective HP]].

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap has no mod pattern.
