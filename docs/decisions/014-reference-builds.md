# 014 Worb and CoC EK Assa are the reference builds

- Date: 2026-10-27 (grilling rounds 14, 28)
- Decided by: owner
- Status: accepted; the Worb settings line is set aside for src/ until leaving skills out comes back (018)
- Scope: tests and fixtures

## Decision
- The reference builds are `3.29\Worb.xml` and `3.29\Ninja Builds\CoC EK Assa.xml` from the owner's PoB builds
  folder. They, and copies of them, may be committed as test fixtures; the repo stays private (005).
- Worb is read with these settings: leave out "Aspect of the Brine King"; Winter Orb gem count 5; the Winter Orb model
  counts 4 hits, rounded down.
- The damage-chain reference is Worb against pobb.in/v8XfQn1yFnAs on Pinnacle Boss (the mockup, 009).

## Consequences
- Tests that need PoB or the owner's builds say so and skip cleanly where they are missing.
