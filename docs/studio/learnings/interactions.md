# Interactions department — lessons
Process lessons only (game facts go to the vault). Format: date · task · trigger → rule → check · status.

- 2026-10-22 · 009 · Blind test: Three Dragons chaos shock on FR crits answered "likely, not confirmed" although
  every link was sourced → A chain of sourced links (PoB source/data, wiki API) is VERIFIED; don't wait for a
  community test → check: list each link with its source; if all are sourced, state "verified (chain)". · active
- 2026-10-22 · 009 · Blind test: FR projectiles hitting a boss estimated 4 of 6 (67%); user reveal ~60% for
  FR, Fireball and AoE-explosion skills → For hit-fraction models, look for the player-community norm per skill
  family before calibrating from geometry → check: model note cites a norm or says "no norm found". · active
- 2026-10-21 · 003 · The user had to ask the follow-up questions (breakpoints, projectile count, shock) that
  produced most of the gains → For every build, ask "what does PoB not count here?" per skill part, trigger
  breakpoint and ailment before saying "no improvement" → check: interaction map has a "PoB doesn't count" row. · active
- 2026-10-22 · 003 · GATE 4 loop 1 FAIL (M2): draft Arcane Surge rule with `when.linked_support_any` silently
  protected the gem from swaps (Worb 425 → 340 tried) → Trace how the engine reads every rule field before release
  → check: re-run one golden build, diff the "N tried / N break a rule" line. · promoted
- 2026-10-22 · 003 · GATE 1 conditions named no single-projectile build, so "1 Projectile" undervaluing Greater Volley
  surfaced only at GATE 4 → One test build per skill-part variant in scoring-change conditions → check: the gate
  lists each test build's part. · promoted
