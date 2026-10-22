# Engineering department — lessons
Process lessons only (game facts go to the vault). Format: date · task · trigger → rule → check · status.

- 2026-10-21 · 003 · Phase A was cut off twice by session/usage limits and had to be reconstructed → Append a
  progress line to the task log after each major step (brief sent, Codex done, verified, tests run) → check:
  log has a line per step; a resumed agent can continue from the log alone. · active
- 2026-10-21 · 003 · Headless write into the PoB install found (A0) → Every new PoB call path gets a check that
  nothing is written outside Builds\AutoBuilder\ (guard hook covers Claude tools, not scripts) → check: test
  or audit run with a before/after listing of the PoB install. · active
