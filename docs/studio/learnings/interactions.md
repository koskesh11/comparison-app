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
- 2026-10-24 (user exercise, Voltaxic Rift + Foulborn Three Dragons autobomber): idea → verified interaction graph
  works with wiki API + PoB Uniques + wiki cargo stat ids (local vs global decided that the herald storm converts to
  chaos). Method: docs/designs/idea-to-build-research.md. User: "learn from this" → promoted into interactions-lead
  and mechanics-researcher prompts.
- 2026-10-24 (010 GATE 4 FAIL): GATE 1 map missed tattoos/runegrafts → one row per PassiveSpec override field ·
  promoted. Missed a player-side cluster jewel on a replace row (H4) → check item kind on both sides + test vs apply
  PoB call · promoted. Reason-fix acceptance looked only at the top row → ≥3 rows, different categories · promoted.
  Gate note misattributed nodes to the wrong cluster jewel → verify ownership via the socket/subgraph · active.
- 2026-10-25 (027, user): judge an interaction against the damage/defence order of operations (wiki Damage, Receiving damage, Defences + PoB diff) - every note names its pipeline step.

## Promoted
Already in the agent prompts (tools/make_agents.py); kept for the record, not counted as active.

- 2026-10-22 · 003 · GATE 4 loop 1 FAIL (M2): draft Arcane Surge rule with `when.linked_support_any` silently
  protected the gem from swaps (Worb 425 → 340 tried) → Trace how the engine reads every rule field before release
  → check: re-run one golden build, diff the "N tried / N break a rule" line. · promoted
- 2026-10-22 · 003 · GATE 1 conditions named no single-projectile build, so "1 Projectile" undervaluing Greater Volley
  surfaced only at GATE 4 → One test build per skill-part variant in scoring-change conditions → check: the gate
  lists each test build's part. · promoted
- 2026-10-24 (user correction): interaction specialists unused since 10-23 (leads did the research themselves under the
  token cap "do small items yourself, max 2") → user unhappy: specialised knowledge never called on → routing table
  in interactions-lead (game facts → owning specialist, up to 4 in parallel, every map row names its source) · promoted.
- 2026-10-26 · 027 (user correction 02:2x) · a headless removal delta was stated as a game fact (EK hit chance) → name
  the item source, PoB's single-enemy model and what PoB keeps after a removal (2c: emptied slot keeps its gems,
  CalcSetup.lua:1605-1608; ticked flasks stay on) · promoted.
- 2026-10-26 · 027-1d/3d · tree.lua:59355 given to the wrong notable; Cospri "unparsed" read from the range text
  "(80-120)%" (recurs the 10-25 "quote the exact ModCache form") → cite the rolled-value ModCache line and the ["name"]
  line above a quoted tree.lua line · promoted.
- 2026-10-26 · 027-3d · engine-path claim ("only P2 reaches cantMeasure") without tracing the item kind's branch → cite
  the deciding audit.py line for that branch (unique / crafted / plain).
- 2026-10-26 · 027-4e · curator blamed another note for problems=1 (its own pipeline_step ["none"]) → run the validator
  yourself and grep its output for the new note names before accepting a curator reply.
- 2026-10-26 · 027-2c · saved partial brief named no item list, so the resumed lane rebuilt its pick list → before
  saving work as partial, write the exact item list and every output file into the brief.
- 2026-10-26 · 035 (user blind test: his 2-minute correction) · the seed had no curse group and GATE 1 no debuff row
  (Flammability alone +29.8%) → one GATE 1 row per build layer for a seed without a sample · promoted.
- 2026-10-26 · 035 · a GATE 1 hand estimate ("not league-start") became the seed claim "MoM is the main route" and
  closed Determination + Flesh and Stone (+25.6% EHP) → name/close a route only with headless numbers for 2+ routes ·
  promoted.
- 2026-10-26 · 035 · Immolate never a candidate and enemy Ignited never in the map (+43.2% TotalDPS together; ignite
  chance 40.86%, uptime ~100%); "non-crit" taken from the gem, PoB showed 21.15% crit → row per caused enemy
  condition, conditional candidates tested with it, crit label from PoB's crit share · promoted.
- 2026-10-26 · 035 · Added Fire Damage scored exactly 0 for Fireball (no physical damage) yet stayed in the 6-link →
  flag a candidate that scores 0 for its skill as dead · active (engine check in the 035 loop-2 spec).
