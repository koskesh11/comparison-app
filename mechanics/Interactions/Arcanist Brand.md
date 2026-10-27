---
type: interaction
status: draft
pob_refs: [triggeredByBrand, repeatFrequency, BrandActivationFrequency, attachedBrandCount, BrandsAttachedLimit, TargetingBrandedEnemy, TriggeredDamage, TriggerRateCap, SkillTriggerRate, EffectiveSourceRate]
source: "PoB 2.67.2 CalcTriggers.lua:1326-1346, 427-436, 565-583, 814-832, 892; CalcPerform.lua:1358-1370; Data/Skills/act_int.lua:544-703; Data/SkillStatMap.lua:2147-2166; ConfigOptions.lua:332-338; poewiki Arcanist Brand rev 1682135; headless scratch variants of CoC EK Assa.xml and FR CoC Occu Three Dragons v4.xml (task 027 batch 3)"
last_confirmed_patch: "3.29.x"
---

Arcanist Brand turns the linked spell into a trigger skill: you cast a brand (0.8 s cast), it attaches to an enemy and activates once per 1.0 s base (cast speed, brand activation frequency and quality speed it up), triggering the linked spells in turn. This note covers only the trigger behaviour; what brands are in general (attach limit, Brand Recall, duration) is in the batch 2 brand note. The supported spell deals 69% less damage (L1) / 63% less (L20) but 40% / 59% MORE with hits against the branded enemy, and area of effect and chaining range are 40% less. The trigger has no cooldown of its own, so the rate is the brand's activation rate, far below a CoC rate (EK sample 1.78/s against 8.93/s).

Pipeline: [[Damage calculation#Hit rate]], [[Damage calculation#More and less]] - the brand activation frequency is the hit rate of the triggered spell (Hit rate); the less / more damage pair is two MORE multipliers on the triggered spell (More and less).

```interaction
id: arcanist-brand
mechanic: "Brand attached to an enemy triggers the linked spell once per activation: 1.0 s base / (cast speed and activation frequency) x attached brands; no cooldown, not rounded to server ticks; supported spell deals 69-63% less damage and 40-59% more vs the branded enemy (L1-L20), 40% less AoE"
family: trigger
pipeline_step: ["Damage calculation#Hit rate", "Damage calculation#More and less"]
pipeline_why: "the brand's activation rate is the source rate of the triggered spell (hit rate of the triggered spell); the less (x0.37) and more vs branded enemy (x1.59) damage are separate MORE multipliers on the spell"
target: enemy
related: [coc-trigger, trigger-rate-cap, spellslinger, cast-on-melee-kill, cast-while-channelling]
pob:
  measured: partial
  how: "handler CalcTriggers.lua:1326-1346: when the main skill is NOT the brand itself, source = the Arcanist Brand skill in the build, trigRate = repeatFrequency (1.0 s, SkillStatMap.lua:2160-2162) x (1 + INC of Speed and BrandActivationFrequency) x MORE BrandActivationFrequency x attachedBrandCount; ignoresTickRate is set (the brand period is not rounded to 33 ms, :583); triggerCD of the triggered spell = brand period (:571-575). Attached brand count = min(config 'BrandsAttachedToEnemy' or the limit, BrandsAttachedLimit) with default limit 1 from base_number_of_sigils_allowed_per_target (CalcPerform.lua:1358-1362; SkillStatMap.lua:2153-2156). Triggered-skill damage: support_brand_damage_+%_final as TriggeredDamage MORE; vs-branded-enemy bonus applies only with Condition:TargetingBrandedEnemy (config targetBrandedEnemy, default true, ConfigOptions.lua:337). Headless EK (Ethereal Knives, Arcanist Brand L20 q20 replacing CoC): EffectiveSourceRate = TriggerRateCap = SkillTriggerRate = 1.78, info 'Arcanist Brand:1 attached Brand', TotalDPS 1009907 (CoC variant 7728444); config BrandsAttachedToEnemy 3 left it at 1 attached brand and 1.78 (limit 1). FR (Forbidden Rite): 1.39/s, TotalDPS 6669873 (CoC 57035872). Not counted: that the brand must be recast when it expires or its enemy dies, the 0.8 s cast and the brand's own mana cost (18 at L1, 32 at L20), and the time to attach"
  config:
    - {var: BrandsAttachedToEnemy, default: 0, ref: "Modules/ConfigOptions.lua:334 (count; capped by BrandsAttachedLimit, default 1)", class: b}
    - {var: targetBrandedEnemy, default: true, ref: "Modules/ConfigOptions.lua:337", class: b}
    - {var: ConfigActiveBrands, default: 0, ref: "Modules/ConfigOptions.lua:332 (number of active brands, limit 3)", class: b}
  unparsed: []
model:
  proposed_kind: brand_attach_uptime
  inputs: {from_pob: [TriggerRateCap, SkillTriggerRate], from_scenario: [brand_attached_fraction]}
  params: {attached_duration_s: 5, unattached_duration_s: 3, cast_time_s: 0.8}
  formula: "triggers per second = brand_attached_fraction x PoB SkillTriggerRate; PoB uses brand_attached_fraction = 1"
  calibration: "no norm found for the attached fraction (needs a living enemy in range; the brand detaches when its enemy dies, wiki rev 1682135 'The brand will detach if the enemy dies' in the gem description)"
providers:
  - {kind: gem, name: "Arcanist Brand (active part)", slot: any, role: enables, target: enemy, text: "Spell, Duration, Multicastable, Brand skill; cast time 0.8 s; base_sigil_repeat_frequency_ms 1000; attached effect duration 5000 ms, unattached 3000 ms; 1 brand per target by default; mana cost 18 (L1) / 32 (L20) / 43 (L40); quality +0.5% brand repeat frequency per 1%", source: "Data/Skills/act_int.lua:544-617 (constants :567-570, cost L1 :577, L20 :596, L40 :616)", pob: full}
  - {kind: support, name: "Arcanist Brand (support part)", slot: any, role: scales, target: self, text: "requires Triggerable AND Spell; adds Triggered; excludes Trapped, RemoteMined, SummonsTotem, HasReservation, InbuiltTrigger; ignores minion types; less damage -69 / -63 / -56 % and more damage vs branded enemy +40 / +59 / +74 % (L1 / L20 / L40); constants: AoE 40% less, chaining range 40% less, projectile max range 48 (4.8 m); no cooldown row", source: "Data/Skills/act_int.lua:619-703 (L1 :663, L20 :682, L40 :702)", pob: full}
makes_redundant: []
conflicts:
  - {with: "any other trigger support on the same spell (CoC, CoMK, CwC, CwDT, Spellslinger)", effect: "PoB disables the spell: 'This skill is supported by more than one trigger'; the wiki adds that Arcanist Brand cannot gain a trigger from support gems or items", source: "Modules/CalcActiveSkill.lua:531-537; wiki rev 1682135"}
  - {with: "minion skills (for example Raise Spectre)", effect: "minions are not modified by the support (no penalty and no bonus), the 4.8 m projectile range still applies (wiki says possible bug)", source: "Data/Skills/act_int.lua:628 (ignoreMinionTypes); wiki rev 1682135"}
  - {with: "spells that reserve mana, totem, trap and mine spells", effect: "cannot be supported", source: "Data/Skills/act_int.lua:619-628"}
conditions:
  - {text: "the brand must be attached to an enemy; it then activates once per activation period and triggers all linked spells in sequence until its duration ends (5 s attached)", source: "poewiki Arcanist Brand rev 1682135; Data/Skills/act_int.lua:567-570"}
  - {text: "triggered spells are not Brand skills but count as dealing Brand Damage and Brand Critical Strikes for brand modifiers", source: "poewiki Arcanist Brand rev 1682135"}
  - {text: "the more damage vs the branded enemy needs the spell to hit the enemy the brand is attached to (config targetBrandedEnemy)", source: "ConfigOptions.lua:337; act_int.lua:641"}
uptime:
  Mapping:       {value: model, config: {targetBrandedEnemy: true, BrandsAttachedToEnemy: 1}, reasoning: "PoB assumes the brand is attached all the time. In a pack the brand must be recast when its enemy dies (attached duration 5 s); the attached fraction is a model input. No norm found", source: "CalcTriggers.lua:1326-1346; wiki rev 1682135"}
  Pinnacle Boss: {value: high, config: {targetBrandedEnemy: true, BrandsAttachedToEnemy: 1}, reasoning: "One long-lived target keeps the brand attached for its 5 s duration; the brand is lost to boss immunity or untargetable phases and must be recast (0.8 s cast). Rate is the PoB number while attached", source: "wiki rev 1682135; Data/Skills/act_int.lua:567-570"}
seeds: []
sources:
  - {ref: "PoB Modules/CalcTriggers.lua, CalcPerform.lua, Data/Skills/act_int.lua, Data/SkillStatMap.lua, Modules/ConfigOptions.lua (2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Arcanist_Brand (rev 1682135; 3.17.0 damage 69-63% less)", kind: wiki, patch: "3.29"}
not_verified:
  - "How often the brand must be recast in mapping and on a boss, and the share of time it is attached (no norm found); PoB assumes always attached"
  - "Sources of extra attached brands (BrandsAttachedLimit above 1) and their effect on the rate: the config count was capped at the limit 1 in the headless test; not run with a source of '+1 brand attached'"
  - "Whether the brand's own mana cost (18-43) and 0.8 s cast time are summed with the triggered spell in the cost budget (outside this note; see Total skill cost must be sustainable)"
  - "Brand mechanics in general (attach limit, Brand Recall, Wave of Conviction detail) are left to the batch 2 brand note"
open_questions:
  - "Is a brand-triggered build wanted as a seed, or only as a comparison against CoC on EK/FR (rate 0.2x of CoC in the headless test)?"
```
