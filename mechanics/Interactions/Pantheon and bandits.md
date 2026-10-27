---
type: interaction
status: draft
pob_refs: [bandit, pantheonMajorGod, pantheonMinorGod, ExtraPoints, data.pantheons, AvoidProjectilesChance, AvoidFreeze, SelfChillEffect, StunRecovery, StunDuration, BlockDuration, SelfIgniteDuration, SelfShockEffect, SelfPoisonDuration, PhysicalDamageReduction, ElementalDamageTaken, LifeFlaskChargesGenerated, MaimImmune, BeenHitRecently, NearbyEnemies, Stationary]
source: "wiki Deal with the Bandits rev 1596867, Pantheon rev 1631432 (Template:Pantheon expansion fetched 2026-10-26), Recently rev 1397426; PoB 2.67.2 CalcSetup.lua, ConfigOptions.lua, Build.lua, ImportTab.lua, PantheonTools.lua, Data/Pantheons.lua, ModParser.lua, ModCache.lua; headless probes of EK, Worb, FR (task 027 batch 4e, A1)"
last_confirmed_patch: "3.29.x"
---

The bandit quest and the Pantheon are two free, permanent self-buff choices. Since 3.25.0 the bandit choice is 8% movement speed (Kraityn), +15% all elemental resistances (Alira), +40 maximum Life (Oak) or exactly 1 passive point for killing all three (Eramir); the old 2 points are gone. PoB's list has Oak, Kraityn, Alira and "None" (label "Kill all"); the value "Eramir" in a saved build falls into the same else branch as "None" and gives the 1 point, so it is harmless.
The Pantheon is one major plus one minor god; PoB reads every line of the base and all upgrade souls from Data/Pantheons.lua as if all upgrades were captured, then drops every line its parser cannot read completely. Of 41 lines, 17 count without a config tick, 11 count only with a config tick (hit recently, nearby enemies, stationary, ground), and 13 never count (11 unparsed, 2 parsed without an output change).
Seed pairs: EK = Brine King + Abberath and Worb = Brine King + Ryslatha change no EHP or DPS key in PoB (only display keys such as chill effect and freeze avoidance); FR = Lunaris + Abberath is worth +13,667 TotalEHP (+5.26%) through 10% avoid projectiles.

Pipeline: [[Receiving damage#Immunity and avoidance]] - most lines are avoidance or immunity; the damage-taken and reduction lines act in [[Receiving damage#Damage taken modifiers]] and [[Receiving damage#Armour and damage reduction]]. See [[Stun]], [[Elemental ailment immunity]] and [[Bleed, poison and corrupted blood immunity]] for the ailment lines.

```interaction
id: pantheon-and-bandits
mechanic: "Bandit quest reward (Eramir 1 passive point, Oak +40 maximum Life, Kraityn 8% increased Movement Speed, Alira +15% to all Elemental Resistances) and the Pantheon (one major + one minor god, every upgrade line active once captured); PoB applies both from Build/Config values with no cost and no uptime, counts a Pantheon line only when ModParser reads the whole line, and needs config ticks for the conditional ones"
family: defence
target: self
related: [stun, elemental-ailment-immunity, bleed-poison-cb-immunity, life-mana-flasks, max-resistances, chance-on-hit-uptime, receiving-damage, defences]
pipeline_step: ["Receiving damage#Immunity and avoidance", "Receiving damage#Damage taken modifiers", "Receiving damage#Armour and damage reduction", "Receiving damage#Damage over time taken", "Receiving damage#Resistances", "Receiving damage#Life"]
pipeline_why: "Pantheon lines are avoidance (projectiles, freeze), immunity (stun, blind, maim, poison), damage-taken inc/less and additional physical damage reduction, DoT-taken reductions; the bandit gives Life and resistances to the pools these steps use"
pob:
  measured: partial
  how: "Bandit: CalcSetup.lua:651-660 adds Alira ElementalResist BASE 15 (653), Kraityn MovementSpeed INC 8 (655), Oak Life BASE 40 (657) and in the else branch (659, reached by None AND by any other value such as Eramir) ExtraPoints BASE 1; ConfigOptions.lua:136 lists None (label Kill all), Oak, Kraityn, Alira only, the tooltip says 'Grants 1 Passive Skill Point' (ConfigOptions.lua:34); Build.lua:648-651 copies the legacy bandit/pantheon attributes into the config, Build.lua:901-902 uses ExtraPoints for the point budget (99 + 23 + extra); ImportTab.lua:1237-1240 maps an imported 'Eramir' to 'None'. Pantheon: CalcSetup.lua:662-673 calls pantheon.applySoulMod (PantheonTools.lua:6-19) for the major and the minor god; it adds a soul line only when modLib.parseMod returns a mod list and no leftover text (PantheonTools.lua:8-9), so unparsed or half-parsed lines vanish silently. Measured with headless PoB (in memory only) per line with fake single-line gods: config state S0 = as saved (no pantheon/bandit-related config set in any seed), A = all conditions ticked (been hit recently + 5 hits, 8 nearby enemies, stationary 3 s, moving, low life, burning and caustic ground, stopped taking DoT, hit recently), B = 1 nearby enemy, stationary 3 s, moving, burning and caustic ground, hit recently."
  config:
    - {var: bandit, default: "None", ref: "Modules/ConfigOptions.lua:136", class: c}
    - {var: pantheonMajorGod, default: "None", ref: "Modules/ConfigOptions.lua:137", class: c}
    - {var: pantheonMinorGod, default: "None", ref: "Modules/ConfigOptions.lua:144", class: c}
    - {var: conditionBeenHitRecently, default: false, ref: "Modules/ConfigOptions.lua:1375", class: b}
    - {var: multiplierBeenHitRecently, default: 0, ref: "Modules/ConfigOptions.lua:1378", class: b}
    - {var: multiplierNearbyEnemies, default: 0, ref: "Modules/ConfigOptions.lua:1234 (value 1 also sets Condition:OnlyOneNearbyEnemy, 1236)", class: b}
    - {var: conditionStationary, default: 0, ref: "Modules/ConfigOptions.lua:158 (seconds, sets Multiplier:StationarySeconds, 166)", class: b}
    - {var: conditionMoving, default: false, ref: "Modules/ConfigOptions.lua:171", class: b}
    - {var: conditionOnBurningGround, default: false, ref: "Modules/ConfigOptions.lua:1174", class: b}
    - {var: conditionOnCausticGround, default: false, ref: "Modules/ConfigOptions.lua:1168", class: b}
    - {var: conditionStoppedTakingDamageOverTimeRecently, default: false, ref: "Modules/ConfigOptions.lua:1438", class: b}
    - {var: conditionLowLife, default: false, ref: "Modules/ConfigOptions.lua:177", class: b}
  unparsed:
    - "Soul of the Brine King: You cannot be Stunned if you've been Stunned or Blocked a Stunning Hit in the past 2 seconds (Data/Pantheons.lua:11; live parse = leftover text, ModParser.lua has only the 'cannot be stunned if ...' patterns at 3104 and 4868-4870)"
    - "Mephod, the Earth Scorcher (Abberath): Unaffected by Burning Ground (Pantheons.lua:137; ModCache.lua:22323 = {nil,\"Unaffected by Burning Ground \"})"
    - "Erebix, Light's Bane (Gruthkul): Enemies that have Hit you with an Attack Recently have 8% reduced Attack Speed (Pantheons.lua:156; live parse = leftover)"
    - "Glace (Lunaris): Avoid Projectiles that have Chained (Pantheons.lua:120; ModCache.lua:14327 = {nil,\"Avoid Projectiles that have Chained \"})"
    - "Soul of Ralakesh: Moving while Bleeding doesn't cause you to take extra Damage (Pantheons.lua:226; ModCache.lua:18302 nil)"
    - "Drek, Apex Hunter (Ralakesh): Corrupted Blood cannot be inflicted on you if you have at least 5 Corrupted Blood Debuffs on you (Pantheons.lua:232; ModCache.lua:14791 nil; ModParser.lua:2499 only matches the short 'corrupted blood cannot be inflicted on you')"
    - "Soul of Shakari: You cannot be Poisoned while there are at least 3 Poisons on you (Pantheons.lua:188; live parse = leftover; ModParser.lua:4920 only has 'cannot be poisoned while bleeding')"
    - "Soul of Solaris: 20% chance to take 50% less Area Damage from Hits (Pantheons.lua:71; live parse = Damage BASE 20 with leftover ' to take 50% less   from Hits ', dropped by PantheonTools.lua:8)"
    - "Kitava, The Destroyer (Solaris): Take no Extra Damage from Critical Strikes if you have taken a Critical Strike Recently (Pantheons.lua:83; live parse = leftover; ModParser.lua:5903 only has the unconditional form)"
    - "Soul of Yugul: You and your Minions prevent +50% of Reflected Damage (Pantheons.lua:167; live parse = leftover) and 50% chance to Reflect Hexes (Pantheons.lua:169; live parse = leftover ' to Reflect Hexes ', dropped)"
    - "Parsed but no output change in any state on all three seeds: Soul of Ryslatha '60% increased Life Recovery from Flasks used when on Low Life' (parsed as FlaskLifeRecovery INC 60 with Condition:LowLife; used only in flask recovery, CalcPerform.lua:1664 and ItemsTab.lua:4684) and Forest of Flames (Solaris) '50% chance to avoid Ailments from Critical Strikes' (parsed as AvoidAilments BASE 50 with Condition:CriticalStrike, the player's own crit condition, not an incoming crit)"
model:
  proposed_kind: pantheon_condition_uptime
  inputs: {from_pob: [TotalEHP, FullDPS, StunAvoidChance, FreezeAvoidChance, AvoidProjectilesChance], from_scenario: ["hits taken per second E on the player (boss: assumption 1 per second, user 2026-10-25)", "number of nearby enemies N (map: scenario input; Pinnacle Boss: not sourced)", "seconds stationary and share of time moving", "share of time on burning or caustic ground"]}
  params: {recently_window_s: 4, pantheon_line_assumed_captured: true}
  formula: "u(been hit recently) = min(1, 4 s x E) for evenly spaced hits ('Recently' = the past four seconds, wiki Recently rev 1397426); u(not hit recently) = 1 - u(been hit recently). Condition lines are ticked or unticked by the same uptime rule as other config ticks (user rule 2026-10-25 as quoted in vault Onslaught: u >= 80% ticked, 50-80% ticked and the user informed with u, below 50% unticked with a warning); Lunaris/Solaris/Gruthkul lines scale with N and hits taken, Tukohama with stationary seconds. Never blend EHP: choose the god pair by PoB TotalEHP with the scenario's ticks set. Unparsed lines get no number (see gaps)"
  calibration: "no norm found for nearby-enemy counts, stationary time or hits taken per second in maps or on pinnacle bosses"
providers:
  - {kind: mod, name: "Bandit: Eramir (kill all three)", slot: quest, role: enables, target: self, text: "1 Passive Skill Point (down from 2 in 3.25.0); PoB: bandit None or any value not in its list adds ExtraPoints 1", source: "wiki Deal with the Bandits rev 1596867 (version history 3.25.0); CalcSetup.lua:658-659", pob: full}
  - {kind: mod, name: "Bandit: Oak", slot: quest, role: enables, target: self, text: "+40 to maximum Life", source: "wiki Deal with the Bandits rev 1596867; CalcSetup.lua:656-657", pob: full}
  - {kind: mod, name: "Bandit: Kraityn", slot: quest, role: enables, target: self, text: "8% increased Movement Speed", source: "wiki Deal with the Bandits rev 1596867; CalcSetup.lua:654-655", pob: full}
  - {kind: mod, name: "Bandit: Alira", slot: quest, role: enables, target: self, text: "+15% to all Elemental Resistances", source: "wiki Deal with the Bandits rev 1596867; CalcSetup.lua:652-653", pob: full}
  - {kind: mod, name: "Pantheon: Soul of the Brine King (major, base)", slot: pantheon, role: blocks, target: self, text: "You cannot be Stunned if you've been Stunned or Blocked a Stunning Hit in the past 2 seconds", source: "Data/Pantheons.lua:11; wiki Pantheon rev 1631432 (Template:Pantheon)", pob: none}
  - {kind: mod, name: "Pantheon: Brine King, Nassar, Lion of the Seas (capture, Reef Map)", slot: pantheon, role: sustains, target: self, text: "30% increased Stun and Block Recovery", source: "Data/Pantheons.lua:17; ModCache.lua:8368; CalcDefence.lua:2207-2208", pob: full}
  - {kind: mod, name: "Pantheon: Brine King, Captain Tanner Lightfoot (capture, Coral Ruins Map)", slot: pantheon, role: blocks, target: self, text: "100% chance to Avoid being Frozen", source: "Data/Pantheons.lua:23; live parse AvoidFreeze BASE 100; EK FreezeAvoidChance 0 to 100 (Worb and FR already 100 from Arctic Armour)", pob: full}
  - {kind: mod, name: "Pantheon: Brine King, Shock and Horror (capture, Mineral Pools Map)", slot: pantheon, role: sustains, target: self, text: "50% reduced Effect of Chill on you", source: "Data/Pantheons.lua:29; live parse SelfChillEffect INC -50; SelfChillEffect 100 to 50 on EK and Worb", pob: full}
  - {kind: mod, name: "Pantheon: Soul of Abberath (minor, base)", slot: pantheon, role: sustains, target: self, text: "60% less Duration of Ignite on You", source: "Data/Pantheons.lua:131; live parse SelfIgniteDuration MORE -60; only SelfIgniteDuration changes", pob: full}
  - {kind: mod, name: "Pantheon: Abberath, Mephod, the Earth Scorcher (upgrade)", slot: pantheon, role: blocks, target: self, text: "Unaffected by Burning Ground", source: "Data/Pantheons.lua:137; ModCache.lua:22323", pob: none}
  - {kind: mod, name: "Pantheon: Abberath, Mephod, the Earth Scorcher (upgrade)", slot: pantheon, role: enables, target: self, text: "10% increased Movement Speed while on Burning Ground", source: "Data/Pantheons.lua:139; live parse MovementSpeed INC 10 with Condition:OnBurningGround; EK +0.07 MovementSpeedMod with conditionOnBurningGround ticked", pob: config}
  - {kind: mod, name: "Pantheon: Soul of Lunaris (major, base)", slot: pantheon, role: enables, target: self, text: "1% additional Physical Damage Reduction for each nearby Enemy, up to 8%", source: "Data/Pantheons.lua:100; live parse PhysicalDamageReduction BASE 1 with Multiplier:NearbyEnemies; needs multiplierNearbyEnemies", pob: config}
  - {kind: mod, name: "Pantheon: Soul of Lunaris (major, base)", slot: pantheon, role: enables, target: self, text: "1% increased Movement Speed for each nearby Enemy, up to 8%", source: "Data/Pantheons.lua:102; live parse MovementSpeed INC 1 with Multiplier:NearbyEnemies; needs multiplierNearbyEnemies", pob: config}
  - {kind: mod, name: "Pantheon: Lunaris, Captain Clayborne, The Accursed (capture, Frozen Cabins Map)", slot: pantheon, role: enables, target: self, text: "10% chance to avoid Projectiles", source: "Data/Pantheons.lua:108; ModCache.lua:3666; CalcDefence.lua:1583; FR TotalEHP 259,674.90 to 273,342.00 (+13,667, +5.26%) in S0", pob: full}
  - {kind: mod, name: "Pantheon: Lunaris, Fragment of Winter (capture, Waterways Map)", slot: pantheon, role: enables, target: self, text: "6% reduced Elemental Damage taken if you have been Hit Recently", source: "Data/Pantheons.lua:114; live parse ElementalDamageTaken INC -6 with Condition:BeenHitRecently; needs conditionBeenHitRecently", pob: config}
  - {kind: mod, name: "Pantheon: Lunaris, Glace (capture, Beach Map)", slot: pantheon, role: enables, target: self, text: "Avoid Projectiles that have Chained", source: "Data/Pantheons.lua:120; ModCache.lua:14327", pob: none}
  - {kind: mod, name: "Pantheon: Soul of Ryslatha (minor, base)", slot: pantheon, role: sustains, target: self, text: "Life Flasks gain 3 Charges every 3 seconds if you haven't used a Life Flask Recently", source: "Data/Pantheons.lua:262; ModParser.lua:5752-5754 (LifeFlaskChargesGenerated BASE 1, neg UsingLifeFlask); Worb LifeFlaskChargeGen 0 to 1", pob: full}
  - {kind: mod, name: "Pantheon: Soul of Ryslatha (minor, base)", slot: pantheon, role: sustains, target: self, text: "60% increased Life Recovery from Flasks used when on Low Life", source: "Data/Pantheons.lua:264; live parse FlaskLifeRecovery INC 60 with Condition:LowLife; no output key changed in S0, A or B on Worb", pob: partial}
  - {kind: mod, name: "Pantheon: Ryslatha, Gorulis, Will-Thief (capture, Infested Valley Map)", slot: pantheon, role: applies, target: enemy, text: "Enemies you've Hit Recently have 50% reduced Life Regeneration rate", source: "Data/Pantheons.lua:270; live parse EnemyModifier with Condition:HitRecently; EnemyLifeRegen changes on EK and Worb", pob: full}
  - {kind: mod, name: "Pantheon: Soul of Solaris (major, base)", slot: pantheon, role: enables, target: self, text: "6% additional Physical Damage Reduction while there is only one nearby Enemy", source: "Data/Pantheons.lua:69; ModParser.lua:1775; needs multiplierNearbyEnemies = 1 (ConfigOptions.lua:1236)", pob: config}
  - {kind: mod, name: "Pantheon: Soul of Solaris (major, base)", slot: pantheon, role: blocks, target: self, text: "20% chance to take 50% less Area Damage from Hits", source: "Data/Pantheons.lua:71; live parse leftover", pob: none}
  - {kind: mod, name: "Pantheon: Solaris, Oak the Mighty (capture, Mesa Map)", slot: pantheon, role: enables, target: self, text: "8% reduced Elemental Damage taken if you haven't been Hit Recently", source: "Data/Pantheons.lua:77; live parse ElementalDamageTaken INC -8 with Condition:BeenHitRecently (negated); counted by default, switched off by conditionBeenHitRecently (S0 41 keys, A 0)", pob: full}
  - {kind: mod, name: "Pantheon: Soul of Tukohama (minor, base)", slot: pantheon, role: enables, target: self, text: "3% additional Physical Damage Reduction per second you've been stationary, up to a maximum of 9%", source: "Data/Pantheons.lua:207; ModParser.lua:1464; needs conditionStationary seconds", pob: config}
  - {kind: mod, name: "Pantheon: Tukohama, Tahsin, Warmaker (capture, Siege Map)", slot: pantheon, role: sustains, target: self, text: "Regenerate 2% of Life per second while stationary", source: "Data/Pantheons.lua:213; ModCache.lua:19265; needs conditionStationary", pob: config}
  - {kind: mod, name: "Pantheon: Soul of Gruthkul (minor, base)", slot: pantheon, role: enables, target: self, text: "1% additional Physical Damage Reduction for each Hit you've taken Recently up to a maximum of 5%", source: "Data/Pantheons.lua:150; live parse PhysicalDamageReduction BASE 1 with Multiplier:BeenHitRecently; needs multiplierBeenHitRecently", pob: config}
  - {kind: mod, name: "Pantheon: Shakari, Terror of the Infinite Drifts (capture)", slot: pantheon, role: enables, target: self, text: "5% reduced Chaos Damage taken", source: "Data/Pantheons.lua:194; ModCache.lua:10050; Worb TotalEHP 76,836.94 to 77,279 as a single line (+442); no change on EK and FR (not probed why)", pob: full}
  - {kind: mod, name: "Pantheon: Soul of Garukhan (minor, base)", slot: pantheon, role: blocks, target: self, text: "60% reduced Effect of Shock on you", source: "Data/Pantheons.lua:243; ModCache.lua:10953", pob: full}
  - {kind: mod, name: "Pantheon: Garukhan, The Blacksmith (capture, Dunes Map)", slot: pantheon, role: blocks, target: self, text: "You cannot be Maimed", source: "Data/Pantheons.lua:251; ModCache.lua:22813; CalcDefence.lua:1591 (MaimImmunity is a boolean output, not seen by the numeric probe)", pob: full}
  - {kind: mod, name: "Pantheon: Soul of Arakaali (major, base)", slot: pantheon, role: enables, target: self, text: "10% reduced Damage taken from Damage Over Time", source: "Data/Pantheons.lua:40; live parse DamageTakenOverTime INC -10; changes the *TakenDotMult and DotEHP keys", pob: full}
  - {kind: mod, name: "Pantheon: Soul of Ralakesh (minor, base)", slot: pantheon, role: enables, target: self, text: "25% reduced Physical Damage over Time taken while moving", source: "Data/Pantheons.lua:224; live parse PhysicalDamageTakenOverTime INC -25 with Condition:Moving; needs conditionMoving", pob: config}
  - {kind: mod, name: "Pantheon: Yugul, Varhesh, Shimmering Aberration (capture)", slot: pantheon, role: blocks, target: self, text: "30% reduced Effect of Curses on you", source: "Data/Pantheons.lua:175; live parse CurseEffectOnSelf INC -30", pob: full}
makes_redundant:
  - {provider: "Brine King Captain Tanner Lightfoot (100% Avoid being Frozen)", when: "a permanent freeze immunity or avoidance is already on the build (Worb and FR carry Arctic Armour; PoB FreezeAvoidChance is 100 without any god)", why: "the freeze line adds nothing; the same god is then used for its other lines (chill effect, stun recovery) and the unparsed stun lockout", source: "headless probe: EK FreezeAvoidChance 0 to 100 with the Brine King, Worb and FR 100 without any god; Skill:ArcticArmour FreezeImmune"}
  - {provider: "Bandit Oak / Kraityn / Alira", when: "the build is Chaos Inoculation (Life 1: EK, FR) or resistances are already over the cap by more than 15", why: "Oak's +40 Life is worth 0 EHP on EK and FR (only StunThreshold changes) and Alira's 15% only adds over-cap resistance (EK fire over cap 26 to 41, FR 71 to 86), so Eramir's 1 passive point is worth more", source: "headless probe p3 (EK, FR, Worb); Modules/CalcSetup.lua:651-660"}
  - {provider: "Solaris Oak the Mighty (not hit recently) vs Lunaris Fragment of Winter (hit recently)", when: "both would be taken", why: "the two lines are opposite on the same flag BeenHitRecently, so only one of them is up at a time; PoB counts Oak by default and Fragment of Winter only after the tick", source: "headless probe p4 (S0 vs A states) on EK, FR, Worb"}
conflicts:
  - {with: "conditionBeenHitRecently tick", effect: "switching it on turns Solaris' Oak the Mighty line off (S0 41 keys changed, A 0) and Lunaris' Fragment of Winter on (S0 0, A 41); Gruthkul needs multiplierBeenHitRecently too", source: "headless probe p4 on EK; ModParser live parse"}
  - {with: "the point budget", effect: "any bandit other than Eramir removes 1 passive point: FR shows 123 / 122 (over budget) and EK 118 / 122, Worb 121 / 122 instead of x / 123; a skill-point-short build cannot afford Oak, Kraityn or Alira", source: "headless probe p3 pointDisplay; Build.lua:901-902"}
conditions:
  - {text: "Kill all three bandit leaders gives 1 Passive Skill Point (it was 2 until 3.24); helping Alira, Kraityn or Oak gives the stated passive bonus instead; the choice can be changed with 20 Orbs of Regret and an amulet (Book of Reform), and changing away from Eramir needs a free skill point", source: "wiki Deal with the Bandits rev 1596867: 'Eramir grants 1 Passive Skill Point if you decide to kill all three. (down from 2)' (version history 3.25.0); the 1.0.1 row says an Eramir reward needs a skill point available to change away"}
  - {text: "Pantheon powers: one major and one minor god; the base power is unlocked by defeating the god in Acts 6-10, each upgrade needs a Divine Vessel plus a map boss capture; upgrades are shared by all characters of a league since 3.24.0 but disabled until the quest An End to Hunger is done; swapping is free in town or hideout; not in Ruthless", source: "wiki Pantheon rev 1631432 (version history 3.24.0, text 'Upgrading')"}
  - {text: "the wiki's current soul lines (Template:Pantheon expansion) equal PoB's Data/Pantheons.lua for 41 of 41 lines (one spacing difference in the Tukohama line); the last wiki line change is 3.20.0 (Ryslatha), the last version row is 3.24.0", source: "wiki Pantheon rev 1631432 vs Data/Pantheons.lua (compared 2026-10-26)"}
  - {text: "'Recently' means the past four seconds", source: "wiki Recently rev 1397426"}
  - {text: "PoB counts every upgrade line the moment the god is chosen, whether or not the player has captured the soul", source: "PantheonTools.lua:6-19 loops over all souls of the god"}
uptime:
  Mapping:
    value: model
    config:
      bandit: "Eramir unless a seed measures Oak/Kraityn/Alira as worth more than 1 passive point (Worb: Oak +941.63 TotalEHP for 1 point; EK and FR: 0)"
      conditionBeenHitRecently: "by the model: in maps with many enemies hits are frequent, so the Hit-Recently family (Lunaris Fragment of Winter, Gruthkul) is mostly up and Solaris Oak the Mighty mostly down; scenario input E"
      multiplierNearbyEnemies: "scenario input N (a pack: several; Solaris one-enemy line only at 1)"
      conditionStationary: "scenario input (seconds; maps with movement: low)"
    reasoning: "the always-on lines (avoidance, immunity, ailment duration and effect, DoT reductions, Nassar, Tanner) are up all the time; condition lines inherit the uptime of their condition; ground lines only on maps with Burning or Caustic Ground; no norm found for the counts"
    source: "ConfigOptions.lua:158,1174,1168,1234,1375,1378; wiki Recently rev 1397426; headless probe p4"
  Pinnacle Boss:
    value: model
    config:
      bandit: "same as Mapping"
      conditionBeenHitRecently: "true when the boss hits at least once every 4 seconds (assumption E = 1 per second, user 2026-10-25), which turns Solaris Oak the Mighty off and Lunaris Fragment of Winter on"
      multiplierNearbyEnemies: "1 for a lone boss (Solaris one-enemy 6% additional physical reduction becomes the only nearby-enemy line that works; Lunaris per-enemy lines give 1% each): NOT VERIFIED how many adds stay near"
      conditionStationary: "scenario input; most boss fights move"
    reasoning: "a lone boss gives N = 1 and frequent hits; the Brine King stun lockout (once stunned or a stunning hit blocked, no stun for 2 seconds) matters on bosses that stun, but PoB does not read it (line unparsed), so its worth is a gap, see [[Stun]]; ground lines are off unless the arena has Burning or Caustic ground"
    source: "ConfigOptions.lua:1234-1236, 2086; Data/Pantheons.lua:11,69,114"
seeds: [EK, Worb, FR]
sources:
  - {ref: "https://www.poewiki.net/wiki/Deal_with_the_Bandits (rev 1596867)", kind: wiki, patch: "3.25.0 (reward rework); current 3.29"}
  - {ref: "https://www.poewiki.net/wiki/Pantheon (rev 1631432), with Template:Pantheon expanded through action=parse on 2026-10-26", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Recently (rev 1397426)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcSetup.lua:651-673, ConfigOptions.lua:32-44,136-154,158-177,1168-1174,1234-1236,1375-1378,1438, Build.lua:648-651,767-769,901-902, ImportTab.lua:1237-1240, PantheonTools.lua:6-19, CalcDefence.lua:1583,1591,2207, CalcPerform.lua:1626,1664", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/Pantheons.lua (all 41 lines), Data/ModCache.lua:3666,8368,10050,10953,14327,14791,18302,19265,22323,22813, Modules/ModParser.lua:1464,1775,2499,3104,4868-4870,4920,5752-5754,5903", kind: pob, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: the wiki Bandit page (rev 1649238) is a monster page; the choice rewards are taken from Deal with the Bandits only"
  - "NOT VERIFIED: that the player has captured every upgrade soul; PoB assumes it, and the base power alone has fewer lines (EK/Worb Brine King base = only the unparsed stun line)"
  - "NOT VERIFIED: why Shakari's 5% reduced Chaos Damage taken changes nothing on EK and FR, and why Ryslatha's Gorulis line changes nothing on FR (seed already immune or capped; not probed)"
  - "NOT VERIFIED: how many enemies stay near the player in a pinnacle boss fight, the stationary seconds, and the hit rate used for 'Recently' (only the user's 1 hit per second assumption exists)"
  - "NOT VERIFIED: whether the in-game stun lockout of the Brine King (2 seconds) is worth anything for the seed bosses; stun frequency of each boss is not sourced"
  - "NOT VERIFIED: Forest of Flames (Solaris) parse AvoidAilments with Condition:CriticalStrike never fires; reason read from the live parse only, not traced in CalcDefence"
  - "NOT VERIFIED: how a literal 'Eramir' behaves in the PoB GUI after saving; the dropdown shows 'Kill all' (selected value None, p1.json) and Build.lua:1024 (buildMode:Save) writes configTab.input.bandit unchanged"
  - "Config probes: n = 0 in S0 and n > 0 in A or B is the evidence for 'config'; the saved config of all three seeds sets none of the probed variables"
open_questions:
  - "Should the generator tick conditionBeenHitRecently on pinnacle bosses (turning Solaris Oak the Mighty off and Fragment of Winter on)? Suggested: yes, by the u >= 80% rule with E = 1 per second."
  - "Should the generator treat the Brine King stun lockout as value on stunning bosses although PoB cannot compute it (EHP delta 0 for the EK and Worb pair)?"
```
