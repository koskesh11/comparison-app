---
type: interaction
status: draft
pob_refs: [StunAvoidChance, StunThreshold, SelfStunChance, StunDuration, BlockDuration, InterruptStunAvoidChance, StunImmune, AvoidStun, AvoidInterruptStun, StunThreshold, StunRecovery, conditionBeenHitRecently, conditionBlockedRecently, conditionStunnedRecently]
source: "poewiki Stun rev 1619327, Immunity rev 1674448, The Maven rev 1700636 (fetched 2026-10-26); PoB 2.67.2 CalcDefence.lua:2151-2250, Data.lua:275-278, ModParser.lua, TreeData/3_29/tree.lua; live parse of every quoted line (b1c-mechanics-immunity.md); EK sample probe (b1c-pob-flasks.md)"
last_confirmed_patch: "3.29.x"
---

Hits stun the player when their damage is large against the stun threshold (normally maximum life): chance = 200 x damage / effective maximum life, ignored at 20% or less, always at 50% or more of life. Damage over time, reflected damage and self-damage cannot stun, and stun is decided before block. Defences are Cannot be Stunned, a chance to avoid, a higher stun threshold, a shorter stun (recovery), and the baseline 50% chance to ignore a stun when you had any energy shield before the hit (Eldritch Battery removes it). Enemy-side stun is a different mechanic and not in this note. Related: [[Block]], [[Energy shield and hybrid]], [[Chance on hit uptime]], [[Defences]].
Impact: PoB reads the configured enemy hit and gives StunAvoidChance, SelfStunChance and the durations; its ES roll is stricter than the wiki (see mechanic), and 'if you haven't been Hit Recently' style conditions are config ticks with no hit-rate behind them. EK sample (CI, ES 5,189): StunAvoidChance 50 in every flask-off probe, i.e. consistent with the 50% energy shield roll (the source was not traced).
Pipeline: [[Receiving damage#Block]] - the wiki puts stun (step 8) before block (step 10) and has no heading for it; [[Defences#Energy shield]] holds the ES layer the 50% roll depends on.

```interaction
id: stun
mechanic: "Stun on you: chance = 200 x hit damage / effective max life (ignored at 20% or less, certain at 50% or more), base duration 0.35 s; avoided by Cannot be Stunned, a chance to avoid, or the 50% energy shield roll; rolls are multiplicative; stun comes before block; damage over time cannot stun"
family: defence
pipeline_step: ["Receiving damage#Block", "Defences#Energy shield"]
pipeline_why: "wiki step 8 'Being stunned' sits after damage mitigation and before block (step 10, no heading of its own in the pipeline note); the ES roll needs energy shield present before the hit"
target: self
related: [block, energy-shield-hybrid, chance-on-hit-uptime, defences, elemental-ailment-immunity, bleed-poison-cb-immunity]
pob:
  measured: partial
  how: "Modules/CalcDefence.lua:2151-2250: StunThreshold = life (or ES / Mana based; Chaos Inoculation uses pre-CI life; plus ES% added) x (1 + INC StunThreshold) (:2178); notAvoidChance = 0 if StunImmune else 100 - min(100, AvoidStun) (:2180); x0.5 if ES > totalTakenHit and not EnergyShieldProtectsMana (:2181-2183); StunAvoidChance = 100 - notAvoidChance (:2184); at 100: StunDuration = BlockDuration = 0 (:2197-2199), else StunDuration = ceil(0.35 x (1 + INC StunDuration) / (1 + INC StunRecovery) x tick) / tick (:2209), BlockDuration likewise with BlockRecovery (:2210); InterruptStunAvoidChance = min(100, AvoidInterruptStun) (:2231); SelfStunChance = (min(200 x effectiveEnemyDamage / StunThreshold, 100) if above 20, else 0) x notAvoidChance (:2238-2239). Constants Modules/Data.lua:275-278 (MinStunChanceNeeded 20, StunBaseMult 200, StunBaseDuration 0.35, StunNotMeleeDamageMult 0.75) equal the wiki values. Displayed Modules/CalcSections.lua:1878-1881. Immunity flag via modDB:Flag(nil, 'StunImmune'). SelfStunChance depends on the configured enemy hit damage, so it is scenario-dependent. Not verified against the wiki: effectiveEnemyDamage (:2232-2237 = totalTakenHit + 0.25 x physical, then x0.75 or a mixed factor by damage category) is an approximation of the wiki's melee / non-melee stunning-damage formula."
  config:
    - {var: conditionBeenHitRecently, default: false, ref: "Modules/ConfigOptions.lua:1375 (type check, no explicit default)", class: b}
    - {var: conditionBlockedRecently, default: false, ref: "Modules/ConfigOptions.lua:1421", class: b}
    - {var: conditionStunnedRecently, default: false, ref: "Modules/ConfigOptions.lua:1357", class: b}
    - {var: conditionStunnedWhileCastingRecently, default: false, ref: "Modules/ConfigOptions.lua:1513", class: b}
    - {var: conditionHaveEnergyShield, default: false, ref: "Modules/ConfigOptions.lua:192 ('Do you always have Energy Shield?'; needed by Occultist Vile Bastion)", class: b}
    - {var: enemy hit damage and damage category, default: "scenario setting", ref: "Modules/CalcDefence.lua:2232-2239 (config var names not looked up)", class: b}
  unparsed:
    - "Soul of the Brine King: You cannot be Stunned if you've been Stunned or Blocked a Stunning Hit in the past 2 seconds (Pantheons.lua:10-11) and Nassar 30% increased Stun and Block Recovery (Pantheons.lua:16-17) - not parsed"
    - "Physical Mastery (effect 20173): Cannot be Stunned by Hits that deal only Physical Damage - not parsed"
    - "Orbala's Stand: Cannot be Stunned by Suppressed Spell Damage (boots.lua:288) - not parsed"
    - "Mark of the Elder / Shaper: cannot be Stunned by Attacks / Spells if the opposite ring is ... (ring.lua:837,851) - not parsed"
    - "Cannot be Stunned if you have at least 25 Rage (wording variant; the real tree text 'while you have at least 25 Rage' parses) and 'You cannot be Stunned while at maximum Endurance Charges' (parses only in the 'you cannot' form, ModParser.lua:2591)"
    - "Not modelled in CalcDefence: cold-crit stun exception (3.28.0 fix) and 'Hits against you cannot be crits if stunned recently'"
    - "Cannot be Stunned if you've been Stunned during Effect (Corundum flask suffix) - unparsed (b1c-pob-flasks.md)"
model:
  proposed_kind: conditional_stun_immunity_uptime
  inputs: {from_pob: [SelfStunChance, StunAvoidChance, StunDuration, "hits per second the build takes (no PoB output field exists for it)"], from_scenario: [hit rate of the enemy, fight length]}
  params: {recently_window_s: "not read; PoB has no output field for it", es_roll_wiki: 50, es_roll_pob_condition: "ES > totalTakenHit"}
  formula: "for 'Cannot be Stunned if you haven't been Hit Recently', 'while Leeching', 'while Bleeding' style conditions use the vault Chance on hit uptime model with the hit-taken rate; the ES roll counts 50% whenever the build has any energy shield before the hit (wiki) and only when ES > incoming hit in PoB, so PoB is the conservative reading. Stun matters when SelfStunChance x hits per second x StunDuration is a real share of fight time."
  calibration: "no norm found (PoB output has no hits-taken-per-second field; the generator derives it from the scenario)"
providers:
  - {kind: unique, name: "Cannot be Stunned uniques", slot: amulet / helmet / staff, role: enables, target: self, text: "Eye of Chayula, Presence of Chayula (amulet), Ezomyte Hold (helmet), Atziri's Rule (staff): Cannot be Stunned", source: "Data/Uniques/amulet.lua:416,427; helmet.lua:67; staff.lua:104", pob: full}
  - {kind: keystone, name: "Unwavering Stance", slot: tree, role: enables, target: self, text: "Cannot be Stunned (also Reliquarian Kaom's Roots and Presence of Chayula nodes); lane 3 owns the keystone", source: "TreeData/3_29/tree.lua (node 40907; Reliquarian nodes 35448 / 54569)", pob: full}
  - {kind: ascendancy, name: "Juggernaut Unstoppable", slot: tree, role: enables, target: self, text: "Cannot be Stunned (node 5819; Ascendant copy node 61072)", source: "TreeData/3_29/tree.lua (node 5819, 61072)", pob: full}
  - {kind: ascendancy, name: "Conditional Cannot be Stunned: Occultist Vile Bastion, Slayer Endless Hunger, Berserker 25 Rage, Aul Precursor's Release", slot: tree, role: enables, target: self, text: "Vile Bastion: while you have Energy Shield (node 37492); Endless Hunger: while Leeching (node 34484); Berserker / Ascendant: while you have at least 25 Rage (node 4194); Precursor's Release: if you have an Equipped Helmet with no Socketed Gems (node 9437). Also Evasion Mastery 'if you haven't been Hit Recently' (effect 25487), Lioneye's Paws variant 1 on Low Life, Craiceann's Tracks (10 Crab Barriers / variant 2 while Bleeding), Bound by Destiny items", variant: "Lioneye's Paws variant 1; Craiceann's Tracks variant 2", source: "TreeData/3_29/tree.lua (nodes 37492, 34484, 4194, 9437; effect 25487); Data/Uniques/boots.lua:809,15,70; Special/BoundByDestiny.lua:41", pob: partial}
  - {kind: notable, name: "Stun Avoidance small, Life and Stun Avoidance, Heart of Oak, Perfectionist, Unwavering Focus; Shield Mastery", slot: tree, role: scales, target: self, text: "15% / 8% / 20% / 30% chance to Avoid being Stunned; Unwavering Focus 50% while Channelling; Shield Mastery 30% while holding a Shield (effect 45263, live parse OK)", source: "TreeData/3_29/tree.lua (nodes 1427, 32117, 65210, 18707, 38275; effect 45263)", pob: full}
  - {kind: notable, name: "Ignore Stuns while Casting: Avoid Interruption, Practical Application, Conjured Barrier, Practiced Caster; Asenath's / Sandstorm Visage", slot: tree / helmet, role: scales, target: self, text: "15% / 25% / 30% / 35% chance to Ignore Stuns while Casting; a separate roll from avoid stun, output InterruptStunAvoidChance", source: "TreeData/3_29/tree.lua (scan in b1c-mechanics-immunity.md); Data/Uniques/helmet.lua:625; Modules/CalcDefence.lua:2231", pob: full}
  - {kind: flask, name: "of Composure / Surefootedness / Persistence / Relentlessness / Tenaciousness (utility); Kiara's Determination; Veiled of the Order", slot: flask, role: scales, target: self, text: "(31-35 .. 51-55)% chance to Avoid being Stunned during Effect (lv 12 / 29 / 46 / 63 / 80, flask-local stat); Kiara's Determination: Immunity to Freeze, Chill, Curses and Stuns during Effect (live parse StunImmune under UsingFlask); Veiled of the Order 50%", source: "Data/ModFlask.lua:155-159; Data/Uniques/flask.lua:268; Data/ModVeiled.lua:189-190", pob: full}
  - {kind: unique, name: "avoid-stun items and crafts: Warrior's Legacy, Saemus' Gift, Lakishu's Blade, The Coming Calamity, corrupted jewel, Veiled prefix, tattoo, jewel suffix", slot: any, role: scales, target: self, text: "30% / 20% / 20% / 35% per Herald chance to Avoid being Stunned; corrupted jewel (20-25)%; Veiled prefix (30-35)% Avoid Elemental Ailments and Avoid being Stunned; tattoo 10%; jewel suffix (6-8)%", source: "Data/Uniques/ring.lua:1620; quiver.lua:262; sword.lua:254; body.lua:557; Data/ModJewel.lua:41,209; Data/ModVeiled.lua:5,222; Data/TattooPassives.lua:4117-4120", pob: full}
  - {kind: notable, name: "Stun Threshold: Stun Threshold small, Warrior's Blood, Uncompromising, Unfaltering; Survivor's Guilt; Rage Mastery; Energy Shield Mastery", slot: tree / belt, role: scales, target: self, text: "increased Stun Threshold 15% / 20% / 20% / 50%; Survivor's Guilt 20%; Rage Mastery every Rage grants 1%; Energy Shield Mastery adds 50% of your Energy Shield to the Stun Threshold (effect 571)", source: "TreeData/3_29/tree.lua (nodes by name; effects 2498, 571); Data/Uniques/belt.lua:954", pob: full}
  - {kind: unique, name: "Stun Threshold base change: Skyforth, Valyrium", slot: boots / ring, role: scales, target: self, text: "Skyforth: Stun Threshold is based on 500% of your Mana instead of Life; Valyrium: Stun Threshold is based on Energy Shield instead of Life (live parse StunThresholdBasedOnManaInsteadOfLife etc.)", source: "Data/Uniques/boots.lua:611; ring.lua:1485; Modules/CalcDefence.lua:2178", pob: full}
  - {kind: notable, name: "increased Stun and Block Recovery: Trial of the Faith, Conjured Barrier, Perfectionist, Pure Might, Armour and Evasion Mastery, belts", slot: tree / belt, role: scales, target: self, text: "shortens the stun and the block animation: 50% / 50% / 50% / 40% / 80% (effect 5108) / belts 15-25%; stun duration = 350 ms x (100 + attacker stun duration) / (100 + recovery)", source: "TreeData/3_29/tree.lua (effect 5108); Data/Uniques/belt.lua:14; Modules/CalcDefence.lua:2204-2213", pob: full}
  - {kind: mod, name: "Pantheon: Soul of the Brine King, Nassar upgrade", slot: pantheon, role: enables, target: self, text: "You cannot be Stunned if you've been Stunned or Blocked a Stunning Hit in the past 2 seconds; 30% increased Stun and Block Recovery", source: "Data/Pantheons.lua:10-11,16-17; wiki Immunity rev 1674448", pob: none}
makes_redundant:
  - {provider: "Avoid-stun chance and the ES roll", when: "StunImmune (Cannot be Stunned) is set", why: "PoB sets notAvoidChance 0 first, so every other avoid source is ignored", source: "Modules/CalcDefence.lua:2180"}
  - {provider: "Stun threshold and recovery", when: "StunAvoidChance reaches 100", why: "PoB sets StunDuration and BlockDuration to 0", source: "Modules/CalcDefence.lua:2197-2199"}
conflicts:
  - {with: "Eldritch Battery", effect: "removes the baseline 50% chance to ignore a stun when you have energy shield", source: "poewiki Stun rev 1619327"}
  - {with: "wiki ES roll versus PoB", effect: "wiki: the 50% ES roll applies if the defender had ES before the hit, even if the hit emptied it; PoB applies it only when output.EnergyShield > totalTakenHit (its own comment: 'POB only applies this modifier when ES > Total incoming damage'), so PoB undercounts avoid-stun for low-ES builds (conservative)", source: "poewiki Stun rev 1619327; Modules/CalcDefence.lua:2181,2194"}
  - {with: "Chaos Inoculation", effect: "stun threshold uses the maximum life the character would have without CI (wiki and PoB agree)", source: "poewiki Stun rev 1619327; Modules/CalcDefence.lua:2178"}
conditions:
  - {text: "Generator requirement per scenario - Mapping: no norm found; no expert statement that stun immunity is required in maps (wiki: hits above 20% of the threshold can stun)", source: "poewiki Stun rev 1619327; b1c-mechanics-immunity.md"}
  - {text: "Generator requirement per scenario - Pinnacle Boss: no norm found for the player's stun immunity. The Maven page lists 'cannot be stunned while stunned / for 4 seconds after stun finished' for the BOSS (enemy side, not a player requirement). A 3.25 Occultist guide claim of 'stun immunity' from a web-search summary is not usable (source not opened)", source: "poewiki The Maven rev 1700636; b1c-mechanics-immunity.md"}
  - {text: "Version history: 3.22.0 stun immunity removed from many bosses (Kitava still cannot be stunned); 3.11.0 many bosses immune to stun while stunned; 3.21 harder to stun with hits for almost all skills (melee untouched, wiki formula not updated)", source: "poewiki Stun rev 1619327"}
  - {text: "Conditional Cannot be Stunned lines (haven't been Hit Recently, blocked recently, Leeching, Bleeding, 25 Rage) count only with their config tick or condition; PoB has no hit-rate behind them, so the generator applies the Chance on hit uptime model with its own hits-taken rate", source: "Modules/ConfigOptions.lua:1357,1375,1421,1513"}
uptime:
  Mapping:
    value: pob
    config: {}
    reasoning: "permanent sources (items, tree, ascendancy, threshold) are always up and PoB's StunAvoidChance / StunThreshold count them; conditional immunities need their condition and a hit rate; use PoB's SelfStunChance for the configured hit"
    source: "Modules/CalcDefence.lua:2178-2239"
  Pinnacle Boss:
    value: model
    config: {conditionBeenHitRecently: "model: share of time with no hit in the Recently window at the boss hit rate"}
    reasoning: "a boss hits hard, so SelfStunChance is high unless Cannot be Stunned is permanent; 'if you haven't been Hit Recently' style immunities are mostly down against a fast boss, which the conditional_stun_immunity_uptime model computes from the hit rate"
    source: "Modules/ConfigOptions.lua:1375; Modules/CalcDefence.lua:2238-2239"
seeds: [EK]
sources:
  - {ref: "https://www.poewiki.net/wiki/Stun (rev 1619327; 3.28.0 cold-crit fix, 3.22.0 boss stun immunity removed, 3.21 stun harder, 3.11.0 bosses immune while stunned)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Immunity (rev 1674448); https://www.poewiki.net/wiki/The_Maven (rev 1700636)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcDefence.lua:2151-2250; Modules/Data.lua:275-278; Modules/ConfigOptions.lua; Data/ModFlask.lua:155-159; Data/Pantheons.lua; TreeData/3_29/tree.lua (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b1c-mechanics-immunity.md; tasks/reports/027-evidence/b1c-pob-flasks.md", kind: discovery, patch: "3.29"}
not_verified:
  - "whether PoB's effectiveEnemyDamage (CalcDefence.lua:2232-2237) or the wiki's stunning-damage formula is exact (the wiki notes the 3.21 change is not in its formula)"
  - "the length of the Recently window and the hits-taken rate are open inputs of the model, not read from a PoB output"
  - "source of EK's StunAvoidChance 50 (consistent with the ES roll, not traced)"
  - "config var names for the enemy hit damage and damage category"
  - "tattoo mapping for avoid stun (TattooPassives.lua:4117-4120; override type order not confirmed)"
  - "live PoB parse of the unique, tree and ascendancy lines was not run line by line; they count as parsed because they are absent from the unparsed list in the evidence"
  - "the 3.25 Occultist guide claim of stun immunity (web-search summary only)"
open_questions:
  - "Does the user want the ES roll modelled as the wiki states (any ES before the hit) instead of PoB's stricter reading?"
  - "No norm for stun immunity was found for any scenario; should the generator treat Cannot be Stunned as a scored preference only?"
```
