---
type: interaction
status: draft
pob_refs: [conditionEnemyOnConsecratedGround, conditionOnConsecratedGround, DamageTakenConsecratedGround, ConsecratedGroundEffect]
source: "wiki Consecrated ground rev 1660567, Bottled Faith rev 1485045; PoB 2.67.2 ConfigOptions.lua, CalcPerform.lua, ModParser.lua, Data/Uniques/flask.lua; item-analyst, tree-ascendancy-analyst, build-strategist (task 027)"
last_confirmed_patch: "3.29.x"
---

Consecrated ground heals the player standing on it (5% life per second, 50% reduced curse effect on you). Ground created by a flask like Bottled Faith also hurts the enemy: increased damage taken and increased critical strike chance against enemies on it, but only while the flask is active and only if the enemy stands on the ground. Trap in PoB: the effect needs the ENEMY-side config, not the player-side one.

Pipeline: [[Damage calculation#Damage taken]], [[Damage calculation#Critical strike]], [[Receiving damage#Recovery]] - the flask ground adds increased damage taken (additive with other taken mods) and increased crit chance on the enemy; the 5% life regen on the player is a Recovery effect; enemy-side config is needed or PoB shows none of it

Config trap: Bottled Faith needs `conditionEnemyOnConsecratedGround` (ConfigOptions.lua:2012). vault/Scenarios/Pinnacle Boss.md sets `conditionOnConsecratedGround` (the player side, ConfigOptions.lua:1148), which gives life regeneration and accuracy and does nothing for the flask's enemy mods. Recorded in not_verified / open_questions; the Scenarios note was not edited.

```interaction
id: consecrated-ground
mechanic: "Ground the player (or a flask) creates: own effect 5% life regen per second and 50% reduced curse effect on you; created by an enemy it affects enemies instead. Bottled Faith adds 7-10% increased damage taken by enemies on it and 100-150% increased critical strike chance against them, during flask effect only"
family: buff
pipeline_step: ["Damage calculation#Damage taken", "Damage calculation#Critical strike", "Receiving damage#Recovery"]
pipeline_why: "the flask ground adds increased damage taken (additive with other taken mods) and increased crit chance on the enemy; the 5% life regen on the player is a Recovery effect; enemy-side config is needed or PoB shows none of it"
target: enemy
related: [flask-uptime]
pob:
  measured: config
  how: "enemy condition OnConsecratedGround is a manual config (ConfigOptions.lua:2012-2013, default off); enemy DamageTaken INC = floor(DamageTakenConsecratedGround x (1 + ConsecratedGroundEffect)) (CalcPerform.lua:3662-3665); 'against enemies on consecrated ground' parses to ActorCondition enemy OnConsecratedGround (ModParser.lua:1998); 'during effect' to Condition UsingFlask (ModParser.lua:1738); damage-taken mod to an EnemyModifier (ModParser.lua:4168); flask uptime and ground duration are not modelled (all-or-nothing)"
  config:
    - {var: conditionEnemyOnConsecratedGround, default: false, ref: "ConfigOptions.lua:2012-2013", class: b}
    - {var: conditionOnConsecratedGround, default: false, ref: "ConfigOptions.lua:1148 (player side: 5% life regen + accuracy, CalcPerform.lua:804-808)", class: b}
    - {var: "flask slot active (UsingFlask)", default: false, ref: "CalcSetup.lua:1028-1031", class: c}
  unparsed:
    - "Bottled Faith: Consecrated Ground created by this Flask has Tripled Radius (area only)"
model: null
providers:
  - {kind: unique, name: "Bottled Faith", slot: flask, role: abuses, target: enemy, text: "Creates Consecrated Ground on Use; (15-30)% reduced Duration; tripled radius; ground applies (7-10)% increased Damage taken to Enemies during Effect; (100-150)% increased Critical Strike Chance against Enemies on Consecrated Ground during Effect", source: "PoB Data/Uniques/flask.lua:136-152 (variant 3); wiki Bottled Faith rev 1485045", pob: config}
  - {kind: unique, name: "The Sorrow of the Divine", slot: flask, role: applies, target: self, text: "Creates Consecrated Ground on Use; Life Recovery from Flasks also applies to ES; Zealot's Oath", source: "PoB Data/Uniques/flask.lua:345-347", pob: partial}
  - {kind: unique, name: "The Overflowing Chalice", slot: flask, role: applies, target: self, text: "Creates Consecrated Ground on Use; (50-100)% increased Charges gained by other Flasks", source: "PoB Data/Uniques/flask.lua:434, 439", pob: partial}
  - {kind: unique, name: "Gifts from Above", slot: ring, role: applies, target: self, text: "Trigger Level 10 Consecrate on Crit; +50% Damage while on Consecrated Ground", source: "PoB Data/Uniques/ring.lua:561, 566", pob: partial}
  - {kind: unique, name: "Zahndethus' Cassock", slot: body, role: applies, target: self, text: "100% chance to create Consecrated Ground when you Block (variant 4)", source: "PoB Data/Uniques/body.lua:786", pob: partial}
  - {kind: unique, name: "Watcher's Eye (Zealotry)", slot: jewel, role: scales, target: enemy, text: "makes your consecrated ground apply increased damage taken to enemies; stacks additively with Bottled Faith", source: "wiki Bottled Faith rev 1485045 (interaction note)", pob: none}
  - {kind: ascendancy, name: "Sanctuary 39790 (Inquisitor)", slot: tree, role: applies, target: enemy, text: "Consecrated Ground you create applies 15% increased Damage taken to Enemies; Consecrated Ground around you while stationary", source: "PoB TreeData/3_29/tree.lua:16448", pob: partial}
  - {kind: ascendancy, name: "Inquisitor 43962", slot: tree, role: applies, target: self, text: "10% chance to create Consecrated Ground on Hit vs Rare/Unique 8 s, linger 4 s", source: "PoB TreeData/3_29/tree.lua:17939", pob: partial}
  - {kind: notable, name: "Righteous Fury 55002", slot: tree, role: applies, target: self, text: "10% chance to create Consecrated Ground on Melee Kill", source: "PoB TreeData/3_29/tree.lua:33255", pob: partial}
  - {kind: notable, name: "Devotion 36949", slot: tree, role: scales, target: self, text: "+25% Consecrated Ground Effect, +10% Life", source: "PoB TreeData/3_29/tree.lua:25378", pob: partial}
  - {kind: unique, name: "Broken Faith", slot: shield, role: blocks, target: self, text: "Create Profane Ground instead of Consecrated Ground", source: "PoB Data/Uniques/shield.lua:970", pob: partial}
  - {kind: keystone, name: "Worship the Blightheart 27781", slot: tree, role: blocks, target: self, text: "Create Fungal Ground instead of Consecrated Ground", source: "PoB TreeData/3_29/tree.lua:51799", pob: partial}
  - {kind: notable, name: "Bitter Heresy 27869 (Lycia)", slot: tree, role: blocks, target: self, text: "Profane Ground instead of Consecrated Ground", source: "PoB TreeData/3_29/tree.lua:14241", pob: partial}
makes_redundant: []
conflicts:
  - {with: "Broken Faith, Worship the Blightheart, Bitter Heresy", effect: "convert consecrated ground into profane / fungal ground: no consecrated-ground payoff", source: "tree-ascendancy-analyst.md; item-analyst.md"}
conditions:
  - {text: "Bottled Faith effects need the ENEMY standing on the ground AND the flask active (during Effect); a boss that moves out of the ground loses it", source: "wiki Bottled Faith rev 1485045; PoB ModParser.lua:1738, 1998"}
  - {text: "both Bottled Faith effect mods are flask-local; ground radius 18 on the Sulphur base, tripled", source: "wiki cargo mod_stats (via mechanics-researcher-other.md)"}
  - {text: "Sulphur Flask lasts 8 s; Bottled Faith (15-30)% reduced Duration gives about 5.6-6.8 s of effect", source: "wiki Bottled Faith rev 1485045"}
uptime:
  Mapping:       {value: partial, config: {conditionEnemyOnConsecratedGround: "only if a source exists (enemy side)"}, reasoning: "ground is stationary under packs that run through it; treat as low-partial for packs; flask duration about 5.6-6.8 s", source: "build-strategist.md; wiki Bottled Faith rev 1485045"}
  Pinnacle Boss: {value: high, config: {conditionEnemyOnConsecratedGround: "only if a source exists (enemy side)"}, reasoning: "high if the boss is stationary; many pinnacle bosses move or teleport, then partial", source: "build-strategist.md"}
seeds: [FR]
sources:
  - {ref: "https://www.poewiki.net/wiki/Consecrated_ground (rev 1660567, 2026-07-07)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Bottled_Faith (rev 1485045, 2024-09-30)", kind: wiki, patch: "3.25"}
  - {ref: "PoB Modules/ConfigOptions.lua:1148, 2012-2013; Modules/CalcPerform.lua:804-808, 3662-3665; Modules/ModParser.lua:1738, 1998, 4168", kind: pob, patch: "3.29"}
not_verified:
  - "vault/Scenarios/Pinnacle Boss.md sets conditionOnConsecratedGround (player side, ConfigOptions.lua:1148); Bottled Faith's enemy-side effects need conditionEnemyOnConsecratedGround (ConfigOptions.lua:2012). Check the scenario and the engine mapping; this note did not edit the Scenarios note"
  - "ground duration (not on the wiki pages for Consecrated ground or Sulphur Flask; assume flask duration, unconfirmed) and radius in metres for 18 x3"
  - "which of the listed providers a Bottled Faith build can combine (item analyst: seed pin only)"
  - "Zealotry Watcher's Eye line taken from the wiki interaction note, not from a PoB item run"
open_questions:
  - "Should the Pinnacle Boss scenario set the enemy-side conditionEnemyOnConsecratedGround (the Bottled Faith mods need it) instead of, or besides, the player-side condition?"
```
