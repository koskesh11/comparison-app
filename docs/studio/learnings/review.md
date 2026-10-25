# Code Review department — lessons
Process lessons only (game facts go to the vault). Format: date · task · trigger → rule → check · status.

- 2026-10-23 · 003 · Loop 1 found inf → null crash only in the GUI path → For every PoB rate/cap, check null
  handling in Python and GUI → check: grep `toFixed(` on PoB-derived fields. · active
- 2026-10-23 · 004 · Old-vs-new flow equality proved little: the dropped state (_base_broken) was empty on both
  golden builds → When a refactor drops state run() used to set, check that state is non-trivial in the comparison
  or require a test that makes it non-trivial → check: the equality evidence names a case with non-empty state. · active
- 2026-10-23 · 004 · Review real diff size, not eol noise → `git diff --stat --ignore-space-at-eol main` at every gate.
  · active
- 2026-10-25 · 029 · Rule scan treats a numbered list or a marker-skipped list as one unit, so new untagged items
  pass → count tags per item, pin the marker count → check: feed the scan an untagged item appended to a tagged
  list · active (029 MEDIUMs parked). The 004 eol lesson recurred in 021/029 → promoted (engineering CODEX_NOTE).
