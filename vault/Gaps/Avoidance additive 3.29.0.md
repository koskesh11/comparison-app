---
type: gap
status: draft
source: "poewiki Avoidance rev 1675590; PoB 2.67.2; mechanics-researcher-receiving-defences.md (Surprises 2) (task 027 evidence)"
last_confirmed_patch: "3.29.x"
---

# Avoid-all damage from hits: wiki says additive since 3.29.0, PoB multiplies (gap, prose only, no mod pattern)

Wiki Avoidance rev 1675590 (patch 3.29.0): sources of 'avoid all damage from hits' are now additive with 'avoid <type> damage' and the 75% cap bug was fixed. PoB keeps AvoidAllDamageFromHitsChance as its own factor in NotHitChance (CalcDefence.lua:1689-1693, 2935), while the per-type EHP path reads only Avoid<Type>DamageChance plus projectile (2829-2836), so they never add. ModParser keeps two stat names (ModParser.lua:386-387); whether a parser line adds avoid-all into each type was not checked.

- A build stacking both kinds is understated in PoB if the wiki is right. PoB may simply lag the 3.29.0 change; this is a conflict, not a proven PoB bug.
- Both readings stay visible; do not pick one silently. Needs an in-game or patch-note check (user).

Linked from: [[Receiving damage#Immunity and avoidance]], [[Defences#Damage avoidance]].

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap has no mod pattern.
