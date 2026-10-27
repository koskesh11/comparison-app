---
type: interaction
status: draft
pob_refs: [BlockChance, SpellBlockChance, BlockChanceMax, SpellBlockChanceMax, BlockChanceOverCap, BlockEffect, DamageTakenOnBlock, EffectiveBlockChance, EffectiveSpellBlockChance, TotalEHP, DisableEHPGainOnBlock, enemyIsBoss]
source: "poewiki Glancing Blows rev 1618363 (version history ends 3.12.0), Blocking rev 1648970 (fetched 2026-10-26); PoB 2.67.2 CalcDefence.lua / ModParser.lua / ConfigOptions.lua / Data/ModCache.lua / TreeData 3_29; headless runs on EK, FR and the Fireball seed (scratchpad b3c/F_run.py, evidence b3c/tree-ascendancy-analyst-F.md)"
last_confirmed_patch: "3.29.x"
---

Glancing Blows (keystone, node 39713, TreeData/3_29/tree.lua:28427-28431) doubles the chance to block attack damage and spell damage and makes you "take 65% of Damage from Blocked Hits". For damage mitigation alone it never wins in PoB: a blocked hit used to be fully prevented (share of damage prevented = b x 100%); with the keystone a doubled chance prevents only 35% of each blocked hit (2b x 35% = 0.7b), so the prevented share falls by 30% at every block chance below half the cap and by much more at or above the cap. On EK (block already at the 78% cap) TotalEHP drops -69.7%; on FR (-46.7%) and the Fireball seed (-5.7%) too. Its value has to come from something PoB's EHP does not count: blocked hits still cannot apply ailments or curses (wiki), more block means more 'on block' triggers and recovery, and block-scaled effects. Related: [[Block]] (block chance, caps and mechanics; written on another branch and resolved at merge), [[Defences]], [[Receiving damage]].

Pipeline: [[Receiving damage#Block]] - PoB multiplies each damage type by 1 - BlockChance x BlockEffect/100 (CalcDefence.lua:2799); the keystone sets BlockEffect to 35 (the share of the hit that is prevented), so the same block chance prevents 35% instead of 100%. Chances and caps: [[Defences#Block chance]].

How PoB applies it: the three lines are three mods (Data/ModCache.lua:14674 BlockChance MORE 100, 14677 SpellBlockChance MORE 100, 22989 BlockEffect BASE 65; Modules/ModParser.lua:2370-2372). CalcDefence.lua:708-712 builds BlockChance as round((base + BASE sum) x (1 + INC) x More(BlockChance)) capped at BlockChanceMax; CalcDefence.lua:729-733 builds SpellBlockChance as round(SpellBlockChance BASE sum x (1 + INC) x the SAME More(BlockChance)) capped at SpellBlockChanceMax; CalcDefence.lua:786-789 sets output.BlockEffect = 100 - BlockEffect BASE sum and DamageTakenOnBlock = 100 - BlockEffect. The 'MORE 100' on SpellBlockChance (14677) is never read: PoB's spell block is doubled only because the attack line doubles the shared 'BlockChance' More. Measured below.

Measured (headless, in memory, nothing saved; keystone only - node 39713 force-allocated alone, path cost not included; enemy level from the headless run: 85 at None, 84 at Pinnacle):

| Seed | attack block (cap) | spell block (cap) | BlockEffect / damage taken on block | TotalEHP None | TotalEHP Pinnacle |
|---|---|---|---|---|---|
| EK | 78 -> 78 (78), natural 78 -> 156 (overcap 0 -> 78) | 78 -> 78 (78), natural 81 -> 162 (overcap 3 -> 84) | 100 -> 35 / 0 -> 65 | 71911 -> 21782 (-69.7%) | 145259 -> 44014 (-69.7%) |
| FR | 44 -> 75 (75), natural 88 (overcap 0 -> 13) | 78 -> 78 (78), overcap 3 -> 98 (more than the doubled 81: a spell-block-per-overcapped-attack-block mod on FR also grows; not decomposed) | 100 -> 35 / 0 -> 65 | 102318 -> 54496 (-46.7%) | 273342 -> 145510 (-46.8%) |
| Fireball seed (NOT VIABLE) | 25 -> 50 (75) | 8 -> 16 (75) | 100 -> 35 / 0 -> 65 | 7806 -> 7365 (-5.7%) | 12065 -> 11386 (-5.6%) |

- Break-even: prevented damage share is b x 100% before and min(2b, cap) x 35% after. With b = 25 (Fireball seed) it is 25% before and 17.5% after; there is no block chance at which the keystone raises PoB's mitigation, because 0.35 x 2 = 0.7 < 1.
- Max block caps: BlockChanceMax 78 on EK, 75 on FR and the Fireball seed; SpellBlockChanceMax 78 on EK and FR, 75 on the Fireball seed. Doubling beyond the cap only grows the overcap (EK).
- The FR config ticks DisableEHPGainOnBlock (ConfigOptions.lua:227), so block-triggered recovery is excluded from FR's TotalEHP; the real value of a doubled block chance with ES on block is not in the FR row.
- Test of the two chance lines (Fireball seed, custom lines instead of the keystone): 'Chance to Block Attack Damage is doubled' alone doubled BOTH attack block (25 -> 50) and spell block (8 -> 16), TotalEHP 7806 -> 9732 (None); 'Chance to Block Spell Damage is doubled' alone changed nothing. No provider in PoB's data carries the spell line without the attack line (grep: tree.lua:28431 and Data/TattooPassives.lua:634-635 only), so the keystone itself is not wrong; a future spell-only doubling would be.
- DPS keys are unchanged (Fireball seed ManaRegen changed through a block-scaled mana regeneration mod; not decomposed).

What PoB's EHP does not count (wiki): a blocked hit still cannot apply ailments or curses (wiki Blocking rev 1648970), and this keystone does not change that; PoB's TotalEHP has no ailment-avoidance term from block (no BlockChance use near ailment avoidance in Modules; grep). The extra block chance therefore buys avoided ailments and on-block triggers that the measured EHP loss does not show.

```interaction
id: glancing-blows
mechanic: "Chance to Block Attack Damage is doubled; Chance to Block Spell Damage is doubled; You take 65% of Damage from Blocked Hits (block prevents only 35% of a blocked hit); a blocked hit still cannot apply on-hit effects such as ailments or curses (wiki)"
family: defence
target: self
related: [defences, receiving-damage, block]
pipeline_step: ["Receiving damage#Block", "Defences#Block chance"]
pipeline_why: "Block is an independent expected-value factor in PoB (1 - BlockChance x BlockEffect/100, CalcDefence.lua:2799); the keystone doubles the chance (More on BlockChance, capped by the block maximum) and cuts the prevention per block to 35%, so the factor goes from 1 - b to 1 - 0.7b (below the cap) - strictly worse for damage taken, better only for effects that depend on a block happening."
pob:
  measured: full
  how: "Data/ModCache.lua:14674 (BlockChance MORE 100), 14677 (SpellBlockChance MORE 100), 22989 (BlockEffect BASE 65); Modules/ModParser.lua:2370-2372; CalcDefence.lua:708-712 (attack block with More(BlockChance)), 729-733 (spell block also uses More(BlockChance); SpellBlockChance MORE is not read), 786-789 (BlockEffect = 100 - BASE sum), 2794-2799 (EHP factor). Measured headless on EK, FR, Fireball seed (node 39713 alone, None and Pinnacle): TotalEHP EK -69.7%, FR -46.7% / -46.8%, Fireball -5.7% / -5.6%; EK block already at its 78 cap; FR attack block 44 -> 75 (cap); Fireball 25 -> 50 and 8 -> 16; DamageTakenOnBlock 0 -> 65. Custom-line test: the attack 'doubled' line alone doubles both block types, the spell line alone does nothing. Not modelled: ailment and curse avoidance of blocked hits, on-block triggers when DisableEHPGainOnBlock is set (FR)."
  config:
    - {var: DisableEHPGainOnBlock, default: "false (FR build ticks it)", ref: "Modules/ConfigOptions.lua:227 (excludes life/mana/ES gained on block or suppress from the EHP; visible only when a gain-on-block mod exists)", class: c}
    - {var: EHPUnluckyWorstOf, default: "Average", ref: "Modules/ConfigOptions.lua:226 (block rolls unlucky in the EHP)", class: c}
    - {var: enemyIsBoss, default: "Pinnacle (list index 3)", ref: "Modules/ConfigOptions.lua:2086 (enemy damage mix and level; block applies to hits only)", class: b}
  unparsed: []
model: null
providers:
  - {kind: keystone, name: "Glancing Blows 39713", slot: tree, role: enables, target: self, text: "Chance to Block Attack Damage is doubled; Chance to Block Spell Damage is doubled; You take 65% of Damage from Blocked Hits", source: "TreeData/3_29/tree.lua:28427-28431; Data/ModCache.lua:14674, 14677, 22989; Modules/ModParser.lua:2370-2372", pob: full}
  - {kind: tattoo, name: "Glancing Blows tattoo (keystone tattoo)", slot: tree, role: enables, target: self, text: "replaces a tree node with the Glancing Blows keystone (Limited to 1 Keystone Tattoo)", source: "Data/TattooPassives.lua:625-640", pob: full}
  - {kind: unique, name: "Emperor's Vigilance", slot: Shield, role: enables, target: self, text: "Glancing Blows on a Steel Kite Shield with (16-22)% Chance to Block Spell Damage, 1000% increased Armour and Energy Shield (current variant), Cannot Block while you have no Energy Shield, damage from Blocked Hits cannot bypass Energy Shield", source: "Data/Uniques/shield.lua:971-985 (header 'Emperor's Vigilance' at 971)", pob: partial}
  - {kind: jewel, name: "Lethal Pride (legacy variant Kiloava, Pre 3.11.0)", slot: jewel, role: enables, target: self, text: "Commanded leadership over (10000-18000) warriors under Kiloava grants the keystone; the keystone has been on the tree since 3.11.0", source: "Data/Uniques/jewel.lua:1904-1910; wiki Glancing Blows rev 1618363", pob: partial, variant: "Pre 3.11.0"}
  - {kind: mod, name: "Crucible weapon tree and Hellscape upside: Glancing Blows", slot: Weapon, role: enables, target: self, text: "weapon tree keystone and Scourge body armour upside", source: "Data/Crucible.lua:1356; Data/ModScourge.lua:108", pob: full}
  - {kind: mod, name: "Chance to Block Attack Damage / Spell Damage (shield, tree, jewels, Dexterity-style scalers)", slot: any, role: scales, target: self, text: "doubled before the cap; useful only up to half of the maximum block chance (EK is already capped)", source: "Modules/CalcDefence.lua:679-733; headless EK/FR/Fireball seed", pob: full}
  - {kind: mod, name: "Energy Shield, Life or Mana gained on Block / when you Block / Block Recently conditions", slot: any, role: abuses, target: self, text: "more blocks mean more triggers; PoB adds them to the EHP unless DisableEHPGainOnBlock is ticked (FR ticks it)", source: "Modules/CalcDefence.lua:2796-2806; Modules/ConfigOptions.lua:227", pob: partial}
  - {kind: mod, name: "Other 'You take #% of Damage from Blocked Hits' sources (The Flawed Refuge 100% elemental, The Oppressor 20%, Thwarting/Guarding/Preserving Gauntlets 10%)", slot: any, role: blocks, target: self, text: "PoB sums them in the same BlockEffect BASE as the keystone's 65 (CalcDefence.lua:786); how the game combines them with Glancing Blows is not stated on the wiki", source: "wiki Blocking rev 1648970; Modules/CalcDefence.lua:786-789", pob: partial}
makes_redundant:
  - {provider: "Block chance above half of the block maximum (rolls beyond the cap)", when: "Glancing Blows allocated", why: "the doubled chance is capped at 78 (EK) / 75 (FR, Fireball seed), so any base block above half the cap adds only overcap", source: "Modules/CalcDefence.lua:679-733; headless EK (overcap grows), FR (44 -> 75)"}
conflicts:
  - {with: "builds that stack block for damage mitigation (EK at the 78 cap, FR with 78 spell block)", effect: "blocked hits now deal 65% of their damage: TotalEHP -69.7% (EK) and -46.7% (FR)", source: "headless EK and FR runs; Modules/CalcDefence.lua:2799"}
  - {with: "'Damage taken from Blocked Hits cannot bypass Energy Shield' style notes and CI/ES pools", effect: "the 65% still reaches the ES pool; only the EHP loss above shows the cost, ES-on-block triggers are not in FR's number", source: "Data/Uniques/shield.lua:971-985; Modules/ConfigOptions.lua:227"}
conditions:
  - {text: "hits only (attacks and spells); damage over time cannot be blocked; a blocked hit still cannot apply on-hit effects (ailments, curses)", source: "wiki Blocking rev 1648970"}
  - {text: "the doubled chance is still limited by the maximum block chances (BlockChanceMax, SpellBlockChanceMax)", source: "Modules/CalcDefence.lua:679-733; headless output (EK 78, FR 75/78, Fireball 75/75)"}
uptime:
  Mapping:       {value: always, config: {enemyIsBoss: "None / map monsters (env.enemyLevel 85 in the headless run)"}, reasoning: "permanent while allocated; in PoB's EHP it costs -69.7% (EK), -46.7% (FR), -5.7% (Fireball seed); the gain (blocked hits cannot apply ailments or curses, doubled on-block triggers) has no PoB output", source: "headless EK/FR/Fireball seed; wiki Blocking rev 1648970"}
  Pinnacle Boss: {value: pob, config: {enemyIsBoss: "Pinnacle (default; env.enemyLevel 84 in the headless run)"}, reasoning: "use PoB's TotalEHP: -69.7% (EK), -46.8% (FR), -5.6% (Fireball seed); a boss hit that is blocked still deals 65% of its damage", source: "headless EK/FR/Fireball seed"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Glancing_Blows (rev 1618363; last version row 3.12.0: 50% -> 65%)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Blocking (rev 1648970, section 'Taking damage from blocked hits')", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcDefence.lua:679-733, 786-789, 2794-2806; Modules/ModParser.lua:2370-2372; Modules/ConfigOptions.lua:226-227, 2086; Data/ModCache.lua:14674, 14677, 22989; Data/TattooPassives.lua:625-640; Data/Uniques/shield.lua:971-985; Data/Uniques/jewel.lua:1904-1910; Data/Crucible.lua:1356; Data/ModScourge.lua:108; TreeData/3_29/tree.lua:28427-28431", kind: pob, patch: "3.29"}
  - {ref: "headless runs EK, FR, Fireball seed (scratchpad b3c/F_run.py, F_show.py; evidence b3c/tree-ascendancy-analyst-F.md)", kind: discovery, patch: "3.29"}
not_verified:
  - "how the game combines Glancing Blows with other 'You take #% of Damage from Blocked Hits' sources (PoB adds the percentages); the wiki lists the items but not the stacking rule"
  - "that PoB's TotalEHP has no ailment- or curse-avoidance term from block: concluded from a grep of BlockChance across Modules (no use near ailment avoidance), not from a test"
  - "the value of the extra on-block triggers and block-scaled effects: not measured (FR ticks DisableEHPGainOnBlock; EK and the Fireball seed have no gain-on-block mod in the output checked)"
  - "[[Block]] is written by another lane on another branch: link resolves at merge; its caps and the wiki block text were read from Blocking rev 1648970 only"
  - "the Fireball seed ManaRegen change under the keystone (a block-scaled mana regeneration mod) was not decomposed"
  - "Emperor's Vigilance variant list and whether it is obtainable in 3.29 were read from PoB's unique data only"
  - "enemy level 85 (None) and 84 (Pinnacle) are env.enemyLevel from the headless run; why None is one level higher was not traced"
open_questions:
  - "Should the generator treat Glancing Blows as a utility pick (ailment avoidance, on-block triggers) and exclude it from pure EHP comparisons, since PoB's EHP can only show a loss?"
```
