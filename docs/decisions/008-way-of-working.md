# 008 One Claude session works with the owner

- Date: 2026-10-27 (grilling rounds 26-29)
- Decided by: owner
- Status: accepted
- Scope: how work runs in this project

## Context
The first project ran an AI studio: an orchestrator, 30 roles in six departments, gates, a lessons store and rules
generated from one Python file. In task 102 it dispatched agents the owner did not know about. The owner: "This is a
fresh run ... I'm not keen in keeping any of it." His goal for the restructuring: good design, also for "rules and
decisions and how everything is located, and how things will be accessed."

## Decision
- One Claude session works directly with the owner. No departments, no orchestrator, no gates.
- No hidden agents: a new kind of agent needs the owner's yes once; every agent is named before it runs.
- One home per kind of rule, written once, enforced by a program where possible:

  | Kind | Home |
  |---|---|
  | Code rules | the checks (006) |
  | Why the code is built this way | docs/ARCHITECTURE.md (with the checks task) and this folder |
  | What the app does and the order of work | docs/ROADMAP.md |
  | How Claude works with the owner | CLAUDE.md (private) |
  | Safety: PoB install, the owner's builds, the backup | .claude/settings.json deny rules and the guard hook |
  | Game knowledge, glossary, exam | the mechanics notes (vault/, renamed mechanics/ later) |
  | Judging the analyzer's output | docs/analyzer-checklist.md (017) |
  | Task cards and logs | tasks/ (private) |
  | History of this run | docs/history/ (private) |
  | The first project | ..\archives\ (outside the repo) |

- No lessons store. A correction goes to the home of its kind; a tool problem gets fixed, not written down.
- Task cards: Start / Goal / Done when / Not / Mode, one resume point that is overwritten, a short log. Finished cards
  move to tasks/done/.
- Machine-wide tools: the ECC rules and agents stay installed; this project's checks and CLAUDE.md override them here.
  The sales, marketing and cowork plugins are off for this project (enabledPlugins in .claude/settings.json).
  Superpowers is off too: its skills are no longer linked here, and its session-start hook in the user-level settings
  skips this project (a project cannot switch off a user-level hook, so the owner had the skip added there, task 103).
  Of the personal skills, only grilling is used by default, others on request.

## Consequences
- The first project's studio, old plans and tasks are archived outside the repo, in `..\archives\` (the
  `pob-autobuilder` folder; its README lists the contents). Nothing from it carries over unless decided in this run,
  but it may hold something we need: look there before rebuilding an old piece from scratch.
