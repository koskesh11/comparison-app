---
type: interaction
status: draft
pob_refs: [BlockChance, SpellBlockChance, BlockChanceMax, SpellBlockChanceMax, ShieldBlockChance, BlockEffect, SpellBlockChanceOverCap, BlockChanceCap, DisableEHPGainOnBlock, TotalEHP]
source: "poewiki Blocking rev 1648970 ('Block' redirects to it; fetched 2026-10-26); PoB 2.67.2 CalcDefence.lua / Data.lua / Item.lua / ModParser.lua; TreeData/3_29/tree.lua; headless probes on CoC EK Assa.xml and Worb.xml (b1-mechanics-researcher.md)"
last_confirmed_patch: "3.29.x"
---

Blocking is a random roll per hit that prevents the whole hit unless Glancing Blows applies; it works against hits only (not damage over time), attack and spell block are separate stats (since 3.4.0), and the default maximum is 75%, raisable to a hard cap of 90% (3.24.0). A blocked hit cannot apply on-hit effects. PoB computes chance, caps and the EHP expectation, but block is not in the maximum hit (CalcDefence.lua:3208-3266 has no block), so it never moves a max-hit goal. Related: [[Defences]], [[Spell suppression]], [[Armour and physical max hit]].
Impact: EK - block is already 78 attack and 78 spell (cap raised to 78); PoB counts it in TotalEHP (145,259) but NOT in the physical max hit 7,538; Reckless Defence's 181% increased crit chance against you is the price (worth little under CI + 78% block but real for spell crit damage). Fireball Elementalist - a shield is compatible (the Worb sample runs wand + Titanium Spirit Shield: BlockChance 44, SpellBlockChance 57); expect about 37-45% attack block from the shield base alone (25 x (1 + local%)) and spell block only from nodes (Arcane Guarding +10, Arcane Sanctuary +8, Sanctuary +4, Safeguard +10 and +3 max); block lowers the average hit taken by chance (TotalEHP) but does not move the 7,000 physical goal, and Glancing Blows halves block's value in damage terms, so keep it off unless on-block triggers are the point.
Pipeline: [[Receiving damage#Block]] - the wiki rolls block (step 10) after stun and all mitigation, removing the whole hit (or all but 35% with Glancing Blows), so it matters for on-hit effects, recoup and 'when you block' triggers, not just damage numbers; [[Defences#Block chance]] holds the caps

```interaction
id: block
mechanic: "Random roll per hit that prevents the whole hit (65% less with Glancing Blows); attack and spell block are separate; default max 75%, hard cap 90%; hits only, never damage over time; a blocked hit cannot apply on-hit effects"
family: defence
pipeline_step: ["Receiving damage#Block", "Defences#Block chance"]
pipeline_why: "wiki step 10, after stun and combining damage: block removes the whole hit after armour, resistance and suppression were applied, so it gates on-hit effects, recoup and block triggers; in PoB it is an independent EHP factor and not part of the maximum hit"
target: self
related: [spell-suppression, armour-phys-max-hit, max-resistances]
pob:
  measured: partial
  how: "full for chance, caps and the EHP expectation, partial for order and triggers. CalcDefence.lua:679-785: BlockChanceMax = min(sum BlockChanceMax, Data.lua:249 BlockChanceCap 90) (679); shield base from the item baseBlockChance = Weapon 2 armourData.BlockChance (688-695) = floor((base + local base) x (1 + local INC/100)) (Classes/Item.lua:2410-2411; Titanium Spirit Shield base 25, Data/Bases/shield.lua:656); BlockChance = round((shield + sum BASE BlockChance) x (1 + sum INC BlockChance/100) x MORE) capped at max (708-712); SpellBlockChance = round(sum BASE SpellBlockChance x (1 + inc/100) x more), no shield base (729-733); spell cap SpellBlockChanceMax (719); BlockEffect = 100 - sum BASE BlockEffect (786; ModParser.lua:2372 'you take N% of damage from blocked hits'); EHP factor blockEffect = 1 - BlockChance x BlockEffect/100 (2799); Glancing Blows doubling = MORE 100 on both stats (ModParser.lua:2370-2371); lucky/unlucky 755-783. Not in max hit (3208-3266). On-block recoveries enter EHP only with NumberOfDamagingHits > 1 (2804-2813, DisableEHPGainOnBlock config). Measured: EK ShieldBlockChance 45 (floor(25 x 1.8)), BlockChance 78, SpellBlockChance 78, BlockChanceMax 78 (source of the 78 cap not traced), SpellBlockChanceOverCap 3, BlockEffect 100; Worb ShieldBlockChance 37 (floor(25 x 1.5), crafted 50% increased), BlockChance 44, SpellBlockChance 57, max 75, BlockEffect 100."
  config:
    - {var: DisableEHPGainOnBlock, default: false, ref: "Modules/CalcDefence.lua:2804-2813 (ConfigOptions.lua line not looked up)", class: b}
    - {var: EHPUnluckyWorstOf, default: 1, ref: "Modules/ConfigOptions.lua:226", class: b}
    - {var: CannotBeBlocked, default: "enemy flag; config box not located", ref: "Modules/CalcDefence.lua:756,2796 (also reduceEnemyBlock)", class: b}
  unparsed: ["EK sample items: 'Recover 4% of Energy Shield when you Block' and '18% increased Stun and Block Recovery' (block-animation speed only, no damage effect; PoB does not use the second for damage); no other unparsed line found in the two samples"]
model: null
providers:
  - {kind: mod, name: "Titanium Spirit Shield (base)", slot: Weapon 2, role: enables, target: self, text: "attack block 25 (local), ES 67-77; a local 'N% increased Chance to Block' multiplies only the shield's own value (cargo local_block_chance_+%, T7 76-81)", source: "Data/Bases/shield.lua:649-656; Classes/Item.lua:2411", pob: full}
  - {kind: mod, name: "shield prefix 'increased Chance to Block' (since 3.25.0)", slot: shield, role: scales, target: self, text: "cargo local_block_chance_+%, LocalIncreasedBlockPercentage1-7 (40-45 ... 76-81)", source: "wiki cargo mod_stats; https://www.poewiki.net/wiki/Blocking rev 1648970 (version 3.25.0)", pob: full}
  - {kind: unique, name: "Reckless Defence", slot: jewel, role: applies, target: self, text: "+6% Chance to Block Attack Damage; +6% Chance to Block Spell Damage; Hits have 181% increased Critical Strike Chance against you (EK carries 2 copies)", source: "CoC EK Assa.xml items 4, 8", pob: full}
  - {kind: notable, name: "Arcane Guarding", slot: tree, role: applies, target: self, text: "+10% Chance to Block Spell Damage while holding a Shield", source: "TreeData/3_29/tree.lua:34732", pob: full}
  - {kind: notable, name: "Arcane Sanctuary", slot: tree, role: applies, target: self, text: "+8% Chance to Block Spell Damage while holding a Shield", source: "TreeData/3_29/tree.lua:45597", pob: full}
  - {kind: notable, name: "Safeguard", slot: tree, role: scales, target: self, text: "+3% to maximum Chance to Block Spell Damage; Recover 50 ES when you Block Spell Damage; +10% chance to Block Spell Damage while holding a Staff or Shield", source: "TreeData/3_29/tree.lua:28815", pob: full}
  - {kind: notable, name: "Sanctuary", slot: tree, role: applies, target: self, text: "+4% Chance to Block Attack Damage while holding a Shield; +4% Chance to Block Spell Damage while holding a Shield", source: "TreeData/3_29/tree.lua:30786", pob: full}
  - {kind: notable, name: "As The Mountain", slot: tree, role: scales, target: self, text: "+12% Chance to Block Attack Damage while Dual Wielding or holding a Shield; +3% to maximum Chance to Block Attack Damage", source: "TreeData/3_29/tree.lua:26479", pob: full}
  - {kind: keystone, name: "Glancing Blows", slot: tree, role: scales, target: self, text: "Chance to Block Attack Damage is doubled; Chance to Block Spell Damage is doubled; You take 65% of Damage from Blocked Hits", source: "TreeData/3_29/tree.lua:28427; Modules/ModParser.lua:2370-2372", pob: full}
  - {kind: keystone, name: "Versatile Combatant", slot: tree, role: blocks, target: self, text: "-10% to maximum Chance to Block Attack/Spell Damage; +2% Chance to Block Spell Damage for each 1% Overcapped Chance to Block Attack Damage", source: "TreeData/3_29/tree.lua:47087", pob: partial}
  - {kind: ascendancy, name: "Vile Bastion (Occultist)", slot: tree, role: scales, target: self, text: "Maximum Energy Shield is increased by Chance to Block Spell Damage", source: "TreeData/3_29/tree.lua:44223", pob: partial}
  - {kind: mod, name: "dual wielding", slot: two weapons, role: applies, target: self, text: "Dual wielding also innately grants +20% chance to Block Attack Damage (cargo inherent_block_while_dual_wielding_% 20)", source: "https://www.poewiki.net/wiki/Blocking rev 1648970", pob: full}
makes_redundant: []
conflicts:
  - {with: "Glancing Blows", effect: "never better for damage alone: expected damage taken without = 1 - b, with = 1 - min(2b, cap) x 0.35, at most 1 - 0.7b (capped at 0.75 x 0.35 = 0.26) - arithmetic from the keystone text and PoB's BlockEffect 35; its use is on-block effects", source: "TreeData/3_29/tree.lua:28427; Modules/CalcDefence.lua:786 (derived)"}
  - {with: "on-hit effects of the attacker", effect: "a blocked hit still cannot apply on-hit effects, such as ailments or curses", source: "https://www.poewiki.net/wiki/Blocking rev 1648970"}
  - {with: "staff block vs shield block", effect: "a shield needs a one-handed main hand; staves are two-handed and have their own block nodes (Staff Block / Whirling Barrier, tree.lua:20303-20499), mutually exclusive with a shield", source: "TreeData/3_29/tree.lua:20303-20499"}
  - {with: "dual wield +20% attack block", effect: "does not combine with shield-only nodes (node text 'while holding a Shield'); a shield adds spell block only through nodes and mods (no shield base for spell block)", source: "https://www.poewiki.net/wiki/Blocking rev 1648970; Modules/CalcDefence.lua:729-733"}
conditions:
  - {text: "random roll per hit, no cooldown, works while frozen or stunned; 'when you block' effects fire before damage is taken; secondary damage from a spell or attack skill can be blocked, no block against self-damage or non-skill explosions", source: "https://www.poewiki.net/wiki/Blocking rev 1648970"}
  - {text: "conditional lines ('if you've Attacked Recently', 'if you have not blocked recently') follow the matching condition; those condition boxes were not verified", source: "Modules/ModParser.lua:4137-4140 (as cited by the researcher)"}
uptime:
  Mapping:
    value: always
    config: {}
    reasoning: "gear and tree stat; conditional lines follow their condition"
    source: "b1-mechanics-researcher.md"
  Pinnacle Boss:
    value: always
    config: {CannotBeBlocked: "enemy flag exists in PoB, config box not located"}
    reasoning: "always as a stat, but some boss hits may be unblockable (undocumented in the evidence); enemy flags CannotBeBlocked / reduceEnemyBlock exist in PoB"
    source: "Modules/CalcDefence.lua:756,2796"
seeds: [EK, Worb]
sources:
  - {ref: "https://www.poewiki.net/wiki/Blocking (rev 1648970, 2026-05-20); version rows 3.24.0 max block can no longer exceed 90%, 3.25.0 shield prefixes changed to 'increased Chance to Block', 3.4.0 attack and spell block reworked into two stats", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcDefence.lua:679-785,2796-2813; Modules/Data.lua:249; Classes/Item.lua:2410-2411; Modules/ModParser.lua:2370-2372 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b1-mechanics-researcher.md", kind: discovery, patch: "3.29"}
not_verified:
  - "source of EK's BlockChanceMax 78 (not traced)"
  - "config box names and lines for BlockedRecently, CannotBeBlocked and DisableEHPGainOnBlock"
  - "unblockable boss hits"
  - "cargo spawn tables for spell block prefixes and suffixes on shields and their tags (templated queries not run)"
  - "whether every sample block line is counted by PoB (stun / block recovery lines do not enter damage)"
  - "the Fireball-with-shield attack-block estimate (about 37-45%) is derived from 25 x (1 + local%), not measured on a Fireball build"
open_questions:
  - "The wiki says 'Blocked hits also prevent trigger effects from activating, such as Cast on Critical Strike Support' in the context of the attacker's on-hit effects; whether it means an ENEMY blocking the player's CoC-triggering hit is not stated, so no EK claim is made. Does the user know?"
```
