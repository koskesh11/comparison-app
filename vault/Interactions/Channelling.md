---
type: interaction
status: draft
pob_refs: [multiplierChannelling, "Multiplier:ChannellingTime", "Condition:Channelling", ManaPerSecondCost, skillStageCount]
source: "wiki Channelling rev 1647943, Focused Channelling Support; PoB 2.67.2 sup_int.lua, ConfigOptions.lua, ModStore.lua, CalcPerform.lua; headless probe on Worb.xml (2026-10-24); skill-gem-analyst, tree-ascendancy-analyst, mechanics-modeler (task 027)"
last_confirmed_patch: "3.29.x"
---

Channelling is one continuous cast whose length is chosen by the player. Focused Channelling adds more damage and more cost per second channelled (lvl 20: 24% per second, damage cap +60% after 2.5 s, cost +20% per second, cap +100% after 5 s). PoB gives Focused Channelling 0 damage and 0 cost until the config 'Channeling for # seconds' is set, and it floors that to whole seconds (3 s = +60% at lvl 20).

On Worb.xml (Pinnacle, Winter Orb, count 5, stage 11) the support is worth +60% at 3 s (FullDPS 7,176,019 -> 11,506,468) but the mana deficit starts at 3 s. Judge the deficit by duration. See also [[Total skill cost must be sustainable]].

```interaction
id: channelling
mechanic: "Channelling skills tick at cast time / cast speed until released, stunned, frozen or unable to pay the cost; Focused Channelling: damage more per second channelled (lvl 20: 24%/s, cap 60%) and cost more (20%/s, cap 100%); costs are paid at start and on every tick"
family: buff
target: self
related: [arcane-surge, coc-trigger]
pob:
  measured: config
  how: "Condition Channelling auto-true for SkillType.Channel (CalcPerform.lua:259-261); Multiplier:ChannellingTime exists only via config multiplierChannelling (ConfigOptions.lua:1274-1276) and is floored (ModStore.lua:403); Focused Channelling = Damage MORE per ChannellingTime limit 60 and Cost MORE limit 100 (sup_int.lua:2538-2600); Winter Orb stage box is separate (skillStageCount, CalcActiveSkill.lua:645-655); headless Worb.xml: 0 s FullDPS 7,176,019 / 95.68 mana/s; 1 s 8,908,426; 2 s 10,640,549 / 133.95/s; 3 s 11,506,468 (+60.3%) / 153.09/s; 5 s same DPS, 191.36/s; ManaRegenRecovery 150.8 -> deficit from 3 s (-2.3/s), -40.6/s at the 5 s cost cap; day-1 snapshot TotalDPS 639,063 -> 1,022,526 at 3 s (+60%)"
  config:
    - {var: multiplierChannelling, default: 0, ref: "ConfigOptions.lua:1274-1276", class: c}
    - {var: conditionChannelling, default: false, ref: "ConfigOptions.lua:1271", class: b}
  unparsed: []
model:
  proposed_kind: channel_time
  inputs:
    from_pob: ["Focused Channelling level -> rate_pct_per_s", ManaPerSecondCost, ManaRegenRecovery, "Mana pool", Time]
    from_pob_config: [multiplierChannelling]
    from_scenario: [segment_s]
  params: {dmg_cap: 60, cost_rate: 20, cost_cap: 100, step: whole_seconds, segment_s: null}
  formula: "bonus(t) = min(rate*floor(t), 60) (continuous reading: min(rate*t, 60)); avg_bonus = (1/L)*integral_0^L bonus(t) dt (lvl 20, L=10 s: whole 49.2%, continuous 52.5%); feed: two PoB runs at floor_t and floor_t+1 interpolated by avg_bonus, floored; simple fallback multiplierChannelling = floor(avg_bonus/rate); cost_avg: same integral with 20%/s cap 100; mana_margin = ManaRegenRecovery - ManaPerSecondCost*(1+cost_avg); deficit judged by duration (pool / deficit). Example (Worb, L=10): about +49% vs 0 s, mana -11.9/s"
  calibration: "no norm found for channel length per scenario"
providers:
  - {kind: support, name: "Focused Channelling (support)", slot: any, role: scales, target: self, text: "Supported Skills deal more Damage per second Channelled up to 60%; lvl 1 = 9%, lvl 20 = 24%, lvl 21 = 25%/s; cost 20% more per second, cap 100%; requires Channel + Spell; no totem/trap/mine", source: "PoB Data/Skills/sup_int.lua:2538-2600; wiki (added 3.26.0)", pob: config}
  - {kind: gem, name: "Winter Orb", slot: any, role: enables, target: self, text: "channelled spell; stages (max 8, +2 at Q20), 25% chance to Freeze (3.29.0); channelling and idle parts, 80% more fire speed while channelling", source: "PoB Data/Skills/act_int.lua:20963-21050; wiki Winter Orb", pob: full}
  - {kind: support, name: "Infused Channelling (support)", slot: any, role: scales, target: self, text: "lvl 20: 29% more damage, 12% less damage taken while channelling (Channel gate)", source: "PoB Data/Skills/sup_int.lua:3880", pob: full}
  - {kind: support, name: "Cast while Channelling (support)", slot: any, role: applies, target: self, text: "triggers a linked non-channelled spell every cast_while_channelling_time_ms; triggered spell 20% less damage; triggered spells do not gain Focused Channelling's damage or cost", source: "PoB Data/Skills/sup_int.lua:678, 747; CalcTriggers.lua:226-383; wiki Focused Channelling", pob: full}
  - {kind: mastery, name: "Caster mastery 33089", slot: tree, role: applies, target: self, text: "Power Charge each second while Channelling a Spell (Worb has it)", source: "PoB TreeData/3_29/tree.lua:31305", pob: partial}
  - {kind: notable, name: "Arcane Adept 15990", slot: tree, role: applies, target: self, text: "5% speed, 20% damage, Arcane Surge after Channelling 1 s", source: "PoB TreeData/3_29/tree.lua:86324", pob: partial}
  - {kind: notable, name: "Vital Focus 54382", slot: tree, role: scales, target: self, text: "+30% damage for channelling skills", source: "PoB TreeData/3_29/tree.lua:86253", pob: full}
  - {kind: notable, name: "Precise Focus 55714", slot: tree, role: scales, target: self, text: "critical strike chance for channelling skills", source: "PoB TreeData/3_29/tree.lua:86293", pob: full}
  - {kind: notable, name: "Unrestrained Focus 45935", slot: tree, role: scales, target: self, text: "8% Attack and Cast Speed, unaffected by Chill", source: "PoB TreeData/3_29/tree.lua:86263", pob: full}
  - {kind: ascendancy, name: "Unhallowed Rite 5502 (Occultist)", slot: tree, role: applies, target: self, text: "Gain Spirit Infusion every 0.5 s while Channelling a Spell", source: "PoB TreeData/3_29/tree.lua:44528", pob: partial}
makes_redundant: []
conflicts:
  - {with: "Cast On Critical Strike, Trigger and Unleash supports", effect: "channelling skills cannot be triggered, repeated, exerted or supported by Unleash (Winter Orb cannot be the CoC-triggered spell)", source: "wiki Channelling rev 1647943; PoB sup_dex.lua:519-527"}
  - {with: "stun, freeze, silence on the player", effect: "ends the channel (freeze even when action speed is not lowered to 0%)", source: "wiki Channelling rev 1647943"}
conditions:
  - {text: "ticks at cast time / cast speed and action speed; instant skills (Frostblink) do not interrupt; cooldown starts when the channel is released", source: "wiki Channelling rev 1647943; PoB act_int.lua:20963-20975"}
  - {text: "Pathfinder Master Distiller 6038 applies only to non-channelling skills (not a block)", source: "PoB TreeData/3_29/tree.lua:83740"}
uptime:
  Mapping:       {value: partial, config: {multiplierChannelling: 0.5}, reasoning: "user 2026-10-25: 0.5 s channels in maps. PoB rounds channel time down to whole seconds (ModStore.lua:403, per the modeler), so 0.5 s gives Focused Channelling +0% in PoB; whether the game grows per whole second stays not_verified", source: "build-strategist.md; mechanics-modeler.md"}
  Pinnacle Boss: {value: model, config: {multiplierChannelling: 3}, reasoning: "user 2026-10-25: 3 s on a boss = the 60% cap at L20 (+60% damage) but cost +60% too, mana deficit from 3 s; stuns/freezes on the player break the channel", source: "headless probe 2026-10-24; vault Scenarios/Pinnacle Boss.md; wiki Channelling rev 1647943"}
seeds: [Worb]
sources:
  - {ref: "https://www.poewiki.net/wiki/Channelling (rev 1647943)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Focused_Channelling_Support", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/ConfigOptions.lua:1271-1276; Classes/ModStore.lua:403; Data/Skills/sup_int.lua:2538-2600; Modules/CalcActiveSkill.lua:645-655", kind: pob, patch: "3.29"}
  - {ref: "user answers U1-U6, tasks/027-interaction-database.md log", kind: user, patch: "3.29"}
not_verified:
  - "whether Focused Channelling grows per whole second or continuously in game (PoB floors to whole seconds)"
  - "whether its timer resets on Winter Orb stage decay or re-channel"
  - "whether a Winter Orb stage is gained per channel tick (wiki silent; Worb would reach 11 stages in about 1.05 s if yes)"
  - "Winter Orb stage time to 8 stages in seconds (depends on cast speed); stage decay after release (no wiki section)"
  - "mana pool key name in the probe (not read); whether Worb.xml itself sets multiplierChannelling (PlayerStat read not done)"
open_questions: []
```
