# 015 What the analyzer calls a flaw

- Date: 2026-10-26 (grilling rounds 3-6)
- Decided by: owner
- Status: accepted; most of it is built after milestone 1 (roadmap ranking items 1-3)
- Scope: what the analyzer reports and proposes

## Decision
- A flaw is a gap in a scaling vector against the target build, together with how to close it. Owner's example: "you're
  missing flat on Fireball compared to the aspired Fireball PoB, and this is how to fix it."
- Over-investment is a flaw too: "you have 1000 % increased damage but only 10 % more." The marginal value of the next
  step of every vector is shown, so every imbalance shows up.
- Flaw checks also ask whether the mechanics work as advertised: sustainability (flask charges spent against gained,
  charge sources such as frenzy "on kill" that never fire on a boss) and on-hit uptime (hits per second times the
  chance, against the duration: 11 hits/s at 10 % is always on, 1 hit/s at 10 % is once every 10 s).
- Alternatives may use any vector and need not make up the whole gap. "The point is to give alternative scaling
  vectors. Many people just stack stats because they're rich in-game."
- Budget is not a constraint: target builds are affordable by definition. A fix may cost something the build can find
  elsewhere (a ring that drops resistances); it may not cost a 90-divine item.
- Build-enabling items: show how close the build gets without them ("remove the unique and see what breaks"). What PoB
  cannot calculate goes to the knowledge base, case by case with the owner.
- Boxes the tool cannot judge are asked of the owner, up to about one minute per comparison.

## Consequences
- The failure modes in docs/analyzer-checklist.md are how a report is judged before the owner sees it.
