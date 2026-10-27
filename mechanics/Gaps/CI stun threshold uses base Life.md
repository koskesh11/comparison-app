---
type: gap
status: draft
source: "poewiki Chaos Inoculation rev 1634768 (re-fetched 2026-10-26); PoB 2.67.2 Modules/CalcDefence.lua:2165-2167; vault Interactions Chaos Inoculation (task 027 batch 3)"
last_confirmed_patch: "3.29.x"
---

# CI stun threshold: PoB reads BASE Life, the wiki says increased Life counts (gap, prose only, no mod pattern)

**PoB.** `elseif modDB:Flag(nil, "ChaosInoculation") then stunThresholdBase = modDB:Sum("BASE", nil, "Life")`, source text "Life before Chaos Inoculation" (`CalcDefence.lua:2165-2167`). Only BASE Life (flat Life plus the class/Strength part) enters; increased and more Life are dropped. PoB has no ailment threshold for the player at all, only `StunThreshold`.

**Wiki (Chaos Inoculation rev 1634768).** "The chance and duration of both being stunned and receiving an elemental status ailments is based on your maximum life before CI takes effect. Maximum Life modifiers such as increased maximum Life, reduced maximum Life, etc. apply to the life before CI is applied." The page cites an early forum thread and its last version-history row is 3.14.1, so this may be outdated.

**Measured (Chaos Inoculation note, headless, CI node 11455 off/on).** EK stun threshold 1267 with CI against 1318 without (-3.9%); FR 1317 against 1594 (-17.4%). If the wiki is right, the real threshold equals the without-CI value, so PoB under-reports it by those percentages and "Life increased" nodes are not worthless on a CI build.

**Rule:** do not use PoB's CI stun threshold as a reason to buy or skip increased Life; the true value is between PoB's number and the without-CI number (unverified in the game). Ailment threshold and ailment duration on the player are not modelled either way.

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap is a formula difference, not a mod line.
