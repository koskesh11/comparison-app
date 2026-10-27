---
type: interaction
status: draft
pob_refs: [CritMultiplier, CritEffect, CritBifurcates, BonusCritDotMultiplier, SelfCritMultiplier, CritMultiplierAppliesToDegen, ReduceCritExtraDamage, NoCritMultiplier]
source: "wiki Critical strike rev 1698799 (patch history 2.2.0, 0.9.3, 3.16.0), mod page CriticalMultiplier1 (cargo mod_stats); PoB 2.67.2 CalcOffence.lua, CalcSetup.lua, CalcDefence.lua, Data/Misc.lua, Data/Skills/act_int.lua / sup_int.lua, TreeData/3_29/tree.lua; headless runs on the EK and FR sample builds (task 027 batch 3)"
last_confirmed_patch: "3.29.x"
---

The critical strike multiplier decides how much extra damage a crit adds: players start at 150% (50% extra damage), monsters at 130%. Every source is a flat addition ("+N% to Critical Strike Multiplier", one additive pool since patch 2.2.0), so there is no increased/more split and PoB reads only the BASE entries. The multiplier acts on hit damage only: damaging ailments get a separate +50% DoT multiplier on a crit instead. Bifurcation (Mystical Infusion) applies the extra damage a second time on the share of crits where both rolls succeed, which at 100% chance doubles it. Related: [[Critical strike chance]], [[Lucky critical strikes]], [[Power charges]], [[Damage over time multiplier]].

Pipeline: [[Damage calculation#Critical strike]] - the multiplier turns the hit into a crit hit before the damage roll and before enemy mitigation; [[Damage calculation#Ailments from hits]] - ailments do not take the hit multiplier, they take the +50% DoT multiplier on crit.

```interaction
id: critical-strike-multiplier
mechanic: "Crit hit = hit x (1 + extra damage); extra damage = (50 base + sum of '+N% to Critical Strike Multiplier' + enemy SelfCritMultiplier BASE such as Assassin's Mark) / 100; PoB floors the result at 1 and rounds the extra damage to 2 decimals; bifurcation adds the extra damage a second time on the share of crits where both rolls succeed"
family: buff
target: self
related: [critical-strike-chance, lucky-critical-strikes, power-charges, damage-over-time-multiplier, coc-trigger]
pipeline_step: ["Damage calculation#Critical strike", "Damage calculation#Ailments from hits"]
pipeline_why: "the multiplier is applied to the hit in the Critical strike step, after increased/more and before the damage roll and enemy mitigation; damaging ailments skip it and take the separate +50% DoT multiplier for ailments from crits (Ailments from hits)"
pob:
  measured: full
  how: "CalcOffence.lua:3203-3262: extraDamage = Sum(BASE, CritMultiplier)/100 (3207), Override CritMultiplier (3208-3210), effective mode adds enemy SelfCritMultiplier BASE and scales by (1 + enemy SelfCritMultiplier INC) then round(x, 2) (3212-3215), bifurcation adds conditionalBifurcateChance x extra (3226-3258; the MORE 'Bifurcated Crit Damage Bonus' is descriptive only), CritMultiplier = 1 + max(0, extraDamage) (3260), CritEffect = 1 - c + c x CritMultiplier (3262-3263). Only BASE is summed: no MORE or INC CritMultiplier modifier is read (INC measured 0, MORE only the descriptive bifurcation entry). No cap. Player base 150 from Data/Misc.lua:89 via CalcSetup.lua:603 (stored as +50); monsters 130 (Misc.lua:166). The crit DoT multiplier +50 (Misc.lua:90) is added under Condition CriticalStrike (CalcSetup.lua:604); with Perfect Agony BonusCritDotMultiplier = (CritMultiplier - 50) x CritMultiplierAppliesToDegen/10000 (3264). Enemy reduction of extra crit damage: the INC path exists (3213) but nothing in ModParser, ModCache or ConfigOptions writes SelfCritMultiplier (grep count 0 in all three); the only source is the Assassin's Mark skill statMap (BASE, act_int.lua:979-1020). The 'reduced extra damage from critical strikes' stat is parsed as the PLAYER's ReduceCritExtraDamage (ModParser.lua:5914) and used only for incoming crits (CalcDefence.lua:1629, 1738, 3531)"
  config:
    - {var: buffMode, default: EFFECTIVE, ref: "Modules/ConfigOptions.lua (misc_buffMode, EFFECTIVE in both seeds)", class: b}
    - {var: usePowerCharges, default: false, ref: "Modules/ConfigOptions.lua:900", class: b}
  unparsed: []
model: null
providers:
  - {kind: mod, name: "Base 150% (50% extra damage)", slot: any, role: enables, target: self, text: "every player starts with +50% to Critical Strike Multiplier; monsters 130% (30% extra)", source: "Data/Misc.lua:89 and 166; CalcSetup.lua:603; wiki Critical strike rev 1698799 (Critical strike multiplier, patch 0.9.3)", pob: full}
  - {kind: support, name: "Increased Critical Damage", slot: gem, role: scales, target: self, text: "+153% (EK) / +161% (FR) to Critical Strike Multiplier at their gem level and quality; the largest single source in both seeds", source: "Data/Skills/sup_int.lua:3684-3700; headless mod lists (Skill:SupportIncreasedCriticalDamage BASE 153 EK, 161 FR)", pob: full}
  - {kind: gem, name: "Assassin's Mark (curse)", slot: gem, role: applies, target: enemy, text: "enemy_additional_critical_strike_multiplier_against_self: PoB adds it as enemy SelfCritMultiplier BASE = +109 (EK) / +49 (FR) to the extra damage (before the 2-decimal rounding); it is the only enemy-side crit multiplier source found in PoB", source: "Data/Skills/act_int.lua:979-1020; CalcOffence.lua:3213-3215; headless enemyDB SelfCritMultiplier", pob: full}
  - {kind: notable, name: "Assassination 28754 (EK)", slot: tree, role: scales, target: self, text: "+25% to Critical Strike Multiplier and 25% increased Critical Strike Chance", source: "TreeData/3_29/tree.lua:71817; headless EK mod list", pob: full}
  - {kind: notable, name: "Critical Strike Multiplier per Power Charge 12783 (EK, FR)", slot: tree, role: scales, target: self, text: "+5% per power charge (x7 = +35, counted only with usePowerCharges)", source: "TreeData/3_29/tree.lua:43545; headless EK and FR mod lists", pob: config}
  - {kind: notable, name: "Arcane Potency 46842 and Spell Critical Strike Multiplier 36452 (EK)", slot: tree, role: scales, target: self, text: "+30% and +10% to Critical Strike Multiplier for Spell Damage: count for Ethereal Knives (5.37 before bifurcation) not for the Cyclone trigger attack (multiplier 4.97 with the Mark)", source: "TreeData/3_29/tree.lua:28444, 28542; headless EK main skill 328 vs Cyclone 288 BASE sum", pob: full}
  - {kind: mastery, name: "Critical Mastery 16123 (EK) / 63861 (FR)", slot: tree, role: scales, target: self, text: "PoB counts +25 to Critical Strike Multiplier from the chosen mastery effect (the node's first listed stat is the ailment-effect line, the selected effect was not traced)", source: "TreeData/3_29/tree.lua:28467 and 77079; headless mod lists (Tree:16123 BASE 25, Tree:63861 BASE 25)", pob: full}
  - {kind: ascendancy, name: "Mystical Infusion 1945 (EK)", slot: tree, role: abuses, target: self, text: "Spell Critical Strike Chance Bifurcates: at 100% chance the second crit roll succeeds as well, so the extra damage is applied twice. Measured EK Ethereal Knives: CritBifurcates 2, CritMultiplier 9.74 = 1 + 2 x (3.28 + 1.09); without bifurcation 5.37 (computed). Spell only", source: "TreeData/3_29/tree.lua:83385; CalcOffence.lua:3226-3258; headless EK main skill", pob: full}
  - {kind: unique, name: "Rune Needle, Vengeance Grasp, Foul Stare, Enthralling Arbiter, Watcher's Eye (FR)", slot: any, role: scales, target: self, text: "FR items add +38 (weapon), +19 and +30 (ring), +12 and +12 (Hypnotic Eye jewels), +26 (Watcher's Eye) to Critical Strike Multiplier; wiki Watcher's Eye can roll '+(30-50)% to Critical Strike Multiplier while affected by Anger'", source: "FR build items 2, 9, 29, 30, 19; headless FR mod list; wiki Critical strike rev 1698799 (Watcher's Eye)", pob: full}
  - {kind: keystone, name: "Perfect Agony", slot: tree, role: abuses, target: self, text: "3.29 form: DoT multiplier for ailments equals Critical Strike Multiplier; crits deal no extra damage; non-crits cannot inflict ailments (PoB flag DotMultiplierIsCritMultiplier; the old CritMultiplierAppliesToDegen form is not this keystone). See [[Perfect Agony]]", source: "TreeData/3_29/tree.lua:80922; Data/ModCache.lua:15014; Modules/CalcOffence.lua:4185; lead re-check batch 3c", pob: full}
  - {kind: notable, name: "Overwhelm (Slayer)", slot: tree, role: scales, target: self, text: "+10% to Critical Strike Multiplier per Nearby Enemy, up to +100%; also 'Nearby Enemies have -30% to Critical Strike Multiplier' (their multiplier against you)", source: "TreeData/3_29/tree.lua:59581-59582", pob: partial}
  - {kind: notable, name: "For the Jugular / Knife in the Back (Assassin)", slot: tree, role: scales, target: enemy, text: "+100% to Critical Strike Multiplier against Enemies not on Low Life (Jugular) / on Low Life (Knife in the Back); needs the enemy low-life config", source: "TreeData/3_29/tree.lua:83308 and 83286; ConfigOptions.lua:1803", pob: config}
  - {kind: notable, name: "Shimmeron (Reliquarian)", slot: tree, role: scales, target: self, text: "+8% to Critical Strike Multiplier per Power Charge", source: "TreeData/3_29/tree.lua:21855", pob: config}
  - {kind: notable, name: "Ahn's Might (Reliquarian)", slot: tree, role: scales, target: self, text: "+100% to Critical Strike Multiplier while you have no Frenzy Charges", source: "TreeData/3_29/tree.lua:21041", pob: full}
  - {kind: notable, name: "Critical Strike Chance and Multiplier (Assassin small nodes)", slot: tree, role: scales, target: self, text: "+10% to Critical Strike Multiplier and 15% increased Critical Strike Chance per node", source: "TreeData/3_29/tree.lua:83621-83622, 83640-83641", pob: full}
makes_redundant: []
conflicts:
  - {with: "Resolute Technique / Precise Technique", effect: "never crit, so the multiplier is unused (PoB NeverCrit sets CritMultiplier 0, CritEffect 1)", source: "TreeData/3_29/tree.lua:21817, 68373; CalcOffence.lua:3042-3047"}
  - {with: "damage over time and the damaging ailment DPS", effect: "ignite, poison and bleed do not scale with the crit multiplier (only +50% DoT multiplier on crit, or the Perfect Agony conversion)", source: "wiki Critical strike rev 1698799 (Ailments); CalcSetup.lua:604; CalcOffence.lua:3264"}
conditions:
  - {text: "all sources are additive; since patch 2.2.0 there are no 'increased' crit multiplier modifiers", source: "wiki Critical strike rev 1698799 version history 2.2.0: 'All sources of increased Critical Strike Multiplier have been changed to additional Critical Strike Multiplier.'"}
  - {text: "extra damage = multiplier minus 100%; player default 150% = 50% extra, monsters 130% = 30% extra", source: "wiki Critical strike rev 1698799: 'Player characters have a base crit multi value of 150%, while monsters have a base crit multi value of 130%, or 50% and 30% extra damage respectively' (0.9.3: 'Players now have a default critical strike damage multiplier of +50%. Monsters are now set to +30%.')"}
  - {text: "an enemy's 'Take #% reduced Extra Damage from Critical Strikes' multiplicatively reduces the multiplier above the baseline 100%; reductions stack additively, capped at 100%; the wiki describes it for characters taking monster crits. No wiki or PoB source found for monsters reducing the PLAYER's crit extra damage at 3.29, and PoB has no setter (see how). So the player multiplier is not reduced by enemy stats except by what Assassin's Mark adds", source: "wiki Critical strike rev 1698799 (Reduced extra damage from critical strikes); PoB grep SelfCritMultiplier = 0 in ModParser.lua / ModCache.lua / ConfigOptions.lua"}
  - {text: "damaging ailments from crits have an inherent +50% to Damage over Time Multiplier (+30% for minions and monsters), additive with other DoT multiplier; they do not scale with the crit multiplier unless Perfect Agony is allocated", source: "wiki Critical strike rev 1698799 (Ailments); Data/Misc.lua:90, 167; CalcSetup.lua:604"}
  - {text: "crits inherently apply ignite, freeze and shock (subject to the ailment threshold); a crit also makes the Cast on Critical Strike trigger fire", source: "wiki Critical strike rev 1698799; CalcOffence.lua:4231-4249; see critical-strike-chance, coc-trigger"}
  - {text: "extra damage is rounded to 2 decimals in effective mode; the multiplier is floored at 1 (a negative sum does not reduce hits below normal damage)", source: "CalcOffence.lua:3215, 3260"}
uptime:
  Mapping:       {value: partial, config: {usePowerCharges: "ticked in both seeds"}, reasoning: "the Assassin's Mark part (+109 EK / +49 FR) exists only on the Marked enemy; without it the multiplier is EK Cyclone 4.97 -> 3.88 and FR 5.92 -> 5.43 (arithmetic). Power charge nodes need charges (EK +35, FR +35 at 7 charges)", source: "headless runs 2026-10-26: EK Cyclone multiplier 4.97 (288 + 109), FR 5.92 (443 + 49); arithmetic for the unmarked values"}
  Pinnacle Boss: {value: high, config: {}, reasoning: "one target, the Mark can stay on the boss (duration and curse limit not traced); the bifurcation bonus needs 100% crit chance on the spell", source: "act_int.lua:979-1020"}
seeds: [EK, FR]
sources:
  - {ref: "https://www.poewiki.net/wiki/Critical_strike (rev 1698799)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/w/api.php?action=cargoquery&tables=mod_stats (Modifier:CriticalMultiplier1 -> base_critical_strike_multiplier_+, global; no local variant found under the ids tried)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcOffence.lua:3042-3047, 3203-3264, 4231-4249; CalcSetup.lua:603-604; CalcDefence.lua:1629, 1738, 3531; Data/Misc.lua:89-90, 166-167; ModParser.lua:2323, 5914", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/Skills/act_int.lua:979-1020, sup_int.lua:3684; TreeData/3_29/tree.lua (node lines above)", kind: pob, patch: "3.29"}
  - {ref: "headless PoB runs on EK 'CoC EK Assa.xml' and FR 'FR CoC Occu Three Dragons v4.xml' (probe scripts in the task scratchpad b3/)", kind: pob, patch: "3.29"}
not_verified:
  - "whether any monster or boss modifier reduces the extra damage of the player's crits at 3.29 (the wiki section covers the player's incoming reduction only); PoB models none"
  - "the chosen mastery effect behind +25 on Critical Mastery 16123 and 63861, and what node 45558 (+35 in FR, tree.lua:34606 lists 'Shield Mastery') contributes: the effect text was not traced"
  - "the stack rule for several bifurcating sources and whether the wiki's 'critical strike bonus damage gets applied twice' is exactly extra x 2 at 100% (PoB: extra x (1 + both-roll share))"
  - "unique item alternatives with large multiplier lines (Data/Uniques amulet/dagger/gloves/bow) were found by grep but their names and obtainability were not checked"
  - "Assassin's Mark duration, cast time, uptime on a map pack, and the curse limit with other curses (not traced)"
  - "whether PoB's Overwhelm 'Nearby Enemies have -30% to Critical Strike Multiplier' is parsed (not checked)"
open_questions:
  - "None for the user."
```
