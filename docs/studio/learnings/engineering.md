# Engineering department — lessons
Process lessons only (game facts go to the vault). Format: date · task · trigger → rule → check · status.

- 2026-10-21 · 003 · Phase A was cut off twice by session/usage limits and had to be reconstructed → Append a
  progress line to the task log after each major step (brief sent, Codex done, verified, tests run) → check:
  log has a line per step; a resumed agent can continue from the log alone. · active
- 2026-10-21 · 003 · Headless write into the PoB install found (A0) → Every new PoB call path gets a check that
  nothing is written outside Builds\AutoBuilder\ (guard hook covers Claude tools, not scripts) → check: test
  or audit run with a before/after listing of the PoB install. · active
- 2026-10-23 · 003 · GATE 2 loop 1 FAIL: 3 of 5 HIGH came from hand-made fixtures (synthetic `FullDPS: 0` while PoB
  drops the key; pre-rounded 7.58 input; inf → null crash in the GUI only) → Test PoB edge cases with real PoB output:
  missing keys, raw values, inf/NaN in Python and GUI → check: fixture comes from an engine run. · promoted
- 2026-10-23 · 003 · GATE 3: new report keys (base.costs, scenario.conditional) not in the golden snapshot, so
  runEquivalence went false silently → Extend golden_common.audit_snapshot in the same change → check:
  pin_golden --verify-run shows runEquivalence.equal true. · promoted (with the line above)
