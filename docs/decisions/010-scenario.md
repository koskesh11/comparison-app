# 010 The scenario sets only the boss box

- Date: 2026-10-27 (grilling rounds 7, 13, 14)
- Decided by: owner
- Status: accepted
- Scope: the analyzer's scenario picker and config handling

## Context
Each PoB carries its author's config. The owner judges builds against a pinnacle boss fight. PoB's box "Is the enemy a
Boss?" offers No / Standard Boss / Guardian/Pinnacle Boss / Uber Pinnacle Boss, default Pinnacle
(Modules/ConfigOptions.lua:2086, PoB 2.67.2).

## Decision
- A scenario picker like PoB's: Standard Boss, Pinnacle Boss, Uber Pinnacle Boss, plus Mapping. Default: Pinnacle Boss.
- The scenario sets only "Is the enemy a Boss?", for both builds. Every other config box stays each build's own.
- Each build's other boxes are checked against the scenario, and settings that differ between the two builds are
  pointed out in the UI, sorted by how much they change the numbers. Settings that look wrong even when both builds
  agree are flagged too (example: Focused Channelling with no channelling time set).
- A scenario's own config values apply only when the build has a use for them (lesson from task 035: a channelling time
  was applied to a build with no channelling skill).

## Consequences
- The analyzer needs to know which config box a build can use; PoB shows a box only under conditions such as `ifMult`,
  `ifCond`, `ifSkill` in ConfigOptions.lua (example: "Channeling for # seconds", ConfigOptions.lua:1274).
