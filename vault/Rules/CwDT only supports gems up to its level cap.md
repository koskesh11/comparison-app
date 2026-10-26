---
type: rule
kind: hard_constraint
status: verified
pob_refs: [SupportCastOnDamageTaken, local_support_gem_max_skill_level_requirement_to_support, levelRequirement]
source: "user 2026-10-25 (verified); poewiki Cast when Damage Taken Support rev 1681765; PoB 2.67.2 Data/Skills/sup_str.lua:1173,1181-1220"
last_confirmed_patch: "3.29.x"
---

```rule
# Nothing here is evaluated by rules.py yet (no require/forbid, no when).
proposed_check:                     # needs a cross-skill check in the engine
  support: SupportCastOnDamageTaken
  cap_stat: local_support_gem_max_skill_level_requirement_to_support   # 3rd value of each level row, sup_str.lua:1181-1220 (= CwDT's own levelRequirement)
  break_when: "levelRequirement of the supported ACTIVE skill gem > cap of the CwDT level"
  applies_to: skill_gems_only       # support gems are not affected
  also_has_stat: "Dark Ritual (act_int.lua:1590, 1758) carries the same stat"
  reject: new_breaks_only           # a build already over the cap is shown the fix, not blocked
tradeoff:
  show: [cwdt_level, cap, triggered_gem_level, triggered_gem_requirement, threshold, cost]
  paths:
    raise_cwdt: "raise CwDT to the level whose cap >= the requirement (L20 cap 70 fits both 70-requirement gems below); higher level also raises the damage threshold (L14 1980, L20 3272) and lowers the 'less damage' penalty"
    lower_triggered_gem: "lower the triggered gem to a level whose requirement <= the cap (less effect or duration from the gem)"
```

**Rule:** Cast when Damage Taken (CwDT) cannot support a skill gem whose level requirement is higher than CwDT's own. Wiki, verbatim: "Cast when Damage Taken cannot support skills with a higher level requirement than that of Cast when Damage Taken itself. This restriction only applies to skill gems; support gems are not affected." Gem text: "This Gem can only Support Skill Gems requiring Level x or lower" (PoB Data/StatDescriptions/stat_descriptions.lua:62686). Version history 1.0.1: "The level requirement of gems augmented by Cast on Damage Taken may not exceed the level requirement of the Cast on Damage Taken gem." Verified in game by the user, 2026-10-25.

**Cap table** (cap = CwDT's own levelRequirement, Data/Skills/sup_str.lua line 1180 + level): L1 38, L2 40, L3 42, L4 44, L5 46, L6 48, L7 50, L8 52, L9 54, L10 56, L11 58, L12 60, L13 62, L14 64, L15 65, L16 66, L17 67, L18 68, L19 69, L20 70, L21 72; L22-L30 74 to 90 in steps of 2; L31-L40 91 to 100 in steps of 1.

**PoB does not enforce it:** `grep -rn "local_support_gem_max_skill_level_requirement_to_support" Modules Classes Data/SkillStatMap.lua` = 0 hits; ModCache 0 hits; calcLib.canGrantedEffectSupportActiveSkill (Modules/CalcTools.lua:86-130) checks no level. PoB counts the trigger anyway, so DPS and trigger rate of a broken link are overstated (the game triggers nothing).

**Breaks in the golden builds:**
- EK (3.29/Ninja Builds/CoC EK Assa.xml, boots group): Vulnerability L20 (levelRequirement 70, act_str.lua:12977) under CwDT L14 (cap 64).
- Worb (3.29/Worb.xml, helmet group): Frost Shield L20 (70, act_int.lua:8087) under CwDT L6 (cap 48).
- Not a break: Worb Immortal Call L8 (48, act_str.lua:6809) under CwDT L6 (48; the check is "<=").

**Fixes (trade-off, not a verdict):** raise CwDT to L20 (cap 70), which fits both L20 gems above, or lower the triggered gem to a level whose requirement is at most the cap.

Related: [[Cast when damage taken]], [[Trigger attack under the CoC cap]].
