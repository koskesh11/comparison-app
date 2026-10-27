# Analyzer checklist

How a report of the analyzer is judged before the owner sees it: by Claude while building it and by the reviewer
(docs/decisions/017). Each item comes from a real miss in the first project. When a test checks an item, the item names
the test.

## Every reported number
- Comes from PoB output or a mechanics note, and says which (docs/decisions/013). No hand-made estimate.
- Names the skill it belongs to: a trigger source (Cyclone) and the spell it triggers (Ethereal Knives) are different
  numbers.
- Is shown the way PoB shows it when it comes from PoB; a number the app works out itself is rounded down where
  the game rounds down (docs/decisions/020).
- Shows trade-offs (DPS, EHP, mana margin, comfort), not a verdict.

## Failure modes
1. **"No change in PoB" is not "no value".** Requirements, uniques as packages, conditional mods, item variants and
   what PoB cannot measure all hide value. Before saying a source adds nothing, ask what PoB does not count here, per
   skill part, trigger breakpoint and ailment. A downside that changes nothing in this build "has no effect / costs
   nothing"; it is never "worth nothing".
2. **Evaluating too little.** All skills used together, all skill groups, minions. If PoB's FullDPS is 0 because no
   group is included in full DPS, measure the main skill's TotalDPS instead.
3. **Ignoring the build's setup.** Config gaps (a channelling time that is not set), boss-only skills, hand-set gem
   counts, the wrong or an unsaved file, settings not carried to derived builds. Before claiming a config box applies,
   quote that option's `ifMult` / `ifCond` / `ifSkill` from ConfigOptions.lua and check it against the build.
4. **Claims without verification.** Obtainability, gem levels, mechanics, mod wording against its effect. A chain of
   facts is verified only when every link has a source.
5. **Hand-rolling what PoB already does.** Before fixing a wrong number, check whether PoB gives the right one with
   other inputs (skill part, config, enemy). A verdict derived from a PoB list uses PoB's own rule for it (for example
   the curse limit from CalcPerform, not the length of a list).
6. **Blunt rules.** Flag only new problems; no lopsided trades; judge a deficit by how long it lasts.
7. **Results without reasons.** Every finding names the PoB modifier sources behind it, and every key number its
   source.
8. **Misread interactions.** A mod's real effect depends on the build: a "downside" can be the point of an item, a
   useless-looking node can carry a jewel-radius bonus, a gem can do nothing unless a config is set. For every "chance
   to X on hit / when hit" source: the hit rate from PoB's output (never the gem text), the effect's duration, the
   uptime per scenario, what the effect is worth when up, and whether PoB's box for it is ticked.
9. **Starting from zero.** Results, the owner's corrections and comparisons must feed the next run. Ask: does the app
   get better with use?
