---
type: gap
status: draft
source: "PoB 2.67.2 Data/ModCache.lua (lines quoted), Data/ModJewelAbyss.lua, headless ab_parse_lua.py over the 721 abyss jewel mods (task 027 batch 4d, item-analyst)"
last_confirmed_patch: "3.29.x"
---

# Abyss jewel lines: lines PoB drops or half-parses (gap, prose only, no mod pattern)

Of the 721 abyss jewel mods in Data/ModJewelAbyss.lua, a live parse at min and max roll leaves 3 partial and 3-7 unparsed per base (Hypnotic 225 full / 3 partial / 3 none, Murderous 285 / 3 / 5, Searching 188 / 3 / 3, Ghastly 134 / 3 / 7). The flat damage, life, ES, mana, resistance, CDR and recoup lines ARE counted, so an Eye jewel is never worth zero in PoB, only less than in game. Lines with the exact ModCache form:

- Hinder on Hit with Spells (Hypnotic, Ghastly minions): ModCache.lua:20 c["(2-3)% chance to Hinder Enemies on Hit with Spells"] = {nil, ...}; a rolled value such as "10% chance to Hinder Enemies on Hit with Spells" (ModCache.lua:3629) = {{}, " to Hinder Enemies  "}: the leftover makes PoB drop the line.
- Blind / Taunt on Hit with Attacks (Murderous, Searching): ModCache.lua:19 c["(2-3)% chance to Blind Enemies on Hit with Attacks"] = {nil, ...}, rolled form :3613 = {{}, " to Blind Enemies  with Attacks "}; the Taunt line has the same form (ModCache.lua:21).
- "(3-5)% chance to gain an additional Vaal Soul on Kill" (all bases): ModCache.lua:7938 "3% chance to ..." = {nil, "an additional Vaal Soul  "}.
- Partial: "Enemies Intimidated by you have (10-15)% increased duration of stuns against them" (the Intimidate condition parses, ModCache.lua:15308; the stun duration is a leftover), "+(250-300) to Evasion Rating if Hit an Enemy Recently", "(5-10)% chance to gain Onslaught when you use a Flask".
- Subsume the Source: "Socketed Rare Abyssal Jewels will be Consumed" ModCache.lua:21758 = {{}, nil}; the consumed mod is not carried over by PoB.

Rule: when the generator picks an Eye jewel, value it by the counted lines only and list the unparsed line as "check yourself" (see [[Mods PoB can't value]]); a chance to Hinder / Blind / Taunt on hit is valued with the [[Chance on hit uptime]] model, not by PoB. Linked from: [[Abyss jewels]].

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap has no mod pattern.
