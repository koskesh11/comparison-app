---
type: interaction
status: draft
pob_refs: [HitSpeed, HitTime, Duration, DurationSecondary, DurationTertiary, BrandTicks, AttachedBrandCount, ActiveBrandLimit, BrandsAttachedLimit, BrandActivationFrequency, TotalDPS, TotalDotDPS, Speed, ActiveBrands, BrandsAttachedToEnemy, targetBrandedEnemy, BrandsInLastQuarter, BrandsInLastHalf]
source: "poewiki Brand rev 1563719, Brand Recall 1682020, Runebinder 1490234, Armageddon Brand 1682017, Wintertide Brand 1682141, Storm Brand 1682010, Penance Brand 1682138, Swiftbrand Support 1682146, Foulgrasp Support 1682297, Sign of Purpose 1619619 (fetched 2026-10-26); PoB 2.67.2 Modules/CalcOffence.lua, CalcPerform.lua, CalcSetup.lua, ConfigOptions.lua, ModParser.lua, Data/SkillStatMap.lua, Data/Skills/act_int.lua, sup_int.lua, TreeData/3_29/tree.lua, Data/Uniques; evidence mechanics-researcher-brands.md (task 027 batch 2)"
last_confirmed_patch: "3.29.x"
---

A brand is a persistent spell placed at the cursor: base 3 active brands, 1 attached per enemy (Runebinder allows 1 more). An attached brand activates at its own frequency; attached and detached durations are separate clocks that do not refresh, and the brand ends when either runs out. When the host dies the brand returns to its cast spot and keeps its remaining clocks. PoB turns a brand into a rate (activation rate x attached count) and assumes it is attached and activating all the time; it has no recast, host-death or reattach term, so the sustained value is PoB x u and u comes from the scenario. Brands are skill effects, not objects: leech and reflect apply to the caster (wiki Brand rev 1563719), the opposite of totems, traps and mines.

Pipeline: [[Damage calculation#Hit rate]] - activation frequency IS the hit rate (HitSpeed replaces cast speed in TotalDPS, CalcOffence.lua:3801), and the attached count multiplies after it. [[Damage calculation#More and less]] - activation frequency, the Wintertide stage curve and the End debuff are multipliers; the "more Hit damage against Branded Enemy" is a Hit-only more multiplier, so a DoT brand (Wintertide) gets nothing from it. For enemy-side "increased damage taken per brand" see [[Damage calculation#Damage taken]]. Wintertide is a DoT: see [[Damage over time multiplier]].

```interaction
id: brands
mechanic: "A brand is a persistent spell placed at the cursor (base 3 active, 1 attached per enemy); while attached it activates at the brand's activation frequency (base period / (1 + increased cast speed and activation freq) / more activation freq; action speed does not matter); attached and detached durations are separate non-refreshing clocks and the brand dies when either ends; a dead host returns the brand to its cast spot; Runebinder allows 1 more attached"
family: uptime
target: enemy
related: [totems, traps-and-mines, damage-over-time-multiplier, chill, ignite, curse-limit, chance-on-hit-uptime]
pipeline_step: ["Damage calculation#Hit rate", "Damage calculation#More and less", "Damage calculation#Damage over time"]
pipeline_why: "activation frequency is the hit rate (TotalDPS = AverageDamage x HitSpeed x attached count, CalcOffence.lua:3801,2490-2494); Wintertide is a DoT whose stages and End debuff enter as Damage MORE (act_int.lua:21129); the branded-enemy bonus is a Hit-only more multiplier (SkillStatMap.lua:769)"
pob:
  measured: partial
  how: "Activation rate: hitTimeOverride = repeatFrequency / (1 + (Speed INC + BrandActivationFrequency INC)/100) / More(BrandActivationFrequency) (Data/Skills/act_int.lua:716,21109); HitSpeed = 1/hitTimeOverride and replaces Speed in TotalDPS (CalcOffence.lua:2471-2473,3801); attached count = config or min(BrandsAttachedLimit, ActiveBrandLimit) (CalcPerform.lua:1357-1368), multiplies DPS (CalcOffence.lua:2490-2494), except Wintertide part 1 which folds it into Damage MORE (act_int.lua:21125-21129). Measured 2026-10-26 (PoB output fields; low-level skill sets, so deltas count, not absolutes): Armageddon Brand L5 in RF Pohx skill set 4: HitSpeed 0.8, Duration 5.016, DurationSecondary 6.006, BrandTicks 4, AttachedBrandCount 1, TotalDPS 208.936 = 261.17 x 0.8 x 1, ignite TotalDotDPS 169.854; a Runebinder line (+1 attached) gives count 2, TotalDPS 417.872 (x2.000) while ignite only 169.854 -> 179.369 (+5.6%, matches the wiki ignite note); targetBrandedEnemy true -> false: AverageDamage 261.17 -> 229.19, TotalDPS -12.2% (on by default); '30% increased Brand Activation Frequency' +25%; 'Brand Skills have 50% increased Duration' changes ticks 4 -> 6 but not Armageddon DPS; '10% increased Spell Damage per Brand' counts 0 brands until ActiveBrands is set (208.936 unset, 250.592 at 2, 271.584 at 3). Wintertide Brand L6 count 3 in Rue Worb skill set 1: HitSpeed 8.28, Duration 2.013, DurationTertiary 2.013, BrandTicks 16, BrandsAttachedLimit 2 without Runebinder, part 1 25500.3, BrandsAttachedToEnemy 1 -> 18515.8 (-27.4%), Runebinder line -> 3 attached 32512.2 (+27.5%), Sign of Purpose line + BrandsInLastQuarter 34128.2 (+33.8%), '50% increased Duration' 31827.4 (+24.8%); targetBrandedEnemy and ActiveBrands have no effect on Wintertide. NOT modelled: attached/detached expiry and recasting (no uptime), host death and reattach, Brand Recall activations and the no-bonus-on-recall rule, brand replacement past the limit, Spell Echo double placement (unverified), Sign of Purpose as the wiki x1.25 (PoB ticked = x2.0 of the rate over the whole duration), Brand Mastery reattach and mana refund (unparsed). Brand Recall: PoB models only its attachment-range buff, cooldown 4 and the 20% cost constant stat (act_int.lua:2595-2626)"
  config:
    - {var: ActiveBrands, default: 0, ref: "Modules/ConfigOptions.lua:331 (every 'per Brand' modifier counts 0 brands until set)", class: b}
    - {var: BrandsAttachedToEnemy, default: "limit", ref: "Modules/ConfigOptions.lua:334 (can lower the attached count, never raise it above the limit)", class: b}
    - {var: targetBrandedEnemy, default: true, ref: "Modules/ConfigOptions.lua:337", class: b}
    - {var: BrandsInLastQuarter, default: false, ref: "Modules/ConfigOptions.lua:340 (sets BrandLastQuarter and BrandLastHalf)", class: b}
    - {var: BrandsInLastHalf, default: false, ref: "Modules/ConfigOptions.lua:344", class: b}
    - {var: conditionUsedBrandRecently, default: false, ref: "Modules/ConfigOptions.lua:1310", class: b}
  unparsed:
    - "Brand Mastery: Recover 10% of Mana when a Brand expires while Attached"
    - "Brand Mastery: Brands Attach to a new Enemy each time they Activate, no more than once every 0.3 seconds"
    - "Seeker Runes: Unattached Brands gain 20% increased Brand Attachment Range per second, up to a maximum of 100%"
    - "Remarkable: Skills which create Brands have 35% chance to create an additional Brand"
    - "Chip Away: Brand Recall grants 20% increased Brand Attachment range to recalled Brands (parsed wrong: BASE 20, remainder left)"
model:
  proposed_kind: brand_uptime
  inputs: {from_pob: [TotalDPS, TotalDotDPS, HitSpeed, Duration, DurationSecondary, BrandTicks, AttachedBrandCount, ActiveBrandLimit, Speed], from_scenario: ["fraction of the attached window a living host stands within range (Mapping, class b)", "recast policy / attach delay (class b)"]}
  params: {base_active_limit: 3, base_attached_limit: 1, attach_range_units: 30, sign_of_purpose_factor_wiki: 1.25}
  formula: "sustained DPS = PoB DPS x u; Pinnacle Boss u = A / (A + gap) with A = Duration and gap = player time between brand expiry and the next attach (0 with a waiting brand in the 3-brand budget, else one cast time 1/Speed); Mapping u = min(1, host_lifetime / A) x R with R = share of time a host is inside 3 m of the brand spot; Sign of Purpose = x1.25 on ticks, floor"
  calibration: "no norm found for attach delay or host lifetime"
providers:
  - {kind: gem, name: "Wintertide Brand", slot: any, role: applies, target: enemy, text: "cold DoT stacking to 20 stages, chills, End debuff 2 s; attached 2 s, detached 6 s, activates every 0.25 s; +1 attached brand on its own", source: "Data/Skills/act_int.lua:21098-21179", pob: partial}
  - {kind: gem, name: "Armageddon Brand", slot: any, role: applies, target: enemy, text: "fire meteor every 1.5 s while attached; attached 5 s, detached 6 s; more Hit damage vs Branded Enemy", source: "Data/Skills/act_int.lua:706-739", pob: partial}
  - {kind: gem, name: "Brand Recall", slot: any, role: enables, target: self, text: "recalls and activates all brands (20% of their cost), cooldown 4 s; no duration refresh since 3.11.0", source: "Data/Skills/act_int.lua:2595-2626; wiki Brand Recall rev 1682020", pob: partial}
  - {kind: support, name: "Swiftbrand", slot: any, role: scales, target: enemy, text: "more activation frequency (L20 44%), 65% less primary and secondary duration", source: "Data/Skills/sup_int.lua:6506-6532; wiki rev 1682146", pob: full}
  - {kind: support, name: "Foulgrasp", slot: any, role: scales, target: self, text: "+2 brand limit, recalled brands trigger Enervating Grasp", source: "Data/Skills/sup_int.lua:2611-2630", pob: partial}
  - {kind: keystone, name: "Runebinder", slot: tree, role: scales, target: enemy, text: "-1 to maximum number of Summoned Totems; You can have an additional Brand Attached to an Enemy", source: "TreeData/3_29/tree.lua:28561-28565; wiki Runebinder rev 1490234", pob: full}
  - {kind: ascendancy, name: "Sign of Purpose (Hierophant)", slot: tree, role: scales, target: enemy, text: "Brands have 100% more Activation Frequency if 75% of Attached Duration expired; Brand Recall 100% increased cooldown recovery", source: "TreeData/3_29/tree.lua:15786-15792; wiki rev 1619619", pob: config}
  - {kind: notable, name: "Brand Equity", slot: tree, role: scales, target: self, text: "You can Cast 2 additional Brands; Brand Skills 20% increased Duration; Brand Recall 20% cooldown recovery", source: "TreeData/3_29/tree.lua:43606-43617", pob: full}
  - {kind: mastery, name: "Brand Mastery", slot: tree, role: scales, target: enemy, variant: "options: mana on expiry / reattach every 0.3 s / +2 brands / +40% range / AoE if 50% expired / Recall CDR", text: "mastery options; reattach and mana refund unparsed", source: "TreeData/3_29/tree.lua:26726-26766,40014-40054,43666-43706", pob: partial}
  - {kind: notable, name: "Runesmith", slot: tree, role: scales, target: enemy, text: "12% increased Cast Speed with Brand Skills; Enemies take 5% increased Damage for each of your Brands Attached to them", source: "TreeData/3_29/tree.lua:26880-26890", pob: full}
  - {kind: unique, name: "Replica Tukohama's Fortress", slot: Shield, role: scales, target: self, variant: "Pre 3.29.0 20% / Current 30% crit per Brand", text: "You can Cast an additional Brand; 30% increased Critical Strike Chance per Brand; 40% increased Brand Damage; Blood Magic", source: "Data/Uniques/shield.lua:214-229", pob: config}
  - {kind: unique, name: "Witchhunter's Judgment", slot: Staff, role: scales, target: self, text: "Grants Level 20 Brandsurge Skill; Brand Skills have (50-100)% increased Duration", source: "Data/Uniques/staff.lua:765-776; wiki Brandsurge rev 1649279", pob: partial}
makes_redundant:
  - {provider: "Runebinder (keystone)", when: "Wintertide Brand already has 2 attached from its own gem stat", why: "Runebinder adds the third; for Armageddon/Storm it is the only way to a second (+100% hits)", source: "Data/Skills/act_int.lua:21177; measured Wintertide part 1 25500.3 -> 32512.2 with a Runebinder line (RF/Worb probe 2026-10-26)"}
conflicts:
  - {with: "Runebinder (keystone)", effect: "-1 to maximum Summoned Totems; with Ancestral Bond/totem builds the limit goes to 0", source: "TreeData/3_29/tree.lua:28565; wiki Runebinder rev 1490234"}
  - {with: "Swiftbrand Support", effect: "65% less attached and detached duration: fewer total activations per brand life offset the faster rate; Wintertide gets fewer stages (floor(duration/period) caps)", source: "Data/Skills/sup_int.lua:6529-6532"}
  - {with: "Elemental Focus Support", effect: "Wintertide debuffs no longer chill (undocumented change 3.15.0)", source: "wiki Wintertide Brand rev 1682141"}
  - {with: "Brand Recall", effect: "recalled activations get no Hit bonus against Branded Enemy and the recalled brand has to attach again", source: "wiki Brand Recall rev 1682020"}
conditions:
  - {text: "an enemy must be within 30 units (3 m) of the brand; attachment range is not affected by area of effect", source: "wiki Brand rev 1563719; Modules/Data.lua:272"}
  - {text: "only 1 brand attached per enemy by default (Wintertide 2, PoB data); brand limit 3 total, unattached replaced first", source: "wiki Brand rev 1563719; Modules/CalcSetup.lua:631"}
  - {text: "activation frequency scales with increased cast speed and activation frequency, with more activation frequency; not with action speed or more cast speed", source: "wiki Brand rev 1563719; act_int.lua:716"}
  - {text: "a dead host returns the brand to its cast spot (3.11.0) and it keeps its remaining attached and detached time; the attached time spent on a host that dies is gone", source: "wiki Brand rev 1563719 version history 3.11.0"}
  - {text: "brands are skill effects, not objects: leech and reflected damage apply to the caster", source: "wiki Brand rev 1563719"}
uptime:
  Mapping:       {value: model, config: {BrandsAttachedToEnemy: "limit unless fewer hosts", ActiveBrands: "set to the brands the build keeps placed"}, reasoning: "hosts die and the brand returns to its cast spot with its remaining clocks; activations per host = floor(host lifetime x F); no PoB number; Wintertide benefits from the End debuff on each removal", source: "wiki Brand rev 1563719; Data/Skills/act_int.lua:21098-21131"}
  Pinnacle Boss: {value: model, config: {BrandsAttachedToEnemy: "limit", targetBrandedEnemy: true}, reasoning: "one host stays attached for all of A; u = A / (A + gap); Armageddon example 0.937 and Wintertide 0.856 assume one cast time of gap and instant attach (attach delay undocumented)", source: "PoB fields Duration 5.016 / 2.013, Speed 3 / 2.957 (probe 2026-10-26); wiki Brand rev 1563719"}
seeds: [Worb]
sources:
  - {ref: "https://www.poewiki.net/wiki/Brand (rev 1563719); Brand_Recall 1682020; Runebinder 1490234; Armageddon_Brand 1682017; Wintertide_Brand 1682141; Storm_Brand 1682010; Penance_Brand 1682138; Swiftbrand_Support 1682146; Foulgrasp_Support 1682297; Sign_of_Purpose 1619619; Brandsurge 1649279 (all fetched 2026-10-26)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcOffence.lua:1458-1465,1910-1912,2471-2494,3801,5911; Modules/CalcPerform.lua:1357-1368; Modules/CalcSetup.lua:631; Modules/ConfigOptions.lua:330-345,1310; Modules/ModParser.lua:617-619,1343-1344,1910,2344,2498,2897,2906,4410; Modules/Data.lua:272; Data/SkillStatMap.lua:769,2150-2174; Data/Skills/act_int.lua:706,2595,21098; Data/Skills/sup_int.lua:2611,6506; TreeData/3_29/tree.lua (lines in providers); Data/Uniques/{shield,staff}.lua", kind: pob, patch: "3.29"}
  - {ref: "PoB changelog.txt:3958 (Wintertide +1 attached fix)", kind: pob, patch: "3.29"}
  - {ref: "https://poedb.tw/us/Wintertide_Brand (gem text 'Can have 1 additional Brands Attached to an Enemy'; discovery only)", kind: discovery, patch: "3.29"}
not_verified:
  - "item-analyst not consulted: unique and support lists come from PoB Data/Uniques and a wiki items query only; The Hungry Loop (Swiftbrand via consumed gem) is variable and not modelled"
  - "Wintertide default attached limit 2: PoB data (act_int.lua:21177) + PoB changelog.txt:3958 + gem text per poedb; the wiki Wintertide page is silent; not tested in game (conflicts with the wiki default of 1)"
  - "attach delay after casting on a boss, first-activation timing, whether Spell Echo works with PoB's brand model (Repeats not checked), whether 'Brand Recall has N% increased Cooldown Recovery Rate' (generic CooldownRecovery INC) is scoped to Brand Recall only"
  - "Armageddon attached duration 5 s is PoB-only (act_int.lua:739); the wiki page does not state it"
  - "Storm Brand and Penance Brand (and their transfigured gems) were read from the wiki but not measured in PoB"
  - "providers not listed (cap): Chip Away cluster notable (tree.lua:88095-88100, parsed wrong), Replica Allelopathy (grants Wintertide Brand, gloves.lua:346-361), Seeker Runes 88105, Remarkable 88118, Brand Loyalty 88128, Holy Conquest 88137, Grand Design 88150, Explosive Runes 40109"
  - "measured builds are low-level skill sets that are not the active set (Armageddon L5 in RF Pohx set 4 at char level 30; Wintertide L6 in Rue Worb set 1, active set 9 has Winter Orb): deltas valid, absolute DPS not representative"
  - "wiki vs PoB differences left as they are: Sign of Purpose ticked = x2.0 vs wiki x1.25 floor (Armageddon BrandTicks 8 vs wiki 5; Wintertide 33 vs 20); Wintertide stages: wiki 'keeps its stages while detached', PoB averages from 0 over one attached duration (act_int.lua:21119), equivalence for detach/reattach cycles unverified"
open_questions:
  - "Which skill set should the generator measure for the Worb seed: the Wintertide set 'Occultist Week 1/12 to 33' is not the active set (set 9, Winter Orb)?"
  - "Should the generator use the wiki x1.25 for Sign of Purpose instead of PoB's x2 tick?"
```
