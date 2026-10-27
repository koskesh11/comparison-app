# 011 Skill settings must match

- Date: 2026-10-27 (grilling rounds 15-18)
- Decided by: owner; the different-main-skill case by Claude (round 15)
- Status: accepted for now; to be re-evaluated as knowledge grows
- Scope: the analyzer, before the chain is shown

## Context
"You cannot just compare pineapples to beans." Skills have parts and settings (Fireball projectile or explosion,
Bladefall blade count, Winter Orb stages). Some PoBs carry the main skill twice, one copy per part (Lightning Strike or
Smite at the right distance).

## Decision
- Compare with the settings saved in the two PoBs, exactly as they are. Situations such as a boss next to a wall are not
  modelled.
- When the main skill's settings differ, say so immediately and hide the chain. One button recalculates your build in
  memory with the target's skill setting; your file is never changed.
- When the target's main skill is a different skill, warn and let the owner pick the target's skill group.

## Consequences
- In about nine months Claude should make these calls on its own; the rule is evaluated over time.
