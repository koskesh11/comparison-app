<!-- Reference part of ../target-design.md: Section 3. Dependency rules and automatic checks. -->

## 3. Dependency rules and automatic checks

Plain words: the folders are stacked in four rows. A folder may use any folder in a row below it, never one above it, and
folders side by side in a row do not use each other. This is what keeps "the part that knows PoB" separate from "the part
that knows your rules" and from "the part that talks to the internet". A tool, not a person, says no when it is broken.

```
 row 1   app        web server, jobs, settings, words for the browser    may use everything below
 row 2   compare    your build against a target build
 row 3   analysis   |   league   |   intake                              side by side: may not use each other
 row 4   pob        |   mechanics                                       side by side: may not use each other

 Rows only point downward. errors.py and progress.py are shared by all rows and import nothing from the project.
```

| Folder | May use | Must not use | Why |
|---|---|---|---|
| `errors.py`, `progress.py` | nothing from the project | every package | every package raises errors and reports progress; they must stay leaves |
| `mechanics` | `errors` | all other packages | the notes loader stays small enough for a non-programmer to read |
| `pob` | `errors` | `mechanics`, `analysis`, `compare`, `league`, `intake`, `app` | the bridge knows PoB and nothing about our rules |
| `analysis` | `pob`, `mechanics`, `errors`, `progress` | `league`, `intake`, `compare`, `app` | one build's numbers: no internet, no files except the build itself |
| `league` | `mechanics`, `errors` | `pob`, `analysis`, `compare`, `intake`, `app` | internet access for game data lives here only |
| `intake` | `errors` | all other packages | everything untrusted that brings a build in (links, codes, file names) lives here only |
| `compare` | `analysis`, `league`, `pob`, `mechanics`, `errors`, `progress` | `intake`, `app` | it receives files already imported; it does not fetch |
| `app` | everything | (nobody may import `app`) | HTTP and wiring are the outermost layer |

### The import-linter contract that enforces it

`pyproject.toml` (syntax checked against the
[layers](https://import-linter.readthedocs.io/en/stable/contract_types/layers/) and
[forbidden](https://import-linter.readthedocs.io/en/stable/contract_types/forbidden/) contract documentation):

```toml
[tool.importlinter]
root_package = "autobuilder"

[[tool.importlinter.contracts]]
name = "Rows: higher may use lower, never the reverse; siblings stay independent"
type = "layers"
layers = [
    "autobuilder.app",
    "autobuilder.compare",
    "autobuilder.analysis | autobuilder.league | autobuilder.intake",
    "autobuilder.pob | autobuilder.mechanics",
]
ignore_imports = [
    # The ratchet: every known violation of today's code is listed here with the step that removes it.
    # The list may only shrink. Example:
    # "autobuilder.analysis.checks.rules -> autobuilder.app.present.numbers",   # removed in step 17
]

[[tool.importlinter.contracts]]
name = "errors.py and progress.py import nothing else from the project"
type = "forbidden"
source_modules = ["autobuilder.errors", "autobuilder.progress"]
forbidden_modules = ["autobuilder.app", "autobuilder.compare", "autobuilder.analysis", "autobuilder.league",
                     "autobuilder.intake", "autobuilder.pob", "autobuilder.mechanics"]

[[tool.importlinter.contracts]]
name = "compare receives imported files; it never imports them itself"
type = "forbidden"
source_modules = ["autobuilder.compare"]
forbidden_modules = ["autobuilder.intake"]
```

What it catches: a domain module importing the server, `analysis` reaching for the internet through `league`, `pob`
learning about our rules, a shortcut import added in a hurry. It also catches indirect chains (`a` imports `b` imports
`app`), which a person reviewing a diff does not see.

### The other automatic checks

Plain words: one command, `python tools/check.py`, runs everything below in order and stops at the first red result.
The same command runs on every push in CI, minus the tests that need your PC. Today none of this exists (no formatter,
linter, type check or CI), and a few `# noqa` comments show a linter was once run by hand.

| Check | Tool and scope | What it catches | Runs |
|---|---|---|---|
| Formatting | `ruff format --check` on `src`, `tests`, `tools`; line length 120 | style drift, and the three lines where a continuation collapsed into a run of spaces (`guide_routes.py:150`, `pobbin.py:70`, `run_tests.py:295`) | editor, `tools/check.py`, CI |
| Lint | `ruff check`, rules E F W (errors), I (import order), B (bug patterns), UP, SIM, C90 (complexity at most 12), PL (at most 50 statements and 8 arguments per function), RUF, S (bandit-style security), T20 (`print`), TID (no relative imports, banned modules) | unused code, likely bugs, functions that outgrew 50 statements, `print` instead of logging, network modules imported outside `league`, `intake`, `app` | same |
| Types | `mypy`. Starts with errors ignored everywhere and switches strict flags on module by module: `pob`, `mechanics`, `errors`, `progress`, `analysis.metrics/findings/thresholds`, `app.settings/state/jobs/inputs`. Every file that gets typed joins the list; the list only grows | wrong keys, `None` not handled, wrong return types at the typed borders (PoB payloads, requests, records) | `tools/check.py`, CI |
| Imports | `lint-imports` with the contract above | layer violations, direct and indirect | same |
| File sizes | `tools/check_file_sizes.py`: Python source 400 lines, tests 500, own Lua 400, JS 250, CSS 250, `index.html` 80, tools 300. Vendor and data files are exempt, each with a written reason | files that grow back into 600-line modules (`audit.py` is 640 today) | same, and `tests/architecture/test_file_sizes.py` |
| Fast tests | `pytest -m "not pob and not owner and not slow"` | logic, parsing, security headers, job store, UI safety, no-PoB regressions | everywhere, including CI |
| PoB tests | `pytest -m pob`; skipped with a clear reason when PoB is not installed | state not restored, endpoint contract, write sandbox | your PC |
| Owner-build tests | `pytest -m owner`; skipped when the pinned builds are missing | golden numbers, real-build cases | your PC |
| UI | `node --check` on every module; `node --test tests/web` ([Node test runner](https://nodejs.org/api/test.html)) | syntax errors, Python/JS rounding drift | fast tests |
| Docs match code | `tests/pob/test_rpc_registry_matches_docs.py` | an endpoint present in Lua, Python or `ARCHITECTURE.md` but not in all three | fast tests |

Key settings, all in `pyproject.toml` (option names checked against the ruff, pytest and mypy documentation):

```toml
[tool.ruff]
line-length = 120
target-version = "py312"                  # lowest supported Python (assumption); the owner develops on 3.14

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP", "SIM", "C90", "PL", "RUF", "S", "T20", "TID"]
[tool.ruff.lint.mccabe]
max-complexity = 12
[tool.ruff.lint.pylint]
max-statements = 50
max-args = 8
[tool.ruff.lint.flake8-tidy-imports]
ban-relative-imports = "all"
[tool.ruff.lint.flake8-tidy-imports.banned-api]
"urllib.request".msg = "Network access belongs to league, intake and app only."
"http.client".msg = "Network access belongs to league, intake and app only."
[tool.ruff.lint.per-file-ignores]
"src/autobuilder/league/**" = ["TID251"]
"src/autobuilder/intake/**" = ["TID251"]
"src/autobuilder/app/**" = ["TID251"]
"tests/**" = ["S101", "PLR2004", "T20"]
"tools/**" = ["T20"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src", "."]                 # no more sys.path edits in test files
addopts = "--strict-markers --import-mode=importlib -ra"
markers = [
    "pob: boots Path of Building in-process (needs PoB installed)",
    "owner: reads the owner's own builds from the PoB Builds folder",
    "slow: takes minutes; runs only with AUTOBUILDER_SLOW=1",
]

[tool.mypy]
python_version = "3.12"
files = ["src/autobuilder"]
ignore_errors = true                      # the inverted ratchet, see mypy's "existing code" guide
warn_unused_ignores = true

[[tool.mypy.overrides]]                   # modules that are fully typed switch checking on
module = ["autobuilder.pob.*", "autobuilder.mechanics.*", "autobuilder.errors", "autobuilder.progress",
          "autobuilder.analysis.metrics", "autobuilder.analysis.findings", "autobuilder.analysis.thresholds",
          "autobuilder.app.settings", "autobuilder.app.state", "autobuilder.app.jobs", "autobuilder.app.inputs"]
ignore_errors = false
disallow_untyped_defs = true
disallow_incomplete_defs = true
disallow_any_generics = true
warn_return_any = true
```

One tool, ruff, does the work of black, isort and flake8; its formatter is documented as a
[drop-in replacement for Black](https://docs.astral.sh/ruff/formatter/), and the `I` rules sort imports.

Legacy files that break some of these rules today get a per-file ignore list, generated once with `ruff check --statistics`;
the list only shrinks as files are moved and cleaned, like the import-linter list. New files start clean.

How the markers work: `tests/conftest.py` skips a `pob` test when `Launch.lua` is not found in the PoB folder, skips an
`owner` test when a pinned build file is missing, and skips `slow` unless `AUTOBUILDER_SLOW=1` (the variable the tests
already use). A fresh checkout on a friend's PC therefore reports "skipped: needs Path of Building" instead of failing.
The marker is set by the test file or class that really boots PoB, not by the import graph (the runner guesses by
imports today, which marks tests "heavy" that only import `pobhost`).

The inverted ratchet is described in [mypy's guide for existing code](https://mypy.readthedocs.io/en/stable/existing_code.html).
Coverage target: 80 % of `src/autobuilder` on the full local run (PoB tests included); CI reports it without failing.

**The one command.** `python tools/check.py` runs, in this order: `ruff format --check`, `ruff check`, `mypy`,
`lint-imports`, `tools/check_file_sizes.py`, the fast tests, `node --test tests/web`. With `--full` it adds the PoB and
owner-build tests through the impact-based runner `tools/run_tests.py`. The optional `.github/workflows/ci.yml` runs
`check.py` on Windows with Python 3.12 and 3.14 on every push. It is the only thing a contributor has to remember.

