---
type: interaction
status: draft
pob_refs: [Minion.TotalDPS, FullDPS, SkillDPS, ActiveMinionLimit, Multiplier:SummonedMinion, skillMinionItemSet, skillMinionSkill, MovementSpeedMod, conditionUsedMinionSkillRecently, meatShieldEnemyNearYou, ExtraAura]
source: "poewiki Animate Guardian rev 1681757 (fetched 2026-10-26; page history ends at 3.29.0); PoB 2.67.2 Data/Skills/act_str.lua, Data/Minions.lua, Modules/CalcPerform.lua, CalcActiveSkill.lua, Calcs.lua, ConfigOptions.lua, TreeData/3_29/tree.lua, Data/Uniques; evidence skill-gem-analyst, pob-coverage-auditor, item-analyst, tree-ascendancy-analyst (task 027 batch 2b); headless runs on 3.27/SRS CI Guardian Giga Build.xml (in memory, never saved)"
last_confirmed_patch: "3.29.x"
---

Animate Guardian gives ONE permanent Guardian that wears items from the build's own item set. Its damage is mostly the animated weapon, so the gem level moves its life far more than its damage. PoB shows the Guardian as one minion (TotalDPS) times the hand-set gem count; the game allows one Guardian, so a count of 2 over-counts. Only six slots are read, and "nearby allies" lines on the worn items do nothing in PoB. Number alive and uptime come from the model [[Minion alive count]]; general minion rules are in [[Minions]].

Pipeline: [[Damage calculation#Increased and reduced]], [[Damage calculation#More and less]] - Guardian damage runs through the minion actor's own pools (MinionModifier mods and its worn items), not the player's; [[Damage calculation#Hit rate]] - the minion count enters only after the per-minion hit rate (FullDPS = minion TotalDPS x gem count, Calcs.lua:179-180).

```interaction
id: animate-guardian
mechanic: "Animate Guardian: one permanent Guardian minion dressed from the build's item set (Weapon 1, Weapon 2, Helmet, Body Armour, Gloves, Boots only); PoB counts it as one minion's TotalDPS x the hand-set gem count and does not cap that count at 1; a dead Guardian cannot be re-summoned in that area"
family: uptime
target: self
related: [minions, raise-spectre, absolution, culling-strike]
pipeline_step: ["Damage calculation#Increased and reduced", "Damage calculation#More and less", "Damage calculation#Hit rate"]
pipeline_why: "Guardian damage runs through the minion actor's own increased/more pools and its worn items (CalcPerform.lua:1222-1235, 1247-1253), not the player's; the number of Guardians enters only after the per-minion hit rate (FullDPS = minion TotalDPS x gem count, Calcs.lua:179-180)"
pob:
  measured: partial
  how: "One Guardian's rate only. Gem is permanentMinion with no limit key, so it contributes one minion (Data/Skills/act_str.lua:488, Data/Minions.lua:605-630, CalcPerform.lua:1436-1444); minion modDB is built from the item set chosen on the gem (CalcActiveSkill.lua:735-745), six slots only (act_str.lua:474-481, CalcPerform.lua:1222-1235); FullDPS = minion TotalDPS x the hand-set gem count (Calcs.lua:116-137,179-180), no cap at 1; limits are output-only so a count over the limit is not capped; 'nearby allies' ExtraAura lines on worn items are never consumed (CalcPerform.lua:3419 iterates the player's modDB); item level cap, ranged-weapon rule and the 'dies once per area' rule are not modelled. Measured on the SRS CI Guardian build (Pinnacle config of the file): Animated Guardian level 80, Minion.TotalDPS 185,862.07, Life 64,222, Speed 6.39/s, MovementSpeedMod 3.07 (Q20)."
  config:
    - {var: "gem count (socket group gem count)", default: 1, ref: "Modules/Calcs.lua:116-137", class: c}
    - {var: skillMinionItemSet, default: "the player's own item set (id 1 in the sample)", ref: "Modules/CalcActiveSkill.lua:735-745 (a missing id falls back to the first set)", class: c}
    - {var: conditionUsedMinionSkillRecently, default: false, ref: "Modules/ConfigOptions.lua:1537-1540; auto-set only when the evaluated main skill is a minion skill that is NOT permanentMinion (Modules/CalcPerform.lua:253-255)", class: b}
    - {var: meatShieldEnemyNearYou, default: false, ref: "Modules/ConfigOptions.lua:543-545", class: b}
    - {var: enemyIsBoss, default: Pinnacle, ref: "Modules/ConfigOptions.lua:2086", class: b}
  unparsed:
    - "Animate Guardian: stat animate_item_maximum_level_requirement has no entry in Data/SkillStatMap.lua"
    - "Chains of Command: three splash lines and 'You cannot have Non-Animated, Non-Manifested Minions'"
    - "Gravebind: Nearby Enemies Killed by anyone count as being Killed by you instead"
model:
  proposed_kind: minion_alive_count
  inputs: {from_pob: [Minion.TotalDPS, "gem count"], from_scenario: ["death rate lambda (class b)", "fight or area time T (class b)"]}
  params: {limit: 1, resummon_delay_tau: "infinite in the area (wiki 3.26.0)"}
  formula: "alive = min(hand-set count, 1) x u, u = 1 (lambda 0) or (1 - exp(-lambda T)) / (lambda T) for a Guardian that stays dead; set the gem count to floor(alive), never above 1 (model: [[Minion alive count]], case b)"
  calibration: "no norm found for lambda (model note searched 3 times, 2026-10-26)"
providers:
  - {kind: gem, name: "Animate Guardian", slot: any, role: enables, target: self, text: "permanent Guardian, one at a time; effective gem level 25 (L21 + 4 from items/tree): minion level 80, TotalDPS 185,862.07, Life 64,222; L1 135,240 / L20 183,548 / L30 203,172 / L40 211,253 DPS, so life moves 3.7x from L21 to L40 and DPS only +14%; quality +2% minion movement speed per 1% (visible in MovementSpeedMod, not in DPS)", source: "Data/Skills/act_str.lua:464-549; wiki Animate Guardian rev 1681757; minion-skills.md section 1", pob: partial}
  - {kind: support, name: "Minion Life Support", slot: any, role: scales, target: self, text: "L20 49% more minion life (linked in the sample Guardian group)", source: "Data/Skills/sup_int.lua:4917-4958", pob: full}
  - {kind: support, name: "Meat Shield Support", slot: any, role: scales, target: self, text: "damage half needs the enemy near you; box ticked: Guardian +30.5%, FullDPS +17.23% in the sample (not counted by default)", source: "Data/Skills/sup_int.lua:4659; Modules/ConfigOptions.lua:543-545; coverage-minion-skills.md section 1", pob: config}
  - {kind: ascendancy, name: "Mindless Aggression (Necromancer)", slot: tree, role: scales, target: self, text: "Minions have 20% more Maximum Life; Minions deal 10% more Damage: Guardian +9.94% DPS, +19.91% Life", source: "TreeData/3_29/tree.lua:57569; tree.md section 2", pob: full}
  - {kind: ascendancy, name: "Unnatural Strength (Necromancer)", slot: tree, role: scales, target: self, text: "Minions have Unholy Might: Guardian +7.19% DPS", source: "TreeData/3_29/tree.lua:57590; tree.md section 2", pob: full}
  - {kind: notable, name: "Enduring Bond", slot: tree, role: scales, target: self, text: "Minions deal 30% increased Damage if you've used a Minion Skill Recently (+17.38% when the config is ticked; already allocated in the sample, so the figure is a second copy)", source: "TreeData/3_29/tree.lua:44812; Modules/ConfigOptions.lua:1537; tree.md section 2", pob: config}
  - {kind: notable, name: "Fearsome Force", slot: tree, role: scales, target: self, text: "Minions have 60% increased Critical Strike Chance and +20% Critical Strike Multiplier: Guardian +11.57% DPS (second copy in the sample)", source: "TreeData/3_29/tree.lua:29954; tree.md section 2", pob: full}
  - {kind: notable, name: "Gravepact", slot: tree, role: scales, target: self, text: "+7% Chaos Resistance; Minions have 8% chance to deal Double Damage: Guardian +8.09% DPS", source: "TreeData/3_29/tree.lua:36165; tree.md section 2", pob: full}
  - {kind: unique, name: "Chains of Command", slot: "Body Armour", role: enables, target: self, text: "triggers Animate Guardian's Weapon on Guardian kill (L20; 10% L18 on Animated Weapon kill); Animated Guardian deals 5% increased Damage per Animated Weapon (reads the LIMIT, not live weapons); you cannot have Non-Animated, Non-Manifested Minions", source: "Data/Uniques/body.lua:957-968; Modules/ModParser.lua:1552", pob: partial}
  - {kind: unique, name: "Kingmaker", slot: Weapon, role: scales, target: self, text: "worn by the Guardian: (300-360)% inc Physical Damage, (7-12)% attack speed, (30-40)% crit chance work for the Guardian; 'Nearby Allies have Culling Strike, +50% crit multiplier, +10 Fortification, 30% item rarity' (the reason to wear it) are ExtraAura lines and give 0% in PoB; vendor recipe", source: "Data/Uniques/axe.lua:299,311-320; Modules/CalcPerform.lua:3419; items.md section 2a", pob: partial}
  - {kind: unique, name: "Leer Cast", slot: Helmet, role: scales, target: self, text: "You and nearby allies gain 50% increased Damage; 25% reduced Damage: PoB counts the drawback on the Guardian and not the benefit line (ExtraAura), wiki says both 'apply as normal'", source: "Data/Uniques/helmet.lua:1569,1575; Modules/CalcPerform.lua:3419; wiki Animate Guardian rev 1681757", pob: partial}
  - {kind: unique, name: "Dying Breath", slot: Weapon, role: scales, target: self, text: "Nearby allies gain 18% increased Damage (measured 0.00%, ExtraAura); Nearby Enemies 18% increased Effect of Curses reaches the Guardian's own evaluation only", source: "Data/Uniques/staff.lua:279-285; Modules/CalcPerform.lua:3419; items.md section 2a", pob: partial}
makes_redundant:
  - {provider: "Animate Guardian gem count 2 (or a second Animate Guardian gem)", when: "always", why: "only one Guardian can exist; PoB multiplies by the count and does not cap it (count 2: FullDPS +18.2%, an over-count)", source: "wiki Animate Guardian rev 1681757 'You can only have one Guardian at a time'; Modules/Calcs.lua:116-137; coverage-minion-skills.md section 1"}
  - {provider: "Gem levels above 20 for the item level cap", when: "always", why: "the cap column of the level table is 100 from L20 on (L20 38% / L21 40%); more levels add only minion level and the life/damage finals", source: "Data/Skills/act_str.lua:464-549"}
  - {provider: "Items in the 13 non-Guardian slots (Amulet, rings, belt, flasks, abyss jewels, grafts)", when: "always", why: "the Guardian reads only six slots; blanking any other slot changes nothing (185,862.07 each)", source: "Data/Skills/act_str.lua:474-481; Modules/CalcPerform.lua:1222-1235; coverage-minion-skills.md section 1"}
conflicts:
  - {with: "The Dark Monarch", effect: "'Cannot have Minions other than X': each variant names one minion type and the Animated Weapons variant does not include the Animate Guardian (wiki The Dark Monarch rev 1702130, per items.md); PoB does not parse the line, so it accepts the combination", source: "Data/Uniques/helmet.lua:854-865; items.md section 1a"}
  - {with: "Wraithlord", effect: "You cannot have Non-Spectre Minions: not parsed, not enforced by PoB", source: "Data/Uniques/helmet.lua:798; items.md section 2b"}
  - {with: "Doppelganger Guise (worn by the Guardian)", effect: "item-granted skills such as Unhinge cannot be used by the Guardian; PoB processes ExtraSkill only for the player's items", source: "wiki Animate Guardian rev 1681757; Modules/CalcSetup.lua:237; items.md section 2a"}
conditions:
  - {text: "If the Guardian dies it cannot be summoned again in that area (a hideout is the exception); it keeps its items on death (3.26.0)", source: "wiki Animate Guardian rev 1681757 (3.26.0); Data/Skills/act_str.lua:468"}
  - {text: "Ranged weapons cannot be animated; items need to be identified; items with socketed gems cannot be animated; gem level caps the item level and a too-low gem level disables the item temporarily. PoB equips the player's own Wand (29-54) and enforces none of these", source: "wiki Animate Guardian rev 1681757; coverage-minion-skills.md section 1 (e5.json base)"}
  - {text: "'Nearby Allies / You and nearby allies' lines and enemy debuffs on Guardian gear reach only the Guardian's own evaluation (own-stat and 'Nearby Enemies' lines work, +8.10% for -10% all resistances); they never reach other skills, because each skill is evaluated in its own env", source: "Modules/CalcPerform.lua:3419; Modules/Calcs.lua:142-205; items.md section 2a"}
  - {text: "Weapon slots: with useSecondWeaponSet the Guardian reads Weapon 1/2 Swap; with those empty it loses the weapon (DPS 107,666). Value of the six slots in the sample: Weapon 1 -42.1% if blanked, Body Armour -13.6%, Helmet / Gloves / Boots / Weapon 2 0; all blank 93,004 (unarmed 2-6 physical)", source: "Modules/CalcPerform.lua:1227; Modules/CalcActiveSkill.lua:766-787; Data/Minions.lua:629-630; coverage-minion-skills.md section 1"}
  - {text: "conditionUsedMinionSkillRecently is auto-set only for non-permanent minions: with the Guardian (permanent) as the evaluated skill it stays off, so an 'if you used a Minion Skill Recently' line gives +13.6% on the Guardian row only after the tick; the real character has it true when it casts any non-permanent minion skill", source: "Modules/CalcPerform.lua:253-255; coverage-minion-skills.md section 4"}
uptime:
  Mapping:       {value: model, config: {"gem count": "1 (never above 1)", conditionUsedMinionSkillRecently: "tick when the build casts any non-permanent minion skill"}, reasoning: "permanent minion: alive from the cast until it dies once in the area; a map is one area, so a death is permanent for the map; no death rate norm found", source: "wiki Animate Guardian rev 1681757 (3.26.0); Minion alive count model case b"}
  Pinnacle Boss: {value: model, config: {enemyIsBoss: Pinnacle, "gem count": "1 x survival share u"}, reasoning: "single area per fight, so a dead Guardian stays dead for the fight; Pinnacle -> None changes the Guardian row +40.1% (defences only, no uptime); no survival norm found", source: "wiki Animate Guardian rev 1681757 (3.26.0); coverage-minion-skills.md section 4 (enemyIsBoss row)"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Animate_Guardian (rev 1681757, fetched 2026-10-26)", kind: wiki, patch: "3.29"}
  - {ref: "Data/Skills/act_str.lua:464-549; Data/Minions.lua:605-630; Modules/CalcPerform.lua:253-255,1222-1235,1436-1444,3419; Modules/CalcActiveSkill.lua:735-745,766-787; Modules/Calcs.lua:116-137,169-205; Modules/ConfigOptions.lua:543-545,1537-1540 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "TreeData/3_29/tree.lua:29954,36165,44812,57569,57590; Data/Uniques/{body,axe,helmet,staff}.lua lines in the providers", kind: pob, patch: "3.29"}
  - {ref: "https://poe-vault.com Ghazzy's Animate Guardian Gearing Guide (patch 3.29, page dated 2026-07-24), summary only", kind: discovery, patch: "3.29"}
not_verified:
  - "whether the wiki's 'ranged weapons cannot be animated' includes wands (bows certainly); PoB equips the player's Wand"
  - "whether the real game counts casting Animate Guardian as 'used a Minion Skill recently' (PoB treats permanent minion skills as not setting it, CalcPerform.lua:253-255)"
  - "whether Sane / Insane conditions of Doppelganger Guise work on a minion; Fleshcrafter-type 'Minions:' lines worn by the Guardian were not tested"
  - "Mask of the Stitched Demon 'no longer keeps the guardian alive as of 3.29' (guide claim, not checked)"
  - "3.29 availability of league-origin or boss-drop items (Kingmaker is a vendor recipe, Leer Cast / Dying Breath random drops per PoB and wiki cargo flags only)"
  - "tree valuations are on the SRS CI Guardian build, in memory; nodes marked 'second copy' are already allocated there, so the figure is not the gain of a first copy"
  - "mod wording of Chains of Command per-weapon damage uses the limit, not live Animated Weapons: effect in game not tested"
open_questions:
  - "Should the generator build a dedicated Animate Guardian item set (melee weapon plus armour, no ranged weapon) instead of the default of wearing the player's own set?"
  - "Leer Cast and Dying Breath benefit lines give 0% in PoB while the wiki says they apply in game: add them as custom mod lines, or keep a Gap?"
  - "Which survival share u should the generator assume for the Guardian in a Pinnacle fight where a death is permanent?"
```
