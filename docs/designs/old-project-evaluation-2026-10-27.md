# What from the old project is worth reusing (evaluation for grilling round 28, 2026-10-27)

Owner (round 28): "my first and foremost biggest goal with this restructuring is to have good design. This also holds
true for rules and decisions and how everything is located. And how things will be accessed." Default (round 27 Q2):
nothing old carries over unless it is decided in this run. The code (engine/) is evaluated separately in task 102.

Verdicts: **reuse** (as is), **idea** (the idea comes back in a new form), **drop** (archived locally, not deleted).

## 1. The AI studio and its process

| Piece | Verdict | Why |
|---|---|---|
| Orchestrator + 30 roles in 6 departments (tools/make_agents.py, .claude/agents/, 31 files) | drop | Built for parallel feature work. It put a layer between you and the work that you could not see (task 102). Changing one rule means editing Python, regenerating 31 files and restarting. Round 26 Q1 already chose one session. |
| Gates 1-4, lanes, dispatch-request approvals, model/effort table | drop | Process standing in for checks that did not exist. Round 20: checks are programs; reviews only where you decided. |
| A fresh reviewer that did not write the code | idea | The one studio idea that works: it finds what the author misses. Already decided (round 21 area review, cold review). |
| Retro after every task; 7 lessons files, 56 active lessons (engineering 21, orchestrator 13, interactions 11, qa 4, review 4, features 3, uiux 0) | drop the ritual, triage once | Most lessons are about running the studio (dispatch, gates, worktrees, /clear habits). A few are durable facts: tool facts (ruff/mypy/pytest are not installed; the PoE wiki blocks WebFetch, curl works; sed in Git Bash rewrites the line endings of every line) and PoB facts (Focused Channelling counts 0 % without a channelling time). Game facts go to mechanics/ notes, tool facts to CLAUDE.md or a check. One pass, then archive. |
| Source tags on every rule "(user, date, task)" and the tag/expiry test (tests/test_agents.py) | idea | Knowing who decided a rule and when is good design. Dated decision records do that without a test that polices tags (section 3). |
| Task files tasks/NNN (front matter with departments/writes, statuses, the "go" queue) | idea, simplified | Your card (Start / Goal / Done when / Not / Mode) + a log + a resume point is worth keeping. Departments, writes, lanes are not. |
| Resume points before /clear | idea | Context resets stay a fact of working with Claude. |
| Worktrees in C:\Users\7800x3D\pob-worktrees, engine\cache junctions | drop | Existed so parallel agents did not collide. One branch per task in the main checkout is enough. |
| 343 linked skills (tools/link_skills.py: superpowers, ECC, skills CLI) | drop | Mostly other domains (healthcare, Kotlin, Laravel, ...). |
| tools/make_agents.py, tools/link_skills.py, tools/token_usage.py | drop | Exist only for the studio, the skill links and the studio's agent costs. |
| tools/run_tests.py | code side | Runs the frozen engine/ tests; src/ gets its own test command from the checks (task 102). |
| tools/hooks/guard_readonly.py + the deny rules in .claude/settings.json | reuse | Decided (round 26 Q3). Enforced on every tool call, not just written down. |
| docs/studio/ (studio-setup.html/pdf), docs/agent-models.md | drop | Describe the studio. |
| Old plans: docs/designs/autobuilder-direction.md, learning-model.md, 030-learning-review.md, idea-to-build-research.md | drop | Generator-era plans, replaced by decisions 1-4 and rounds 1-27. |
| This run's docs: codebase-strategy.md, design-audit-2026-10-26.md, target-design.md + target-design/ | reuse, restructured | Section 3. |
| Project memory: the 19-slide deck and its note; "rules live only in tools/make_agents.py" | drop | Owner, round 28: the deck is outdated, delete it entirely. "Short answers" stays. |
| 14 old task branches, frozen/* tags | code side | Kept until the history clean-up before any going public; the tags are the frozen generator's only record. |

## 2. Rules from the old prompts (content)

Each comes back only with your yes (round 27 Q2).
- **Worth re-confirming:** the evidence rule (no fact without file:line, a PoB number or a quoted source, otherwise
  "unverified"); failure modes 1-9 as a checklist for judging the analyzer's output (they are game-analysis lessons:
  "no change in PoB is not no value", config gaps, a mod's effect depends on the build); the PoB install and your builds
  are read-only and the app writes only to Builds\AutoBuilder\ (enforced by the hook); show trade-offs, not verdicts;
  every number traceable; PoE rounds down; the golden builds (Worb, CoC EK Assa) as reference fixtures; the PoE wiki is
  fetched with curl.
- **Old project only (gone):** departments, gates, dispatch, Codex, worktrees, token budgets, the Reddit voice rule,
  meetings with named agents, the generator goal, "files under 800 lines".
- **Already this run's decisions** (task 101 copied them from the strategy doc): milestone 1, the order after it, the
  code rules, the review method, build import, the knowledge rule, the backup is read-only.

## 3. Where rules and decisions live

**Does "rules live only in tools/make_agents.py" make sense? No.**
1. One 700-line Python file mixes four kinds of thing: product decisions, code rules, safety rules, agent prompts.
2. To read a rule you read a generator; to change one you edit Python, regenerate and restart.
3. Nothing in it is enforced. The "800 lines" text survived task 101 next to your 400-line rule.
4. It is private, so the code rules are invisible to anyone reading the repo, including the cold reviewer.

**Principle:** each kind of rule lives where it is used, is enforced by a program where it can be, is written once,
and current state is kept apart from history.

| Kind | Home | Read by, when | Published |
|---|---|---|---|
| Code rules (layers, imports, sizes, format, types) | pyproject.toml + tools/checks/ (programs) | run on every commit and merge | yes |
| Why the code is built this way | docs/ARCHITECTURE.md + docs/decisions/NNN-title.md (one dated record per decision: context, decision, consequences, status) | Claude when a task touches the design; any reader | yes |
| What the app does, milestone 1, the order after it | docs/ROADMAP.md, current state only | you; Claude at the start of a task | yes |
| How Claude works with you (short answers, evidence rule, no hidden agents, where things live) | CLAUDE.md, short (about 80 lines), pointing to the files above | loaded automatically every session | no (decision 3) |
| Safety (PoB install, your builds, the backup) | .claude/settings.json deny rules + the guard hook | enforced on every tool call | no |
| Game knowledge, glossary, exam | mechanics/ notes | the app and Claude | yes |
| Task cards and logs | tasks/ | you and Claude | no |
| History: grilling transcripts, old plans | docs/history/ (private) | rarely | no |

codebase-strategy.md today mixes three of these (the grilling transcript, the current decisions, resume points). Once
its current decisions are written into ROADMAP.md, decisions/ and CLAUDE.md, it becomes history.

## 4. Your machine-wide setup

| Piece | Value here | Verdict |
|---|---|---|
| ECC rules (~/.claude/rules/ecc, about 10 short files, loaded every session) | Generic and mostly sound (small functions, handle every error, no secrets). Conflicts: "files < 800" vs your 400; "80 % coverage" and "black + isort + ruff" are not decided here (ruff alone formats, sorts and lints). They say a project's own rules win. | Keep (global, business-os uses them). Here the checks are the authority; CLAUDE.md says so. |
| ~/.claude/AGENTS.md (ECC core) | Says "use the matching specialist agent for domain work", the opposite of round 26 Q1. Project rules override it. | Keep globally; CLAUDE.md states the override. |
| superpowers plugin | At every session start: "If you think there is even a 1% chance a skill might apply ... you MUST invoke the skill." A second process layer deciding how work runs, the same problem as the studio. Its skills (TDD, debugging, verification) are fine; the mandate is not. | Off for this project, if Claude Code allows that per project (unverified; checked before acting). |
| ECC agents (architect, code-reviewer, python-reviewer and dozens more) | Used only when chosen; round 26 Q2 means none starts without your yes. They carry generic checklists (80 % coverage). | Keep installed, unused by default. The project's reviewer is defined by the project. |
| sales, marketing, cowork plugins | About 60 skill descriptions in every session here, none about this project. | Off for this project, if possible (same check). |
| Your skills (~/.claude/skills) | grilling: how this run makes decisions. plan-ceo-review / plan-eng-review / gstack: the old orchestrator required them; "founder-mode scope expansion" does not fit. research, writing-for-agents: plausible later (sourced mechanics research; writing CLAUDE.md). caveman, prototype, web-prototype, setup-pre-commit (Husky, a JavaScript tool), migrate-to-shoehorn, scaffold-exercises: not for this project. | Keep installed for your other projects; here only grilling by default, others on request. |
