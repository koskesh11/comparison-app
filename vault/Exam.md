# Exam: does the system actually learn?

Measures whether the analyzer and its knowledge get better over time (owner, 2026-10-26: "if there's no improvement in
6 months and you keep making the same mistakes, there's no point"). The exam is re-run regularly and the score is
tracked. New questions come from the owner's examples, from every mistake he catches, and from questions the system
proposes. The format is provisional until the target design defines the knowledge format.

Each question has a type:
- **spot:** the system must notice and raise the interaction question by itself.
- **explain:** it must state the mechanic correctly, with sources.
- **idea:** it must come up with the build idea itself.

The expected answer stays "unverified" until it is checked in PoB and confirmed by the owner.

## E1. Fireball with Far Shot and pierce (type: spot, then explain)
- Source: owner, 2026-10-26.
- Question: Fireball is a projectile that explodes, so it has a projectile part and an area (explosion) part. How does
  it interact with Far Shot (more damage the further the projectile travels; one unique helmet grants it) and with
  pierce (the projectile flies through enemies and keeps gaining distance)? Which part of Fireball does each modifier
  affect?
- A passing answer must: notice that the two parts can be affected differently; check the exact modifier wording
  (e.g. whether it applies to attacks only, or to projectile hits only); and measure in PoB what changes.
- Expected answer: UNVERIFIED (research it, then confirm with the owner).

## E2. Forbidden Rite of Soul Sacrifice with Foulborn Three Dragons (type: idea; later stage)
- Source: owner, 2026-10-26 (his idea, not PoB'd yet).
- Idea to reach on its own: Forbidden Rite of Soul Sacrifice deals chaos damage based on the energy shield it uses, so
  stacking ES (e.g. ~17,000 with Chaos Inoculation for chaos immunity) scales offence through defence. The Foulborn
  Three Dragons helmet lets chaos damage shock, ignite or freeze, with two of those at once. Shock raises the enemy's
  damage taken (a multiplier) and freeze is a defensive layer. Add Cyclone with Cast on Critical Strike for comfort
  (see Glossary).
- Expected answer: UNVERIFIED (PoB it, then confirm with the owner).
