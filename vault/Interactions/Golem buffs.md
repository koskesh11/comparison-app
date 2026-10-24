---
type: interaction
status: draft
pob_refs: [ActiveGolemLimit, base_number_of_golems_allowed, golem_buff_effect_+%, HaveColdGolem]
source: "PoB 2.67.2 CalcPerform.lua:1443-1448 / SkillStatMap.lua:1991, 2089 / ModParser.lua:478-485, 4443; skill-gem-analyst, tree-ascendancy-analyst, item-analyst (task 027); tasks/reports/021-gate1.md N5"
last_confirmed_patch: "3.29.x"
---

Each summoned golem skill gives the player a buff while the golem lives. PoB applies the buff of every enabled golem skill but does NOT enforce the golem limit (the limit is only parsed and shown), so enforcing count <= limit is the app's job: [[Golem count within limit]] (task 021, not merged). The Worb seed runs 4 golems = 1 base + Golem Commander + Liege of the Primordial (+2).

```interaction
id: golem-buffs
mechanic: "Summoned golems grant the player a buff each (crit, speed, damage, defence); the number of golems is capped by ActiveGolemLimit; golem buff effect is scaled by 'effect of buffs granted by your golems'"
family: buff
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
model: null
providers:
  - {kind: gem, name: "Summon Ice Golem", slot: gem, role: enables, target: self, text: "+40% increased Critical Strike Chance, +420 accuracy (L20); sets Condition HaveColdGolem", source: "PoB act_dex.lua:15693-15757", pob: full}
  - {kind: gem, name: "Summon Lightning Golem", slot: gem, role: enables, target: self, text: "+10% attack and cast speed, +1081 mana regen per minute (L20)", source: "PoB act_int.lua:19183-19248", pob: full}
  - {kind: gem, name: "Summon Flame Golem", slot: gem, role: enables, target: self, text: "+29% increased Damage, +20% increased Area of Effect (L20)", source: "PoB act_str.lua:11383-11447", pob: full}
  - {kind: gem, name: "Summon Stone Golem", slot: gem, role: enables, target: self, text: "+6300 life regeneration per minute, +20% defences (L20)", source: "PoB act_str.lua:11629-11694", pob: full}
  - {kind: gem, name: "Summon Chaos Golem", slot: gem, role: enables, target: self, text: "+16 DoT multiplier, +17% chaos resistance (L20)", source: "PoB act_int.lua:18767-18831", pob: full}
  - {kind: notable, name: "Golem Commander 34506", slot: tree, role: scales, target: self, text: "40% increased Effect of Buffs granted by your Golems; +1 to maximum number of Summoned Golems", source: "tree-ascendancy-analyst; TREE L57171", pob: partial}
  - {kind: ascendancy, name: "Liege of the Primordial 56461 (Elementalist)", slot: tree, role: scales, target: self, text: "Golems immune to Elemental Damage; resummoned 4 s after being killed; +2 to maximum number of Summoned Golems", source: "tree-ascendancy-analyst; TREE L50276", pob: partial}
  - {kind: ascendancy, name: "Ascendant/Elementalist 8281", slot: tree, role: scales, target: self, text: "+1 to maximum number of Summoned Golems", source: "tree-ascendancy-analyst; TREE L18653", pob: partial}
  - {kind: notable, name: "Primordial Bond 57892", slot: tree, role: scales, target: self, text: "10% inc Damage per Summoned Golem; 20% inc Effect of Buffs granted by your Golems", source: "tree-ascendancy-analyst; TREE L87367", pob: partial}
  - {kind: jewel, name: "Primordial Eminence", slot: jewel, role: scales, target: self, text: "30% increased Effect of Buffs granted by your Golems; Golems (16-20)% increased Attack and Cast Speed", source: "PoB Data/Uniques/jewel.lua:548-549; ModParser.lua:478", pob: full}
  - {kind: unique, name: "Brinerot Mark", slot: ring, role: scales, target: self, text: "25% increased Effect of Buffs granted by Socketed Golem Skills; +3 to Level of Socketed Golem Gems (needs the golem gem socketed in it)", source: "PoB Data/Uniques/ring.lua:202-205; ModParser.lua:479", pob: full}
  - {kind: unique, name: "Clayshaper / The Anima Stone", slot: mace, role: scales, target: self, text: "+1 max golem (ActiveGolemLimit)", source: "PoB Data/Uniques/mace.lua:76, jewel.lua:19-20; ModParser.lua:628-629", pob: full}
  - {kind: unique, name: "Dark Monarch", slot: helmet, role: scales, target: self, text: "Maximum number of Summoned Golems is Doubled (variant 2 only)", source: "PoB Data/Uniques/helmet.lua:852", pob: partial}
makes_redundant: []
conflicts:
  - {with: "golem skill count above ActiveGolemLimit", effect: "PoB still adds every enabled golem's buff but only 'limit' golems can exist in game", source: "pob-coverage-auditor (CalcPerform.lua:1446-1448); 021-gate1 N5"}
conditions:
  - {text: "buff applies only while the golem is alive; golems die and need a recast (summon cooldown 6 s)", source: "skill-gem-analyst"}
  - {text: "enforce golem count <= ActiveGolemLimit in the generator (Worb: 1 base + Golem Commander + Liege = 4)", source: "021-gate1 N5"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "Always while golems are alive; PoB applies the buff if the skill group is enabled", source: "build-strategist table"}
  Pinnacle Boss: {value: partial, config: {}, reasoning: "Golems die to boss one-shots and need respawn (6 s cooldown): buff lost until recast. Liege resummons after 4 s. High where the golems survive", source: "build-strategist table; Liege of the Primordial TREE L50276"}
seeds: [Worb]
sources:
  - {ref: "PoB CalcPerform.lua:1443-1448, SkillStatMap.lua:1991, 2086-2093, ModParser.lua:478-485, 4443-4445", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/Skills act_dex/act_int/act_str.lua golem rows", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/021-gate1.md N5", kind: discovery, patch: "3.29"}
not_verified:
  - "Base golem limit 1 from the wiki Golem page (not fetched; PoB data only)"
  - "Golem survival and recast uptime"
  - "Whether any listed item beats the tree/ascendancy golem sources (no PoB run)"
open_questions:
  - "None."
```
