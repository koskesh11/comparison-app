---
type: research
status: draft
pob_refs: [ForbiddenRite, ForbiddenRiteAltX, Cyclone, SupportCastOnCriticalStrike, SupportCastOnCritTriggered, SupportAwakenedCastOnCriticalStrike, AssassinsMark, ChaosCanShock, ChaosCanFreeze, ChaosCanChill, ShockMinimum, ShockBase, EnemyShockEffect, EnemyFreezeDuration, BifurcateCrit, CritChanceLucky, HaveTriggerBots, CooldownRecovery, GrantedAscendancyNode, conditionEnemyShocked, conditionShockEffect]
source: "PoB 2.67.2-beta install (TreeData/3_29/tree.lua, Data/, Modules/), user builds (read-only), poewiki API (Forbidden Rite, Occultist, Trickster, Assassin, Elementalist, Shock, Freeze, Forbidden Flame, Bloodline, Chaos Mastery, Like Clockwork, Shaper of Storms, Perfect Crime, Summon Triggerbots, Polymath, Knife in the Back; fetched 2026-10-21), poe.ninja Allflame snapshot 1136-20261021-32209 (protobuf + NDIC dictionaries decoded 2026-10-21)"
last_confirmed_patch: 3.29.x
---

# FR CoC Cyclone: ascendancy and passive tree (task 000, phase 1)

Paths are relative to the PoB install (`C:\Users\7800x3D\AppData\Roaming\Path of Building Community`).
`tree.lua` = `TreeData/3_29/tree.lua`; line = the node's first stat line. Sibling notes:
[[FR CoC Cyclone - skills and supports]], [[Foulborn Three Dragons - chaos shock and freeze]].
Trade-offs only, no verdicts. UNVERIFIED = not confirmed by PoB source or wiki.

## 0. What decides whether an ascendancy or tree node is worth anything here

| Mechanic | Evidence | So a node is worth something if it... |
|---|---|---|
| FR base damage = 14% max Life + 5% max ES (added chaos); self-hit 40% Life + 25% ES as chaos | `Data/Skills/act_int.lua:7468-7471`, applied in preDamageFunc `:7390-7417`. Wiki (Forbidden Rite, 3.29): self-hit also happens on CoC triggers | ...adds Life (2.8x the FR value of ES), ES, or chaos res (cuts the self-hit) |
| FR of Soul Sacrifice = 20% max ES; self-hit 50% ES | `act_int.lua:7615-7616` | ...adds ES (Life adds nothing to it) |
| CI: self-hit becomes 0 (`ChaosDamageTaken` MORE -100), but FR's Life part is about 0 | `Modules/ModParser.lua:2251-2253` | |
| CoC needs every Cyclone hit to crit and hit ([[CoC requires 100% crit and hit]]); CoC cooldown 0.15 s | `Data/Skills/sup_dex.lua:610`; PoB divides by cooldown recovery `Modules/CalcTriggers.lua:101,159`, server tick 0.033 s `Modules/Data.lua:238` | ...adds attack crit, accuracy, or cooldown recovery |
| Chaos damage counts towards shock/freeze only with `ChaosCanShock` / `ChaosCanFreeze` | `Modules/CalcOffence.lua:4313-4328` | |
| "Your Chaos Damage can Freeze" gives freeze only, not chill | `ModParser.lua:3638-3640` (generic `your (%w+) damage can (%w+)`); wiki Freeze: freezing damage "cannot inherently chill" (Three Dragons example) | chill-conditional nodes need another chill source |
| Crits always inflict the ailment if the damage can | `CalcOffence.lua:4245-4249`; wiki Shock: "Critical strikes inherently have 100% chance to shock" | FR spell crit chance = shock/freeze application chance |
| Shock = 50 x (damage / threshold)^0.4 x effect | `CalcOffence.lua:5352-5355` | shock effect nodes scale chaos shock |
| "effect of lightning ailments" / "non-damaging ailments" include shock; "effect of cold ailments" = chill + brittle only; "duration of cold ailments" includes freeze | `ModParser.lua:777, 783, 786-787, 799` | freeze needs duration, not effect (wiki Freeze agrees: effect mods do nothing for freeze) |
| PoB adds your own shock to DPS only with a guaranteed source (`ShockBase/Override/Minimum`) or the config "Is the enemy Shocked" + effect | `Modules/CalcPerform.lua:3565-3609`, `Modules/ConfigOptions.lua:1943-1948` | shock-effect nodes show **0 DPS in PoB** unless configured or Shaper of Storms; freeze is never in DPS. "No change in PoB" is not "no value" |
| "...if highest damage type is lightning / cold" never applies to FR (chaos is highest) | `ModParser.lua:2784-2790` | misread trap |

## 1. Ascendancies (3.29 tree)

**Occultist (Witch)**. ninja: 4 of 12 FR+CoC+Cyclone.
- Chaos: Withering Presence `tree.lua:44331` (15% more chaos, +60% chaos res = smaller FR self-hit if not CI, Withered aura); Void Beacon `:44249` (nearby -20% chaos res; the cold half does nothing here); 10% chaos small nodes (nodes at `:44286`, `:44409`).
- ES/FR scaling: 6% ES small nodes; Vile Bastion `:44228` (ES increased by spell block chance; the user's builds pair it with shield block nodes).
- Crit: none direct. Forbidden Power `:44271` (+1 max power charge, a charge per 200 mana spent); each power charge = 50% increased crit (`Data/Misc.lua:79`, `Modules/CalcSetup.lua:613`).
- Ailment: Frigid Wake `:44354` is its own cold freeze + 15% more **cold**; FR gets nothing from the cold part.
- Trigger: none. Unhallowed Rite `:44528` needs channelling a **spell**; Cyclone is a channelling attack, and PoB's buff only boosts channelling spells (`CalcPerform.lua:741-748`). No value for this build.
- Trade-off: best chaos multipliers + ES; no crit, hit or ailment help, so Three Dragons is still needed for both shock and freeze.

**Trickster (Shadow)**. ninja: 0 of 100 FR.
- Polymath `tree.lua:84164`: 2% more damage per mastery type (wiki: 3% to 2% in 3.26.0). Applies to FR.
- ES: Escape Artist `:84244`, 5% ES small nodes, Soul Drinker `:84007` (ES leech; "20% increased Attack and Cast Speed while Leeching ES" removed, `TreeData/3_26` vs `3_27`).
- Swift Killer `:84146` (+2 frenzy; frenzy gives no crit). One Step Ahead `:84088` changed from 108%/92% (3.26) to 90%/90% (3.27+).
- No crit, chaos, hit or ailment nodes. The value is defence + Polymath.

**Assassin (Shadow)**. ninja: 1 of 12.
- Crit for CoC: nine small nodes with 15% crit each (nodes `tree.lua:83324-83672`). Assassination Style picks one of:
  - Knife in the Back `:83285`: 100% more crit vs enemies **not** on Low Life.
  - For the Jugular `:83308`: 100% more crit only vs Low Life.
  - Trade-off: with Knife in the Back the more-crit drops off once the enemy is on Low Life, and CoC's 100% must still hold then (enemy Low Life % UNVERIFIED). PoB models it: `Data/ModCache.lua:4232`.
- Mystical Infusion `:83392` (3.29, wiki confirms): **spell** crit bifurcates, 30% less spell crit. It changes FR crit (and so FR's guaranteed shock/freeze), not Cyclone's CoC crit. PoB: `CalcOffence.lua:3131-3181`. Wiki: "always crit" effects stop bifurcation.
- Deathmarked `:83599`: triggers level 30 Assassin's Mark on an attack crit vs rare/unique (PoB grants it: `ModCache.lua:22239`); 10% mark effect per max power charge.
  - 3.29 removed "Marked Enemy cannot Evade Attacks" (wiki Assassin 3.29.0; `TreeData/3_27` vs `3_29`), so this hit-chance source is gone.
  - It only starts after a first crit.
- Unstable Infusion `:83536` (power charges); Opportunistic `:83660` (25% more with at most 1 rare/unique nearby). Life: one 4% small node only.

**Elementalist (Witch)**. ninja: 0 of 12 (1 of 100 FR).
- Shaper of Storms `tree.lua:50157`: Hits always Shock, All Damage can Shock, minimum 25% shock (wiki: 25% since 3.26.0).
  - This alone makes chaos shock work, so the helmet's chaos-shock line becomes redundant (overlap).
  - It is a guaranteed source (`ShockMinimum`, `ModParser.lua:2778`), so PoB then values shock-effect nodes in DPS.
- Shaper of Winter `:50179`: All Damage with Hits can Chill (gives `ChaosCanChill`, `ModParser.lua:2816-2821`). That is the chill the Three Dragons freeze does not give, and it turns on chill-conditional nodes.
- Small nodes: 10% lightning ailment effect (node `:50084`); "cold ailment effect" (`:50106`) is chill/brittle, not freeze.
- Mastermind of Discord `:49969` (exposure) affects elemental res only, so nothing for FR. No crit, chaos or ES.

**Saboteur (Shadow)**. ninja: 0.
- Like Clockwork `tree.lua:84696`: 50% cooldown recovery (wiki 3.28.0), giving more CoC triggers (`CalcTriggers.lua:101,159`). The user took it through Forbidden jewels.
- Perfect Crime `:84328`: Triggerbots trigger every triggered spell twice. PoB doubles the trigger rate (`CalcTriggers.lua:815-818`) and applies 30% less damage (`ModCache.lua:8390`), net x1.4.
  - Wiki: skill cost paid twice.
  - FR's self-hit (and the Chaos Mastery drain) probably doubles too: inferred from the wiki's "whenever the spell is used", UNVERIFIED.
- Calculated Risk `:84653`: lucky crit chance (eases 100% crit) but "Damage with Hits is Unlucky".
- Bomb Specialist `:84447`: FR is area damage; PoB averages it to 15% more (`ModCache.lua:16929`).
- Harness the Void `:90103` is hidden (Forbidden Flame only, wiki) and adds nothing to FR, which is already chaos.

**Others the evidence points to**
- **Pathfinder**: 6 of 12 FR+CoC+Cyclone on ninja, poison-focused.
  - Nature's Reprisal `tree.lua:83779` (Withered on hit, +50% Withered effect).
  - Master Distiller `:83740`: PoB excludes triggered **and** channelling skills from its crit (`ModParser.lua:2971-2973`), so neither Cyclone nor FR gets it.
- **Juggernaut**: 1 of 12. Undeniable `:15341` (+500 accuracy, accuracy from Str) is a hit-chance source; FR scales with Life.
- **Inquisitor** (user's VD Archmage):
  - Instruments of Justice `:16431`: FR base crit (6%, `act_int.lua:7489`) becomes the weapon's.
  - Righteous Providence `:16674`: crit.
  - Inevitable Judgement `:16694`: elemental res only, nothing for FR.
- **Hierophant**: Sanctuary of Thought `:15927` (20% mana as extra ES, FR ES scaling); Arcane Blessing `:15746`.
- **Warden** (id Raider; Ranger start, far from the int/chaos area; pathing cost UNVERIFIED):
  - Oath of Winter `:85068`: enemies you freeze stay frozen at least 2 s.
  - Oath of Spring `:84989`: up to 50 shocks at 2% max each; how TD chaos shocks stack is UNVERIFIED.
  - Fury of Nature `:90084` (100% more non-damaging ailment effect) sits under Warden in tree.lua but is a **hidden** notable: Forbidden Flame only, Ranger only (wiki).
- **Deadeye**: Endless Munitions `:85517` (+2 projectiles; FR's "All Primary Projectiles" part scales with projectile count, `act_int.lua:7414-7415`); Focal Point `:85422` (75% mark effect).
- **Reliquarian** (Scion), one option per "display" (tree.lua parent edges); cannot roll on Forbidden Flame (wiki); ninja 4 of 100 FR, 0 CoC:
  - Fidelitas' Spike `:20976`: Hits always Shock; "Deal no Physical Damage" costs FR nothing.
  - Polaric Devastation `:22345`: 40% ailment duration, which counts for freeze.
  - Xirgil's Crank `:21837`: +1 spell gems.
  - Presence of Chayula `:22634`: 20% Life converted to ES.
- **Ascendant** picks: Assassin `:20178` (+0.75% crit), Elementalist `:18653` (shocks at least 10%, a guaranteed source), Saboteur `:21157` (15% cooldown recovery), Occultist `:19082`, Trickster `:20533`.
- **Bloodlines** (wiki: 11, from endgame bosses, share ascendancy points; ninja: 88 of 100 FR use none):
  - Lycia Sinner Saint `:14266` converts elemental to chaos; FR is already chaos.
  - Breachlord Tul of the Blizzard `:15524`: 30% freeze duration.
- **Forbidden Flame + Flesh** adds a second ascendancy notable from the **same class** (`Modules/CalcSetup.lua:1401-1416`; wiki: class-locked).
  - Witch: Occultist + Shaper of Storms, or Elementalist + Withering Presence. Shadow: e.g. Trickster/Assassin + Like Clockwork.
  - All of these are in PoB's list (`ModCache.lua:13695-13997`); in-game roll pool for new 3.29 notables UNVERIFIED.

## 2. The user's builds (parsed read-only, active spec)

| Build (tree) | Ascendancy | Keystones (node ids allocated) | Masteries (crit/chaos/ailment related) | Notes |
|---|---|---|---|---|
| 3.26 FR CoC Occu No Mirror Helm (3_26) | Vile Bastion, Void Beacon, Forbidden Power, Withering Presence | Hex Master, Chaos Inoculation, Zealot's Oath | Critical: +3 crit support levels, +25% multi vs unique; Chaos: +1 chaos gems / lose 10%; Charge: 3% dmg per charge; ES x3 | FR of Soul Sacrifice + Awakened CoC + Cyclone; 22.2k ES; Militant Faith (Dominus), Megalomaniac, medium clusters (Pressure Points, Basics of Pain) |
| 3.26 Occu CoC FR YT, spec "30 Div Budget" (3_26) | Forbidden Power, Vile Bastion, Withering Presence, Void Beacon | Glancing Blows, Hex Master, CI | Critical +3; ES; Reservation | 3 large chaos clusters (Dark Ideation, Unholy Grace, Unwaveringly Evil); Militant Faith "3% increased Effect of non-Damaging Ailments per 10 Devotion"; CritChance stat 71.7% in this spec |
| 3.26 Trickster CoC (3_26) | One Step Ahead, Polymath, Escape Artist, Soul Drinker | Ghost Reaver, Ghost Dance, The Agnostic, CI | Chaos +1/lose 10%; Critical +3 and +25% vs unique; 13 masteries for Polymath | Forbidden Flame/Flesh: **Like Clockwork**; Militant Faith (Dominus). The Agnostic + CI with 12.7k ES means some keystones are conquered (Inner Conviction, `TimelessJewelData/LegionPassives.lua:11110`); which ones is UNVERIFIED |
| 3.27 Sabo BladeFall Reap (3_27) | Born in the Shadows, Calculated Risk, Bomb Specialist, Like Clockwork | CI | Chaos: 10% more vs ES enemies; Charge: 100% duration | CoC with Reap/Bladefall, FR on CwDT; Forbidden: **Perfect Crime**; Lethal Pride |
| 3.28 CoC VD Archmage (3_27, 8 specs) | Sanctuary, Inevitable Judgement, Righteous Providence, Pious Path | Mind Over Matter, Eldritch Battery | Critical: **50% increased Effect of non-Damaging Ailments with Crits**, +3 crit supports; Cold: chills at least 10% | CoC Lancing Steel to Detonate Dead/Immolate (fire). **Plain** Three Dragons (fire can shock, lightning can freeze) in item sets "COC Swap {2}" and "Level 95 {3}"; the active set "Level 98 {4}" uses a rare helmet |
| 3.28 Trickster Unholy Trinity Frostblade (3_28) | Swift Killer, Escape Artist, Polymath + **Sinner Saint** (Lycia) | Ghost Dance, Wind Dancer, Acrobatics | Critical: 50% non-damaging ailment effect with crits; ES: 30% chaos not bypassing ES | **Foulborn** Three Dragons: kept "Cold can Ignite but not Freeze or Chill", mutated "Chaos can Freeze" + "Chaos can Shock". Frost Blades converted to chaos by Sinner Saint 67% + Foulborn Green Nightmare (cold to chaos in radius), so chaos does the freezing and shocking and leftover cold cannot (the kept downside is why conversion is the point). Forbidden: Mistwalker |

Since 3.26 (tree diff): Soul Drinker lost its speed line, One Step Ahead changed, Like Clockwork went 30% to 50%, Polymath 3% to 2%, and Calculated Risk gained "enemies' damage Unlucky". The 3.26 numbers need a re-check on 3_29.

## 3. Passive tree: what matters (3_29)

**Keystones**
- Ruled out by CoC (never crit): Resolute Technique `tree.lua:21817`, Precise Technique `:68373`.
- Crits deal no extra damage: Elemental Overload `:39958` (its 40% more is elemental only), Perfect Agony `:80926`.
- **Secrets of Suffering** `:85638` (cluster keystone): cannot Chill/Freeze/Shock, so it cancels the helmet's point (crits apply Brittle/Sapped instead).
- CI `:74130` vs Life (Section 0 trade-off).
- Seen with this archetype: Eldritch Battery `:67101` (6 of 12 on ninja), Zealot's Oath `:26697`, Ghost Reaver `:80297`, Ghost Dance `:79901`, Hex Master `:63127`, Glancing Blows `:28431`, Mind Over Matter `:40257`.
- Pain Attunement `:62458` (30% more spell damage on Low Life; 3 of 12 on ninja). The FR self-hit is relevant to staying on Low Life, UNVERIFIED as a plan.
- Solipsism `:55153` costs Int-to-ES.

**Crit for Cyclone** (attack or global; Cyclone is melee)
- Assassination `:71828`, True Strike `:58881`, Eagle Eye `:39299`, Depth Perception `:80224`, Disemboweling `:23912`, Dismembering `:41036`.
- Clusters: Pressure Points `:86010`, Basics of Pain `:86069`.
- Critical Mastery +3 to crit supports `:23957` (CoC is tagged critical: `Data/Gems.lua:4857-4858`; level effect is in the skills note).
- High Voltage `:69734` (100% crit vs Shocked): chaos shock feeds Cyclone crit, but the first hit on an unshocked enemy must already crit.

**FR crit** (shock/freeze application, and bifurcation for Assassin): Doom Cast `:77065`, Annihilation `:51179`, Arcane Potency `:28455`.

**Hit for CoC**
- Accuracy Mastery "Gain Accuracy Rating equal to your Intelligence" `:22969` (big on Int-stacked CI).
- Mark Mastery "50% more Accuracy against Marked Enemy" `:66727` (all six builds run Assassin's Mark; PoB `ModCache.lua:10333`).
- Accuracy notables listed under Crit above (Eagle Eye, Depth Perception), plus Acuity `:79694`.

**Chaos damage**
- Heart of Darkness `:41179`, Force of Darkness `:47660` (15% chaos pen), Atrophy `:76750`, Corruption `:41275` (Withered effect).
- Cleansed Thoughts `:67619` (chaos res doubled: smaller self-hit when not CI).
- Clusters: Unholy Grace `:87276`, Unwaveringly Evil `:87248`, Wicked Pall `:87286`, Dark Ideation `:87267`, Touch of Cruelty `:87235`.
- Chaos Mastery "+1 Chaos gems / Lose 10% of Life and ES when you use a Chaos Skill" `:41327`. **PoB applies only the +1**: the "lose 10%" line is parsed with leftover text (`ModCache.lua:17462`) and skipped (`Classes/PassiveTree.lua:860-866`). Whether each CoC trigger counts as a "use" is UNVERIFIED; the wiki says FR's self-hit does.

**Shock** (works for chaos-inflicted shock in PoB; 0 DPS shown unless configured or with a guaranteed source)
- Breath of Lightning `:50820`, Static Blows `:59749`, Elemental Focus `:71924`, Ash, Frost and Storm `:46344`, Overshock `:87767`, Astonishing Affliction `:87664`.
- Critical Mastery "50% increased Effect of non-Damaging Ailments you inflict with Critical Strikes" `:23936`.
- Lightning Mastery `:43027` (+15% max shock), `:43036` (shock spread), `:43042` (max mana applies to shock effect at 30%; PoB parses it, `ModCache.lua:17155`).
- Curse Mastery +20% chance to Freeze/Shock cursed enemies `:36740`. Holy Dominion `:30851` (10% chance).

**Freeze** (duration only; never in PoB DPS)
- Winter's Embrace `:64852`, Breath of Rime `:54708`, Lasting Tempest `:55514`, Elemental Focus.
- Cold Mastery "Enemies permanently take 5% increased Damage for each second they've ever been Frozen by you, up to 50%" `:54795` (PoB parses it, `ModCache.lua:15366`).
- Blast-Freeze `:87735` (spread).

**Traps** (look relevant but are not)
- Storm Weaver `:34801` and Sadist `:87051`: elemental damage only.
- Fingers of Frost `:61759`, Glacial Cage `:64789`: need chill, which chaos freeze does not give (Shaper of Winter or another chill source does).

**ES/Life**: Written in Blood `:75277` (both), Unnatural Calm `:40718`; for life FR, Divine Flesh (Glorious Vanity, +5% max chaos res, `LegionPassives.lua:7364`; 73 of 100 FR on ninja).

**Jewel radius**: the user's Militant Faith rolls (non-damaging ailment effect per Devotion; conquered keystones) and Foulborn Green Nightmare change what "empty-looking" nodes do. Audit tree nodes together with the jewel in radius.

## 4. poe.ninja (Allflame, snapshot 1136-20261021-32209)

- **Decoding**: generic protobuf; dimension = {1: name, 2: dictionary, 3: [(index, count)]}. Dictionaries come from `GET /poe1/api/builds/dictionary/<sha1>` in an `NDIC` format: a header, then a block table, then length-prefixed strings.
- Totals: 124,393 characters. `skills=Forbidden Rite`: **100**.
- Filters combine with repeated params; `&skills=A,B` is ignored, which returned the unfiltered total.
- FR (100): Pathfinder 71, Occultist 12, Reliquarian 4, Hierophant 3, Necromancer 3, Assassin 2, Ascendant/Chieftain/Elementalist/Inquisitor/Juggernaut 1 each; Trickster 0.
  - Skills: Unhinge 68, Cyclone 12. CoC support on FR: 13. Bloodline: None 88.
- FR + `allgems=Cast On Critical Strike Support`: **13**. FR + Cyclone (main skill) + CoC: **12**.
  - Ascendancy: Pathfinder 6, Occultist 4, Assassin 1, Juggernaut 1. Weapons: 11 Dagger/Shield, 1 Staff.
  - Keypassives: CI 4, Vile Bastion 4, Void Beacon 4, Withering Presence 4, Zealot's Oath 3, Pain Attunement 3, Eldritch Battery 6.
- FR + The Three Dragons (either variant): **0**. Foulborn Three Dragons overall: 80 (71 Chieftain, mostly Scorching Ray of Immolation; 4 Hexblast of Havoc). Plain: 19.
- Not decodable from these dims: which Foulborn mutation an item has.

## 5. Contradictions between sources

- **Unhallowed Rite**:
  - PoB tree.lua `:44528`: "every 0.5 seconds"; PoB model: 15% recharge, 5% more channelling-spell damage, 10% more cost, 10 stacks (`CalcPerform.lua:741-748, 1017`).
  - Wiki Occultist 3.29.0: "every second", 30% / 10% / 20% per stack, 5 stacks.
  - Irrelevant for Cyclone, but PoB and the wiki disagree.
- **Fury of Nature** and **Harness the Void** sit under normal ascendancies in tree.lua; the wiki says they are hidden notables, Forbidden Flame only.
- **Deathmarked** "cannot Evade" is gone in 3.29 (wiki and the tree agree); any 3.27/3.28 plan relying on it for hit chance is outdated.

## 6. Open questions

- In-game, does "Lose 10% of Life and ES when you use a Chaos Skill" fire on every CoC trigger? With Triggerbots, does FR self-hit twice?
- Enemy Low Life threshold for Knife in the Back (CoC crit hole).
- Can Forbidden jewels roll the 3.29-new notables in game?
- Oath of Spring stacking with chaos shock.
- Which keystones Militant Faith converts in the user's 3.26 builds.

Failure-mode check: freeze and shock nodes flagged as "0 in PoB, not 0 value". Every skill was evaluated together (Cyclone crit/hit vs FR crit/ailment vs FR self-hit). Hidden/radius nodes are flagged. Downsides that are the point (Fidelitas' Spike "no physical", the Three Dragons kept cold line) are noted. Unconfirmed items are marked UNVERIFIED.
