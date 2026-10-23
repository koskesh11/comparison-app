# Orchestrator — lessons
Process lessons only (game facts go to the vault). Format: date · task · trigger → rule → check · status.

- 2026-10-22 · session · User: "much shorter, way too much text" → Reports in a few lines; details live in
  task files → check: final message fits on one screen. · promoted (memory feedback-short-answers)
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
