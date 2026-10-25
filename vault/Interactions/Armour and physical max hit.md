---
type: interaction
status: draft
pob_refs: [PhysicalMaximumHitTaken, PhysicalDamageReduction, PhysicalEffectiveAppliedArmour, PhysicalTotalHitPool, BasePhysicalDamageReduction, PhysicalAfterReductionTakenHitMulti, DamageReductionMax, enemyPhysicalDamage, TotalEHP]
source: "poewiki Armour rev 1625574 (fetched 2026-10-26); PoB 2.67.2 CalcDefence.lua / Data.lua / ConfigOptions.lua; headless probes on 3.29\\Ninja Builds\\CoC EK Assa.xml and 3.29\\Worb.xml (b1-mechanics-researcher.md, M1 in b1-pob-coverage-auditor.md)"
last_confirmed_patch: "3.29.x"
---

Armour cuts a physical hit by A / (A + 5 x D) with D the hit after damage-taken-as and resistance, and never prevents more than A/5 of a hit far above it; it does nothing against damage over time. PoB shows the displayed reduction and TotalEHP for the configured enemy hit, but PhysicalMaximumHitTaken solves the hit size in reverse (a quadratic, CalcDefence.lua:3235-3261), so it is armour-correct for the hit that exactly kills you; it ignores block, evasion, avoidance and dodge ("if every hit lands"). Related: [[Defences]], [[Endurance charges]], [[Damage over time multiplier]].
Impact: EK - armour is irrelevant: 658 armour (Spec:ArmourInc 23) is 1.7% reduction at a 7,538 hit; the EK physical max hit 7,538 (already at or above the 7,000 goal) comes from ES 5,189 + BasePhysicalDamageReduction 16 + 23% less physical taken (PhysicalTakenHitMult 0.77), so adding armour buys about 0. Fireball Elementalist - reaching 7,000 by armour alone at a 4,100 pool (Life 3,000 + ES 1,100) needs about 24.8k armour (41% reduction at the hit), 12.6k with 15% flat reduction; armour is the expensive lever, flat reduction, damage-taken multipliers and pool size are cheaper per point. From 5,142 the next +1,858 of max hit via armour costs about 18.2k extra armour at pool 4,100 (6,534 to 24,756), or about +1,700 pool at Worb-level armour.
Derived table (NOT a PoB output; formula below, pure physical hit, pool = TotalHitPool, no damage-taken mods, no overwhelm; treat as plus or minus 10%): armour needed for physical max hit 7,000 at pool 4,100 is 24,756 / 20,056 / 16,042 / 12,573 at flat reduction 0 / 5 / 10 / 15%; the full table is in the block under model.params.
Pipeline: [[Receiving damage#Armour and damage reduction]] - armour acts after damage-taken-as and resistance but before damage-taken modifiers and spell suppression, so the hit size D it sees is already shifted and resisted; [[Defences#Armour formula]] and [[Defences#Physical damage reduction cap]] hold the formula and the 90 cap

```interaction
id: armour-phys-max-hit
mechanic: "Armour reduces a physical hit by A / (A + 5 x D) (cap 90, never vs damage over time); PoB's physical maximum hit solves the hit size D in reverse from the pools, so armour's value for a max-hit goal is a diminishing-returns curve in pool size, flat reduction and armour"
family: defence
pipeline_step: ["Receiving damage#Armour and damage reduction", "Defences#Armour formula", "Defences#Physical damage reduction cap"]
pipeline_why: "armour acts after damage-taken-as and resistance, before damage-taken modifiers and suppression (wiki Armour: after damage shifts and resistances, before modifiers to damage taken and spell suppression); it is per hit size, so the max hit has to solve D itself"
target: self
related: [endurance-charges, damage-over-time-multiplier, spell-suppression, block, max-resistances]
pob:
  measured: partial
  how: "formula calcs.armourReductionF CalcDefence.lua:67-72; DISPLAYED PhysicalDamageReduction / TakenHit and TotalEHP use the configured hit D (CalcDefence.lua:2030, armourReduction(effectiveAppliedArmour, damage*resMult); ConfigOptions.lua:2368 enemyPhysicalDamage overrides the default 1.5 x the enemy base damage); PhysicalMaximumHitTaken does NOT use the configured hit: CalcDefence.lua:3235-3261 solves the whole chain for RAW with a quadratic a = 5(1-flatDR+ow)*taken*(res*conv)^2, b = ((ow-flatDR)*A*taken - 5*(pool - flat*taken))*res*conv, c = -A*(pool - flat*taken), then 'tack on some caps' (3259-3261: noDRMaxHit floor, maxDRMaxHit with DamageReductionMax 90); when damage is shifted (conv != 100%) up to Data.lua:295 maxHitSmoothingPasses = 8 passes of calcs.takenHitFromDamage (3273-3302, shown as '(approximate)' in the breakdown 3350). Block, evasion, avoidance and dodge are not in this chain (3208-3266 has no reference)."
  config:
    - {var: enemyPhysicalDamage, default: "placeholder round(monsterDamageTable[level] x 1.5)", ref: "Modules/ConfigOptions.lua:2368 (moves displayed reduction and TotalEHP only, not the max hit)", class: b}
    - {var: enemyIsBoss, default: "Pinnacle (index 3)", ref: "Modules/ConfigOptions.lua:2086 (boss presets 2086-2115)", class: b}
  unparsed: []
model:
  proposed_kind: armour_phys_max_hit
  inputs:
    from_pob: [PhysicalTotalHitPool, PhysicalEffectiveAppliedArmour, BasePhysicalDamageReduction, PhysicalAfterReductionTakenHitMulti, DamageReductionMax]
    from_scenario: [enemyPhysicalDamage, enemyIsBoss]
  params:
    armour_needed_derived:
      note: "DERIVED from the wiki formulas, not PoB outputs; pure physical hit, pool = TotalHitPool, no damage-taken mods, no overwhelm; flat DR f = additional physical damage reduction; required armour A = X*5R/(R-X) with X = R(1-f) - P, checked by re-running the quadratic; treat as plus or minus 10% (PoB differs 3.3% on Worb, 7% on EK)"
      pool_4100_life3000_es1100:
        target_7000: {f0: 24756, f5: 20056, f10: 16042, f15: 12573, dr_at_hit_f0_percent: 41.4}
        target_5142: {f0: 6534, f5: 4631, f10: 2941, f15: 1429}
      pool_3433_life2333_es1100_ES_of_last_run_unknown:
        target_5142: {f0: 12799}
        target_7000: {f0: 36366, f5: 29763, f10: 24279, f15: 19651}
      diminishing_returns_pool_4100_f0: {armour_0: 4100, armour_5000: 4931, armour_10000: 5572, armour_15000: 6112, armour_20000: 6588, armour_30000: 7416}
      marginal_note: "+1,000 armour at 24.8k adds about 83 of max hit"
      cheaper_levers: "pool 5,819 reaches 7,000 with Worb-level armour 4,715 and f=5%; a damage-taken multiplier m divides the pool: with 0.8 the pool-equivalent of 4,100 is 5,125 and the armour needed for 7,000 drops to 12,805 (m=0.7: 6,829); in Worb the measured physical taken multiplier is 0.4899, which is why a 6,624 pool shows 16,310"
    measured_armour_sweep_via_config_custom_mod:
      note: "M1 in b1-pob-coverage-auditor.md; armour changes only the physical key and TotalEHP, DPS untouched; both builds ran with enemyIsBoss Pinnacle"
      Worb: {base_4715: {dr: 37, phys_max: 16310, total_ehp: 76837}, plus_1000: {dr: 42, phys_max: 16577, total_ehp: 78989}, plus_5000: {dr: 58, phys_max: 17582, total_ehp: 87439}}
      EK: {base_658: {dr: 23, phys_max: 7538, total_ehp: 145259}, plus_1000: {dr: 34, phys_max: 7912, total_ehp: 156210}, plus_5000: {dr: 61, phys_max: 9196, total_ehp: 190637}}
  formula: "wiki: DR = A/(A+5D); required armour A = DR x 5 x D / (1 - DR); net damage D_net = 5 D^2 / (A + 5 D); PoB max hit = positive root of the quadratic at CalcDefence.lua:3251-3256 (RAW such that the chain just empties the pool), caps at 3259-3261"
  calibration: "Worb: formula (conv 0.9) 16,853 vs PoB PhysicalMaximumHitTaken 16,310 (3.3% difference; conversion smoothing 3273-3300 lowers it); same run FireMaximumHitTaken 47,619 = 6624 / FireResistTakenHitMulti 0.28 / FireAfterReductionTakenHitMulti 0.4968 (exact). EK: formula 7,036 vs PoB 7,538 (7% difference, not traced; candidates BasePhysicalDamageReductionWhenHit at 3231, smoothing)"
providers:
  - {kind: gem, name: "Determination", slot: any, role: scales, target: self, text: "aura (reserves manaReservationPercent 50 at L20); L20 determination_aura_armour_+%_final 49 (more armour) and base_physical_damage_reduction_rating 1,026", source: "Data/Skills/act_str.lua:2640,2696 (stats 2665-2672)", pob: full}
  - {kind: flask, name: "Granite Flask", slot: Flask, role: scales, target: self, text: "base buff '+1500 to Armour' (6 s, 30 charges used of 60)", source: "Data/Bases/flask.lua:279-285", pob: full}
  - {kind: gem, name: "Molten Shell", slot: any, role: scales, target: self, text: "grants armour and absorbs 75% of hits up to 10% of armour (limit 5,000), shares the Guard cooldown; L20 armour value not read", source: "Data/Skills/act_str.lua:7589,7635-7637,7668", pob: partial}
  - {kind: mastery, name: "Armour Mastery", slot: tree, role: scales, target: self, text: "+1 Armour per 2 Strength; 20% chance to Defend with 200% of Armour; +1% to all maximum Elemental Resistances if Equipped Helmet, Body Armour, Gloves, and Boots all have Armour", source: "TreeData/3_29/tree.lua:24557", pob: full}
  - {kind: mastery, name: "Armour and Energy Shield Mastery", slot: tree, role: scales, target: self, text: "2% chance to Defend with 150% of Armour per 5% missing Energy Shield (a hybrid option; the 'chance to defend' family raises ArmourDefense, not counted in the pure formula)", source: "TreeData/3_29/tree.lua:25191,25311", pob: partial}
  - {kind: mod, name: "N% additional Physical Damage Reduction (flat reduction f)", slot: body armour, role: scales, target: self, text: "Worb Empyrean Guardian: '5% additional Physical Damage Reduction', also '10% of Physical Damage from Hits taken as Cold Damage' and 'Gain an Endurance Charge every 15 seconds'; enters the formula as flatDR", source: "CalcDefence.lua:1538 min(max(0, sum), DamageReductionMax); Worb.xml item id 3", pob: full}
  - {kind: mod, name: "Endurance charges", slot: any, role: scales, target: self, text: "flat physical damage reduction per charge (not re-verified here)", source: "vault/Interactions/Endurance charges.md", pob: full}
  - {kind: mod, name: "Sacred Chainmail body base (Worb)", slot: body armour, role: scales, target: self, text: "Armour 3111 base roll x 126% increased Armour and ES (quality 20)", source: "Worb.xml item id 3", pob: full}
makes_redundant: []
conflicts:
  - {with: "damage over time", effect: "armour never mitigates damage over time (wiki Armour); PoB TakenDotMult has no armour term", source: "https://www.poewiki.net/wiki/Armour rev 1625574; Modules/CalcDefence.lua:1971"}
  - {with: "damage taken as another type", effect: "the shifted portion gets the final type's mitigation: a physical-taken-as-cold body (Worb) gives that portion cold resistance instead of armour; taken as chaos under Chaos Inoculation is immune (EK, ChaosAfterReductionTakenHitMulti 0)", source: "Receiving damage#Damage taken as; b1-mechanics-researcher.md"}
  - {with: "armour on a non-physical type", effect: "needs a separate mod (Transcendence, Doryani's Prototype, Juggernaut)", source: "https://www.poewiki.net/wiki/Armour rev 1625574"}
  - {with: "diminishing returns and the 90 cap", effect: "past reduction 90 nothing counts; Overwhelm subtracts after the cap", source: "Defences#Physical damage reduction cap"}
conditions:
  - {text: "Determination needs its reservation (3.29 percent reservation); Granite Flask is a timed buff (6 s of every use, charge-limited); only armour on gear or tree counts, ES-only bases give none", source: "Data/Skills/act_str.lua:2640; Data/Bases/flask.lua:279-285"}
  - {text: "the displayed reduction and TotalEHP follow the configured enemy hit (enemyPhysicalDamage, boss preset); the physical max hit does not", source: "Modules/ConfigOptions.lua:2086-2115,2368; Modules/CalcDefence.lua:2030,3235-3261"}
uptime:
  Mapping:
    value: always
    config: {}
    reasoning: "gear, tree and the Determination aura are always on; the flask: use PoB's flask tooltip uptime (see [[Flask uptime]]), not re-modelled"
    source: "b1-mechanics-researcher.md; vault Flask uptime note"
  Pinnacle Boss:
    value: always
    config: {enemyIsBoss: "Pinnacle (default index 3)"}
    reasoning: "same uptime, but the boss hits are larger so the armour reduction is worse (D grows, DR = A/(A+5D)); only the displayed DR and TotalEHP follow the boss hit config, the physical max hit does not"
    source: "Modules/ConfigOptions.lua:2086-2115,2368"
seeds: [EK, Worb]
sources:
  - {ref: "https://www.poewiki.net/wiki/Armour (rev 1625574, 2026-03-03)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcDefence.lua:67-72,2030,3208-3350; Modules/Data.lua:243,295; Modules/ConfigOptions.lua:2086,2368 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b1-mechanics-researcher.md; b1-pob-coverage-auditor.md (M1)", kind: discovery, patch: "3.29"}
not_verified:
  - "EK physical max hit differs 7% from the researcher's re-implementation of the formula (cause not traced)"
  - "the 90-cap clause inside CalcDefence.lua:3259-3261 was not exercised"
  - "Molten Shell L20 armour value; the order of the Determination flat 1,026 (base armour) against its 'more' part"
  - "the last run's ES (only Life 2,333 given), so the pool 3,433 rows are conditional"
  - "wiki Armour version rows 3.25.0 / 3.16.0 were not read in full (the Defences note says 3.16.0: formula improved)"
  - "the derived armour-needed table is a hand re-implementation, not a PoB output"
open_questions:
  - "Is the 7,000 physical goal meant as PoB's PhysicalMaximumHitTaken (which assumes every hit lands: no block, evasion, avoidance or dodge) or as the displayed reduction against the configured boss hit? The two use different hit sizes."
```
