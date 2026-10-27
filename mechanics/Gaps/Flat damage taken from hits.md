---
type: gap
status: draft
source: "poewiki Receiving damage rev 1702582, Damage taken rev 1673455; PoB 2.67.2; mechanics-researcher-damage-calc.md (open item 1) (task 027 evidence)"
last_confirmed_patch: "3.29.x"
---

# Flat 'damage taken from hits' on the enemy is not in PoB's offence (gap, prose only, no mod pattern)

Wiki Receiving damage step 7: flat '# damage taken from hits' is applied first, before the summed increases and the more/less multipliers. PoB's incoming side has it (CalcDefence.lua:2009, 2102), but its offence side has no counterpart: grep for FlatDamageTaken / DamageTakenFromHits in CalcOffence.lua finds nothing, and the enemy effMult is (1 + takenInc) x takenMore x (1 - resist) only (3580-3597).

- A flat taken-from-hits effect on the enemy (if any provider exists) is invisible to PoB's DPS. No concrete provider has been found in the evidence.
- Rule: if a provider is found, treat it as a vault model, not a PoB number.

Linked from: [[Damage calculation#Damage taken]].

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap has no mod pattern.
