---
type: interaction
status: draft
pob_refs: [PhysicalMaximumHitTaken, FireMaximumHitTaken, ColdMaximumHitTaken, PhysicalDamageFromHitsTakenAsFire, PhysicalDamageFromHitsTakenAsCold, PhysicalDamageTakenAsFire, PhysicalDamageTaken, TotalEHP]
source: "poewiki Damage taken as rev 1618416, Receiving damage rev 1702582 (fetched 2026-10-26); PoB 2.67.2 ModParser.lua / CalcDefence.lua / Data/ModEldritch.lua / Data/ModExplicit.lua / Data/Uniques; headless probes on 3.29\\Ninja Builds\\CoC EK Assa.xml and 3.29\\Worb.xml (b1b-mechanics-researcher.md section B, b1b-pob-coverage-auditor.md taken-as)"
last_confirmed_patch: "3.29.x"
---

"N% of Physical Damage from Hits taken as Fire (Cold, Lightning) Damage" shifts part of an incoming physical hit to another type before armour and resistance. The shifted part skips armour and meets the new type's resistance; only the unshifted part gets armour. At 75% resistance and no armour a 10% shift lifts the physical max hit about x1.08. PoB parses and counts it for hits and damage over time with no config tick, but the wording matters: "taken as Cold" without the word "Damage" parses as PhysicalDamageTaken, a wrong mod. Related: [[Armour and physical max hit]], [[Flat physical damage reduction]], [[Conversion and gain as extra]] (offensive side, a different mechanic).

Pipeline: [[Receiving damage#Damage taken as]] - the shift happens first (defender-side, all calculations at once, a hit is shifted at most once), before resistance, armour and every damage-taken modifier; this is not offensive conversion

```interaction
id: physical-taken-as-elemental
mechanic: "N% of Physical Damage [from Hits] taken as <element> Damage: the shifted share gets the element's resistance instead of armour (only the final type applies); the unshifted physical share still gets armour; the max hit of the PHYSICAL key rises, the raw elemental max hit keys do not"
family: defence
pipeline_step: ["Receiving damage#Damage taken as", "Receiving damage#Armour and damage reduction", "Receiving damage#Resistances"]
pipeline_why: "wiki Damage taken as: the shifted portion does not retain its original type and is not mitigated twice, so it skips armour; the shift is the first defender step, before resistance and armour"
target: self
related: [armour-phys-max-hit, flat-physical-damage-reduction, max-resistances, penetration]
pob:
  measured: full
  how: "no dedicated pattern: form '^([%+%-]?[%d%.]+)%%? of' BASE (ModParser.lua:81) + name 'physical damage from hits taken' (:298) or 'physical damage taken' (:297) + suffix 'as physical/lightning/cold/fire/chaos damage' (suffixTypes ModParser.lua:5986-5991; short form only for 'as fire' :5990); result names PhysicalDamageFromHitsTakenAsFire / PhysicalDamageTakenAsFire. Use: damageShiftTable[src][dst] = DoT form + hit form + Elemental variants, same-type share = max(100 - sum, 0) (CalcDefence.lua:1846-1867); hit path CalcDefence.lua:84-100; DoT path uses only the plain form (1855-1860), so 'from Hits' lines do not shift DoT; max hit: convertPercent = damageShiftTable[type][convertedType] (3212) into the quadratic and the smoothing passes (3273-3302, Data.lua:295). Plain and 'from Hits' wording gave identical hit max hits in the probe. PoB leaves out: the wiki side effect that the shifted cold part can chill or freeze you and lightning can shock you; a share above 100% in total is not rescaled (max(100-sum,0), no cap on the destination, 1866)."
  config: []
  unparsed: []
model: null
providers:
  - {kind: mod, name: "Eater of Worlds body implicit (fire / cold / lightning / chaos)", slot: body armour, role: applies, target: self, text: "10% to 12% of Physical Damage from Hits taken as Fire (Cold, Lightning, Chaos) Damage (T6/T5 10, T4/T3 11, T2/T1 12), weight 500 on body armour; the Worb body uses the 10% cold roll", source: "Data/ModEldritch.lua:1805-1810,1823-1828,1841-1846,1859-1864; Worb.xml item 3", pob: full}
  - {kind: mod, name: "Influenced body prefix (Elder fire, Shaper cold and lightning, Warlord, Crusader, Redeemer)", slot: body armour, role: applies, target: self, text: "(8-12)% of Physical Damage from Hits taken as <type> Damage (lvl 68) / (13-15)% (lvl 82-84); Maven-elevated 16-18% versions have weight 0", source: "Data/ModExplicit.lua:1945-1950,3001-3031,3803-3853", pob: full}
  - {kind: mod, name: "Influenced helmet prefix", slot: helmet, role: applies, target: self, text: "(4-6)% / (7-10)% of Physical Damage from Hits taken as <type> Damage (lvl 68 / 83)", source: "Data/ModExplicit.lua:2927-2965", pob: full}
  - {kind: mod, name: "Hunter's body prefix (chaos)", slot: body armour, role: applies, target: self, text: "(8-12)% / (13-15)% of Physical Damage from Hits taken as Chaos Damage; poor fit while chaos resistance is 0", source: "Data/ModExplicit.lua:3047-3048", pob: full}
  - {kind: unique, name: "Taste of Hate", slot: flask, variant: "variant 4", role: applies, target: self, text: "(10-15)% of Physical Damage from Hits taken as Cold Damage during Effect (variants 1-3: 30% / 20%)", source: "Data/Uniques/flask.lua:419-422", pob: config}
  - {kind: unique, name: "Cloak of Flame", slot: body armour, variant: "variant 2", role: applies, target: self, text: "40% of Physical Damage taken as Fire Damage (hit and DoT; variant 1 before 3.19.0: 20% of Physical Damage from Hits); +(50-75)% to Fire Resistance", source: "Data/Uniques/body.lua:524-537", pob: full}
  - {kind: unique, name: "Lightning Coil", slot: body armour, variant: "variant 3", role: applies, target: self, text: "50% of Physical Damage from Hits taken as Lightning Damage; same item has -60% to Lightning Resistance and an armour/evasion base", source: "Data/Uniques/body.lua:887-899", pob: full}
  - {kind: unique, name: "The Formless Inferno", slot: helmet, role: applies, target: self, text: "8% of Physical Damage from Hits taken as Fire Damage", source: "Data/Uniques/helmet.lua:100", pob: full}
  - {kind: unique, name: "Dawnbreaker", slot: shield, role: applies, target: self, text: "(10-20)% of Physical Damage taken as Fire Damage (hit and DoT)", source: "Data/Uniques/shield.lua:87", pob: full}
makes_redundant: []
conflicts:
  - {with: "armour on the shifted part", effect: "the shifted portion is not reduced by armour (wiki example: physical shifted to fire is not mitigated by armour); only the unshifted share is", source: "poewiki Damage taken as rev 1618416; Modules/CalcDefence.lua:84-100"}
  - {with: "chaos target without chaos resistance", effect: "taken as Chaos is worthless while chaos resistance is 0 (seed goal minimum 0); under Chaos Inoculation it is immune (EK, ChaosAfterReductionTakenHitMulti 0)", source: "b1b-mechanics-researcher.md section B; vault Armour and physical max hit"}
  - {with: "'from Hits' wording on damage over time", effect: "'of Physical Damage from Hits taken as' shifts hits only; plain 'of Physical Damage taken as' also shifts DoT; PoB's DoT table skips the FromHits mods", source: "Modules/CalcDefence.lua:1855-1860; poewiki Damage taken as rev 1618416"}
  - {with: "shifted element ailments on you", effect: "wiki: the shifted cold part can chill or freeze you, the lightning part can shock you; shifted fire never ignites; PoB does not model this side effect", source: "poewiki Damage taken as rev 1618416"}
  - {with: "legacy sources since 3.25.0", effect: "wiki: many Incursion, Delve, shield corruption, Fire Warband helmet and all Watcher's Eye taken-as modifiers can no longer roll; PoB still lists them with spawn weight 0; left out of the providers", source: "poewiki Damage taken as rev 1618416 (3.25.0); Data/ModDelve.lua:40; Data/ModCorrupted.lua:296; Data/ModExplicit.lua:1609; Data/ModVeiled.lua:179,182"}
conditions:
  - {text: "write 'taken as Cold Damage': 'taken as Cold' without the word Damage parses as PhysicalDamageTaken BASE with leftover text 'as Cold' (wrong mod); only 'as fire' has a short form", source: "Modules/ModParser.lua:5986-5991 (live parse in b1b-pob-coverage-auditor.md)"}
  - {text: "Taste of Hate is a timed flask buff, charge-limited: use PoB's flask uptime (see Flask uptime), not re-modelled", source: "Data/Uniques/flask.lua:419-422; vault Flask uptime"}
  - {text: "the physical max hit key rises; FireMaximumHitTaken (a raw fire hit) is untouched, so a taken-as mod helps the 7,000 physical goal but not a fire max-hit goal", source: "b1b-pob-coverage-auditor.md measurements; Modules/CalcDefence.lua:3307"}
  - {text: "a body takes one Eater and one Exarch implicit: the Eater taken-as roll competes with the Eater aura-effect roll (see Determination and Grace), not with the Exarch charge source", source: "Data/ModEldritch.lua:3785-3790,3497; Worb.xml item 3"}
uptime:
  Mapping:
    value: always
    config: {}
    reasoning: "gear lines are always on; the flask line follows PoB's flask tooltip uptime"
    source: "Modules/CalcDefence.lua:84-100; vault Flask uptime"
  Pinnacle Boss:
    value: always
    config: {}
    reasoning: "same uptime; the value of the shift depends on the element's resistance after boss penetration (the 75% falls by the penetration), so the gain is smaller than at the map's resistance"
    source: "vault Receiving damage#Resistances; Modules/ConfigOptions.lua enemy penetration inputs"
seeds: [Worb, EK, Fireball]
sources:
  - {ref: "https://www.poewiki.net/wiki/Damage_taken_as (rev 1618416; version table 3.6.0 to 3.26.0)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/ModParser.lua:81,297-298,5986-5991; Modules/CalcDefence.lua:84-100,1846-1867,3212,3273-3302; Modules/Data.lua:295 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b1b-mechanics-researcher.md (B); b1b-pob-coverage-auditor.md (taken-as, measurements)", kind: discovery, patch: "3.29"}
not_verified:
  - "measured effect of 20% Physical from Hits taken as Fire or Cold (auditor probe, one change, rolled back): Worb PhysicalMaximumHitTaken 16,310 to 19,199 / 19,198, TotalEHP 76,837 to 82,657 / 82,669; EK 7,538 to 9,096, TotalEHP 145,259 to 158,805; Fire and Cold max hit keys unchanged; not re-run here"
  - "derived, not a PoB output: remaining hit fraction = (1 - s) x (1 - armourDR) + s x (1 - res); s 0.10, res 0.75, armour 0: 0.925, max hit x1.081; with armour DR 0.41: 0.552 vs 0.586, x1.06; s 0.12: x1.099 at armour 0 (researcher arithmetic)"
  - "which element is best for the Fireball seed (needs the final resistances and boss penetration, not in the seed)"
  - "which Eater tier (T1-T2 or lower) the build's source can reach (needs a crafting source)"
  - "influenced-mod availability in the current league (obtainability step not run); Scourge and Foulborn providers (ModScourge.lua:45-52, ModFoulborn.lua:16,26,200) not league-checked and left out"
  - "the 3.25.0 line about buffed influenced mods is marked Undocumented on the wiki: the values here are PoB data, not wiki"
  - "other lines of The Formless Inferno, Dawnbreaker and Taste of Hate were not read; the current Taste of Hate variant in the item was not checked"
  - "the parse trap was shown with the uncached value 37%; the repo's own copy of PoB parsing was not re-checked"
open_questions:
  - "Cloak of Flame (40% taken as Fire, hit and DoT, fire resistance on the body) uses the body slot and excludes the Sacred Chainmail suffix and Eater-implicit plan: should the generator compare it with the Eater plan? The trade-off was not evaluated."
```
