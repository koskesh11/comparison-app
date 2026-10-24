---
type: interaction
status: draft
pob_refs: [conditionEnemyChilled, conditionEnemyChilledEffect, conditionEnemyChilledByYourHits, multiplierChilledByYouSeconds, ChillMax, ChillEffectMod, ChillDuration, ChillSourceEffect, ColdCannotChill]
source: "poewiki Chill rev 1596635, Ailment rev 1673310 (fetched 2026-10-24); PoB 2.67.2 CalcOffence.lua / CalcPerform.lua / ConfigOptions.lua / Data/Skills; TreeData/3_29/tree.lua; Data/Uniques"
last_confirmed_patch: "3.29.x"
---

Every hit with cold damage tries to chill (100%, crit or not): the enemy gets reduced action speed for 2 s, strength = 50% x (hit damage / ailment threshold)^0.4 x (1 + effect mods), capped at 30% (40% with Shaper of Winter), minimum 5%. Chill is independent of freeze. It matters because many mods pay off "against Chilled enemies" (Hypothermia, Bonechill, Hyperboreus and others) and because Bonechill folds chill effect into cold damage taken. Bonechill and the chill-effect nodes are folded into this note. Related: [[Freeze]], [[Shock]], [[Enemy ailment threshold]], [[Damage type can ailment]], [[Elemental ailment count]]. Providers beyond the seed set: see tasks/reports/027-research.md.

```interaction
id: chill
mechanic: "Cold hits chill (100% chance, crit or not); action speed reduction E = 50% x (D/T)^0.4 x (1+M), D = cold damage dealt, T = ailment threshold; min 5% (lower is discarded), cap 30% (40% with Shaper of Winter), base duration 2 s; chill is applied AFTER the hit; non-damaging chill (Chilled ground, Skitterbots) base effect 10%"
family: ailment
target: enemy
related: [freeze, shock, shatter, enemy-ailment-threshold, damage-type-can-ailment, elemental-ailment-count]
pob:
  measured: partial
  how: "chill chance forced to 100 (CalcOffence.lua:4233-4236); data Chill default 10, min 5, max 30, duration 2 (Modules/Data.lua:425-431); formula 50*(D/T)^0.4*effectMod (CalcOffence.lua:5346-5351), same as the wiki; outputs ChillDuration, ChillEffectMod, ChillSourceEffect (CalcOffence.lua:5390-5394,5430-5440); the enemy Chilled condition is set automatically only for guaranteed sources (skills with guaranteedChill / ChillingArea / NonHitChill, Skitterbots, Bonechill sets HasBonechill; CalcPerform.lua:1393-1431, 3560-3590), otherwise config only"
  config:
    - {var: conditionEnemyChilled, default: false, ref: "Modules/ConfigOptions.lua:1899", class: b}
    - {var: conditionEnemyChilledEffect, default: 0, ref: "Modules/ConfigOptions.lua:1899-1912 (count, 0 -> ChillVal)", class: c}
    - {var: conditionEnemyChilledByYourHits, default: false, ref: "Modules/ConfigOptions.lua:1899-1912", class: b}
    - {var: multiplierChilledByYouSeconds, default: 0, ref: "Modules/ConfigOptions.lua:1899-1912", class: c}
  unparsed: []
model: null
providers:
  # gems: seed set (Worb)
  - {kind: support, name: "Bonechill Support", slot: any, role: scales, target: enemy, text: "L20: +44% chill effect, 14% more cold damage; chills inflicted and chilling areas also grant cold damage taken equal to the slow amount (PoB sets Condition:Chilled and ColdDamageTaken 'Bonechill' on the enemy via skill flag supportBonechill); gate Attack|Damage|NonHitChill|ChillingArea", source: "Data/Skills/sup_int.lua:541,591; Modules/CalcPerform.lua:1393-1432,3507-3511", pob: full}
  - {kind: support, name: "Hypothermia Support", slot: any, role: abuses, target: enemy, text: "more damage with hits and ailments against chilled enemies (L20 29%), more cold DoT, +20% chance to freeze chilled enemies; PoB's DoT bonus has no Chilled condition (wiki says against chilled)", source: "Data/Skills/sup_dex.lua:2335-2382; Data/SkillStatMap.lua:1055-1056; wiki Hypothermia Support", pob: partial}
  - {kind: support, name: "Coursing Current Support", slot: any, role: scales, target: enemy, text: "3.29.0: L3 chill effect +28% and shock effect +28%; each of chill and shock inflicts the other (inflict_equivalent_shock_on_inflicting_chill_with_hits)", source: "Data/Skills/sup_int.lua:1318,1340; wiki Version 3.29.0", pob: partial}
  - {kind: gem, name: "Frost Shield", slot: any, role: applies, target: enemy, text: "chills enemies in area (ChillingArea, NonHitChill); quality +1% cold ailment effect per 1%", source: "Data/Skills/act_int.lua:8014", pob: full}
  - {kind: gem, name: "Summon Ice Golem", slot: any, role: applies, target: enemy, text: "chilling spinning attack (minion skill, ChillingArea type); golem buff +40% crit chance", source: "Data/Skills/act_dex.lua:15693,15757", pob: partial}
  # tree: seed set and alternatives
  - {kind: mod, name: "Chill Effect smalls (20% inc Effect of Chill)", slot: tree, role: scales, target: enemy, text: "20% increased Effect of Chill (nodes 21170, 53290, 40483, 30427); Season of Ice 2959 also +12% Cold DoT Multiplier", source: "TreeData/3_29/tree.lua:61803,64749,64766,79016,78997", pob: full}
  - {kind: notable, name: "Chilling Presence", slot: tree, role: applies, target: enemy, text: "Nearby Enemies are Chilled", source: "TreeData/3_29/tree.lua:87710 (node 58248)", pob: config}
  - {kind: mastery, name: "Cold Mastery (effect 19495)", slot: tree, role: scales, target: enemy, text: "Chills from your Hits always reduce Action Speed by at least 10%", source: "TreeData/3_29/tree.lua:54791", pob: full}
  - {kind: mastery, name: "Mace Mastery (effect 37132)", slot: tree, role: enables, target: enemy, text: "All Damage with Maces and Sceptres inflicts Chill (weapon-scoped; no use for staff or wand casters)", source: "TreeData/3_29/tree.lua:20864; Modules/ModParser.lua:3646", pob: full}
  - {kind: ascendancy, name: "Shaper of Winter (Elementalist)", slot: tree, role: enables, target: enemy, text: "All Damage with Hits can Chill / Your Chills can reduce Action Speed by up to a maximum of 40% / Enemies Chilled by your Hits lessen their Damage dealt by half of Chill Effect (this is 'can CHILL', not 'can Freeze')", source: "TreeData/3_29/tree.lua:50179 (node 40810); Modules/ModParser.lua:2794,2816", pob: full}
  - {kind: notable, name: "Glacial Cage", slot: tree, role: abuses, target: enemy, text: "Enemies permanently take 1% inc Damage per second ever Chilled, max 10%", source: "TreeData/3_29/tree.lua:64789 (node 62849)", pob: config}
  - {kind: notable, name: "Snowstorm / Blanketed Snow", slot: tree, role: abuses, target: enemy, text: "8% of Lightning as extra Cold vs Chilled / Penetrate 10% Cold Resistance vs Chilled", source: "TreeData/3_29/tree.lua:87160,87205", pob: config}
  - {kind: keystone, name: "Bitter Frost", slot: tree, role: abuses, target: enemy, text: "Enemies Chilled by your Hits have Cold Damage taken increased by Chill Effect / Cannot deal non-Cold Damage", source: "TreeData/3_29/tree.lua:56305 (node 12128)", pob: config}
  - {kind: notable, name: "Fingers of Frost", slot: tree, role: abuses, target: enemy, text: "Chilled enemies freeze 30% chance (UNPARSED in PoB)", source: "TreeData/3_29/tree.lua:61759; Data/ModCache.lua:15273", pob: none}
  - {kind: ascendancy, name: "Corpse Pact (Necromancer)", slot: tree, role: applies, target: enemy, text: "Enemies near corpses you Spawned Recently are Chilled and Shocked", source: "TreeData/3_29/tree.lua:57455 (node 23572)", pob: config}
  # uniques
  - {kind: unique, name: "Call of the Void", slot: Ring, role: enables, target: enemy, text: "All Damage with Hits can Chill; Enemies Chilled by your Hits lessen their Damage dealt by half of Chill Effect; can be Shattered as though Frozen", source: "Data/Uniques/ring.lua:1633,1635,1636; Modules/ModParser.lua:2816,2839", pob: partial}
  - {kind: unique, name: "Soul Taker", slot: Axe, role: enables, target: enemy, text: "Your Physical Damage can Chill", source: "Data/Uniques/axe.lua:160", pob: full, variant: "variant 5"}
  - {kind: unique, name: "Zerphi's Heart", slot: Amulet, role: enables, target: enemy, text: "Chaos Damage can Ignite, Chill and Shock", source: "Data/Uniques/amulet.lua:1025; Modules/ModParser.lua:3674", pob: full, variant: "variant 2"}
  - {kind: unique, name: "Replica Frostbreath", slot: Mace, role: enables, target: enemy, text: "Your Chaos Damage can Chill; Attacks with this Weapon deal Double Damage to Chilled Enemies", source: "Data/Uniques/mace.lua:139-140", pob: full}
  - {kind: unique, name: "Expedition's End", slot: Body Armour, role: applies, target: enemy, text: "Nearby Enemies are Chilled; Freeze Chilled Enemies as though dealing (50-100)% more Damage", source: "Data/Uniques/body.lua:1262-1263", pob: full}
  - {kind: unique, name: "Ahuana's Bite", slot: Quiver, role: scales, target: enemy, text: "Chill Enemies as though dealing (60-100)% more Damage; Enemies Chilled by your Hits have Damage taken increased by Chill Effect", source: "Data/Uniques/quiver.lua:13-14; Modules/ModParser.lua:3744,3868", pob: full}
  - {kind: unique, name: "Hyperboreus", slot: Belt, role: applies, target: enemy, text: "Chill nearby Enemies when you Focus (30% reduced Action Speed); (50-70)% inc Damage with Hits and Ailments against Chilled Enemies (variants 11-19 differ only in the picked line)", source: "Data/Uniques/belt.lua:436,439", pob: partial}
  - {kind: unique, name: "The Pandemonius", slot: Amulet, role: applies, target: enemy, text: "Chill Enemy for 1 s when Hit; Damage Penetrates 20% Cold Resistance against Chilled Enemies. Foulborn replaces the Cold-damage line with 'Cannot be Chilled'", source: "Data/Uniques/amulet.lua:585,587; Data/ModFoulbornMap.jsonc:83", pob: partial}
  - {kind: unique, name: "Frostbreath / Cospri's Malice / Tasalio's Sign", slot: various, role: abuses, target: enemy, text: "Double Damage to Chilled Enemies (Frostbreath mace); +60% Crit Chance vs Chilled (Cospri's Malice sword); Adds 40-60 Cold vs Chilled (Tasalio's Sign ring)", source: "Data/Uniques/mace.lua:127; sword.lua:680; ring.lua:1298", pob: config}
  - {kind: unique, name: "The Three Dragons (cold line)", slot: Helmet, role: blocks, target: enemy, text: "Your Cold Damage can Ignite but not Freeze or Chill; stays on the Foulborn unless it is the mutated line", source: "Data/Uniques/helmet.lua:1670", pob: full}
  - {kind: unique, name: "Galesight / Leadership's Price", slot: various, role: blocks, target: enemy, text: "Cannot inflict Freeze or Chill (Galesight); Cannot Ignite, Chill, Freeze or Shock (Leadership's Price)", source: "Data/Uniques/helmet.lua:654; amulet.lua:817", pob: full}
  - {kind: keystone, name: "Secrets of Suffering", slot: tree, role: blocks, target: enemy, text: "Cannot Ignite, Chill, Freeze or Shock", source: "TreeData/3_29/tree.lua:85638 (node 57280)", pob: full}
makes_redundant:
  - {provider: "chance to chill lines", when: "any cold hit", why: "chill chance is forced to 100% in PoB and in the game for hits that can chill; only damage-type permission, effect and duration matter", source: "Modules/CalcOffence.lua:4233-4235; https://www.poewiki.net/wiki/Chill rev 1596635"}
conflicts:
  - {with: "The Three Dragons cold line (Foulborn keeps it unless mutated)", effect: "cold hits cannot chill; with both chaos mutations nothing chills", source: "Data/Uniques/helmet.lua:1670; vault Gaps/Foulborn The Three Dragons"}
  - {with: "Elemental Overload (keystone)", effect: "removes the crit link used by Critical Mastery 9986 (50% inc Effect of non-Damaging Ailments you inflict with Critical Strikes)", source: "TreeData/3_29/tree.lua:39958,23938"}
conditions:
  - {text: "chill applies AFTER the hit (magnitude depends on damage dealt); only the strongest chill applies; effect mods apply before min/max (100% inc effect lowers damage needed for the 5% minimum to 0.06% of T and for max to 4.93% of T)", source: "https://www.poewiki.net/wiki/Chill rev 1596635"}
  - {text: "a hit-chill does NOT make the enemy 'Chilled' for 'against chilled enemies' mods in PoB unless a guaranteed source or the config box exists", source: "Modules/CalcPerform.lua:3500-3516,3560; Modules/ConfigOptions.lua:1899-1912"}
  - {text: "if the player chills with several damage types, the chill effect uses the total damage of all applicable types", source: "https://www.poewiki.net/wiki/Chill rev 1596635 (In-depth)"}
uptime:
  Mapping:
    value: high
    config: {conditionEnemyChilled: true, conditionEnemyChilledEffect: "model: only from the chill formula, small on packs and capped at 30%"}
    reasoning: "cold hit = 100% chill; ON if the build deals cold hits"
    source: "Modules/CalcOffence.lua:4233-4236; build-strategist table (tasks/reports/027-research.md)"
  Pinnacle Boss:
    value: high
    config: {conditionEnemyChilled: "true if the build deals cold hits (the condition is safe for 'vs chilled' mods)", conditionEnemyChilledEffect: "only from a model against the boss threshold; effect size is low"}
    reasoning: "the condition is hit-based and reliable; the effect size against the boss threshold (PoB 7.68 x 404%) is low"
    source: "https://www.poewiki.net/wiki/Chill rev 1596635; Modules/CalcOffence.lua:5333-5343"
seeds: [Worb]
sources:
  - {ref: "https://www.poewiki.net/wiki/Chill (rev 1596635, 2025-11-25)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Ailment (rev 1673310)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcOffence.lua:4233-4236,5346-5351; Modules/CalcPerform.lua:1393-1432,3500-3516; Modules/Data.lua:425-431 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "wiki Version 3.20.0 (monster chill multiplicative), 3.21.1 (no 300 ms discard), 3.29.0 (Coursing Current support)", kind: patch_notes, patch: "3.29"}
not_verified:
  - "whether the Chill page formula is current: it carries no confirm tag, but the Shock page tags the same formula 'potentially outdated'; no patch after 3.9.0 changing it was found (PoB uses the same exponent 0.4 and base 50%)"
  - "that a normal cold spell with no Bonechill leaves Condition:Chilled false in PoB (read from code, not run on a build)"
  - "chill-count caps; Unrestrained Focus (Unaffected by Chill while Channelling) is self-defence only"
open_questions:
  - "Pinnacle Boss: should 'against chilled enemies' mods be credited without the config box when the build deals cold hits (strategist rule: yes)?"
```
