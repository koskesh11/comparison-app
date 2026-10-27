# 021 The checks and their tools

- Date: 2026-10-27 (task 104)
- Decided by: Claude (decision 006 leaves the tools to the checks task; the owner said "just do")
- Status: accepted
- Scope: src/, its tests, the notes format, the commit hook and the merge into main

## Context
Decision 006 makes every code rule a program; the list of checks came from the task 102 review (layout and checks
report, with the routed rules S1-S13 and T1-T2). On 2026-10-27 no linter, type checker or test runner was installed.

## Decision
- One command, `python tools/check.py`: fast checks F1-F14 before every commit (git hook `.githooks/pre-commit`,
  installed by `tools/install_hooks.py`); `--full` adds the merge checks. `tools/merge_to_main.py` merges a task branch
  only when the merge checklist is answered, the full checks pass in a clean export of the branch and the first
  app's tests pass. docs/ARCHITECTURE.md lists every check and its tool.
- Tools, pinned in `pyproject.toml` (newest release at least two weeks old): ruff (format and lint), import-linter
  (layers), mypy strict (types), pytest with xdist and coverage (tests, at least 80 % of src/), vulture and pylint's
  duplicate-code (dead code and copies). Custom checks are small scripts in `tools/checks/`, each tested by planting
  a violation.
- Line endings: text files are stored with LF (`.gitattributes`). The frozen first app and the notes keep their bytes,
  because the golden test pins them; the notes join the LF rule when src/ first reads them.
- The guard tests M4-M7 run over the milestone 1 registries (number cases, report keys, endpoints, change kinds)
  and fail as soon as an entry arrives without its test.
- Not now: the GitHub checks (before going public, decision 006); ESLint (`node --check` and the no-inline rule
  cover M1's web code).

## Consequences
- A rule found later is added as a check with its planted-violation test, not as prose.
- The first app's tests keep running with `python tools/run_tests.py`; the merge script runs them too.
