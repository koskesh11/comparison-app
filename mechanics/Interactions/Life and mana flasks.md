---
type: interaction
status: draft
pob_refs: [LifeRecovery, LifeRegenRecovery, ManaRecovery, TotalEHP, BleedAvoidChance, FlaskInstantRecovery, LifeFlaskInstantRecovery, ManaFlaskInstantRecovery, LifeFlaskEffectNotRemoved, UsingFlask, UsingLifeFlask, UsingManaFlask, conditionUsingFlask]
source: "PoB 2.67.2 CalcPerform.lua:1638-1658, 1673-1676, 1776-1789, 3121; CalcDefence.lua:1311-1313, 2952; Item.lua:2419-2455; ModParser.lua:5089, 5185-5199; ConfigOptions.lua:1098; headless EK measurements (b1c-pob-flasks.md section c, section a)"
last_confirmed_patch: "3.29.x"
---

What PoB counts from life and mana flasks. For an ordinary life flask PoB shows the recovery only in the item tooltip, not in any build output: the recovery enters LifeRecovery and LifeRegenRecovery only when the flask effect is "not removed" at full life (a flag from a tree or item line), and TotalEHP does not use flask recovery at all (it comes from the hit-pool simulation). A flask that recovers 100% instantly does not set the UsingFlask condition, so "during flask effect" bonuses do not fire for it. EK (CoC Ethereal Knives, CI, Life 1): its Eternal Life flask is worth 0 EHP and 0 recovery in PoB; the only counted effect is its bleed and corrupted blood immunity, which PoB counts as always on. Related: [[Defensive utility flasks]], [[Offensive utility flasks]], [[Flask uptime]], [[Recovery]], [[Bleed, poison and corrupted blood immunity]].

Pipeline: [[Receiving damage#Recovery]] and [[Defences#Recovery and leech]] - flask recovery is a recovery source over time, outside the hit pool (not part of TotalEHP).

```interaction
id: life-mana-flasks
mechanic: "A life or mana flask recovers its amount over its duration (or instantly with instant recovery); PoB computes the per-second figure into LifeRecovery / ManaRecovery only if the effect is not removed at full life or mana, shows the amount otherwise only in the tooltip, and never in TotalEHP or max hit. UsingFlask is set for an active flask unless its instant recovery is 100%"
family: resource
pipeline_step: ["Receiving damage#Recovery", "Defences#Recovery and leech"]
pipeline_why: "flask recovery is regeneration-like recovery over time, applied after the hit pool; PoB adds it to LifeRegenRecovery only when the effect is not removed"
target: self
related: [recovery, flask-uptime, defensive-utility-flasks, offensive-utility-flasks, bleed-poison-cb-immunity]
pob:
  measured: partial
  how: "Item data (Item.lua:2419-2455): flaskData.lifeBase = base life x (1 + quality/100) x recovery mod, instantPerc, duration (rate-adjusted), lifeTotal, lifeAdditional, lifeEffectNotRemoved / manaEffectNotRemoved. calcFlaskRecovery returns EMPTY unless flaskData.lifeEffectNotRemoved or the mod LifeFlaskEffectNotRemoved is set (CalcPerform.lua:1652-1658; ModParser.lua:5185-5199 parses 'Life flask effects are not removed when unreserved life is filled' and the mana equivalents); the second mergeFlasks pass (CalcPerform.lua:3121) adds that per-second recovery to the modDB, which CalcDefence.lua:1311-1313 sums into LifeRecovery and LifeRegenRecovery. Instant recovery: getFlaskInstantRecovery (CalcPerform.lua:1638-1650) = base instant% + low-life instant + LifeFlaskInstantRecovery / ManaFlaskInstantRecovery, capped at 100; only active flasks with instantPerc below 100 set UsingFlask (CalcPerform.lua:1776-1778). Conditions set per active flask: UsingFlask, Using<BaseNameNoSpaces> (e.g. UsingEternalLifeFlask, CalcPerform.lua:1779), UsingLifeFlask (unless CannotRecoverLifeOutsideLeech, :1785), UsingManaFlask (:1789); Have<BaseName> from CalcSetup.lua:1029. TotalEHP is the hit-pool simulation (CalcDefence.lua:2952), so flask recovery is not in EHP or max hit (stated from code). EK measured (Life 1, ES 5,189, CI): Eternal Life (2,080 base, 2,496 at quality 20 over 1.2 s, 64% increased Recovery rate) gives LifeRecovery 0 with the flask on and off and TotalEHP unchanged; only BleedImmune / CorruptedBloodImmune count (BleedAvoidChance 0 to 100); UsingFlask, UsingLifeFlask, UsingEternalLifeFlask true, UsingManaFlask absent. PoB leaves out the tooltip-only amount in builds, the real firing of reactive suffixes, and several effects of life and mana flasks (see unparsed)."
  config:
    - {var: conditionUsingFlask, default: false, ref: "Modules/ConfigOptions.lua:1098", class: b}
    - {var: "flask slot active checkbox (Items tab)", default: false, ref: "Modules/CalcSetup.lua:1028-1031", class: c}
  unparsed:
    - "flask suffix: Grants N% of Life Recovery to Minions (unparsed)"
    - "flask suffix: Gain N Charges when you are Hit by an Enemy (unparsed)"
    - "flask suffix: Removes Curses on use / Removes Burning on use (unparsed)"
    - "flask suffix: Mana Recovery occurs instantly at the end of Effect (unparsed)"
    - "flask suffix: Effect does not Queue (unparsed)"
    - "Eternal Life (EK Flask 2): immunity to Bleeding / Corrupted Blood 'if used while Bleeding' parses to the always-on flags BleedImmune / CorruptedBloodImmune; the reactive 'Used when you start Bleeding' enchant has no PoB line"
model: null
providers:
  - {kind: flask, name: "Eternal Life Flask (EK Flask 2, Condensed ... of Sealing)", slot: flask, role: sustains, target: self, text: "life 2,080 base (2,496 at quality 20), 1.2 s duration, uses 15 of 45 charges; 64% increased Recovery rate; immunity to Bleeding / Corrupted Blood if used while. EK (CI): 0 recovery and 0 EHP, bleed immunity only", source: "b1c-pob-flasks.md (a), (c) (probe_tip.py); Item.lua:2419-2455", pob: partial}
  - {kind: mod, name: "Life / Mana flask effects are not removed when unreserved life / mana is filled", slot: any, role: enables, target: self, text: "makes the flask effect last at full life or mana; this is what lets PoB count the recovery into LifeRecovery and ManaRecovery (flaskData.lifeEffectNotRemoved / LifeFlaskEffectNotRemoved)", source: "Modules/ModParser.lua:5185-5199; Modules/CalcPerform.lua:1652-1658", pob: full}
  - {kind: mod, name: "Instant recovery on life / mana flasks", slot: any, role: scales, target: self, text: "LifeFlaskInstantRecovery / ManaFlaskInstantRecovery plus base and low-life instant percent, capped at 100; at 100 the flask does not set UsingFlask", source: "Modules/CalcPerform.lua:1638-1650, 1776-1778", pob: full}
  - {kind: mod, name: "Recover an additional N% of the flask's life recovery over 10 s if not on full life", slot: any, role: scales, target: self, text: "parsed", source: "Modules/ModParser.lua:5089", pob: full}
  - {kind: mod, name: "Low-life more recovery and Life Flask charge multipliers", slot: any, role: scales, target: self, text: "low-life 'more recovery' for life flasks; LifeFlaskCharges / LifeFlaskRecovery multipliers", source: "Modules/CalcPerform.lua:1673-1676; Modules/CalcSetup.lua:937, 1039-1041", pob: full}
makes_redundant:
  - {provider: "Eternal Life bleed immunity", when: "another permanent bleed or corrupted blood immunity source is on (the flask's own recovery is worth 0 on CI)", why: "PoB counts the reactive 'if used while Bleeding' suffix as always on, so it adds nothing once BleedAvoidChance is already 100", source: "b1c-pob-flasks.md (a); vault Bleed, poison and corrupted blood immunity"}
conflicts:
  - {with: "Chaos Inoculation (Life 1)", effect: "life flask recovery of 2,496 life over 1.2 s is worth nothing: LifeRecovery 0, TotalEHP unchanged", source: "b1c-pob-flasks.md (a)"}
conditions:
  - {text: "conditionUsingFlask (ConfigOptions.lua:1098) is a check box, default false, 'automatically enabled if you have a flask active': the config only forces it; UsingFlask is set for every active flask with instantPerc below 100", source: "Modules/ConfigOptions.lua:1098; Modules/CalcPerform.lua:1776-1778"}
  - {text: "a flask with 100% instant recovery does NOT set UsingFlask, so 'during flask effect' bonuses do not trigger for it", source: "Modules/CalcPerform.lua:1776-1778"}
  - {text: "the reactive 'if used while Bleeding / Poisoned / Frozen / Chilled / Shocked / Ignited' suffixes are fired in the game by the Instilling flask enchants ('Used when you ...'); PoB has no parser line for them and counts the suffix as always on", source: "Data/EnchantmentFlask.lua:20-25; Main.lua:120; b1c-item-flasks.md"}
uptime:
  Mapping:
    value: pob
    config: {"flask slot active": true}
    reasoning: "use PoB's flask tooltip uptime; a life flask has no uptime line unless its effect is not removed (hasUptime false, ItemsTab.lua:4831-4837); see Flask uptime for the model"
    source: "Classes/ItemsTab.lua:4830-4857; vault Flask uptime"
  Pinnacle Boss:
    value: pob
    config: {"flask slot active": true}
    reasoning: "same: PoB's number as the floor; Surgeon's crit charges are not counted by PoB; flask recovery is not in the hit pool, so it does not change the max hit"
    source: "Classes/ItemsTab.lua:4830-4857; Modules/CalcDefence.lua:2952; vault Flask uptime"
seeds: [EK]
sources:
  - {ref: "Modules/CalcPerform.lua:1638-1658,1673-1676,1776-1789,3121; Modules/CalcDefence.lua:1311-1313,2952; Item.lua:2419-2455; Modules/ModParser.lua:5089,5185-5199; Modules/ConfigOptions.lua:1098 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b1c-pob-flasks.md (sections a, c); b1c-item-flasks.md", kind: discovery, patch: "3.29"}
not_verified:
  - "life-flask EHP or regeneration effect on a non-CI build: code reading only, no life-build run (EK is CI, Life 1)"
  - "wiki rules for life and mana flasks (instant recovery, effect removal at full life) were not read for this note"
  - "mana flask recovery: no mana-flask build was measured (UsingManaFlask absent on EK)"
  - "Item.lua:2419-2455 is cited by b1c-pob-flasks.md without its folder; not re-checked"
open_questions: []
```
