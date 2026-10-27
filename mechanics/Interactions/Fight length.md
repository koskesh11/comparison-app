---
type: interaction
status: draft
pob_refs: [FullDPS, enemyIsBoss, multiplierFrozenByYouSeconds, conditionEnemyFrozen]
source: "poewiki Sirus rev 1702453 + cargo AtlasExile5; poedb (secondary, absolute factor); PoB PR #4435 / #4436; PoB 2.67.2 CalcOffence.lua / ConfigOptions.lua; mechanics-modeler and mechanics-researcher evidence files (task 027, 2026-10-25)"
last_confirmed_patch: "3.29.x"
---

PoB has no enemy life and no time-to-kill, so the length of a boss fight (damage time plus immunity windows) cannot come from PoB. Some inputs grow with fight time, mainly Cold Mastery 26782 (5% increased damage per second the boss was ever Frozen, max 50%), so the fight length feeds [[Freeze]] (multiplierFrozenByYouSeconds) and the freeze result feeds back into FullDPS: a short fixed-point loop (HP / FullDPS). Boss HP comes from the vault (default Sirus); a boss without a row is a gap, see [[Boss life]]. Uber divides raw HP by the Uber-preset FullDPS, which already holds the 70% less damage taken. See also [[Channelling]], [[Flask uptime]].

Pipeline: none - no damage/defence step: fight length is a time input (boss HP / FullDPS) outside the per-hit order; it only decides how long time-scaled inputs (frozen seconds, channel time) are up

```interaction
id: fight-length
mechanic: "Time to kill a single-target boss = boss HP (life + ES) / PoB FullDPS, plus the boss's invulnerable windows; fight-length-dependent inputs (Cold Mastery 26782 frozen seconds) are fed back until the length settles"
family: uptime
pipeline_step: []
pipeline_why: "no damage/defence step: fight length is a time input (boss HP / FullDPS) outside the per-hit order; it only decides how long time-scaled inputs (frozen seconds, channel time) are up"
target: enemy
related: [freeze, channelling, flask-uptime]
pob:
  measured: none
  how: "PoB has no enemy life or time-to-kill: grep of Modules/ for monsterLifeTable finds only minion life (CalcActiveSkill.lua:725-727), corpse life (CalcOffence.lua:1474,1916) and the ailment threshold (CalcOffence.lua:5336); the Uber -70% is inside FullDPS (CalcOffence.lua:3492-3493) (mechanics-researcher-boss-hp.md, boss-hp)"
  config:
    - {var: enemyIsBoss, default: "Pinnacle (list index 3)", ref: "Modules/ConfigOptions.lua:2086", class: b}
    - {var: multiplierFrozenByYouSeconds, default: 0, ref: "Modules/ConfigOptions.lua:1927-1930 (PoB limit 50/5 = 10 s for Cold Mastery 26782)", class: c}
    - {var: conditionEnemyFrozen, default: false, ref: "Modules/ConfigOptions.lua:1924", class: b}
  unparsed: []
model:
  proposed_kind: fight_length
  applies_when: "scenario Pinnacle Boss or Uber Pinnacle Boss (single target, no adds); boss = the scenario's boss row, else the default"
  inputs:
    from_pob: [FullDPS]
    from_pob_config: [enemyIsBoss, multiplierFrozenByYouSeconds]
    from_scenario: [boss, version]
    from_vault: [boss_life, boss_es, immune_windows, immune_window_s, "freeze_uptime (Interactions/Freeze.md)", cold_mastery_26782_allocated]
  params:
    boss_default: {Pinnacle: "Sirus (default)", Uber: "Sirus (default)"}
    boss_hp:
      Sirus: {Pinnacle: {area_level: 84, life: 70494097, es: 390360}, Uber: {area_level: 85, life: 75105854, es: 414432}}
    boss_hp_table: "other bosses: table in tasks/reports/027-evidence/mechanics-researcher-boss-hp.md (boss-hp); not copied here"
    hp_source: "poewiki life multiplier (cargo, revid) x absolute factor from poedb (secondary source)"
    immune:
      Sirus: {windows: 3, low_s: 15, high_s: 30, at_life_pct: [75, 50, 25], default_s: "low end (45 s total), range shown (90 s)", source: "poewiki Sirus rev 1702453"}
    start_inputs: {multiplierFrozenByYouSeconds: 0}
    rounds_max: 3
    stop_delta_s: 1
    freeze_accrual_during_immunity: false
    uber_damage_taken: "raw HP / Uber-preset FullDPS; the 70% less damage taken is already inside that FullDPS (CalcOffence.lua:3492-3493); never divide HP by 0.3 again (ratio check Uber / Pinnacle FullDPS = 0.3000 on both samples)"
    missing_boss_row: gap
    no_pob_fallback: "no PoB 7.68 x mapLevelBossLifeMult fallback: that product is the ailment threshold (CalcOffence.lua:5333-5343, PR #4435), not life"
    feed_zero_when_no_freeze: "feed multiplierFrozenByYouSeconds = 0 explicitly when the freeze model says no freeze: PoB applies Cold Mastery 26782 even with conditionEnemyFrozen off (W Uber, frozen off: fz 0 -> 1,952,277, fz 10 -> 2,494,576, +27.8%)"
  formula:
    hp: "life + es (ES removed first and counted once; no ES recharge during immunity assumed)"
    damage_s: "damage_s(n) = floor(hp / floor(FullDPS(n)))"
    t_fight: "t(n) = damage_s(n) + windows * low_s   (range: damage_s(n) + windows * high_s)"
    feed_next: "multiplierFrozenByYouSeconds(n+1) = floor(avg_bonus(damage_s(n)) / 5) if Freeze.md gives uptime >= 0.50 (box ticked by the user rule 2026-10-25) AND Cold Mastery 26782 is allocated, else 0 (set 0 explicitly)"
    avg_bonus: "avg_bonus(L) = (1/L) * integral_0^L min(5 * floor(uptime * t), 50) dt   (uptime 1: L <= 10 -> 2.5*(floor(L)-1)*floor(L)/L approx; L > 10 -> 50 - 275/L)"
    loop: "round 0 with start_inputs; stop when |t(n) - t(n-1)| < 1 s; after round 3 show t(3) with 'not converged' and the spread [min, max] of t(2), t(3)"
    no_dependent_input: "if no fight-length input applies (no freeze or no mastery 26782): one round only"
    display: "per round: round, inputs fed, FullDPS, damage_s, t_fight (low / high); boss label e.g. 'Sirus (default)'; uber_check = FullDPS(Uber) / FullDPS(Pinnacle) at identical inputs, expect ~0.3"
  calibration: "Worb.xml Pinnacle (count 4, ch 3, frozen on, Brine King off): r0 fz 0 6,743,727 -> 10 s / 55 s; r1 fz 4 7,493,030 -> 9 s / 54 s; r2 fz 4 -> 54 s converged (high 99 s). Worb.xml Uber: no freeze (d 0.171 s) -> fz 0, 1,952,277 -> 38 s / 83 s (128 s). Day-1 snapshot (FullDPS include of Winter Orb in memory, count 4, ch 3, no mastery 26782): Pinnacle 4,090,105 -> 17 s / 62 s (107 s); Uber 1,227,031 -> 61 s / 106 s (151 s). Uber check 0.3000 on both samples. Old fixed 30 s: fz 8, Worb Pinnacle 8,242,333 (+10.0%), Worb Uber 2,386,117 although it does not freeze. Source: mechanics-modeler-fight-length.md (probe 2026-10-25)."
providers: []
makes_redundant: []
conflicts: []
conditions:
  - {text: "HP = raw wiki/poedb HP; absolute life is not on poewiki or in PoB (wiki gives only a multiplier, e.g. Sirus 2400%), the absolute factor comes from poedb (secondary source; fandom Sirus agrees within 0.6%)", source: "tasks/reports/027-evidence/mechanics-researcher-boss-hp.md (boss-hp); poewiki Sirus rev 1702453"}
  - {text: "Sirus becomes invulnerable at 75%, 50%, 25% life for 15-30 s each (3 windows; default the low end 45 s, range 90 s); final phase has no throne", source: "poewiki Sirus rev 1702453"}
  - {text: "a boss without a vault HP row gives 'fight length unknown' (gap), never a PoB-derived number", source: "PoB PR #4435; Modules/CalcOffence.lua:5333-5343"}
uptime:
  Pinnacle Boss: {value: model, config: {multiplierFrozenByYouSeconds: "model: floor(avg_bonus over damage time / 5), 0 when Freeze.md says no freeze"}, reasoning: "fight length = Sirus (default) HP / Pinnacle FullDPS plus 3 immune windows; Worb.xml converges at 54 s (99 s with 30 s windows). Uber variant (same scenario, Uber preset): raw Sirus L85 HP / Uber-preset FullDPS, which already holds the 70% less damage taken (CalcOffence.lua:3492-3493); Worb.xml 83 s (128 s), no freeze (d 0.171 s) so multiplierFrozenByYouSeconds 0", source: "mechanics-modeler-fight-length.md (Rounds, Uber ratio check); mechanics-researcher-boss-hp.md (uber-damage-taken); poewiki Sirus rev 1702453"}
  Mapping: {value: none, reasoning: "no boss row; not applicable", source: "mechanics-modeler-fight-length.md (scenarios: mapping)"}
seeds: [Worb]
sources:
  - {ref: "https://www.poewiki.net/wiki/Sirus,_Awakener_of_Worlds (rev 1702453)", kind: wiki, patch: "3.29"}
  - {ref: "poewiki cargo monsters AtlasExile5 (health_multiplier 24, Metadata/Monsters/AtlasBosses)", kind: wiki, patch: "3.29"}
  - {ref: "https://poedb.tw/us/Sirus%2C_Awakener_of_Worlds#SirusAwakenerofWorldsAtlasExile5 (SECONDARY source: absolute life factor, not authoritative)", kind: wiki, patch: "3.29"}
  - {ref: "https://github.com/PathOfBuildingCommunity/PathOfBuilding/pull/4435 (7.68 = ailment threshold) and /pull/4436 (Uber preset -70% damage taken)", kind: github, patch: "3.29"}
  - {ref: "Modules/CalcOffence.lua:3492-3493 (takenInc / takenMore in effective mode), 5333-5343 (ailment threshold)", kind: pob, patch: "3.29"}
not_verified:
  - "Whether the frozen-seconds counter can grow while Sirus is invulnerable (default: no; alternative reading +3 s fz on Worb)"
  - "Whether Sirus's ES recharges during throne windows (if it refills each window, HP +3 x 390,360 = +1.65%)"
  - "Sirus final-phase heal (3.10.0 'heals to 75% ... at Awakening level 8'): old Awakening rule, ignored"
  - "Non-immune downtime (dashes, Meteor Maze, Die beam repositioning) not modelled, so t_fight is a lower bound"
  - "Shock effect per preset: hand-set 57 (W) / 25 (D1) kept; on Uber the hit is 0.3x so the Own shock effect model would give less, Uber FullDPS likely overstated"
  - "D1 freeze at 0.305 s uses the average crit; low-roll crits fall below 0.3 s (crit min not read)"
  - "Boss HP absolute factor (poedb, secondary): f(84)=180.587, f(85)=181.226 derived by mechanics-researcher; what f(L) is made of is undocumented"
  - "D1 FullDPS covers Winter Orb only (golems and other groups not included)"
  - "Venarius / Cortex multipliers (cargo candidates disagree) and the Maven brain-phase count: no row until confirmed"
open_questions:
  - "U7: the poewiki has only life multipliers; absolute boss HP needs poedb's factor (secondary, Sirus agrees with fandom within 0.6%). Accept poedb-derived HP as the default source?"
```
