# Target software design for PoB Autobuilder

Date: 2026-10-27. Status: proposal for the owner's review; no code has been changed. Baseline: `main` at 4caf626.
Inputs: `docs/designs/design-audit-2026-10-26.md` (the problems), `docs/designs/codebase-strategy.md` (the decisions), and
a read of the code: all Lua and the Python of `engine/` that matters here (the frozen modules and the diff modules were
skimmed), `gui/index.html`, `tools/run_tests.py`, and the structure and headers of `tests/`.

## How to read this document

Every section starts with plain words; the technical detail follows. Marks used throughout:

- **new**: does not exist today. **moved / split / renamed**: today's code, reorganised, logic unchanged.
- **(unsettled)**: a design point I could not settle from the code alone. They are collected in Appendix A.
- **[pob]**, **[owner]**, **[slow]**: test markers (section 3). `pob` boots Path of Building, `owner` reads your own
  builds from the PoB Builds folder, `slow` takes minutes.
- `~120` means an estimated line budget. A bare number is today's measured size of a file that moves unchanged.

What I need from you: answers to the eight questions in section 9, and a yes or no to the migration order in section 7.

What I did not do: I did not run the test suite. Which tests need PoB comes from reading the files and may be off by a
few. Line counts of today's files were measured; target line budgets are estimates.

## The design in eight lines

1. The app becomes one installable Python package, `autobuilder`, in `src/`. It starts with `python -m autobuilder`.
2. Inside, seven folders with one job each: `app` (web server, jobs, the words shown in the browser), `pob` (talks to
   Path of Building), `analysis` (what PoB says about one build), `compare` (your build against a target build),
   `mechanics` (reads your notes folder), `intake` (how a build gets in), `league` (league and gem data from the internet).
3. Arrows between the folders point downward only, and a tool checks it: `app` -> `compare` -> `analysis` -> `pob`.
4. Everything that crosses the Python/Lua border goes through one function, `PobSession.call(endpoint, data)`, and one
   table of 26 named Lua endpoints. No more Lua source text built by string pasting.
5. The `Auditor` god object becomes `BuildSession`: a build file calculated under a scenario. It never touches the internet.
6. Results become records (`MetricVector`, `Finding`), not strings. One place turns records into sentences.
7. The UI becomes about 20 small ES-module files. The new analyzer view (scaling vectors side by side) is a folder in it.
8. The frozen features (audit suggestions, apply-and-save, optimize CLI) leave `main`. They stay in the git tag
   `frozen/2026-10-27`; nothing is lost.

Two things are called "mechanics", as you decided: the folder `mechanics/` at the top (the notes, renamed from `vault/`)
and the package `src/autobuilder/mechanics/` (the code that reads them).

## 1. Principles

Ten widely used practices drive every choice below. Each has a plain-words line, the reason it matters here (with the
evidence from the audit), and a source. All links were checked with `curl -sI` on 2026-10-27 and answer 200.

### P1. A standard Python project layout: `src/` layout and `pyproject.toml`

- In plain words: the code lives in one named package under `src/`, and one file, `pyproject.toml`, says what the project
  is, what it needs and how its tools are set up. Any Python developer recognises it at once.
- Why here: `engine/` is a loose folder of scripts that import each other by bare name, so the app only runs from inside
  it, and 35 files in `tests/` edit the import path by hand (audit problem 1). There is no formatter, linter or tool config.
- Source: [Python Packaging User Guide, src layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/);
  [PEP 621, project metadata in pyproject.toml](https://peps.python.org/pep-0621/);
  [Writing your pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/).

### P2. Layered architecture and the dependency rule

- In plain words: code is stacked in layers. A layer may use the layers below it and never the ones above. The part that
  talks to the browser is on top; the part that talks to PoB is at the bottom.
- Why here: today the error module imports the optimizer, which imports the audit; domain code raises HTTP-shaped errors;
  the server module itself is handed around as "the app state" (audit problem 4). Nothing stops any module importing any other.
- Source: [Robert C. Martin, The Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html).

### P3. Ports and adapters (hexagonal architecture)

- In plain words: everything outside our own logic (PoB, the internet, the disk, the browser) is reached through a small
  piece of code, an adapter, behind a narrow interface, a port. The inside never knows what is on the other side.
- Why here: it lets tests use a fake PoB, makes "analysis never touches the network" a rule a tool can check, and keeps the
  later option (one OS process per PoB engine) inside one module. Python's `Protocol` is the port type.
- Source: [Alistair Cockburn, Hexagonal architecture](https://alistair.cockburn.us/hexagonal-architecture/);
  [PEP 544, Protocols](https://peps.python.org/pep-0544/).

### P4. Single responsibility

- In plain words: each module and class has one reason to change. If you must say "and" to describe it, split it.
- Why here: `Auditor` loads the build, applies the scenario, downloads league data, searches suggestions and prints a report;
  101 uses in 12 modules (audit problem 3). `gui/index.html` holds two apps in 1,343 lines (problem 5).
- Source: [Robert C. Martin, The Single Responsibility Principle](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html).

### P5. One source of truth

- In plain words: every fact (a threshold, the rounding rule, the list of Lua endpoints, an error kind) is written in
  exactly one place; everything else reads it. This is what the DRY rule really means: one piece of knowledge, one home.
- Why here: the 0.1 % cut-off exists five times (Python and JS), the two rounding rules disagree for negative numbers,
  and four places decide which Lua is loaded (audit problems 2 and 7).
- Source: [Don't repeat yourself](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself).

### P6. Data versus presentation

- In plain words: calculations produce facts (numbers, ids, records). A separate layer turns facts into sentences and
  rounded numbers for a screen. The calculation never writes English.
- Why here: rule failures are strings like `"[Rule name] message"` that get parsed back; a progress label is the API
  contract; the UI repeats Python's thresholds (audit problems 6 and 7). The analyzer must sort, group and filter
  findings, and the chat box later must explain them. Strings cannot be sorted or explained; records can.
- Source: [Martin Fowler, Presentation Domain Data Layering](https://martinfowler.com/bliki/PresentationDomainDataLayering.html).

### P7. Typed boundaries: parse, don't validate

- In plain words: where data enters (PoB's JSON, the browser's request, a notes file) it is checked once and turned into a
  typed record. Inside, code trusts the type. Records are frozen (immutable); "changing" one means making a new one.
- Why here: PoB payloads have no schema and are read as nested dicts everywhere; PoB drops keys and sends infinity as
  null. The calculation context is described once, in a docstring (`rules.py:3-7`).
- Source: [Alexis King, Parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/);
  [mypy documentation](https://mypy.readthedocs.io/en/stable/).

### P8. Explicit dependencies: one composition root, no module-level globals

- In plain words: settings and shared objects are created once at start-up, in one place, and handed to whoever needs
  them. Nothing reads the environment or keeps hidden global state on its own.
- Why here: folder paths are fixed at import time in 8 modules; the server keeps `API_TOKEN`, `pool`, `engine_lock`,
  `jobs` as module globals that tests have to patch (audit problems 4 and 9).
- Source: [The Twelve-Factor App, Config](https://12factor.net/config);
  [Mark Seemann, Composition Root](https://blog.ploeh.dk/2011/07/28/CompositionRoot/);
  [Martin Fowler, Dependency Injection](https://martinfowler.com/articles/injection.html).

### P9. Architecture rules are enforced by tools, not by memory

- In plain words: every rule we care about (layers, file size, formatting, which tests need what) is checked by one
  command. A rule that nobody checks gets broken within a month.
- Why here: the public feedback was about structure. Structure only stays if a machine says no when it is violated.
  A "ratchet" lets the legacy code pass today while the list of exceptions can only shrink.
- Source: [Thoughtworks, Fitness-function driven development](https://www.thoughtworks.com/en-us/insights/articles/fitness-function-driven-development);
  [import-linter](https://import-linter.readthedocs.io/en/stable/); [Ruff](https://docs.astral.sh/ruff/).

### P10. Tests mirror the code and are split by what they need

- In plain words: many fast tests for pure logic, few slow tests with real PoB. Tests sit in the same folders as the
  code, are named for the behaviour they protect, and carry a marker saying what they need.
- Why here: tests are named after review gates (`test_guide_gate4_why.py`), 35 files in `tests/` edit `sys.path`, and the golden
  tests silently need the owner's Documents folder, so a friend's checkout fails (audit problem 8).
- Source: [Martin Fowler, The Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html);
  [pytest, how to mark test functions](https://docs.pytest.org/en/stable/how-to/mark.html).

Further links used in later sections: [Architecture decision records](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions),
[ES modules (MDN)](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules),
[Content Security Policy (MDN)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP),
[Lua 5.1 manual](https://www.lua.org/manual/5.1/manual.html), [ctypes](https://docs.python.org/3/library/ctypes.html),
[import-linter layers](https://import-linter.readthedocs.io/en/stable/contract_types/layers/),
[import-linter forbidden](https://import-linter.readthedocs.io/en/stable/contract_types/forbidden/),
[ruff banned-api](https://docs.astral.sh/ruff/rules/banned-api/), [Node test runner](https://nodejs.org/api/test.html),
[SHGetKnownFolderPath](https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shgetknownfolderpath).

## Where the rest lives

This page is the short version. Section numbers in the text refer to these files:

| Section | File |
|---|---|
| 2. The complete target file tree | [target-design/file-tree.md](target-design/file-tree.md) |
| 3. Dependency rules and automatic checks | [target-design/checks.md](target-design/checks.md) |
| 4. Key interfaces | [target-design/interfaces.md](target-design/interfaces.md) |
| 6. The UI module tree | [target-design/ui.md](target-design/ui.md) |
| 7. Migration order | [target-design/migration.md](target-design/migration.md) |
| Appendix A. Unsettled technical points | [target-design/unsettled.md](target-design/unsettled.md) |

## 5. One worked flow: "compare my build with a target build"

Plain words: you pick your build, paste a target link, and press Analyze. The browser sends one request and then asks
every 0.6 seconds how it is going. A background thread loads both builds in two PoB engines, finds every difference,
tests each one on your build, ranks them, and runs the checks. The browser draws the result. File names below are the
target ones; "today" names the code the step grows out of.

**In the browser**

1. `web/js/views/start.js`: you choose your build in the sidebar (`views/sidebar.js` keeps the choice in `store.js`),
   paste a pobb.in link or a PoB code, and press Analyze. The form no longer checks the link pattern itself (today the
   page repeats `pobbin.LINK_PATTERN`); the server's answer is shown next to the field.
2. `start.js` calls `api.startAnalysis(request)` in `web/js/api.js`:
   `{own: {build: "3.29/Worb.xml"}, targets: [{link: "pobb.in/v8XfQn1yFnAs"}], scenario, leaveOut, includeDrafts}`.
   `api.js` is the only code that calls `fetch`; it adds the `X-Api-Token` header from the page's `<meta>` tag.
3. `main.js` switches to `views/progress.js` and calls `api.pollJob(jobId, {onProgress, signal})`, which asks
   `GET /api/jobs/{id}` every 600 ms, retries a failed request a few times and then shows "lost contact" (today
   `poll()` has no `catch`, so one failed request leaves the progress screen up forever).

**On the server (HTTP thread)**

4. `app/server.py` (`Handler.do_POST`) calls `app/security.py` (`guard`: Host, Origin, token compared in constant time),
   reads the body (64 KB cap), and finds the route in `app/routes/__init__.py`: `app/routes/analysis.py` (`start`).
5. `app/inputs.py` (`parse_analysis_request`) turns the JSON into a typed `AnalysisRequest(own, targets, setup)`. Your build
   name goes through `intake/library.py` (`resolve_build`, confined to the Builds folder); a link goes through
   `intake/pobbin.py` (`parse_link`, no network yet). A wrong type, an unknown scenario or too many targets raises
   `InvalidInput`, which becomes a 400 with a clear message. (Today: `_request_spec`, `_settings`, `_strict_bool` in
   `guide_routes.py` and `_start_audit` in `server.py`.)
6. `state.jobs.start(JobKind.ANALYSIS, label)` returns `(job, created)`; if a job already runs, its id comes back and the
   browser shows that one. `app/runner.py` starts a worker thread and the route answers `{jobId}` at once.

**On the worker thread (`app/runner.py`, `run_analysis`)**

7. `reporter = state.jobs.reporter(job.id)`; `reporter(Stage.FETCHING)`. For each link: `intake/pobbin.py` (`fetch`, same-host
   redirects only, size and time limits) -> `intake/code.py` (`decode`, zlib-bomb and DOCTYPE guards) -> `intake/store.py`
   (`save_import`, atomic write). A pasted code skips the fetch. (Today: `pobbin.import_link`.)
8. `reporter(Stage.LOADING)`; `with state.pool.lease() as own_pob, state.pool.lease() as target_pob:`. The pool has two
   engines and one job runs at a time, so two leases cannot deadlock. `notes = mechanics.load_notes(settings.mechanics_dir)`
   is read fresh, so a note you edited a minute ago counts.
9. `analysis/session.py` (`BuildSession.open`) loads your file, hashes it, applies the left-out skills, the scenario and the
   source-gated config in that fixed order and evaluates once (today `Auditor.__init__`). The target is opened the same
   way with `SessionSetup(scenario=None)`, which means "as its author saved it".
10. `reporter(Stage.MEASURING)`; `analysis/report.py` (`key_numbers(own)`) makes the tiles, reservations and DPS steps;
    `own.vector()` and `target.vector()` call `Endpoint.ANALYSIS_VECTORS` once per session and `analysis/vectors.py` turns the
    rows into two `MetricVector` objects.
11. `compare/service.py` (`compare(own, target, league, reporter)`):
    - `compare/target.py` loads the target into your engine as PoB's compare entry (needed for tree paths and PoB's own power
      rows) and takes `snapshot(own)` and `snapshot(target)`; it releases the target in a `finally`.
    - `compare/diff/__init__.py` (`diff`, pure) lists the gem, item, flask, jewel, tree and config differences as rows.
    - `reporter(Stage.TESTING, done, total)`; `compare/testing.py` (`test_rows`) tests the rows within the 90-second limit.
      `compare/evaluate.py` evaluates one change with `Endpoint.COMPARE_EVALUATE_CHANGE`, or for a compound change inside
      `with own.calc.discarding_changes():` with `COMPARE_APPLY_CHANGES`. `own.vector(ctx).delta(own.vector())` gives the
      row's `VectorDelta`; `compare/result.py` (`build_result`) wraps it.
    - `reporter(Stage.RANKING)`; `compare/ranking.py` (`rank`): a difference worth 3 % of DPS or more gets its own line,
      largest first; everything smaller is one group with its combined total. `compare/why.py` adds the modifier sources
      (`Endpoint.ANALYSIS_WHY`) and `compare/notes.py` the notes. `compare/vectors.py` (`attribute`) puts each row under the
      vector it moves most and returns the `Comparison`.
12. `reporter(Stage.CHECKING)`; `analysis/checks/__init__.py` (`run_checks`) returns the `Finding` list.
13. `app/present/report.py` (`to_wire`) builds the JSON: records become fields, missing and infinite numbers become `null`,
    sentences are written here. `state.jobs.finish(job.id, wire)`. Leaving the `with` returns both engines; a session that
    raised is closed and replaced, as today's pool does.
14. Any exception: `app/errors.py` (`classify`) maps a domain error to a status and a stable `kind`; anything unexpected
    becomes "The check failed. Reference ID is in the log", logged with the full traceback by `app/logging_setup.py`.

**Back in the browser**

15. `pollJob` sees `status: "done"`; `main.js` calls `views/analyzer/index.js` (`render(result)`).
16. `analyzer/header.js` and `tiles.js` draw the key numbers, `vectors.js` the vectors side by side (yours, target, gap),
    `drilldown.js` the differences under each vector, `checks.js` the findings, `reservation.js` the reservation panel.
    Everything is built with `h()` and `textContent`. Numbers go through `lib/format.js`, which uses the same truncation rule
    and the same test cases as `app/present/numbers.py`.

## 8. What does not change, and why

Plain words: most of what is good in the code stays exactly as it is, in a new place. The audit lists these strengths; the
design keeps each one and says where it lives.

| Stays | Why it stays | Where it lives after |
|---|---|---|
| The product decisions of `codebase-strategy.md`: analyzer first, generator frozen, AI-workflow files unpublished, restructure rather than rewrite | they are yours; this design only carries them out | unchanged |
| The calculation logic: snapshot diff, rules, costs, scoring, models, part variants, availability, ranking | it works and is tested; moving it is the point, rewriting it is not | `compare/`, `analysis/` |
| "Every number is PoB's": PoB runs in-process through its own `lua51.dll`, and Python only composes PoB's outputs | the project's best habit; also the reason for the golden tests | `pob/` |
| The local server's security: Host and Origin checks, a per-run token compared in constant time, anti-framing, no-store, 64 KB body cap, builds confined to the Builds folder, stable non-leaking error bodies, log redaction | strong already; covered by tests | `app/security.py`, `app/errors.py`, `intake/library.py`, `app/logging_setup.py` |
| Write protection: the Lua sandbox and the Python audit hook | documented and tested; the whole PoB-in-process idea depends on it | `pob/lua/sandbox.lua`, `pob/write_guard.py` |
| The pobb.in importer's limits: same-host redirects, size and time limits, zlib-bomb guard, no DOCTYPE or ENTITY, atomic write | careful input handling | `intake/` |
| Knowledge as data: Markdown notes with one YAML block, `draft` or `verified`, with sources; note text is not edited by the rename | your format and your 164 interaction notes | `mechanics/` |
| Pure, unit-tested logic and the recorded Lua outputs used as contract fixtures | cheap, fast, portable tests | `tests/fixtures/` |
| The engine pool's lease and replace logic and its 329 lines of tests | correct and tested; only its type changes (`PobSession`) | `pob/pool.py` |
| XSS-safe UI by construction (`h()` with `textContent`), the design tokens, focus and reduced-motion support | safe and already designed | `web/js/lib/dom.js`, `web/css/tokens.css` |
| The impact-based test runner | it selects tests from the import graph and caps PoB-heavy processes by memory; it only learns package paths | `tools/run_tests.py`, `tools/testmap.py` |
| Files on disk: `build_settings.json` content, the JSON-lines log format, the token file | your data and tools keep working; only the folder moves (`userdata/`) | `userdata/` |
| PoB itself: your installation, never bundled; one copied graphics stub with a licence note | its licence is its own | `pob/lua/vendor/` |
| The numbers | every step must keep the golden baseline identical | `tests/fixtures/golden.json` |

## 9. Open questions for the owner

Plain words: these are the only things the code cannot answer, because they are about what you want. Each has my
recommended answer, so a one-word reply is enough. The technical points I could not settle are in Appendix A, not here.

1. **Gear and flask "no effect" findings.** Today the audit lists mod lines that change nothing in PoB (wasted, only with
   a condition, over the cap ...). They are not suggestions, so they were not on your freeze list. Keep them as a check in
   the analyzer, collapsed and run on demand because they cost extra PoB time, or freeze them with the audit? Recommended:
   keep, on demand. If frozen, `analysis/checks/gear_mods.py`, `pob/lua/analysis/gear_mods.lua` and one endpoint leave the tree.
2. **Which builds may live in the repo as test fixtures?** For the golden and real-build tests to run on a friend's PC that
   has PoB, two or three build files must be in the repo. The repo is private but your friends can read it. May copies of
   EK and Worb be committed, or only public pobb.in builds like the one already there? Recommended: public builds only,
   plus yours only if you are comfortable with friends reading them.
3. **One target or several in the first version?** The request already takes a list of targets. The result for many targets
   (a matrix, "the best of each department") is a design of its own. Recommended: one target first.
4. **The scenario picker.** Round 7 says the fight is always a pinnacle boss, but the page still offers a scenario list
   (Mapping and Pinnacle Boss). Hide the picker and always use Pinnacle Boss (the Mapping note stays on disk), or keep it?
   Recommended: hide it.
5. **Draft notes.** Today the box "Include draft vault rules" is ticked by default, so unverified notes change the
   numbers. Round 11 says your words are taken as given but never as a 100 % rule. Should unverified (draft) notes change
   the numbers by default? Recommended: no; verified notes only, with a visible switch.
6. **The target's own settings.** Round 1 says each build keeps its own settings. Should the target be calculated exactly as
   its author saved it (recommended; that is how the Worb comparison went, and the author's channelling time counted), or
   should your Pinnacle Boss scenario be applied to it as well? (Your own build keeps getting the scenario, as today.)
7. **Where imported targets are saved.** Today a pasted link is saved in PoB's own Builds folder, under `AutoBuilder/imports`,
   so you can open it in PoB to check. Keep that, or save into the app's own folder (`userdata/imports`) so PoB's build list
   stays clean? Recommended: keep it, because you open them in PoB.
8. **How visible are the frozen features?** The git tag only, plus one sentence in the README, or also a short `docs/FROZEN.md`
   that lists what was frozen and why? Recommended: the tag and one README sentence.

