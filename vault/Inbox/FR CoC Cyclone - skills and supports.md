---
type: research
status: draft
pob_refs: [ForbiddenRite, ForbiddenRiteAltX, Cyclone, CycloneAltX, SupportCastOnCriticalStrike, SupportCastOnCritTriggered, SupportAwakenedCastOnCriticalStrike, SupportCastOnCritTriggeredPlus, SupportCooldownRecovery, SupportGreaterVolley, SupportGreaterMultipleProjectiles, SupportVoidManipulation, SupportIncreasedCriticalDamage, SupportPowerChargeOnCritical, SupportWitheringTouch, SupportElementalFocus, SupportControlledDestruction, SupportInspiration, TriggerRateCap, SkillTriggerRate, EffectiveSourceRate, FRDamageTaken, ManaPerSecondCost, ESPerSecondCost, CostESInsteadOfManaOrLife]
source: "PoB Community install (launch.versionNumber 2.67.2-16de4b82d, gem data 3.29) Data/Skills + Modules, file:line below; PoB headless runs on the user's 3.26 builds (in memory, nothing saved); poewiki API (action=parse) pages Forbidden Rite, Forbidden Rite of Soul Sacrifice, Cast On Critical Strike Support, Awakened Cast On Critical Strike Support, Cooldown Recovery Support, Cyclone, Greater Volley Support, Greater Multiple Projectiles Support, Whispers of Infinity, Energy Leech Support; PoB changelog.txt"
last_confirmed_patch: 3.29.x
---

# FR CoC Cyclone: skills and supports (task 000, phase 1)

Covers skills and supports only. The Foulborn Three Dragons helmet is covered in a separate note.
Paths: `Data/...` and `Modules/...` are relative to `%APPDATA%\Path of Building Community`.
"PoB run" means a headless calculation on a user build, changed in memory only (never saved).
The 3.26 builds keep their 3.26 tree and their saved item text, so PoB-run numbers show **direction and size**
of a change. They do not describe a valid 3.29 character.

## 1. Forbidden Rite (FR) in PoB 3.29

| | Forbidden Rite (`ForbiddenRite`) | FR of Soul Sacrifice (`ForbiddenRiteAltX`) |
|---|---|---|
| Base chaos damage added | 14% max Life + 5% max ES (`act_int.lua:7468-7471`) | 20% max ES only (`act_int.lua:7615`) |
| Self-hit per cast | 40% Life + 25% ES as chaos (`:7468,7471`) | 50% ES as chaos (`:7616`) |
| Cost L1→L20 (L21/L24) | 8→21 **Mana** (22/23) (`:7489-7512`) | 18→45 **Life** (46/51) (`:7634-7657`) |
| Common | Spell, Damage, Area, Chaos, Projectile, ProjectilesFromUser, Triggerable, Multicastable, CanRapidFire (`:7379`); cast 0.75 s; crit 6%; 110% added-damage effectiveness; **no cooldown**; secondary projectiles 6 (L1-10), 7 (L11-20), 8 (L21+); quality: +0.1 secondary projectile per 1% (`:7464-7466`) | same (`:7538`, `:7611-7613`) |

- Gem tags: Spell, AoE, Chaos, Projectile; 100 Int weighting (`Gems.lua:12983-13002`).
- Damage formula (`act_int.lua:7409-7413`): `add = Life*0.14 + ES*0.05` is added to the skill's **base** chaos min/max.
  Base damage is not multiplied by damage effectiveness. Only *added* flat damage is ×1.1
  (`CalcOffence.lua:3351-3356`). The gem's own flat base (498-747 at L20, wiki) is small next to the Life/ES part.
- **Scales with:** max Life/ES (also temporary buffs, wiki); increased/more Damage, Spell, Chaos, Projectile and
  Area damage (baseFlags spell/projectile/area, `:7456-7460`); FR crit chance and multiplier; flat added chaos ×1.1.
- **Does not scale with:** attack modifiers, Cyclone damage, cast speed (triggered: speed = trigger rate,
  `CalcOffence.lua:2291-2295`), or chain/fork/pierce. Wiki (current page): "does not benefit from Chain, Fork, Split,
  Pierce or any projectile behaviour modifiers"; `projectile_behaviour_only_explode` (`act_int.lua:7480`).
- **Projectiles (wiki, current page):** "on single target, two projectiles will hit the enemy. Sources of additional
  projectiles will only add projectiles to the initial cursor-targeted projectile". The wiki also recommends "not to get
  more than +4 additional projectiles … due to the tendency for projectiles to miss on smaller single targets".
  PoB part 2 "All Primary Projectiles" multiplies DPS by `ProjectileCount + 1` (`act_int.lua:7414-7416`). That matches
  the wiki's "+1 secondary", but it assumes **every** primary projectile hits.
- **Self-damage:** wiki: the self-hit also happens when FR is triggered. It is secondary damage, "does not count as a cost",
  "cannot be blocked, dodged, evaded or reduced by spell suppression". PoB computes it per cast as `FRDamageTaken`
  (`act_int.lua:7410-7417`). The damage-taken multiplier is 0 under Chaos Inoculation (PoB run: "* 0.00").
  **PoB gap:** PoB never turns the self-hit into damage per second (self-hit × trigger rate) or into a recovery drain.
  Also, its "Self hit Damage" total loops with `ipairs` over a string-keyed table, so FR never adds to it
  (`CalcOffence.lua:6088-6090`; found by reading the code, not by a test).
- Wiki 3.29.0: "Forbidden Rite Now deals 14% of your maximum Life as base Chaos Damage (previously 12%)". PoB data matches.
  Wiki 3.26.0 (Soul Sacrifice): 20% ES base (was 15%) and 50% ES self-hit (was 40%).
  Wiki (Soul Sacrifice): it costs Life, so it "cannot be used with Chaos Inoculation" unless the cost is converted
  (Whispers of Infinity).

## 2. Cast On Critical Strike (CoC) and Awakened CoC

- **Attack part** (`sup_dex.lua:519-583`): requires Attack. Excludes Trapped, RemoteMined, SummonsTotem, HasReservation
  and DisallowTriggerSupports. Quality: +1% attack crit chance per 1%. Cost multiplier 120%.
- **Spell part** (`sup_dex.lua:584-651`): requires Spell AND Triggerable. Adds the **Triggered and Cooldown** types.
  Excludes Trapped, RemoteMined, SummonsTotem, HasReservation, InbuiltTrigger and DisallowTriggerSupports.
  Cooldown 0.15 s, 1 stored use. Quality: +1% spell crit chance per 1%.
  Damage: 19% less (L1) to 10% less (L20), 9% less (L21) (`:610-630`). `spell_uncastable_if_triggerable`: FR in the
  link cannot be cast by hand.
- **Awakened** (`sup_dex.lua:652-748`): 9% less (L1) to 7% less (L5/L6), +10/13/16/19/22/25% Cooldown Recovery Rate
  at L1-6 (`:727-732`), same 0.15 s. Marked `legacy = true` (`:663`). Wiki 3.28.0: "All Awakened Support Gems can no
  longer be obtained, except for Awakened Empower, Awakened Enlighten and Awakened Enhance". PoB 2.61.0 (3.28):
  "Hide legacy awakened gems from dropdown" (`changelog.txt:456`). The same applies to Awakened Void Manipulation
  and Awakened GMP.
- Wiki: no CoC change since 3.17.0. The PoB changelog has no CoC trigger-calc change since 3.26 (searched `changelog.txt:1-990`).
- **How PoB calculates the trigger rate** (`CalcTriggers.lua`):
  1. Source = an attack in the **same socket group** (`slotMatch` `:33-39`, CoC config `:1156-1159`). If several attacks
     qualify, PoB takes the fastest by HitSpeed or Speed (`:69-87`). For Cyclone this is its attack rate.
  2. Trigger chance = source hit chance × source crit chance (`:737-786`).
  3. Cap = 1 / (0.15 / ICDR, rounded **up** to the 0.033 s server tick) (`:563-591`, `Modules/Data.lua:237-238`).
     ICDR is the **triggered spell's** CooldownRecovery (`:563`). Cooldown stats map to CooldownRecovery INC
     (`SkillStatMap.lua:533-538`).
  4. Rate = simulation of 1000 source attacks, with cooldowns aligned to server ticks and trigger chance as a geometric
     expected value (`:91-134`, called at `:814`).
- **Breakpoints:** wiki table and PoB agree: 0% → 6.06/s, ≥14% → 7.57/s, ≥52% → 10.10/s, ≥128% → 15.15/s.
  Wiki: "exceeding the attack rates even slightly can significantly reduce proc rate … multiples of the attack rate also work".

## 3. Cyclone (the trigger attack)

- `act_dex.lua:4681-4786`. Types: Attack, Area, Melee, Movement, Channel.
  Weapons: Claw, Dagger, unarmed, 1H Axe/Mace/Sword, Thrusting 1H Sword, Sceptre, Staff, 2H Axe/Mace/Sword
  (`:4687-4700`). **No bows or wands.** Attribute requirements: Str 40 / Dex 60 weighting (`Gems.lua`, Cyclone entry).
- Attack speed: `attackSpeedMultiplier = 200`, so the attack rate is weapon APS × 3 (`CalcOffence.lua:2299-2300`).
  Wiki infobox: "Attack Speed: 300% of base". The wiki says it deals damage once per spin.
  PoB uses the Cyclone attack rate directly as the CoC source rate (PoB run "Cyclone attack rate").
- Cost per attack: 2 Mana (L1), 3 (L2-23), 4 (L24+) (`:4745-4784`). Movement speed: 30% less (L1) to 20% less (L20).
  Quality gives AoE per extra melee range only (`:4733-4738`). Already covered in [[Trigger attack stays at cheapest level]].
- **What changes the FR trigger rate:** Cyclone attack rate relative to the breakpoint; Cyclone crit and hit chance
  (both below 100% → chance-scaled); ICDR on FR; the number of spells in the CoC link (they take turns, wiki "trigger
  order"). Dual-wield halving does **not** apply to the CoC gem (`CalcTriggers.lua:449-454` is limited to
  source-weapon and item triggers). Hitting several enemies in one spin still gives one trigger (wiki 2.4.0: "one spell per frame").
- Cyclone of Tumult (`act_dex.lua:4787+`): 180% of base attack speed (`attackSpeedMultiplier = 80`) plus 25% more per
  stage, and stages are a config value. Its trigger rate depends on the hand-set stage count.

**PoB run, build "FR CoC Occu No Mirror Helm" (FR part 1 as saved):**

| Setup (in memory) | Cyclone APS | FR triggers/s (cap) | FR DPS | FR ES/s | Cyclone ES/s |
|---|---|---|---|---|---|
| As saved (Aw. CoC eff. L10, Aw. VM, Greater Volley) | 10.03 | 10.03 (10.10) | 16.60M | 1555 | 60.2 |
| Aw. gems → CoC 20/20 + VM 20/20 (obtainable in 3.29) | 10.03 | **5.07** (7.58) | 7.71M | 755 | 60.2 |
| … and 44% reduced attack speed (custom mod) | 7.52 | 7.52 (7.58) | 11.45M | 1121 | — |
| … and +37% ICDR instead (custom mod) | 10.03 | 10.03 (10.10) | 15.27M | 1495 | 60.2 |
| … Greater Volley → Cooldown Recovery 3/20 | 10.03 | 10.03 (10.10) | 18.63M | 1495 | 60.2 |
| … Greater Volley removed (3 supports) | 10.03 | 5.07 | 9.41M | 502 | 60.2 |
| … GV removed and 44% reduced attack speed | 7.52 | 7.52 | 13.97M | 745 | 45.1 |

Why: the build's ICDR is 37% (Awakened CoC L10) + 15% (jewels 3+3, boots 9) = 52%, exactly the 10.10/s breakpoint.
Without the Awakened gem it drops to 15%, so the cap becomes 7.58/s. Cyclone at 10.03 APS overshoots that cap, and
PoB's simulation lands on every 2nd attack: "/ 1.98 (Estimated impact of skill rotation…)".
**A slower Cyclone or more ICDR raises FR DPS**, and the FR cost per second rises with it.

## 4. Supports for FR under CoC

PoB compatibility (`calcLib.canGrantedEffectSupportActiveSkill`, `CalcTools.lua:86-116`) was checked against FR with
CoC's added types. 99 non-legacy supports pass. A pass only means the support links; it does not mean it helps.

- **Blocked because CoC adds Triggered:** Spell Echo, Greater Spell Echo, Unleash, Greater Unleash, Intensify,
  Pinpoint, Trinity, Unholy Trinity, Gluttony.
- **Unlocked by CoC:** Cooldown Recovery (requires Cooldown, `sup_int.lua:1280-1292`). FR has no cooldown until CoC
  adds the type. Exceptional gem, 30-40% ICDR (+0.25% per quality), 150% cost (wiki 3.28.0 "Introduced"). It replaces
  Awakened CoC's ICDR (PoB run above: 9.41M → 18.63M). The wiki lists its source as Arkhon's Vault (3.28 content);
  **UNVERIFIED** whether that source still exists in 3.29.
- **Helps (PoB-scored):** Void Manipulation (34% more chaos at L20; Awakened +1 chaos gem level is legacy);
  Increased Critical Damage; Increased Critical Strikes (matters only if FR crit < 100%; the "Occu CoC FR YT" build has
  FR crit 72.45%); Power Charge On Critical (4% more damage per power charge, `sup_int.lua:5603-5611`; PoB run:
  9.41M → 12.07M, but charges come from a hand-set config); Added Chaos Damage (×1.1).
  Withering Touch is attack-only, so it supports Cyclone, not FR. Its Withered stacks raise chaos damage taken by
  6% per stack, up to 15 (`CalcPerform.lua:848`), but the stack count is a **hand-set config**
  (`ConfigOptions.lua:1839`). Its cost multiplier hits Cyclone only.
- **Projectile supports:** Greater Volley (+4, 21% less projectile damage, ×1.5 cost) and GMP (+4, 26% less). They only
  pay off in PoB if FR is set to part 2.
  PoB run: GV in part 1 = 7.71M vs 9.41M without it (a loss); part 2 = 46.27M (6 hits assumed).
  The wiki warns more than +4 projectiles miss small targets, so the true value lies between those numbers.
  Wiki 3.28.0: the Greater version no longer stacks with its non-Greater version.
  Chain, Fork, Pierce and Returning link but do nothing (wiki).
  Faster Projectiles shortens time to impact (wiki); PoB does not score this QoL gain.
- **Do nothing in PoB:** Faster Casting (trigger rate replaces cast time). Elemental Focus and Inspiration gave the same
  FR DPS in the PoB run (9.34M each). Neither adds to pure chaos damage, and FR crit was already 100%; Inspiration's
  crit per charge could matter on a build with less FR crit.
- **Break or hurt the setup:**
  - Elemental Focus sets `CannotShock/CannotChill/CannotFreeze` (`SkillStatMap.lua:1061-1064`), which blocks the
    helmet's chaos shock/freeze.
  - Controlled Destruction: 80% less crit chance (`sup_int.lua:1172-1180`); PoB run 3.98M (about −57%). It also
    links to Cyclone.
  - Spell Totem, Trap and Mine supports add SummonsTotem/Trapped/RemoteMined, which CoC excludes (`sup_dex.lua:591`),
    so the trigger stops.
  - Other trigger supports (CwDT, Cast on Death and so on) pass PoB's check. In-game they conflict:
    **UNVERIFIED** for two trigger supports; the wiki only states this for spells with built-in triggers.
  - Lifetap makes costs Life, which is unusable on CI unless converted.
  - Arcane Surge and Inspiration charges need *mana* spent. With Whispers (ES costs) they likely never build:
    **UNVERIFIED**; PoB uses config values.
  - Energy Leech (wiki 3.27.0) now gives "more Damage while on Full Energy Shield"; ES costs every cast make that
    condition doubtful: **UNVERIFIED**.
- **Costs on both skills:** a support linked with both skills multiplies *both* costs (CoC, VM, ICD, PCoC).
  GV and Cooldown Recovery multiply FR only. Withering Touch and Faster Attacks multiply Cyclone only.

## 5. Mana or other resource: summing Cyclone and FR

PoB costs (`CalcOffence.lua:1713-1738`, `5943-5948`):

`cost/use = floor(base × Π support multipliers) → inc/more/efficiency`

`per second: Cyclone = cost × attack rate; FR = cost × **trigger rate**`

PoB reports each skill on its own; it never sums them, which is what [[Total skill cost must be sustainable]] adds.

- PoB run, build "FR CoC Occu No Mirror Helm":
  - Cyclone: `3 × 2.028 = 6`/attack × 10.03 = 60.2/s.
  - FR of Soul Sacrifice: `51 × 3.0419 = 155`/cast × 10.03 = 1555/s.
  - **Sum 1615/s**, against ES regen 2692/s. The costs are paid in **ES** because of Whispers of Infinity
    (`CostESInsteadOfManaOrLife`, `CalcOffence.lua:1766-1784`).
- Regular FR (mana) in the same links at L23: 69 per cast (PoB run).
  Derived: 69 × 5.07 = 350/s; × 7.57 = 522/s; × 10.10 = 697/s (cost per cast × trigger rate). Add Cyclone on top.
- Trade-off: each step up in trigger rate raises the FR cost per second by the same factor. Inspiration's "less mana cost"
  is `ManaCost MORE` (`sup_str.lua:4621-4623`), and PoB does not apply it to Whispers ES costs
  (PoB run: 99 → 119 ES per cast). Real game behaviour: **UNVERIFIED**.
- The rule should sum **per resource** (Mana, Life, ES) because of the Soul Sacrifice life cost and Whispers.
  For non-CI FR, the self-hit per second (`FRDamageTaken` × trigger rate) is a separate drain that PoB ignores.

## 6. The user's 3.26 builds (read-only; supports per PoB effect list)

| Build | Main link (gem level/quality as saved) | Notes from the PoB run |
|---|---|---|
| FR CoC Occu No Mirror Helm (Occultist, CI, Zealot's Oath) | Cyclone 20/23, FR of Soul Sacrifice 21/20 (part 1), Aw. CoC 6/20, Inc. Crit Damage 20/20, Aw. Void Manip 5/20, Greater Volley 20/20 | Effective levels: FR 24, Aw. CoC 10, ICD 24/30. GV supports FR only. ICDR exactly 52%. Cyclone 10.03 APS |
| Occu CoC FR YT (Occultist, CI, Glancing Blows), 5 skill sets, **active = set 1 "30 Div Budget"** | Set 1: Cyclone 21/0, Aw. CoC 5/20, Aw. VM 5/20, PCoC 20/20, FR SS 20/20 (part 1), GV 20/20. Set 5 "My Current Setup": Cyclone 20/20, Aw. CoC 6/20, **Aw. GMP 5/20**, Aw. VM 6/20, FR SS 21/20, PCoC 20/20 | Cyclone tuned to 7.566 APS, just under 7.57 (ICDR 37% = Aw. CoC 31 + boots 6). FR crit 72.45%. The sidebar (part 1) shows 2.07M; the calcs tab shows 12.4M (×6), so the **hand-set skill parts differ** |
| Trickster CoC (CI, Ghost Reaver) | FR SS 21/20 (part 2), Inc. Crit Damage 21/20, Cyclone 21/20, Aw. CoC 5/20, Aw. VM 5/20, PCoC 20/23 | ICDR 61% (Aw. CoC 31 + tree 30). 10.03/s. With normal gems the trigger rate falls to 5.02/s: part 1 goes 6.70M → 3.06M, part 2 (sidebar) goes 13.40M → 6.12M. Sidebar and calcs-tab parts differ here too |

All three: **CI + Whispers of Infinity + FR of Soul Sacrifice**, with Cyclone tuned just under a CoC breakpoint.
Other groups: Assassin's Mark + Mark On Hit, Automation + Withering Step, and auras.

**3.26 → 3.29 changes that matter here:**
- Awakened supports cannot be obtained (3.28.0), so every build loses its ICDR breakpoint and Awakened damage.
- Cooldown Recovery Support added (3.28.0).
- Greater and non-Greater supports no longer stack (3.28.0).
- FR 14% Life (3.29.0). This does not matter on CI.
- Cyclone +20% more damage (3.27.0). Irrelevant: the attack only triggers.
- Whispers of Infinity (wiki 3.27.0): +50-100 ES (was 200-400); now drops from Uber Incarnation of Dread.
  Undocumented changes to percentage and over-time costs. Item side: covered in the separate item note.

## Open questions

- Is the new character CI? With regular FR on Life, the self-hit is 40% Life + 25% ES per cast at 5-10 casts/s, and
  PoB shows only the per-cast value.
- Which FR skill part should the app trust? Part 1 undercounts (the wiki says 2 projectiles hit a single target).
  Part 2 overcounts beyond +4 projectiles. A model note may be needed, similar to [[Winter Orb projectile overlap]].
- Sources disagree: the wiki says "slightly above the breakpoint hurts a lot"; PoB's simulation at 7.581 APS against
  the 7.576 cap still gives 7.566/s (tick rounding, `CalcTriggers.lua:112`). Not resolved.
- Cooldown Recovery Support drop source in 3.29, Inspiration/Arcane Surge with ES costs, Energy Leech uptime, and
  stacking two trigger supports: all **UNVERIFIED**.
