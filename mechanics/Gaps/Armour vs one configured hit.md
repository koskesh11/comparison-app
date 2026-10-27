---
type: gap
status: draft
source: "poewiki Armour rev 1625574; PoB 2.67.2; pob-coverage-auditor-calc-order.md (R3, EHP combine) (task 027 evidence)"
last_confirmed_patch: "3.29.x"
---

# Armour is evaluated against one configured hit size (gap, prose only, no mod pattern)

Armour reduces a hit by A / (A + 5 x D), so the result depends on the size of D. PoB evaluates it against a single configured enemy hit per damage type (config enemy<Type>Damage or the boss preset, enemy mods, crit averaged in; CalcDefence.lua:1735-1822, 2011-2031), and on the offence side against the AVERAGE hit of the pass (CalcOffence.lua:3510-3511). EHP then repeats that one size until the pools are gone (CalcDefence.lua:2613-2784).

- Many small hits are reduced more than the number shows, one huge hit less. The error depends on the actual hit spread.
- Rule: any armour verdict names the configured hit size next to the number; compare armour options at two hit sizes.

Linked from: [[Receiving damage#Armour and damage reduction]], [[Damage calculation#Armour against hits]], [[Damage calculation#Damage roll]], [[Defences#Armour formula]].

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap has no mod pattern.
