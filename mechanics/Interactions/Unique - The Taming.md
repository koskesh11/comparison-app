---
type: interaction
status: draft
pob_refs: [TotalDPS, FullDPS, LightningResist, EnemyFreezeChance, EnemyShockChance, EnemyIgniteChance, FreezeChanceOnHit, ShockChanceOnHit]
source: "PoB 2.67.2 Data/Uniques/ring.lua:1259-1278, Data/ModCache.lua:2658/1099/3627, ModParser.lua:3627-3635, ConfigOptions.lua:1878-1958, CalcOffence.lua:4234-4249; poewiki The Taming rev 1649810; vault Chance on hit uptime, Elemental ailment count; headless Worb probes (task 027 batch 2c, item-analyst-worb.md)"
last_confirmed_patch: "3.29.x"
---

The Taming is a package: 39% increased Elemental Damage with Hits and Ailments for each type of elemental ailment on the enemy (the point), a freeze/shock/ignite chance line, and +31% all elemental resistance in two lines. In Worb only three types are reachable (Chilled, Frozen, Shocked = 117%), so the ring is already at its cap; an automatic "tick every ailment" would add +14% that does not exist ([[Elemental ailment count]]).
PoB credits the 39% line -10.50% (Pinnacle and Mapping); the resistances only matter as a Lightning overcap buffer (75 -> 66 without the ring) and the chance line is dead (nothing in Worb can ignite, freeze/shock are already 100%). The ring's share of the three config ticks is 0 for Chilled (Winter Orb chills by itself, the box only carries the effect value), -3.5% for Shocked and -3.5% for Frozen.
Pipeline: [[Damage calculation#Increased and reduced]] - the 39% per type joins the same additive elemental/cold INC pool as the Light of Meaning (each further 39 is a shrinking share)

```interaction
id: unique-the-taming
mechanic: "Unique package: 39% increased Elemental Damage per elemental ailment type on the enemy (Worb reaches 3 of 7 types = 117%) plus +31% all elemental resistances and a freeze/shock/ignite chance line that does nothing in this build"
family: ailment
pipeline_step: ["Damage calculation#Increased and reduced"]
pipeline_why: "the line is Elemental Damage INC per enemy ailment condition, so it adds to the single additive increased pool (Worb pool 1014%: Light 180 + Taming 117 + rest)"
target: enemy
related: [elemental-ailment-count, freeze, shock, chill, ignite, damage-type-can-ailment, chance-on-hit-uptime, enemy-ailment-threshold, scorch-brittle-sap, radius-jewel]
pob:
  measured: config
  how: "Parse: every line parses, extra = nil. The 39% line is a live parse (ModCache has the 10/20/35% forms, not 39%): 7 mods ElementalDamage INC 39, keywordFlags 786432 (Hit|Ailment), one per enemy condition Frozen, Chilled, Ignited, Shocked, Scorched, Brittle, Sapped (ModParser.lua:3627-3635). PoB counts a type only when its enemy condition is true; the conditions come from config ticks (ConfigOptions.lua:1878, 1884, 1899, 1924, 1931, 1943, 1958, defaults false), except Chilled which Winter Orb sets itself (ChillChance forced 100, CalcOffence.lua:4234-4236; Condition Chilled stays 1 with the box off). Whole-item removal Worb (Pinnacle / Mapping): TotalDPS 1,343,497.51 -> 1,202,400.81 (-10.50%) / 1,934,211.10 -> 1,731,076.52 (-10.50%), FullDPS 6,012,004.07 / 8,655,382.60; LightningResist 75 -> 66 (Fire/Cold stay 75); EHP -5.20% Pinnacle / 0.00% Mapping; no unmet requirement. Pool arithmetic: Cold + Elemental + Damage INC on hit 1014%, Taming 3 types x 39 = 117, Light of Meaning 180: (1+9.97)/(1+11.14) = x0.895 = -10.50%."
  config:
    - {var: conditionEnemyChilled, default: false, ref: "Modules/ConfigOptions.lua:1878", class: b}
    - {var: conditionEnemyShocked, default: false, ref: "Modules/ConfigOptions.lua:1884", class: b}
    - {var: conditionEnemyFrozen, default: false, ref: "Modules/ConfigOptions.lua:1899", class: b}
    - {var: conditionEnemyIgnited, default: false, ref: "Modules/ConfigOptions.lua:1924", class: b}
    - {var: conditionEnemyScorched, default: false, ref: "Modules/ConfigOptions.lua:1931", class: b}
    - {var: conditionEnemyBrittle, default: false, ref: "Modules/ConfigOptions.lua:1943", class: b}
    - {var: conditionEnemySapped, default: false, ref: "Modules/ConfigOptions.lua:1958", class: b}
  unparsed: []
model: null
providers:
  - {kind: unique, name: "The Taming", variant: "Current (since 3.25.0)", slot: Ring 2, role: sustains, target: self, text: "implicit: +9% to all Elemental Resistances (0.00% DPS; with the +22% only the Lightning overcap 75 -> 66)", source: "Data/Uniques/ring.lua:1266; ModCache.lua:2658", pob: full}
  - {kind: unique, name: "The Taming", slot: Ring 2, role: sustains, target: self, text: "+22% to all Elemental Resistances ((20-30)); 0.00% DPS, Lightning overcap buffer of 22 only", source: "Data/Uniques/ring.lua:1268; ModCache.lua:1099", pob: full}
  - {kind: unique, name: "The Taming", slot: Ring 2, role: applies, target: enemy, text: "10% chance to Freeze, Shock and Ignite: dead line in Worb (Ignite impossible: DealNoFire, ColdCanIgnite not set; Freeze/Shock chance already 100 with and without the ring, so under 1 point added, DPS 0.00%)", source: "Data/Uniques/ring.lua:1272; ModCache.lua:3627; CalcOffence.lua:4244-4249", pob: full}
  - {kind: unique, name: "The Taming", slot: Ring 2, role: abuses, target: enemy, text: "39% increased Elemental Damage with Hits and Ailments for each type of Elemental Ailment on Enemy ((30-40); two lines in the file): -10.50% TotalDPS when removed, 117% with Chilled + Frozen + Shocked", source: "Data/Uniques/ring.lua:1277-1278; ModParser.lua:3627-3635; live parse", pob: config}
package:
  seed: Worb
  slot: Ring 2
  base: "Prismatic Ring, no sockets"
  xml_item_id: 8
  variant: "Current (legacy variants 3.25.0 and 3.0.0 on the wiki page)"
  removal: "TotalDPS -10.50% Pinnacle and Mapping (39% line = the whole delta; resistance lines and chance line 0.00% DPS; Lightning 75 -> 66; EHP -5.20% Pinnacle) - in-memory removal; the ring has no sockets, so there is no emptied-slot gem effect, but PoB's number is still a single-enemy headless delta, not a game fact. Config-tick shares with the ring (Pinnacle / Mapping): Chilled box 0 (Winter Orb chills by itself), Shocked box -3.5% of the -30.59% / -30.51%, Frozen box the whole -3.50% tick; all three off with ring -39.05% / -38.98%, without ring -34.46% / -34.39%"
  lost_with_item:
    - "117% damage pool share (3 ailment types x 39) = -10.50% TotalDPS"
    - "+31% all elemental resistances (Lightning 75 -> 66, Fire and Cold stay 75: overcap buffer of 22 on Lightning only)"
    - "conditions UniqueItemInRing 2 off; multipliers RingItem 2 -> 1, PrismaticRingEquipped off, UniqueItem 3 -> 2"
  downsides_that_are_the_point: []
  foulborn: "none: wiki The Taming rev 1649810: 'Using all Foulborn uniques for the recipe will not create a Foulborn The Taming (which does not exist)'; ModFoulbornMap grep = no hit"
  obtainability: "poewiki The Taming rev 1649810: release 1.0.0, is_drop_restricted 1, drop_text 'The Taming is a vendor recipe item.'; recipe Berek's Grip + Berek's Pass + Berek's Respite (or 3x Hunter's Reward); PoB ring.lua:1259-1260 'League: Domination, Nemesis; Source: Vendor Recipe'. Patch 3.29"
makes_redundant:
  - {provider: "The Taming chance line (10% freeze/shock/ignite)", when: "Rashkaldor's Patience, or when other sources already reach 100 (Worb: freeze chance 90 with the ring / 80 without, shock 100 from Tree:27038 alone)", why: "chance is capped at 100 (min(100, chance), CalcOffence.lua:4244); crits always apply", source: "CalcOffence.lua:4244-4249; w2.json"}
conflicts:
  - {with: "Leadership's Price, Galesight, Secrets of Suffering", effect: "cut the ailment type count the 39% line multiplies by (vault Elemental ailment count)", source: "vault Elemental ailment count"}
  - {with: "Light of Meaning and other Cold/Elemental Damage INC", effect: "same additive pool, diminishing share: each 39 is about 3.5% in Worb", source: "w3.json pool 1014%"}
conditions:
  - {text: "Each ailment type counts once; PoB counts a type only when its enemy condition is true (config tick, or Chilled set by the skill)", source: "ModParser.lua:3627-3635; poewiki The Taming rev 1649810"}
  - {text: "Ignited / Scorched / Brittle / Sapped are not attainable in Worb (no fire damage, ColdCanIgnite not set, Scorch/Brittle/Sap chance 0, no inflict flag): ticking them would add +3.50% each with the ring that does not exist in play; all 7 ticked = +14.00%", source: "w2.json; ConfigTab.lua:1138-1160; ConfigOptions.lua:1884/1931/1958"}
uptime:
  Mapping:       {value: high, config: {conditionEnemyChilled: true, conditionEnemyShocked: true, conditionEnemyFrozen: true}, reasoning: "chance on hit uptime method with V 6.45/s, lower bound m = 1 hit per volley for packs: Shock d 3.4 s, n = 21, p = 1 (Tree:27038 alone) -> 100%; Chill d 3.4 s, p = 1 -> 100%; Freeze p 0.90 per hit (0.993 counting crits 93.39%) -> about 100%. All three at least 80%, boxes ticked, no notice (= Worb.xml)", source: "vault Chance on hit uptime; CalcOffence.lua:4244-4249"}
  Pinnacle Boss: {value: partial, config: {conditionEnemyChilled: true, conditionEnemyShocked: true, conditionEnemyFrozen: "chance is about 100%, whether the freeze lasts against the boss threshold is open"}, reasoning: "chance side as in Mapping with m = 4 hits per volley from the vault model; freeze duration against a pinnacle boss's ailment threshold is not verified", source: "vault Chance on hit uptime; vault Freeze; vault Enemy ailment threshold"}
seeds: [Worb]
sources:
  - {ref: "https://www.poewiki.net/wiki/The_Taming (rev 1649810)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Data/Uniques/ring.lua, Data/ModCache.lua, Modules/ModParser.lua, Modules/ConfigOptions.lua, Modules/CalcOffence.lua", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/partial/b2c/item-analyst-worb.md (headless Worb probes, SC/out/w1.json, w2.json, w3.json)", kind: pob, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: freeze duration against a pinnacle boss's freeze threshold"
  - "wiki says a type counts once per type (rev 1649810), which matches PoB"
open_questions:
  - "Should the generator cap the ailment-type tick count at what the build can reach (Worb: 3 of 7) instead of ticking every box?"
```
