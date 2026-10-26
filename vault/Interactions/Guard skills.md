---
type: interaction
status: draft
pob_refs: [GuardSkillActive, sharedGuardAbsorbRate, sharedGuardAbsorb, GuardAbsorbRate, GuardAbsorbLimit, PhysicalMaximumHitTaken, FireMaximumHitTaken, TotalEHP, LostNonVaalBuffRecently]
source: "poewiki Guard skill rev 1660806, Steelskin rev 1682040, Molten Shell rev 1681668, Vaal Molten Shell rev 1681807, Arcane Cloak rev 1697344, Veteran's Awareness rev 1479640 (fetched 2026-10-26); PoB 2.67.2 CalcPerform.lua / CalcDefence.lua / CalcTools.lua / Data/Skills; headless probes on 3.29\\Ninja Builds\\CoC EK Assa.xml and 3.29\\Worb.xml (b1b-mechanics-researcher.md C, b1b-pob-coverage-auditor.md guard, b1b-skill-gem-analyst.md 1-5)"
last_confirmed_patch: "3.29.x"
---

A guard skill (Steelskin, Molten Shell, Vaal Molten Shell, Immortal Call, Arcane Cloak) puts a buff in front of your life and ES that takes a share of each hit until it is used up. PoB counts it as a static one-time absorb pool that is always full, always available and has no duration, cooldown or trigger, so its max hit and EHP gain is a best case. PoB also keeps only one non-Vaal guard, chosen by Lua table order, and a Vaal Molten Shell wipes the rest, which differs from the wiki. Related: [[Cast when damage taken]], [[Armour and physical max hit]], [[Endurance charges]].

Pipeline: [[Receiving damage#Guard and Aegis]] - the guard takes its share of the hit after mitigation and aegises, before ward, ES and life (wiki Molten Shell: "the Molten Shell buff takes damage after mitigation and aegises, but before the player's main resources like ward and life")

```interaction
id: guard-skills
mechanic: "Guard skills absorb a share of each hit into a one-time pool (Steelskin 70% up to 2,209 at L20, 1.5 s; Molten Shell 75% up to 10% of armour, max 5,000, 3 s; Vaal Molten Shell 39% (L20) up to 20% of armour, max 10,000, 9 s); non-Vaal guards share one cooldown that does not recover while a guard buff runs; PoB counts the pool as always available"
family: buff
pipeline_step: ["Receiving damage#Guard and Aegis"]
pipeline_why: "wiki Guard skill and Molten Shell: the buff takes damage after mitigation and aegises, before ward, ES and life; PoB puts the absorb in front of every type's hit pool"
target: self
related: [cast-when-damage-taken, armour-phys-max-hit, endurance-charges, flat-physical-damage-reduction, spell-suppression]
pob:
  measured: partial
  how: "Gate: buff type Guard applied at CalcPerform.lua:2350-2362 when env.mode_buffs (true in the main output, CalcSetup.lua:565-575) and the gem is enabled in an enabled group; no config box (only LostNonVaalBuffRecently, ConfigOptions.lua:1265, default false, feeds a condition not the absorb). Data: Steelskin quick_guard_damage_absorbed_% 70, duration 1.5 s, cooldown 3 s (act_str.lua:11004-11035); Molten Shell 75%, limit 10% of Armour capped at molten_shell_max_damage_absorbed 5000, duration 3 s, cooldown 4 s (act_str.lua:7589-7640); Vaal Molten Shell 20% of Armour, max 10,000 (act_str.lua:7734-7735). Effectiveness stats scale by the gem's levelRequirement (CalcTools.lua:202-214), so absorb limits are L20 2,209 / L21 2,403 and the Molten Shell armour +858 (L20) / +909 (L21). Pool: sharedGuardAbsorbRate = min(Sum(GuardAbsorbRate), 100), sharedGuardAbsorb = calcLib.val(GuardAbsorbLimit) (CalcDefence.lua:2425-2428); entered in every type's TotalHitPool as pool - protected + min(pool, protected)/(1 - rate) with protected = absorb/rate*(1-rate) (CalcDefence.lua:3179-3190) = max hit, and in the EHP simulation as Guard (218-310, 2642-2652) = TotalEHP. Guard choice: CalcPerform.lua:3318-3341 walks pairs(guards): Vaal Molten Shell wipes all others and breaks; other Vaal names are all kept; the first non-Vaal name met is kept and later non-Vaal guards are skipped; Immortal Call is a guard in PoB (GuardSkillActive = 1 on Worb at base, no absorb). PoB leaves out: guard duration (Steelskin 1.5 s, Molten Shell 3 s), the shared cooldown (3 s / 4 s) and its no-recovery-during-buff rule (PoB marks the stat but does not use it), the activation or trigger (CwDT, manual), the reflected fire damage, quality duration or cooldown gains. Code oddity (not measured): CalcDefence.lua:3181 parses as a or (0 + b) or 0, so a per-type <Type>GuardAbsorbRate would never join the max-hit pool; every Guard gem writes the shared stat, so no gem is affected today."
  config:
    - {var: LostNonVaalBuffRecently, default: false, ref: "Modules/ConfigOptions.lua:1265", class: b}
  unparsed: []
model: null
providers:
  - {kind: gem, name: "Steelskin", slot: any, role: sustains, target: self, text: "buff takes 70% of hit damage until depleted; limit L20 2,209 / L21 2,403 (derived from the PoB formula, L20 = wiki); 1.5 s, cooldown 3 s, bleed immunity; Str 155 / 159; instant; mana 16", source: "Data/Skills/act_str.lua:11004-11062; Modules/CalcTools.lua:202-214; poewiki Steelskin rev 1682040", pob: full}
  - {kind: gem, name: "Molten Shell", slot: any, role: sustains, target: self, text: "adds armour (+858 at L20, +909 at L21) and absorbs 75% of hit damage up to 10% of armour including the buff armour, max 5,000; 3 s, cooldown 4 s; reflects 3000% as fire; Str 155; instant", source: "Data/Skills/act_str.lua:7589-7690; poewiki Molten Shell rev 1681668", pob: full}
  - {kind: gem, name: "Vaal Molten Shell", slot: any, role: sustains, target: self, text: "39% (L20) / 40% (L21) of hit damage up to 20% of armour, max 10,000; 9 s; cost 50 Soul, no shared guard cooldown; replaces an ongoing guard buff (wiki); not supportable by Cast when Damage Taken", source: "Data/Skills/act_str.lua:7691-7769; poewiki Vaal Molten Shell rev 1681807", pob: full}
  - {kind: gem, name: "Immortal Call", slot: any, role: sustains, target: self, text: "less Physical and Elemental Damage taken for a short time (L20: 35% less physical, 34% less elemental; 15% less physical per Endurance charge consumed); 1 s, shares the guard cooldown; PoB treats it as a guard with no absorb", source: "Data/Skills/act_str.lua:6758-6843; Modules/CalcPerform.lua:3318-3341", pob: full}
  - {kind: gem, name: "Arcane Cloak", slot: any, role: sustains, target: self, text: "spends 64% of Mana at L20 for a buff that takes 75% of hit damage until depleted, limit = the mana spent; 3 s, shares the guard cooldown; PoB uses ManaUnreserved, the wiki says current Mana", source: "Data/Skills/act_int.lua:331-360; poewiki Arcane Cloak rev 1697344", pob: partial}
  - {kind: support, name: "Cast when Damage Taken", slot: any, role: enables, target: self, text: "triggers Steelskin and Molten Shell (both Spell + Triggerable); not Vaal Molten Shell, Determination or Grace; CwDT level cap = third table value (L20 70, L21 72), Steelskin and Molten Shell L20 need CwDT >= L20, L21 needs L21; a guard triggered this way protects the NEXT hit only; PoB does not check the cap", source: "Data/Skills/sup_str.lua:1146-1153,1200-1201; vault Cast when damage taken", pob: partial}
  - {kind: keystone, name: "Veteran's Awareness", slot: jewel, role: scales, target: self, text: "+10% to all Elemental Resistances and maximum Elemental Resistances and 20% additional Physical Damage Reduction while affected by a Non-Vaal Guard Skill; 20% more Damage taken if a Non-Vaal Guard Buff was lost Recently (PoB applies the penalty only when LostNonVaalBuffRecently is ticked)", source: "TreeData/3_29/tree.lua:85671; Data/Uniques/jewel.lua:208-212; poewiki Veteran's Awareness rev 1479640", pob: config}
  - {kind: notable, name: "Dynamo", slot: tree, role: scales, target: self, text: "18% increased maximum Mana; Guard Skills have 40% increased Duration (PoB ignores guard duration in the pool)", source: "TreeData/3_29/tree.lua:42712-42726", pob: partial}
  - {kind: notable, name: "Adamant", slot: tree, role: scales, target: self, text: "25% increased Armour; Remove Bleeding when you use a Guard Skill; Guard Skills have 25% increased Duration", source: "TreeData/3_29/tree.lua:49400-49416", pob: partial}
  - {kind: notable, name: "Guard Skill cooldown recovery nodes (41026, 10073)", slot: tree, role: scales, target: self, text: "Guard Skills have 20% increased Cooldown Recovery Rate (Mana and Guard Skill Cooldown Recovery; Armour and Guard Skill Cooldown Recovery); only shortens the post-buff cooldown", source: "TreeData/3_29/tree.lua:42814-42819,49366-49370", pob: none}
  - {kind: mastery, name: "Mana Mastery option (44948)", slot: tree, role: sustains, target: self, text: "Recover 10% of Mana over 1 second when you use a Guard Skill", source: "TreeData/3_29/tree.lua:24342", pob: none}
  - {kind: flask, name: "Flask enchant (guard)", slot: flask, role: enables, target: self, text: "Used when you Use a Guard Skill / Used when you lose a Guard Skill Buff", source: "Data/EnchantmentFlask.lua:16-18", pob: none}
makes_redundant:
  - {provider: "Molten Shell (gem)", when: "armour is low, for example 5,000 base armour adds only 586 to the pool", why: "the limit is 10% of armour, so Steelskin's fixed 2,209 is larger below 22,090 armour (derived: 10% x (armour + 858) = 2,209)", source: "Data/Skills/act_str.lua:7600-7610; b1b-mechanics-researcher.md C"}
conflicts:
  - {with: "wiki: one non-Vaal guard at a time, Vaal Molten Shell can coexist with one non-Vaal guard", effect: "wiki: Vaal Molten Shell does not share the cooldown and a non-Vaal guard (Steelskin) can be used without removing it, but casting Vaal Molten Shell replaces ongoing guard buffs. PoB: Vaal Molten Shell wipes every other guard and breaks the loop, so VMS plus Steelskin never coexist in PoB", source: "poewiki Guard skill rev 1660806, Vaal Molten Shell rev 1681807; Modules/CalcPerform.lua:3318-3341"}
  - {with: "two non-Vaal guards enabled together", effect: "PoB keeps the first non-Vaal name returned by pairs(guards), an unspecified order: on Worb (Immortal Call already enabled) adding Molten Shell or Steelskin gave the new skill in two processes and Immortal Call in one, same file and change; a generator must not stack two non-Vaal guards and must read sharedGuardAbsorbRate to see which one PoB used", source: "Modules/CalcPerform.lua:3318-3332; b1b-pob-coverage-auditor.md guard (3 processes)"}
  - {with: "Immortal Call", effect: "PoB counts Immortal Call as a guard, so it competes with Steelskin and Molten Shell for the single slot; on Worb Immortal Call is worth more than the absorb guards", source: "Modules/CalcPerform.lua:3318-3341; b1b-pob-coverage-auditor.md measurements"}
  - {with: "guard duration and cooldown", effect: "PoB counts the absorb as always available at the moment of the hit; the real buff is up 1.5 s (Steelskin) or 3 s (Molten Shell) per 3-4 s cooldown that does not recover while the buff runs, so TotalEHP and max hit with a guard are a best case", source: "Modules/CalcDefence.lua:2425-2428; Data/Skills/act_str.lua:11043,7649; vault gap Guard absorb static pool"}
  - {with: "buff-effect mods and Empower", effect: "guard mods are unscalable, so buff-effect mods do not change the absorb; a gem level raised by Empower changes the limit via the level-requirement formula (L22 2,611, L23 2,837, L24 3,080, derived), whether the CwDT cap check uses the base or raised level is unverified", source: "Data/Skills/act_str.lua statMap unscalable; b1b-skill-gem-analyst.md 3, 7"}
conditions:
  - {text: "Steelskin and Molten Shell need Str 155 at L20 (159 at L21); a Witch seed shows no Strength", source: "poewiki Steelskin rev 1682040, Molten Shell rev 1681668"}
  - {text: "Molten Shell's pool depends on armour (10% of armour including its +858), capped at 5,000; Vaal Molten Shell 20% capped at 10,000", source: "Data/Skills/act_str.lua:7600-7610,7734-7735"}
  - {text: "PoB's Armour change from Molten Shell gets armour increases and Determination's more, then the 10% is taken of the total", source: "b1b-skill-gem-analyst.md 3"}
  - {text: "quality 20: Steelskin +10% cooldown recovery; Molten Shell and Vaal Molten Shell +20% duration; PoB counts neither", source: "Data/Skills/act_str.lua:11030,7631,7730; Modules/CalcTools.lua:193-197"}
uptime:
  Mapping:
    value: partial
    config: {}
    reasoning: "PoB: always full and available (best case). Derived from base duration and cooldown (no cooldown-recovery mods, specialist arithmetic): Steelskin 1.5 / (1.5 + 3) = 33%, Molten Shell 3 / (3 + 4) = 43%, Arcane Cloak 3 / (3 + 4) = 43%, Immortal Call 1 / (1 + 3) = 25%; many hits per second in maps, so the guard cycles"
    source: "Data/Skills/act_str.lua:11043,7649,6798; poewiki Guard skill rev 1660806 (cooldown does not recover during buff); derived"
  Pinnacle Boss:
    value: partial
    config: {LostNonVaalBuffRecently: "leave unticked unless the generator models a lost guard buff"}
    reasoning: "same derived windows (33-43%); the absorb limit is fixed (2,209 at L20) so its share of a large boss hit is small and a CwDT-triggered guard protects only the next hit; PoB's pool counts it as available for every hit"
    source: "Data/Skills/act_str.lua:11004-11060; vault Cast when damage taken; derived"
seeds: [EK, Worb, Fireball]
sources:
  - {ref: "https://www.poewiki.net/wiki/Guard_skill (rev 1660806, introduced 3.7.0)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Steelskin (rev 1682040); Molten_Shell (rev 1681668); Vaal_Molten_Shell (rev 1681807); Arcane_Cloak (rev 1697344); Veteran's_Awareness (rev 1479640)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcPerform.lua:2350-2362,3318-3341; Modules/CalcDefence.lua:218-310,2425-2428,2642-2652,3179-3190; Modules/CalcTools.lua:193-214; Data/Skills/act_str.lua:7589-7769,11004-11062 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b1b-mechanics-researcher.md (C); b1b-pob-coverage-auditor.md (guard, measurements); b1b-skill-gem-analyst.md (1-5)", kind: discovery, patch: "3.29"}
not_verified:
  - "measured (auditor probes, one change, rolled back; Worb Immortal Call disabled as control 16,310 to 11,854 phys max hit): control + Steelskin L20 (2,209 at 70%) phys max 15,499, TotalEHP 75,169; + Molten Shell L20 (588 at 75%, Armour 5,882) 13,048, TotalEHP 63,296; + Vaal Molten Shell L20 (1,176 at 39%) 14,021, TotalEHP 68,241; so replacing Immortal Call with an absorb guard is a net loss on Worb"
  - "measured EK (base phys max 7,538, TotalEHP 145,259): Steelskin gem already in the file, enabled false to true, sharedGuardAbsorb 1,946 at 70%: phys max 10,297 (+2,759), fire max 30,340 (+8,274), TotalEHP 199,920 (+54,661); new Steelskin group 2,403: phys 10,945, fire 32,283, TotalEHP 212,669; Molten Shell (absorb 203 at 75%, Armour 658 to 2,033) phys 8,187; Vaal Molten Shell (407 at 40%) phys 8,476. CORRECTION by the skill-gem-analyst: by the PoB formula 1,946 is an effective gem level 19 and 2,403 an effective level 21 (L20 = 2,209, confirmed by the Worb row), so EK carries about +1 gem level; where it comes from was not looked up. The Molten Shell armour gain +1,375 is +909 (effective L21) times EK's armour increases, not decomposed"
  - "the uptime percentages (33 / 35 / 43 / 47 / 25) are specialist arithmetic from base duration plus cooldown; with quality 20 Steelskin 1.5 / (1.5 + 2.73) = 35% and Molten Shell 3.6 / (3.6 + 4) = 47%; none measured or wiki-quoted"
  - "derived pool sizes for the Fireball seed (Life 3,000 + ES 1,100 = 4,100): Steelskin +2,209 (about +54%) as a full snapshot; Molten Shell min(10% x (armour + 858), 5,000), 586 at 5,000 armour; Vaal Molten Shell min(20% x armour, 10,000)"
  - "Steelskin usable while casting: the wiki text for Steelskin has no 'moving' line; Instant only by PoB's skill type"
  - "Runegraft of Time (multiple different guards at once): named on the wiki only, no match in Data/Uniques and no PoB mod"
  - "the wiki Molten Shell note that buff-effect mods (currently Ichimonji only) affect only the armour was not applied"
  - "whether pairs() order really changes PoB's chosen guard between runs: observed in 3 processes, the Lua hash-order cause is an inference"
  - "L21 values come from the PoB table and formula; the wiki cargo level table for L21 was not fetched"
  - "Vaal Immortal Call (CannotDie flag) and whether PoB's guard list includes it were not checked; Crucible and Scourge guard cooldown mods left out"
  - "Dynamo, Adamant and the cooldown nodes: position relative to the Witch start not checked"
open_questions:
  - "Which reading should the generator use when a build has two non-Vaal guards or Vaal Molten Shell plus a non-Vaal guard? PoB keeps one (pairs order, VMS wipes the rest); the wiki allows VMS plus one non-Vaal guard."
  - "Should the generator discount the guard absorb by its derived window (33-43%) or show PoB's best case with the window as a label? The numbers are not a PoB output."
  - "Immortal Call counts as a guard in PoB and ranks above the absorb guards on Worb: should the generator treat it as occupying the single non-Vaal slot?"
```
