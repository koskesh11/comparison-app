# Architecture of src/

The analyzer's code lives in `src/autobuilder/`. The first app (`engine/`, `gui/`) is frozen reference; code comes over
only through the checks (decision 004). What carries over and why: the task 102 report (verdict per engine/ file).
Every rule below that a program can check is a check (decision 006); this page says where each one lives.

## Layers
Each folder may import only the folders below it (import-linter, `pyproject.toml`):

| Row | Folder | Does |
|---|---|---|
| 1 | `app/` | the local server: security checks, inputs, jobs, logging; `present/` holds every sentence and number format |
| 2 | `compare/` | two builds side by side: the chain table, skill-settings and config differences, the recalculate button |
| 3 | `analysis/`, `intake/` | one build calculated under a scenario, and its damage chain; where builds come from |
| 4 | `pob/` | the only code that talks to Path of Building |

`errors.py` and `progress.py` (when they exist) import nothing else of the app. Network code lives only in `intake/`,
`league/` and `app/`; the environment is read only in `app/settings.py`.

## How src/ calls PoB
One way only (task 102, cross-area section 3): Python loads PoB's own `lua51.dll` (LuaJIT 2.1) through ctypes in
`pob/lua_host.py`. At boot, fixed Lua files load in a fixed order (`pob/lua/loader.lua`). After that every request is
`call(name, payload)`: the name is looked up in one Lua table filled by `Rpc.register`, the JSON payload is pushed as
bytes, and the call runs under `lua_pcall`. Every reply is an `{ok, value, error}` envelope with inf, NaN and missing
values written out (S12). An endpoint that changes the build applies the change, recalculates, reads, and undoes the
change with another recalculation on every path, errors included (`pob/lua/analysis/scenario.lua`). `recalculate()` in
`pob/lua/build.lua` is PoB's own: it flags the build and runs one frame, whose build step wipes the cache, updates the
socket groups, rebuilds the output and refreshes the stat list and the config tab's calculator (PoB
Modules/Build.lua:1258-1273); an error PoB catches inside the frame becomes a Lua error. No Lua is ever built from
Python strings (check F6).

## Endpoints
Every Lua function src/ may call. A name is registered once in Lua (`Rpc.register`), listed in
`pob/endpoints.py` (`Endpoint`) and in this table; check F7 fails when the three disagree.

| name | does | changes the build? |
|---|---|---|
| `build.load` | opens a build from its XML text; returns its summary; a build PoB cannot open fails and leaves none open | replaces it |
| `build.summary` | name, class, level, main skill and 16 of PoB's output numbers | no |
| `build.state` | every number of both PoB calculations (the sidebar's and the Calcs tab's), the config inputs and placeholders, the Calcs tab's inputs, the fields of every skill group and gem (what M6 compares) | no |
| `analysis.summary` | the summary under a scenario: sets "Is the enemy a Boss?" (`boss`, one of PoB's values), recalculates in PoB's order, reads | temporary: put back and recalculated before it returns, also on error |
| `analysis.chain` | the damage chain under a scenario (`boss`): the rows of PoB's Calcs sections Skill Hit Damage, Attack/Cast Rate, Crits and Accuracy for the main skill, each cell with PoB's text, its raw numbers and its sources, and the hit per hand for an attack (decision 023) | temporary: the boss box and the Calcs tab pointed at the sidebar, put back and recalculated |

## Checks
`python tools/check.py` runs the fast checks (the commit hook runs them too); `--full` adds the merge checks, which
`tools/merge_to_main.py` runs in a clean export of the branch before it merges. One line per check, then one summary
line naming every failure. Code rules routed from the first project (S1-S13, T1-T2) are mapped in the task 102
layout and checks report.

| Id | Check | How |
|---|---|---|
| F1 | format | `ruff format --check` |
| F2 | lint (bugs, complexity, prints, blind except, magic numbers) | `ruff check` |
| F3 | layers; no use of engine/, no sys.path edits | import-linter, `tools/checks/no_engine.py` |
| F4 | no hand-written file over 400 lines | `tools/checks/sizes.py`, exemptions with a reason in `size_exemptions.toml` |
| F5 | network, environment, personal paths | `tools/checks/structure.py` |
| F6 | only `pob/lua_host.py` uses ctypes and the Lua C API | `tools/checks/lua_calls.py` |
| F7 | one endpoint table (Lua, enum, this page); no Lua globals; `dofile` only in loader.lua | `tools/checks/lua_rules.py` |
| F8 | our Lua compiles with PoB's lua51.dll (compile only) | `tools/checks/lua_syntax.py` |
| F9 | browser code parses; no inline script, style or handlers | `tools/checks/web.py`, `node --check` |
| F10 | every mechanics note parses (front matter, status, one block for Rules and Models) | `tools/checks/notes.py` |
| F11 | no unstaged deletions (an interrupted run) | `tools/checks/git_state.py` |
| F12 | text files stored with LF (`.gitattributes`) | `tools/checks/eol.py` |
| F13 | a test that patches a function counts its calls | `tools/checks/patch_counts.py` |
| F14 | child processes: listed module, no pipe, a timeout | `tools/checks/structure.py` |
| M1 | types, strict | `mypy` |
| M2 | all src/ tests, in parallel, with coverage of at least 80 % (M10) | `pytest -n auto --cov` |
| M3 | test tree: mirrored test files, the guard tests (M4-M7, M11), honest markers, one PoB per run | `tools/checks/testtree.py` |
| M4 | PoB edge cases and shared number formats | `tests/autobuilder/test_number_cases.py` |
| M5 | every report key is in the golden snapshot | `tests/autobuilder/test_golden_has_all_keys.py` |
| M6 | every endpoint leaves the build as it was | `tests/autobuilder/pob/test_every_endpoint_restores.py` |
| M7 | the in-memory button matches a saved change | `tests/autobuilder/compare/test_recalc_matches_apply.py` |
| M8 | the full checks pass in a clean export (no git-ignored file needed) | `tools/merge_to_main.py` |
| M9 | dead code and duplication | `vulture`, `pylint --enable=duplicate-code` |
| M11 | nothing written outside Builds\AutoBuilder | write-guard tests, required with `pob/lua_host.py`; listing in `pob_session` |
| M12 | the merge checklist | [ARCHITECTURE-CHECKLIST.md](ARCHITECTURE-CHECKLIST.md), answered in the merge commit |

## Tests
- `tests/autobuilder/` mirrors `src/autobuilder/`: `src/autobuilder/a/b.py` is tested in `tests/autobuilder/a/test_b.py`.
- Markers: `pob` (boots PoB), `owner` (reads the owner's builds), `slow`. A test that needs PoB uses the shared
  `pob_session` fixture (one PoB per run; every `pob` test runs on one xdist worker, `--dist loadgroup`); it skips
  cleanly when PoB is not installed. The PoB layer's own tests also use `bare_lua`, a Lua state on PoB's DLL without
  PoB, and Lua probe files in `tests/autobuilder/pob/lua/`.
- The reference builds (decision 014) are committed byte for byte in `tests/autobuilder/fixtures/builds/`.
- pytest runs without faulthandler: LuaJIT raises each Lua error as a Windows SEH exception, which faulthandler would
  print as fatal although LuaJIT catches it.
- No network outside `tests/autobuilder/intake/`, and none inside it either: the pobb.in code takes its opener as an
  argument, and the intake tests pass a fake that records each request. The PoB install and the owner's builds are listed before and after
  every PoB run; a change outside `Builds\AutoBuilder\` fails the run.
- `tests/checks/` tests the checks themselves: each plants a violation and expects the check to report it.
- The first app's tests stay in `tests/*.py` and run with `python tools/run_tests.py` (frozen, decision 004).

## Setup
```
python -m venv .venv
.venv\Scripts\python -m pip install --group dev
python tools/install_hooks.py
```
The dev tools are pinned in `pyproject.toml` (decision 021).
