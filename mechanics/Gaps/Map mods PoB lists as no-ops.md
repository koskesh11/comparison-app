---
type: gap
status: draft
source: "task 027 batch 4e A2 (tasks/reports/027-evidence/partial/b4e/A2-map-modifiers.md); PoB 2.67.2 grep of Modules/ and Classes/, headless measurement on three seeds, 2026-10-26"
last_confirmed_patch: "3.29.x"
---

# Map mods PoB lists as no-ops (gap, prose only, no mod pattern)

What PoB cannot calculate for map modifiers (grep of Modules/ and Classes/, PoB 2.67.2, 2026-10-26). Thorns damage taken has its own note: [[Map thorns damage taken]]. Mod list and measured deltas: [[Map modifiers]].

- "Can this build run this mod": no code compares a mod with a build; the only outputs are the numbers measured per mod. Searching Modules/ and Classes/ for a map-mod check finds ConfigOptions.lua:70-130 (apply) and nothing else.
- Monster life / ES / kill time: Fecund, Unwavering, Buffered, Titan's (ModMap.lua:43-102) write enemy Life MORE and LifeGainAsEnergyShield, measured 0 output keys change on all three seeds (no time-to-kill number exists in PoB output).
- Monster speed and extra projectiles/chains: Fleet writes enemy Speed INC (ModMap.lua:146-153) but only enemySkillTime / EHPSurvivalTime move (EK, FR), TotalEHP is per hit and ignores monster attack rate; Chaining / Splitting / Twinned / pack-size and rarity mods are empty entries (ModMap.lua:370-403).
- Buffs expiring faster (of Transience, ModMap.lua:322-329), Blinding on hit (346-352), "players cannot inflict Exposure" (of Balance, 203-212): empty or comment-only apply; not selectable (not in Suffix list 424-441).
- Area of effect: of Impotence lowers AreaOfEffectRadius (measured on Worb and FR) but no number turns radius into hits on a pack, so the DPS stays unchanged.
- Monster speed-up conditions, Rare/Magic counts and ground effects (of Flames / Ice / Lightning ...): empty entries (ModMap.lua:380-403).
- Uber mod "cannot Recharge Energy Shield" (MapUberModNoRegen): PoB can flag NoEnergyShieldRecharge via item text (ModParser.lua:4786) but no map dropdown sets it.
- Medium / White tier: the tier selector exists (ConfigOptions.lua:842) but the headless probe could not move it (selIndex only); not measured.

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap has no mod pattern.
