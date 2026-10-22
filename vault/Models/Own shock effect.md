---
type: model
status: draft
pob_refs: [conditionEnemyShocked, conditionShockEffect, enemyIsBoss, ailmentMode, ShockEffectMod, ShockDuration, MaximumShock, ShockChanceOnHit, ShockChanceOnCrit, ChaosCanShock]
superseded_by_pob:
source: "PoB 2.67.2 (3.29) Modules/CalcOffence.lua, Modules/CalcPerform.lua, Modules/Data.lua; poewiki Shock (3.9.0); headless runs on FR CoC v2/v4 (in memory, 2026-10-21)"
last_confirmed_patch: "3.29.x"
---

```model
proposed_kind: own_shock_effect     # not in models.py KINDS yet; no "kind:" so the app skips this note
applies_to: { scope: all_enabled_skill_groups }   # shock is an enemy debuff; the strongest source wins
inputs:
  from_pob_per_skill: ["<Type>CritAverage", "<Type>HitAverage", CritChance, HitChance, ShockChanceOnHit, ShockChanceOnCrit, ShockEffectMod, ShockDuration, MaximumShock, Speed]   # <Type> = Lightning + types whose <Type>CanShock flag is set
  from_pob_enemy: threshold      # breakdown ShockDPS row tagged "(<enemyIsBoss>)" (CALCS env only), cross-check CalcOffence.lua:5333-5342
  from_pob_config: [enemyIsBoss, enemyLevel, ailmentMode, conditionEnemyShocked, conditionShockEffect]
  from_model: hits_per_cast      # Model "Projectiles hitting a single target" for FR, else 1
params:
  base: 50          # CalcOffence.lua:5353; wiki E = 1/2*(D/T)^0.4*(1+M), 3.9.0, tagged "potentially outdated"
  exponent: 0.4
  min_effect: 5     # Data.lua:427; wiki: shocks below the minimum "are never applied"
solve:              # D from a run WITHOUT config shock (otherwise it feeds itself)
  per_source: "crit: D = sum <Type>CritAverage, p = Crit*Hit; non-crit: D = sum <Type>HitAverage, p = (1-Crit)*ShockChanceOnHit*Hit"
  raw: "50 * (D/T)^0.4 * ShockEffectMod"
  S: "0 if raw < 5 else floor(min(raw, MaximumShock))"
  uptime: "1 - (1-p)^(Speed * ShockDuration * hits_per_cast)"     # model, not PoB
  shock: "floor(max over sources of uptime * S)"
  feed_pob: { conditionEnemyShocked: true, conditionShockEffect: shock }   # PoB computes the DPS; shown next to PoB's own number
freeze_note: "duration 0.06 s per 1% of T dealt, x FreezeDurationMod; minimum 0.3 s (needs D >= T/20), max 3 s; no DPS; pinnacle bosses floor at 50% action speed (3.25.0)"
scenarios: { single_target: "enemyIsBoss as set", pack: "no-boss T -> usually the cap; per-enemy uptime not modelled" }
```

**Gap:** PoB works out your own shock % only in the breakdown table (`Modules/CalcOffence.lua:5447`; rows are not capped and sub-5% rows are listed). There is no output key. DPS changes only through the config pair (`Modules/CalcPerform.lua:3565-3606`), and then for every hit and DoT of every skill (`CalcPerform.lua:3519-3530`). Paths relative to `%APPDATA%\Path of Building Community`.

**Model:** take the hit size D from a run without config shock, compute the shock PoB would show, scale by uptime, round down ([[Models round down]]), then feed it back into PoB's config so PoB does the DPS math.

**FR CoC numbers (headless):**
- v4: FR ChaosCritAverage 1,263,421. Pinnacle T 6,349,995 -> 26% -> FullDPS 57.00M -> 65.19M (+14.4%). Standard Boss T 7,865,171 -> 24% (+13.3%). No boss T 38,853 -> capped 50% (+27.6%).
- v2: 28% (+15.5%).
- Uptime ~100%: FR crits 100%, ShockDuration 2.667 s, 7.52 triggers/s.

**Risks:**
- Multiplying DPS by (1 + S) instead of feeding config gives 71.8M, not 65.19M (damage taken stacks additively).
- Reading D with shock already applied gives 27%.
- Scenario notes set no enemyIsBoss, so [[Mapping]] still uses the saved Pinnacle threshold.

**User to verify (UNVERIFIED):** the formula is current (wiki tags it "potentially outdated"); whether the 5% minimum applies before or after effect mods; Three Dragons chaos shock with FR in game; the generic boss threshold.

Related: [[Foulborn Three Dragons - chaos shock and freeze]], [[Foulborn The Three Dragons]], [[Projectiles hitting a single target]].
