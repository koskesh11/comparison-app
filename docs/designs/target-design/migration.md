<!-- Reference part of ../target-design.md: Section 7. Migration order. -->

## 7. Migration order

Plain words: 23 small steps, each one a pull request that is merged only when the checks pass. The order is "tools first,
then remove what is frozen, then move files with the logic untouched, then fix the weak spots, then the UI, then the new
feature". After every step the app is started by hand and one analysis and one comparison are run. Each step lists what
moves, what must stay green (by today's file names; a step that moves a test also renames it as in section 2), the risk
and how to undo it. Undo is always `git revert` of the step's merge; special cases are noted. `python tools/run_tests.py --all`
is the full run on your PC; from step 1 `python -m pytest` runs the same tests.

**Step 0. Anchor.**

- Moves: nothing. Creates the tag `frozen/2026-10-27` on the current head and runs the full baseline (`python tools/run_tests.py --all`), saving the list of files, test counts and skips in the pull request as "what green means".
- Green: it defines green.
- Risk: none; the run needs PoB and your builds and takes minutes.
- Undo: delete the tag.

**Step 1. Tooling, no code moves.**

- Changes: adds `pyproject.toml` (project data, ruff, pytest, mypy and import-linter settings), `tests/conftest.py` (markers and auto-skip), `tools/check.py`, `tools/check_file_sizes.py` (report-only), `.gitignore`. One separate commit runs `ruff format` over `engine/`, `tests/`, `tools/` and adds `.git-blame-ignore-revs`; it also fixes the three collapsed lines.
- Green: the same counts as step 0 from both runners. The existing `unittest` classes are collected by pytest as they are; if a file needs a one-line import fix, it is made here.
- Risk: low; formatting is noisy in `git blame` (hence the ignore file). `tests/golden.json` stores engine file hashes for information only; `test_golden.py` compares build, note and number hashes.
- Undo: revert both commits.

**Step 2. Freeze.**

- Moves out of `main` (they stay in the tag): `optimize.py`, `guide_apply.py`, `tree_search.py`, `unobtainable.py`; the suggestion methods and the command-line printer of `audit.py`; the preview and apply parts of `guide_routes.py` and `server.py`; the 14 frozen Lua endpoints; the suggestion, apply and tick / preview / save parts of `gui/index.html`; the frozen tests; the files listed under "also leaving". `tests/pin_golden.py --verify-run` and `tests/perf_baseline.py` are adapted (they called a full `Auditor.run()` with suggestion sections).
- Green: everything that is left: `test_server_errors.py`, `test_server_security.py`, `test_gui_safety.py`, `test_golden.py`, `test_guide_check_pob.py`, `test_guide_lua.py`, `test_guide_checks.py`, `test_guide_gate2.py`, `test_guide_gate4_diff.py`, `_rank`, `_why`, `test_part_variants.py`, `test_costs.py`, `test_scoring.py`, `test_rules.py`.
- Risk: medium. Kept code lives in files shared with frozen code, and the old UI loses its suggestion screens, so it needs a by-hand run: pick a build, run an analysis, run a guide check, look at the reservation panel.
- Undo: revert, or `git checkout frozen/2026-10-27 -- <file>`.

**Step 3. Make `engine/` a package.**

- Moves: `engine/*` becomes `src/autobuilder/*` in one `git mv` (Python and Lua still side by side); `__init__.py`, `__main__.py`; every `import x` becomes `from autobuilder import x`; the 35 `sys.path` edits in five spellings are deleted; `Start Autobuilder.bat` runs `python -m autobuilder`; a temporary `autobuilder/paths.py` holds the project, Lua and data folders instead of the `__file__`-derived constants of 8 modules; the untracked folders `engine/userdata` and `engine/cache` move once, by hand, to `userdata/` and `userdata/cache` (keep your `build_settings.json`); `tools/run_tests.py` learns the folders.
- Green: the whole suite.
- Risk: medium-high but mechanical. A wrong constant silently reads an empty folder (`load_scenarios()` would return nothing), which `test_golden.py`, `test_server_security.py` and `test_gui_safety.py` catch loudly; `GUI_FILE`, the token file, the settings file, the league cache, the log folder and the Lua folder are each re-derived.
- Undo: revert the one commit and move the two folders back.

**Step 4. `vault/` becomes `mechanics/` (folder only).**

- Moves: `git mv vault mechanics`; the notes path in `paths.py`; the `vault/` rules in `tools/run_tests.py`; `workspace.json` is untracked. No note text is edited.
- Green: `test_golden.py` (note hashes are keyed by `Rules/<name>.md`, not by the top folder, so they still match), `test_rules.py`, `test_costs.py`, `test_obtainability.py`, `test_guide_gate4_why.py`.
- Risk: low, with one human step: open `mechanics/` as the vault in Obsidian (window state does not carry over). Note texts that still say "vault" are fixed in step 21 with a re-pin.
- Undo: `git mv` back.

**Step 5. Domain errors and job stages (no moves).**

- Changes: adds `errors.py` (BadLink, Unreadable, TooLarge, FetchFailed, StaleBuild, PobError ...) split from `api_errors.py`, `pobbin.py`, `guide_check.py`, `pobhost.py`; `api_errors.py` keeps the HTTP errors and an explicit mapping table in `classify`; the two `StaleAudit` classes become one `StaleBuild`; adds `progress.py` with `Stage`; the job and the page use stage ids; the `assert` that guards a production rule (`guide_check.py:323`) becomes an error.
- Green: `test_server_errors.py`, `test_pobbin.py`, `test_guide_gate2.py` (stuck job), `test_guide_check_pob.py`, `test_gui_safety.py`.
- Risk: low to medium. Error `kind` strings and stage names are part of the browser contract, so the page's strings change in the same commit.
- Undo: revert.

**Step 6. `mechanics/` (code).**

- Moves: `vault.py`, the loader half of `models.py`, `vault_note_status` and `load_named_gap_patterns` from `guide_interactions.py`, `_load_overrides` from `obtainability.py` become `mechanics/{notes,rules,scenarios,models,gaps}.py`; `load_notes(dir)` returns one `MechanicsNotes`; the import-linter contract gets its first lines (`mechanics` imports only `errors`). New tests `test_notes_loading.py` and `test_real_notes_parse.py`.
- Green: `test_rules.py`, `test_costs.py`, `test_scoring.py`, `test_obtainability.py`, `test_guide_gate4_why.py`, `test_golden.py`.
- Risk: low to medium; many modules import `vault`.
- Undo: revert.

**Step 7. `pob/` (Python, and the Lua files flat).**

- Moves: `pobhost.py` becomes `pob/lua_host.py` and `pob/write_guard.py`; `engine_pool.py` becomes `pob/pool.py`; every Lua file moves, still flat, into `pob/lua/` (`pob_headless.lua` to `boot.lua`, `write_sandbox.lua` to `sandbox.lua`, the copied PoB stub to `vendor/`); `ENGINE_DIR` becomes `LUA_DIR` in Python and Lua. Tests `test_pobhost_write_guard.py`, `test_write_sandbox.py`, `test_engine_pool.py`, `test_headless_filesearch.py` move to `tests/pob/`.
- Green: those four, `test_guide_lua.py`, and `test_golden.py`, whose bit-identical numbers prove the Lua still loads.
- Risk: medium. The `dofile(ENGINE_DIR .. "/x.lua")` chains and the tests that name Lua files by path break first; the allowed write roots of the guard and sandbox do not change.
- Undo: revert.

**Step 8. `analysis/` (the pure parts).**

- Moves: `costs.py` (split into margins and conditions), `scoring.py` (the number functions; its text helpers wait for step 17), `rules.py` to `analysis/checks/rules.py`, the apply half of `models.py` to `mechanic_models.py`, `part_variants.py` into `skills.py`; `display.py` to `app/present/numbers.py`. `analysis` still imports `numbers`; those imports are listed under `ignore_imports` in the contract and each is removed in step 17.
- Green: `test_costs.py`, `test_scoring.py`, `test_rules.py`, `test_part_variants.py`, `test_display.py`, `test_golden.py`, `test_fulldps_fallback.py`.
- Risk: low (pure functions).
- Undo: revert.

**Step 9. `compare/`.**

- Moves: the 14 `guide_check*` and `guide_diff*` modules plus `guide_interactions.py` and `guide_lua.py` go to `compare/` as in the table (`guide_check.py` becomes `service.py` and `testing.py`; `guide_diff.py` becomes `diff/__init__.py` and `diff/context.py`; `guide_lua.py` becomes `target.py`). The 730- and 729-line test files are split by behaviour into `tests/compare/`.
- Green: `test_guide_diff.py`, `test_guide_gate4_diff.py`, `_rank`, `_why`, `test_guide_check.py`, `test_guide_check_fr.py`, `test_guide_check_mageblood.py`, `test_guide_check_pob.py`, `test_guide_checks.py`, `test_guide_lua.py`, `test_guide_gate2.py`, `test_golden.py`.
- Risk: medium. It is the largest file count, and `compare` still imports `audit` (`Auditor`, `NO_WORSE_PCT`) until steps 15 and 17; those imports are listed in the contract's ignore list.
- Undo: revert.

**Step 10. `intake/` and `league/`.**

- Moves: `pobbin.py` becomes `intake/{pobbin,code,store}.py`; `list_builds` and `resolve_build` leave `server.py` for `intake/library.py`; `obtainability.py` becomes `league/{client,obtainability}.py`. One deliberate behaviour change: offline, league data is "unknown" instead of an exception (the availability code already handles empty data). A trimmed league fixture replaces the local 3 MB cache in tests.
- Green: `test_pobbin.py`, `test_obtainability.py`, `test_guide_check.py` (availability), `test_server_security.py`.
- Risk: low.
- Undo: revert.

**Step 11. `app/`.**

- Moves: `server.py` becomes `app/server.py` and `app/security.py`; the request parsing of `guide_routes.py` and `server.py` becomes `app/inputs.py`; the routes become `app/routes/*`; the thread code becomes `app/runner.py` and `app/jobs.py` (dictionary-based for now); `api_errors.py` becomes `app/errors.py`; `build_settings.py`; `runlog.py` becomes `app/logging_setup.py`, and domain code logs through the standard `logging` module. The old routes `/api/audit` and `/api/guide-check` stay. Tests `test_server_security.py`, `test_server_errors.py`, `test_runlog.py` and the route classes of `test_guide_gate2.py` move to `tests/app/`.
- Green: those.
- Risk: medium. They patch module globals (`server.API_TOKEN`, `server.pool`), which keep working until step 16.
- Undo: revert.

**Step 12. The Lua registry and `PobSession.call`, added beside the old calls.**

- Moves: nothing is removed. Adds `rpc.lua` and `loader.lua`; registers every kept endpoint under its new dotted name while the old global functions still exist; adds `pob/endpoints.py`, `pob/session.py` (`call` through the C API) and `pob/wire.py`. A temporary parity test calls every endpoint both ways on one build and compares the JSON.
- Green: `test_golden.py`, `test_guide_lua.py`, `test_guide_checks.py`, new `test_lua_host_errors.py` and `test_rpc_registry_matches_docs.py`.
- Risk: medium (C-API details: stack handling, the error handler), but nothing depends on it yet.
- Undo: delete the new files.

**Step 13. Switch the callers; delete the string-built calls.**

- Moves: `Auditor.call`, `guide_lua._call`, `guide_check_eval._swap` and `_apply_path`, and the raw snippets (`guide_check_eval.py:75,138`, `guide_check.py:328`) use `session.call`; `_lua_str` disappears from every module and test that imports it (4 modules and 6 tests today, 3 modules once the frozen code is gone); the `evaluateJSON` override becomes `compare.evaluate_change`; `ensure_loaded` and the `type(snapshotJSON)` probe go; `audit.lua` is split into `calc / state / facts / gear_mods`; the `AuditCore` and `GuideCore` globals become values returned by `dofile`; the old global `*JSON` functions are removed.
- Green: `test_golden.py` (bit-identical numbers), `test_guide_lua.py`, `test_guide_checks.py`, `test_guide_check_pob.py`, `test_write_sandbox.py`.
- Risk: high, because this is the bridge every number crosses. One caller per commit; the parity test stays until the last caller has moved.
- Undo: revert the last commit; callers are independent.

**Step 14. Context managers and the effect check.**

- Moves: `scenario()`, `left_out()` and `discarding_changes()` replace `load_audit_hooks` and `restore_player`; `call` refuses a `persistent` endpoint outside `discarding_changes()`.
- Green: `test_golden.py`, new `test_session_restores_state.py`, `test_guide_check_pob.py` (compound changes and zero-row re-tests), `test_guide_checks.py`.
- Risk: medium. Some effects are classified wrongly today (for example `applyChangesJSON` also restores skills and config); the check will show where.
- Undo: revert.

**Step 15. `BuildSession` replaces `Auditor`.**

- Moves, in this order: (a) league data leaves the constructor; the runner loads it and passes it to `compare`; (b) report assembly goes to `analysis/report.py` and the setup order to `scenario_setup.py`; (c) `models_not_applied` becomes `without_models()` and the server stops overwriting `source_sha256`; (d) `Auditor` is renamed `BuildSession` and its 12 users are updated.
- Green: `test_golden.py`, `test_guide_check_pob.py`, `test_guide_gate2.py`, `test_guide_gate4_why.py`, `test_fulldps_fallback.py`, `test_part_variants.py`; `golden_common.offline_auditor` no longer patches `Obtainability.load`.
- Risk: high (101 uses in 12 modules today, fewer once the frozen modules are gone); (a) to (c) happen while the class is still called `Auditor`, and (d) is a mechanical rename at the end.
- Undo: revert (d) alone, or the whole step.

**Step 16. `Settings`, `AppState`, `JobStore`.**

- Moves: `app/settings.py`, `state.py`, `jobs.py` (replacing the dictionaries), `main.py`; `paths.py` is deleted; the module globals go; a new `POST /api/analyze` runs the job, with the two old routes kept as thin wrappers until step 19 so the old page keeps working.
- Green: `test_server_security.py`, `test_server_errors.py`, `test_runlog.py`, `test_guide_gate2.py`, new `test_job_store.py`, `test_settings.py`, `test_request_parsing.py`.
- Risk: medium; it touches every route.
- Undo: revert.

**Step 17. One metric model and findings.**

- Moves, in sub-steps: (a) `thresholds.py` replaces the five copies of the 0.1 % cut-off; (b) `MetricVector` and `delta` replace `dimensions()` and the deltas in `build_result()`; (c) rule and cost checks return `Finding`; (d) `app/present/report.py` and `numbers.py` take over every sentence and every rounding, and the `analysis -> app` entries leave the contract's ignore list one by one.
- Green: `test_golden.py` (numbers unchanged; strings that moved are re-pinned in the same commit), `test_rules.py`, `test_costs.py`, `test_scoring.py`, `test_part_variants.py`, `test_guide_gate4_rank.py`, `test_display.py`, new `test_metric_vector.py`, `test_findings.py`, `test_number_format.py`.
- Risk: medium to high. Wire shapes change, so `present/report.py` keeps an adapter for the old page until step 19. One visible effect to announce: a -0.05 % change prints "-0.1 %" in the page and "0.0 %" in the CLI today; after this step it prints "0.0 %" everywhere (truncate toward zero).
- Undo: revert the sub-step.

**Step 18. Web: static route and split into modules (no behaviour change).**

- Moves: `web/` with `index.html` as a shell, the CSS files and the JS modules cut from the already trimmed `gui/index.html`, as in section 6; `app/static.py` with the allow-list; `GUI_FILE` goes; `test_gui_safety.py` becomes `tests/web/test_ui_safety.py` and scans every module; new `test_ui_modules.py`, `test_static_files.py`.
- Green: those, `test_server_security.py`; by hand, one analysis and one comparison in the browser.
- Risk: medium. The functions share two global objects, so they are kept as two stores at first.
- Undo: revert; `gui/` returns.

**Step 19. Web: fixes, each with a test.**

- Moves: `pollJob` with error handling replaces the two pollers; one formatter family and the shared `format_cases.json`; thresholds and stage names come from `GET /api/meta`; the pobb.in pattern and error-kind lists leave the page; strict CSP; self-hosted fonts; the page uses `POST /api/analyze` and the two old routes are deleted.
- Green: `format.test.mjs`, `test_number_format.py`, `test_ui_safety.py`, `test_api_security.py`.
- Risk: low to medium. A strict policy rejects what it does not know (read the browser console by hand once), and the fonts must be licence-compatible (both are under the SIL Open Font License; confirm when the files are added).
- Undo: revert; the policy can be relaxed by one line while debugging.

**Step 20. Tests finished.**

- Moves: the remaining tests are renamed and moved as in section 2; markers are on every PoB and owner test; the portable fixtures arrive (builds you approve, open question 2, and the trimmed league data); `tools/run_tests.py` and the new `tools/testmap.py` are rewritten for packages and markers; the scripts move to `tools/`; `tests/__init__.py` goes.
- Green: `python -m pytest -m "not pob and not owner and not slow"` passes on a clean checkout with no PoB (the new gate), and the full run on your PC matches step 0's counts plus the new tests.
- Risk: low.
- Undo: revert.

**Step 21. Docs and words.**

- Moves: `docs/ARCHITECTURE.md` (the diagram, the layers, the endpoint table, the words we use), `docs/DECISIONS.md`, the README rewrite, `docs/history/`; the wording pass (guide becomes target; vault becomes mechanics in the page and in notes that name `engine/audit.py` or `tasks/`); `tools/pin_golden.py` gets a `--notes-only` option so a text change in a note re-pins the note hashes without running PoB.
- Green: `test_rpc_registry_matches_docs.py`, `test_golden_numbers.py` (note hashes, re-pinned in the same commit), `test_real_notes_parse.py`.
- Risk: low; without the re-pin `test_golden` reports "notes changed".
- Undo: revert.

**Step 22. The analyzer feature (its own plan).**

- Moves: nothing; it adds `pob/lua/analysis/vectors.lua` (from the 2026-10-26 prototype), `analysis/vectors.py`, `compare/vectors.py`, `analysis/checks/{sustain,config}.py`, `views/analyzer/{vectors,drilldown,checks}.js`, then alternatives. It starts with a spike: reproduce the Worb comparison with two `BuildSession` objects and check the output against the prototype's numbers (for example Worb 1,435,204 and the target 2,967,940 total DPS).
- Green: everything above plus the new tests in section 2.
- Risk: the unsettled points in Appendix A.
- Undo: the views and endpoints are additive; remove them.

