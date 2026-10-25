---
type: gap
status: draft
source: "poewiki Receiving damage rev 1702582, Ignite rev 1598418, Poison rev 1700788, Bleeding rev 1700575; PoB 2.67.2; pob-coverage-auditor-calc-order.md (D12) (task 027 evidence)"
last_confirmed_patch: "3.29.x"
---

# Ailments from hits: unmitigated source and the ignite 50% roll (gap, prose only, no mod pattern)

The wiki says damaging ailments (ignite, poison, bleed) start from the hit's FLAT damage with no defender mitigation and no hit-only modifiers. PoB recomputes the source with calcAilmentSourceDamage (CalcOffence.lua:143-155; bleed 4520-4565, poison 4820-4840, ignite 5105-5152), which matches, but then applies enemy resist and taken-mods in the DoT multiplier (5192-5230). Ignite assumes the MIDDLE of the damage roll (50%) unless stack potential exceeds 1, then shifts toward the top (5076-5084). Shock, chill and freeze size from the post-mitigation hit average (4315-4331).

- Ignite DPS is an average; the real ignite uses the rolled hit. Builds that ignite only on high rolls are not distinguished.
- Rule: label ailment numbers as 'average roll' and check enemy resist applies where PoB applies it (unverified against the game).

Linked from: [[Damage calculation#Ailments from hits]].

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap has no mod pattern.
