---
type: interaction
status: draft
pob_refs: [Armour, Evasion, PhysicalMaximumHitTaken, TotalEHP, ManaReservedPercent, ManaReserved, ManaUnreserved, ManaUnreservedPercent, AuraEffect, conditionAffectedByDetermination]
source: "poewiki Determination rev 1681683, Grace rev 1681682, Damage taken as rev 1618416 (fetched 2026-10-26); PoB 2.67.2 Data/Skills act_str.lua / act_dex.lua, CalcPerform.lua, ModParser.lua, Data/Uniques/Special/WatchersEye.lua; headless probes on 3.29\\Ninja Builds\\CoC EK Assa.xml and 3.29\\Worb.xml (b1b-mechanics-researcher.md D, b1b-pob-coverage-auditor.md determination-grace, b1b-skill-gem-analyst.md 1, 2, 5, 6)"
last_confirmed_patch: "3.29.x"
---

Determination is an aura that gives more armour plus flat armour (L20: 49% more Armour and +1,026); Grace gives more evasion plus flat evasion (L20: 29% more Evasion and +1,545). Each reserves 50% of mana at the gem; PoB applies the aura whenever the gem and its group are enabled, with no config tick. Armour feeds the physical max hit (a diminishing-returns lever, see [[Armour and physical max hit]]); evasion does not enter PhysicalMaximumHitTaken, it only raises TotalEHP. This note covers what the two gems give and their item lines; generic aura and reservation rules belong to the reservation notes.

Pipeline: Determination - [[Receiving damage#Armour and damage reduction]] (armour acts after damage-taken-as and resistance); Grace - [[Receiving damage#Preventing the hit]] (evasion makes a hit miss before any mitigation); the Watcher's Eye lines act at [[Receiving damage#Spell suppression]] and [[Receiving damage#Block]]

```interaction
id: determination-grace
mechanic: "Determination: aura, L20 49% more Armour and +1,026 flat Armour; Grace: aura, L20 29% more Evasion and +1,545 flat Evasion; both reserve 50% of mana at the gem and are on whenever the gem is enabled; the flat part is also scaled by aura effect"
family: buff
pipeline_step: ["Receiving damage#Armour and damage reduction", "Receiving damage#Preventing the hit"]
pipeline_why: "Determination raises armour, which acts after damage-taken-as and resistance on the hit; Grace raises evasion, which acts first (chance to avoid the hit) and is not part of the physical max hit chain"
target: self
related: [armour-phys-max-hit, flat-physical-damage-reduction, physical-taken-as-elemental, spell-suppression, block]
pob:
  measured: partial
  how: "Gem data (Data/Skills): Determination L20 determination_aura_armour_+%_final 49 = Armour MORE and base_physical_damage_reduction_rating 1,026 (flat armour), manaReservationPercent 50 at every level, cast cooldown 1.2 (act_str.lua:2640-2700, rows 2696-2697); Grace L20 29% more Evasion and 1,545 flat Evasion, reservation 50% (act_dex.lua:8922-8980, rows 8978-8979). Both are GlobalEffect Aura mods (MORE and BASE), so increased armour or evasion applies to the flat part and aura effect scales both (CalcPerform.lua:2462-2464). Gate: auras apply when env.mode_buffs (CalcPerform.lua:2444-2445; main output buffMode EFFECTIVE, CalcSetup.lua:565-575); no Determination or Grace entry in ConfigOptions.lua (grep: no match). Item lines 'while affected by Determination / Grace' = condition AffectedBy<Name>, set when the aura is active (ModParser.lua:6118, CalcPerform.lua:2469-2471). Reservation output keys: per skill activeSkill.skillData.ManaReservedPercent / ManaReservedBase (CalcPerform.lua:2063-2066); totals ManaReserved, ManaReservedPercent (capped at the pool, 100), ManaUnreserved, ManaUnreservedPercent (NOT capped, goes negative, no skill is disabled) (CalcPerform.lua:564-567). PoB leaves out: Grace's evasion in the physical max hit (the chain has no evasion term, CalcDefence.lua:3208-3266), the Blind lines of Grace and Watcher's Eye (unparsed), the Anomalous / Divergent / Phantasmal alternate qualities (PoB has none: grep 'Anomalous' in Data, Modules, Classes finds no file), quality 20 gives only +40% area (base_skill_area_of_effect_+% 2 per 1%, SkillStatMap.lua:572), which changes who the aura reaches, not your own armour or evasion."
  config: []
  unparsed:
    - "Watcher's Eye: (30-50)% chance to Blind Enemies which Hit you while affected by Grace (Data/ModCache.lua:9228,10083 return an empty mod list)"
    - "Watcher's Eye: Prevent +(50-75)% of Reflected Physical Damage you would take while affected by Determination (Data/ModCache.lua:18648)"
model: null
providers:
  - {kind: gem, name: "Determination", slot: any, role: scales, target: self, text: "aura: L20 49% more Armour and +1,026 Armour (L21 50% more, +1,077); reserves 50% of mana at every gem level; Str 155 (159 at L21)", source: "Data/Skills/act_str.lua:2640-2700; poewiki Determination rev 1681683", pob: full}
  - {kind: gem, name: "Grace", slot: any, role: scales, target: self, text: "aura: L20 29% more Evasion and +1,545 Evasion (L21 30% more, +1,620); reserves 50% of mana; Dex 155 (159 at L21); wiki 3.25.0: 136 additional Evasion at gem level 1 up to 1,545 at level 20", source: "Data/Skills/act_dex.lua:8922-8980; poewiki Grace rev 1681682", pob: full}
  - {kind: unique, name: "Watcher's Eye (Determination lines)", slot: jewel, role: scales, target: self, text: "(5-8)% additional Physical Damage Reduction, +(600-1000) to Armour, +(5-8)% Chance to Block Attack Damage, (40-60)% reduced Extra Damage from Critical Strikes, Unaffected by Vulnerability, Prevent +(50-75)% of Reflected Physical Damage (unparsed), all while affected by Determination", source: "Data/Uniques/Special/WatchersEye.lua:5-10", pob: partial}
  - {kind: unique, name: "Watcher's Eye (Grace lines)", slot: jewel, role: scales, target: self, text: "+(5-8)% chance to Evade Attack Hits, +(12-15)% chance to Suppress Spell Damage, Unaffected by Enfeeble, (10-15)% increased Movement Speed, (30-50)% chance to Blind Enemies which Hit you (unparsed), all while affected by Grace; suppression is the useful line for a spell build", source: "Data/Uniques/Special/WatchersEye.lua:11-15", pob: partial}
  - {kind: unique, name: "Sublime Vision (Watcher's Eye variants)", slot: jewel, role: scales, target: self, text: "Auras from your Skills have (20-40)% increased Effect on you; +1 to Maximum Endurance Charges while affected by Determination; Aura Skills other than Determination are Disabled (Grace variant: +1 Maximum Frenzy Charges)", source: "Data/Uniques/Special/WatchersEye.lua:95,97", pob: partial}
  - {kind: mod, name: "Eater of Worlds body implicit", slot: body armour, role: scales, target: self, text: "Determination has (19-36)% increased Aura Effect (6 tiers; Grace has the same set), weight 300 on body armour", source: "Data/ModEldritch.lua:3785-3790,3803", pob: full}
  - {kind: mod, name: "Corrupted amulet mod", slot: amulet, role: scales, target: self, text: "Determination has (20-30)% increased Aura Effect", source: "Data/ModCorrupted.lua:353", pob: full}
  - {kind: mod, name: "Crucible weapon-tree mod", slot: shield, role: scales, target: self, text: "Determination has 20% / 25% / 30% increased Aura Effect, and Determination has 25% increased Reservation", source: "Data/Crucible.lua:1855-1857", pob: full}
  - {kind: unique, name: "String of Servitude", slot: belt, role: scales, target: self, text: "Determination has (45-60)% increased Aura Effect (one variant) / Grace has (45-60)% increased Aura Effect (one variant)", source: "Data/Uniques/belt.lua:916,918", pob: full}
  - {kind: unique, name: "Aul's Uprising", slot: amulet, role: enables, target: self, text: "Determination has no Reservation / Grace has no Reservation (variants)", source: "Data/Uniques/amulet.lua:166,169", pob: full}
  - {kind: keystone, name: "Iron Reflexes with Grace", slot: tree, role: scales, target: self, text: "Grace can also be used with Iron Reflexes to gain armour instead of evasion (wiki); PoB handling not checked", source: "poewiki Grace rev 1681682", pob: none}
makes_redundant: []
conflicts:
  - {with: "Grace and the physical max hit", effect: "Grace's evasion adds to TotalEHP (Worb +14,724, EK +15,228) but nothing to PhysicalMaximumHitTaken, because the max-hit chain has no evasion term", source: "Modules/CalcDefence.lua:3208-3266; b1b-pob-coverage-auditor.md measurements"}
  - {with: "Generosity Support", effect: "aura_cannot_affect_self (Awakened Generosity too): the aura no longer affects you, useless for own defence", source: "b1b-skill-gem-analyst.md 7 (Data/Skills sup_int.lua)"}
  - {with: "Sublime Vision and other auras", effect: "Aura Skills other than Determination are Disabled: the Fireball seed's Herald of Ash would be disabled", source: "Data/Uniques/Special/WatchersEye.lua:95; Data/Skills/act_str.lua"}
  - {with: "Watcher's Eye legacy lines", effect: "wiki: all Watcher's Eye modifiers of the old kind no longer roll since 3.25.0; PoB's Special file still lists them (treated as legacy here)", source: "poewiki Damage taken as rev 1618416 (3.25.0); Data/Uniques/Special/WatchersEye.lua:58-78"}
  - {with: "alternate qualities", effect: "the wiki still lists Anomalous, Divergent and Phantasmal qualities for both gems (Determination: 0.25% stun avoidance, 0.1% of evasion as extra armour; Grace: 0.1% ailment avoidance, 0.05% avoid chaos hit damage, per 1% quality; 3.12.0-3.13.0 rows); PoB has none, so they are never scored", source: "b1b-skill-gem-analyst.md 2; poewiki Determination rev 1681683, Grace rev 1681682"}
conditions:
  - {text: "aura effect (for example EK's +30%) scales the gem's stats, so use the real gem and not custom mods: EK gem Armour 4,554, phys max 8,500, TotalEHP 173,695 versus custom mods '+1026 to Armour' and '49% more Armour' Armour 3,166, 8,177, 163,889; Worb is identical either way", source: "Modules/CalcPerform.lua:2462-2464; b1b-pob-coverage-auditor.md (probe_ek_aura)"}
  - {text: "reservation: the gem reserves 50% at every gem level; the auditor's 44.64% (Worb, 607 of 1,359 mana) and 36.76% (EK, 442 of 1,201) per aura are AFTER each build's own reservation mods, not 50% x gem", source: "Data/Skills/act_str.lua:2677-2697; Modules/CalcPerform.lua:2063-2066; b1b-skill-gem-analyst.md section 5.4"}
  - {text: "adding either aura to a build whose mana is already reserved can push ManaUnreserved negative (Worb 145 to -461 with both; EK 107 to -334) without disabling any skill: the generator must read ManaUnreserved", source: "Modules/CalcPerform.lua:564-567; b1b-pob-coverage-auditor.md"}
  - {text: "Grace's Blind line: spells always hit, so it does nothing against caster monsters; no config box for it (conditionEnemyBlinded is the generic tick); hit rate, Blind duration and uptime per scenario were not measured (Blind base duration 4 s and 20% less accuracy / evasion are in the vault Blind note)", source: "vault Blind; b1b-mechanics-researcher.md D"}
uptime:
  Mapping:
    value: always
    config: {}
    reasoning: "an aura is on while the gem is enabled and reserved; PoB applies it with no config tick"
    source: "Modules/CalcPerform.lua:2444-2445"
  Pinnacle Boss:
    value: always
    config: {enemyIsBoss: "Pinnacle (default index 3)"}
    reasoning: "same uptime; Determination's armour is worth less against the larger boss hit (DR = A/(A+5D)); Grace's evasion is not in the physical max hit at all"
    source: "Modules/ConfigOptions.lua:2086-2115; vault Armour and physical max hit"
seeds: [EK, Worb, Fireball]
sources:
  - {ref: "https://www.poewiki.net/wiki/Determination (rev 1681683); Grace (rev 1681682)", kind: wiki, patch: "3.29"}
  - {ref: "Data/Skills/act_str.lua:2640-2700; Data/Skills/act_dex.lua:8922-8980; Modules/CalcPerform.lua:564-567,2063-2066,2444-2471; Modules/ModParser.lua:6118; Data/Uniques/Special/WatchersEye.lua (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b1b-mechanics-researcher.md (D); b1b-pob-coverage-auditor.md (determination-grace, measurements); b1b-skill-gem-analyst.md (1, 2, 5, 6)", kind: discovery, patch: "3.29"}
not_verified:
  - "measured (auditor probes, my added L20 gem, no quality, rolled back): Worb Determination Armour 4,715 to 9,105, PhysicalMaximumHitTaken 16,310 to 17,149 (+839), TotalEHP 76,837 to 84,321; Grace Evasion 1,482 to 5,100, phys max unchanged, TotalEHP 91,561; EK Determination Armour 658 to 4,554, phys max 7,538 to 8,500 (+962), TotalEHP 145,259 to 173,695; Grace Evasion 14,082 to 27,230, TotalEHP 160,487"
  - "reservation per skill after each build's mods (not 50% x gem): Worb Determination and Grace 44.64% = 607 mana each, the 4 auras already there 22.32% / 304 each, ManaUnreserved 145 to -461; EK 36.76% = 442 each, Pride 29.49% / 355, Clarity 156, ManaUnreserved 107 to -334; 3.29\\CoC\\Goal.xml Grace L20 q20 38.76% / 407 mana, Evasion 22,087, ManaUnreserved 92; V1.xml Grace L19 41.32% / 404, ManaUnreserved 52; no 3.29 build contains Determination"
  - "derived, not a PoB output: with 5,000 base armour, (5,000 + 1,026) x 1.49 = 8,979 (+3,979 armour) is worth about +330 to +660 physical max hit at the vault slope (+83 per 1,000 armour at 24.8k, +166 at 0-5k)"
  - "EK TotalDPS rose 1.1% (7,728,445 to 7,815,414) when the aura groups were added; cause not looked up"
  - "supports on the auras for the Fireball seed (Enlighten, Arrogance reserving Life on a 3,000 Life seed, Cooldown Recovery) were listed by a compatibility probe, not run in a build"
  - "whether a Purity-linked Watcher's Eye replaces the legacy lines in 3.29 (wiki 3.25.0 says new Purity modifiers exist)"
  - "Iron Reflexes with Grace: keystone route and PoB handling not checked"
  - "Hit rate for Grace's Blind line, aura-effect scaling of the flat 1,026 in a real run and PoB's PhysicalMaximumHitTaken with these auras on a Fireball build: no build to run"
  - "Name-only matches that are not providers: Kiara's Determination, Kalisa's Grace, The Snowblind Grace, Grace of the Goddess, Graceful Execution, Unholy Grace"
open_questions:
  - "Both auras reserve 50% at the gem; on a Fireball seed with Mind over Matter and Herald of Ash the unreserved mana competes. Which of Determination, Grace and the other seed auras gets the mana is a reservation-note decision (batch 4); this note only gives the PoB output keys."
  - "Should the generator treat the Watcher's Eye lines as live or legacy (wiki 3.25.0 vs PoB's Special file)?"
```
