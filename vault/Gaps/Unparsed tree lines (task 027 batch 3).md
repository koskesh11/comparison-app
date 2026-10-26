---
type: gap
status: draft
source: "PoB 2.67.2 Data/ModCache.lua (nil mod lists), TreeData/3_29/tree.lua, Data/Skills/act_str.lua:8590-8602; vault Interactions Assassin's Mark, Assassin ascendancy, Power charges, Occultist ascendancy, Elementalist ascendancy, Freeze, Pain Attunement (task 027 batch 3)"
last_confirmed_patch: "3.29.x"
---

# Unparsed passive-tree and gem lines (gap, prose only, no mod pattern)

Each line below is on the passive tree (or a gem) and PoB returns no mod for it. They are worth 0 in every PoB number, so a "no change" result for the node or gem does NOT mean no value. Tree lines never reach the audit's wasted-mod test (engine/audit.lua `equippedItems` walks item slots only), so a gap pattern for them would never fire; the generator and the guide check must read this note instead.

| Line (node) | ModCache | What PoB misses | Source note |
|---|---|---|---|
| Your Mark Transfers to another Enemy when Marked Enemy dies (Focal Point, Deadeye, tree.lua:85417; Mercenary's Lot gloves, Data/Uniques/gloves.lua:294) | 23077 nil | after the marked enemy dies the mark moves on, so a pack needs fewer re-marks; Mark effect lines on the same node do parse | [[Assassin's Mark]] |
| 15% chance to gain a Power Charge on Critical Strike; 30% chance to gain a Power Charge on Non-Critical Strike (Unstable Infusion, Assassin, tree.lua:83531) | 5184, 8131 nil | charge generation; its +1 maximum Power Charge parses (ModCache.lua:230) | [[Assassin ascendancy]] |
| Gain a Power Charge after Spending a total of 200 Mana (Forbidden Power, Occultist, tree.lua:44266) | 16217 nil | charge generation; the other three lines parse | [[Occultist ascendancy]] |
| 20% chance to gain a Power Charge when you Block (Mage Hunter, tree.lua:88692) | 6361 nil | charge generation; block and spell damage lines parse | [[Power charges]] |
| Gain Power Charges instead of Frenzy Charges (Inner Conviction keystone; not in TreeData/3_29/tree.lua, grep 0; also in Data/Uniques/body.lua:1156 and jewel.lua:1925; where the seeds get it was not re-traced) | 16163 nil | frenzy charges are not swapped for power charges; the "3% more Spell Damage per Power Charge" line parses (ModCache.lua:8049) | [[Power charges]] |
| Every 4 seconds, 50% chance to Freeze nearby Non-Frozen Enemies for 0.4 seconds (Frigid Wake, Occultist, tree.lua:44349) | 15467 nil | a periodic freeze: crowd control, no DPS number; PoB has no player-side freeze source | [[Occultist ascendancy]], [[Freeze]] |
| Summoned Golems are Resummoned 4 seconds after being Killed (Liege of the Primordial, Elementalist, tree.lua:50271) | 21966 nil | golem uptime after death; PoB also does not enforce the golem limit, so removing the notable shows 0.0% | [[Elementalist ascendancy]], [[Golem buffs]] |
| Recover 0.5% of Life per Poison affecting Enemies you Kill (Toxic Delivery, Assassin, tree.lua:83345) | 18908 nil | life recovery on poison kills; poison damage lines parse | [[Assassin ascendancy]] |

**Petrified Blood (gem, not a tree node).** The stat `cannot_recover_above_low_life_except_flasks` is "Display Only" in PoB (`Data/Skills/act_str.lua:8600-8602`): the gem's other stats are mapped (life-loss prevention, `ManaCostAsLifeCost`, lines 8590-8599) but this one sets no condition, so PoB does not put the character on Low Life and gives Low Life effects (Pain Attunement) nothing from the gem; the wiki names Petrified Blood as a Low Life source ([[Pain Attunement]], wiki rev 1605415 as quoted there).

**Reading rule.** A node on this list that PoB scores as "no change" or as a small gain still carries the missing effect in the game. Do not remove it for DPS reasons alone; label its value "not measurable in PoB". Counting charges: PoB assumes the maximum number of Power Charges whenever the config tick 'use power charges' is set, and none otherwise, so charge GENERATION lines never matter to PoB in either state ([[Power charges]]).

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and tree lines carry no item slot, so a pattern here would not fire. Item twins of some lines are covered by [[Unparsed item lines (task 027 batch 3)]].
