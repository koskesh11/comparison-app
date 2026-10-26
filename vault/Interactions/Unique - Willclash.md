---
type: interaction
status: draft
pob_refs: [usePowerCharges, overridePowerCharges, PowerChargesMax, SpellBlockChance, enemySkillTime]
source: "PoB 2.67.2 Data/Uniques/helmet.lua:1707-1715, Data/Bases/helmet.lua:804-812, Modules/ConfigOptions.lua:900-903 and 2318-2362, Modules/CalcPerform.lua:1044 and 1117, Modules/CalcDefence.lua:2963, Data/ModCache.lua lines per provider; poewiki Willclash rev 1539150; vault notes power-charges, block, chance-on-hit-uptime; b2c-item-analyst-leaguestart.md (task 027 batch 2c)"
last_confirmed_patch: "3.29.x"
---

Willclash is a Golden Mask that generates a Power Charge every second while none was lost recently, gives +5% spell block and (3-5)% increased Elemental Damage per Power Charge, and loses all Power Charges when you Block. It is built for characters that do not block (suppression, evasion, dodge) so the charge loop survives; on a block build it is nearly a dead helmet after the first block.
PoB only has the usePowerCharges tick (default off), which assumes max charges: charge gain, "recently lost" and "lose on block" are not modelled, so PoB over-credits Willclash with full block and damage whenever the tick is on. Two lines are unparsed (red).
Uniques are packages: every line is valued, including the downside that is the point (lose all charges on block).

Pipeline: [[Defences#Block chance]] / [[Receiving damage#Block]] - spell block per charge; [[Damage calculation#Increased and reduced]] - elemental damage per charge

```interaction
id: unique-willclash
mechanic: "Unique package: free Power Charges (up to 3) that scale spell block and elemental damage - until you block, which removes them all"
family: charge
pipeline_step: ["Defences#Block chance", "Receiving damage#Block", "Damage calculation#Increased and reduced"]
pipeline_why: "per-charge spell block adds to the block chance used in the block step; per-charge elemental damage is an increased-pool mod multiplied by the charge count"
target: self
related: [power-charges, block, chance-on-hit-uptime, defences, spell-suppression]
pob:
  measured: config
  how: "Power charges exist only if usePowerCharges is ticked (ConfigOptions.lua:900, default unticked); PoB then assumes PowerChargesMax (CalcPerform.lua:1044, 1117 sets Multiplier PowerCharge); overridePowerCharges (ConfigOptions.lua:903) sets a count. The per-charge lines parse (ModCache.lua:2214 SpellBlockChance BASE 5 x Multiplier PowerCharge; 9960 / 9137 ElementalDamage INC x PowerCharge). The charge-gain line (ModCache.lua:16234) and the lose-on-block line (ModCache.lua:17542 / 16235) are `{nil, leftover}` = unparsed; grep ModParser.lua for 'power charge every' / 'every second if you haven' found no hit. 'Recently lost' and 'lose on block' are not modelled. The tick does not read the item. Removal delta not measured (no headless run)."
  config:
    - {var: usePowerCharges, default: false, ref: "Modules/ConfigOptions.lua:900", class: c}
    - {var: overridePowerCharges, default: "blank = max", ref: "Modules/ConfigOptions.lua:903", class: c}
  unparsed:
    - "Willclash: 'Gain a Power Charge every Second if you haven't lost Power Charges Recently' -> Data/ModCache.lua:16234 {nil, leftover}"
    - "Willclash: 'Lose all Power Charges when you Block' -> Data/ModCache.lua:17542 / 16235 {nil, leftover}"
model:
  proposed_kind: power_charge_uptime_lose_on_block
  inputs: {from_pob: [enemySkillTime, SpellBlockChance, PowerChargesMax], from_scenario: [enemy attack interval (boss speed)]}
  params: {recently_seconds: 4, charge_gain_per_second: 1, max_charges: 3}
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
  removal: "NOT MEASURED"
  downsides_that_are_the_point: ["Lose all Power Charges when you Block: built for builds that do NOT block (suppression, evasion, dodge); on a block build it is nearly a dead helmet after the first block", "PoB's usePowerCharges tick ignores this line and credits full charges"]
  foulborn: "none (no Willclash entry in ModFoulbornMap)"
  obtainability: "cargo drop_enabled 1, is_drop_restricted 0, drop_level null, req 35, release 3.12.0 (Heist); wiki rev 1539150: league-specific history, '3.12.5e ... drop disabled', 3.14.0 many league-specific items added to the core drop pool (entry does not name Willclash); NOT VERIFIED whether it is in the plain core pool or still tag-gated; patch 3.29"
makes_redundant:
  - {provider: "other power-charge generators (on-kill sources, Power Siphon)", when: "no block in the build", why: "Willclash generates up to 3 charges by itself", source: "Data/ModCache.lua:16234"}
conflicts:
  - {with: "any block source on the same character (shield, block flasks)", effect: "each block removes all Power Charges", source: "Data/ModCache.lua:17542"}
  - {with: "charge-consuming skills", effect: "reset the 'lost recently' window", source: "Data/ModCache.lua:16234"}
conditions:
  - {text: "charge gain needs no Power Charge lost in the last (assumed) 4 s; per-charge lines need PoB tick usePowerCharges or a hand-set count", source: "Modules/ConfigOptions.lua:900-903; Data/ModCache.lua:16234"}
uptime:
  Mapping:       {value: model, config: {usePowerCharges: "model: PoB ticks max charges; real uptime depends on blocks per second"}, reasoning: "packs hit often (default enemySkillTime 700 ms), so a blocking build has about 0 charges; a non-blocking build reaches 3 charges 7 s after the last loss", source: "Modules/CalcDefence.lua:2963; Modules/ConfigOptions.lua:2362"}
  Pinnacle Boss: {value: model, config: {usePowerCharges: "model: PoB ticks max charges; real uptime depends on blocks per second"}, reasoning: "a boss with slow hits keeps charges unless the player blocks them (5 s interval, 50% block: P(>=3) about 50%); PoB ticks both scenarios as max", source: "Modules/ConfigOptions.lua:2318-2320; Data/BossSkills.lua"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Willclash (rev 1539150)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Data/Uniques/helmet.lua, Modules/ConfigOptions.lua, Modules/CalcPerform.lua, Modules/CalcDefence.lua, Data/ModCache.lua", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b2c-item-analyst-leaguestart.md", kind: discovery, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: tick phase and the 4 s 'recently' window (wiki Recently not fetched)"
  - "NOT VERIFIED: whether 'Lose all Power Charges when you Block' triggers on spell block as well as attack block (wiki page has no text; assumed yes)"
  - "NOT VERIFIED: Willclash drop-pool status (Heist-only history; cargo says drop_enabled 1)"
  - "NOT VERIFIED: removal delta (no headless run)"
open_questions:
  - "PoB's usePowerCharges tick ignores 'Lose all Power Charges when you Block' and the charge-gain line (both unparsed): should the generator treat Willclash charges as zero for any build with a block source, instead of PoB's max charges?"
```
