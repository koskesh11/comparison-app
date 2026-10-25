---
type: interaction
status: draft
pob_refs: [ActiveTotemLimit, TotemsSummoned, TotemPlacementTime, TotemPlacementSpeed, TotemDuration, TotemActionSpeed, TotalDPS, Speed, SummonsTotem]
source: "poewiki Totem rev 1703193 (fetched 2026-10-25); PoB 2.67.2 Modules/CalcOffence.lua, Calcs.lua, CalcPerform.lua, CalcSetup.lua, ConfigOptions.lua, ModParser.lua, Data/SkillStatMap.lua, Data/Skills/sup_str.lua, Data/Uniques, TreeData/3_29/tree.lua; evidence skill-gem-analyst-uptime.md, pob-coverage-auditor-uptime.md (task 027)"
last_confirmed_patch: "3.29.x"
---

A totem is an object that uses ONE of your skills with YOUR stats and then fires on its own. The totem limit is 1 by default (global); each extra totem fires independently. PoB shows TotalDPS for ONE totem and does not multiply it by the number of totems, by the totem duration or by the placement time, so a build with 3 totems is under-reported by PoB unless the count is applied outside PoB. Totems cannot be triggered, take no Cast on Critical Strike, Cast when Damage Taken or exert (see [[Cast when damage taken]] and [[Warcries]]), and a Spell Totem Support costs 50% less damage and 40% less cast speed at L20 as the price of the delivery.

Pipeline: [[Damage calculation#Hit rate]] - DPS = average hit x hits per second per totem (CalcOffence.lua:3801); the totem count is not part of that product in PoB, so it has to be applied on top. The support gems' final damage and speed enter as [[Damage calculation#More and less]]. For on-hit chance effects that totem hits apply to the enemy (freeze, shock, exposure chance) use [[Chance on hit uptime]] with H = hits per second summed over the live totems.

```interaction
id: totems
mechanic: "A totem is a proxy that uses one of the player's skills with the player's stats (no snapshot); default limit 1 active totem (global), each extra totem fires its own uses; base placement 0.6 s (ballista 0.5 s), then an emergence delay before it can act; the totem lives for its duration (8 s for Spell Totem and Ballista Totem Support) and dies with the player; PoB TotalDPS is per totem"
family: uptime
target: self
related: [traps-and-mines, cast-when-damage-taken, warcries, chance-on-hit-uptime, coc-trigger]
pipeline_step: ["Damage calculation#Hit rate", "Damage calculation#More and less"]
pipeline_why: "PoB TotalDPS = AverageDamage x (HitSpeed or Speed) x dpsMultiplier x quantityMultiplier (CalcOffence.lua:3801); none of these carries the totem count, so N totems must be applied outside PoB. Spell Totem and Ballista Totem Support are final 'less damage' and 'less speed' multipliers (Data/Skills/sup_str.lua:4514,5035)"
pob:
  measured: partial
  how: "Per-totem rate only. Totem flag from addFlags totem and ballista (sup_str.lua:4514,5035). Limit = ActiveTotemLimit, summed from base 1 (CalcSetup.lua:61), gem stats base_number_of_totems_allowed, number_of_additional_totems_allowed and attack_skills_additional_ballista_totems_allowed (SkillStatMap.lua:1876-1884) and parsed mods (ModParser.lua:599-602,4404-4405) at CalcOffence.lua:1433; TotemsSummoned = config override or the limit (1434, ConfigOptions.lua:1123-1124) and feeds only 'per Summoned Totem' mods (ModParser.lua:1537-1540, 4413) and bleed stack potential x activeTotems (CalcOffence.lua:4451-4453). Placement time base 0.6 s and ballista 0.5 s (CalcSetup.lua:59-60) is displayed, Speed gets TotemActionSpeed (2414-2419), TotemDuration is computed and displayed (1624-1637) but neither duration, placement nor emergence reduces DPS; only skills with totemFireOnce use placement time in HitTime (2420-2423). TotalDPS has no totem factor (3801); FullDPS multiplies by the gem GROUP count, not the totem count (Calcs.lua:253-255). Totems are excluded from exert (CalcOffence.lua:2628-2629)"
  config:
    - {var: TotemsSummoned, default: "maximum (ActiveTotemLimit)", ref: "Modules/ConfigOptions.lua:1123-1124 (affects every 'per Summoned Totem' modifier, even for non-totem skills; implies HaveTotem)", class: b}
  unparsed: []
model:
  proposed_kind: totem_dps_scale
  inputs: {from_pob: [TotalDPS, ActiveTotemLimit, TotemsSummoned, TotemDuration, TotemPlacementTime, Speed], from_scenario: ["R = share of the fight the target stands inside the totem's range (class b)", "resummon policy: replace at expiry or keep the oldest alive (class b)"]}
  params: {base_placement_s: 0.6, ballista_placement_s: 0.5, spell_and_ballista_duration_s: 8, spell_totem_range_m_wiki: 7, emergence_s_spell_totem_wiki: 0.66}
  formula: "real DPS = TotalDPS(PoB, one totem) x N x u. N = min(ActiveTotemLimit, totems the player keeps placed); u = R x (D - e) / D with D = TotemDuration (8 s base, only Totem Duration scales it, not skill effect duration) and e = emergence delay (wiki: about 0.66 s default for Spell Totem Support; since 3.28.0 placement speed scales it) when the totem is replaced exactly at expiry; filling N totems costs N x TotemPlacementTime of player time. Round the result down. All per-totem hits count for hit-rate effects: H = N x per-totem hit rate (see Chance on hit uptime)"
  calibration: "no norm found; the emergence value is 'appears to be' in the wiki and the 7 m range is quoted for Spell Totem Support (wiki Totem rev 1703193)"
providers:
  - {kind: support, name: "Spell Totem Support", slot: any, role: enables, target: self, text: "summon a totem that casts the spell for you; L20 50% less damage and 40% less cast speed (final), base duration 8000 ms, range 60; needs a spell skill that is not triggered; skills cost nothing when used by the totem", source: "Data/Skills/sup_str.lua:5035; wiki Totem rev 1703193", pob: full}
  - {kind: support, name: "Ballista Totem Support", slot: any, role: enables, target: self, text: "bow or wand attack summons a ballista totem; L20 30% less damage, 50% less attack speed, +2 ballista totems allowed, base duration 8000 ms", source: "Data/Skills/sup_str.lua:4514; Data/SkillStatMap.lua:1879-1881", pob: full}
  - {kind: support, name: "Multiple Totems Support", slot: any, role: scales, target: self, text: "+2 totems allowed for the supported skill (base_number_of_totems_allowed 2); L20 21% less damage", source: "Data/Skills/sup_str.lua:3884; Data/SkillStatMap.lua:1882-1884", pob: full}
  - {kind: keystone, name: "Ancestral Bond", slot: tree, role: enables, target: self, text: "You can't deal Damage with Skills yourself; +1 to maximum number of Summoned Totems (all damage must then come from totems)", source: "TreeData/3_29/tree.lua:25677", pob: full}
  - {kind: ascendancy, name: "Pursuit of Faith (Hierophant)", slot: tree, role: scales, target: self, text: "+1 to maximum number of Summoned Totems", source: "TreeData/3_29/tree.lua:15947", pob: full}
  - {kind: ascendancy, name: "Hierophant (Ascendant)", slot: tree, role: scales, target: self, text: "+1 to maximum number of Summoned Totems; Gain Arcane Surge when you or your Totems Hit an Enemy with a Spell", source: "TreeData/3_29/tree.lua:17890", pob: full}
  - {kind: unique, name: "Tukohama's Fortress", slot: Shield, role: scales, target: self, text: "+1 to maximum number of Summoned Totems; 40% increased Totem Damage (variant 1 and 2 add +300 Armour per Summoned Totem)", source: "Data/Uniques/shield.lua:201-210", pob: full}
  - {kind: unique, name: "The Crustacean's Call", slot: Staff, role: scales, target: self, text: "+2 to maximum number of Summoned Totems; socketed spells supported by level 20 Crab Totem; totems have 100% increased movement speed", source: "Data/Uniques/staff.lua:191-199", pob: full}
  - {kind: unique, name: "Cadigan's Authority", slot: Sceptre, role: scales, target: self, text: "+(3-5) to maximum number of Summoned Totems, but you cannot have more than 2 Summoned Totems of the same type; (40-70)% increased Totem Placement speed", source: "Data/Uniques/mace.lua:691-700", pob: partial}
  - {kind: unique, name: "Skirmish", slot: Quiver, role: scales, target: self, text: "Attack skills can have 1 additional Totem Summoned at a time", source: "Data/Uniques/quiver.lua:282-291; Modules/ModParser.lua:4405", pob: full}
  - {kind: unique, name: "Soul Mantle", slot: Body Armour, role: scales, target: self, text: "+1 to maximum number of Summoned Totems (variants 1-4, i.e. before 3.17.0 in the wiki; not in Current); socketed Spell Totem; random Hex on you when your Totems die", variant: "variants 1-4 (Current has no extra totem)", source: "Data/Uniques/body.lua:704-719; wiki Totem rev 1703193 (legacy Soul Mantle before 3.17.0)", pob: full}
  - {kind: unique, name: "Iron Commander", slot: Bow, role: scales, target: self, text: "Siege Ballista has +1 to maximum number of Summoned Totems per 200 Dexterity; (14-20)% increased Totem Placement speed", source: "Data/Uniques/bow.lua:283-293", pob: full}
makes_redundant: []
conflicts:
  - {with: "Runebinder (keystone)", effect: "-1 to maximum number of Summoned Totems (and an extra Brand)", source: "TreeData/3_29/tree.lua:28565; wiki Totem rev 1703193"}
  - {with: "Conjoined Spire (Abyssal Bloodline)", effect: "All other Summoned Totems die when you Summon a Totem: the limit stays 1 regardless of maximum totems, and bonuses scale with the maximum instead (10% more damage and area per maximum totem, 5% more life)", source: "TreeData/3_29/tree.lua:12742-12746; wiki Totem rev 1703193"}
  - {with: "Cast on Critical Strike, Cast when Damage Taken, other trigger supports", effect: "totems cannot be triggered and the supports exclude SummonsTotem; skills that summon a totem cannot be triggered", source: "Data/Skills/sup_str.lua:1153; Data/Skills/sup_dex.lua:519-527; wiki Totem rev 1703193"}
  - {with: "Warcry exerted attacks", effect: "attacks used by proxies such as totems cannot be exerted", source: "Modules/CalcOffence.lua:2628-2629; wiki Exerting rev 1660569"}
conditions:
  - {text: "By default a player can have one active totem; it is a global limit among all skills; summoning past the limit destroys the oldest. Sources add to the global limit or to specific skills only", source: "wiki Totem rev 1703193 'Totem limit'"}
  - {text: "The totem uses the player's stats, not its own; changes to player stats immediately affect it (no snapshot); skills cost nothing when used by totems; hits and their on-hit effects (leech, reflect) belong to the totem, not the player", source: "wiki Totem rev 1703193 'Offensive stats'"}
  - {text: "Totem duration is affected only by Totem Duration modifiers, not Skill Effect Duration; totems summoned by the player die when the player dies (3.21.0)", source: "wiki Totem rev 1703193; version history 3.21.0"}
  - {text: "Totem Placement speed also scales the speed at which totems emerge (3.28.0); ranged attack totems have a base placement speed of 0.5 s (was 0.35 s)", source: "wiki Totem rev 1703193 version history 3.28.0; PoB CalcSetup.lua:60"}
  - {text: "Totems have 80% less damage taken from enemies, take full damage from self-damage (3.16.0), base 40% elemental and 20% chaos resistance; they do not inherit player defences", source: "wiki Totem rev 1703193 'Defensive stats' and 3.16.0"}
uptime:
  Mapping:       {value: model, config: {TotemsSummoned: "set to the number of totems the build keeps placed (default = limit)"}, reasoning: "PoB assumes the totem fires without gaps and never reports duration, placement or emergence loss; against packs R is high because the pack walks into range, but a stationary totem loses uptime when the player moves on, which no source quantifies", source: "Modules/CalcOffence.lua:1433-1434,1624-1637,3801; wiki Totem rev 1703193"}
  Pinnacle Boss: {value: model, config: {TotemsSummoned: "as above; the model multiplies per-totem DPS by N and u"}, reasoning: "a single boss moves, so R (inside totem range) is the unknown: no norm found; N totems multiply DPS in the game while PoB shows one", source: "Modules/CalcOffence.lua:3801; evidence skill-gem-analyst-uptime.md"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Totem (rev 1703193, fetched 2026-10-25); version history 2.0.0, 3.0.0, 3.10.0, 3.16.0, 3.21.0, 3.28.0", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Exerting (rev 1660569)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcOffence.lua:1413-1454,1624-1637,2414-2423,2628-2629,3801,4451-4453; Modules/Calcs.lua:253-255; Modules/CalcPerform.lua:1371-1374; Modules/CalcSetup.lua:59-61; Modules/ConfigOptions.lua:1123-1124; Data/SkillStatMap.lua:1866-1887 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "Data/Skills/sup_str.lua:3884,4514,5035; Data/Uniques/{shield,staff,mace,quiver,body,bow}.lua; TreeData/3_29/tree.lua:12742,15947,17890,25677,28565", kind: pob, patch: "3.29"}
not_verified:
  - "whether player-side 'when you hit' conditions fire on totem hits: the wiki says the hits belong to the totem and on-hit effects affect the totem; the Hierophant line 'you or your Totems Hit' suggests they do not by default, but no source states the condition semantics"
  - "the emergence delay (about 0.66 s) and the 7 m Spell Totem range are 'appears to be' / 'approximately' in the wiki; PoB has neither"
  - "that the PoB TotalDPS of a totem with TotemsSummoned = N is still one totem in every case (read the product at CalcOffence.lua:3801; no build with several totems was run)"
  - "whether PoB parses Cadigan's Authority 'cannot have more than 2 Summoned Totems of the same type' (the item line was read, the parser was not checked); whether Conjoined Spire changes PoB totem damage was not traced"
  - "the unit of base_totem_range 60 in the gem data (the wiki gives metres for the Spell Totem Support only)"
open_questions:
  - "Should the generator multiply a totem skill's DPS by the totem count itself (outside PoB), and with which uptime factor u, when comparing a totem build with a self-cast build?"
```
