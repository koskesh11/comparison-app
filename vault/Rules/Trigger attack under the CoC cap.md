---
type: rule
kind: hard_constraint
status: draft
pob_refs: [SupportCastOnCriticalStrike, SupportAwakenedCastOnCriticalStrike, SupportCooldownRecovery, EffectiveSourceRate, TriggerRateCap, SkillTriggerRate]
source: "PoB 2.67.2 (3.29) Modules/CalcTriggers.lua; poewiki Cast On Critical Strike Support; headless sweep on FR CoC v3/v4 (in memory, 2026-10-21)"
last_confirmed_patch: "3.29.x"
---

```rule
# Nothing here is evaluated by rules.py yet (no require/forbid).
when:
  linked_support_any: [SupportCastOnCriticalStrike, SupportAwakenedCastOnCriticalStrike]
evaluate_on: triggered_spell        # not implemented in rules.py yet
proposed_check:                     # needs a cross-skill check in the engine
  source_rate: { skill: triggered_spell, stat: EffectiveSourceRate }   # = trigger attack's rate
  cap:         { skill: triggered_spell, stat: TriggerRateCap }
  actual:      { skill: triggered_spell, stat: SkillTriggerRate }
  break_when: "cap * (1 - margin) < source_rate < 2 * cap"            # wiki: multiples of the attack rate also work
  margin: 0                         # user decision 2026-10-22: aim exactly at the cap
  reject: new_breaks_only           # a build already over the cap is shown the fix, not blocked
tradeoff:
  show: [dps, cost_per_second_per_resource, movement_speed, margin_to_cap]
  paths:
    more_cooldown_recovery: "PoB's own 'extra ICDR of N% would reach next breakpoint' (CalcTriggers.lua:663-683, breakdown only in MAIN/CALCS mode); raises the triggered spell's cap only, e.g. Cooldown Recovery support (links to the spell, not the attack)"
    less_attack_speed: "Tabulate Speed INC/MORE on the trigger source skill (CalcSections.lua:577-578); weapon-local speed sits in the base (Item.lua:2294-2295)"
```

**Rule:** with CoC, the attack must not trigger faster than the spell's cap allows. Slightly over the cap costs more than slightly under. Paths relative to `%APPDATA%\Path of Building Community`.

**How PoB gets the numbers (headless 2026-10-21):**
- Cap = 1 / (ceil(0.15 / icdr / 0.033) x 0.033). icdr = 1 + cooldown recovery of the triggered spell (`Modules/CalcTriggers.lua:563-591`); server tick 0.033 s (`Modules/Data.lua:237-238`); CoC cooldown 0.15 s (`Data/Skills/sup_dex.lua:610`).
- Breakpoints: 0 / 14 / 52 / 128% cooldown recovery -> 6.06 / 7.58 / 10.10 / 15.15 triggers per second.
- The three keys exist only on the triggered spell's output. The actual rate comes from a 1000-attack simulation (`CalcTriggers.lua:91-134`).
- Several spells in one CoC link take turns (`CalcTriggers.lua:1156-1159`).

**How much going over costs (v4 sweep, trigger rate as % of cap):** +0.07% -> 99.9%; +0.82% -> 97.5%; +5.34% -> 84.1%; +30% -> 66.6%; +100.9% -> about full.

**Wiki** (*Cast On Critical Strike Support*, gem unchanged since 3.17.0): "exceeding the attack rates even slightly can significantly reduce proc rate ... It is better to be slightly below the attack rate than above it. Note that multiples of the attack rate also work".

**Real case, v3 -> v4:** Cyclone 10.03 -> 7.52/s (Silver -> Sapphire flask under Mageblood: Onslaught lost; gloves 16% -> 11% attack speed). FR 5.07 -> 7.52/s, FullDPS 38.49M -> 57.00M. Costs: movement speed mod 2.192 -> 1.88, FR ES cost 755 -> 1,121 /s.

**Risk:** a DPS maximiser picks +0.07% over the cap, because PoB shows almost no loss there. The user set the margin to 0 on 2026-10-22: aim exactly at the cap, never above it (UNVERIFIED how far below the cap is safe in game).

Related: [[CoC requires 100% crit and hit]], [[FR CoC Cyclone - skills and supports]], [[Total skill cost must be sustainable]].
