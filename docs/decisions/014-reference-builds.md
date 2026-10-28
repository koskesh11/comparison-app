# 014 Worb and CoC EK Assa are the reference builds

- Date: 2026-10-27 (grilling rounds 14, 28)
- Decided by: owner
- Status: accepted; the Worb settings line is set aside for src/ until leaving skills out comes back (018);
  extended 2026-10-28 with the variety builds (owner, grilling part 1)
- Scope: tests and fixtures

## Decision
- The reference builds are `3.29\Worb.xml` and `3.29\Ninja Builds\CoC EK Assa.xml` from the owner's PoB builds
  folder. They, and copies of them, may be committed as test fixtures. The repo is public since 2026-10-28 (025);
  the owner made the whole project public knowing this.
- Test builds beside them (owner, 2026-10-28): Elemental Hit Slayer, Phys Dot Elementalist and Winter Orb (Occultist),
  guides their authors shared publicly, saved by the owner to Builds\AutoBuilder\Variety Builds and committed byte
  for byte. They bring dual wield, hits of several damage types, a staged skill and minion main skills. Tests make
  each stage (decision 026) into its own build from the saved file and compare neighbouring stages.
- Worb is read with these settings: leave out "Aspect of the Brine King"; Winter Orb gem count 5; the Winter Orb model
  counts 4 hits, rounded down.
- The damage-chain reference is Worb against pobb.in/v8XfQn1yFnAs on Pinnacle Boss (the mockup, 009).

## Consequences
- Tests that need PoB or the owner's builds say so and skip cleanly where they are missing.
