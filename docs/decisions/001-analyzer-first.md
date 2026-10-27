# 001 The app is a build analyzer first

- Date: 2026-10-26, refined in grilling rounds 1, 3, 13 and 23 (2026-10-26/27)
- Decided by: owner
- Status: accepted
- Scope: product

## Context
The first project aimed at a build generator. Public feedback on 2026-10-26 said the repo had no visible structure, and
the generator was far from usable. The owner's real job: decide what to change, see why his build is weaker than a
target build, and check whether the target's config boxes are right for how the game works (round 3). "I don't want two
PoBs open side by side going line by line."

## Decision
The app is a build analyzer. You load your build and a target build; Path of Building calculates both; the app shows
how each one scales and where every gap comes from. One-to-one comparison first; comparing many builds comes later
(ranking item 6 in the roadmap). The generator comes back later, built on top of the analyzer.

## Consequences
- Milestone 1 is the damage-chain comparison (see the roadmap and 009).
- The analyzer must point out all the flaws, not just the obvious ones (round 3: "worth it in a month if").
- Drop condition (round 5): the tool gives wrong answers.
