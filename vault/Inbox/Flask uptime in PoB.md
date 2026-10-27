---
type: research
status: draft
pob_refs: [flask uptime]
source: "PoB 2.67.2 install, Classes/ItemsTab.lua:4830-4855 (read 2026-10-27, task 103); first-project lesson of 2026-10-24 (task 021, owner correction)"
last_confirmed_patch: 3.29.x
---

# Flask uptime in PoB (draft, for the owner to verify)

PoB does compute flask uptime, but only for the item tooltip: Classes/ItemsTab.lua:4830-4855 adds the line
"Flask uptime: X% average, Y% minimum" (or "Flask uptime: 100%") for utility flasks, and for life and mana flasks only
in some cases (line 4831 starts with `not item.base.flask.life and not item.base.flask.mana`). The first project's
lesson adds that the uptime counts generated charges only (charges on kill or on crit not included) and that the
calculation still treats an active flask as fully on; that part is unverified here.

Why it matters: Gaps/Mods PoB can't value.md says "PoB assumes 100% flask uptime" for flask duration mods. That holds
for the calculation, not for the tooltip. The sustainability checks (roadmap ranking item 3) need the uptime PoB already
computes instead of a hand-rolled one (analyzer checklist, failure mode 5).

Open: confirm which flasks get the line (ItemsTab.lua:4831-4840) and whether the calculation reads the uptime anywhere.
