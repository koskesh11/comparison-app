# Code Review department — lessons
Process lessons only (game facts go to the vault). Format: date · task · trigger → rule → check · status.


- 2026-10-23 · 003 · Loop 1 found inf → null crash only in the GUI path → For every PoB rate/cap, check null
  handling in Python and GUI → check: grep `toFixed(` on PoB-derived fields. · active
