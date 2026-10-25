---
type: interaction
status: draft
pob_refs: [FireResistMax, ColdResistMax, LightningResistMax, ChaosResistMax, ElementalResistMax, MaxResistCap, ResistFloor, ResistOverCap, FireMaximumHitTaken, FireResistTakenHitMulti, FireEnemyPen]
source: "poewiki Resistance rev 1659347 (fetched 2026-10-26); PoB 2.67.2 CalcDefence.lua / Data.lua / ModParser.lua; TreeData/3_29/tree.lua; wiki cargo (b1-mechanics-researcher.md)"
last_confirmed_patch: "3.29.x"
---

Resistances have a default maximum of 75%, raisable with '+#% to maximum Resistance' sources up to a hard limit of 90%; only resistance up to the maximum mitigates damage, and the part above is an overcap buffer against reduced-resistance effects and exposure. PoB computes it fully (cap, floor -200, overcap) and applies it as damage x (1 - resist) before armour, so max resistance multiplies the elemental maximum hit directly (exact for single-type elemental). Melding of the Flesh caps all elemental resistances at the highest maximum, see [[Max res equalise]]. Related: [[Defences]], [[Armour and physical max hit]].
Impact: EK - Fire/Cold/Lightning max hit is 22,066/22,066/22,884 at 75/75/76 resists with OverCap 26/16/46; raising max res is a direct x1/(1-...) on the elemental max hits only; the physical 7,538 is untouched (physical has no resistance) and chaos is immune (CI). Fireball Elementalist - the goal list has only a physical max hit, so max res does not move it; each extra +5% max res (Purity of Fire L20 +4, Prismatic Skin +2, Ruby flask +5 timed) lifts the fire max hit by about 22% (multiplier 0.28 to 0.23) at pool 4,100, the cheap way to bring the elemental side of the hit table up to the 7,000 physical goal (derived arithmetic, see the block).
Pipeline: [[Receiving damage#Resistances]] - the wiki applies resistance (6.4) after damage taken as and avoidance and before armour, with penetration at the same step, so the max-resistance cap sets the multiplier the whole later chain sees; [[Defences#Resistance caps]] holds the cap, floor and overcap

```interaction
id: max-resistances
mechanic: "Maximum resistance: default 75%, raised by '+#% to maximum Resistance' sources to a hard cap of 90%; resistance above the maximum is only an overcap buffer, and the maximum sets the multiplier on elemental maximum hit"
family: defence
pipeline_step: ["Receiving damage#Resistances", "Defences#Resistance caps"]
pipeline_why: "wiki 6.4: resistance acts as damage x (1 - resist) after damage taken as and avoidance, before armour and damage-taken modifiers (penetration at the same step), so max resistance multiplies the elemental maximum hit directly; the overcap is not an input of the max hit"
target: self
related: [max-res-equalise, armour-phys-max-hit, spell-suppression, block]
pob:
  measured: full
  how: "CalcDefence.lua:593-631: max = Override ResistMax or min(Data.lua:246 MaxResistCap 90, sum BASE '<Type>ResistMax' + 'ElementalResistMax') (596); total = base x INC (601-603); both truncated (m_modf, 612-618); final = max(min(total, max), Data.lua:245 ResistFloor -200) (620); outputs ResistOverCap, ResistOver75, Missing<Type>Resist (625-629); DoT uses ResistOverTime (630). ModParser: 'maximum fire/cold/lightning/chaos resistance' -> <Type>ResistMax (268-274), 'all maximum elemental resistances' -> ElementalResistMax (283), 'all maximum resistances' -> {ElementalResistMax, ChaosResistMax} (284), 'your maximum resistances are N%' -> OVERRIDE (4838-4841), Melding of the Flesh flag ElementalResistMaxIsHighestResistMax (4846, CalcDefence.lua:576-591). Max hit: resMult = 1 - (capped resist - enemy penetration)/100 (CalcDefence.lua:2008, 2078 -> <Type>ResistTakenHitMulti, used in the max-hit solve at 3224/3229): elemental max hit = TotalHitPool / ResistTakenHitMulti / AfterReductionTakenHitMulti (exact for single-type elemental: Worb Fire 47,619 = 6624 / 0.28 / 0.4968). Overcap is shown only as a buffer figure. Enemy penetration comes from the boss preset: Worb and EK both show FireEnemyPen 3 (measured)."
  config:
    - {var: enemyIsBoss, default: "Pinnacle (index 3)", ref: "Modules/ConfigOptions.lua:2086 (sets the enemy penetration and damage presets)", class: b}
    - {var: "enemy<Type>Pen", default: "boss preset (FireEnemyPen 3 in both samples)", ref: "box line not located", class: b}
  unparsed: []
model:
  proposed_kind: max_res_elemental_max_hit
  inputs:
    from_pob: [PhysicalTotalHitPool, FireResistMax, FireEnemyPen, AfterReductionTakenHitMulti]
    from_scenario: [enemyIsBoss]
  params:
    worked_numbers_derived:
      note: "DERIVED arithmetic (not PoB outputs): pool 4,100, no damage-taken mods, enemy penetration 3; elemental max hit = pool / (1 - (res - 3)/100)"
      max_hit_by_res: {res75: 14642, res80: 17826, res85: 22777, res90: 31538}
      gain: "75 to 80: multiplier 0.28 to 0.23 = +21.7% elemental max hit; 80 to 85: +27.8%; 85 to 90: +38.5% (the gain grows because the multiplier is small)"
  formula: "elemental max hit = TotalHitPool / (1 - (min(res, max) - enemy pen)/100) / AfterReductionTakenHitMulti"
  calibration: "exact on Worb: FireMaximumHitTaken 47,619 = 6624 / 0.28 / 0.4968 (b1-mechanics-researcher.md)"
providers:
  - {kind: gem, name: "Purity of Fire / Ice / Lightning", slot: any, role: scales, target: self, text: "aura (reserves 35%); L20 +41% Fire Resistance and '+4% to maximum Fire Resistance' (base_maximum_fire_damage_resistance_%)", source: "Data/Skills/act_str.lua:8902,8958 (Ice: act_dex.lua:12227; Lightning: act_int.lua:14633)", pob: full}
  - {kind: flask, name: "Ruby / Sapphire / Topaz Flask", slot: Flask, role: scales, target: self, text: "+5% to maximum Fire Resistance, +40% to Fire Resistance for 8 s", source: "Data/Bases/flask.lua:255-261", pob: full}
  - {kind: notable, name: "Nomadic Teachings / Prismatic Skin", slot: tree, role: scales, target: self, text: "+2% to all maximum Elemental Resistances", source: "TreeData/3_29/tree.lua:27313,38823", pob: full}
  - {kind: notable, name: "Sanctuary / Soul of Steel / Anointed Flesh / Crystal Skin / Prismatic Carapace / Prismatic Dance", slot: tree, role: scales, target: self, text: "+1% to all maximum Elemental Resistances each (Sanctuary also +4% attack and spell block while holding a Shield; Master of the Maelstrom +1% needs a recent kill of a Cursed enemy)", source: "TreeData/3_29/tree.lua:30786,35326,38020,65585,88506,88567,89191", pob: full}
  - {kind: notable, name: "Wizardry / Winter Prowler / Molten One's Mark / Born of Chaos", slot: tree, role: scales, target: self, text: "single-type maximum resistance +2 (Wizardry lightning, Winter Prowler cold, Molten One's Mark fire) and chaos +3 (Born of Chaos)", source: "TreeData/3_29/tree.lua:88918,88848,88780,88984", pob: full}
  - {kind: mod, name: "crafted / essence suffix MaximumAllResist1_ / 2 and MaximumColdResist1-3 etc.", slot: item, role: scales, target: self, text: "+1% / +2% to all maximum Resistances; single-type maximum resistance suffixes (spawn tags not read)", source: "wiki cargo mods: id MaximumAllResist1_ (domain 1, generation_type 2), stat additional_maximum_all_resistances_% (global)", pob: full}
  - {kind: mod, name: "Maven-influenced all-resistances", slot: item, role: scales, target: self, text: "+(19-22)% to all Elemental Resistances, +1% to all maximum Elemental Resistances", source: "wiki cargo AllResistancesInfluenceMaven____", pob: full}
  - {kind: mod, name: "Eldritch implicits (Searing Exarch / Eater of Worlds, incl. Unique / Pinnacle-presence variants)", slot: body armour / helmet / boots / gloves, role: scales, target: self, text: "+1% to +3% to maximum <Type> Resistance (presence variants +2 to +5)", source: "wiki cargo MaximumColdResistanceEldritchImplicit1-6, ...PinnaclePresence1-6", pob: full}
  - {kind: keystone, name: "Veteran's Awareness", slot: tree, role: scales, target: self, text: "+10% to all Elemental Resistances and maximum Elemental Resistances while affected by a Non-Vaal Guard Skill; 20% more Damage taken if a Non-Vaal Guard Buff was lost Recently", source: "TreeData/3_29/tree.lua:85667", pob: config, requires: ["Non-Vaal Guard Skill"]}
  - {kind: mod, name: "Resistance Shrine / Lesser Resistance Shrine", slot: map, role: scales, target: self, text: "Resistance Shrine '+10% to all maximum Resistances'; Lesser +2%", source: "https://www.poewiki.net/wiki/Resistance rev 1659347", pob: config}
  - {kind: unique, name: "several uniques (names not mapped)", slot: amulet / shield / other, role: scales, target: self, text: "cargo mod ids IncreasedMaximumResistsUnique__1 (+(1-5)% to all maximum Resistances), IncreasedMaximumResistsUniqueAmulet87 (+(1-3)%), IncreasedMaximumResistsUniqueShieldStrInt1 (+4%)", source: "wiki cargo mods", pob: full}
  - {kind: ascendancy, name: "Melding of the Flesh (Reliquarian)", slot: tree, role: blocks, target: self, text: "-5% to all maximum Elemental Resistances and caps all elemental resistances at the highest maximum (see max-res-equalise)", source: "TreeData/3_29/tree.lua:22301; Modules/CalcDefence.lua:576-591", pob: full}
makes_redundant: []
conflicts:
  - {with: "Melding of the Flesh", effect: "-5% to all maximum Elemental Resistances and all elemental resistances capped by the highest maximum; see max-res-equalise", source: "TreeData/3_29/tree.lua:22301; Modules/CalcDefence.lua:576-591"}
  - {with: "the 90 hard cap", effect: "a stack past 90 is wasted but is a buffer against max-res reduction (wiki Resistance example: can ignore up to 5% max res reduction)", source: "Modules/CalcDefence.lua:596 (MaxResistCap 90); https://www.poewiki.net/wiki/Resistance rev 1659347"}
  - {with: "resistance above the maximum", effect: "only a buffer against 'reduced resistance' effects and exposure (wiki Overcapped resistances), not extra mitigation; chaos and elemental maximum are separate keys (ChaosResistMax) and 'all maximum resistances' lines feed both", source: "https://www.poewiki.net/wiki/Resistance rev 1659347; Modules/ModParser.lua:284"}
conditions:
  - {text: "Purity needs its mana reservation and an aura slot; flasks are timed (8 s); variants 'while poisoned', 'with no endurance charges', 'while affected by Herald of Ash' exist for uniques (cargo ids additional_maximum_all_resistances_%_while_poisoned, ..._with_no_endurance_charges, maximum_fire_damage_resistance_%_while_affected_by_herald_of_ash)", source: "Data/Skills/act_str.lua:8902; Data/Bases/flask.lua:255-261; wiki cargo"}
uptime:
  Mapping:
    value: always
    config: {}
    reasoning: "gear, tree and aura are always on; for the flask use PoB's flask tooltip uptime (see [[Flask uptime]]); map mods can lower max res on the map (MapPlayerMaxResists1/2MapWorlds listed as sources, values not fetched)"
    source: "b1-mechanics-researcher.md; https://www.poewiki.net/wiki/Resistance rev 1659347"
  Pinnacle Boss:
    value: always
    config: {enemyIsBoss: "Pinnacle (default index 3)"}
    reasoning: "same sources, but boss penetration (FireEnemyPen 3 in both samples) lowers each resistance by 3 in max hit: effective multiplier 1 - (max - 3)/100"
    source: "b1-mechanics-researcher.md (measured); Modules/CalcDefence.lua:2008,2078"
seeds: [EK, Worb]
sources:
  - {ref: "https://www.poewiki.net/wiki/Resistance (rev 1659347, 2026-06-24); version rows 3.6.0 (max res cap 90 added), 3.16.0 (floor -200), 3.17.0 (reduced-resistance cap 100%), 3.26.0 (resistance mods no longer roll on weapons)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcDefence.lua:576-631,2008,2078,3224-3229; Modules/Data.lua:245,246; Modules/ModParser.lua:268-284,4838-4846 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b1-mechanics-researcher.md", kind: discovery, patch: "3.29"}
not_verified:
  - "spawn slots and tags of the max-res suffixes (templated wiki query not run)"
  - "which uniques carry max res and their names"
  - "map-mod values (MapPlayerMaxResists1/2MapWorlds sign and size)"
  - "whether exposure or a curse on the player that lowers resistance is modelled in max hit"
  - "the config line of the enemy penetration boxes"
  - "shrine and incursion availability"
  - "the Fireball +22% per +5% max res claim is derived arithmetic at pool 4,100 and penetration 3, not a measurement"
  - "no max-resistance ascendancy node found for Assassin or Elementalist in the 3.29 tree scan (hits only Chieftain Valako, Reliquarian Melding of the Flesh)"
open_questions:
  - "Is a physical-only max hit goal enough, or should the generator also keep the elemental max hits (which max resistance moves) near the goal?"
```
