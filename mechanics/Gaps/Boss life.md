---
type: gap
status: draft
source: "mechanics-researcher-boss-hp.md (fallback-life, boss-hp), task 027 evidence; PoB 2.67.2 CalcOffence.lua:5333-5343; PoB PR #4435; poewiki Sirus rev 1702453"
last_confirmed_patch: "3.29.x"
---

# Boss life (gap, prose only, no mod pattern)

PoB has no enemy life and no time-to-kill. Its only boss-sized number is the ailment threshold: 7.68 x mapLevelBossLifeMult x monsterLifeTable (CalcOffence.lua:5333-5343, from PoB PR #4435). That is a threshold, not life (poewiki Ailment rev 1673310), so there is no PoB fallback for boss HP. Level 84 example: 6,349,995 for the Pinnacle threshold against 70,494,097 real Sirus life (poedb).

- A boss without a vault HP row gives "fight length unknown" (gap), never a number derived from the 7.68 product.
- The poewiki gives only life multipliers (Sirus 2400%), not absolute life. The absolute factor comes from poedb (secondary source). Only Sirus has a row so far, see [[Fight length]].
- Venarius / Cortex multipliers are NOT VERIFIED (cargo candidates disagree: 6.66 / 8.1 vs 6.8 / 8.4).
- The Maven brain-phase count is not sourced (the Maven is several bars, at least 85 base units, about 3.5x Sirus).

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap has no mod pattern.
