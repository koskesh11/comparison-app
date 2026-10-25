---
type: gap
status: draft
source: "poewiki Evasion rev 1611557; PoB 2.67.2 CalcDefence.lua; mechanics-researcher-receiving-defences.md (task 027 evidence)"
last_confirmed_patch: "3.29.x"
---

# PoB evasion is an average chance, the game uses an entropy counter (gap, prose only, no mod pattern)

The wiki describes evasion as a deterministic entropy counter (a hit counts as evade while entropy stays below 100; a crit is evaded on a separate roll that does not touch entropy). PoB uses the plain expected value 1 - 1.25 x accuracy / (accuracy + (evasion/5)^0.9), capped at 95 (CalcDefence.lua:57-63, 1094-1107; Data.lua:247); the word 'entropy' does not occur in CalcDefence.lua.

- The long-run hit rate is the same, so averages and EHP agree. Short-run streaks (a one-shot analysis of a few hits) do not.
- Rule: use PoB's evade chance for builds; do not claim a streak guarantee from it. EHPUnluckyWorstOf (ConfigOptions.lua:226) is PoB's own worst-case option.

Linked from: [[Receiving damage#Preventing the hit]], [[Defences#Evasion]].

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap has no mod pattern.
