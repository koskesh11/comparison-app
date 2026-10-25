# QA department — lessons
Process lessons only (game facts go to the vault). Format: date · task · trigger → rule → check · status.

- 2026-10-22 · 003 · QA re-pinned tests/golden.json while interactions was still editing the vault; the vault
  hash test failed afterwards → Re-pin golden values only after the vault writer has finished; ask the
  orchestrator who holds vault/ → check: task file shows no active vault writer before re-pinning. · active
- 2026-10-23 · 003 · No browser tooling (Playwright/jsdom absent); GUI checked against an ad-hoc stub DOM → Keep a
  stub-DOM render script in tests/ that runs renderReport on a saved report → check: new GUI fields rendered by it. · active
- 2026-10-25 · 021 · GATE 3 flagged "2 tiers" and pinned uniques as failures; both were user decisions (task log
  scope change, vault Inbox/Seed unique pins) → judge against the current Done when and the vault rules → check:
  each FAIL cites the Done-when line or vault rule · active (orchestrator side promoted).
- 2026-10-25 · 021 · Seed-run tool printed only at the end, so a killed run had no stage times → tools stream one
  line per stage → check: kill a run mid-way and see the last stage printed · active (fix in 021 loop 1).
