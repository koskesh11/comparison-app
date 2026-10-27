---
type: gap
status: draft
source: "poewiki Elemental Equilibrium rev 1605611, Exposure rev 1673498 (as quoted in vault Interactions Elemental Equilibrium); PoB 2.67.2 Modules/CalcPerform.lua:3630-3636, ConfigOptions.lua:2048 (task 027 batch 3)"
last_confirmed_patch: "3.29.x"
---

# Elemental Equilibrium and on-hit exposure: order of operations differs (gap, prose only, no mod pattern)

**Wiki.** Elemental Equilibrium (EE) is applied BEFORE regular on-hit exposure: a hit removes the exposure of the element it dealt, and an on-hit exposure source of the same element (Eye of Malice, Cold Mastery, Awakened penetration supports) can still land afterwards. So for a single-element build the exposure is up at the next hit only with the source's own chance (Eye of Malice 25% -> about 25%), not always ([[Elemental Equilibrium]], derived from the wiki order, not stated as a number on the page).

**PoB.** The exposure block (`CalcPerform.lua:3630-3636`) skips the element's whole exposure when `ElementalEquilibrium` is active and the enemy flag `Condition:HitBy<Element>Damage` is set. That flag comes only from the config boxes (`enemyConditionHitByFireDamage` etc., `ConfigOptions.lua:2048`, shown only with the keystone), never from the build's own hit. Result: with no box ticked PoB keeps the exposure (EE looks like it does nothing); with the box ticked PoB drops ALL exposure of that element including the on-hit source (about 0% instead of the wiki's chance-based uptime).

**Consequence.** Neither PoB state matches the wiki for a build whose own element is the one with an on-hit exposure source: the unticked state overstates exposure, the ticked state understates it. The honest range for the single-element case is "0% (box) to 100% (no box); the wiki order gives the source's own chance". Rotation builds (another element hits first) are the case PoB's boxes model well.

**Rule:** report exposure for an EE build as a range, name which box PoB used, and do not credit an on-hit exposure source of the build's own element at 100% under EE. Whether the game really re-applies after removal (wiki order) was not tested in the game.

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap is a calculation-order difference, not a mod line.
