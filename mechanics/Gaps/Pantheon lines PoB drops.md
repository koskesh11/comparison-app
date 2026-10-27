---
type: gap
status: draft
source: "PoB 2.67.2 Modules/PantheonTools.lua:6-19, Data/Pantheons.lua, Modules/ModParser.lua, Data/ModCache.lua (greps and live parse run 2026-10-26, task 027 batch 4e, A1)"
last_confirmed_patch: "3.29.x"
---

# Pantheon lines PoB drops or counts at 0 (gap, prose only, no mod pattern)

PantheonTools.lua:8-9 adds a soul line only when modLib.parseMod returns a mod list and no leftover text, so a line the parser cannot read completely vanishes silently. Of the 41 lines in Data/Pantheons.lua, 13 never change a PoB output (11 unparsed, 2 parsed with no output change). The in-game effect exists; PoB gives it no number. Proofs (grep on Modules/ModParser.lua and Data/ModCache.lua):

- Brine King base: "You cannot be Stunned if you've been Stunned or Blocked a Stunning Hit in the past 2 seconds" (Pantheons.lua:11): grep -n -i "cannot be stunned if" ModParser.lua gives only 3104, 4868, 4869, 4870 (helmet gems, not hit recently, crab barriers, influence items); live parse = leftover text.
- Abberath, Mephod: "Unaffected by Burning Ground" (Pantheons.lua:137): grep -n -i "unaffected by burning ground" ModParser.lua: no hit; ModCache.lua:22323 = {nil,"Unaffected by Burning Ground "}.
- Gruthkul, Erebix: "Enemies that have Hit you with an Attack Recently have 8% reduced Attack Speed" (Pantheons.lua:156): grep -n -i "reduced attack speed" in ModParser.lua and Calc*.lua: no match for this form; live parse = leftover.
- Lunaris, Glace: "Avoid Projectiles that have Chained" (Pantheons.lua:120): grep -n -i "avoid projectiles that have chained": no hit; ModCache.lua:14327 = {nil,"Avoid Projectiles that have Chained "}.
- Ralakesh: "Moving while Bleeding doesn't cause you to take extra Damage" (Pantheons.lua:226): grep -n -i "moving while bleeding": no hit; ModCache.lua:18302 = {nil,...}.
- Ralakesh, Drek: "Corrupted Blood cannot be inflicted on you if you have at least 5 Corrupted Blood Debuffs on you" (Pantheons.lua:232): grep -n -i "corrupted blood cannot": only ModParser.lua:2499 (the short form); ModCache.lua:14791 = {nil,...}.
- Shakari: "You cannot be Poisoned while there are at least 3 Poisons on you" (Pantheons.lua:188): grep -n -i "cannot be poisoned while": only ModParser.lua:4920 (while bleeding); live parse = leftover.
- Solaris: "20% chance to take 50% less Area Damage from Hits" (Pantheons.lua:71): grep -n -i "less area damage": no hit; live parse = Damage BASE 20 with leftover " to take 50% less   from Hits ", dropped by PantheonTools.lua:8.
- Solaris, Kitava: "Take no Extra Damage from Critical Strikes if you have taken a Critical Strike Recently" (Pantheons.lua:83): grep -n -i "no extra damage from critical": ModParser.lua:2522, 3106, 5903, 5904 (other conditions); live parse = leftover.
- Yugul: "You and your Minions prevent +50% of Reflected Damage" (Pantheons.lua:167) and "50% chance to Reflect Hexes" (Pantheons.lua:169): grep -n -i "reflect hexes" and "prevent .* of reflected": no hit; live parse = leftover (" to Reflect Hexes ", dropped).
- Parsed but no output change: Ryslatha "60% increased Life Recovery from Flasks used when on Low Life" (Pantheons.lua:264) parses as FlaskLifeRecovery INC 60 with Condition:LowLife; only CalcPerform.lua:1664 and ItemsTab.lua:4684 use it; 0 output keys changed in S0, A and B on Worb.
- Parsed but no output change: Solaris, Forest of Flames "50% chance to avoid Ailments from Critical Strikes" parses as AvoidAilments BASE 50 with Condition:CriticalStrike; 0 output keys changed in S0, A and B on all three seeds (reason read from the live parse only, not traced in CalcDefence: NOT VERIFIED).

Rule: when the generator compares god pairs by PoB TotalEHP, a pair whose value sits in these lines (Brine King stun lockout, Yugul reflect, Solaris area-damage line) shows an EHP delta of 0; report those lines as "check yourself" with the source line, never as a number (see [[Mods PoB can't value]]). Linked from: [[Pantheon and bandits]].

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap has no mod pattern.
