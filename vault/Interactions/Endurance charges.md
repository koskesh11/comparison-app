---
type: interaction
status: draft
pob_refs: [useEnduranceCharges, overrideEnduranceCharges, EnduranceChargesMax, EnduranceChargesMin, EnduranceCharges, EnduranceChargesDuration, HaveMaximumEnduranceCharges, PhysicalDamageReduction, ElementalDamageReduction]
source: "wiki Endurance charge rev 1697434, Charge rev 1700592, Fortification rev 1698776; PoB 2.67.2 ConfigOptions.lua, CalcPerform.lua, CalcSetup.lua, CalcDefence.lua, ModParser.lua, Data/Misc.lua, Data/ModCache.lua, TreeData/3_29/tree.lua, Data/Uniques; mechanics-researcher-uptime.md, pob-coverage-auditor-calc-order.md (task 027)"
last_confirmed_patch: "3.29.x"
---

Endurance charges give 4% additional physical and 4% additional elemental damage reduction per charge (since 3.25.0 the elemental part is damage reduction, no longer resistance). PoB counts them only when useEnduranceCharges is ticked (max charges, or the override) or when an item says "count as having maximum"; gaining them on kill, block, hit or crit is not parsed. Same pattern as [[Power charges]] and [[Frenzy charges]]; they feed [[Fortify]] (Replica Badge) and [[Onslaught]] (Ahn's Heritage, Daresso's Defiance).

Pipeline: [[Receiving damage#Armour and damage reduction]] - the charge bonus is extra damage reduction added to the armour reduction on the same hit, then capped at 90% in [[Defences#Physical damage reduction cap]]; it is worth most against many small hits and nothing against damage over time.

```interaction
id: endurance-charges
mechanic: "Endurance charges: 4% additional Physical and 4% additional Elemental Damage Reduction per charge (max 3 by default, 10 s, every gain resets all charges of the type); PoB uses max charges only if useEnduranceCharges is ticked, charge gain is not modelled"
family: charge
target: self
related: [power-charges, frenzy-charges, fortify, onslaught, chance-on-hit-uptime]
pipeline_step: ["Receiving damage#Armour and damage reduction", "Defences#Physical damage reduction cap"]
pipeline_why: "Per-charge damage reduction adds to the armour reduction after shifts and resistances and before damage-taken modifiers; the sum is clamped to 90 (wiki Damage reduction rev 1605942, PoB CalcDefence.lua:1538). It does not act on DoT."
pob:
  measured: config
  how: "Config: ConfigOptions.lua:912-917 -> CalcPerform.lua:1070-1071 (count = override or EnduranceChargesMax), 'count as maximum' flag HaveMaximumEnduranceCharges CalcPerform.lua:1112-1113, min charges 1000/1082, max 1001, duration 1002 (floor of base x charge-duration mods), base max 3 CalcSetup.lua:34 / Data/Misc.lua:94. Effect: CalcSetup.lua:617-618 adds PhysicalDamageReduction / ElementalDamageReduction BASE 4 per charge (Data/Misc.lua:75-76), summed and capped at CalcDefence.lua:1538. Gain on kill, block, hit, crit, stun returns no mods (ModCache.lua:3719-3723, 6369, 16279, 16283, 22877). Minions: minionsUseEnduranceCharges (ConfigOptions.lua:982-992). Charges lost/stolen by enemies are not modelled"
  config:
    - {var: useEnduranceCharges, default: false, ref: "Modules/ConfigOptions.lua:912-914", class: b}
    - {var: overrideEnduranceCharges, default: max, ref: "Modules/ConfigOptions.lua:915-917", class: c}
  unparsed:
    - "10% chance to gain an Endurance Charge on Kill (generic): ModCache.lua:3719 returns nil"
    - "Bringer of Rain: 20% chance to gain an Endurance Charge when you Block: ModCache.lua:6369"
    - "Ambu's Charge: Gain an Endurance Charge when you take a Critical Strike: ModCache.lua:16283"
    - "Replica Ambu's Charge: Gain an Endurance Charge when you are Hit: ModCache.lua:16279"
    - "Daresso's Defiance: You gain an Endurance Charge on Kill / lose all when Hit: ModCache.lua:22877, 22947"
    - "Unflinching (Juggernaut): 30% chance to gain an Endurance Charge when you are Hit, Gain 1 per second if you've been Hit Recently (tree.lua:15360-15362)"
model:
  proposed_kind: on_event_charge_uptime
  inputs: {from_pob: [EnduranceChargesMax, EnduranceChargesDuration], from_scenario: ["event rate per second on you or on the target (kills/s, hits taken/s E, blocks/s, hits dealt/s V)", "chance p of the provider"]}
  params: {duration_s_default: 10}
  formula: "u(at least 1 charge) = 1-(1-p)^(R*d), R = events/s, d = EnduranceChargesDuration; every gain resets ALL charges (wiki Charge rev 1700592), so the bonus is full (max stacks) only after max gains inside d; skill hits give at most 1 charge per skill use, so for 'on Hit' use uses/s, not hits/s. On-hit chance providers: set uptime value model and use [[Chance on hit uptime]]. 'Count as maximum' and minimum charges: u = 1 (no model)"
  calibration: "no norm found; wiki gives the 10 s duration and the reset-all rule, no kill rate or hit rate for maps or bosses"
providers:
  - {kind: unique, name: "Ralakesh's Impatience (Endurance Current)", slot: boots, role: enables, target: self, text: "Count as having maximum number of Endurance Charges (counts, does not generate)", source: "Data/Uniques/boots.lua:921-933; Modules/ModParser.lua:5268", pob: full, variant: "Endurance Current (variant 3)"}
  - {kind: unique, name: "Replica Badge of the Brotherhood", slot: amulet, role: scales, target: self, text: "Your Maximum Endurance Charges is equal to your Maximum Frenzy Charges; +1 to maximum Fortification per Endurance Charge; (20-25)% chance to lose an Endurance Charge when you gain Fortification", source: "Data/Uniques/amulet.lua:231-235; Modules/ModParser.lua:4164; ModCache.lua:251", pob: full}
  - {kind: unique, name: "Grand Spectrum (Crimson)", slot: jewel, role: enables, target: self, text: "+1 to Minimum Endurance Charges per Grand Spectrum (min charges are always present; limited to 3)", source: "Data/Uniques/jewel.lua:229-242 (variant 5); ModCache.lua:240", pob: full, variant: "Current - Min Endurance Charge"}
  - {kind: ascendancy, name: "Unflinching 1734 (Juggernaut)", slot: tree, role: applies, target: self, text: "30% chance to gain an Endurance Charge when you are Hit; 25% chance that you instead gain up to maximum; Gain 1 Endurance Charge every second if you've been Hit Recently; +1 to Maximum Endurance Charges", source: "TreeData/3_29/tree.lua:15353-15363", pob: partial}
  - {kind: ascendancy, name: "Unrelenting 56789 (Juggernaut)", slot: tree, role: scales, target: self, text: "1% additional Elemental Damage Reduction and 1% additional Physical Damage Reduction per Endurance Charge", source: "TreeData/3_29/tree.lua:15379-15387; ModCache.lua:3368, 3370", pob: full}
  - {kind: ascendancy, name: "Conviction of Power 25651 (Hierophant)", slot: tree, role: enables, target: self, text: "+4 to Minimum Endurance Charges, +4 to Minimum Power Charges, +1 to Maximum Power and Endurance Charges", source: "TreeData/3_29/tree.lua:15676-15685; ModCache.lua:1982", pob: full}
  - {kind: notable, name: "Disciple of the Unyielding 64882 (cluster)", slot: tree, role: applies, target: self, text: "+1 to Minimum Endurance Charges; 8% chance to gain an Endurance Charge on Kill; 8% increased Damage per Endurance Charge", source: "TreeData/3_29/tree.lua:52760-52773; ModCache.lua:11523", pob: partial}
  - {kind: unique, name: "The Bringer of Rain", slot: helmet, role: applies, target: self, text: "20% chance to gain an Endurance Charge when you Block (current variants 3-5); Can't use Chest armour", source: "Data/Uniques/helmet.lua:895-920; ModCache.lua:6369", pob: none, variant: "variants 3,4,5"}
  - {kind: unique, name: "Ambu's Charge", slot: body, role: applies, target: self, text: "Gain an Endurance Charge when you take a Critical Strike (current variant 5: gain up to maximum); share charges with nearby party members", source: "Data/Uniques/body.lua:924-943; ModCache.lua:16283", pob: none}
  - {kind: unique, name: "Replica Ambu's Charge", slot: body, role: applies, target: self, text: "Gain an Endurance Charge when you are Hit; Lose 2% of Life per second if you have been Hit Recently", source: "Data/Uniques/body.lua:945-955; ModCache.lua:16279", pob: none}
  - {kind: unique, name: "Daresso's Defiance", slot: body, role: applies, target: self, text: "You gain an Endurance Charge on Kill; you lose all Endurance Charges when Hit; Onslaught for 5 seconds per Endurance Charge when Hit (current variants)", source: "Data/Uniques/body.lua:819-840; ModCache.lua:22878, 22947", pob: partial}
  - {kind: unique, name: "Ahn's Heritage", slot: shield, role: blocks, target: self, text: "-1 to Maximum Endurance Charges; You have Onslaught while at maximum Endurance Charges", source: "Data/Uniques/shield.lua:6-20; ModCache.lua:22913", pob: full}
makes_redundant:
  - {provider: "kill/block/hit-based endurance charge generation", when: "Ralakesh's Impatience (Endurance Current) worn or Grand Spectrum / Conviction of Power minimum charges", why: "'count as maximum' and minimum charges make the charges always present, so PoB's max-charge assumption becomes true without a gain source", source: "Data/Uniques/boots.lua:933; Data/Uniques/jewel.lua:242; TreeData/3_29/tree.lua:15683"}
conflicts:
  - {with: "Replica Badge of the Brotherhood", effect: "(20-25)% chance to lose an Endurance Charge each time you gain Fortification, so charges and Fortification drain each other", source: "Data/Uniques/amulet.lua:235"}
  - {with: "Daresso's Defiance", effect: "all Endurance Charges are lost when Hit, so the damage reduction is gone exactly when a hit lands; the Onslaught per charge is the payoff", source: "Data/Uniques/body.lua:834"}
conditions:
  - {text: "every gain resets the 10 s timer of ALL charges of that type, even at maximum; gaining at the limit adds no charge", source: "wiki Charge rev 1700592: 'If the character would gain a charge while already at the limit for that type of charge, no additional charge will be gained. However, the duration of all charges of that type will still be reset.'"}
  - {text: "hits grant at most 1 charge of each type per skill use (channelling skills while channelling, reservation skills, brands, orbs and some named skills are exceptions)", source: "wiki Charge rev 1700592"}
  - {text: "since 3.25.0 each charge gives 4% additional Elemental Damage Reduction, not 4% to all Elemental Resistances", source: "wiki Endurance charge rev 1697434 version history 3.25.0"}
  - {text: "the same damage-reduction layer is capped at 90 (physical) and Overwhelm subtracts afterwards", source: "wiki Damage reduction rev 1605942 via vault Defences#Physical damage reduction cap"}
  - {text: "wiki: damage-taken 'less' modifiers (Fortification) are calculated after armour, resistances and endurance charges", source: "wiki Fortification rev 1698776"}
uptime:
  Mapping:       {value: model, config: {useEnduranceCharges: "true when a gain source or 'count as max' exists; kill/block/hit chance sources: model u = 1-(1-p)^(R*10)", overrideEnduranceCharges: "leave at max only if u >= 0.99, else blend two PoB runs"}, reasoning: "kill rate in maps is high but not measured here; 'count as max' and minimum charges are always (u = 1). Chance providers use [[Chance on hit uptime]] (hits dealt per skill use, 1 charge per use)", source: "wiki Charge rev 1700592; mechanics-researcher-uptime.md table row 'Endurance / Frenzy / Power charge on hit'; Data/Uniques/boots.lua:933"}
  Pinnacle Boss: {value: model, config: {useEnduranceCharges: "true for 'count as max', minimum charges, or when-hit / on-crit-taken sources via E = 1000/enemySpeed (class b assumption); kill-based sources = none (no kills on a lone boss)"}, reasoning: "boss hits on you drive when-hit and crit-taken sources; no pinnacle hit-rate source found, so every when-hit uptime stays an assumption", source: "Modules/ConfigOptions.lua:2318-2320, 2362; mechanics-researcher-uptime.md section 'How often does a pinnacle boss hit the player per second'"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Endurance_charge (rev 1697434)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Charge (rev 1700592)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Fortification (rev 1698776)", kind: wiki, patch: "3.29"}
  - {ref: "wiki cargo generic_stats (name Character): elemental_damage_reduction_%_per_endurance_charge 4, physical_damage_reduction_%_per_endurance_charge 4, max_endurance_charges 3 (queried 2026-10-25)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/ConfigOptions.lua:912-917, CalcPerform.lua:1001-1002, 1070-1071, 1112-1113, CalcSetup.lua:34, 617-618, CalcDefence.lua:1538, ModParser.lua:5268, Data/Misc.lua:75-76, 94", kind: pob, patch: "3.29"}
  - {ref: "PoB TreeData/3_29/tree.lua:15353-15387, 15676-15685, 52760-52773; Data/Uniques/{boots,amulet,jewel,helmet,body,shield}.lua", kind: pob, patch: "3.29"}
not_verified:
  - "wiki Endurance charge page lists the player bonus through a cargo query; the query result (4% / 4% / +3) was read via the cargo API, the rendered page text itself carries no numbers"
  - "whether ModCache entries with leftover text (for example ModCache.lua:7223 for the Unflinching text, value 25 on EnduranceChargesMax) are applied by PoB; not run"
  - "Replica Badge of the Brotherhood and Ahn's Heritage current-league obtainability (not checked)"
  - "kill rate in maps and hit rate of a pinnacle boss on the player (no source)"
  - "Monster-side charges (15% additional physical DR and +15% elemental resistances per charge, wiki) are not configurable in PoB as far as read; not traced"
  - "Ralakesh's effect on minimum charges (no source mentions it)"
open_questions:
  - "Should the generator treat 'count as maximum' / minimum-charge providers as always on for both scenarios and ignore chance-based gain? (suggested yes)"
```
