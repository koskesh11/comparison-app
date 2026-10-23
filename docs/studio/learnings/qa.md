# QA department — lessons
Process lessons only (game facts go to the vault). Format: date · task · trigger → rule → check · status.

- 2026-10-22 · 003 · QA re-pinned tests/golden.json while interactions was still editing the vault; the vault
  hash test failed afterwards → Re-pin golden values only after the vault writer has finished; ask the
  orchestrator who holds vault/ → check: task file shows no active vault writer before re-pinning. · active
- 2026-10-23 · 003 · No browser tooling (Playwright/jsdom absent); GUI checked against an ad-hoc stub DOM → Keep a
  stub-DOM render script in tests/ that runs renderReport on a saved report → check: new GUI fields rendered by it. · active
