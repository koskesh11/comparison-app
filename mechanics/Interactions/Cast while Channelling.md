---
type: interaction
status: draft
pob_refs: [triggerTime, triggeredWhileChannelling, ChannelTimeToTrigger, TriggerRateCap, SkillTriggerRate, TriggeredDamage, CooldownRecovery]
source: "PoB 2.67.2 CalcTriggers.lua:222-392 (CWCHandler), 1398-1400; Data/Skills/sup_int.lua:678-905; Data/SkillStatMap.lua:248-250; poewiki Cast while Channelling Support rev 1681944; headless variants of CoC EK Assa.xml and FR CoC Occu Three Dragons v4.xml (scratch copies, task 027 batch 3)"
last_confirmed_patch: "3.29.x"
---

Cast while Channelling (CwC) makes a channelling skill trigger one linked spell on a FIXED interval while the channel is held: 0.40 s at L1, 0.32 s at L20 (3.125 triggers per second at best), and the triggered spell deals 20% less damage (3.29.0). There is no crit or hit requirement and no support cooldown, so the rate does not depend on attack speed, only on gem level and on how long you channel. That makes it much slower than CoC on a fast Cyclone (EK sample: 3.13/s against 8.93/s), but it works for builds that cannot crit. What channelling itself means (moving, no other action) is in [[Channelling]] and is not repeated here.

Pipeline: [[Damage calculation#Hit rate]], [[Damage calculation#More and less]] - the fixed interval is the hit rate of the triggered spell (Hit rate); the 20% less damage is a MORE (less) multiplier on the triggered spell (More and less).

```interaction
id: cast-while-channelling
mechanic: "Channelling skill triggers one linked non-channelling spell every 0.40 s (L1) to 0.32 s (L20) while channelled (max 3.125/s at L20); triggered spell deals 20% less damage; no support cooldown, rate independent of attack speed"
family: trigger
pipeline_step: ["Damage calculation#Hit rate", "Damage calculation#More and less"]
pipeline_why: "the fixed channel interval is the hit rate of the triggered spell (rate = 1 / interval, capped by the spell's own cooldown); the -20% damage is a MORE multiplier on the triggered spell"
target: self
related: [channelling, coc-trigger, trigger-rate-cap, cast-on-melee-kill, cast-when-damage-taken, totems]
pob:
  measured: partial
  how: "CWCHandler (CalcTriggers.lua:222-392, registered at :1398-1400): source = the FIRST active skill in the same socket group that has skillData.triggerTime (set only on Channel skills supported by the primary gem, SkillStatMap/sup_int.lua:688-690), is not itself triggered and passes calcLib.canGrantedEffectSupportActiveSkill of the primary support (:228-236); triggered spells = skills with triggeredWhileChannelling in the same group (SkillStatMap.lua:248-250). Rate: TriggerRateCap = min(1/effective cooldown of the spell, 1/interval) (:249-262); SkillTriggerRate from calcMultiSpellRotationImpact (spells cycle in socket order). Not counted: how long the channel is held (PoB treats it as 100% of the time; toggling channellingCycloneCheck did not change the numbers). Headless EK (Cyclone L1 source, Ethereal Knives, CwC L20 replacing CoC): ChannelTimeToTrigger 0.32, TriggerRateCap 3.125, SkillTriggerRate 3.128125 (the 1000-attack simulation overshoots the cap by 0.003), TotalDPS 2440337 (CoC variant 7728444 at 8.93/s). Same rate on the FR sample: 3.128125, TotalDPS 20705949 (CoC 57035872)"
  config: []
  unparsed: []
model:
  proposed_kind: channel_hold_uptime
  inputs: {from_pob: [ChannelTimeToTrigger, TriggerRateCap, SkillTriggerRate], from_scenario: [channel_hold_fraction]}
  params: {interval_s_l1: 0.4, interval_s_l20: 0.32, interval_s_l40: 0.26, less_damage_pct: 20, awakened_interval_s_l5: 0.3, awakened_less_damage_pct: 30}
  formula: "triggers per second = channel_hold_fraction x min(1 / interval, 1 / spell cooldown); PoB uses channel_hold_fraction = 1"
  calibration: "no norm found for the channel hold fraction in mapping or on a boss"
providers:
  - {kind: support, name: "Cast while Channelling", slot: any, role: enables, target: self, text: "Channel skill triggers a linked spell every 400 ms (L1) / 320 ms (L20) / 260 ms (L40); primary part requires Channel and excludes SummonsTotem, DisallowTriggerSupports; quality +0.5% channelled skill damage per 1%", source: "Data/Skills/sup_int.lua:678-745 (L1 line 705, L20 line 724, L40 line 744)", pob: full}
  - {kind: support, name: "Cast while Channelling (triggered part)", slot: any, role: scales, target: self, text: "linked spell must be Spell AND Triggerable; excludes SummonsTotem, InbuiltTrigger, DisallowTriggerSupports; no cooldown row; constant 20% less damage as TriggeredDamage MORE at every level; quality +0.5% triggered skill damage per 1%", source: "Data/Skills/sup_int.lua:747-813 (requires :752, excludes :754, constant :765-766)", pob: full}
  - {kind: support, name: "Awakened Cast While Channelling", slot: any, role: scales, target: self, text: "legacy gem, levels 1-5: 340 ms at L1, 300 ms at L5; triggered part deals 30% less damage; also 100% avoid interruption at L5 (0 below)", source: "Data/Skills/sup_int.lua:815-905 (legacy :826, L1 :845, L5 :849, -30 :887)", pob: full}
  - {kind: gem, name: "Cyclone (channelling source)", slot: gem, role: enables, target: self, text: "Attack, Area, Melee, Movement, Channel: is a valid CwC source (not a Spell, so only the primary support part matters); EK pins L1, FR pins L20", source: "Data/Skills/act_dex.lua:4686; headless EK variant", pob: full}
makes_redundant: []
conflicts:
  - {with: "any other trigger support on the same spell (CoC, CoMK, CwDT, Spellslinger, Arcanist Brand)", effect: "PoB disables the spell: 'This skill is supported by more than one trigger'", source: "Modules/CalcActiveSkill.lua:531-537"}
  - {with: "Spell Totem on the triggered spell", effect: "cannot be supported (SummonsTotem in excludeSkillTypes); the in-game text also names traps and mines but the PoB data row excludes only SummonsTotem and DisallowTriggerSupports", source: "Data/Skills/sup_int.lua:754; wiki rev 1681944"}
  - {with: "a channelling spell (for example Winter Orb) as the triggered spell", effect: "needs Triggerable, which channelling skills lack; CwC links only non-channelling spells", source: "Data/Skills/sup_int.lua:752; wiki rev 1681944 ('non-channelling spells')"}
conditions:
  - {text: "the channelling skill must be held; the spell fires only while channelling and uses the cursor position as its target", source: "poewiki Cast while Channelling Support rev 1681944"}
  - {text: "with several linked spells only one is triggered per interval; they cycle in socket order", source: "poewiki rev 1681944; CalcTriggers.lua:91-134 (rotation simulation)"}
  - {text: "the rate is independent of the cast time or cooldown of the channelling skill; flat added cooldown (for example Lightning Conduit) counts against the interval only above it", source: "poewiki rev 1681944 (Casting Interval)"}
  - {text: "a supported minion-summoning spell: the 20% less damage does not apply to the minions", source: "poewiki rev 1681944 (Minions, youtube ref)"}
uptime:
  Mapping:       {value: partial, config: {}, reasoning: "Triggers only while the channel is held. PoB assumes 100%; real mapping includes moving without the channel, other skills and loading. No norm found for the held fraction", source: "CalcTriggers.lua:222-392 (no uptime input); wiki rev 1681944"}
  Pinnacle Boss: {value: partial, config: {}, reasoning: "Held channel on a boss is possible but phases, immunity and dodging break it. The rate itself is fixed by the gem level (3.125/s max), so the number is stable while channelling", source: "CalcTriggers.lua:249-262; wiki rev 1681944"}
seeds: []
sources:
  - {ref: "PoB Modules/CalcTriggers.lua, Data/Skills/sup_int.lua, Data/SkillStatMap.lua (2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Cast_while_Channelling_Support (rev 1681944; 3.29.0 history: 0.4-0.32 s, 20% less damage)", kind: wiki, patch: "3.29"}
not_verified:
  - "How long a Cyclone build actually holds the channel in mapping or on a boss (no norm found)"
  - "Whether the EK / FR seeds could use a lower-level Cyclone for CwC: the interval does not depend on Cyclone, only on the CwC gem level (PoB headless used L20)"
  - "Why SkillTriggerRate (3.128125) is above the cap (3.125): the cause is the 1000-trigger simulation in calcMultiSpellRotationImpact (CalcTriggers.lua:91-134); not isolated"
  - "Whether the Awakened gem can still be obtained at 3.29 (legacy = true in the data)"
open_questions:
  - "Is a CwC build wanted for a no-crit seed, or is CwC only a comparison point against CoC on the EK/FR seeds?"
```
