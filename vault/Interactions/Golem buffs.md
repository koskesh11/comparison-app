---
type: interaction
status: draft
pob_refs: [ActiveGolemLimit, base_number_of_golems_allowed, golem_buff_effect_+%, HaveColdGolem]
source: "PoB 2.67.2 CalcPerform.lua:1443-1448 / SkillStatMap.lua:1991, 2089 / ModParser.lua:478-485, 4443 / ModCache.lua:932, 9323, 21965-21966; poewiki Golem rev 1702428, Liege of the Primordial rev 1625326, Golem Commander rev 1343723; skill-gem-analyst, tree-ascendancy-analyst, item-analyst, b1-tree-ascendancy-analyst.md (task 027); tasks/reports/021-gate1.md N5"
last_confirmed_patch: "3.29.x"
---

Each summoned golem skill gives the player a buff while the golem lives. PoB applies the buff of every enabled golem skill but does NOT enforce the golem limit (the limit is only parsed and shown), so enforcing count <= limit is the app's job: [[Golem count within limit]] (task 021, not merged). The Worb seed runs 4 golems = 1 base (wiki Golem rev 1702428: a player can have one active golem by default) + Golem Commander (+1) + Liege of the Primordial (+2). Duplicates of the same golem add nothing (buffs do not stack, same page). Since 3.28.0 Liege no longer scales buff effect (wiki rev 1625326): it only adds +2 count, elemental immunity for the golems and a resummon 4 s after death, which PoB does not parse; Golem Commander (40%) is the only buff-effect node of the two.
Impact EK: the Assassin cannot take Liege (Elementalist ascendancy) and the EK golem use is not read, so no claim. Impact Fireball: Liege costs 2 of the 8 ascendancy points and competes with Shaper of Storms and Bastion of Elements ([[Primal Aegis and Bastion of Elements]]); Golem Commander is a regular notable. Whether the golem buffs are worth it is a DPS and defence question for PoB (each golem separately).

Pipeline: none - no single step: each golem gives a different buff (crit, speed, damage, defence) that acts in that buff's own step; check the individual golem rather than the group

```interaction
id: golem-buffs
mechanic: "Summoned golems grant the player a buff each (crit, speed, damage, defence); the number of golems is capped by ActiveGolemLimit; golem buff effect is scaled by 'effect of buffs granted by your golems'"
family: buff
pipeline_step: []
pipeline_why: "no single step: each golem gives a different buff (crit, speed, damage, defence) that acts in that buff's own step; check the individual golem rather than the group"
target: self
related: [arcane-surge, power-charges]
pob:
  measured: partial
  how: "buffs are GlobalEffect Buff mods on the player, applied when the golem skill group is enabled (no minion damage needed); ActiveGolemLimit = max over golem skills (CalcPerform.lua:1443-1448, SkillStatMap.lua:1991, ModParser.lua:4443-4445); no comparison with the number of golem skills (grep GolemLimit in Modules/Classes: parse and output only). Buff effect scalers ModParser.lua:478-485, SkillStatMap.lua:2089-2093"
  config:
    - {var: conditionSummonedGolemInPast8Sec, default: false, ref: "ConfigOptions.lua:1127-1131", class: b}
    - {var: conditionSummonedGolemInPast10Sec, default: false, ref: "ConfigOptions.lua:1127-1131", class: b}
    - {var: Carrion/Chaos/Stone golem equal-count checks, default: false, ref: "ConfigOptions.lua:347-361", class: c}
  unparsed:
    - "You can have 1 additional golem (unsupported, extra = full text)"
    - "Liege of the Primordial: Summoned Golems are Resummoned 4 seconds after being Killed (ModCache.lua:21966 = {nil, text}, so PoB gives no resummon uptime)"
model: null
providers:
  - {kind: gem, name: "Summon Ice Golem", slot: gem, role: enables, target: self, text: "+40% increased Critical Strike Chance, +420 accuracy (L20); sets Condition HaveColdGolem", source: "PoB act_dex.lua:15693-15757", pob: full}
  - {kind: gem, name: "Summon Lightning Golem", slot: gem, role: enables, target: self, text: "+10% attack and cast speed, +1081 mana regen per minute (L20)", source: "PoB act_int.lua:19183-19248", pob: full}
  - {kind: gem, name: "Summon Flame Golem", slot: gem, role: enables, target: self, text: "+29% increased Damage, +20% increased Area of Effect (L20)", source: "PoB act_str.lua:11383-11447", pob: full}
  - {kind: gem, name: "Summon Stone Golem", slot: gem, role: enables, target: self, text: "+6300 life regeneration per minute, +20% defences (L20)", source: "PoB act_str.lua:11629-11694", pob: full}
  - {kind: gem, name: "Summon Chaos Golem", slot: gem, role: enables, target: self, text: "+16 DoT multiplier, +17% chaos resistance (L20)", source: "PoB act_int.lua:18767-18831", pob: full}
  - {kind: notable, name: "Golem Commander 34506", slot: tree, role: scales, target: self, text: "40% increased Effect of Buffs granted by your Golems; +1 to maximum number of Summoned Golems (3.16.0: 40%, up from 30%, and the 15% life / 20% damage line removed; introduced 3.8.0)", source: "TreeData/3_29/tree.lua:57162-57176; Data/ModCache.lua:9323 (BuffEffect INC 40, SkillType Golem); ModParser.lua:478; wiki Golem Commander rev 1343723", pob: full}
  - {kind: ascendancy, name: "Liege of the Primordial 56461 (Elementalist)", slot: tree, role: sustains, target: self, text: "Summoned Golems are Immune to Elemental Damage; Summoned Golems are Resummoned 4 seconds after being Killed; +2 to maximum number of Summoned Golems. No longer has 50% increased Effect of Buffs granted by your Golems (removed in 3.28.0, so it does not scale buff effect); 3.26.0 raised the count +1 to +2 and added the elemental immunity", source: "TreeData/3_29/tree.lua:50269-50285; wiki Liege of the Primordial rev 1625326; Data/ModCache.lua:932 (ActiveGolemLimit BASE 2, full), 21965 (elemental immunity, parsed), 21966 (resummon, unparsed)", pob: partial}
  - {kind: ascendancy, name: "Ascendant/Elementalist 8281", slot: tree, role: scales, target: self, text: "+1 to maximum number of Summoned Golems", source: "tree-ascendancy-analyst; TREE L18653", pob: partial}
  - {kind: notable, name: "Primordial Bond 57892", slot: tree, role: scales, target: self, text: "10% inc Damage per Summoned Golem; 20% inc Effect of Buffs granted by your Golems", source: "tree-ascendancy-analyst; TREE L87367", pob: partial}
  - {kind: jewel, name: "Primordial Eminence", slot: jewel, role: scales, target: self, text: "30% increased Effect of Buffs granted by your Golems; Golems (16-20)% increased Attack and Cast Speed", source: "PoB Data/Uniques/jewel.lua:548-549; ModParser.lua:478", pob: full}
  - {kind: unique, name: "Brinerot Mark", slot: ring, role: scales, target: self, text: "25% increased Effect of Buffs granted by Socketed Golem Skills; +3 to Level of Socketed Golem Gems (needs the golem gem socketed in it)", source: "PoB Data/Uniques/ring.lua:202-205; ModParser.lua:479", pob: full}
  - {kind: unique, name: "Clayshaper / The Anima Stone", slot: mace, role: scales, target: self, text: "+1 max golem (ActiveGolemLimit)", source: "PoB Data/Uniques/mace.lua:76, jewel.lua:19-20; ModParser.lua:628-629", pob: full}
makes_redundant: []
conflicts:
  - {with: "golem skill count above ActiveGolemLimit", effect: "PoB still adds every enabled golem's buff but only 'limit' golems can exist in game", source: "pob-coverage-auditor (CalcPerform.lua:1446-1448); 021-gate1 N5"}
conditions:
  - {text: "buff applies only while the golem is alive; golems die and need a recast (summon cooldown 6 s); with Liege the golem is resummoned 4 s after death, and the buffs are not active while the golems are dead", source: "skill-gem-analyst; wiki Liege of the Primordial rev 1625326"}
  - {text: "base limit is one active golem; when the player has several of the same golem their buffs do not stack (Summon Carrion Golem has no buff)", source: "wiki Golem rev 1702428"}
  - {text: "enforce golem count <= ActiveGolemLimit in the generator (Worb: 1 base + Golem Commander + Liege = 4)", source: "021-gate1 N5"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "Always while golems are alive; PoB applies the buff if the skill group is enabled", source: "build-strategist table"}
  Pinnacle Boss: {value: partial, config: {}, reasoning: "Golems die to boss one-shots and need respawn (6 s cooldown): buff lost until recast. Liege resummons after 4 s, so the buff is off for at least 4 s per death; PoB has no model for the resummon (unparsed line), use a scenario input. Elemental immunity helps against elemental damage; physical and chaos still kill golems. High where the golems survive", source: "build-strategist table; TreeData/3_29/tree.lua:50269-50285; Data/ModCache.lua:21966; b1-tree-ascendancy-analyst.md"}
seeds: [Worb, Fireball]
sources:
  - {ref: "PoB CalcPerform.lua:1443-1448, SkillStatMap.lua:1991, 2086-2093, ModParser.lua:478-485, 4443-4445", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/Skills act_dex/act_int/act_str.lua golem rows", kind: pob, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Golem (rev 1702428; base limit 1, same golems do not stack; limit sources listed in not_verified)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Liege_of_the_Primordial (rev 1625326; 3.28.0 no longer 50% increased buff effect; 3.26.0 count +2 and elemental immunity)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Golem_Commander (rev 1343723; 3.16.0)", kind: wiki, patch: "3.29"}
  - {ref: "tasks/reports/021-gate1.md N5", kind: discovery, patch: "3.29"}
not_verified:
  - "Further golem limit sources per wiki Golem rev 1702428 that are not providers here and whose PoB parse was not read: of Hordes transfigured gems (+2), Foulborn Midnight Bargain (+2, +4 dual wielding), The Primordial Chain (+3, +4 corrupted), Congregation Support; the same page lists Clayshaper as +1 (+2 dual wielded), The Anima Stone +1 (3+ Primordial items) and Dark Monarch doubling (helmet, variant 2 only: Maximum number of Summoned Golems is Doubled, PoB Data/Uniques/helmet.lua:852, parse partial; moved out of the providers to keep the list at 12)"
  - "Liege resummon has no PoB figure (unparsed line, ModCache.lua:21966); no PoB run of Worb with the 4 golems; the effect of the 6 s summon cooldown against the 4 s resummon in a boss fight is not modelled"
  - "Golem survival and recast uptime"
  - "Whether any listed item beats the tree/ascendancy golem sources (no PoB run)"
open_questions:
  - "None."
```
