---
type: interaction
status: draft
pob_refs: [useFrenzyCharges, overrideFrenzyCharges, FrenzyChargesMax, FrenzyCharges]
source: "PoB 2.67.2 ConfigOptions.lua / CalcPerform.lua; item-analyst, skill-gem-analyst, tree-ascendancy-analyst (task 027)"
last_confirmed_patch: "3.29.x"
---

PoB counts frenzy charges only from a config tick (max charges when ticked); gaining them on kill, crit or frozen kill is not parsed. So the charge count is a scenario assumption, not a PoB result. Items that make charges "count as maximum" make the assumption true.

Pipeline: [[Damage calculation#More and less]], [[Damage calculation#Hit rate]] - each charge is 4% more damage (own multiplier) and speed (hit rate); PoB counts them only from a config tick, so the step applies only to the assumed charge count

```interaction
id: frenzy-charges
mechanic: "Frenzy charges give 4% more damage and speed per charge (PoB); PoB uses max charges only if useFrenzyCharges is ticked, charge gain is not modelled"
family: charge
pipeline_step: ["Damage calculation#More and less", "Damage calculation#Hit rate"]
pipeline_why: "each charge is 4% more damage (own multiplier) and speed (hit rate); PoB counts them only from a config tick, so the step applies only to the assumed charge count"
target: self
related: [power-charges, rampage]
pob:
  measured: config
  how: "ConfigOptions.lua:906-910 -> CalcPerform.lua:1058-1068 (count), max at 994; per-charge effect CalcSetup.lua:614-616, Misc.lua:72-74. Gain on kill/crit/frozen-kill returns no mods (red lines)"
  config:
    - {var: useFrenzyCharges, default: false, ref: "ConfigOptions.lua:906-910", class: b}
    - {var: overrideFrenzyCharges, default: max, ref: "ConfigOptions.lua:906-910", class: c}
  unparsed:
    - "Ice Bite: chance_to_gain_frenzy_charge_on_killing_frozen_enemy_% not in SkillStatMap"
    - "Touch of Anguish: 20% chance to gain a Frenzy Charge on Killing a Frozen Enemy"
    - "Terminus Est: Gain a Frenzy Charge on Critical Strike"
model: null
providers:
  - {kind: unique, name: "Ralakesh's Impatience (Frenzy Current)", slot: boots, role: enables, target: self, text: "Count as having maximum number of Frenzy Charges (counts, does not generate); pick the right Current variant", source: "PoB Data/Uniques/boots.lua:921-935", pob: full, variant: "Frenzy Current (variant 4)"}
  - {kind: unique, name: "Badge of the Brotherhood", slot: amulet, role: scales, target: self, text: "Your Maximum Frenzy Charges is equal to your Maximum Power Charges", source: "PoB Data/Uniques/amulet.lua:217; ModParser.lua:4165", pob: full}
  - {kind: unique, name: "Grand Spectrum (Viridian)", slot: jewel, role: enables, target: self, text: "+1 to Minimum Frenzy Charges per Grand Spectrum (min charges, FR seed)", source: "PoB Data/Uniques/jewel.lua:259 (variant 6); 021-gate1 N9", pob: full}
  - {kind: support, name: "Ice Bite", slot: any, role: applies, target: self, text: "69% (L20) chance to gain a Frenzy Charge on killing a frozen enemy; added cold per charge", source: "PoB sup_dex.lua:2405-2449", pob: partial, payoff_of: [conditionEnemyFrozen]}
  - {kind: unique, name: "Terminus Est", slot: weapon, role: applies, target: self, text: "Gain a Frenzy Charge on Critical Strike", source: "PoB Data/Uniques/sword.lua:1053 (variant 3)", pob: none}
  - {kind: unique, name: "Darkray Vectors", slot: boots, role: scales, target: self, text: "+1 Maximum Frenzy Charges, 40% reduced charge duration", source: "PoB Data/Uniques/boots.lua:712-716 (variant 3)", pob: full}
  - {kind: unique, name: "Sinvicta's Mettle", slot: weapon, role: applies, target: self, text: "Gain a Frenzy Charge on every 50th Rampage Kill", source: "PoB Data/Uniques/axe.lua:395-397", pob: none}
  - {kind: ascendancy, name: "Unleashed Potential (Ascendant) 19355", slot: tree, role: scales, target: self, text: "+1 each max charge, 400% charge duration, 25% charge on kill", source: "tree-ascendancy-analyst; TREE L90047", pob: partial}
  - {kind: notable, name: "Disciple of the Slaughter 58921", slot: tree, role: applies, target: self, text: "+1 Min Frenzy, 8% on Kill, 8% inc Damage per charge", source: "tree-ascendancy-analyst; TREE L52847", pob: partial}
  - {kind: mastery, name: "Charge Mastery effect 29652", slot: tree, role: sustains, target: self, text: "100% increased Charge Duration (Worb node 34723)", source: "tree-ascendancy-analyst; TREE L43486", pob: full}
  - {kind: ascendancy, name: "Ahn's Might (Reliquarian) 47058", slot: tree, role: blocks, target: self, text: "-1 Max Frenzy Charge", source: "tree-ascendancy-analyst; TREE L21039", pob: full}
makes_redundant:
  - {provider: "kill/crit-based frenzy generation", when: "Ralakesh Frenzy Current worn", why: "'counts as maximum' makes the charges always on for DPS; Badge only sets max Frenzy = max Power, Ralakesh covers one charge type", source: "build-strategist redundancy list; boots.lua:931-935"}
conflicts: []
conditions:
  - {text: "gain-on-kill sources need kills; a lone boss gives none", source: "build-strategist table"}
uptime:
  Mapping:       {value: high, config: {useFrenzyCharges: true}, reasoning: "Kills keep charges up; tick only if a gain source or 'counts as max' exists in the build", source: "build-strategist table"}
  Pinnacle Boss: {value: partial, config: {useFrenzyCharges: "true only for Ralakesh/Badge 'count as max' (always); kill-based sources = low"}, reasoning: "No kills on a lone boss; Ice Bite frozen-kill charge = none", source: "build-strategist table"}
seeds: [EK, FR]
sources:
  - {ref: "PoB ConfigOptions.lua:906-910, CalcPerform.lua:994, 1058-1068", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/Uniques/boots.lua, amulet.lua, jewel.lua", kind: pob, patch: "3.29"}
not_verified:
  - "Ralakesh's effect on minimum charges (no source mentions it)"
  - "Base charge duration 10 s (build-strategist statement, no source line)"
  - "Grand Spectrum Viridian min-frenzy effect in the FR build was not run"
open_questions:
  - "Ralakesh counts as maximum: should the generator treat charges as always on for the Boss scenario? (suggested yes)"
```
