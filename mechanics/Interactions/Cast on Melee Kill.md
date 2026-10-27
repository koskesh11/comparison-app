---
type: interaction
status: draft
pob_refs: [triggeredByMeleeKill, chanceToTriggerOnMeleeKill, Condition:KilledRecently, TriggerRateCap, SkillTriggerRate, EffectiveSourceRate, CooldownRecovery]
source: "PoB 2.67.2 CalcTriggers.lua:1160-1171, 394-470, 563-591; Data/Skills/sup_str.lua:1013-1143; Data/SkillStatMap.lua:239-247; ConfigOptions.lua:1281; poewiki Cast on Melee Kill Support rev 1681749; headless variants of CoC EK Assa.xml and FR CoC Occu Three Dragons v4.xml (scratch copies, task 027 batch 3)"
last_confirmed_patch: "3.29.x"
---

Cast on Melee Kill (CoMK) makes a melee attack skill trigger a linked spell when the attack kills an enemy. The triggered spell gets MORE spell damage instead of the CoC penalty (+20% at L1, +39% at L20, +54% at L40) and has the same 0.15 s cooldown as CoC. The catch is the trigger: it needs a kill, and PoB has no kill-rate input. It turns the support on only with the config tick "Have you Killed Recently?" and then assumes EVERY hit of the melee attack kills, so the PoB rate is an upper bound that is worth most in clear (packs die) and close to nothing on a boss that stays alive. Evidence: tasks/reports/027-evidence/skill-gem-analyst.md and the batch 3 scratch file.

Pipeline: [[Damage calculation#Hit rate]], [[Damage calculation#More and less]] - kills per second bound the hit rate of the triggered spell (Hit rate); the gem's spell damage is a separate MORE multiplier on the triggered spell (More and less).

```interaction
id: cast-on-melee-kill
mechanic: "Melee attack skill kills an enemy -> triggers one linked spell; 0.15 s cooldown in 33 ms frames (cap 10.10/s at 52% cooldown recovery); triggered spell deals 20% (L1) to 39% (L20) MORE spell damage; PoB assumes every hit kills once Killed Recently is ticked"
family: trigger
pipeline_step: ["Damage calculation#Hit rate", "Damage calculation#More and less"]
pipeline_why: "the number of kills per second is the source rate that limits the triggered spell (hit rate of the triggered spell, capped by the 0.15 s cooldown); the gem's +x% spell damage is a MORE multiplier on that spell"
target: self
related: [coc-trigger, trigger-rate-cap, channelling, cast-while-channelling, cast-when-damage-taken, totems, traps-and-mines]
pob:
  measured: config
  how: "CalcTriggers.lua:1160-1171 (handler returns a config only when Condition:KilledRecently is set, else message 'Cast on Melee Kill requires recent kills' and the spell is self-cast); trigger source = Attack AND Melee skill in the same socket group (slotMatch, :27-33); source rate = HitSpeed of that attack from the skill cache (:75-87) times its hit chance (:737-757; crit chance is NOT used because triggerOnCrit is not set); cap from cooldown 0.15 s rounded up to server ticks (:563-591, ServerTickRate 1/0.033 at Modules/Data.lua:238); 'assumingEveryHitKills' (:439-441) only adds a breakdown line, no kill rate is computed. chanceToTriggerOnMeleeKill (SkillStatMap.lua:245-247) is set but read nowhere in Modules (grep). Headless EK (Cyclone L1 source, Ethereal Knives L21, CoMK L20 replacing CoC): tick off -> not triggered, Speed 2.8 self-cast; tick on -> EffectiveSourceRate 8.9208, TriggerRateCap 10.101, SkillTriggerRate 8.9297, TotalDPS 12103959 (CoC variant 7728444, same rates). FR (Cyclone L20 source, Forbidden Rite): tick on -> 7.524, cap 7.5758, TotalDPS 87155917 (CoC 57035872)"
  config:
    - {var: conditionKilledRecently, default: false, ref: "Modules/ConfigOptions.lua:1281", class: b}
    - {var: multiplierKilledRecently, default: 0, ref: "Modules/ConfigOptions.lua:1284 (count; also implies Killed Recently)", class: b}
  unparsed: []
model:
  proposed_kind: melee_kill_trigger_rate
  inputs: {from_pob: [HitSpeed, HitChance, TriggerRateCap], from_scenario: [melee_kills_per_second]}
  params: {kill_fraction_of_hits_mapping: null, kill_fraction_of_hits_boss: null}
  formula: "trigger rate = min(TriggerRateCap, HitSpeed x HitChance x kill_fraction), kill_fraction = melee kills per hit; PoB uses kill_fraction = 1 whenever Killed Recently is ticked (upper bound)"
  calibration: "no norm found for the kill fraction (wiki only says kills must come from the melee attack portion, not from damage over time; forum Cyclone+CoMK guide says clear is strong and bosses are weak, qualitative only)"
providers:
  - {kind: support, name: "Cast on Melee Kill", slot: any, role: enables, target: self, text: "melee attack skill kill triggers a linked spell; support part requires Melee, excludes Trapped, RemoteMined, SummonsTotem, HasReservation, DisallowTriggerSupports; constant cast_linked_spells_on_melee_kill_% 100; quality +0.5% attack damage per 1%", source: "Data/Skills/sup_str.lua:1018-1031", pob: config}
  - {kind: support, name: "Cast on Melee Kill (triggered part)", slot: any, role: scales, target: self, text: "linked spell must be Spell AND Triggerable; adds Triggered and Cooldown; cooldown 0.15, storedUses 1; +20% (L1) .. +39% (L20) .. +54% (L40) MORE spell damage; manaMultiplier 20 (120% cost); quality +0.5% spell damage per 1%", source: "Data/Skills/sup_str.lua:1078-1143 (L1 line 1104, L20 line 1123, L40 line 1143)", pob: full}
  - {kind: gem, name: "Cyclone (melee attack source)", slot: gem, role: enables, target: self, text: "Attack, Area, Melee, Movement, Channel: a valid melee source; both seeds already own it as the CoC source", source: "Data/Skills/act_dex.lua:4686", pob: full}
  - {kind: unique, name: "Squirming Terror", slot: ring, role: enables, target: self, text: "20% chance to Trigger Socketed Spell on Kill, 0.5 s cooldown; PoB handler also needs Killed Recently and assumes every hit kills", source: "Data/Uniques/ring.lua:1695; CalcTriggers.lua:1140-1150", pob: config}
makes_redundant: []
conflicts:
  - {with: "any other trigger support on the same spell (CoC, CwDT, CwC, Spellslinger, Arcanist Brand)", effect: "PoB disables the spell: 'This skill is supported by more than one trigger'", source: "Modules/CalcActiveSkill.lua:531-537"}
  - {with: "Totem, Trap, Mine, reserving or channelling spells", effect: "cannot be the triggered spell (SummonsTotem, Trapped, RemoteMined, HasReservation in excludeSkillTypes; channelling skills have no Triggerable type, see Winter Orb in coc-trigger)", source: "Data/Skills/sup_str.lua:1020 (primary excludes), :1083-1085 (triggered part requires/excludes)"}
conditions:
  - {text: "the kill must come from the melee attack portion of the supported attack; damage over time kills (for example a bleed applied by the melee hit) do not trigger", source: "poewiki Cast on Melee Kill Support rev 1681749 (Skill functions and interactions)"}
  - {text: "trigger source must be an Attack AND Melee skill in the same socket group; a spell kill or minion kill is not a source", source: "CalcTriggers.lua:1164-1166"}
  - {text: "PoB triggers the spell only with Condition:KilledRecently (config tick or kill count)", source: "CalcTriggers.lua:1161; Data/SkillStatMap.lua:240"}
uptime:
  Mapping:       {value: model, config: {conditionKilledRecently: true}, reasoning: "Kills per second in a pack are bounded by the melee hit rate; PoB assumes 1 kill per hit, so use PoB's TriggerRateCap/SkillTriggerRate only as an upper bound. Spread (single-target) hits that do not kill lose triggers; no norm found for the share", source: "CalcTriggers.lua:439-441; wiki rev 1681749"}
  Pinnacle Boss: {value: low, config: {conditionKilledRecently: "set only when adds die; the boss itself dies once"}, reasoning: "The melee hit must KILL; a boss with a large life pool is not killed until the end of the fight, so only adds and the final hit trigger. PoB would still report the full rate with the tick on", source: "wiki rev 1681749 (trigger on kill); CalcTriggers.lua:439-441 (every hit assumed to kill)"}
seeds: []
sources:
  - {ref: "PoB Modules/CalcTriggers.lua, Data/Skills/sup_str.lua, Data/SkillStatMap.lua, Modules/ConfigOptions.lua (2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Cast_on_Melee_Kill_Support (rev 1681749)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.pathofexile.com/forum/view-thread/1207694", kind: forum, patch: "3.29"}
not_verified:
  - "How many melee hits per kill in real mapping and on bosses (no norm found); the model parameters are empty on purpose"
  - "Whether a kill by a melee hit from a minion or from the supported attack's secondary damage (for example Cyclone ground effects) counts; the wiki only names 'melee attack damage'"
  - "Whether CoMK has a per-gem or per-triggered-spell cooldown at 3.29 (same open question as coc-trigger)"
  - "Cast time effect: PoB adds the spell cast time to the cooldown only with the flag SpellCastTimeAddedToCooldownIfTriggered (CalcTriggers.lua:46); not checked for the EK/FR spells"
open_questions:
  - "Which scenario is the CoMK build judged in: pack clear only, or also the pinnacle boss (where it triggers only from adds)?"
```
