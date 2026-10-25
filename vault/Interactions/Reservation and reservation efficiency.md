---
type: interaction
status: draft
pob_refs: [ManaReserved, ManaReservedPercent, ManaUnreserved, LifeReserved, LifeUnreserved, ManaReservationEfficiency, ReservationEfficiency, SupportManaMultiplier, BloodMagicReserved, manaReservationPercent, manaReservationFlat]
source: "PoB 2.67.2 CalcPerform.lua:547-583, 1969-2092, ModStore.lua:317-343, CalcDefence.lua:232, 2352, 2655; Data/Skills/sup_int.lua:2279-2343; poewiki Reservation rev 1697378; headless Worb/EK probes (task 027 batch 4)"
last_confirmed_patch: "3.29.x"
---

An aura, herald or stance holds back part of your mana (or life) as long as it is active. The size is: base % (or flat) x support multipliers (Enlighten), then divided by (100% + total reservation efficiency). PoB computes the amounts exactly, but keeps every skill active even when the sum is over 100%, so the fit check is ours: Rule [[Reservation must fit the pool]]. What is reserved is gone from the pool that Mind over Matter, Hierophant area scaling and skill costs draw on.
Percent reservations do not change with gem level (Worb probe: Herald of Ice L20 -> L1 gave the same 22.32%); flat ones (Clarity, mines) do.

Pipeline: [[Receiving damage#Mana before life]] - reserved mana leaves the unreserved pool that absorbs damage before life (PoB feeds ManaUnreserved to the mind-over-matter pool), so reservation is paid in effective HP; the aura buffs it buys act in [[Damage calculation#Increased and reduced]] and the defence layers

```interaction
id: reservation-efficiency
mechanic: "Skills reserve a % (or flat amount) of Mana or Life while active: reserved = base x support multiplier (Enlighten) / (100% + total Reservation Efficiency); PoB rounds the percent to 0.01% per skill and the pool total up to a whole number"
family: resource
pipeline_step: ["Receiving damage#Mana before life", "Receiving damage#Life"]
pipeline_why: "reserved mana is removed from ManaUnreserved, the pool Mind over Matter and mana-before-life draw from; reserved life is removed from LifeUnreserved; the reservation itself is not damage, it shrinks the pools the hit-order steps use"
target: self
related: [aura-effect, life-reservation, skill-cost-from-es, arcane-surge]
pob:
  measured: partial
  how: "Amounts are full: CalcPerform.lua:1969-2090 per active HasReservation skill: mult = floor(More(SupportManaMultiplier),4) (1982); base percent x100 x mult truncated (2029, m_modf); + INC 'ManaReserved/Reserved' truncated, + MORE ManaReserved truncated, + MORE Reserved truncated (2031-2034); then round(x / (1 + efficiency/100) / efficiencyMore) / 100 (2035) with efficiency = max(sum INC ManaReservationEfficiency + ReservationEfficiency, -100) (2009) -> nearest 0.01% per skill. Flat path same at 2016-2023. Pool total (CalcPerform.lua:562): reserved = flatSum + ceil(max x percentSum / 100) -> one round-UP for the whole pool, output ManaReserved is capped at Mana (564) but ManaUnreserved = max - reserved can go NEGATIVE (566). Blood Magic / Prism Guardian move the mana part to life (1994-2002). What PoB does NOT do: disable skills that do not fit (no skillFlags.disable on over-reservation; only ManaReservationPercentForced skills with 0 mana are disabled, 2084-2087); sustain or recovery are not looked at. Evidence (Worb 3.29, saved gems incl. Aspect of the Brine King): Mana 1359, ManaReserved 1359, ManaUnreserved -158, no skill disabled. Golden test (Brine King left out): 4 skills x 22.32% = 89.28% -> ceil(1359 x 0.8928) = 1214 reserved, ManaUnreserved 145. Per-skill skillData.ManaReservedBase is rounded up per skill (304 each = 1216) but the pool uses the summed percent (1214), so per-skill sums can differ by 1-3 from the pool. Probe 1: Herald of Ice gem L20 -> L1: ManaReservedPercent 22.32 -> 22.32, ManaUnreserved 145 -> 145 (no change, base % is level-independent). Probe 2: add Enlighten L3 (manaMultiplier -8, sup_int.lua:2297) to the same group: 25 x 0.92 = 2300 / 1.12 = 2053.6 -> round 2054 -> 20.54% per skill, 4 x 20.54 = 82.16% -> ManaReserved 1117, ManaUnreserved 242 (+97 mana); TotalEHP unchanged 76836.9 because Worb has no Mind over Matter. Efficiency 12% in Worb comes from Mana Mastery tree node 53188 (Tree:53188 source from modDB Tabulate)."
  config: []
  unparsed: []
model: null
providers:
  - {kind: mastery, name: "Mana Mastery 53188 (effect 64875)", slot: tree, role: scales, target: self, text: "12% increased Mana Reservation Efficiency of Skills", source: "TreeData/3_29/tree.lua node 53188 (mastery effects, effect 64875); Worb modDB source Tree:53188", pob: full, requires: ["a notable in the same cluster, see Rule Mastery needs a notable in its cluster"]}
  - {kind: notable, name: "Sovereignty 32932", slot: tree, role: scales, target: self, text: "12% increased Mana Reservation Efficiency of Skills; 10% increased effect of Non-Curse Auras from your Skills", source: "tree.lua node 32932 (EK build modDB source Tree:32932)", pob: full}
  - {kind: notable, name: "Reservation Efficiency small nodes 28859, 21974, 25831", slot: tree, role: scales, target: self, text: "8% increased Mana Reservation Efficiency of Skills each", source: "tree.lua nodes 28859 / 21974 / 25831 (EK build modDB sources)", pob: full}
  - {kind: support, name: "Enlighten (Support)", slot: any, role: scales, target: self, text: "no stats; from level 2 a cost & reservation multiplier on supported gems: L2 -4, L3 -8, L4 -12 ... L10 -36 (drop-only gem; the wiki lists experience only up to level 3, PoB data goes to level 10)", source: "PoB Data/Skills/sup_int.lua:2279-2306; CalcActiveSkill.lua:523-524 (manaMultiplier -> SupportManaMultiplier MORE); wiki Enlighten Support rev 1681794 ('cost and reservation multiplier less than 100%'; 'multiplicative with ... Increased Reservation Efficiency')", pob: full}
  - {kind: support, name: "Awakened Enlighten", slot: any, role: scales, target: self, text: "same, to level 20: -56% cost & reservation multiplier (L20), level requirement up to 100", source: "PoB Data/Skills/sup_int.lua:2307-2344", pob: full}
  - {kind: unique, name: "Prism Guardian (shield)", slot: shield, role: scales, target: self, text: "Socketed Gems Cost and Reserve Life instead of Mana; Socketed Gems have 30% increased Reservation Efficiency", source: "PoB Data/Uniques/shield.lua:1009-1010; ModParser.lua:3244 (ExtraSupport SupportBloodMagicUniquePrismGuardian, other.lua:589-604)", pob: full}
  - {kind: jewel, name: "Conqueror's Efficiency (Crimson jewel)", slot: jewel, role: scales, target: self, text: "4% increased Mana Reservation Efficiency of Skills (and 3% reduced Mana Cost)", source: "PoB Data/Uniques/jewel.lua:1691-1696", pob: full}
  - {kind: ascendancy, name: "Unwavering Faith (Guardian 64768)", slot: tree, role: scales, target: self, text: "50% increased Reservation Efficiency of Skills", source: "TreeData/3_29/tree.lua:14815-14822 (node 64768); parse checked headless: ReservationEfficiency INC 50", pob: full}
  - {kind: notable, name: "Charisma 6799", slot: tree, role: scales, target: self, text: "16% increased Mana Reservation Efficiency of Skills; 6% increased effect of Non-Curse Auras from your Skills", source: "TreeData/3_29/tree.lua node 6799 (stats line 66123-66124)", pob: full}
  - {kind: notable, name: "Cluster small passive 'Reservation Efficiency'", slot: cluster jewel, role: scales, target: self, text: "Added Small Passive Skills grant: 6% increased Mana Reservation Efficiency of Skills", source: "PoB Data/ClusterJewels.lua:152-157", pob: full}
  - {kind: unique, name: "Saqawal's Nest (body armour)", slot: body armour, role: scales, target: self, text: "(12-20)% increased Mana Reservation Efficiency of Skills", source: "PoB Data/Uniques/body.lua:1320", pob: full}
  - {kind: unique, name: "The Arkhon's Tools (belt)", slot: belt, role: scales, target: self, text: "(10-20)% increased Mana Reservation Efficiency of Skills", source: "PoB Data/Uniques/belt.lua:1042", pob: full}
  - {kind: unique, name: "Alpha's Howl (helmet)", slot: helmet, role: scales, target: self, text: "16% increased Mana Reservation Efficiency of Skills", source: "PoB Data/Uniques/helmet.lua:209", pob: full}
  - {kind: foulborn, name: "Alpha's Howl, Foulborn", slot: helmet, role: scales, target: self, text: "32% increased Life Reservation Efficiency of Skills (Life only: useful only with Blood Magic / Prism Guardian)", source: "PoB Data/ModFoulborn.lua:9 (MutatedUniqueHelmetDex5LifeReservationEfficiency), ModFoulbornMap.jsonc:339 (replaces ManaReservationEfficiencyUniqueHelmetDex5_)", pob: full, variant: "replaces '16% increased Mana Reservation Efficiency of Skills'"}
  - {kind: ascendancy, name: "Bringer of Ruin (Elementalist 258)", slot: tree, role: scales, target: self, text: "66% increased Mana Reservation Efficiency of Herald Skills; 66% increased Effect of Herald Buffs on you", source: "TreeData/3_29/tree.lua node 258", pob: full}
makes_redundant:
  - {provider: "Enlighten on a pool that already fits", when: "ManaUnreserved >= 0 with all aura slots filled and no Mind over Matter / area-per-unreserved-mana payoff", why: "a gem slot spent on spare mana buys nothing PoB counts (Worb probe: Enlighten L3 gave +97 unreserved mana and +0 TotalEHP); keep it when the goal is a 4th/5th reservation skill or a Mind over Matter pool", source: "headless Worb probe 2 (this note); CalcDefence.lua:232"}
conflicts:
  - {with: "Mind over Matter pool (id mind-over-matter)", effect: "reserved mana shrinks the pool that absorbs damage: pool = ManaUnreserved (max with 0, floor), so every aura slot costs MoM effective HP", source: "CalcDefence.lua:232, 2352 (max(ManaUnreserved,0)), 2655"}
  - {with: "Hierophant Sanctuary of Thought 29026", effect: "'1% increased Area of Effect per 50 Unreserved Maximum Mana, up to 100%' falls with every reservation", source: "TreeData/3_29/tree.lua:15928"}
  - {with: "Blood Magic 57279 / Sanguimancy 8982 / Prism Guardian / The Covenant", effect: "mana reservation moves to Life (LifeUnreserved), costs paid in life; with life already the EHP pool this is a trade, not a gain", source: "CalcPerform.lua:1994-2002; ModParser.lua:2278, 3244"}
  - {with: "Whispers of Infinity (id skill-cost-from-es)", effect: "costs are paid from ES but reservation still comes out of the mana pool", source: "Interactions/Skill cost from ES.md (CalcOffence.lua:1763-1790)"}
  - {with: "Memory Vault, Essence Worm, Vivinsect, The Sundered Will family (reduced efficiency)", effect: "negative efficiency multiplies reservation: 20% reduced = x1.25 (sum is floored at -100 in PoB)", source: "PoB Data/Uniques/helmet.lua:1324, ring.lua:539, 1556, 1722; CalcPerform.lua:2009"}
conditions:
  - {text: "Sum of reserved percentages (+ flat) must be <= the pool, else the skill does not work in game while PoB still shows it; Rule: Reservation must fit the pool (ManaUnreserved >= 0, LifeUnreserved >= 0)", source: "vault Rules/Reservation must fit the pool.md; headless Worb baseline ManaUnreserved -158 with no skill disabled"}
  - {text: "Reserved amount is a divisor of efficiency, not a sum of cost modifiers: Inspiration and mana cost modifiers do NOT change reservation; Enlighten multiplies with efficiency", source: "wiki Reservation rev 1697378 ('Modifiers to cost ... will not have any effect on reservation'); CalcPerform.lua:2009-2035"}
  - {text: "Flat reservation (Clarity, Vitality, Precision, mines) grows with gem level; percent reservation does not (probe: Herald of Ice L1 = L20)", source: "wiki Reservation rev 1697378 ('flat amount, which grows with gem level ... percentage ... does not change with gem level'); Data/Skills/act_int.lua:2688-2689 (Clarity manaReservationFlat 34, 48 ...)"}
  - {text: "ModStore PerStat 'ManaReservedPercent' (Supreme Ego, Farewell to Flesh) is per skill: floor(that skill's ManaReservedBase / Mana x 100), capped at 100, and uses the per-skill rounded-up base", source: "Classes/ModStore.lua:317-343"}
  - {text: "Low Mana / Low Life condition is set when unreserved/max <= 50% (LowPoolThreshold) after reservation", source: "CalcPerform.lua:570-572"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "Reservation is permanent while the skill is on; PoB counts it with no config. Reservation persists through death since 3.25.0.", source: "CalcPerform.lua:1979; wiki Reservation rev 1697378 version history 3.25.0"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "Same; PoB counts every active skill with no config", source: "CalcPerform.lua:1979"}
seeds: [EK, Worb]
sources:
  - {ref: "PoB Modules/CalcPerform.lua:562-566, 1969-2092; Classes/ModStore.lua:317-343; Modules/CalcOffence.lua:1195-1210; Modules/CalcDefence.lua:232, 2352, 2655; Data/SkillStatMap.lua:2132-2149", kind: pob, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Reservation (rev 1697378): 'Resource Reserved = Base Reserve % / (100% + Total Reserve Efficiency %)'; 3.14.0: 'Percentage reservations ... up to two decimal places ... the total amount of resources reserved must still be a whole number'; 3.16.0: 'Reservation Efficiency works by dividing the cost'", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Enlighten_Support (rev 1681794)", kind: wiki, patch: "3.29"}
  - {ref: "headless probes on Worb.xml and CoC EK Assa.xml via engine/pobhost.py (A2_probe.py, A2_src.py in the task 027 batch 4 scratchpad)", kind: pob, patch: "3.29"}
not_verified:
  - "In-game rounding direction of the pool total (PoB rounds up with m_ceil, CalcPerform.lua:562; wiki says only 'whole number')"
  - "Enlighten level values: PoB data is used (L3 = -8, L4 = -12); the wiki progression table is not rendered by the API and was not compared"
  - "Mana Mastery option list (the other mastery effects of node 53188) and Conqueror's Efficiency obtainability: not read or checked"
  - "Sovereignty / Mana Mastery / Charisma node ids come from tree.lua only; in-game tooltips not compared"
  - "Alpha's Howl identity of ModFoulbornMap key 'UniqueHelmetDex5' is inferred from the matching 16%/32% (helmet.lua:209 vs ModFoulborn.lua:9)"
  - "Whispers of Infinity mana-pool reduction size: not read here (see Interactions/Skill cost from ES.md)"
  - "Division by zero: PoB clamps efficiency at -100 (CalcPerform.lua:2009) so 1 + eff/100 = 0; the resulting value was not tested"
  - "Whether the Fireball Elementalist seed (task 035) puts a herald in the aura slot with Bringer of Ruin: not checked"
  - "Fireball Elementalist seed reservation fit (Herald of Ash / Zealotry / Anger plus Bringer of Ruin): not probed, that build is not in the headless set"
open_questions:
  - "Should the generator treat ManaUnreserved >= 0 as a hard stop when Mind over Matter is the planned max-hit route (needs a minimum unreserved pool, not just >= 0)?"
```
