---
type: gap
status: draft
source: "PoB 2.67.2 Data/ModCache.lua (nil or empty mod lists), Data/Uniques/*.lua, Data/ModFoulbornMap.lua, Modules/ModParser.lua:5325-5328, Data/Skills/other.lua:2756-2775; vault Interactions Curse application and effect, Curse limit, Item triggers, Power charges, Avatar of Fire, Chaos Inoculation, Crimson Dance (task 027 batch 3, evidence per pattern below)"
last_confirmed_patch: "3.29.x"
---

```gap
# Unique/Foulborn item lines PoB leaves unparsed (ModCache: nil mods, or an empty list with leftover text).
# They are not "wasted": PoB just has no number for them. Substrings are exact lines from Data/Uniques or Data/ModFoulbornMap.lua.
patterns:
  - match: "ignoring Curse Limit"
    why: "curse applied on block / when hit that ignores the curse limit (Sentari's Answer 3 lines, Ylfeban's Trickery current variant): PoB leaves the line unparsed (Data/ModCache.lua:14864-14879 nil), so the curse and its effect are not in any number and the curse limit is unaffected"
  - match: "Curse Enemies with Socketed Hex Curse Gem on Hit"
    why: "Mark of Submission: the line parses to an EMPTY mod list (Data/ModCache.lua:14876), so the socketed hex is applied on hit in the game but PoB values it only if the hex is set up in the skills tab"
  - match: "Lightning Bolt on Melee Hit with this Weapon"
    why: "Foulborn Mjolner: Trigger Level 20 Lightning Bolt on Melee Hit; PoB leaves the line unparsed (Data/ModCache.lua:22216 nil), so there is no trigger and no Lightning Bolt in PoB; the base Mjolner socket trigger it replaces is modelled"
  - match: "Socketed Lightning Spells have no Cost if Triggered"
    why: "Mjolner: the text is unparsed (Data/ModCache.lua:21742 nil) but PoB already makes the triggered spell free through the hidden support (Data/Skills/other.lua:2756-2775, no_cost at :2770, manaMultiplier -100 at :2773; Modules/CalcActiveSkill.lua:523-524), so removing the line shows no change and nothing is lost"
  - match: "chance to gain a Power Charge when you Cast a Curse Spell"
    why: "Anathema: power charge generation is not parsed (Data/ModCache.lua:5193, 6365 nil); PoB assumes max charges only when 'use power charges' is ticked, so the charge source itself has no value"
  - match: "Power Charge on Killing a Frozen Enemy"
    why: "Tulborn / Tulfall and the Foulborn ring mod: power charge on kill is not parsed (Data/ModCache.lua:7308, 10118, 16241 nil); PoB assumes max charges only when 'use power charges' is ticked, so the charge source has no value"
  - match: "Power Charge when you Hit a Frozen Enemy"
    why: "Replica Tulfall: power charge on hitting a frozen enemy is not parsed (Data/ModCache.lua:10120 nil); same as the kill version"
  - match: "Power Charge after Spending a total of 200 Mana"
    why: "Cane of Unravelling and the Foulborn Tulborn mod (same line as the Forbidden Power ascendancy node): not parsed (Data/ModCache.lua:16217 nil), so no charge is generated in PoB"
  - match: "Cover Enemies in Ash when they Hit you"
    why: "Xoph's Heart variant 1 (Pre 3.21.0, Data/Uniques/amulet.lua:1343) and Xoph's Blood (amulet.lua:1357): unparsed (Data/ModCache.lua:14803 nil); enemies covered in ash take 20% increased Fire Damage and move 20% slower, which PoB only counts through the config box 'Is the enemy covered in Ash?' (Modules/ConfigOptions.lua:2006-2007), never from this line; on Xoph's Blood the Avatar of Fire half parses (amulet.lua:1358). Current Xoph's Heart has 'Nearby Enemies are Covered in Ash' instead, which PoB parses (Modules/ModParser.lua:4337, ModCache.lua:18335), so it is not a gap there"
  - match: "Skeletons Cover Enemies in Ash on Hit"
    why: "Earendel's Embrace: minion line unparsed (Data/ModCache.lua:22000 nil); Covered in Ash is only counted through the config box (Modules/ConfigOptions.lua:2006-2007); the 'Summoned Skeletons have Avatar of Fire' half parses"
  - match: "Zombies Cover Enemies in Ash on Hit"
    why: "Replica Earendel's Embrace: minion line unparsed (Data/ModCache.lua:18874 nil); Covered in Ash is only counted through the config box (Modules/ConfigOptions.lua:2006-2007)"
  - match: "Cannot be used with Chaos Inoculation"
    why: "Midnight Bargain: restriction line unparsed (Data/ModCache.lua:14596-14597 nil); PoB does not stop you wearing it with Chaos Inoculation (the game does), and still values the Life reservation line"
  - match: "chance to Aggravate Bleeding"
    why: "Foulborn Rigwald's Quills (Data/ModFoulbornMap.lua:516, not in Data/Uniques) and any item with this mod: PoB parses it to an empty mod list with leftover text (Data/ModCache.lua:8081, 8696, 9220, 9620, 10074 are the (30-50)% rolls), so Aggravate has no value. PoB has no Aggravate mechanic: Modules/ModParser.lua:2327 (Crimson Dance line) only sets Condition:CannotAggravate, which nothing reads. The 'x3' is the enemy-moving bleed bonus (Modules/CalcSetup.lua:639). Whether an Aggravated bleed uses the moving rate is NOT VERIFIED (game rule, not PoB)"
  - match: "Your Mark Transfers to another Enemy"
    why: "Mercenary's Lot: unparsed (Data/ModCache.lua:23077 nil); the transfer to another enemy when the marked one dies has no value in PoB, the other lines of the item parse"
```

Each pattern relabels an item line with a matching text as 'can't measure' in the audit, but in practice almost none reach the patterns. Engine check: a line whose mod list is nil, or that PoB parsed with leftover text (`modLine.extra`), is flagged unsupported (PoB Classes/Item.lua:1325, 1344, 1352; engine/audit.lua:318) and goes to the 'unparsed' group (engine/audit.py:332-334) BEFORE the gap patterns are consulted, so patterns for such lines change nothing in the audit. Only P2 (Mark of Submission, empty list without leftover, ModCache.lua:14876) reaches them; as an uncrafted unique it lands in the 'uniquePackage' group with the pattern text as the reason (engine/audit.py:331, 336-338), NOT in 'cantMeasure' (:339-341, non-unique or crafted lines only). Audit match = case-insensitive substring on the item line (engine/audit.py:324). The guide check reads ALL patterns (engine/guide_interactions.py:93-107 and 124, casefold substring on item / flask / jewel mods). Loader: engine/vault.py:37-44. Verified headless? No: all evidence is Data/ModCache.lua, Data/Uniques and the engine source (read-only).

**Left out on purpose.**
- Foulborn Cospri's Malice '(80-120)% increased Elemental Damage with Attack Skills': PoB DOES parse this line (Data/ModCache.lua has '80%', '94%', '100%' increased Elemental Damage with Attack Skills as ElementalDamage INC with the Attack keyword flag, lines 11682, 11952, 4163), so it is not a gap. The Item triggers note's 'PoB counts 0 of it' (lines 30 and 36) looks wrong; it needs a headless parse of the exact item text before the note is corrected.
- 'Cover Enemies in Ash for 5 seconds when you Ignite them' (ring, Data/Uniques/ring.lua:986): parsed for the left ring slot (Modules/ModParser.lua:4335).
- Lines already covered by [[Mods PoB can't value]] ('Grants Level', 'Creates Consecrated Ground', flask lines) are not repeated.

**Cross-lane fix needed (not edited here).** The Item triggers note, lines 30 and 36 ('PoB counts 0'), and its cite Data/Skills/other.lua:2770 need a fix: 2770 is `no_cost`, `manaMultiplier` is at :2773.

**NOT VERIFIED.**
- No live parse of any line was run (everything is ModCache / Data reading).
- The source item of ModCache.lua:7308 (the 25% Power Charge on Killing a Frozen Enemy roll) was not found.
- Mark of Submission "PoB values the hex only if it is set up in the skills tab": no PoB source was read for this.

Linked from: [[Curse application and effect]], [[Curse limit]], [[Item triggers]], [[Power charges]], [[Avatar of Fire]], [[Chaos Inoculation]], [[Crimson Dance]]. PoB paths are relative to `%APPDATA%\Path of Building Community`.
