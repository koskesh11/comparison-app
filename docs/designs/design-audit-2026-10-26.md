# Software design audit (2026-10-26)

Read-only audit of `main` at 4caf626 for the analyzer refocus (see `docs/decisions/`). Out of scope: `tasks/`, `docs/studio/`, `.claude/` and the frozen generator branches. References are `file:line` from the repo root; line counts come from the files (±1).

## Summary

The code inside most files is careful: short functions, named constants, PoB source citations, strong local security. What developers react to is the structure around the files:

- everything lives in one flat folder (`engine/`: 37 Python and 14 Lua files) with name prefixes instead of packages;
- one class, `Auditor`, is the de-facto API of every feature;
- the Python-Lua boundary is an unwritten, stateful protocol built from Lua source strings;
- the UI is one 1,343-line file holding two apps;
- tests and docs are organised by the project's history (tasks, gates, review IDs), not by what the code does.

File size is not the general problem. The largest Python file is `engine/audit.py` (641 lines); no Lua file is over 472 lines. The UI file is the exception.

## Size at a glance

| Area | Files | Lines | Largest |
|---|---|---|---|
| `engine/*.py` | 37 | ~6,200 | `audit.py` 641, `guide_check.py` 387, `guide_diff_items.py` 354 |
| of which `engine/guide_*.py` | 18 | ~2,960 | |
| `engine/*.lua`, own | 12 | ~2,490 | `audit.lua` 472, `audit_gems.lua` 343, `audit_tree.lua` 338 |
| `engine/*.lua`, copied from PoB | 2 | 591 | `_SimpleGraphic.def.lua` 516; `HeadlessWrapper.upstream.lua` (75) is loaded by nothing |
| `gui/index.html` | 1 | 1,343 | CSS 226, markup 23, JS ~1,076 |
| `tests/*.py` | 43 | ~8,950 | `test_guide_check_pob.py` 730, `test_guide_diff.py` 729 |
| `tools/run_tests.py` | 1 | 373 | |

## 1. Design problems, ranked

Ranked by how much each one hurts understanding and maintenance.

### 1. One flat folder, prefixes instead of packages

Evidence:
- `engine/` holds the HTTP layer (`server.py`, `guide_routes.py`, `api_errors.py`), the PoB bridge (`pobhost.py`, `engine_pool.py`, `pob_headless.lua`, `write_sandbox.lua`, `filesearch.lua`), the copied PoB files, the analysis (`audit.py`, `audit*.lua`, `costs.py`, `scoring.py`, `rules.py`, `models.py`, `tree_search.py`, `unobtainable.py`), the compare feature (18 `guide_*.py` and 4 `guide*.lua`, ~3,700 lines), knowledge loaders (`vault.py`, `obtainability.py`), a network client (`pobbin.py`) and two command-line tools (`audit.py:632`, `optimize.py:207`).
- `engine/` is not a package. Modules import each other by bare name (`import build_settings`, `from audit import ...`), so the app only runs from inside the folder (`Start Autobuilder.bat:3`, `README.md:35`).
- 35 of the 43 Python files in `tests/` edit `sys.path` before importing, in five spellings (`ENGINE_DIR`, `parents[1] / "engine"`, `PROJECT_ROOT / "engine"`, `TESTS_DIR.parent / "engine"`, or `tests/` itself), then mix `import guide_diff` with `from tests import golden_common`.
- Prefixes stand in for folders: `guide_check_avail`, `_eval`, `_log`, `_notes`, `_rank`, `_result`, `_retest`, `_why`; `guide_diff_common`, `_gems`, `_items`, `_tree`.
- No `pyproject.toml`, formatter, linter or CI config; `# noqa` comments (`audit.py:406,467`) show a linter was run by hand.

Why it hurts: the layers are invisible, IDEs and linters cannot resolve imports, and nothing stops any module from importing any other (problem 4).

Fix: packages that match the target layout (section 5), a `pyproject.toml`, start with `python -m <package>`, delete the `sys.path` edits.

### 2. The Python-Lua boundary is an unwritten, stateful protocol built from strings

Evidence:
- Each call is generated as Lua source: `engine.run(f"return {function}({_lua_str(json.dumps(request))})")`. The construction is repeated 7 times (`audit.py:124`, `:146`, `:189`; `guide_lua.py:22`; `optimize.py:195`; `guide_check_eval.py:82`, `:122`); raw snippets add more (`guide_check_eval.py:75,138`, `guide_check.py:328`).
- The escaper is private (`pobhost._lua_str`, `pobhost.py:191`) but imported by 4 engine modules and 6 test files. It escapes only `\` and `'`; it is correct only because `json.dumps` escapes control characters and non-ASCII by default.
- The Lua side is 36 global `*JSON` functions in 9 files (`evaluateJSON` is defined twice), glued by `dofile` chains (`audit.lua:468-472`, `guide.lua:12-13`) and global tables (`AuditCore`, `GuideCore`, `WriteSandbox`, `build`, `_G.__guide`).
- Four places decide which Lua is loaded: `pobhost.py:116`; `audit.py:87` (re-runs `audit.lua` for every Auditor); `guide_lua.py:14-16` (asks `type(snapshotJSON)` before every call); `guide_check_eval.py:118-119` (loads `guide_check_config.lua` on first use). `audit.lua` is in fact the loader of the guide helpers.
- `guide.lua:182-184` replaces the global `evaluateJSON` from `audit.lua:200` with a wrapper. Reading `audit.lua` gives the wrong picture of what `Auditor.evaluate` runs.
- The Lua state keeps session data between calls (`calcFunc` `audit.lua:5`, `savedConfig` `audit.lua:372`, `disabledGems` `audit.lua:418`), so order matters: load the build, run `audit.lua`, disable skills, set config, evaluate, restore. This order is written down nowhere.
- Payloads have no schema. The calculation context is described once, in a docstring (`rules.py:3-7`), and read as nested dicts everywhere.

Why it hurts: every number crosses this boundary, and it is the hardest part to read, change or test.

Fix, keeping PoB in-process:
- One `PobSession` class per Lua state: `load_build(path)`, `call(name, payload) -> dict`, and context managers `scenario(config)` and `left_out(skills)` that restore on exit.
- `call` uses the Lua C API instead of generating code: look the function up in one registry table (`rpc[name]`), push the JSON with `lua_pushlstring`, run `lua_pcall` with one argument. No escaping, no generated code, a clear error for unknown names.
- One Lua loader registers every endpoint in that table in a fixed order. No global overrides: the guide variant of `evaluate` becomes its own endpoint or an explicit option.
- Dataclasses (or TypedDicts) for what comes back: `CalcContext`, `SkillOutput`, `Snapshot`.
- A table in `docs/ARCHITECTURE.md`: endpoint, request, response, and the state it changes.

Later option, worth an ADR but not now: one OS process per PoB engine, talking JSON lines over a pipe. For: no process-wide `chdir` (problem 9), no Python write-guard hook, real parallel checks, a Lua crash cannot take the server down, memory is freed when a worker exits. Against: a few seconds of start-up per worker, one more moving part. With `PobSession` in place the swap stays inside one module.

### 3. `Auditor` is a god object and the de-facto session API

Evidence:
- `engine/audit.py` (641 lines) holds the `Auditor` class (lines 47-461) and a command-line printer (464-641).
- The constructor (`audit.py:50-83`) loads the build, hashes the file, re-runs `audit.lua`, leaves skills out, applies scenario config, loads rules and models, evaluates, and downloads league data (`audit.py:79` -> `Obtainability.load()` -> `obtainability.py:29-35`, which always asks pathofexile.com for the league name; no cache, no fallback). Without network no audit or guide check starts; the tests avoid this by patching (`tests/golden_common.py:146-158`).
- 101 `auditor.*` uses in 12 modules (`guide_check.py` 19, `guide_check_eval.py` 17, `guide_apply.py` 16, `optimize.py` 16, `unobtainable.py` 15, ...); `tree_search.py:47` keeps it as `self.a`.
- Callers change it from outside: `server.py:248-249` overwrite `suggestions` and `source_sha256`; `guide_check_eval.py:55-62` swaps `models` and adds a new attribute `named_models`, read back with `getattr(..., [])` (`guide_check_eval.py:68`).
- The compare feature uses an object called "Auditor" to mean "my build, calculated under a scenario".

Why it hurts: the analyzer's core concept (a calculated build under a scenario) is hidden inside the audit feature, every feature pays for the audit's set-up, and tests need heavy patching.

Fix:
- `BuildSession` (or `CalculatedBuild`): file and hash, scenario, left-out skills, rules and models, `evaluate(override)`, `main_out`, `dimensions`. No network.
- League data passed in, optional, with an "unknown" state when offline.
- The suggestion search (`gem_levels`, `support_swaps`, `repath`, `branches`, `TreeSearch`, `unobtainable`) moves to its own frozen module; the printer to the CLI module.

### 4. Dependencies point the wrong way; HTTP inside domain code; the server module is the app state

Evidence:
- `api_errors.py` (HTTP error mapping) imports `optimize` and `pobhost` (`api_errors.py:5-6`); `optimize` imports `audit`. Importing the error module loads the whole analysis stack.
- Domain modules raise HTTP-shaped errors: `pobbin.py:32-47` (`BadLink(InvalidRequest)`, `FetchFailed` with `status = 502`), `guide_check.py:27-29` (`GuideLoadError(ApiError)`, status 400), `guide_apply.py:37-68` (`InvalidRequest`).
- Two different `StaleAudit` classes: `api_errors.py:34` and `optimize.py:21`. `classify()` handles both (`api_errors.py:58-61`) and `guide_routes.py:220-224` converts one into the other.
- The server hands itself to the routes as the state object: `guide_routes.handle_post(sys.modules[__name__], ...)` (`server.py:162,195,272`). The routes reach into `state.Auditor`, `state.jobs`, `state.pool`, `state.engine_lock`, `state.resolve_build`, `state.BUILDS_DIR`, `state.DEFAULT_OUT_DIR`; tests fake this unwritten contract with `SimpleNamespace(...)` (`tests/test_server_errors.py:159`, `tests/test_guide_apply.py:316`, `tests/test_guide_gate2.py:216`).
- Mutable module globals hold the app: `API_TOKEN`, `pool`, `engine_lock`, `jobs`, `guide_capability` (`server.py:36-40`).
- Compare depends on audit for a constant: `guide_check_result.py:3` and `guide_check_rank.py:3` import `NO_WORSE_PCT`.

Why it hurts: no layer can be changed or tested alone, and the contract between server and routes is invisible.

Fix: domain packages define plain domain errors (`BadLink`, `StaleBuild`, `PobError`); only `app/errors.py` maps them to HTTP. An explicit `AppState` dataclass (engine pool, job store, paths, capability) passed to handlers. Shared constants in one metrics module.

### 5. The UI is one 1,343-line file holding two apps

See section 3. In short: 226 lines of CSS, ~1,076 lines of JS with about 90 top-level functions, two global state objects changed from 30+ places, two copies of the polling loop (one without error handling), domain rules in the view, and inline code that rules out a strict Content Security Policy.

### 6. Results are strings, and presentation lives inside the analysis

Evidence:
- Rule violations are strings `"[Rule name] message"` (`rules.py:121-122`), parsed back with `rule_name()` (`rules.py:139-141`) and by searching for `WORSE_MARK` (`rules.py:22`, `guide_check_result.py:45-51`).
- `guide_check_why.breakdown` diffs KPI sources by their display labels, e.g. "PoB Total EHP (enemy hits until death, all layers)" (`audit.py:411`, `guide_check_why.py:12-32`).
- A progress label is the API contract: the server tests `label != "Testing differences"` (`guide_routes.py:35`) and the UI repeats the text in `STAGES` and `TESTING` (`index.html:857-858`).
- `dims["weakens"]` ships preformatted text (`audit.py:218`); `rules.py`, `costs.py` and `scoring.py` import `display.fmt` to build messages.

Why it hurts: the analyzer's output (config checks, sustainability checks, gaps per vector) must be sorted, grouped, filtered and explained. Strings cannot be.

Fix: a `Finding` record (check id, subject, stat, actual, limit, gap, severity, sources) and a `Stage` enum for progress; text is made in one presentation layer.

### 7. Two metric models; thresholds and rounding duplicated across Python and JS

Evidence:
- Audit "dims": `dps`, `ehp`, `physMaxHit`, `manaFrom`, `manaTo`, `costs`, `models`, `loses`, `weakens`, `skills`, `parts` (`audit.py:204-223`). Guide "result": `base`/`after`/`delta` with `dpsPct`, `ehpPct`, `manaMargin`, `maxHit` (`guide_check_result.py:14-34`). The UI has a renderer for each (`dimChips`, `index.html:456-487`; `numbersCell`, `index.html:1082-1089`).
- The 0.1% cut-off appears 5 times: `NO_WORSE_PCT` (`audit.py:33`), `ZERO_LIMIT` (`guide_check_result.py:7`), `LOSS_LIMIT` (`guide_check_why.py:8`), a bare `0.1` (`guide_check_result.py:59`) and `ZERO_PCT` (`index.html:859`); `dimChips` uses 0.05 (`index.html:458`).
- Truncation exists twice and disagrees for negative numbers: `display.py:13` truncates toward zero, `index.html:283` uses `Math.floor`. A -0.05% change prints "0.0%" in the CLI and "-0.1%" in the GUI.

Why it hurts: the analyzer compares vectors of numbers. It needs one vector type, one set of thresholds and one rounding rule.

Fix: a `MetricVector` dataclass with `delta(other)`; thresholds in one module and sent to the UI with the report; the UI only formats, with one formatter family.

### 8. Tests and docs follow the project's history; tests are not portable; process files sit in the repo

Tests:
- Named after review gates: `test_guide_gate2.py`, `test_guide_gate4_diff.py`, `test_guide_gate4_rank.py`, `test_guide_gate4_why.py`; docstrings cite review IDs ("H1 ... H3 ... H4 ... M9", `test_guide_gate2.py:1-6`).
- Overlapping names: `test_guide_check.py`, `test_guide_checks.py`, `test_guide_check_pob.py`; `test_apply.py` next to `test_guide_apply.py`.
- Non-tests in `tests/`: `pin_golden.py`, `perf_baseline.py`, `record_guide_snapshots.py`, `spike_guide_compare.py` ("Not a pass/fail test", line 5), `evidence_checks.py`.
- Golden and many PoB tests read the owner's builds from Documents (`tests/golden_common.py:24,32-48`), so a friend's checkout fails or skips them (`README.md:69-70`).
- No unit/PoB split other than the runner's import-graph guess (`tools/run_tests.py:244`).

Docs:
- No architecture overview, module map or description of the Lua API.
- `README.md` describes the previous product (audit, guide check, generator "in progress") and starts the app from inside `engine/`.
- `docs/` is mostly planning history (`autobuilder-direction.md` "CEO Plan" with a "GSTACK REVIEW REPORT", `learning-model.md`, `030-learning-review.md`), plus AI-workflow material (`docs/agent-models.md`) and `Start Orchestrator.bat` at the root, against decision 3 in `codebase-strategy.md`.
- Code, tests and notes point at files that are not in the repo (`tasks/` is ignored): `tests/evidence_checks.py:3-4`, `tests/spike_guide_compare.py:5`, `vault/Interactions/README.md:12`, `vault/Scenarios/Pinnacle Boss.md:11`; `tools/run_tests.py:30,139` refer to ignored test and agent files.

Why it hurts: a visitor's first ten minutes are the README, the folder list and the test names. All three tell the story of the process, not of the program.

Fix: tests named by behaviour, mirroring the packages (`tests/pob/`, `tests/analysis/`, `tests/compare/`, `tests/app/`); scripts to `tools/`; a pytest marker or folder for "needs PoB" and for "needs the owner's builds"; a few reference builds as XML fixtures in the repo so golden tests run anywhere. README (what it does, how to run, layout), `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`; planning history to `docs/history/` or out of the repo.

### 9. Configuration and paths: scattered, fixed at import time, plus a process-wide chdir

Evidence:
- Path constants in 8 modules, most fixed at import: `pobhost.py:9-12`, `server.py:25-27`, `vault.py:9`, `build_settings.py:6`, `obtainability.py:14`, `optimize.py:14` (an alias of `pobhost.AUTOBUILDER_DIR`), `runlog.py:84`, `engine_pool.py:36`.
- "Documents/Path of Building/Builds" is hard-coded three times (`pobhost.py:12`, `server.py:25`, `tests/golden_common.py:24`); OneDrive breaks it (`README.md:28-29`). `tests/golden_common.py:25` re-derives the PoB folder and ignores the `POB_DIR` override that `pobhost.py:9` honours.
- `pobhost.py:9` reads `os.environ["APPDATA"]` at import time.
- `PobEngine.__init__` changes the working folder of the whole process (`os.chdir(pob_dir)`, `pobhost.py:98`). This is why an audit hook guards every Python write (`pobhost.py:18-81`) and why test helpers carry a "HAZARD" note (`tests/golden_common.py:5-6`).

Fix: one `config.py` with a frozen `Settings` dataclass, resolved once in `main()` (environment, then defaults; the Windows Known Folder API for Documents), passed down. Keep the guard; treat the `chdir` as the root cause (worker-process option in problem 2).

### 10. Error handling, logging and concurrency loose ends

- Two logging paths: the JSONL run log (`runlog.py`, logger `pob.run`, `propagate = False`) and five root-logger calls that only reach the console (`engine_pool.py:43`, `guide_check.py:74,191`, `guide_diff.py:161`, `guide_interactions.py:134`). The UI tells the user "Reference ID is in the log" (`guide_routes.py:202`).
- `assert` guards a production invariant (`guide_check.py:323`); `_canonical(result)` is called only for its side effect (`guide_check.py:384`).
- The job store never forgets: `jobs` (`server.py:39`) keeps every report until the server stops.
- `build_settings.py` rewrites a JSON file without a lock from several threads and fails on a corrupt file; `server.py:161` calls its private `_load_all()`.
- A pool of two PoB engines (`engine_pool.py:15`) is always used behind one global lock (`server.py:38,69,245`; `guide_routes.py:68,168,237,265`), so one engine is always idle. The intended model is not written down.
- Three lines where a line continuation collapsed into a long run of spaces: `guide_routes.py:150`, `pobbin.py:70`, `tools/run_tests.py:295`. A formatter would have caught them.

## 2. What is good and worth keeping as is

- **Local server security.** Host and Origin checks, a per-run token compared with `hmac.compare_digest`, anti-framing and no-store headers, a 64 KB body cap, builds confined to the PoB Builds folder (`server.py:28-31,53-57,108-125`), stable, non-leaking error bodies (`api_errors.classify`), log redaction (`runlog.py:16-33`). Covered by `tests/test_server_security.py` and `tests/test_server_errors.py`.
- **Write protection around PoB.** The Lua write sandbox (`write_sandbox.lua`) plus the Python write guard (`pobhost.py:18-81`), both documented and tested (`tests/test_write_sandbox.py`, `tests/test_pobhost_write_guard.py`).
- **The pobb.in importer** (`pobbin.py`): same-host redirects only, size and time limits, zlib-bomb guard, no DOCTYPE or ENTITY, atomic write, limits stated in the docstring.
- **"Every number is PoB's".** Lua returns PoB's own outputs and Python composes them. Comments and notes cite PoB source by file and line (`costs.py:29-50`, `audit.lua:44`, the vault notes). This is the project's best habit; keep it in every new module.
- **Knowledge as data.** Markdown notes with one YAML block, a `draft`/`verified` status and sources (`vault/Rules/Total skill cost must be sustainable.md`, `vault/Scenarios/Pinnacle Boss.md`), read by a 54-line loader (`vault.py`). Keep the format; only the loaders move.
- **Pure, unit-tested logic.** `guide_diff*.py` compares two snapshots without PoB and is tested with small builders (`tests/test_guide_diff.py:16-40`); `rules.py`, `costs.py`, `scoring.py`, `display.py` and `part_variants.py` are pure functions with tests. The recorded Lua outputs in `tests/fixtures/snapshots/` act as contract fixtures for the boundary.
- **The engine pool** lease/replace logic (`engine_pool.py`), with 329 lines of tests.
- **XSS-safe UI by construction.** Every element goes through `h()` with `textContent` (`index.html:268-279`), enforced by `tests/test_gui_safety.py` (no HTML sinks, `node --check`). Design tokens in `:root` (`index.html:11-30`), `:focus-visible`, `aria-live`, reduced-motion support.
- **Small units.** Apart from `audit.py` and the UI, files stay under 400 lines and functions are short.
- **The impact-based test runner** (`tools/run_tests.py`): picks tests from the import graph and runs PoB-heavy files within a memory budget. Keep it; it needs to learn package paths (section 6).

## 3. The UI: gui/index.html

### What is in the file

| Lines | Content |
|---|---|
| 1-9 | head; API token meta tag (filled in by `server.py:173`); Google Fonts |
| 10-237 | CSS, 226 lines: tokens 11-30, layout and sidebar 31-62, report 64-160, guide check 162-224 (`g*` classes), responsive 226-236 |
| 239-262 | markup, 23 lines: sidebar (search, scenario, leave-out, drafts, re-run, guide button, build list), `main`, action bar |
| 264-364 | shared core: `state`, `$`, `h()`, seven formatters, ES "unverified" notes, skill lines |
| 366-384 | `api()`: token header, JSON, errors carrying `status` and `kind` |
| 386-453 | sidebar and audit flow: load builds, pick, start, poll, progress, error |
| 455-849 | audit report: key-number tiles, suggestions with selection and conflict rules, findings, reservation panel, apply |
| 851-1335 | guide check: its own state `G`, constants, coercion helpers, its own formatters, input form, progress, ranked result, tick/preview/save bar |
| 1336-1340 | event wiring and start-up |

API calls: 8 call sites, 7 endpoints. `GET /api/builds` (388), `POST /api/audit` (432), `GET /api/jobs/{id}` (440 and 946: two pollers), `POST /api/jobs/{id}/apply` (834), `POST /api/guide-check` (936), `POST /api/guide-preview` (1235), `POST /api/guide-apply` (1296).

State: `state` (265; 6 fields, plus `defaultScenario` and `lastResult` added later, the latter holding a DOM node) and `G` (854-856; 23 fields, including DOM references `rowEls`, `boxes`, `groups`, `groupA`, `barEl`). About 45 direct field assignments on 31 lines, plus Set and Map changes. The two apps switch each other off by writing into the other's state (`startAudit` sets `G.active`, 424; `openGuide` clears `state.job`, 892).

### Problems specific to the file

- Two formatter families that differ only in the text for a missing value: `fmtNum`/`fmtBig`/`fmtPct`/`fmtMargin` (286-302) and `gPct`/`gBig`/`gMargin`/`gPlain` (871-874). The truncation rule disagrees with the Python one (problem 7).
- Two pollers. `poll()` (438-444) has no `catch`: one failed request leaves the progress screen up forever. `guidePoll()` (943-954) handles it.
- Domain rules in the view: which suggestions conflict is decided with the sentinel strings `"__tree__"` and `"__mastery__" + name` (512-521, 728, 734); the pobb.in pattern (860) repeats `pobbin.LINK_PATTERN`; error kinds (958) and stage names (857) repeat the server's.
- `renderReport()` is ~105 lines (647-752) and rebuilds the whole report on every checkbox click (529).
- Leftover code for an old report shape (`legacyMana`, 462).
- Inline CSS and JS: the server can only send `frame-ancestors` as its Content Security Policy (`server.py:31`); a strict `script-src 'self'` needs external files.

### Proposed split

Native ES modules served by the same server, no build step:

```
gui/
  index.html            shell only: sidebar, main, one module script tag for js/main.js
  css/tokens.css        the :root variables
  css/base.css          layout, sidebar, buttons, chips, rows, details
  css/report.css        key-number tiles, findings, reservation
  css/compare.css       comparison view (rename the g* classes)
  js/main.js            start-up and view switching: one place decides which view is active
  js/api.js             request(), pollJob() with errors and cancel, one function per endpoint
  js/store.js           a small state store per view; no DOM nodes in state
  js/lib/dom.js         $ and h()
  js/lib/format.js      one formatter family; same truncation rule as the Python side
  js/lib/safe.js        arr/obj/str/fin for untrusted data, used by every view
  js/views/sidebar.js
  js/views/report/      header.js, tiles.js, findings.js, reservation.js
  js/views/compare/     input.js, progress.js, result.js (rows, groups, sort and filter)
```

- The audit suggestions and both apply-and-save flows are frozen (`codebase-strategy.md`, round 2). Leaving `suggestionRow`, selection and conflicts, the apply handler and the tick/preview/save bar out removes roughly 300 lines of JS. The analyzer view (vectors side by side, differences as drill-down) gets its own `views/vectors/` folder when it is designed.
- Server: a static route for `/css/` and `/js/` with an allow-list and MIME types, the same security headers, and a policy of `default-src 'self'` plus the two font hosts. Self-hosting the two fonts drops the external hosts and the privacy note in `README.md:48-49`.
- `tests/test_gui_safety.py` slices `index.html` between two text markers (lines 12-13) and checks one inline script; it must scan every `gui/js/**/*.js` instead.
- Alternatives considered: a framework (Preact, Lit) or a bundler. Not now: a personal local tool, no build step today, and `h()` already gives safe composition. Revisit if the analyzer view grows many interactive widgets.

## 4. The three changes that would most improve how a developer friend sees the code

1. **Folders that show the layers, and docs that explain them.** Move `engine/` into packages (`app/`, `pob/`, `analysis/`, `compare/`, `knowledge/`), add `pyproject.toml`, pytest and a formatter and linter (ruff), remove the 35 `sys.path` edits, rename tests by behaviour, move scripts out of `tests/`, take frozen features off the import path, and write `README.md` and `docs/ARCHITECTURE.md` (one diagram, one table of Lua endpoints) for the new layout. Mostly `git mv`, with tests green after each area. It answers the first thing visitors criticised.
2. **A small, typed PoB bridge.** `PobSession.call(name, payload)` through the C API and one Lua registry table, a fixed load order, scenario and leave-out as context managers that restore state, dataclasses for the context and snapshot; split `Auditor` into a network-free `BuildSession` and the frozen suggestion search. The most fragile part becomes the most readable, and it is the base the scaling-vector analysis and the checks need.
3. **The UI as modules with one API client and one formatter, built together with the analyzer redesign.** It removes the file developers pointed at, fixes the silent poll failure and the rounding mismatch, moves domain rules back to the server and allows a strict CSP.

Suggested order: formatter and `pyproject.toml` first, as a separate formatting-only commit, so later diffs stay readable; then the package moves area by area. Changes 2 and 3 build on them.

## 5. Notes on the target layout in codebase-strategy.md

The proposed `app/ pob/ analysis/ compare/ knowledge/ web/ tests/ docs/` is right. Refinements:
- Put all Lua under `pob/lua/`: load order, globals and the write sandbox are runtime concerns. Feature subfolders (`pob/lua/analysis/`, `pob/lua/compare/`); the copied PoB files in `pob/lua/vendor/`. `HeadlessWrapper.upstream.lua` is loaded by nothing; keep it there as a reference with a note, or drop it.
- `app/` owns HTTP, one routes module per feature, the job store (with eviction), the HTTP error mapping and `config.py`. Domain packages never import from `app/`.
- `analysis/metrics.py` holds `MetricVector`, the thresholds and the DPS-stat choice; `analysis/checks/` holds rules, costs and scenario checks, returning `Finding` records.
- `knowledge/` holds the loaders (`vault.py`, `models.py`, rule parsing, obtainability overrides). The strategy page names the data folder both "mechanics" (round 1) and "knowledge" (target layout): pick one before the move. Renaming the data folder also moves the Obsidian vault and every path cited inside notes.
- Frozen code (`optimize.py`, `guide_apply.py`, `tree_search.py`, `unobtainable.py`, the suggestion steps of `Auditor.run`) goes to the frozen branch or a `legacy/` package the app never imports, which removes over 1,000 lines from the code a reader must understand. Check callers first: the compare "why" lines use `whyJSON` and `gemStatDiffJSON` (`guide_check_why.py:44,59`), which live in `audit_tree.lua` and `audit_gems.lua`; PoB's power report (`powerReportJSON`) may serve "marginal value per vector" later.

## 6. Things that will break when files move

- `tools/run_tests.py` maps tests to modules by file name in fixed folders (`CODE_DIRS`, lines 35 and 94-99) and calls a test "heavy" when it reaches `pobhost` (line 32).
- `tests/golden.json` pins hashes of engine files by bare file name (`engineFiles`, lines 9-60): re-pin after the move.
- `tests/test_gui_safety.py` slices `index.html` by text markers (lines 12-13).
- Lua paths are built as `ENGINE_DIR .. "/x.lua"` (`pob_headless.lua:6-8`, `audit.lua:468-472`, `guide.lua:12-13`, `guide_lua.py:16`, `guide_check_eval.py:119`).
- Vault notes cite code paths (`vault/Scenarios/Pinnacle Boss.md:11` names `engine/audit.py`).
- `Start Autobuilder.bat` and the README start the app from inside `engine/`.
