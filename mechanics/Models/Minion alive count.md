---
type: model
status: draft
label: "draft - not user-verified"
verified_by:
pob_refs: [FullDPS, SkillDPS, Minion.TotalDPS, Speed, HitSpeed, SummonedMinionsPerCast, summonSpeed, Duration, DurationSecondary, ActiveMinionLimit, ActiveRagingSpiritLimit, ActiveSpectreLimit, ActiveZombieLimit, ActiveSentinelOfAbsolutionLimit, multiplierSummonedMinion, enemyIsBoss]
superseded_by_pob:
source: "PoB 2.67.2 (3.29) Modules/Calcs.lua, CalcOffence.lua, CalcPerform.lua, ConfigOptions.lua, Data/SkillStatMap.lua, Data/Minions.lua, Data/Skills/act_int.lua + act_str.lua; poewiki Minion rev 1703018, Summon Raging Spirit rev 1681790, Raise Spectre rev 1702628, Animate Guardian rev 1681757, Absolution rev 1682183 (fetched 2026-10-26); headless check on 3.27/SRS CI Guardian Giga Build.xml (in memory, not saved, 2026-10-26)"
last_confirmed_patch: "3.29.x"
---

```model
proposed_kind: minion_alive_count   # draft - not user-verified; not in models.py KINDS; no "kind:" so the app skips this note
label: "draft - not user-verified"
applies_when: "a minion skill group is in FullDPS. PoB counts it as Minion.TotalDPS (ONE minion, CalcOffence.lua:3801)
  x the HAND-SET gem count (Calcs.lua:116-137, 179-180). The limit, summon rate, duration and deaths never reduce DPS."
applies_to: { scope: minion_skill_groups_in_FullDPS }
replaces: "the gem count of that group. Never multiply on top of the hand-set count."
inputs:
  from_pob_per_skill: [Speed, HitSpeed, SummonedMinionsPerCast, Duration, DurationSecondary, ActiveMinionLimit, "Active<Type>Limit", Minion.TotalDPS, "SkillDPS[].count", "gem quality"]
  from_pob_skilldata: summonSpeed        # skillData, not an output key: SummonedMinionsPerCast x (HitSpeed or Speed) x dpsMultiplier (CalcOffence.lua:4097, its only use)
  from_pob_config: [enemyIsBoss, multiplierSummonedMinion]
  from_scenario: [f_cast, precast, death_rate_lambda, resummon_delay_tau, hit_fraction_h]
  from_model: damage_s                   # [[Fight length]] (Pinnacle only, used only when precast is false)
params:
  limit:                                 # PoB output, floor(base x more) (CalcOffence.lua:1057-1059)
    raging_spirit: ActiveRagingSpiritLimit        # Minions.lua:215; SkillStatMap.lua:1989; base 20 (wiki SRS 2.5.0)
    spectre: ActiveSpectreLimit                   # Data.lua:1158; SkillStatMap.lua:2007; the sum of ALL Raise Spectre groups must fit it
    zombie: ActiveZombieLimit                     # Minions.lua:24; SkillStatMap.lua:1977
    sentinel_of_absolution: ActiveSentinelOfAbsolutionLimit   # Minions.lua:879; SkillStatMap.lua:2022; base 3 (act_str.lua:42)
    animated_guardian: 1                          # no limit key (Minions.lua:605-630); "Skills without a limit contribute one minion" (CalcPerform.lua:1436)
  duration_field: { srs: Duration, absolution: DurationSecondary }   # SRS base 5 s (wiki SRS); Absolution sentinels 15 s (act_str.lua:43, wiki 3.28.0); CalcOffence.lua:1505-1510, 1529-1533
  srs_quality_extra_chance: "quality x 1.5%"      # act_int.lua:19367; NOT in SkillStatMap (grep), so PoB ignores it; wiki SRS 3.23.0 "0-30%" at Q0-20
  absolution_per_cast_vs_boss: "0.25 x HitChance" # act_str.lua:44 (25% on hitting a rare/unique; not in SkillStatMap: PoB ignores it)
  absolution_per_kill_in_maps: 1                  # act_str.lua:7: a non-unique enemy dying with the debuff summons one, or refreshes one at the max
  resummon_delay_tau:
    animated_guardian: infinite_in_area           # act_str.lua:468; wiki Animate Guardian 3.26.0 (hideout excepted)
    spectre: "orb until the next area; a new Raise Spectre can replace an orb, but it needs a corpse: no norm found"   # wiki Raise Spectre 3.27.0
    zombie: "needs a corpse: no norm found; wiki Raise Zombie not fetched (Cloudflare 2026-10-26)"
  death_rate_lambda: 0        # no norm found; 0 = PoB's own assumption
  hit_fraction_h: 1           # no norm found (searched 2026-10-26); 1 = PoB's own assumption
  precast: { Pinnacle: true, Mapping: false }    # UNVERIFIED assumption; see Risks
solve:
  rate: "summonSpeed x (1 + srs_quality_extra_chance) x f_cast   # never multiply by SummonedMinionsPerCast again"
  life_eff: "lambda = 0 -> D; else (1 - exp(-lambda x D)) / lambda   # D = duration_field"
  # (a) duration minions (SRS, Absolution sentinels)
  steady: "min(limit, rate x life_eff)"
  t_fill: "steady / rate"
  ramp: "precast -> 1; damage_s >= t_fill -> 1 - t_fill / (2 x damage_s); else rate x damage_s / (2 x steady)"
  cadence: "to stay at the limit: one cast every life_eff / limit s, i.e. f_cast_min = limit / (summonSpeed x (1 + extra) x life_eff)"
  alive_a: "steady x ramp"
  # (b) permanent minions (Raise Spectre, Animate Guardian, Raise Zombie)
  u_b: "lambda = 0 -> 1; tau finite -> 1 / (1 + lambda x tau); tau infinite -> (1 - exp(-lambda x T)) / (lambda x T)   # T = fight or area time"
  alive_b: "min(hand-set count, limit) x u_b   # spectres: each group, then sum over groups capped at ActiveSpectreLimit"
  # (c) single boss
  attacking: "alive x hit_fraction_h"
  count: "max(1, floor(attacking))     # [[Models round down]]"
  feed_pob: { "gem count of the group": count, multiplierSummonedMinion: "sum of floor(alive) over all minion types, only when a 'per summoned minion' mod exists (CalcPerform.lua:1436-1498; ConfigOptions.lua:1139-1141); not measured" }
results_srs_sample:   # 3.27/SRS CI Guardian Giga Build.xml, Pinnacle, gem L21 Q23, hand-set count 6
  inputs: { Speed: 2.7, SummonedMinionsPerCast: 1, summonSpeed: 2.7, Duration: 9.207, ActiveRagingSpiritLimit: 6, Minion.TotalDPS: 10577103 }
  model: { uncapped: 24.86, steady: 6, t_fill_s: 2.22, f_cast_min: 0.241, cadence_s: 1.53, count: 6 }
  pob: { count_6: 70514022, count_5: 58761685 (-16.67%), count_4: 47009348 (-33.33%) }
  sensitivity: { "h 0.946 (0.5 s idle per spirit)": 5, "precast false, damage_s 60": 5, "f_cast 0.20": 4, "quality extra counted": 6 }
scenarios:
  Pinnacle Boss: "single target, no adds. (a) with precast; Sirus immune windows (15-30 s, [[Fight length]]) outlast D, so spirits lapse unless the player keeps f_cast >= f_cast_min during them. (b) a dead Guardian stays dead for the fight; a dead Spectre stays an orb until the next area. (c) h applies. Absolution: sentinels only from the 25% chance on hitting the boss."
  Mapping: "packs. (a) per pack, without precast; Raging Spirits pick targets not already targeted (wiki Minion), so h = 1 toward the pack; damage per enemy is not modelled. Absolution: kills keep sentinels at the limit. (b) Spectres and Guardian come back at the next area."
```

**Gap:** PoB counts minion damage as one minion's TotalDPS x the hand-set gem count (`Modules/Calcs.lua:116-137, 179-180`). It works out the limit (`CalcOffence.lua:1057-1059`) and the summon rate (`CalcOffence.lua:4097`, used nowhere else), but the count never comes from them. It has no model of duration, deaths, resummons or targeting.

**Model:** for duration minions, alive = min(limit, summon rate x lifetime), with a ramp-up from 0 when you cannot precast. For permanent minions, alive = count x the share of time they are alive, given deaths and resummon delay. On a single boss, scale by the share that is attacking, round down ([[Models round down]]), and feed the result into PoB as the gem count. That replaces the hand-set count.

**SRS sample (headless, not saved):** 2.7 summons/s x 9.207 s = 24.86, against a limit of 6. So 6 are alive, which matches the hand-set 6, and FullDPS stays at 70,514,022. Holding 6 alive needs 24% of the player's time spent casting, one cast every 1.53 s. Any loss rounds down to 5, which costs 16.67% of FullDPS.

**Risks:**
- Rounding down is harsh here. A 1% loss (0.5 s idle, or one ramp-up per 60 s) already gives 5, not 6.
- Precast is assumed for Pinnacle fights. If it is false, the Sirus sample has damage_s = floor(70,884,457 / 70,514,022) = 1 s. That is less than t_fill (2.22 s), so the count drops to 1, and the [[Fight length]] loop then swings back and forth.
- Do not count SummonedMinionsPerCast twice: summonSpeed already includes it.

**User to verify (UNVERIFIED):** whether you can precast before Pinnacle fights; the hit fraction and death rate for each family (no norm found); resummon delays for Spectres and Zombies; the SRS quality extra-spirit chance in game; Absolution's 25% boss summon chance.

Related: [[Minions]], [[Fight length]], [[Mapping]], [[Pinnacle Boss]].
