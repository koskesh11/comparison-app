---
type: gap
status: draft
source: "poewiki Spell suppression rev 1675604; PoB 2.67.2; mechanics-researcher-receiving-defences.md (Table B) (task 027 evidence)"
last_confirmed_patch: "3.29.x"
---

# Spell suppression also reduces damage of ailments the suppressed spell inflicted, PoB does not (gap, prose only, no mod pattern)

The wiki says suppressed spell hits take 40% less damage from the hit and from ailments it inflicts. PoB's DoT multiplier TakenDotMult (CalcDefence.lua:1962-1971) has no suppression factor; suppression enters only the hit path (2072, 2105, 2816-2825).

- DoT taken from spell-inflicted ignite or poison is overstated in PoB by up to the suppression effect for builds with high suppression.
- Rule: unverified in-game; do not credit suppression against ailment DPS.

Linked from: [[Receiving damage#Spell suppression]].

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap has no mod pattern.
