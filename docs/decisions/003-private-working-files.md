# 003 Working files stay private

- Date: 2026-10-26 (commit 4caf626), homes revised in grilling rounds 28-29 (2026-10-27)
- Decided by: owner; the history location by Claude (round 29)
- Status: accepted
- Scope: tasks/, .claude/, CLAUDE.md, docs/history/, tools/hooks/

## Context
The first project's AI process files (task logs, agent prompts, lessons) buried the code for anyone reading the repo.

## Decision
These stay on the developer's machine and are git-ignored: the task cards (`tasks/`), Claude's settings, hook and
reviewer definition (`.claude/`, `tools/hooks/`), the working agreement (`CLAUDE.md`) and the history
(`docs/history/`: this run's grilling transcript and evaluations). The first project's material (its AI studio, old
plans, tasks 000-045) is not in the repo at all: it sits in `..\archives\`, next to the repo (owner, 2026-10-27).
Everything a reader
needs to understand the code is published: decisions (this folder), the roadmap, the checks, the analyzer checklist and
the mechanics notes.

## Consequences
- Published files never depend on a private one; a cold reviewer with a clean copy of the repo has all it needs (007).
- The git history still contains old workflow files; it is cleaned once, before any going public (005). Done
  2026-10-28, when the repo went public (025).
