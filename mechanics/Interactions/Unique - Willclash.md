---
type: interaction
status: draft
pob_refs: [usePowerCharges, overridePowerCharges, PowerChargesMax, SpellBlockChance, enemySkillTime]
source: "b5c-ia2.md, b5c-ia4.md; PoB 2.67.2 Data/Uniques/helmet.lua:1707-1715, Data/Bases/helmet.lua:804-812, Modules/ConfigOptions.lua:900-903 and 2318-2362, Modules/CalcPerform.lua:1044 and 1117, Modules/CalcDefence.lua:2963, Data/ModCache.lua lines per provider; poewiki Willclash rev 1539150; vault notes power-charges, block, chance-on-hit-uptime; b2c-item-analyst-leaguestart.md (task 027 batch 2c)"
last_confirmed_patch: "3.29.x"
---

Willclash is a Golden Mask that generates a Power Charge every second while none was lost recently, gives +5% spell block and (3-5)% increased Elemental Damage per Power Charge, and loses all Power Charges when you Block. It is built for characters that do not block (suppression, evasion, dodge) so the charge loop survives; on a block build it is nearly a dead helmet after the first block.
PoB only has the usePowerCharges tick (default off), which assumes max charges: charge gain, "recently lost" and "lose on block" are not modelled, so PoB over-credits Willclash with full block and damage whenever the tick is on. Two lines are unparsed (red).
Measured on Rue Worb.xml: Willclash is NOT in the active item set 9 (that set wears Eye of Malice); it sits in set 7 'Occultist Swap' (item 61). There Ralakesh's Impatience forces maximum Power Charges, so the usePowerCharges tick and overridePowerCharges change nothing; the build also has its own block sources (attack block 55, spell block 18 without Willclash), so in game the lose-all-charges line would fire and PoB cannot show it.
Uniques are packages: every line is valued, including the downside that is the point (lose all charges on block).

Pipeline: [[Defences#Block chance]] / [[Receiving damage#Block]] - spell block per charge; [[Damage calculation#Increased and reduced]] - elemental damage per charge

```interaction
id: unique-willclash
mechanic: "Unique package: free Power Charges (up to 3) that scale spell block and elemental damage - until you block, which removes them all"
family: charge
pipeline_step: ["Defences#Block chance", "Receiving damage#Block", "Damage calculation#Increased and reduced"]
pipeline_why: "per-charge spell block adds to the block chance used in the block step; per-charge elemental damage is an increased-pool mod multiplied by the charge count"
target: self
related: [power-charges, block, chance-on-hit-uptime, defences, spell-suppression, unique-ralakeshs-impatience]
pob:
  measured: config
  how: "Power charges exist only if usePowerCharges is ticked (ConfigOptions.lua:900, default unticked); PoB then assumes PowerChargesMax (CalcPerform.lua:1044, 1117 sets Multiplier PowerCharge); overridePowerCharges (ConfigOptions.lua:903) sets a count. The per-charge lines parse (ModCache.lua:2214 SpellBlockChance BASE 5 x Multiplier PowerCharge; 9960 / 9137 ElementalDamage INC x PowerCharge). The charge-gain line (ModCache.lua:16234) and the lose-on-block line (ModCache.lua:17542 / 16235) are `{nil, leftover}` = unparsed; grep ModParser.lua for 'power charge every' / 'every second if you haven' found no hit. 'Recently lost' and 'lose on block' are not modelled. The tick does not read the item. Measured in Rue Worb.xml item set 7 (b5c-ia2.md): PoB shows 12/12 Power Charges at every tick state because Ralakesh's Impatience (Power variant, 'Count as having maximum number of Power Charges', flag HaveMaximumPowerCharges, CalcPerform.lua:1106-1107) forces the maximum; usePowerCharges on/off and overridePowerCharges 0/1/2 give identical FullDPS (31,460,171 Pinnacle base in the PoB-order rerun, b5c-ia4.md section 3). The Willclash lines have no consumer for the two unparsed texts: verified (chain) from the item mod list, ModCache lines below."
  config:
    - {var: usePowerCharges, default: false, ref: "Modules/ConfigOptions.lua:900", class: c}
    - {var: overridePowerCharges, default: "blank = max", ref: "Modules/ConfigOptions.lua:903", class: c}
    - {var: HaveMaximumPowerCharges, default: false, ref: "Modules/CalcPerform.lua:1106-1107", class: a}
  unparsed:
    - "Willclash: 'Gain a Power Charge every Second if you haven't lost Power Charges Recently' -> Data/ModCache.lua:16234 {nil, leftover}"
    - "Willclash: 'Lose all Power Charges when you Block' -> Data/ModCache.lua:17542 / 16235 {nil, leftover}"
model:
  proposed_kind: power_charge_uptime_lose_on_block
  inputs: {from_pob: [enemySkillTime, SpellBlockChance, BlockChance, PowerChargesMax], from_scenario: [enemy attack interval (boss speed)], measured_set_7: "enemySkillTime 5 s in both scenarios (3.5 s with the helmet groups off; likely the frozen / chilled / cold exposure ticks of config set 7, not isolated), BlockChance 55, SpellBlockChance 18 without Willclash, PowerChargesMax 12 (Base 3, Malachai's Loop +2, two Foulborn Romira's Banquet +1 each, Graven's Secret +1, four tree nodes +1 each)"}
  params: {recently_seconds: 4, charge_gain_per_second: 1, max_charges: 3, note_max_charges: "max_charges 3 = base PowerChargesMax; Willclash alone makes at most that many, the 12 in set 7 come from other sources and Ralakesh"}
  formula: "P(at least n charges) ~ exp(-b x (4 + n)), b = blocks per second = (1 / enemySkillTime) x chance a hit is blocked; no block -> 3 charges (max) 7 s after the last loss. Per charge +5% spell block and +3-5% increased Elemental Damage; at 3 charges +15% spell block and +9-15% elemental. Examples: 700 ms and 50% block -> b = 0.71/s -> P(>=1) 2.8%, P(>=3) 0.7%; 5 s boss interval and 50% block -> b = 0.1/s -> P(>=1) 61%, P(>=3) 50%"
  calibration: "derived, not PoB; 'Recently' = 4 s and the tick phase are assumptions (NOT VERIFIED, wiki Recently not fetched); enemySkillTime from CalcDefence.lua:2963 (config enemySpeed ConfigOptions.lua:2362 default 700 ms, or the selected boss speed ConfigOptions.lua:2318-2320; Data/BossSkills.lua 1000-25000 ms)"
providers:
  - {kind: unique, name: "Willclash", variant: "no variants", slot: helmet, role: sustains, target: self, text: "(350-400)% increased Evasion and Energy Shield (local)", source: "Data/Uniques/helmet.lua:1707-1715; Data/ModCache.lua:8827, 9489", pob: full}
  - {kind: unique, name: "Willclash", variant: "no variants", slot: helmet, role: sustains, target: self, text: "+5% Chance to Block Spell Damage per Power Charge", source: "Data/ModCache.lua:2214", pob: config}
  - {kind: unique, name: "Willclash", variant: "no variants", slot: helmet, role: scales, target: self, text: "(3-5)% increased Elemental Damage per Power charge", source: "Data/ModCache.lua:9960, 9137", pob: config}
  - {kind: unique, name: "Willclash", variant: "no variants", slot: helmet, role: enables, target: self, text: "Gain a Power Charge every Second if you haven't lost Power Charges Recently", source: "Data/ModCache.lua:16234", pob: none}
  - {kind: unique, name: "Willclash", variant: "no variants", slot: helmet, role: blocks, target: self, text: "Lose all Power Charges when you Block", source: "Data/ModCache.lua:17542, 16235", pob: none}
package:
  seed: none
  slot: "Helmet"
  base: "Golden Mask (req 35, 40 Dex / 40 Int; base ES 20-22, Eva 96-103)"
  variant: "none"
  removal: "PoB removal delta on Rue Worb.xml, item set 7 'Occultist Swap' (Willclash item 61, range 350-400% roll 1, no implicit; activated with its skill set 7, config set 7 and spec 'Occultist Swap'), main skill Winter Orb. NOT the active set 9. Absolute numbers from b5c-ia4.md section 3 (PoB's own rebuild order; IA2's earlier absolutes were 6.25% too low, its removal effects stand). Pinnacle (enemyIsBoss Pinnacle): base FullDPS 31,460,171, Winter Orb TotalDPS 6,291,913, TotalEHP 151,174, spell block 75; helmet removed FullDPS 29,520,496 (-6.2%), TotalEHP 62,925 (-58.4%), spell block 18; game-like row = helmet removed AND its Helmet-slot socket groups (Frost Shield + Bonechill) disabled: FullDPS 26,924,556 (-14.4%), enemy action interval 5 -> 3.5 s (b5c-ia2.md). Mapping: base FullDPS 42,202,310, TotalEHP 88,421; helmet removed 39,599,329 (-6.2%), TotalEHP 36,836 (-58.3%); game-like 36,124,856 (-14.4%). PoB keeps the emptied slot's gems active (CalcSetup.lua:1605-1608), so the -14.4% row is the one that matches the game. Per line (relative, IA2 run, Pinnacle; the same percentages in Mapping): (3-5)% increased Elemental Damage per Power Charge -6.2% FullDPS, all of the helmet's -6.2% (5% x 12 charges = 60% increased Elemental Damage on Winter Orb); +5% spell block per charge 0.0% FullDPS, TotalEHP -52% (spell block 75 -> 18; ES 8,074 -> 7,068 through PoB's ES from spell block, CalcDefence.lua:833); (350-400)% increased Evasion and ES 0.0% FullDPS, TotalEHP -11% (ES 8,074 -> 7,514, Evasion 5,141 -> 3,950); +1 max Power Charge implicit: absent in item 61. Fixed charge counts (both per-charge lines made flat, IA2 run, relative to its base): 1 charge FullDPS -5.7% (spell block 23), 2 charges -5.2% (28), 3 charges -4.6% (33; what Willclash alone can reach), 6 charges -3.1% (48). Headless single-enemy deltas, not game facts; set 8 'Occultist Week 1' is a half-finished set in the file (38 unmet requirements, enemy action speed 0, one item in both ring slots) and is not quoted."
  downsides_that_are_the_point: ["Lose all Power Charges when you Block: built for builds that do NOT block (suppression, evasion, dodge); on a block build it is nearly a dead helmet after the first block", "PoB's usePowerCharges tick ignores this line and credits full charges"]
  foulborn: "none (no Willclash entry in ModFoulbornMap)"
  obtainability: "cargo drop_enabled 1, is_drop_restricted 0, drop_level null, req 35, release 3.12.0 (Heist); wiki rev 1539150: league-specific history, '3.12.5e ... drop disabled', 3.14.0 many league-specific items added to the core drop pool (entry does not name Willclash); NOT VERIFIED whether it is in the plain core pool or still tag-gated; patch 3.29"
  block_sources_in_set_7: "Block sources that would fire 'Lose all Power Charges when you Block' in game (b5c-ia2.md, base modDB, Pinnacle = Mapping): attack BlockChance 55 (Twilight Regalia 7, three Cobalt Jewel lines 3 each conditional, tree node 45558 4 per Shield Block stat, Rumi's Concoction flask 12 while using it); spell block 18 without Willclash (tree 43061 +4, tree 6770 +10, flask +4); with Willclash at 12 charges 75 (SpellBlockChanceMax). PoB shows none of this: both charge lines are unparsed (Data/ModCache.lua:16234 and 16235 for the gain line, 16235 and 17542 for the lose line). Whether 'Block' in the line covers spell block as well as attack block is NOT VERIFIED."
makes_redundant:
  - {provider: "other power-charge generators (on-kill sources, Power Siphon)", when: "no block in the build", why: "Willclash generates up to 3 charges by itself", source: "Data/ModCache.lua:16234"}
conflicts:
  - {with: "any block source on the same character (shield, block flasks)", effect: "each block removes all Power Charges", source: "Data/ModCache.lua:17542"}
  - {with: "charge-consuming skills", effect: "reset the 'lost recently' window", source: "Data/ModCache.lua:16234"}
conditions:
  - {text: "charge gain needs no Power Charge lost in the last (assumed) 4 s; per-charge lines need PoB tick usePowerCharges or a hand-set count", source: "Modules/ConfigOptions.lua:900-903; Data/ModCache.lua:16234"}
uptime:
  Mapping:       {value: model, config: {usePowerCharges: "model: PoB ticks max charges; real uptime depends on blocks per second (in Rue Worb set 7 the tick is irrelevant, Ralakesh forces max)"}, reasoning: "packs hit often (default enemySkillTime 700 ms), so a blocking build has about 0 charges; a non-blocking build reaches 3 charges 7 s after the last loss; measured set 7: enemySkillTime 5 s, attack block 55", source: "Modules/CalcDefence.lua:2963; Modules/ConfigOptions.lua:2362; b5c-ia2.md"}
  Pinnacle Boss: {value: model, config: {usePowerCharges: "model: PoB ticks max charges; real uptime depends on blocks per second"}, reasoning: "a boss with slow hits keeps charges unless the player blocks them (5 s interval, 50% block: P(>=3) about 50%); PoB ticks both scenarios as max", source: "Modules/ConfigOptions.lua:2318-2320; Data/BossSkills.lua; b5c-ia2.md (set 7 enemySkillTime 5 s)"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Willclash (rev 1539150)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Data/Uniques/helmet.lua, Modules/ConfigOptions.lua, Modules/CalcPerform.lua, Modules/CalcDefence.lua, Data/ModCache.lua", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b2c-item-analyst-leaguestart.md", kind: discovery, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b5c-ia2.md (Willclash set 7 relative effects, block sources) and b5c-ia4.md section 3 (corrected absolutes)", kind: pob, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: tick phase and the 4 s 'recently' window (wiki Recently not fetched)"
  - "NOT VERIFIED: whether 'Lose all Power Charges when you Block' triggers on spell block as well as attack block (wiki page has no text; assumed yes)"
  - "NOT VERIFIED: Willclash drop-pool status (Heist-only history; cargo says drop_enabled 1)"
  - "NOT VERIFIED: whether Ralakesh's Impatience 'Count as having maximum number of Power Charges' keeps Willclash's per-charge mods at maximum after charges are lost on a block in game (PoB flag HaveMaximumPowerCharges, CalcPerform.lua:1106-1107, ignores the loss)"
  - "NOT VERIFIED: that Rue Worb.xml item set 7 is the Willclash setup the user means (active set 9 wears Eye of Malice); the cause of the 5 s enemy action interval (frozen / chilled / cold exposure ticks) was not isolated"
open_questions:
  - "PoB's usePowerCharges tick ignores 'Lose all Power Charges when you Block' and the charge-gain line (both unparsed): should the generator treat Willclash charges as zero for any build with a block source, instead of PoB's max charges?"
```
