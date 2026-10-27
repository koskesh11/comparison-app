# Roadmap

Current state only; the reasons are in [decisions/](decisions/README.md). Last updated 2026-10-27 (task 102).

## What the app is
A build analyzer for Path of Exile 1. You load your build and a target build; your installed Path of Building
calculates both; the app shows how each one scales, where every gap comes from and what closing it is worth. Every
number is PoB's or comes from a verified mechanics note.

## Where it stands
- The first app (`engine/`, `gui/`) is frozen and runnable as reference: it audits one build through PoB headless and
  has an early guide check against a pobb.in build. Its generator is frozen on git tags (decision 002).
- The analyzer is not built yet. Its code goes into `src/`, which does not exist yet (decision 004).
- The damage-chain mockup with real PoB numbers is approved (decision 009).
- The review of the code that carries over is done (task 102): 26 of engine/'s 51 files carry a piece into `src/`,
  12 pieces as they are and 29 rewritten; the rest stays in engine/ as reference.

## Next, in this order
1. The checks for `src/`: linter, import rule, size check, commit hook, local merge script, architecture checklist,
   the `src/` folder names, `vault/` renamed to `mechanics/` (decisions 006, 013).
2. Milestone 1.

## Milestone 1
Done when:
1. The app loads your build plus a target (a pobb.in link or a pasted PoB code).
2. It shows the damage chain like the mockup: hit damage of the main skill, scenario Pinnacle Boss by default,
   both builds exactly as saved (decision 018), without the worth column (decision 019).
3. It flags differences in skill settings and config between the two builds.
4. All checks are green and the cold AI review passes.

## After milestone 1 (the owner's ranking, 2026-10-27)
1. Alternative scaling vectors, the marginal value of each vector (the chain's worth column and config differences
   sorted by their effect, decision 019), build-enabling items.
2. Defence vectors, other skills, minions, damage over time.
3. Sustainability checks (flask charges, charge sources) and on-hit uptime.
4. Hovering a source shows the target's actual items and mods (example: the target's crit-multi Cobalt Jewels).
5. The in-app chat on the owner's Claude subscription, with speech-to-text (decision 016).
6. Comparing many builds.

Ongoing, not ranked: the exam and the glossary. When the owner brings the 3.30 patch notes (league start
13 November 2026), every mechanics note, exam question and glossary term is checked against them.

## Not now
The generator, pricing.

## Open for the owner
Private for good, or presented to the community when good enough (decision 005).
