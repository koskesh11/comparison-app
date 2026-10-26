---
type: gap
status: draft
source: "poewiki Vaal Pact rev 1647702 (re-fetched 2026-10-26); PoB 2.67.2 Modules/CalcDefence.lua:1265-1277; vault Interactions Vaal Pact, Energy shield recovery keystones; headless FR (task 027 batch 3c)"
last_confirmed_patch: "3.29.x"
---

# Vaal Pact and Zealot's Oath: PoB loses the ES regeneration, the wiki says it still works (gap, prose only, no mod pattern)

**PoB.** The regeneration loop checks `modDB:Flag(nil, "No"..resource.."Regen") or modDB:Flag(nil, "CannotGain"..resource)` FIRST (`CalcDefence.lua:1265`); only in the `elseif resource == "Life" and modDB:Flag(nil, "ZealotsOath")` branch (`CalcDefence.lua:1267`) are Life regeneration BASE and percent copied onto Energy Shield. Vaal Pact's "Cannot Recover Life other than from Leech" parses to `NoLifeRegen` (Data/ModCache.lua:14558), so the Zealot's Oath branch is never reached and nothing is moved to ES.

**Wiki (Vaal Pact rev 1647702).** "The Cannot Recover Life other than from Leech modifier prevents life recovery from sources that aren't leech or Temporal Rift. This is checked when the player's life is modified; it does not remove life recovery stats from the character entirely. Accordingly, life recovery modifiers can still be used for other purposes through mechanics like Zealot's Oath, Pious Path, or Kaom's Spirit."

**Measured (headless FR CoC Occu Three Dragons v4, node 10808 added in memory, nothing saved).** ES regeneration 2250.6/s -> 115/s (-94.9%), EnergyShieldRegenPercent 13.1 -> 0.7 ([[Vaal Pact]], [[Energy shield recovery keystones]]). The 2250.6 includes the Consecrated Ground tick (5%); without it the Oath gives 1266.5/s.

**Consequence.** For any Zealot's Oath, Pious Path or Kaom's Spirit build, PoB shows Vaal Pact as costing almost all ES regeneration; by the wiki that cost is not real, so PoB under-rates the pair. Whether the game really keeps the regeneration is untested (the wiki states it, no in-game test). Until the user tests it, do not reject Vaal Pact on a Zealot's Oath build on PoB's regeneration loss alone, and label the figure "PoB reading".

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap sits in the check order of the regeneration code, not in a mod line.
