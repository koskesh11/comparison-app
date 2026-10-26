---
type: interaction
status: draft
pob_refs: [ChaosCanFreeze, ChaosCanShock, ChaosCanIgnite, LightningCanFreeze, LightningCannotShock, ColdCannotFreeze, ColdCannotChill, FireCannotIgnite, FireCanShock]
source: "poewiki Ailment rev 1673310, The Three Dragons rev 1675049, Foulborn unique item rev 1702126 (fetched 2026-10-24); wiki cargo mod_stats; PoB 2.67.2 ModParser.lua / CalcOffence.lua; PoB Data/Uniques, ModFoulbornMap.jsonc, TreeData/3_29/tree.lua; vault Gaps/Foulborn The Three Dragons"
last_confirmed_patch: "3.29.x"
---

Each ailment has a default damage type (freeze and chill: cold, shock: lightning, ignite: fire). Some items, gems and ascendancies change that: "Your Chaos Damage can Freeze", "but not Freeze or Chill". These are global flags (stat ids without a local_ prefix, also on weapons). The ailment magnitude counts only the damage of the types that can inflict it. This is the core of the Foulborn The Three Dragons seed (FR): the mutation lines let chaos hits freeze, shock and ignite, but PoB gives no DPS for freeze and only config-gated DPS for shock. Related: [[Freeze]], [[Shock]], [[Chill]], [[Foulborn The Three Dragons]], [[Own shock effect]]. Providers beyond the seed set: see tasks/reports/027-research.md.

Pipeline: [[Damage calculation#Ailments from hits]] - which damage types may inflict an ailment decides the damage that sizes it (ailment chance and magnitude use only those types), which is evaluated in the ailments-from-hits step

```interaction
id: damage-type-can-ailment
mechanic: "A damage type other than the ailment's own can be allowed (or forbidden) to inflict it; the ailment's chance and magnitude then use only the damage of the types that can inflict it; a Foulborn mutation REPLACES one original line, so a 'but not' drawback disappears only if its own line is the one mutated"
family: ailment
pipeline_step: ["Damage calculation#Ailments from hits"]
pipeline_why: "which damage types may inflict an ailment decides the damage that sizes it (ailment chance and magnitude use only those types), which is evaluated in the ailments-from-hits step"
target: enemy
related: [freeze, shock, chill, enemy-ailment-threshold, elemental-ailment-count]
pob:
  measured: partial
  how: "generic parse 'your (%w+) damage can (%w+)' -> flag <Type>Can<Ailment> (ModParser.lua:3638-3639), explicit lines for the three originals (3670-3672), 'all damage can freeze' 3645, 'chaos damage can ignite, chill and shock' 3674; consumed by calcAverageSourceDamage (CalcOffence.lua:4315-4329): a type counts for an ailment if it is the ailment's own type (and not <Type>Cannot<Ailment>) or has <Type>Can<Ailment>; the flags feed chance, duration and effect, but PoB adds no DPS unless conditionEnemyShocked + conditionShockEffect (or conditionEnemyFrozen for vs-frozen mods) are set"
  config:
    - {var: conditionEnemyShocked, default: false, ref: "Modules/ConfigOptions.lua:1943", class: b}
    - {var: conditionShockEffect, default: 0, ref: "Modules/ConfigOptions.lua:1947", class: c}
    - {var: conditionEnemyFrozen, default: false, ref: "Modules/ConfigOptions.lua:1924", class: b}
  unparsed: []
model: null
providers:
  # seed: Foulborn The Three Dragons (all three mutation lines, each replaces one original)
  - {kind: foulborn, name: "Foulborn The Three Dragons", slot: Helmet, role: enables, target: enemy, text: "Your Chaos Damage can Freeze (global flag ChaosCanFreeze); still needs a freeze chance or a crit", variant: "REPLACES 'Your Lightning Damage can Freeze but not Shock' (MutatedUniqueHelmetDexInt4ChaosDamageCanFreeze); lightning can shock again", source: "Data/ModFoulbornMap.jsonc:346 -> Data/ModFoulborn.lua:123; original Data/Uniques/helmet.lua:1671; wiki Modifier stat chaos_damage_can_freeze", pob: partial}
  - {kind: foulborn, name: "Foulborn The Three Dragons", slot: Helmet, role: enables, target: enemy, text: "Your Chaos Damage can Shock (ChaosCanShock)", variant: "REPLACES 'Your Fire Damage can Shock but not Ignite' (MutatedUniqueHelmetDexInt4ChaosDamageCanShock); fire can ignite again (FireCannotIgnite goes with the line)", source: "Data/ModFoulbornMap.jsonc:348 -> Data/ModFoulborn.lua:121; original Data/Uniques/helmet.lua:1669; wiki Modifier stat chaos_damage_can_shock", pob: partial}
  - {kind: foulborn, name: "Foulborn The Three Dragons", slot: Helmet, role: enables, target: enemy, text: "Your Chaos Damage can Ignite (ChaosCanIgnite); PoB values it when the skill can deal fire (CalcOffence.lua:5131)", variant: "REPLACES 'Your Cold Damage can Ignite but not Freeze or Chill' (MutatedUniqueHelmetDexInt4ChaosDamageCanIgnite); NOT mutated in the user's v4, so the cold line stays and cold still cannot freeze or chill", source: "Data/ModFoulbornMap.jsonc:347 -> Data/ModFoulborn.lua:122; original Data/Uniques/helmet.lua:1670; wiki Modifier stat base_chaos_damage_can_ignite", pob: partial}
  - {kind: unique, name: "The Three Dragons (plain)", slot: Helmet, role: enables, target: enemy, text: "Your Fire Damage can Shock but not Ignite; Your Cold Damage can Ignite but not Freeze or Chill; Your Lightning Damage can Freeze but not Shock; the item does not convert stats; with Elemental Conflux: fire shocks and chills but not ignites, cold ignites and shocks but not freezes or chills, lightning chills and ignites but not shocks", source: "Data/Uniques/helmet.lua:1669-1671; Modules/ModParser.lua:3670-3672; wiki The Three Dragons rev 1675049", pob: full}
  # alternatives (at most 12)
  - {kind: gem, name: "Hexblast", slot: any, role: enables, target: enemy, text: "all_damage_can_ignite_freeze_shock: chaos spell whose damage can ignite, freeze and shock", source: "Data/Skills/act_int.lua:9084; Data/SkillStatMap.lua:1257-1265", pob: full}
  - {kind: ascendancy, name: "Shaper of Storms (Elementalist)", slot: tree, role: enables, target: enemy, text: "Hits always Shock / All Damage can Shock", source: "TreeData/3_29/tree.lua:50157 (node 27038); Modules/ModParser.lua:2828-2833", pob: full}
  - {kind: ascendancy, name: "Shaper of Flames (Elementalist)", slot: tree, role: enables, target: enemy, text: "Hits always Ignite / All Damage can Ignite", source: "TreeData/3_29/tree.lua:50135 (node 53123); Modules/ModParser.lua:2810", pob: full}
  - {kind: ascendancy, name: "Shaper of Winter (Elementalist)", slot: tree, role: enables, target: enemy, text: "All Damage with Hits can Chill (can chill, not can freeze)", source: "TreeData/3_29/tree.lua:50179 (node 40810); Modules/ModParser.lua:2816-2821", pob: full}
  - {kind: unique, name: "Expedition's End", slot: Body Armour, role: enables, target: enemy, text: "All Damage can Freeze (scope of the stat id NOT VERIFIED)", source: "Data/Uniques/body.lua:1261; Modules/ModParser.lua:3645", pob: full}
  - {kind: unique, name: "Voltaxic Rift", slot: Bow, role: enables, target: enemy, text: "Your Chaos Damage can Shock (stat chaos_damage_can_shock on a WEAPON, no local_ prefix = still global)", source: "Data/Uniques/bow.lua:517; wiki Modifier ChaosDamageCanShockUniqueBow10 rev 1633740", pob: full}
  - {kind: unique, name: "Echoforge / Starforge / Voidforge", slot: Sword, role: enables, target: enemy, text: "Chaos can Shock (Echoforge); Physical can Shock (Starforge, variant 3); Elemental can Shock (Voidforge, variant 3)", source: "Data/Uniques/sword.lua:825,1034,1070", pob: full}
  - {kind: unique, name: "Zerphi's Heart", slot: Amulet, role: enables, target: enemy, text: "Chaos Damage can Ignite, Chill and Shock", source: "Data/Uniques/amulet.lua:1025; Modules/ModParser.lua:3674", pob: full, variant: "variant 2"}
  - {kind: unique, name: "Soul Taker / Replica Soul Taker", slot: Axe, role: enables, target: enemy, text: "Physical can Chill (Soul Taker, stat physical_damage_can_chill rev 1631083); Physical can Freeze (Replica)", source: "Data/Uniques/axe.lua:160,173", pob: full}
  - {kind: unique, name: "Call of the Void", slot: Ring, role: enables, target: enemy, text: "All Damage with Hits can Chill", source: "Data/Uniques/ring.lua:1633", pob: full}
  - {kind: unique, name: "Wing of the Wyvern", slot: Bow, role: enables, target: enemy, text: "Your Chaos Damage can Freeze (scope NOT VERIFIED)", source: "Data/Uniques/bow.lua:611", pob: full}
  - {kind: unique, name: "Hrimburn / Stormfire / Replica Volkuur's Guidance", slot: various, role: enables, target: enemy, text: "can Ignite: cold (Hrimburn gloves), lightning (Stormfire ring), chaos (Replica Volkuur's Guidance gloves); Cinderswallow Urn flask: physical can ignite (variant 8)", source: "Data/Uniques/gloves.lua:264,883; ring.lua:1242; flask.lua:222", pob: full}
  # blocks
  - {kind: support, name: "Elemental Focus Support", slot: any, role: blocks, target: enemy, text: "supported skill cannot inflict ailments; removes the point of every can-freeze/can-shock line on that skill", source: "Data/SkillStatMap.lua:1059-1066", pob: full}
  - {kind: keystone, name: "Secrets of Suffering", slot: tree, role: blocks, target: enemy, text: "Cannot Ignite, Chill, Freeze or Shock (verified headless: ShockChanceOnCrit and FreezeChanceOnCrit 100 -> 0 on FR v4, DPS identical)", source: "TreeData/3_29/tree.lua:85638 (node 57280); vault Gaps/Foulborn The Three Dragons", pob: full}
makes_redundant: []
conflicts:
  - {with: "Foulborn The Three Dragons cold line", effect: "kept unless mutated: cold cannot freeze or chill; with both chaos freeze and chaos shock mutations nothing can chill", source: "Data/Uniques/helmet.lua:1670; vault Gaps/Foulborn The Three Dragons"}
  - {with: "Elemental Focus (support) / Secrets of Suffering / Avatar of Fire", effect: "remove the ailment the can-line enables", source: "Data/SkillStatMap.lua:1059-1066; TreeData/3_29/tree.lua:85638,28412"}
  - {with: "wiki vs PoB on 'but not' wording", effect: "wiki: a hit can inflict ailments of any type it dealt; PoB: explicit Cannot flags per type (ColdCannotFreeze etc.); both agree for the Three Dragons lines", source: "https://www.poewiki.net/wiki/The_Three_Dragons rev 1675049; Modules/ModParser.lua:3670-3672"}
conditions:
  - {text: "the enemy must take at least 1 point of damage of a type that can inflict the ailment; a chance-to-ignite/shock/freeze mod stays per ailment, so Foulborn chaos freeze still needs a freeze chance or a crit (crits 100%)", source: "https://www.poewiki.net/wiki/Ailment rev 1673310; wiki The Three Dragons rev 1675049"}
  - {text: "the tree has NO 'All Damage can Freeze' node; freeze for non-cold damage comes from items (or Hexblast); no tattoo gives a can-freeze/shock line", source: "TreeData/3_29/tree.lua (grep can Freeze); Data/TattooPassives.lua"}
uptime:
  Mapping:
    value: always
    config: {}
    reasoning: "a permission, always on while the item is worn; the value shows only through the ailment it enables (see freeze, shock)"
    source: "build-strategist table (tasks/reports/027-research.md); Modules/CalcOffence.lua:4315-4329"
  Pinnacle Boss:
    value: always
    config: {}
    reasoning: "same permission; adds nothing if freeze or shock is not assumed (PoB gives no DPS for it, vault Gap note still correct)"
    source: "vault Gaps/Foulborn The Three Dragons; Models/Own shock effect"
seeds: [FR]
sources:
  - {ref: "https://www.poewiki.net/wiki/The_Three_Dragons (rev 1675049, 2026-07-19)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Foulborn_unique_item (rev 1702126, 2026-08-27)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Ailment (rev 1673310)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/ModParser.lua:3638-3645,3670-3674; Modules/CalcOffence.lua:4315-4329; Data/ModFoulbornMap.jsonc:346-348 (PoB 2.67.2; PoB reads the .jsonc, not the .lua)", kind: pob, patch: "3.29"}
not_verified:
  - "that chaos damage actually freezes or shocks in game with Forbidden Rite (vault Gap lists it as user-to-verify); no wiki text for the exact chaos-freeze duration (the formula says cold and/or other contributing damage types count)"
  - "first Foulborn introduction version (The Three Dragons itself has no mechanic change since 1.1.1; Foulborn existed before 3.27.0c)"
  - "scope (global vs local) of Wing of the Wyvern chaos-freeze and Expedition's End all-damage-freeze (wiki Modifier page names garbled)"
  - "tattoos with 'can freeze' wording: none found in Data/TattooPassives.lua"
open_questions:
  - "FR v4 keeps the cold line ('Your Cold Damage can Ignite but not Freeze or Chill'): confirm which of the three lines the user mutated (evidence says fire and lightning were replaced)"
```
