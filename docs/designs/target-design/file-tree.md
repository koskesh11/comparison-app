<!-- Reference part of ../target-design.md: Section 2. The complete target file tree. -->

## 2. The complete target file tree

Plain words: the program moves into `src/autobuilder/`, split into seven folders by job. The browser pages get their own
top-level folder, `web/`. The tests mirror the program's folders. Your notes keep their format and become `mechanics/`.
Where a file comes from is in the last column, so you can see that almost all logic is today's code in a new place.

```
pob-autobuilder/
  pyproject.toml  README.md  LICENSE  Start Autobuilder.bat  .gitignore  .github/workflows/ci.yml
  src/autobuilder/
    __main__.py  errors.py  progress.py
    app/         web server, jobs, settings, the words shown in the browser      (20 files)
    pob/         the bridge to Path of Building: Python here, Lua in pob/lua/    (7 + 21 files)
    mechanics/   the code that reads the notes folder                            (6)
    analysis/    one build: numbers, scaling vectors, checks                     (17)
    compare/     your build against a target build                               (19)
    intake/      how a build gets in: Builds folder, pobb.in link, pasted code   (5)
    league/      league and gem availability data from the internet              (3)
  web/           index.html, css/, js/, fonts/  (replaces gui/)                  (26)
  tests/         mirrors src/; helpers/ and fixtures/                            (75)
  tools/         test runner, the one check command, golden pinning              (7)
  docs/          ARCHITECTURE, DECISIONS, designs/, history/                     (9)
  mechanics/     the notes (an Obsidian vault), renamed from vault/              (227)
```

How to read the tables: **Lines** are estimates (`~`) for new or reshaped files and exact numbers for files that move
unchanged. **From** names today's file; a bare name means `engine/<name>` (in the tests tables, `tests/<name>`).
Groups L1-L4 are one folder, `tests/`, split only to keep the tables short.

### A. Repository root

**7 files, about 371 lines.** By folder: root 6, `.github/workflows/` 1.

| Path | Job | Lines | From |
|---|---|---:|---|
| `pyproject.toml` | Project name, version, dependencies and the settings of every tool (ruff, mypy, pytest, import-linter); build backend hatchling, which ships the `.lua` files with the package (assumption; setuptools with package data also works) | ~170 | new; replaces requirements.txt |
| `README.md` | What the app does, how to start it, a map of the folders | ~90 | rewrite of README.md (82) |
| `LICENSE` | MIT licence | 21 | unchanged |
| `Start Autobuilder.bat` | Double-click start: runs `python -m autobuilder` | ~12 | changed (5) |
| `.gitignore` | What git ignores: runtime data, caches, the AI-workflow files | ~30 | changed (19) |
| `.git-blame-ignore-revs` | Hides the one formatting-only commit from `git blame` | ~3 | new |
| `.github/workflows/ci.yml` | Runs every check that needs no PoB on each push (optional) | ~45 | new |

### B. Python package, top level (`src/autobuilder/`)

**4 files, about 129 lines.** By folder: `src/autobuilder/` 4.

| Path | Job | Lines | From |
|---|---|---:|---|
| `src/autobuilder/__init__.py` | Package marker and version string | ~4 | new |
| `src/autobuilder/__main__.py` | `python -m autobuilder` starts the app | ~10 | new |
| `src/autobuilder/errors.py` | The errors any package may raise (BadLink, TooLarge, FetchFailed, StaleBuild, PobError ...); no HTTP in here | ~70 | split from api_errors.py, pobbin.py, guide_check.py, pobhost.py (`StaleBuild` is new) |
| `src/autobuilder/progress.py` | The list of job stages (`Stage`) and the progress-reporter type, shared by domain code and the job store | ~45 | new |

### C. `app/` : the web server, jobs, settings and the words shown to the browser

**20 files, about 1,842 lines.** By folder: `app/` 13, `app/routes/` 4, `app/present/` 3.

| Path | Job | Lines | From |
|---|---|---:|---|
| `src/autobuilder/app/__init__.py` | Package marker | ~1 | new |
| `src/autobuilder/app/main.py` | Composition root: read settings, build the app state, start the server, open the browser | ~70 | server.py (`main`) |
| `src/autobuilder/app/settings.py` | `Settings`: every folder, port and limit, resolved once from the environment | ~120 | new; replaces path constants in 8 modules |
| `src/autobuilder/app/state.py` | `AppState`: the settings, engine pool, job store and token handed to every handler | ~50 | new; replaces the module globals of server.py |
| `src/autobuilder/app/server.py` | HTTP handler: read the request, guard it, dispatch to a route, send JSON | ~190 | server.py (split) |
| `src/autobuilder/app/security.py` | Host, Origin and token checks, body-size caps (64 KB; 300 KB when a pasted code is sent), security headers and the Content Security Policy | ~100 | server.py (split) |
| `src/autobuilder/app/static.py` | Serves the UI files from an allow-list; puts the API token into index.html | ~90 | server.py (`_serve_gui`) + new allow-list |
| `src/autobuilder/app/errors.py` | HTTP errors and the table that maps domain errors to a status code and a stable `kind` | ~90 | api_errors.py (HTTP half) |
| `src/autobuilder/app/inputs.py` | Turns the browser's JSON into typed requests; rejects anything malformed | ~150 | guide_routes.py, server.py (request parsing) |
| `src/autobuilder/app/jobs.py` | `JobStore`: create, update, finish and expire jobs; keeps only the last N finished ones | ~140 | server.py (`jobs`), guide_routes.py (JobProgress, expiry) + new eviction |
| `src/autobuilder/app/runner.py` | Runs one analysis on a worker thread: lease a PoB engine, call the domain, store result or error | ~140 | server.py (`run_audit`), guide_routes.py (`run_guide_job`) |
| `src/autobuilder/app/build_settings.py` | Remembers each build's scenario and left-out skills; atomic write, survives a corrupt file | ~60 | build_settings.py (25) + lock and atomic write |
| `src/autobuilder/app/logging_setup.py` | Daily JSON-lines log with secrets removed; attaches to the standard `logging` tree | ~110 | runlog.py |
| `src/autobuilder/app/routes/__init__.py` | The route table: path and method to handler | ~25 | new |
| `src/autobuilder/app/routes/builds.py` | `GET /api/meta` (scenarios, thresholds, stage names, capability) and `GET /api/builds` | ~70 | server.py (`_get_route`) |
| `src/autobuilder/app/routes/analysis.py` | `POST /api/analyze`: validate, create a job, start the runner | ~100 | server.py (`_start_audit`), guide_routes.py (`start_check`) |
| `src/autobuilder/app/routes/jobs.py` | `GET /api/jobs/{id}`: the public view of a job | ~50 | server.py (`public_job`, job route) |
| `src/autobuilder/app/present/__init__.py` | Package marker | ~1 | new |
| `src/autobuilder/app/present/numbers.py` | PoE-style rounding (truncate toward zero) and number text; the one Python rounding rule | ~45 | display.py (34) |
| `src/autobuilder/app/present/report.py` | Turns analysis and comparison results into the JSON the browser gets, including all sentences | ~240 | scoring.py / rules.py / costs.py text helpers, guide_check.py (`_header`, `_banners`) + new |

### D. `pob/` : the bridge to Path of Building (Python side)

**7 files, about 764 lines.** By folder: `pob/` 7.

| Path | Job | Lines | From |
|---|---|---:|---|
| `src/autobuilder/pob/__init__.py` | Package marker | ~1 | new |
| `src/autobuilder/pob/lua_host.py` | Low level: load lua51.dll with ctypes, create a Lua state, run a chunk, call a function with one string | ~150 | pobhost.py (`PobEngine`, low level) |
| `src/autobuilder/pob/session.py` | `PobSession`: load a build, `call(endpoint, payload)`, and the context managers that restore state | ~170 | new (replaces generated-Lua calls) |
| `src/autobuilder/pob/endpoints.py` | `Endpoint`: the name and effect (read / temporary / setup / persistent) of every Lua endpoint | ~90 | new |
| `src/autobuilder/pob/wire.py` | Typed shapes of what Lua returns (`CalcContext`, `Snapshot` ...) and the functions that check them | ~160 | new (rules.py docstring + scattered `.get()` chains) |
| `src/autobuilder/pob/write_guard.py` | Refuses Python writes into the PoB install (process-wide audit hook) | ~75 | pobhost.py (guard half) |
| `src/autobuilder/pob/pool.py` | Pool of PoB sessions with lease / replace-on-error | 118 | engine_pool.py |

### E. `pob/lua/` : the Lua that runs inside PoB

Every endpoint is registered once in `rpc.lua`; `loader.lua` is the only place that says what is loaded and in which order.

**21 files, about 2,756 lines.** By folder: `pob/lua/` 6, `pob/lua/vendor/` 2, `pob/lua/analysis/` 7, `pob/lua/compare/` 6.

| Path | Job | Lines | From |
|---|---|---:|---|
| `src/autobuilder/pob/lua/boot.lua` | Starts PoB headless: stubs, write sandbox, zlib, PoB's own Launch.lua | ~100 | pob_headless.lua (112) |
| `src/autobuilder/pob/lua/rpc.lua` | The registry: `Rpc.register(name, fn, effect)`, `Rpc.endpoints[name]`; one place for JSON helpers | ~80 | new |
| `src/autobuilder/pob/lua/loader.lua` | Loads the analysis and compare files in a fixed order; replaces the `dofile` chains | ~40 | new (replaces audit.lua lines 468-472, guide.lua 12-13) |
| `src/autobuilder/pob/lua/build.lua` | Endpoint `build.load`: open a build file and return its summary | ~55 | pob_headless.lua (`loadBuildFromFile`, `summaryJSON`) |
| `src/autobuilder/pob/lua/sandbox.lua` | Refuses Lua file writes outside the allowed folders | 154 | write_sandbox.lua |
| `src/autobuilder/pob/lua/filesearch.lua` | File-search stub PoB needs while headless | 119 | filesearch.lua |
| `src/autobuilder/pob/lua/vendor/_SimpleGraphic.def.lua` | PoB's graphics stub, copied unchanged from PoB | 516 | _SimpleGraphic.def.lua |
| `src/autobuilder/pob/lua/vendor/README.md` | Says where the copied file comes from, its licence and PoB version | ~12 | new |
| `src/autobuilder/pob/lua/analysis/calc.lua` | Calculation core: switch main skill, `analysis.evaluate`, part variants | ~200 | audit.lua (lines 1-204) |
| `src/autobuilder/pob/lua/analysis/state.lua` | Scenario config and left-out skills: set, and restore (`analysis.set_config` ...) | ~90 | audit.lua (lines 370-445) |
| `src/autobuilder/pob/lua/analysis/facts.lua` | Read-only facts: capability keys, equipped titles, reservations | ~70 | audit.lua (lines 392-466) |
| `src/autobuilder/pob/lua/analysis/costs.lua` | Other skills' costs and consecrated-ground sources | 115 | audit_costs.lua |
| `src/autobuilder/pob/lua/analysis/gear_mods.lua` | Remove each mod line and see whether anything changes (kept only if open question 1 says yes) | ~125 | audit.lua (lines 206-327) |
| `src/autobuilder/pob/lua/analysis/explain.lua` | Which modifier sources change (`analysis.why`) and a gem's own stat changes | ~110 | audit_tree.lua (`whyJSON`), audit_gems.lua (`gemStatDiffJSON`) |
| `src/autobuilder/pob/lua/analysis/vectors.lua` | Per-vector totals and their sources for one build (own or target) | ~120 | new (shape unsettled) |
| `src/autobuilder/pob/lua/compare/target.lua` | Load, release and probe the target build; tree facts; PoB's own power rows | ~160 | guide.lua (minus the `evaluateJSON` override) |
| `src/autobuilder/pob/lua/compare/snapshot.lua` | A stable, plain snapshot of a build for the pure comparison | 207 | guide_snapshot.lua |
| `src/autobuilder/pob/lua/compare/changes.lua` | Apply or temporarily apply a difference: nodes, items, gems, groups | 330 | guide_changes.lua |
| `src/autobuilder/pob/lua/compare/evaluate.lua` | `compare.evaluate_change`: evaluate with a temporary item or gem change, undone before returning | ~60 | guide.lua (the `evaluateJSON` override, now its own endpoint) |
| `src/autobuilder/pob/lua/compare/config.lua` | Swap PoB config values for one evaluation and report the old ones | ~25 | guide_check_config.lua (21) |
| `src/autobuilder/pob/lua/compare/needs.lua` | What conditions a mod line needs; curse-limit state | 68 | audit_why.lua |

### F. `mechanics/` (code) : reads the notes folder

**6 files, about 287 lines.** By folder: `mechanics/` 6.

| Path | Job | Lines | From |
|---|---|---:|---|
| `src/autobuilder/mechanics/__init__.py` | Exports `load_notes` and `MechanicsNotes` | ~12 | new |
| `src/autobuilder/mechanics/notes.py` | Reads one note (front matter + one fenced block) and loads the whole folder; note status index | ~90 | vault.py, guide_interactions.py (`vault_note_status`) |
| `src/autobuilder/mechanics/rules.py` | `Rule` and its loader | ~35 | vault.py |
| `src/autobuilder/mechanics/scenarios.py` | Scenario notes (fight assumptions) and their loader | ~35 | vault.py |
| `src/autobuilder/mechanics/models.py` | `Model` and its loader (the calculation lives in `analysis/mechanic_models.py`) | ~35 | models.py (loader half) |
| `src/autobuilder/mechanics/gaps.py` | Gap patterns, named gap patterns and gem-obtainability overrides | ~80 | vault.py, guide_interactions.py, obtainability.py (`_load_overrides`) |

### G. `analysis/` : what PoB says about one build

**17 files, about 2,041 lines.** By folder: `analysis/` 12, `analysis/checks/` 5.

| Path | Job | Lines | From |
|---|---|---:|---|
| `src/autobuilder/analysis/__init__.py` | Package marker | ~1 | new |
| `src/autobuilder/analysis/session.py` | `BuildSession`: a build file calculated under a scenario; evaluate, main output, no network | ~230 | audit.py (`Auditor`, lines 47-232) |
| `src/autobuilder/analysis/scenario_setup.py` | Applies leave-out, scenario config and source-gated config in the fixed order; records DPS after each step | ~110 | audit.py (`load_audit_hooks`, `apply_conditional_config`) |
| `src/autobuilder/analysis/report.py` | The key numbers: DPS, EHP, max hit, margins, reservations, where each number comes from | ~210 | audit.py (`run` header, `kpi_sources`, `dps_breakdown`) |
| `src/autobuilder/analysis/metrics.py` | `MetricVector`, `Metric`, `VectorDelta`: the one way to hold and compare numbers | ~160 | new; replaces `dimensions()` and `build_result()` |
| `src/autobuilder/analysis/thresholds.py` | Every cut-off in one place: zero-change, group-under, weakens, trade-off | ~35 | new; merges five copies of the 0.1 % rule |
| `src/autobuilder/analysis/vectors.py` | The vector catalogue (increased, more, crit, penetration, enemy, speed, projectiles ...) and extraction | ~170 | new (shape unsettled) |
| `src/autobuilder/analysis/findings.py` | `Finding`, `Severity`, `Source`: what a check returns | ~70 | new |
| `src/autobuilder/analysis/costs.py` | Resource margins (regen minus costs) for Mana, Life and ES | ~150 | costs.py (margins half) |
| `src/autobuilder/analysis/conditions.py` | Source-gated config (consecrated ground): which build lines count as a source | ~150 | costs.py (`CONSECRATED_SOURCES`, `plan_conditional`) |
| `src/autobuilder/analysis/skills.py` | Per-skill DPS rows, the DPS stat choice, trigger facts, part variants | ~170 | scoring.py (numbers half), part_variants.py |
| `src/autobuilder/analysis/mechanic_models.py` | Applies `Model` notes (for example Winter Orb hit overlap) to a calculated context | ~85 | models.py (apply half) |
| `src/autobuilder/analysis/checks/__init__.py` | `run_checks(session)`: runs every check and returns findings | ~50 | new |
| `src/autobuilder/analysis/checks/rules.py` | Checks a build against the `Rule` notes; returns findings | ~150 | rules.py |
| `src/autobuilder/analysis/checks/sustain.py` | Sustainability checks (resource margins; later flask charges, charge sources) | ~90 | new; uses costs.py |
| `src/autobuilder/analysis/checks/config.py` | Config sanity checks (for example Focused Channelling with no channelling time) | ~110 | new (shape unsettled) |
| `src/autobuilder/analysis/checks/gear_mods.py` | Mod lines that change nothing in PoB, grouped by reason (kept only if open question 1 says yes) | ~100 | audit.py (`wasted_mods`) |

### H. `compare/` : your build against a target build

**19 files, about 2,746 lines.** By folder: `compare/` 13, `compare/diff/` 6.

| Path | Job | Lines | From |
|---|---|---:|---|
| `src/autobuilder/compare/__init__.py` | Package marker | ~1 | new |
| `src/autobuilder/compare/service.py` | `compare()`: load both builds, diff, test every difference, rank, explain | ~210 | guide_check.py, guide_check_log.py |
| `src/autobuilder/compare/types.py` | Typed shapes of rows, row results and the comparison | ~120 | new (replaces nested dicts) |
| `src/autobuilder/compare/target.py` | Load and release the target build in PoB; take both snapshots | ~120 | guide_lua.py, guide_check.py (`_load_pair`) |
| `src/autobuilder/compare/testing.py` | Test each difference on your build within the time limit; the reasons a row cannot be tested | ~220 | guide_check.py (test loop, untested reasons) |
| `src/autobuilder/compare/evaluate.py` | Turn a difference into a PoB evaluation; config swap; restore your build | ~140 | guide_check_eval.py |
| `src/autobuilder/compare/result.py` | A row's before / after / change, and its chips | ~100 | guide_check_result.py |
| `src/autobuilder/compare/ranking.py` | Order rows by gain; the 3 % rule (small differences grouped with a combined total) | ~80 | guide_check_rank.py + new rule |
| `src/autobuilder/compare/why.py` | Which modifier sources explain a row | ~100 | guide_check_why.py |
| `src/autobuilder/compare/notes.py` | Notes for a row: conditions it needs, curse limit, how the row was tested | ~200 | guide_check_notes.py, guide_interactions.py |
| `src/autobuilder/compare/availability.py` | Is the gem obtainable in the current league (or unknown, offline) | ~75 | guide_check_avail.py |
| `src/autobuilder/compare/config_rows.py` | Config differences: evaluate them; re-test zero rows under the target's settings | ~75 | guide_check_retest.py |
| `src/autobuilder/compare/vectors.py` | Side-by-side vectors of the two builds and which differences belong under which vector | ~150 | new (shape unsettled) |
| `src/autobuilder/compare/diff/__init__.py` | `diff()`: compare two snapshots; `tree_candidates()` | ~85 | guide_diff.py (split) |
| `src/autobuilder/compare/diff/common.py` | Shared row constructors, names, snapshot check | 143 | guide_diff_common.py |
| `src/autobuilder/compare/diff/gems.py` | Gem group, support and level differences | 265 | guide_diff_gems.py |
| `src/autobuilder/compare/diff/items.py` | Item, flask and jewel differences | 354 | guide_diff_items.py |
| `src/autobuilder/compare/diff/tree.py` | Passive tree differences | 188 | guide_diff_tree.py |
| `src/autobuilder/compare/diff/context.py` | Config differences and the banners around the rows | ~120 | guide_diff.py (split) |

### I. `intake/` : how a build gets into the app

**5 files, about 291 lines.** By folder: `intake/` 5.

| Path | Job | Lines | From |
|---|---|---:|---|
| `src/autobuilder/intake/__init__.py` | Package marker | ~1 | new |
| `src/autobuilder/intake/library.py` | List the builds in the PoB Builds folder; resolve a name to a file, confined to that folder | ~70 | server.py (`list_builds`, `resolve_build`) |
| `src/autobuilder/intake/pobbin.py` | pobb.in link parsing and the limited, same-host download | ~105 | pobbin.py (link and fetch half) |
| `src/autobuilder/intake/code.py` | Decode a PoB code (base64url + zlib) with size and markup guards; accepts pasted codes | ~70 | pobbin.py (`decode`) + new paste path |
| `src/autobuilder/intake/store.py` | Save an imported build atomically under the imports folder | ~45 | pobbin.py (`save_import`, `import_link`) |

### J. `league/` : league and gem-availability data from the internet

**3 files, about 181 lines.** By folder: `league/` 3.

| Path | Job | Lines | From |
|---|---|---:|---|
| `src/autobuilder/league/__init__.py` | Package marker | ~1 | new |
| `src/autobuilder/league/client.py` | Fetch the league name and poe.ninja gem data; cache for 24 h; offline returns nothing, not an error | ~70 | obtainability.py (fetch half) |
| `src/autobuilder/league/obtainability.py` | `Obtainability`: which gems and levels exist this league | ~110 | obtainability.py (logic half) |

### K. `web/` : the browser UI (plain ES modules, no build step)

**26 files, about 1,960 lines.** By folder: `web/` 1, `web/css/` 4, `web/fonts/` 5, `web/js/` 3, `web/js/lib/` 3, `web/js/views/` 3, `web/js/views/analyzer/` 7.

| Path | Job | Lines | From |
|---|---|---:|---|
| `web/index.html` | Shell only: sidebar, main area, one module script tag; carries the API token | ~45 | gui/index.html (lines 1-9, 239-262) |
| `web/css/tokens.css` | Colours, fonts, radii: the design variables | ~25 | gui/index.html (lines 11-30) |
| `web/css/base.css` | Layout, sidebar, buttons, chips, rows, details, small screens | ~120 | gui/index.html (CSS) |
| `web/css/analyzer.css` | Key-number tiles, vector table, drill-down rows, findings | ~200 | gui/index.html (CSS) + new |
| `web/css/progress.css` | Progress screen and stage list | ~45 | gui/index.html (CSS) |
| `web/fonts/*.woff2 (5 files)` | Cinzel and IBM Plex Sans, served by the app itself (no Google Fonts) | data | new (binary) |
| `web/js/main.js` | Start-up and the one place that decides which view is shown | ~60 | gui/index.html (lines 1336-1340) |
| `web/js/api.js` | The only code that calls `fetch`: token header, errors, `pollJob` with retry and cancel | ~120 | gui/index.html (`api`, `poll`, `guidePoll`) |
| `web/js/store.js` | A tiny state store (get, set, subscribe); no DOM nodes in state | ~50 | new (replaces `state` and `G`) |
| `web/js/lib/dom.js` | `$` and `h()`: build elements with text set through textContent only | ~35 | gui/index.html (lines 266-279) |
| `web/js/lib/format.js` | The one number-formatter family; same truncation rule as Python | ~85 | gui/index.html (two formatter families) |
| `web/js/lib/safe.js` | `arr`, `obj`, `str`, `fin`: safe reads of untrusted data | ~20 | gui/index.html (lines 867-870) |
| `web/js/views/sidebar.js` | Build list, search, scenario, left-out skills | ~110 | gui/index.html (sidebar code) |
| `web/js/views/start.js` | Pick your build, paste a target link or code, start the analysis | ~120 | gui/index.html (`renderGuideInput`) |
| `web/js/views/progress.js` | Stage list and progress bar | ~100 | gui/index.html (`updateProgress`, `stageList`) |
| `web/js/views/analyzer/index.js` | Draws the analyzer result from its parts | ~90 | new |
| `web/js/views/analyzer/header.js` | Build name, scenario, league, banners | ~70 | gui/index.html (`renderReport` header, `headerStrip`) |
| `web/js/views/analyzer/tiles.js` | Key-number tiles with the PoB values underneath | ~130 | gui/index.html (`kpiTile`, `costTiles`) |
| `web/js/views/analyzer/reservation.js` | Reservation panel: which reserving skills do you run | ~65 | gui/index.html (`reservationPanel`) |
| `web/js/views/analyzer/vectors.js` | The scaling vectors side by side, with gaps and the next step's value | ~170 | new (shape unsettled) |
| `web/js/views/analyzer/drilldown.js` | Differences under a vector: own rows for 3 % and up, one group below | ~190 | gui/index.html (`guideRow`, `numbersCell`, groups) |
| `web/js/views/analyzer/checks.js` | Config, sustainability and rule findings | ~110 | new + gui/index.html (findings group) |

### L1. `tests/` top, helpers and fixtures

Markers: **pob** = boots Path of Building; **owner** = reads the owner's own builds; **slow** = takes minutes. No marker = runs anywhere. In the From column a bare name is today's file under `tests/`.

**15 files, about 871 lines.** By folder: `tests/` 1, `tests/helpers/` 6, `tests/fixtures/` 3, `tests/fixtures/builds/` 1, `tests/fixtures/snapshots/` 3, `tests/fixtures/reports/` 1.

| Path | Job | Lines | From |
|---|---|---:|---|
| `tests/conftest.py` | Registers the markers and skips tests whose needs are missing; shared fixtures | ~90 | new |
| `tests/helpers/__init__.py` | Package marker | ~1 | new |
| `tests/helpers/golden.py` | Golden-baseline helpers: build list, fingerprints, snapshot of a session | ~330 | golden_common.py (370) |
| `tests/helpers/pob_builds.py` | Boot PoB and load a named build; decode the checked-in target code | ~130 | guide_testlib.py (130) |
| `tests/helpers/build_edits.py` | Make an edited temporary copy of a build (remove a gem, a node ...) | ~150 | guide_check_testlib.py (156) |
| `tests/helpers/snapshot_builders.py` | Small builders for hand-made snapshots | ~70 | test_guide_diff.py (lines 16-80) |
| `tests/helpers/fakes.py` | Fake PoB calculator, fake pool, fake handler, `make_state()` | ~100 | test_server_security.py (FakeHandler, FakePool) + new |
| `tests/fixtures/golden.json` | Pinned baseline numbers and note hashes | data | golden.json |
| `tests/fixtures/format_cases.json` | Number-formatting cases run by both Python and JS | data | new |
| `tests/fixtures/league_gems_small.json` | A trimmed gem list so league tests run offline anywhere | data | new (trimmed from the local 3 MB cache) |
| `tests/fixtures/builds/pobb_F8CiRC9KVADl.code.txt` | A public target build as a PoB code | data | fixtures/pobb_F8CiRC9KVADl.code.txt |
| `tests/fixtures/snapshots/ek_player.json` | Recorded snapshot of the owner's EK build | data | fixtures/snapshots/ek_player.json |
| `tests/fixtures/snapshots/worb_player.json` | Recorded snapshot of the owner's Worb build | data | fixtures/snapshots/worb_player.json |
| `tests/fixtures/snapshots/pobb_guide.json` | Recorded snapshot of the public target | data | fixtures/snapshots/pobb_guide.json |
| `tests/fixtures/reports/compare_report_ek.json` | Recorded comparison report used by the ranking tests | data | fixtures/guide_report_ek.json (renamed) |

### L2. `tests/pob/`, `tests/mechanics/`, `tests/analysis/`

**24 files, about 3,293 lines.** By folder: `tests/pob/` 9, `tests/mechanics/` 2, `tests/analysis/` 13.

| Path | Job | Lines | From |
|---|---|---:|---|
| `tests/pob/test_rpc_registry_matches_docs.py` | Lua registrations = the `Endpoint` list = the table in ARCHITECTURE.md (needs no PoB) | ~60 | new |
| `tests/pob/test_lua_host_errors.py` | Lua errors become PobError with the first line; closed host; unknown endpoint [pob] | ~70 | new |
| `tests/pob/test_session_restores_state.py` | scenario, left_out and discarding_changes put numbers back exactly [pob] | ~130 | new |
| `tests/pob/test_write_sandbox.py` | Lua cannot write outside the allowed folders [pob] | 180 | test_write_sandbox.py |
| `tests/pob/test_python_write_guard.py` | Python cannot write into the PoB install | 137 | test_pobhost_write_guard.py |
| `tests/pob/test_engine_pool_leases.py` | Lease, replace on error, close [pob in part] | 329 | test_engine_pool.py |
| `tests/pob/test_headless_file_search.py` | The file-search stub behaves like PoB's [pob] | 134 | test_headless_filesearch.py |
| `tests/pob/test_target_snapshots.py` | Probe, snapshots, tree info, PoB power rows are stable and valid [pob] | ~160 | test_guide_lua.py (read-only part) |
| `tests/pob/test_reversible_changes.py` | Item, gem and tree changes restore PoB's state; refusals restore too [pob] | ~280 | test_guide_lua.py (restore, apply, refusal parts) |
| `tests/mechanics/test_notes_loading.py` | Front matter, fenced blocks, draft vs verified, bad notes fail loudly | ~90 | new |
| `tests/mechanics/test_real_notes_parse.py` | Every note in mechanics/ loads | ~50 | new |
| `tests/analysis/test_metric_vector.py` | delta, percent, zero and missing values, thresholds | ~110 | new |
| `tests/analysis/test_findings.py` | Finding ordering, grouping, sources | ~60 | new |
| `tests/analysis/test_rule_checks.py` | Rule notes against calculated contexts; worsened rules | ~140 | test_rules.py (68) + new |
| `tests/analysis/test_resource_margins.py` | Regen minus cost for Mana, Life, ES | ~200 | test_costs.py (first half) |
| `tests/analysis/test_scenario_conditions.py` | Consecrated-ground sources and source-gated config | ~160 | test_costs.py (second half) |
| `tests/analysis/test_skill_dps_rows.py` | DPS stat choice, per-skill rows, trigger facts, models applied | ~200 | test_scoring.py (196) |
| `tests/analysis/test_part_variants.py` | Per-part values for multi-part skills | 243 | test_part_variants.py |
| `tests/analysis/test_build_session.py` | Open, evaluate, stale file, without_models [pob] | ~130 | new |
| `tests/analysis/test_dps_measure_without_full_dps.py` | Builds with every Full DPS group unticked [pob, owner] | 45 | test_fulldps_fallback.py |
| `tests/analysis/test_golden_numbers.py` | Numbers equal the pinned baseline [pob, owner] | 146 | test_golden.py |
| `tests/analysis/test_results_are_repeatable.py` | Two runs give identical numbers [pob, owner, slow] | 39 | test_determinism.py |
| `tests/analysis/test_vectors_extraction.py` | Vector values and sources for a recorded build [pob] | ~100 | new (shape unsettled) |
| `tests/analysis/test_checks_config_and_sustain.py` | Config and sustainability findings | ~100 | new (shape unsettled) |

### L3. `tests/compare/`

**19 files, about 2,842 lines.** By folder: `tests/compare/` 19.

| Path | Job | Lines | From |
|---|---|---:|---|
| `tests/compare/test_diff_gems.py` | Gem and support differences | ~190 | test_guide_diff.py (GemDiffTests) |
| `tests/compare/test_diff_items.py` | Item, flask and weapon differences | ~140 | test_guide_diff.py (ItemDiffTests) |
| `tests/compare/test_diff_tree_and_jewels.py` | Tree, jewel and override differences | ~280 | test_guide_diff.py (TreeAndJewelTests), test_guide_gate4_diff.py |
| `tests/compare/test_diff_config_and_banners.py` | Config rows, banners, determinism | ~190 | test_guide_diff.py (ConfigBannerContractTests) |
| `tests/compare/test_diff_on_recorded_snapshots.py` | The diff on the checked-in snapshots | ~200 | test_guide_diff.py (RealSnapshotTests) |
| `tests/compare/test_override_on_real_pob.py` | A tattoo override survives snapshot and diff [pob, owner] | ~90 | test_guide_gate4_diff.py (RealPobOverrideTests) |
| `tests/compare/test_ranking.py` | Best order, trade-offs after pure gains, the 3 % grouping | ~62 | test_guide_gate4_rank.py (62) + new |
| `tests/compare/test_why_lines.py` | Why-line wording, caps, curse and needs notes | ~110 | test_guide_gate4_why.py (fast part) |
| `tests/compare/test_why_lines_on_real_pob.py` | Why lines on real rows [pob, owner] | ~110 | test_guide_gate4_why.py (real part) |
| `tests/compare/test_untested_reasons.py` | Mageblood, granted skills, alternate weapon sets are listed, not tested | ~100 | test_guide_check_mageblood.py + parts of test_guide_check_pob.py |
| `tests/compare/test_availability.py` | League availability states, offline (uses the trimmed league fixture) | ~60 | test_guide_check.py |
| `tests/compare/test_rows_on_real_pob.py` | Real rows: support swaps, free sockets, locked, mastery [pob, owner] | ~190 | test_guide_check_pob.py (RealEkGuideCheckTests) |
| `tests/compare/test_comparison_contract.py` | Progress, chips, sorts, breakdown, time limit, memory budget [pob, owner] | ~290 | test_guide_check_pob.py (RealPobbContractTests) |
| `tests/compare/test_worb_cases.py` | The Worb cases [pob, owner] | ~110 | test_guide_check_pob.py (RealWorbTests) |
| `tests/compare/test_compound_changes_restore_player.py` | Compound changes and zero-row re-tests leave your build untouched [pob, owner] | ~190 | test_guide_check_pob.py (RealApplyPathTests, RealConditionalRetestTests) |
| `tests/compare/test_override_limits.py` | Cluster, timeless, two-handed and Awakened cases [pob, owner] | 175 | test_guide_checks.py |
| `tests/compare/test_known_regression_fr_pair.py` | The FR CoC v1 / v4 pair [pob, owner] | 65 | test_guide_check_fr.py |
| `tests/compare/test_full_link_and_broken_rules.py` | A full link never gets a 7th gem; an already-broken rule made worse [pob, owner] | ~190 | test_guide_gate2.py (two classes) |
| `tests/compare/test_vector_attribution.py` | Differences land under the right vector [pob] | ~100 | new (shape unsettled) |

### L4. `tests/intake/`, `league/`, `app/`, `web/`, `architecture/`

**17 files, about 2,124 lines.** By folder: `tests/intake/` 2, `tests/league/` 2, `tests/app/` 9, `tests/web/` 3, `tests/architecture/` 1.

| Path | Job | Lines | From |
|---|---|---:|---|
| `tests/intake/test_pobbin_import.py` | Link parsing, fetch limits, decoding (network stubbed) | 210 | test_pobbin.py |
| `tests/intake/test_library_confinement.py` | A build name cannot leave the Builds folder | ~60 | new |
| `tests/league/test_obtainability.py` | Gem variants, allow and deny lists | 95 | test_obtainability.py |
| `tests/league/test_league_client.py` | Cache age; offline gives nothing, not a crash | ~70 | new |
| `tests/app/test_api_security.py` | Host, Origin, token, headers, size cap | ~270 | test_server_security.py (262) |
| `tests/app/test_api_errors.py` | Stable, non-leaking error bodies for every error kind | ~330 | test_server_errors.py (340, minus apply parts) |
| `tests/app/test_job_store.py` | Start, progress, finish, evict, expire, one running job per kind | ~120 | new |
| `tests/app/test_settings.py` | Environment overrides, absolute paths, friendly failures | ~90 | new |
| `tests/app/test_static_files.py` | Allow-list, MIME types, no path escapes, token injected | ~80 | new |
| `tests/app/test_logging_redaction.py` | Secrets never reach the log | 104 | test_runlog.py |
| `tests/app/test_number_format.py` | Rounding rule, shared cases with the JS formatter | ~70 | test_display.py (41) + new |
| `tests/app/test_request_parsing.py` | Every malformed request is rejected with a clear message | ~110 | new |
| `tests/app/test_analysis_route.py` | Request defaults reach the session; a stuck job is given up [pob, owner] | ~170 | test_guide_gate2.py (RouteDefaultsTests, StuckJobTests) |
| `tests/web/test_ui_safety.py` | No HTML sinks, no inline script or style, every module parses | ~200 | test_gui_safety.py (216) |
| `tests/web/format.test.mjs` | The JS formatter against the shared cases (`node --test`) | ~45 | new |
| `tests/web/test_ui_modules.py` | Every `import` in web/js points at a file that exists | ~60 | new |
| `tests/architecture/test_file_sizes.py` | No file over its size limit | ~40 | new |

### M. `tools/` : scripts for developers, not part of the app

**7 files, about 834 lines.** By folder: `tools/` 7.

| Path | Job | Lines | From |
|---|---|---:|---|
| `tools/run_tests.py` | Runs the tests your change affects, in parallel, within a memory budget | ~230 | run_tests.py (373, split) |
| `tools/testmap.py` | Import graph and the rules that map a changed file to tests | ~190 | run_tests.py (split) |
| `tools/check.py` | The one command: format check, lint, types, import contracts, file sizes, fast tests | ~70 | new |
| `tools/check_file_sizes.py` | Fails when a file is over its limit; every exemption carries a reason | ~60 | new |
| `tools/pin_golden.py` | Regenerates tests/fixtures/golden.json (needs PoB and the owner's builds) | 154 | tests/pin_golden.py |
| `tools/record_snapshots.py` | Re-records the snapshot fixtures from real PoB runs | 58 | tests/record_guide_snapshots.py |
| `tools/perf_baseline.py` | Times one full analysis (not pass/fail) | 72 | tests/perf_baseline.py |

### N. `docs/`

**9 files, about 2,006 lines.** By folder: `docs/` 2, `docs/designs/` 3, `docs/history/` 4.

| Path | Job | Lines | From |
|---|---|---:|---|
| `docs/ARCHITECTURE.md` | One diagram, the layer table, the Lua endpoint table, the code words (the game words live in `mechanics/Glossary.md`) | ~260 | new |
| `docs/DECISIONS.md` | Why Python, why local, why PoB in-process, why mechanics notes, why frozen features live in a tag | ~220 | new |
| `docs/designs/target-design.md` | This document | (this file) | new |
| `docs/designs/codebase-strategy.md` | The owner's product decisions | 274 | unchanged |
| `docs/designs/design-audit-2026-10-26.md` | The design audit | 256 | unchanged |
| `docs/history/autobuilder-direction.md` | Early plan (history) | 478 | docs/designs/autobuilder-direction.md |
| `docs/history/learning-model.md` | Learning-model notes (history) | 219 | docs/designs/learning-model.md |
| `docs/history/030-learning-review.md` | Learning review (history) | 237 | docs/designs/030-learning-review.md |
| `docs/history/idea-to-build-research.md` | Research notes (history) | 62 | docs/designs/idea-to-build-research.md |

### O. `mechanics/` : the notes (data, renamed from `vault/`)

**227 files.** Listed by folder because the note names do not change; the full list is `git ls-files vault` today, plus
two notes created on 2026-10-27 that were still untracked when this was written (`Glossary.md`, `Exam.md`).
The step that renames the folder changes no note text, so the pinned note hashes in the golden baseline stay valid.

| Folder | Files | Notes |
|---|---:|---|
| `mechanics/Home.md`, `Dashboard.md`, `Glossary.md`, `Exam.md` | 4 | Entry pages (their wording changes in the docs step, "vault" becomes "mechanics"); the agreed vocabulary (the game words, including "scaling vector"); the learning exam. The last two are new and untracked today |
| `mechanics/.obsidian/` | 4 | Obsidian settings. `workspace.json` (window state) stops being tracked |
| `mechanics/Rules/` | 11 | Expert constraints PoB does not enforce (read by `mechanics/rules.py`) |
| `mechanics/Models/` | 5 | Mechanics PoB does not calculate (read by `mechanics/models.py`) |
| `mechanics/Scenarios/` | 2 | Fight assumptions: Mapping, Pinnacle Boss (read by `mechanics/scenarios.py`) |
| `mechanics/Gaps/` | 32 | Mod lines PoB cannot value, gem overrides (read by `mechanics/gaps.py`); the `.keep` file goes |
| `mechanics/Interactions/` | 164 | 163 interaction notes and `README.md`. No code reads them yet; `mechanics/interactions.py` arrives with the knowledge-base work |
| `mechanics/Inbox/` | 3 | Drafts to review; the `.keep` file goes |
| `mechanics/_templates/` | 2 | Note templates |

### Totals

| Folder | Files | About lines |
|---|---:|---:|
| Repository root | 7 | 371 |
| `src/autobuilder/` top level | 4 | 129 |
| `src/autobuilder/app/` (with `routes/`, `present/`) | 20 | 1,842 |
| `src/autobuilder/pob/` (Python) | 7 | 764 |
| `src/autobuilder/pob/lua/` (Lua, with `vendor/`) | 21 | 2,756 |
| `src/autobuilder/mechanics/` (code) | 6 | 287 |
| `src/autobuilder/analysis/` (with `checks/`) | 17 | 2,041 |
| `src/autobuilder/compare/` (with `diff/`) | 19 | 2,746 |
| `src/autobuilder/intake/` | 5 | 291 |
| `src/autobuilder/league/` | 3 | 181 |
| `web/` (HTML, CSS, JS, fonts) | 26 | 1,960 |
| `tests/` (code, helpers, fixtures) | 75 | 9,130 |
| `tools/` | 7 | 834 |
| `docs/` | 9 | 2,006 |
| `mechanics/` (the notes, renamed from `vault/`) | 227 | notes |
| **Total** | **453** | **25,338 + notes** |

Python package: 81 files, about 8,281 lines. Lua: 21 files, about 2,756 lines (516 of them copied from PoB). Browser: 26 files (5 are fonts), about 1,960 lines.

Today for comparison (tracked files outside `tasks/`, `docs/studio/`, `.claude/`): 340 files. `engine/` has 37 Python files
(6,201 lines) and 14 Lua files (3,079 lines); `gui/index.html` is 1 file (1,343 lines); `tests/` has 42 Python files
(8,529 lines) plus 5 fixtures and `golden.json`; 228 tracked files are notes. The target has more, smaller files: about 20 new
Python modules are real new code (settings, jobs, session, metrics ...), the rest is today's code in new places.

### What leaves the app (frozen), and where it goes

Plain words: three groups of features stop being part of the app. Nothing is deleted from history. Step 0 of the
migration creates the git tag `frozen/2026-10-27` on the last commit that still contains them; to bring a piece back you
read it from the tag (`git show frozen/2026-10-27:engine/optimize.py`) and port it, as the strategy page says, instead of merging.

| What leaves | Where it lives today | About lines | Goes to |
|---|---|---:|---|
| Build generator | branch `task-035-fireball-starter` (not on `main`) | 26,000 | stays on its branch, untouched |
| Audit suggestions: gem upgrades, support swaps, re-path, tree and mastery swaps, low-value branches, unobtainable-gem alerts | `audit.py` (`gem_levels`, `support_swaps`, `_swap_parts`, `repath`, `node_value`, `branches`, `suggest`, the steps in `run`), `tree_search.py` 187, `unobtainable.py` 237 | 560 | the tag |
| Apply-and-save | `optimize.py` 238, `guide_apply.py` 302, the preview/apply parts of `guide_routes.py`, `_apply*` in `server.py`; routes `POST /api/jobs/{id}/apply`, `/api/guide-preview`, `/api/guide-apply`; the XML-saving branch of `applyChangesJSON` | 600 | the tag |
| Command-line audit and optimize | `audit.py` lines 464-640, `optimize.py` `main` | 210 | the tag |
| 14 Lua endpoints and 5 change types only they use | `audit_tree.lua`: repathJSON, listBranchesJSON, listAllocatedNormalJSON, listAdditionsJSON, treeConnectedJSON, powerReportJSON, nodePathsJSON, masteryOptionsJSON, nodeStatsJSON; `audit_gems.lua`: listMainGemsJSON, listGemsJSON, auditGemLevelsJSON, auditGemReplaceJSON, auditSupportSwapsJSON; change types repath, mastery, gem, swap, replaceGem | 580 | the tag |
| UI parts | `gui/index.html`: suggestion rows, selection and conflict code, apply handler, action bar, the guide tick / preview / save bar, their CSS | 360 | the tag |
| Tests of the above | `test_apply.py` 215, `test_guide_apply.py` 351, `test_unobtainable.py` 401, and parts of `test_server_errors.py`, `test_server_security.py`, `test_guide_gate2.py` | 1,100 | the tag |

Stays because the comparison still uses it, even though it lives in a file that is otherwise frozen: `whyJSON`,
`gemStatDiffJSON`, `applyChangesJSON` (compound what-ifs, `save=false`) and `part_variants`. Callers were checked in the
code: `guide_check_why.py:44,59`, `guide_check_eval.py:82`, `audit.py` `dimensions`.

Also leaving the repository tree (not the machine):

| File | Why | Where it goes |
|---|---|---|
| `Start Orchestrator.bat`, `docs/agent-models.md` | AI-workflow files; decision 3 says they are not published | untracked and ignored, kept on the owner's PC |
| `requirements.txt` | replaced by `pyproject.toml` (one source of truth for dependencies) | deleted |
| `engine/HeadlessWrapper.upstream.lua` (75) | loaded by nothing; the origin is noted in `pob/lua/vendor/README.md` | deleted (in the tag) |
| `tests/evidence_checks.py` (186), `tests/spike_guide_compare.py` (138) | cite files in the ignored `tasks/` folder; the spike says it is "not a pass/fail test" | deleted (in the tag); the numbers they checked are pinned in `golden.json` |
| `tests/__init__.py`, `tests/golden.json` | no longer needed / moved to `tests/fixtures/` | deleted / moved |

### Slots reserved for later (no files are created now)

- Alternatives (other vectors that close a gap): `compare/alternatives.py` and `web/js/views/analyzer/alternatives.js`.
- Chat box on your Claude subscription (`claude -p`): an adapter package `autobuilder/assistant/` plus `app/routes/chat.py` and
  `web/js/views/chat/`. It reads `Finding` records, so it needs nothing the design above lacks.
- Prices from poe.ninja's documented economy data: `league/prices.py`.
- The learning log, the exam and the glossary: the notes `Exam.md` and `Glossary.md` already exist at the top of `mechanics/`;
  the code that reads them (`mechanics/glossary.py`, `mechanics/corrections.py`) comes with the knowledge-base work.
- Several targets at once: the request already takes a list of targets; the result view for a matrix comes later.

