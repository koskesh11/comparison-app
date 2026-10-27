---
type: gap
status: draft
source: "poewiki Damage reduction rev 1605942, Damage over time rev 1702687; PoB 2.67.2; pob-coverage-auditor-calc-order.md (R8) (task 027 evidence)"
last_confirmed_patch: "3.29.x"
---

# PoB applies flat damage reduction to damage over time, game behaviour unverified (gap, prose only, no mod pattern)

TakenDotMult = (1 - resistOverTime) x (1 - BaseDR) x (1 + inc) x more (CalcDefence.lua:1956-1972), so PoB applies the flat Base<Type>DamageReduction to DoT (line 1965) and DotEHP uses it (3373). The wiki Damage reduction page (rev 1605942) says damage reduction can mitigate DoT but 'can only be gained from armour against hits'. No source states that extra flat reduction applies to DoT in the game.

- If it does not apply, DoT EHP is overstated for builds with flat physical reduction.
- Rule: unverified; do not count flat reduction toward DoT survival without an in-game check.

Linked from: [[Receiving damage#Damage over time taken]].

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap has no mod pattern.
