# Orchestrator — lessons
Process lessons only (game facts go to the vault). Format: date · task · trigger → rule → check · status.


- 2026-10-22 · 001 · 14 of 30 agent files had invalid YAML (": " in descriptions) and silently didn't load →
  After regenerating agents, verify they load (frontmatter parse) → check: tests/test_agents.py (task 009). · active
- 2026-10-22 · 013 · Said project skills would load next session; they loaded live → Verify before claiming,
  also for tooling behaviour → check: claim backed by a tool result in the same turn. · active
- 2026-10-22 · 013 · Usage limit hit mid-session with an agent running → Save state to the task file before
  starting expensive work when usage is low; prefer SendMessage resumes over new agents → check: task file
  has a resumable "Findings/Plan" section. · active
- 2026-10-23 · 003 · User: "why do we need to get this interaction right, when PoB already does it?" — I had
  ordered a label workaround for Greater Volley instead of asking PoB about the other skill part → Before any fix
  for a wrong number, first check whether PoB can give the right number with different inputs (skill part, config,
  enemy) → check: the fix names the PoB input that changes, or says why PoB can't. · active
- 2026-10-23 · 003 · pytest isn't installed; the gate agents had to find that out themselves → Gate prompts say
  `python -m unittest discover -s tests` (slow: AUTOBUILDER_SLOW=1) → check: the command is in the dispatch. · active
- 2026-10-23 · 003 · Both loop-2 gate agents stopped without writing reports (usage limit) → Log the dispatch before
  waiting; re-dispatch from the log → check: resume point names the report paths. · active
- 2026-10-23 · 004 · The task file was untracked in main when the worktree was made, so engineering created a forked
  copy in the worktree (merge needed a manual reconcile) → Commit the task file to main before `git worktree add`
  → check: `git status --short tasks/` is clean before dispatch. · active
- 2026-10-23 · 004 · A light-lane GATE 2 could carry small MEDIUMs; fixing M1-M3 + L1 before merge cost one short
  engineering loop and removed a regression (apply needed network) → Fix a MEDIUM before merge when the change
  itself introduced it. · active
- 2026-10-24 (010 resume): an interrupted agent run left uncommitted partial work and no report → at resume
  check the worktree (git status, diff --stat) and hand the partial work to the re-dispatched agent · active.
- 2026-10-25 (task 021, user correction): did not tell the user "/clear now" after GATE 1, the eng review or GATE 2,
  because background agents were running. Agents write their reports to files, so a resume point naming those files
  makes /clear safe. Lesson: after every gate or task, write the resume point and say "/clear now", even while agents run.
  Amended 2026-10-26 (task 035, 2nd occurrence): a /clear keeps a running lead alive but cancels its in-flight
  specialist calls ("interrupted"), and the lead then stops BLOCKED → leads now re-dispatch once on their own after a
  restart-interrupt (LEAD_NOTE in tools/make_agents.py) · promoted.
- 2026-10-26 (task 035/041, own gate failure): committed and pushed a make_agents.py rule without running its tests.
  The word "once" tripped test_agents' rule hygiene (TEMPORARY_RE), and main stayed red for about an hour → after
  any edit to make_agents.py, run `python tools/run_tests.py --files tests/test_agents.py` before committing · active.
- 2026-10-26 (task 041, own rework): a history rewrite with sed in Git Bash changed CRLF on every line of the
  rewritten file (42/42 lines instead of 2), caught before the push by `git diff --stat old new` → rewrite blob text
  with a byte-exact Python replace (stdin.buffer/stdout.buffer), and check that the diff stat shows only the intended
  lines before any force-push · active.
- 2026-10-26 (task 041, user correction): the Reddit draft came out in a generic, cheerful launch voice and hid
  what's broken. The user said "take my language and the way i talked throughout this project", "mention the things
  that dont work", "list them" → posts in his name use his voice, built from his messages and the task-card quotes,
  and list what doesn't work with PoB numbers (his "1000%" was really +91% DPS / +57% EHP) · promoted (make_agents.py).

- 2026-10-25 · 028 · 3rd unverified limit (wiki blocked, flask uptime, meta budget 'until P1' long expired) →
  promoted as an enforced check: rules carry source tags + task-based expiry, tests/test_agents.py fails on an
  expired rule; evidence before any 'limit/blocker' claim is a prompt rule for all agents. · promoted

## Promoted
Already in the agent prompts (tools/make_agents.py); kept for the record, not counted as active.

- 2026-10-22 · session · User: "much shorter, way too much text" → Reports in a few lines; details live in
  task files → check: final message fits on one screen. · promoted (memory feedback-short-answers)
- 2026-10-23 · 003 · GATE 4 loop 2 F1: my M5 decision covered false sources only, not "instead of" cancelling a real
  source → Split every gate-fix decision into one acceptance check per failure direction → check: the fix-loop log
  entry has a test line per direction. · promoted (interactions-lead prompt)
- 2026-10-24: a project fact ("wiki page fetches are blocked") was repeated to the user unverified; it was wrong (curl
  works, only WebFetch hits a bot check). Lesson: verify a stated project fact before repeating it as a limit. Fixed in
  tools/make_agents.py (wiki = most important mechanics source, user).
  RECURRED 2026-10-24 (task 021): this session ran on a main-thread prompt loaded before the fix and passed the stale
  line to data-sources-analyst; user caught it. Lesson: after editing agent prompts, the running session keeps the old
  one — re-check facts in prompts against .claude/agents/orchestrator.md, or tell the user to restart. Already promoted.
 · promoted (wiki rule in FACTS; evidence rule, task 028)
- 2026-10-24 (task 021 brainstorm, user correction): claimed "PoB assumes 100% flask uptime" without checking; PoB
  computes flask uptime (ItemsTab.lua:4830-4857, average/minimum from generated charges, tooltip only; kill/crit charges
  not included; calcs still treat an active flask as fully on). Lesson: before saying "PoB doesn't do X", grep PoB
  Modules/ and Classes/ for it (failure modes 4, 5). · promoted (evidence rule: cite file:line or say unverified, task 028)
- 2026-10-24 (user): agent cost = conversation resent per tool call, not start-up (cached). Leads give narrow briefs with
  the evidence in hand; specialists short-lived; SendMessage reuse only when prior context is needed · promoted (all
  leads + orchestrator). Measure in the 021 retro vs 010 gates.
- 2026-10-25 · 030 · User: "the app never learns". The goal said the sample builds are "learning material" and the
  direction doc says "a build coach that learns"; I read it as test data → split goals into capability claims with a
  done-when and check each against the code at every milestone merge → check: milestone report lists every claim
  with file:line or "missing" · promoted (orchestrator rule "Goals into capabilities" + failure mode 9).
- 2026-10-25 · 021 · Dispatch-approval rule relied on SendMessage, which leads do not have → before relying on a rule,
  check its mechanism exists in the agents' tool lists → check: test_prompts_only_name_tools_the_agent_has · promoted.
- 2026-10-25 · 021 · A lead wrote code itself to avoid the approval round trip → put PRE-APPROVED specialist briefs
  into the dispatch → check: dispatch text carries the briefs when the work is known · promoted ("Dispatch hygiene").
- 2026-10-25 · 021 · GATE 3 judged against the outdated card at the top (2 wrong findings) → rewrite the card when
  Done when changes; gate briefs quote the current Done when → check: brief contains the Done-when text · promoted.
- 2026-10-25 · 021 · Timed GATE 3 overlapped another agent's --all; speed work ran 147 min (user: unacceptable) →
  every dispatch has a time box; nothing CPU-heavy during a timed gate → check: time box in every brief · promoted.
- 2026-10-25 · 029 · Worktrees and logs landed on the user's Desktop → worktrees under pob-worktrees, writes only in
  allowed folders · promoted (task 029).
- 2026-10-26 · 027 · RECURRED (user correction): the 029 fix changed only where NEW worktrees go; wt-021, wt-021-m2 and
  wt-027 (created 10-24) stayed on the Desktop → moved with `git worktree move`; when a location rule changes, migrate
  the existing items too; `git worktree list` check at session start and before every report · promoted (task 027).
- 2026-10-26 · 027 (blind-test reveal) · my 02:2x summary said "EK hit chance" for a number measured on Cyclone (the
  attack that triggers EK) → the user rejected a correct finding; in summaries name the skill each number belongs to
  (trigger source vs triggered spell).
- 2026-10-26 · 035 · the 11:4x/11:5x log stamps were estimates, an hour ahead of the real clock (curator commit
  10:51) → take the time from `date +%H:%M` before writing a log entry.
- 2026-10-26 · 040 · Read can't rasterize PDFs here (no poppler) → check print layout with an Edge headless screenshot
  of the HTML framed at 794x1123 px per page; count pages via `/Type /Page` in the PDF.
