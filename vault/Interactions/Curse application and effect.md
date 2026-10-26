---
type: interaction
status: draft
pob_refs: [conditionEnemyCursed, conditionCursedEnemyRecently, multiplierCurseExpiredOnEnemy, multiplierCurseDurationExpiredOnEnemy, CurseEffectOnSelf, CurseEffect, CursesIgnoreHexproof, ignoreHexproof, EnemyCurseLimit, Condition:Cursed, CurseOnEnemy, enemyIsBoss]
source: "poewiki Curse rev 1675786, Hexproof rev 1486560, Curse immunity rev 1348384, Mark rev 1647869, Bane rev 1682026, Blasphemy Support rev 1681869, Hextouch Support rev 1681745, Mark On Hit Support rev 1682222, Awakened Hextouch Support rev 1698384, Hexpass Support rev 1682304, Version 3.20.0 rev 1635782; PoB 2.67.2 CalcPerform.lua / ConfigOptions.lua / ModMap.lua / ModParser.lua / ModCache.lua / SkillStatMap.lua / Data/Skills / Data/Uniques / TreeData 3_29; headless probe b3b/curse_probe.py (task 027 batch 3b)"
last_confirmed_patch: "3.29.x"
---

A curse reaches the enemy only if a method applies it, the enemy is not hexproof or curse immune, and a free (or lower-priority) slot exists; then its strength is the curse's own value times your curse effect. Since 3.20.0 bosses no longer reduce curse effect, and none of PoB's four boss presets does (probe: increased 0, more 1 on FR and EK); the real reducers are the Hexwarded map mod and the Hexproof / Immune to Curses mods. How many curses fit is in [[Curse limit]] and is not repeated here. Assassin's Mark values are in [[Assassin's Mark]].

Pipeline: [[Damage calculation#Resistance, exposure and penetration]], [[Damage calculation#Damage taken]] - the curse modifiers land on the enemy as resistance, damage taken, less damage and slow; curse effect scales them before that

```interaction
id: curse-application
mechanic: "A curse applies when a method (self-cast, Blasphemy aura, Hextouch, Mark On Hit, Bane, item) fires, the enemy is not Immune to Curses (absolute) and not Hexproof (hexes only, bypassable; marks ignore it), and a slot is free or the new curse has priority; effect = curse value x (1 + increased) x more, where bosses have NO curse-effect reduction since 3.20.0 but Hexwarded maps have 25/40/60% less"
family: buff
pipeline_step: ["Damage calculation#Resistance, exposure and penetration", "Damage calculation#Damage taken"]
pipeline_why: "curses act through enemy resistance, damage taken, less damage dealt and slow; curse effect scales those values, the application rules only decide whether and when they exist"
target: enemy
related: [curse-limit, assassins-mark]
pob:
  measured: partial
  how: "CalcPerform.lua:2653-2707 builds each curse (effect = (1 + CurseEffect inc + enemy CurseEffectOnSelf inc) x CurseEffect more x enemy CurseEffectOnSelf more); 2662 skips hexes when enemyDB flag Hexproof is set unless CursesIgnoreHexproof / ignoreHexproof; 3178 same for ExtraCurse; slots 3216-3315 with priority (determineCursePriority CalcPerform.lua:587-611, Data.lua:328-352); 3361-3365 sets enemy condition Cursed for any slotted curse. PoB has NO source that sets the enemy Hexproof flag (grep of Modules, Classes, Data: only consumers at CalcPerform.lua:2662, 2934, 3178), so hexproof maps and monsters are not modelled. Hexwarded map mod is modelled (Data/ModMap.lua:24-31). The chance in 'x% chance to Curse non-Cursed Enemies ... on Hit' is dropped (ModCache: ExtraSkill without chance). Probe on the seeds: FR limit 7, 5 slots (Assassin's Mark, Punishment, Despair, Temporal Chains, Enfeeble), enemy CurseEffectOnSelf inc 0 / more 1 under None, Boss, Pinnacle and Uber; EK limit 2, 2 slots (Assassin's Mark, Vulnerability), same 0 / 1"
  config:
    - {var: conditionEnemyCursed, default: false, ref: "Modules/ConfigOptions.lua:1806", class: b}
    - {var: conditionCursedEnemyRecently, default: false, ref: "Modules/ConfigOptions.lua:1601", class: b}
    - {var: multiplierCurseExpiredOnEnemy, default: 0, ref: "Modules/ConfigOptions.lua:1833", class: b}
    - {var: multiplierCurseDurationExpiredOnEnemy, default: 0, ref: "Modules/ConfigOptions.lua:1836", class: b}
    - {var: conditionEnemyOnProfaneGround, default: false, ref: "Modules/ConfigOptions.lua:2017-2021 (enemy curse effect +10% inc)", class: b}
    - {var: "map mod Hexwarded (25/40/60% less curse effect on monsters)", default: none, ref: "Data/ModMap.lua:24-31", class: b}
    - {var: enemyIsBoss, default: Pinnacle, ref: "Modules/ConfigOptions.lua:2086-2222 (no curse effect or Hexproof in any preset)", class: b}
    - {var: balanceOfTerrorSelfCast<CurseName>, default: false, ref: "Modules/CalcPerform.lua:2657-2661 (curse stays on you, skipped for enemies)", class: c}
    - {var: conditionCanBeCurseImmune, default: false, ref: "Modules/ConfigOptions.lua:1225 (you, not the enemy)", class: b}
  unparsed:
    - "Sentari's Answer: Curse Enemies with Punishment / Temporal Chains / Elemental Weakness when you Block ..., ignoring Curse Limit (ModCache: nil mods; the [[Curse limit]] note lists it as pob full)"
    - "Ylfeban's Trickery: Curse Enemies which Hit you with a random Hex, ignoring Curse Limit (ModCache: nil mods)"
    - "Mark of Submission: Curse Enemies with Socketed Hex Curse Gem on Hit (ModCache: empty mod list)"
    - "Ylfeban's Trickery old variants / Asenath's-type '(10-30)% chance to Curse non-Cursed Enemies with a random Hex on Hit': parsed as ExtraSkill without a skill id, so nothing is applied"
model: null
providers:
  - {kind: gem, name: "Despair / Punishment / Temporal Chains / Enfeeble (self-cast hexes)", slot: any, role: applies, target: enemy, text: "cast per pack; each hex has its own duration, then it must be cast again; counts as SelfCast for conditions", source: "CalcPerform.lua:2655, 2662; FR seed slots (probe FR_slots.json)", pob: full}
  - {kind: gem, name: "Assassin's Mark + Mark On Hit (FR seed)", slot: any, role: applies, target: enemy, text: "Mark On Hit triggers the mark when an Attack hits a Rare or Unique enemy (cooldown 4 s in PoB data); marks ignore Hexproof and have no duration; effect values in the Assassin's Mark note", source: "PoB Data/Skills/sup_dex.lua:2970-2985 (cooldown 4, trigger_on_attack_hit_against_rare_or_unique); SkillStatMap.lua:2106; wiki Mark On Hit Support rev 1682222 (3.17.0)", pob: full}
  - {kind: support, name: "Blasphemy", slot: any, role: applies, target: enemy, text: "hex becomes an aura (reserves 35% mana, 1.2 s cooldown on cast), applies to all enemies in its radius, 25% less curse effect; wins slots against self-cast and on-hit curses (priority CurseFromAura 20000); hexes only, not marks", source: "PoB Data/Skills/sup_int.lua:364-412; Data.lua:328-352; wiki Blasphemy Support rev 1681869 (25% less effect since 3.20.0), Curse rev 1675786", pob: full}
  - {kind: support, name: "Hextouch", slot: any, role: applies, target: enemy, text: "hex is applied to enemies hit by the supported skill (first hit does not get it); 35% less curse effect, 35-26% less curse duration (3.27.0); no mana cost; not for totems, traps, mines, minions", source: "PoB Data/Skills/sup_int.lua:1416-1482; wiki Hextouch Support rev 1681745 (3.20.0, 3.27.0)", pob: partial}
  - {kind: support, name: "Awakened Hextouch", slot: any, role: applies, target: enemy, text: "as Hextouch plus (10-28)% chance to affect Hexproof enemies and +1 curse gem level from gem level 5; no longer obtainable since 3.28.0", source: "PoB Data/Skills/sup_int.lua:1609-1670 (chance_to_ignore_hexproof_% has no statMap entry there); wiki Awakened Hextouch Support rev 1698384", pob: partial}
  - {kind: gem, name: "Bane", slot: any, role: applies, target: enemy, text: "applies the linked hexes in an area itself (Bane does not use a slot, the curses do); hexes from Bane have 25% less effect (3.20.0); linked hexes pay no cost; Blasphemy hexes cannot be linked", source: "PoB Data/Skills/act_int.lua:1460-1600 (curse count capped at EnemyCurseLimit); wiki Bane rev 1682026 (3.20.0)", pob: full}
  - {kind: support, name: "Hexpass", slot: any, role: enables, target: enemy, text: "supported hexes affect Hexproof enemies (100%), hexed enemies cannot crit, 30% reduced area at level 1; new in 3.28.0", source: "PoB Data/Skills/sup_int.lua:3014-3060; wiki Hexpass Support rev 1682304", pob: partial}
  - {kind: notable, name: "Unholy Authority 31344 (Occultist)", slot: tree, role: enables, target: enemy, text: "Your Hexes can affect Hexproof Enemies (plus one additional curse)", source: "TreeData/3_29/tree.lua:44503-44512; ModParser.lua:5339 (CursesIgnoreHexproof); wiki Unholy Authority rev 1490201 (3.20.0)", pob: partial}
  - {kind: unique, name: "Cospri's Will", slot: body, role: enables, target: enemy, text: "Your Hexes can affect Hexproof Enemies; one additional curse; Always Poison on Hit against Cursed Enemies (uses the Cursed condition); curse and poison cannot happen on the same hit", source: "PoB Data/Uniques/body.lua:285-293; wiki Cospri's Will rev 1674863", pob: partial}
  - {kind: unique, name: "Oskarm", slot: gloves, role: applies, target: enemy, text: "Trigger Level 10 Assassin's Mark when you Hit a Rare or Unique Enemy and have no Mark", source: "PoB Data/Uniques/gloves.lua:301; ModCache ExtraSkill AssassinsMark level 10 triggered", pob: partial}
  - {kind: unique, name: "Sentari's Answer", slot: shield, role: applies, target: enemy, text: "curses on block (Punishment melee, Temporal Chains projectile, Elemental Weakness spell) that ignore the curse limit", source: "PoB Data/Uniques/shield.lua:766-779; wiki Curse rev 1675786", pob: none}
  - {kind: unique, name: "Ylfeban's Trickery", slot: helmet, role: applies, target: enemy, text: "Curse Enemies which Hit you with a random Hex, ignoring Curse Limit (current variant)", source: "PoB Data/Uniques/helmet.lua:810-824; ModCache nil mods; wiki Curse rev 1675786", pob: none}
  - {kind: mod, name: "Hexwarded map suffix", slot: map, role: blocks, target: enemy, text: "(25/40/60)% less effect of Curses on Monsters; the Uber-map variant reads 100% reduced; Hexproof map suffix: Monsters are Hexproof; corrupted-area variant: Monsters are Unaffected by Curses and Reflect Hexes", source: "wiki cargo mods MapMonstersCurseEffectOnSelfFinal/2/3, MapUberModPlayerCurseEffect, MapHexproof, MapCorruptedSideAreaMonsterUnaffectedByCurses; PoB Data/ModMap.lua:24-31 (25/40/60 only)", pob: partial}
makes_redundant:
  - {provider: "Hexpass / Unholy Authority / Cospri's Will hexproof bypass", when: "the map and the boss are not Hexproof", why: "the bypass only matters on Hexproof monsters; marks ignore Hexproof anyway", source: "wiki Hexproof rev 1486560 ('Hexproof only affects Hex curses and does not affect Mark curses')"}
conflicts:
  - {with: "Blasphemy auras filling the curse limit", effect: "self-cast, triggered and on-hit curses never apply while the aura fills the slots (cannot proc Impending Doom Support)", source: "wiki Curse rev 1675786, curse priority section"}
  - {with: "Hexpass or Hextouch on a hex that also has Blasphemy", effect: "Hexpass crit prevention does not work through the Blasphemy aura", source: "wiki Hexpass Support rev 1682304"}
  - {with: "Hexproof monster", effect: "hexes apply as lock icons, enemy counts as cursed, but no debuff effect; marks still work", source: "wiki Hexproof rev 1486560"}
  - {with: "Immune to Curses (monster or Expedition remnant mod)", effect: "no hex and no mark applies; absolute, no bypass", source: "wiki Curse immunity rev 1348384"}
conditions:
  - {text: "default order when the limit is full: the oldest curse expires when a different one is applied; Blasphemy auras > Mark of Submission socketed curses > triggered curse skills (main hand, amulet, helmet, off hand, body, belt, gloves, boots, ring 1, ring 2; the later one replaces the earlier) > non-skill curse on hit modifiers (Temporal Chains, Enfeeble, Vulnerability, Elemental Weakness, Flammability, Frostbite, Conductivity, Despair, Punishment; later replaces earlier); marks always replace each other", source: "wiki Curse rev 1675786, curse priority section"}
  - {text: "PoB priority number = curse base (Temporal Chains 1 ... Punishment 9, marks 10-13) + 100 x socket + slot (weapon 1 1000, amulet 2000, helmet 3000, weapon 2 4000, body 5000, gloves 6000, boots 7000, rings 8000-10000; NO belt entry) + 11000 for item-granted + 20000 for aura; higher number replaces lower, same name keeps the higher", source: "CalcPerform.lua:587-611, 3239-3271; Data.lua:328-352"}
  - {text: "Bosses: Pinnacle bosses, map bosses, Incursion architects, Betrayal targets, Breachlords and others no longer have 33% / 66% less effect of curses on them since 3.20.0 ('so that Hexes will be consistently effective against all monsters')", source: "wiki Version 3.20.0 rev 1635782; wiki Curse rev 1675786 version history"}
  - {text: "Curse effect is increased/more on the skill: curse-specific effect mods (for example 'increased Frostbite Curse Effect') affect only the gem, not 'Curse Enemies with Frostbite on Hit' item curses; PoB scales the item curse with enemy-side effect only (CalcPerform.lua:3185)", source: "wiki Curse rev 1675786 (Curse effect note); CalcPerform.lua:3185"}
  - {text: "Hexproof enemies are still considered cursed (Hexblast, Self-Flagellation, Curse Mastery work), PoB would not count them as Cursed if the flag were set (curse skipped before slotting)", source: "wiki Hexproof rev 1486560; CalcPerform.lua:2662, 3361-3365"}
  - {text: "Each curse mod of mods with local_ stat ids is item-local; the bypass and additional-curse stats here are global (stat ids ignore_hexproof, number_of_additional_curses_allowed, hexproof carry no local_ prefix)", source: "wiki cargo mods IgnoreHexproofUnique___1 (ignore_hexproof), MonsterHexproof1 (hexproof)"}
uptime:
  Mapping:       {value: partial, config: {conditionEnemyCursed: "not needed: PoB sets Cursed itself when a curse is slotted (CalcPerform.lua:3361-3365); tick only to force it", conditionCursedEnemyRecently: "tick only if a curse really lands every few seconds"}, reasoning: "per method: Blasphemy aura on every enemy inside its radius while the aura lasts (high); self-cast hex on the pack you cast on until its duration ends (needs recasting per pack); Hextouch on every enemy the supported skill hits after the first hit; Mark On Hit and Oskarm only on Rare or Unique enemies, so none on white packs and one mark on one target. Hexproof map suffix removes all hex effects, Hexwarded takes 25/40/60% off", source: "wiki Blasphemy Support rev 1681869, Hextouch Support rev 1681745, Mark On Hit Support rev 1682222, Mark rev 1647869; vault Chance on hit uptime"}
  Pinnacle Boss: {value: high, config: {enemyIsBoss: "Pinnacle or Uber: no curse effect change in PoB (probe: increased 0, more 1)"}, reasoning: "one target: a mark (no duration) or Blasphemy aura stays on while in range; a self-cast hex or Hextouch hex lasts its duration and is refreshed by hits; the Mark On Hit cooldown (4 s in PoB data) is irrelevant while the mark stays. No boss curse penalty since 3.20.0. Whether single pinnacle bosses or phases carry Hexproof, Immune to Curses or a curse-removing mechanic is not documented on the wiki pages read", source: "wiki Version 3.20.0 rev 1635782, Mark rev 1647869, Curse immunity rev 1348384 ('There are no known monsters with full Curse immunity')"}
seeds: [EK, FR]
sources:
  - {ref: "https://www.poewiki.net/wiki/Curse (rev 1675786)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Version_3.20.0 (rev 1635782), section Curses", kind: wiki, patch: "3.20.0"}
  - {ref: "https://www.poewiki.net/wiki/Hexproof (rev 1486560)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Curse_immunity (rev 1348384)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Mark (rev 1647869)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Bane (rev 1682026), Blasphemy_Support (rev 1681869), Hextouch_Support (rev 1681745), Mark_On_Hit_Support (rev 1682222), Hexpass_Support (rev 1682304), Awakened_Hextouch_Support (rev 1698384)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcPerform.lua:587-611, 2653-2707, 3143-3315, 3361-3365; ConfigOptions.lua:1601, 1806, 1833, 1836, 2017-2021, 2086-2222; Data/ModMap.lua:24-31; ModParser.lua:3383-3400, 5338-5347; Data/SkillStatMap.lua:2100-2108", kind: pob, patch: "3.29"}
  - {ref: "scratchpad b3b/curse_probe.py, FR_curseprobe.json, EK_curseprobe.json (headless PoB 2.67.2, enemyIsBoss None/Boss/Pinnacle/Uber)", kind: pob, patch: "3.29"}
not_verified:
  - "Which map bosses or pinnacle bosses carry the Hexproof implicit (MonsterImplicitHexproof) or Immune to Curses in their phases: not enumerated; the wiki says no known monster has full curse immunity, but boss-phase behaviour is undocumented in the pages read"
  - "READING CONFLICT Sentari's Answer: the [[Curse limit]] note lists it as pob full; ModCache.lua has nil mods for its three curse-on-block lines, so PoB would not count them (code reading of ModCache, not run)"
  - "Hexpass in PoB: its statMap sets flag CursesIgnoreHexproof in the supported skill's mod list, while CalcPerform.lua:2662 reads modDB:Flag(nil, 'CursesIgnoreHexproof') or skillData.ignoreHexproof; whether the flag reaches modDB was not run (moot while no enemy can be Hexproof in PoB)"
  - "Wiki lists belt in the triggered-curse order (main hand, amulet, helmet, off hand, body, belt, gloves, boots, rings); PoB Data.lua:328-352 has no belt slot: belt-triggered curses get slot priority 0 (code reading)"
  - "Hextouch / Mark On Hit applied-on-hit timing (first hit unbenefitted, 4 s cooldown) is not modelled by PoB; the curse is simply counted as slotted"
  - "Hexwarded values: PoB offers 25/40/60; the wiki has also 10, 15, 50 and a 100% reduced Uber-map variant (ids listed above); which exist at 3.29 league mechanics was not checked"
  - "Why EK's Vulnerability is SkillType.Triggered (which item or gem triggers it) was not traced"
  - "Curse duration of each hex and uptime numbers per hex were not computed (no hit-rate model run for curses); the FR hexes are self-cast and EK/FR marks follow the Assassin's Mark note"
open_questions:
  - "For the generator: model Hexproof as a scenario flag (Hexproof map suffix) so bypass providers (Hexpass, Unholy Authority, Cospri's Will) get a value, or leave them at zero as PoB does?"
  - "Should Sentari's Answer, Ylfeban's Trickery and Mark of Submission count as curse sources when PoB leaves them unparsed (a hand-set ExtraCurse equivalent), or be flagged as unmeasured?"
```
