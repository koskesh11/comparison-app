---
type: interaction
status: draft
pob_refs: [conditionShatteredEnemyRecently, ShatteredEnemyRecently, conditionEnemyFrozen]
source: "poewiki Shatter rev 1673468, Freeze rev 1630938 (fetched 2026-10-24); PoB 2.67.2 ConfigOptions.lua / ModParser.lua; Data/Uniques, Data/Skills, TreeData/3_29/tree.lua"
last_confirmed_patch: "3.29.x"
---

Monsters killed by a HIT while frozen shatter: no corpse, loot still drops. Unique bosses cannot shatter and damage-over-time kills never shatter, so shatter is a pack-clearing payoff (Herald of Ice explosion, Winter's Embrace damage, corpse-denial) and has no boss value. PoB does not simulate it at all; it only has the config box "Have you Shattered an enemy Recently?" that unlocks the conditional mods. Related: [[Freeze]], [[Chill]], [[Enemy ailment threshold]].

Pipeline: none - no damage/defence step: shatter is a kill condition (corpse removal after a hit on a Frozen non-unique), it adds no damage and never applies to unique bosses or DoT kills

```interaction
id: shatter
mechanic: "Non-unique monsters killed by a hit while Frozen shatter (no corpse, loot still drops, no corpse effects); unique bosses cannot shatter; kills from damage over time never shatter, only hits"
family: ailment
pipeline_step: []
pipeline_why: "no damage/defence step: shatter is a kill condition (corpse removal after a hit on a Frozen non-unique), it adds no damage and never applies to unique bosses or DoT kills"
target: enemy
related: [freeze, chill, enemy-ailment-threshold]
pob:
  measured: none
  how: "no shatter simulation; PoB only parses the 'if you've shattered an enemy recently' conditions and has one config box (ConfigOptions.lua:1342-1343; ModParser.lua:1936,3584,4340,6498); nothing in PoB distinguishes unique boss from normal enemy for shatter"
  config:
    - {var: conditionShatteredEnemyRecently, default: false, ref: "Modules/ConfigOptions.lua:1342-1343", class: b}
  unparsed:
    - "Call of the Void: Enemies Chilled by your Hits can be Shattered as though Frozen (no PoB parse found)"
    - "Icefang Orbit / Venopuncture: Poisoned / Bleeding Enemies you Kill with Hits Shatter (not read in PoB)"
    - "Herald of Ice shatter explosion: no hook in Modules/ or SkillStatMap (grep)"
model: null
providers:
  - {kind: gem, name: "Herald of Ice", slot: any, role: abuses, target: enemy, text: "If you shatter an enemy, it explodes for AoE cold damage (L20 308-462, radius 12, 1 s cooldown); reserves 25%; the buff part (added cold) IS scored by PoB, the explosion is not; Worb runs Herald of Ice", source: "Data/Skills/act_dex.lua:9439,9511", pob: none}
  - {kind: gem, name: "Glacial Hammer", slot: any, role: enables, target: enemy, text: "glacial_hammer_shatter_frozen_enemies_at_33%_life: shatters frozen enemies at 33% life (skill-specific; non-unique enemies only, wiki 3.23.0)", source: "Data/Skills/act_str.lua:5054,5136; wiki Version 3.23.0", pob: none}
  - {kind: gem, name: "Summon Ice Golem of Shattering", slot: any, role: enables, target: enemy, text: "name only; no shatter stat in PoB data (only active_skill_no_golem_aura)", source: "Data/Skills/act_dex.lua:15858", pob: none}
  - {kind: notable, name: "Winter's Embrace", slot: tree, role: abuses, target: enemy, text: "30% increased Damage if you've Shattered an Enemy Recently (the only shatter payoff on the tree) + 60% increased Freeze Duration", source: "TreeData/3_29/tree.lua:64852 (node 41870); Modules/ModParser.lua:1936", pob: config}
  - {kind: unique, name: "Call of the Void", slot: Ring, role: enables, target: enemy, text: "Enemies Chilled by your Hits can be Shattered as though Frozen; All Damage with Hits can Chill", source: "Data/Uniques/ring.lua:1633,1635", pob: none}
  - {kind: unique, name: "Icefang Orbit", slot: Ring, role: enables, target: enemy, text: "Poisoned Enemies you Kill with Hits Shatter; Non-Chilled Enemies you Poison are Chilled", source: "Data/Uniques/ring.lua:698-699", pob: none}
  - {kind: unique, name: "Venopuncture", slot: Ring, role: enables, target: enemy, text: "Bleeding Enemies you Kill with Hits Shatter; Non-Chilled Enemies you inflict Bleeding on are Chilled", source: "Data/Uniques/ring.lua:1509-1510", pob: none}
  - {kind: unique, name: "Nuro's Harp", slot: Bow, role: abuses, target: enemy, text: "Create Consecrated Ground when you Shatter an Enemy; 15% chance to create Chilled Ground when you Freeze", source: "Data/Uniques/bow.lua:364-365", pob: none, variant: "variant 3"}
  - {kind: jewel, name: "First Snow", slot: Jewel, role: abuses, target: enemy, text: "radius jewel: with 40 Int in radius Freezing Pulse fires 2 additional Projectiles and 25% inc Freezing Pulse Damage if you've Shattered an Enemy Recently (skill-specific)", source: "Data/Uniques/jewel.lua:973-975; Modules/ModParser.lua:6498", pob: config}
  - {kind: jewel, name: "Chill of Corruption", slot: Jewel, role: abuses, target: enemy, text: "50% chance to gain an additional Vaal Soul per Enemy Shattered", source: "Data/Uniques/jewel.lua:1375", pob: none}
  - {kind: mod, name: "Shattered an enemy recently (crit multiplier / cover in frost)", slot: tree, role: abuses, target: enemy, text: "crit multiplier if you've Shattered an Enemy Recently and 'cover in frost' lines belong to tree and ascendancy, not items", source: "Modules/ModParser.lua:3584,4340", pob: config}
makes_redundant: []
conflicts:
  - {with: "unique bosses (Pinnacle Boss scenario)", effect: "cannot shatter; every shatter payoff is worth 0 against them", source: "https://www.poewiki.net/wiki/Shatter rev 1673468"}
  - {with: "damage-over-time kills", effect: "DoT kills do not shatter; culling strike is the recommended way for DoT builds that freeze (forum thread 3284453 via wiki)", source: "https://www.poewiki.net/wiki/Shatter rev 1673468"}
conditions:
  - {text: "the enemy must be Frozen and be killed by a hit; non-unique only; consequences: no corpse (no raise, explode, Elemental Proliferation transfer), no secondary form (Shield Crab), no Porcupine Goliath spines; NOT suppressed: spawn-on-death enemies (Fracturing), on-death explosions (Tormented Martyr), tar zombies", source: "https://www.poewiki.net/wiki/Shatter rev 1673468; Freeze rev 1630938"}
uptime:
  Mapping:
    value: partial
    config: {conditionShatteredEnemyRecently: "ON only if freeze is assumed (see freeze) AND hits kill (not DoT)"}
    reasoning: "needs a hit kill on a frozen non-unique enemy; packs qualify, DoT kills do not"
    source: "build-strategist table (tasks/reports/027-research.md); https://www.poewiki.net/wiki/Shatter rev 1673468"
  Pinnacle Boss:
    value: none
    config: {conditionShatteredEnemyRecently: false}
    reasoning: "unique bosses cannot shatter; only adds in the fight could shatter"
    source: "https://www.poewiki.net/wiki/Shatter rev 1673468 (introduced 0.8.6)"
seeds: [Worb]
sources:
  - {ref: "https://www.poewiki.net/wiki/Shatter (rev 1673468, 2026-07-13)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Freeze (rev 1630938), Shatter section", kind: wiki, patch: "3.29"}
  - {ref: "Modules/ConfigOptions.lua:1342-1343; Modules/ModParser.lua:1936,3584,4340,6498 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "wiki Version 3.23.0 (Glacial Hammer description), 3.24.0 (Arohongui Warmonger tattoo shatter line removed)", kind: patch_notes, patch: "3.29"}
not_verified:
  - "whether 'unique bosses cannot shatter' covers rare or magic monsters flagged unique-like (wiki says non-unique enemies; rares were not tested in game)"
  - "that no other item has a shatter line beyond those found (scan of unique lines containing 'shatter'; Shattershard 'Shield Shatter' is a block skill, not this mechanic)"
  - "that PoB tracks 'killed a frozen enemy' by itself: it is a config condition (ShatteredEnemyRecently), read from ModParser only"
open_questions: []
```
