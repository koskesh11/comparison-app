---
type: interaction
status: draft
pob_refs: [conditionEnemyFrozen, conditionEnemyChilled, conditionEnemyIgnited, conditionEnemyShocked, conditionEnemyScorched, inflictBrittle, inflictSap, EnemyFreezeChance, EnemyShockChance, EnemyIgniteChance]
source: "poewiki The Taming rev 1649810, Ailment rev 1673310, Version 3.25.0 (fetched 2026-10-24); PoB 2.67.2 ModParser.lua / ConfigOptions.lua / CalcPerform.lua; PoB Data/Uniques/ring.lua, TreeData/3_29/tree.lua"
last_confirmed_patch: "3.29.x"
---

Some items scale with the number of different elemental ailment TYPES on the enemy: The Taming gives (30-40)% increased Elemental Damage with Hits and Ailments for each type (max 7: Ignite, Chill, Freeze, Shock, Scorch, Brittle, Sap). Extra stacks of the same type do not count; bleed and poison do not count. PoB adds the mod once per enemy condition (Frozen, Chilled, Ignited, Shocked, Scorched, Brittle, Sapped), but each condition is a config tick (or a guaranteed source), never derived from the build. So the Taming only shows value for the types the user ticks, and the real uptime of each type (esp. freeze on bosses, and scorch/brittle/sap which need dedicated sources) is not modelled. Related: [[Freeze]], [[Chill]], [[Shock]], [[Enemy ailment threshold]]. Providers beyond the seed set: see tasks/reports/027-research.md.

```interaction
id: elemental-ailment-count
mechanic: "Damage scales per DIFFERENT elemental ailment type on the enemy (Ignite, Chill, Freeze, Shock, Scorch, Brittle, Sap = max 7; bleed and poison do not count; extra stacks of one type do not add): The Taming (30-40)% increased Elemental Damage with Hits and Ailments per type"
family: ailment
target: enemy
related: [freeze, chill, shock, enemy-ailment-threshold, damage-type-can-ailment]
pob:
  measured: config
  how: "The Taming line parses into 7 ElementalDamage INC mods (Hit|Ailment keywords), one per enemy condition Frozen, Chilled, Ignited, Shocked, Scorched, Brittle, Sapped (ModParser.lua:3627-3635); the count is the number of those enemy conditions that are true; conditions come only from config checkboxes or guaranteed sources (CalcPerform.lua:1401-1431, 3565-3606), PoB does NOT infer them from % chance; the chance line '10% chance to Freeze, Shock and Ignite' raises chances only (ModParser.lua:766)"
  config:
    - {var: conditionEnemyIgnited, default: false, ref: "Modules/ConfigOptions.lua:1878", class: b}
    - {var: conditionEnemyScorched, default: false, ref: "Modules/ConfigOptions.lua:1884 (visible only with inflictScorch)", class: b}
    - {var: conditionEnemyChilled, default: false, ref: "Modules/ConfigOptions.lua:1899", class: b}
    - {var: conditionEnemyFrozen, default: false, ref: "Modules/ConfigOptions.lua:1924", class: b}
    - {var: "enemy Brittle checkbox (var name not read)", default: false, ref: "Modules/ConfigOptions.lua:1931 (ifFlag inflictBrittle)", class: b}
    - {var: conditionEnemyShocked, default: false, ref: "Modules/ConfigOptions.lua:1943", class: b}
    - {var: "enemy Sapped checkbox (var name not read)", default: false, ref: "Modules/ConfigOptions.lua:1958 (ifFlag inflictSap)", class: b}
  unparsed: []
model: null
providers:
  - {kind: unique, name: "The Taming", slot: Ring, role: abuses, target: enemy, text: "(30-40)% increased Elemental Damage with Hits and Ailments for each type of Elemental Ailment on Enemy; 10% chance to Freeze, Shock and Ignite; (20-30)% all elemental resistances; implicit +(8-10)% all res; no Foulborn version exists; vendor recipe Berek's Grip + Pass + Respite", source: "Data/Uniques/ring.lua:1257-1281 (Current variant 3, 1268,1272,1277-1278); wiki The Taming rev 1649810; Modules/ModParser.lua:3627-3635", pob: config, variant: "Current (variant 3); Pre 3.0.0 and Pre 3.25.0 variants exist"}
  - {kind: unique, name: "Yoke of Suffering", slot: Amulet, role: abuses, target: enemy, text: "Enemies take (5-10)% increased Damage for each type of Ailment you have inflicted on them (PoB counts 9 types: 7 elemental + Bleeding + Poisoned); Your Elemental Damage can Shock; drawback 30% reduced Duration of Ailments on Enemies", source: "Data/Uniques/amulet.lua:1370-1374; Modules/ModParser.lua:3604-3613", pob: config, variant: "variant 2"}
  - {kind: gem, name: "Elemental Hit", slot: any, role: abuses, target: enemy, text: "+10% final damage per elemental ailment on the target, counting Chilled and Frozen (attack gem)", source: "Data/Skills/act_dex.lua:6137-6138,6284-6285", pob: partial}
  - {kind: support, name: "Coursing Current Support", slot: any, role: sustains, target: enemy, text: "3.29.0: chill makes shock and shock makes chill, so one source yields two types (both count)", source: "Data/Skills/sup_int.lua:1318; wiki Version 3.29.0", pob: partial}
  - {kind: unique, name: "Rashkaldor's Patience", slot: Amulet, role: sustains, target: enemy, text: "Always Freeze, Shock and Ignite (3 types); drawback 20% reduced duration of Elemental Ailments on Enemies", source: "Data/Uniques/amulet.lua:939,943", pob: full}
  - {kind: unique, name: "Story of the Vaal / Fate of the Vaal", slot: Sword, role: sustains, target: enemy, text: "Hits with this Weapon always Ignite, Freeze and Shock (weapon-local)", source: "Data/Uniques/sword.lua:569,586", pob: full}
  - {kind: unique, name: "Doedre's Tongue / The Admiral", slot: various, role: sustains, target: enemy, text: "(20-25)% / (10-25)% chance to Freeze, Shock and Ignite", source: "Data/Uniques/amulet.lua:389; body.lua:1436", pob: full}
  - {kind: unique, name: "Expedition's End / Call of the Void / Galesight", slot: various, role: sustains, target: enemy, text: "chill sources (Nearby Enemies are Chilled; All Damage with Hits can Chill) and Brittle (Galesight (25-50)% chance, but Galesight cannot freeze or chill)", source: "Data/Uniques/body.lua:1262; ring.lua:1633; helmet.lua:653-654", pob: full}
  - {kind: unique, name: "Watcher's Eye (Hatred / Wrath / Anger)", slot: Jewel, role: sustains, target: enemy, text: "Always inflict Brittle while affected by Hatred; Always Sap (Wrath); Always Scorch (Anger)", source: "Data/Uniques/Special/WatchersEye.lua:99; Modules/ModParser.lua:3838", pob: partial}
  - {kind: unique, name: "Leadership's Price", slot: Amulet, role: sustains, target: enemy, text: "all three Conflux (secondary ailments) but Cannot Ignite, Chill, Freeze or Shock: a package whose point is Scorch, Brittle, Sap only", source: "Data/Uniques/amulet.lua:816-817", pob: full}
  - {kind: ascendancy, name: "Oath of Spring / Oath of Summer (Raider)", slot: tree, role: scales, target: enemy, text: "up to 50 Shocks per enemy; an additional Scorch per enemy, ignite becomes scorch. More stacks of one type do NOT raise the count", source: "TreeData/3_29/tree.lua:84989,84778; wiki The Taming rev 1649810", pob: partial}
  - {kind: keystone, name: "Secrets of Suffering", slot: tree, role: sustains, target: enemy, text: "Critical Strikes inflict Scorch, Brittle and Sapped (3 types) but Cannot Ignite, Chill, Freeze or Shock", source: "TreeData/3_29/tree.lua:85638 (node 57280)", pob: full}
  - {kind: notable, name: "Fury of Nature (Raider)", slot: tree, role: scales, target: enemy, text: "Non-Damaging Elemental Ailments you inflict spread to nearby enemies within 2 metres / have 100% more Effect", source: "TreeData/3_29/tree.lua:90084 (node 18054)", pob: full}
  - {kind: keystone, name: "Voracious Flame", slot: tree, role: scales, target: enemy, text: "additional Ignite per enemy but Cannot deal non-Fire Damage; not a new TYPE", source: "TreeData/3_29/tree.lua:47294 (node 63903)", pob: partial}
makes_redundant:
  - {provider: "Taming chance line (10% chance to Freeze, Shock and Ignite)", when: "Rashkaldor's Patience or a weapon with always-F/S/I is worn", why: "chance lines on the Taming add nothing when the ailments are already guaranteed", source: "Data/Uniques/amulet.lua:939; sword.lua:569"}
conflicts:
  - {with: "Galesight / Leadership's Price / Secrets of Suffering", effect: "block freeze and chill (and ignite/shock), cutting the count to the secondary types", source: "Data/Uniques/helmet.lua:654; amulet.lua:817; TreeData/3_29/tree.lua:85638"}
  - {with: "wiki vs PoB", effect: "none on the list or values (7 types, 30-40%); the gap is only that PoB counts a type only if its config says so", source: "wiki The Taming rev 1649810; Modules/ModParser.lua:3627-3635"}
conditions:
  - {text: "counts once per TYPE of Ignite, Chill, Freeze, Shock, Scorch, Brittle, Sap; additional stacks (Emberwake, Oath of Summer, Oath of Spring) do not add; bleed and poison are non-elemental and do not count; there is no limit on the number of different ailments a target can have", source: "https://www.poewiki.net/wiki/The_Taming rev 1649810; wiki Ailment rev 1673310"}
  - {text: "current text since 3.25.0 (from '20% increased Damage with Hits and Ailments per Freeze, Shock or Ignite on Enemy'); no 'Elemental Damage with Attack Skills' line any more", source: "wiki Version 3.25.0; Data/Uniques/ring.lua:1277-1281"}
uptime:
  Mapping:
    value: partial
    config: {conditionEnemyChilled: "per derived source", conditionEnemyIgnited: "per derived source", conditionEnemyShocked: "per derived source", conditionEnemyFrozen: "derived (see freeze)", conditionEnemyScorched: "only with a dedicated source", Brittle checkbox: "only with a dedicated source", Sapped checkbox: "only with a dedicated source"}
    reasoning: "chill + ignite + shock are usually up; freeze when assumed; scorch/brittle/sap need dedicated sources. Tick each type separately by its derived source, never all 7"
    source: "build-strategist table (tasks/reports/027-research.md); Modules/ConfigOptions.lua:1878-1965"
  Pinnacle Boss:
    value: low
    config: {conditionEnemyChilled: "true if the build deals cold hits", conditionEnemyFrozen: "model: only if duration >= 0.3 s (see freeze)", conditionEnemyShocked: "model (Own shock effect)", conditionEnemyIgnited: "needs fire damage or chance"}
    reasoning: "chill (hit-based) holds, ignite needs fire or chance, shock partial, freeze rarely on a boss, the others need dedicated sources; The Taming value = sum of the ticked types, do not assume 4+"
    source: "build-strategist table (tasks/reports/027-research.md)"
seeds: [Worb]
sources:
  - {ref: "https://www.poewiki.net/wiki/The_Taming (rev 1649810, 2026-05-31)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Ailment (rev 1673310)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/ModParser.lua:3627-3635; Modules/ConfigOptions.lua:1878-1965; Modules/CalcPerform.lua:1401-1431,3565-3606 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "wiki Version 3.25.0 (The Taming rework), 3.28.0 (level requirement fix)", kind: patch_notes, patch: "3.29"}
not_verified:
  - "that a Frozen boss with a minimum action speed counts for The Taming: the wiki sentence about 'conditional for freeze' is generic, not Taming-specific"
  - "whether Coursing Current type conversions (3.29) create Sap, Scorch or Brittle (they create chill and shock, which count)"
  - "how many of the 7 types a Worb-like build can actually keep up; Worb's shock source is NOT identified; the Worb sample ticks chilled + frozen + shocked"
  - "that PoB models multiple shocks (Oath of Spring); only parse text read"
open_questions: []
```
