# Agent models and effort (task 001)

> Superseded 2026-10-23 by task 019 (token budget): current models and reasons are in the MODELS table of
> tools/make_agents.py and in tasks/019-token-reduction.md. The table below is the task 001 state.

Source of truth: the `MODELS` table in `tools/make_agents.py`; regenerate with `python tools/make_agents.py .`.
Code itself is always written by Codex (gpt-5.6-sol, medium) via `tools/codex_task.py`; the models below are the
Claude side (judgment, briefs, verification).

## Facts used (claude-api reference, cached 2026-10-06)
| Model | ID | $/MTok in / out | Effort levels | Context |
|---|---|---|---|---|
| Fable 5.1 | `claude-fable-5-1` | 10 / 50 | low–max | 1M |
| Opus 5.5 | `claude-opus-5-5` | 4 / 20 | low–max (API default medium) | 1M |
| Sonnet 5.5 | `claude-sonnet-5-5` | 2 / 10 | low–max (API default high) | 1M |
| Haiku 5.5 | `claude-haiku-5-5` | 0.10 / 0.50 (≤100K prompt) | low–max (API default medium) | 1M |

## Rule
- **Opus 5.5** where a wrong call is expensive: game interactions, gates, correctness, truth, PoB internals.
- **Sonnet 5.5** for skilled but checkable work: PoB code reading, specs, UI, test running, integration.
- **Haiku 5.5** for purely mechanical checks.
- Effort: **xhigh** for the two decision makers (orchestrator, interactions-lead), **high** for judgment and
  code verification, **medium** for checklist and routine work. Leads can raise effort per dispatch when a
  task is unusually hard.

## Table
| Agent | Model | Effort | Why |
|---|---|---|---|
| orchestrator | Opus 5.5 | xhigh | Runs the gates and owns the result (user decision). |
| interactions-lead | Opus 5.5 | xhigh | GATE 1 and 4; most past failures were misread interactions. |
| skill-gem-analyst | Opus 5.5 | high | Triggers, supports, breakpoints: subtle, expensive when wrong. |
| item-analyst | Opus 5.5 | high | Uniques as packages, Foulborn, Mageblood: failure modes 1 and 8. |
| tree-ascendancy-analyst | Opus 5.5 | high | Timeless/jewel radius and keystone conversion (Inner Conviction case). |
| mechanics-modeler | Opus 5.5 | high | Builds the math the app adds on top of PoB. |
| build-strategist | Opus 5.5 | medium | Expert-player judgment, called less often. |
| mechanics-researcher | Opus 5.5 | high | Interaction research is the user's top priority and feeds GATE 1; wrong claims cost rework. |
| pob-coverage-auditor | Sonnet 5.5 | high | Reads PoB code (ModParser/Calc*): code reading is Sonnet's strength. |
| vault-curator | Sonnet 5.5 | medium | Writes notes in a fixed format and validates them. |
| product-lead | Opus 5.5 | high | Spec quality drives every later step. |
| spec-writer | Sonnet 5.5 | high | Writes specs from the lead's decisions. |
| data-sources-analyst | Sonnet 5.5 | medium | poe.ninja/trade API plumbing, caching. |
| user-advocate | Sonnet 5.5 | medium | Checks results against known preferences. |
| uiux-lead | Sonnet 5.5 | high | UI decisions are visible and easy to correct. |
| ux-designer | Sonnet 5.5 | high | Layouts and wording. |
| frontend-dev | Sonnet 5.5 | medium | Briefs Codex and verifies one HTML file. |
| ui-qa | Sonnet 5.5 | medium | Rendering/contrast/value checks against the API. |
| engineering-lead | Opus 5.5 | high | Plans across Lua/Python/PoB internals. |
| pob-engine-dev | Opus 5.5 | high | PoB internals and state restore: easy to get subtly wrong. |
| optimizer-dev | Sonnet 5.5 | high | Search/scoring code, verified against golden numbers. |
| integration-dev | Sonnet 5.5 | medium | Server, caching, persistence. |
| review-lead | Opus 5.5 | high | GATE 2: blocks CRITICAL/HIGH findings. |
| correctness-reviewer | Opus 5.5 | high | Logic and PoB API misuse, unrestored state. |
| truth-reviewer | Opus 5.5 | high | Every number traceable: the user's core requirement. |
| security-reviewer | Sonnet 5.5 | high | Small localhost surface; well-known patterns. |
| qa-lead | Sonnet 5.5 | high | GATE 3 coordination; evidence-based, numbers decide. |
| player-sanity-tester | Opus 5.5 | medium | Reads suggestions as an expert player (failure modes 6-8). |
| regression-tester | Sonnet 5.5 | medium | Runs the golden tests and compares numbers. |
| api-tester | Haiku 5.5 | medium | Exercises fixed endpoints: mechanical. |

Totals: 15 Opus, 14 Sonnet, 1 Haiku. Fable 5.1 is not used (user decision 2026-10-22).

## Decisions (2026-10-22)
- No Fable 5.1 for any agent (user).
- mechanics-researcher on Opus 5.5 high instead of Sonnet (orchestrator, delegated by the user).

## Close calls (user may override)
- **pob-engine-dev on Sonnet**: Codex writes the code; Opus mainly for PoB-internals judgment in briefs.
- **user-advocate on Haiku**: mostly a checklist, but in task 003 it sent the spec draft back as "not ready"
  with fixes (product-lead report, 2026-10-21), which takes judgment.

Note: Claude Code reads `model` and `effort` from subagent frontmatter (Agent tool documentation: "Each agent
type's model, reasoning effort, and tools come from its definition (.claude/agents/*.md frontmatter)").
