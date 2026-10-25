# Task 030 — CEO review: the app learns build creation

Working plan for /plan-ceo-review on tasks/030-learning-build-knowledge.md. Depth: strategy-only (direction task).

## Pre-review audit (2026-10-25)
- Branch main @ 149d6ae; no remote; no stash. Open: 021 M3 (unmerged, gates pending), 027 research (unmerged).
- Existing direction: docs/designs/autobuilder-direction.md:437-478 (task 020). R3 "guide check as evaluator /
  learning harness"; R7 poe.ninja tier-usage stats DEFERRED; sample builds = "learning material" (:447);
  016 learn-from-mistakes parked, "fits the grading harness later" (:471).
- Landscape: no ML passive-tree optimizer found; poe-optimizer = genetic search on PoB's engine; poe.ninja builds /
  profiles endpoints are internal, "not available for third-party use" (poe.ninja/docs/api) -> ladder node-usage
  statistics are not a usable signal without permission.

## 0A Premise challenge
- Real problem: every run decides from zero. The app can say "PoB says +X% here" but not "this notable is good for
  crit/CoC builds and dead weight for freeze builds, because ...". Without that, generate is slow (10 min/seed,
  tasks/reports/021-m3-session2.md:20), optimize gives deltas without reasons, and guide compare can't explain why a
  guide took a node.
- Premise 1 (user): learning is needed. Accepted.
- Premise 2 (challenged): "learning" does not have to mean machine learning. With 3 seeds, a trained model has no
  data; the evidence the app already produces (PoB deltas per choice) is exact but build-dependent.
- Premise 3 (challenged): a notable's value is not a number, it is a number *in a context* (mechanics the build
  uses, scenario mapping/boss, tier). Knowledge must be keyed by context, or it teaches wrong lessons (failure mode 8).
- Do-nothing cost: slow runs, no transferable reasons, same mistakes repeated, guide compare stays "diff + delta".

## 0B Existing leverage
| Sub-problem | Existing code / data |
|---|---|
| Measured value of a choice | gen_tree per-node reasons (9f56b0b), audit tree_search / gem / gear checks, PoB deltas |
| Context vocabulary (why) | 027 interaction DB: 51 notes, mechanics + providers + conditions (wt-027, unmerged) |
| Answer key | user sample builds + gen_grade.py (grade vs sample), guide check (010) diff-and-test |
| Expert rules / corrections | vault Rules/Models/Scenarios/Gaps, loaded by engine/vault.py:22-47 |
| Studio lessons | docs/studio/learnings (studio only, not the app) |

REALITY: premise-table pass unverified=0 (receipts above)
REALITY: already-done pass no learning store exists; nothing in engine reads vault/Interactions (grep, wt-027)
REALITY: surface-check n/a no CLI/route named in this direction plan
REALITY: binding-decisions finding R7 defers poe.ninja usage stats; any option using them reopens R7 docs/designs/autobuilder-direction.md:458
REALITY: numbers pass 10 min/seed [measured: tasks/reports/021-m3-session2.md:20]; 51 notes [measured: ls wt-027/vault/Interactions]
REALITY: deferred-asks pass no linked issue
REALITY: pr-count n/a direction doc only

## 0C Dream state
```
CURRENT                         THIS PLAN                          12-MONTH IDEAL
each run starts from zero  -->  every PoB evaluation is kept  -->  app explains any notable/gem/item choice
reasons per build only          with its context (mechanics,       in context ("good for CoC crit, useless
027 DB unused                   scenario, tier) + 027 tags;        for freeze"), generates faster from priors,
                                priors order candidates;           compares guides with reasons; PoB stays
                                PoB still verifies every pick      the final judge for every number
```

## Decision ledger
| ID and owner | Contract and evidence | Current | Proposed | Status | Exact approval and scope |
|---|---|---|---|---|---|
| D1 approach (user) | how the app learns; 0A-0C | C trained model | — | approved | user AskUserQuestion 2026-10-25: "Trained model"; data source open (poe.ninja builds API internal) |
| M mode (user) | 0E | SELECTIVE EXPANSION | — | approved | user 2026-10-25 "Selective" |
| Q1/Q2/premises/approach (user) | office-hours | self-play+experts; first win "Why this notable"; 5 premises; B trained surrogate | — | approved | user AskUserQuestion 2026-10-25 |
| DOC (user) | design approval | docs/designs/learning-model.md | — | approved | user "Approve" 2026-10-25 |
| E1 gems/items | 0G | in scope | — | approved | user "Add now" |
| E2 corrections (016) | 0G | in scope | — | approved | user "Add" |
| E3 learn button | 0G | in scope | — | approved | user "Add" |
| E4 community records | 0G | deferred | — | deferred | user "Defer" -> tasks/030 Deferred |
| D2 M1 order (user) | Codex outside voice | evidence first; model = M5 gated | — | approved | user "Evidence first" 2026-10-25 |
| P prep (user) | prerequisite offer | /office-hours run inline | — | approved | user 2026-10-25 "Run it" |

## currentDecision (D1)
Commitment comparison:
| Commitment | Source | Current | A | B | C |
|---|---|---|---|---|---|
| Keep every PoB evaluation with its context | 0A | no | yes | no | yes |
| Use 027 interactions as the "why" vocabulary | 027 | no | yes | yes | yes |
| Priors narrow/order tree candidates; PoB verifies | 0C | no | yes | yes (static) | yes |
| Learns more with every run / guide / correction | user | no | yes | no | yes |
| Needs a large build corpus | landscape | — | no | no | yes (poe.ninja not allowed) |

Question: D1 — How should the app learn?
A) Evidence log + context (recommended)
Store every PoB evaluation the app already does (tree picks, audit swaps, guide diffs, grade vs sample) with its context (027 mechanics, scenario, tier) and PoB's reason; aggregate into per-choice knowledge. Effort M, risk medium.
B) Interaction DB as filter only
Use 027 providers to pick tree candidates and explain them; nothing is learned from runs. Effort S, risk low.
C) Trained model on many builds
Statistical model over a large build corpus. Effort XL, risk high; no allowed data source today (poe.ninja builds API is internal).

## 0I Temporal interrogation (strategy-only)
- Hour 1: PoB delta semantics per choice type (design "Delta definition", E1). The engine is single-threaded Lua, one
  engine per process. [CC ~2 h spike]
- Hours 2-3: context feature extraction without 027 (fallback modDB features); record schema versioning.
- Hours 4-5: engine queue between server jobs and self-play (E3); model staleness vs PoB version.
- Hour 6+: held-out harness, counterfactual reason test, panel states. Human team ~6-8 weeks / CC ~4-6 days for M1-M4.

## Current scope (Section 1 preface)
Mode SELECTIVE EXPANSION (user). Approved: D1 trained model, approach B, premises 1-5, design doc, E1/E2/E3, plan
with milestone split (user "Approve, finish compact"). Deferred: E4. Pending: ML dependency (-> /plan-eng-review),
threshold values (set before the spike).

## Review sections (strategy-only, capability level)

### 1 Architecture
```
 gui/index.html --panel--> server.py --why route--> learn.explain() --+--> model file (read-only)
        |                      |                                     +--> PoB live delta (engine queue)
   learn button --start/stop--> self-play runner --engine queue--> PobEngine (one) --> evidence store
                                       trainer (offline/CLI) <-- evidence store ; trainer --> model file
 027 vault/Interactions --features--> learn.features <-- PoB modDB (fallback)
```
- New components: evidence store, self-play runner, feature extractor, trainer, explain API, engine queue.
- Coupling: the runner reuses the generator/audit engine path (one PobEngine). The engine queue becomes a single point
  of failure for all PoB work. Owner must prove the queue never starves an interactive request (test: self-play
  running and a panel request is served within one record's time).
- Scaling: records grow without bound. Owner must prove the store is append-only with compaction and a size cap.
- Rollback: the panel and the button sit behind a setting. Deleting the model file makes the panel show the PoB delta only.
- A1 WARNING: the engine queue is new shared state across server jobs; today each job owns its engine for the run.

### 2 Error & rescue map (capability level)
| Capability | What can go wrong | Rescue | User sees |
|---|---|---|---|
| self-play record | PoB calc error / Lua OOM | skip the record, log build+choice, restart the engine after N errors | progress shows skipped count |
| engine queue | interactive request during a record | pause runner at the record boundary | normal latency |
| trainer | too few records / one context | refuse to train, keep the old model | "not enough evidence" |
| model load | missing / corrupt / PoB version mismatch | PoB-only panel | "model from PoB x.y, retrain" |
| feature extract | 027 notes missing or invalid | modDB fallback features, flagged | label marked "basic features" |
| correction record | PoB disagrees with the user | keep, flag | "PoB disagrees: possible missing config" |
| store write | disk full / partial write | atomic batch append, drop partial batch | error message, runner stops |
No CRITICAL GAP at capability level; the owner names concrete exceptions in /plan-eng-review.

### 3 Security
- New local routes (why, learn start/stop/status): the server is already localhost-only. Validate build ids and choice
  ids (no paths from the client). Likelihood low, impact medium; mitigated by existing localhost and traversal guards.
- New ML dependency = supply-chain risk: pin exact versions (eng review).
- S1 WARNING: pickled model files can run code. Owner must prove a non-executable model format (JSON/text trees).
- Data: no PII; user samples stay local; E4 deferred.

### 4 Data flow & edge cases
`choice -> validate (allocatable? obtainable?) -> PoB delta -> record -> store -> trainer -> model -> panel`
- nil/empty: no allocatable alternative -> no record; empty store -> PoB-only panel.
- stale: PoB/league update -> records tagged, old model flagged stale.
- duplicate: same build+choice+context key -> dedupe, keep the latest PoB version.
- Interactions: start pressed twice -> idempotent; app closed mid-run -> runner stops at a record boundary, store
  consistent; panel opened while learning -> served first (queue priority).

### 5 Code quality
- Reuse gen_tree / audit swap code for deltas (don't re-implement PowerBuilder), vault.py loaders for 027, and
  guide_routes/pobbin for pobb.in parsing.
- Q1: learning gets its own modules (engine/learn_*.py), each under 800 lines.

### 6 Tests
| New thing | Test | no_claim |
|---|---|---|
| delta per choice type | unit on a fixture build: remove/add/swap equals a direct PoB calc | real-league prices |
| record schema + store | unit: append, dedupe, compaction, partial-write recovery | disk-full on a real FS |
| engine queue | integration: an interactive request preempts the runner (controlled pause points) | multi-process |
| trainer | unit: refuses below N records; fixed seed gives the same model | model quality |
| held-out check | harness: leave-one-build-out on 3 seeds; B vs A reported | generalization beyond seeds |
| counterfactual reason | integration: flipping the context changes the sign as claimed | causality in general |
| panel | GUI safety test + API: loading/empty/stale/error states | visual polish |
Hostile test: corrupt model file + stale PoB version + empty store at once -> PoB-only panel, no crash.

### 7 Performance
- Slowest paths: a self-play record (one PoB calc, ~0.1 s [estimated]) and the panel's live delta (one calc per choice
  shown; a 120-node tree = 120 calcs).
- P1 WARNING: the panel computes live deltas lazily (on expand) and caches them per build hash, or it is slower than
  today's audit.
- Memory: one engine (170-220 MB heap); store on disk; trainer runs only when idle.

### 8 Observability
- Runner log: records/min, skipped + reason, engine restarts. The "what it learned" summary doubles as the dashboard.
- Model card: training date, PoB version, record counts per context, held-out score (panel footer).

### 9 Deployment
- Local app, no migrations. Model file + schema version; a schema bump discards incompatible records with a notice.
- Feature flag: learning off by default until the M1 gate passes.

### 10 Long-term trajectory
- Reversibility 4/5 (delete store + model). Debt: a new ML dependency; the trainer needs upkeep per PoB patch.
- Platform: the evidence store is the base for candidate ranking (speed), guide-compare reasons, and E4 later.
- Cherry-pick retrospective: E1 enlarges M2 but uses the same pipeline; E3 forced the engine queue, which the
  generator also benefits from.

### 11 Design & UX (UI scope: panel + learn button)
| Feature | Loading | Empty | Error | Success | Partial |
|---|---|---|---|---|---|
| Why panel | "measuring in PoB" | "not enough evidence" | "PoB failed: reason" | label + evidence + PoB delta | label, reason not confirmed |
| Learn button | starting | "no builds to learn from" | stopped + reason | progress + summary | paused for your request |
```
 build view -> click node/gem/item -> panel (PoB delta now, learned label, evidence count, reason or "not confirmed")
 settings -> Learn overnight -> progress -> stop / finish -> "what it learned" list -> click -> panel
```
- Recommend /plan-design-review before the M1 GUI work.


## Outside voice (Codex CLI, read-only, completed)
12 findings (4 P0, 7 P1, 1 P2). P0-1 premise wording, P0-3 attribution, P1-5 exploration, P1-6 multi-target label,
P1-7/8 lineage counts and splits, P1-11 correction signals: applied (orchestrator, technical). P0-2/P0-4/P1-9/P1-10/
P2-12 (generalization, causality, gates, baselines, M1 size): resolved by user D2 (evidence first, model = M5 gated on
untouched archetypes with preregistered thresholds). Cross-model: Codex and the native spec reviewers agree on gate and
held-out weaknesses.

Approval readiness: PASS (D1, M, P, Q1/Q2/premises/approach, DOC, E1-E3, E4 deferred, D2: each with a user answer
reference above).

## NOT in scope
- E4 community-shared records (deferred, tasks/030 "Deferred").
- poe.ninja builds statistics (R7 deferred; no third-party API).
- Trained model before M5's gate.

## What already exists
gen_tree per-node reasons, audit swaps, guide check, gen_grade, vault loaders, 027 interaction DB (unmerged).

## Completion summary
| Item | Result |
|---|---|
| Mode | SELECTIVE EXPANSION |
| Step 0 | trained model chosen; office-hours design; 5 premises; E1-E3 accepted, E4 deferred |
| Sections 1-11 | A1 queue, S1 model format, P1 lazy panel deltas: warnings, owner = /plan-eng-review; 0 critical gaps |
| Error/rescue | 7 rows, 0 critical gaps |
| Scope proposals | 4 proposed, 3 accepted, 1 deferred |
| CEO plan | written (~/.gstack/projects/pob-autobuilder/ceo-plans/2026-10-25-learning-model.md) |
| Outside voice | Codex completed, 12 findings, all dispositioned |
| Reality rows | 7/7, 0 unverified |
| Unresolved | 0 (ML dependency and thresholds owned by /plan-eng-review) |

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 1 | CLEAR | 4 proposals, 3 accepted, 1 deferred |
| Outside Review | codex CLI (plan-review) | Independent 2nd opinion | 1 | completed | 12 findings; 12 resolved; 0 unresolved |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 0 | — | — |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | — | — |
| DX Review | `/plan-devex-review` | Developer experience gaps | 0 | — | — |

- **OUTSIDE COVERAGE:** codex, plan-review, completed, 12 findings (all resolved).
- **CROSS-MODEL:** native Claude spec reviewers and Codex both flagged gates and held-out weakness; resolved by D2.
- **VERDICT:** CEO CLEARED; eng review required (before M1).

NO UNRESOLVED DECISIONS
