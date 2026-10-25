---
type: interaction
status: draft
pob_refs: [SupportCastOnCriticalStrike, SupportCastOnCritTriggered, TriggerRateCap, SkillTriggerRate, EffectiveSourceRate, CooldownRecovery]
source: "PoB 2.67.2 CalcTriggers.lua / sup_dex.lua; poewiki Cast On Critical Strike Support, Cooldown, Trigger (rev 1702121); tasks/reports/021-gate1.md I1-I3c, N3, N9"
last_confirmed_patch: "3.29.x"
---

Cast On Critical Strike (CoC) makes an attack skill's crit trigger a linked spell. The trigger rate is the attack rate x crit chance, but the spell has a 0.15 s cooldown that is rounded up to 33 ms server frames, so there are hard rate breakpoints. Attacking faster than the cap loses procs. Rules: [[CoC requires 100% crit and hit]], [[Trigger attack under the CoC cap]], [[Trigger attack stays at cheapest level]].

Pipeline: [[Damage calculation#Hit rate]], [[Damage calculation#Critical strike]] - the trigger fires from a crit, so it needs crit chance (Critical strike) and its proc rate is capped by the 0.15 s cooldown (hit rate of the triggered spell); attacking faster than the cap adds no damage

```interaction
id: coc-trigger
mechanic: "Attack crit triggers one linked spell; 0.15 s cooldown in 33 ms frames = max 6.06 / 7.57 / 10.10 / 15.15 triggers per s at 0 / 14 / 52 / 128% cooldown recovery; faster attacks lose procs"
family: trigger
pipeline_step: ["Damage calculation#Hit rate", "Damage calculation#Critical strike"]
pipeline_why: "the trigger fires from a crit, so it needs crit chance (Critical strike) and its proc rate is capped by the 0.15 s cooldown (hit rate of the triggered spell); attacking faster than the cap adds no damage"
target: self
related: [channelling, returning-projectiles]
pob:
  measured: full
  how: "CalcTriggers.lua:1156-1159 (handler), 736-782 (rate = hit chance x crit chance), 563-591 (cap, rounded up to the server tick), 91-134 (simulation); outputs TriggerRateCap, SkillTriggerRate, EffectiveSourceRate. Like Clockwork is NOT in PoB gem data (grep clockwork found only spectre.lua Heist skills)"
  config: []
  unparsed: []
model:
  proposed_kind: coc_cooldown_recovery_from_granted_passive
  inputs: {from_pob: [TriggerRateCap, SkillTriggerRate, CooldownRecovery], from_scenario: []}
  params: {like_clockwork_cdr_pct: 50, breakpoints_pct: [0, 14, 52, 128], breakpoint_rates_per_s: [6.06, 7.57, 10.10, 15.15]}
  formula: "Like Clockwork (50% cooldown recovery) is below the 52% breakpoint: alone it gives 132 ms = 7.57/s; it needs >= 2% more from another source for 99 ms = 10.10/s. The granted passive is only counted if the Forbidden pair is worn (CalcSetup.lua:1401-1416)"
  calibration: "wiki CoC breakpoint table (source reddit fh8bnh); PoB cap formula 1 / (ceil(0.15 / icdr / 0.033) x 0.033)"
providers:
  - {kind: support, name: "Cast On Critical Strike", slot: any, role: enables, target: self, text: "attack crit triggers a linked spell; cooldown 0.15 s, storedUses 1; -19% (L1) to -10% (L20) less Spell Damage, -9% at L21", source: "PoB Data/Skills/sup_dex.lua:519-535, 584-631", pob: full}
  - {kind: support, name: "Awakened Cast On Critical Strike", slot: any, role: scales, target: self, text: "Awakened gems cap at level 5: -7% spell damage, +22% cooldown speed, cooldown still 0.15; only passes the 14% breakpoint (132 ms)", source: "PoB sup_dex.lua:699-731; skill-gem-analyst", pob: full}
  - {kind: unique, name: "Forbidden Flame + Forbidden Flesh (pair, same notable, class match)", slot: jewel, role: scales, target: self, text: "grants Saboteur notable Like Clockwork: 50% increased Cooldown Recovery Rate", source: "PoB ModParser.lua:5540; CalcSetup.lua:1401-1416; tree.lua (3_29) 84689-84698, skill id 51462", pob: partial, variant: "pair is user-pasted text, not in Data/Uniques"}
  - {kind: ascendancy, name: "Like Clockwork (Saboteur)", slot: tree, role: scales, target: self, text: "50% increased Cooldown Recovery Rate (wiki: 3.28.0 raised 40 -> 50%)", source: "TreeData/3_29/tree.lua:84691-84697; poewiki Like Clockwork", pob: full}
  - {kind: unique, name: "The Flow Untethered", slot: belt, role: scales, target: self, text: "(15-20)% cooldown recovery rate", source: "PoB Data/Uniques/belt.lua:332", pob: full}
  - {kind: unique, name: "The Torrent's Reclamation", slot: belt, role: scales, target: self, text: "(15-20)% cooldown recovery rate", source: "PoB Data/Uniques/belt.lua:348", pob: full}
  - {kind: unique, name: "The Sands of Time", slot: mace, role: scales, target: self, text: "(10-15)% cooldown recovery rate", source: "PoB Data/Uniques/mace.lua:607", pob: full}
  - {kind: ascendancy, name: "Ascendant/Saboteur 58827", slot: tree, role: scales, target: self, text: "15% increased Cooldown Recovery Rate", source: "tree-ascendancy-analyst; TREE L21157", pob: full}
  - {kind: tattoo, name: "Tattoo of the Tasalio Makanga", slot: tree, role: scales, target: self, text: "8% increased Cooldown Recovery Rate", source: "tree-ascendancy-analyst; TAT L4039", pob: full}
  - {kind: gem, name: "Cyclone (trigger attack, L1-L20)", slot: gem, role: enables, target: self, text: "attack source; damage mult 0.816-1.5, cost 2/3/4, move speed -30% to -20%; EK pins L1, FR pins L20", source: "PoB act_dex.lua:4721-4768; 021-gate1 I2", pob: full}
makes_redundant: []
conflicts:
  - {with: "Winter Orb as the triggered spell", effect: "cannot be CoC-triggered (no Triggerable skill type; channelling skills cannot be triggered)", source: "PoB act_int.lua:20963; wiki Channelling; skill-gem-analyst"}
  - {with: "Resolute Technique / Precise Technique", effect: "never deal Critical Strikes: no trigger", source: "TREE L21817 / L68373; 021-gate1 I1 (tree.lua:21813)"}
  - {with: "a second attack skill in the CoC group", effect: "CoC source = fastest attack in its group; never add a second attack", source: "CalcTriggers.lua:75-87, 1156-1158; 021-gate1 I3b"}
conditions:
  - {text: "crit chance 100% and hit chance 100% on the trigger attack, or the trigger rate drops by the same factor", source: "CalcTriggers.lua:739-781; vault Rules/CoC requires 100% crit and hit"}
  - {text: "only ONE spell is triggered per CoC event; identical spells share the cooldown", source: "poewiki Cast On Critical Strike Support, Trigger rev 1702121"}
  - {text: "enforce source attack rate <= cap; near-cap band is not simulated by the audit (new breaks only)", source: "021-gate1 I3"}
uptime:
  Mapping:       {value: pob, config: {}, reasoning: "Use PoB's TriggerRateCap/SkillTriggerRate, not 100%: mapping has stray hits and movement, the attack is not continuous. Like Clockwork added as a model (50% cooldown recovery) because PoB lacks it", source: "build-strategist table; CalcTriggers.lua:563-591"}
  Pinnacle Boss: {value: pob, config: {}, reasoning: "High while the boss is attackable; lost in boss immunity or phase transitions (no attack = no trigger). PoB number", source: "build-strategist table"}
seeds: [EK, FR]
sources:
  - {ref: "PoB Modules/CalcTriggers.lua, Data/Skills/sup_dex.lua (2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Cast_On_Critical_Strike_Support (rev 1681748)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Cooldown (server frames)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Trigger (rev 1702121)", kind: wiki, patch: "3.29"}
  - {ref: "tasks/reports/021-gate1.md rows I1-I3c, N3, N9", kind: discovery, patch: "3.29"}
not_verified:
  - "Whether the 0.15 s cooldown applies per triggered spell or per gem for all spells at 3.29 (wiki 2.4.0 history: per triggered skill; PoB stores it on the support row)"
  - "Whether Like Clockwork reaches the triggered spell in PoB (CalcTriggers reads the main skill modList incl. global CooldownRecovery); not run headless"
  - "Whether EK sits at the cap (seed pin says unverified)"
  - "Lucky crit (Calculated Risk) raising the chance in the CoC check"
open_questions:
  - "None for the user; the Like Clockwork 50% < 52% reading is a lead ruling."
```
