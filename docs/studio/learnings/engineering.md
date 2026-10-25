# Engineering department — lessons
Process lessons only (game facts go to the vault). Format: date · task · trigger → rule → check · status.

- 2026-10-21 · 003 · Phase A was cut off twice by session/usage limits and had to be reconstructed → Append a
  progress line to the task log after each major step (brief sent, Codex done, verified, tests run) → check:
  log has a line per step; a resumed agent can continue from the log alone. · active
- 2026-10-21 · 003 · Headless write into the PoB install found (A0) → Every new PoB call path gets a check that
  nothing is written outside Builds\AutoBuilder\ (guard hook covers Claude tools, not scripts) → check: test
  or audit run with a before/after listing of the PoB install. · active
- 2026-10-23 · 004 · GATE 2: apply started rebuilding an Auditor and silently gained a network call
  (Obtainability.load) → When a path starts constructing an object, list what its constructor fetches and pass it
  in → check: run the path with the fetch patched to raise. · active
- 2026-10-23 · 004 · GATE 2: rewrite flipped engine/server.py CRLF → LF (whole-file diff); Python write_text turned
  LF files into CRLF → Byte-level edits; match main's eol → check: `git ls-files --eol` on every changed file vs main.
  · active
- 2026-10-24 (010 GATE 4 loops 1-2): why-lines hid every loss ("+ lines cut at 4") → show losses, test on the 3 most
  negative real rows · promoted. Test ≠ apply (calc-only jewel swap kept cluster passives, H4) → list test-vs-apply
  differences per swap · promoted. Interrupted run left ~43 stray deletions → `git status | grep '^ D'` empty before
  commit · promoted. Cluster node ownership: read spec.subGraphs, not node ids · active.
- 2026-10-24 (from review, 010 re-review): sort/score rule changed but GUI tooltip kept old wording → grep gui/ for the
  old description · active. A verdict derived from a PoB list (curse "limit full" = len(curseSlots)) must use PoB's
  own rule (CalcPerform) · active.
- 2026-10-24 (024): subprocess stdout pipe deadlocked on chatty PoB output → child output to a temp file + per-job
  timeout · active. Fresh worktree lacks gitignored engine/cache (6 files fail) → junction from main · promoted.
  Baseline measured on an old base (170 vs 395 tests) → rebase onto main and compare test counts first · active.
- 2026-10-24 (025): Bash heredocs halve backslashes (broke Lua escapes) → write backslash content via a Python patch,
  then grep the file · active. mklink in a worktree printed a banner but no link (17 files failed) → `ls engine/cache`
  after linking · active.

- 2026-10-25 · 028 · A scripted prompt edit matched OLD strings exactly and left two bullets mis-indented; the
  tag test caught one → after a scripted prompt edit, regenerate and run tests/test_agents.py before reading diffs
  → check: that test run's summary line. · active
- 2026-10-25 · 021 M3 · run_tests output piped through head hid 3 new failures until --all → read the runner's
  summary line, never a truncated list → check: grep 'files,' and FAIL in a saved output file. · active
- 2026-10-25 · 021 M3 · the 150 s critical path was one class re-running the same real job 5x → same real job
  twice in a class = setUpClass → check: per-test timings grouped by identical setup. · active

## Promoted
Already in the agent prompts (tools/make_agents.py); kept for the record, not counted as active.

- 2026-10-23 · 003 · GATE 2 loop 1 FAIL: 3 of 5 HIGH came from hand-made fixtures (synthetic `FullDPS: 0` while PoB
  drops the key; pre-rounded 7.58 input; inf → null crash in the GUI only) → Test PoB edge cases with real PoB output:
  missing keys, raw values, inf/NaN in Python and GUI → check: fixture comes from an engine run. · promoted
- 2026-10-23 · 003 · GATE 3: new report keys (base.costs, scenario.conditional) not in the golden snapshot, so
  runEquivalence went false silently → Extend golden_common.audit_snapshot in the same change → check:
  pin_golden --verify-run shows runEquivalence.equal true. · promoted (with the line above)
- 2026-10-25 · 021/029 · Line endings flipped twice (4 files LF to CRLF; make_agents.py CRLF to LF), hiding the real
  diff (also review lesson 004) → after each commit `git diff --stat` equals `--ignore-cr-at-eol` → check: equal
  stats · promoted (CODEX_NOTE "Line endings").
- 2026-10-25 · 029 · Bash heredocs halve backslashes and truncate long text → write patch scripts with placeholders;
  check `ast.parse` after each edit · active.
- 2026-10-25 · 021 · A test that patches the rating function must count its calls (that is how the post-restore rate
  showed as fail-before) · active.
