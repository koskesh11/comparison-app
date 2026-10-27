---
type: interaction
status: draft
pob_refs: [usePowerCharges, overridePowerCharges, PowerChargesMax, PowerChargesMin, PowerCharges, PowerChargesDuration, ChargeDuration, SupportPowerChargeOnCritical]
source: "PoB 2.67.2 ConfigOptions.lua / ConfigTab.lua / CalcPerform.lua / CalcSetup.lua / Data/Skills/act_int.lua; poewiki Charge rev 1700592, Power charge rev 1697266, Assassin's Mark rev 1681632, Unstable Infusion rev 1580147, Forbidden Power (Ascendancy) rev 1539109, Disciple of the Forbidden rev 1347313 (fetched 2026-10-26); headless runs on CoC EK Assa.xml and FR CoC Occu Three Dragons v4.xml (scratchpad b3b/pc_src.py, pc_whatif.py, pc_whatif2.py, pc_cost.py); item-analyst, skill-gem-analyst, tree-ascendancy-analyst (task 027); tasks/reports/021-gate1.md N9"
last_confirmed_patch: "3.29.x"
---

Power charges count in PoB only when usePowerCharges is ticked, and then PoB assumes the MAXIMUM (7 in both CoC seeds) at all times; charge gain (on kill, on crit, on hit, per mana spent) is not parsed, and the charge duration is only displayed. Max charges (PowerChargesMax) come from tree and items and feed other mechanics, e.g. [[Curse limit]] with Anathema, and [[Frenzy charges]] with Badge of the Brotherhood. Measured: the tick is worth 2.6x FullDPS in EK (5.73M to 15.14M) and 2.2x in FR (26.0M to 57.0M) compared with the one minimum charge; at 5 charges the seeds lose 10% (EK) and 14% (FR), at 4 charges 25% and 24%. Whether a single boss keeps the charges up therefore decides how much of the number is real: in EK Unstable Infusion (crit and hit based) refills all 7 within about 4 s of hitting the boss, in FR only the Assassin's Mark quality (5% per hit) works on a boss and it needs about 16 s.

Pipeline: [[Damage calculation#Critical strike]] - power charges raise crit chance, so they act in the critical strike step; PoB counts them only from a config tick and does not model charge gain

```interaction
id: power-charges
mechanic: "Power charges (crit chance / spell damage scaling per charge); PoB counts max charges only when usePowerCharges is ticked, gain is not modelled"
family: charge
pipeline_step: ["Damage calculation#Critical strike"]
pipeline_why: "power charges raise crit chance, so they act in the critical strike step; PoB counts them only from a config tick and does not model charge gain"
target: self
related: [frenzy-charges, curse-limit, arcane-surge, assassins-mark]
pob:
  measured: config
  how: "ConfigOptions.lua:900-905 -> CalcPerform.lua:986-988 (Min, Max, Duration), 1043-1057 (PowerCharges = override or Max when UsePowerCharges, then floored at Min), 1117 (Multiplier PowerCharge). Gain on kill/crit/hit/mana spent is unparsed (ModCache.lua:5184, 6361, 8131, 16217 give nil mods); only 'Power Charge On Critical' gem name recognised (ModParser.lua:2034). Duration is output only (CalcPerform.lua:988, shown at CalcSections.lua:1860, no DPS use; base 10 s CalcSetup.lua:31). Minions: minionsUsePowerCharges (ConfigOptions.lua:976-990). The override cannot be set to 0: type count ignores 0 (ConfigTab.lua:1144-1145), so '0 charges' is not reachable; usePowerCharges off gives PowerChargesMin (1 in both seeds from Disciple of the Forbidden). usePowerCharges is ticked in both seed files (EK XML line 966, FR XML line 349)."
  config:
    - {var: usePowerCharges, default: false, ref: "ConfigOptions.lua:900-905", class: b}
    - {var: overridePowerCharges, default: max, ref: "ConfigOptions.lua:900-905; zero ignored ConfigTab.lua:1145", class: c}
  unparsed:
    - "Anathema: (10-20)% chance to gain a Power Charge when you Cast a Curse Spell"
    - "Tulborn/Tulfall: Gain a Power Charge on Killing a Frozen Enemy"
    - "10% chance to gain a Power Charge on Kill (generic)"
    - "Unstable Infusion (EK): 15% chance to gain a Power Charge on Critical Strike / 30% on Non-Critical Strike (ModCache.lua:5184, 8131 nil); its +1 maximum on the same node IS counted (Tree:4242 in PowerChargesMax)"
    - "Disciple of the Forbidden (both seeds): 8% chance to gain a Power Charge on Kill (the +1 minimum is counted: PowerChargesMin Tree:9261)"
    - "Forbidden Power (FR): Gain a Power Charge after Spending a total of 200 Mana (ModCache.lua:16217 nil)"
    - "Mage Hunter (FR): 20% chance to gain a Power Charge when you Block (ModCache.lua:6361 nil)"
    - "Inner Conviction (EK, FR): Gain Power Charges instead of Frenzy Charges (ModCache.lua:16163 nil); its '3% more Spell Damage per Power Charge' IS counted (ModCache.lua:8049)"
    - "Assassin's Mark: 100% charge when the marked enemy dies and (quality) chance per hit on it - constantStats chance_to_grant_power_charge_on_death_% and quality grant_attacker_power_charge_when_hit_%_chance have no statMap entry (Data/Skills/act_int.lua:988-1018)"
model:
  proposed_kind: power_charge_ramp
  inputs:
    from_pob: ["Speed of the hit source (Cyclone attack rate: EK 8.921/s, FR 7.524/s)", "per-charge CritChance of the source (EK 69.18/77.13/85.08/93.02/100 at 1..5 charges; FR 80.76 at 1, 100 at 5)", "PowerChargesMax 7 and PowerChargesMin 1", "PowerChargesDuration (EK 21 s, FR 11 s; floor of 10 x (1 + INC))"]
    from_scenario: ["boss is hit continuously by the source skill", "fight length (not set here)"]
  params: {EK_unstable_infusion_crit: 0.15, EK_unstable_infusion_noncrit: 0.30, FR_mark_quality_per_hit: 0.05, charge_duration_resets_on_every_gain: true}
  formula: "rate(n) = hits_per_s x (p_crit x crit(n) + p_non x (1 - crit(n))); expected time from the minimum charge to k charges = sum over n=1..k-1 of 1 / rate(n); all charges expire together if no gain for the duration D (gain at maximum also refreshes), chance per gap = exp(-rate x D)"
  calibration: "LOWER BOUND, labelled: counts only Cyclone hits (one hit per attack, each hit rolling separately - wiki Charge rev 1700592 lists channelling skills that hit while channelling, e.g. Cyclone, as an exception to one charge per skill use); triggered Ethereal Knives / Forbidden Rite hits are not counted. Result: EK reaches 5 charges after 2.5 s and 7 after 4.0 s (rate 1.34 to 1.75 per s, gap-reset chance 6e-13); FR reaches 5 charges after 10.6 s and 7 after 15.9 s (rate 0.376 per s, reset chance 1.6% per gap). No community norm found."
providers:
  - {kind: unique, name: "Grand Spectrum (Cobalt)", slot: jewel, role: enables, target: self, text: "+1 to Minimum Power Charges per Grand Spectrum (variant 5); 25% inc crit chance per Grand Spectrum (variant 3); count + colours pinned, 3 needed. The FR seed carries the Frenzy-minimum, crit and Endurance-minimum variants (XML lines 770, 844, 906), not the Power-minimum one", source: "PoB Data/Uniques/jewel.lua:225-226; Item.lua:2466, ModParser.lua:1463; 021-gate1 N9", pob: full}
  - {kind: unique, name: "Badge of the Brotherhood", slot: amulet, role: scales, target: self, text: "Max Frenzy = Max Power, so each +max power charge also raises Frenzy (EK seed: FrenzyChargesMax 7 measured)", source: "PoB Data/Uniques/amulet.lua:217; headless pc_src_EK.json", pob: full}
  - {kind: unique, name: "Anathema", slot: ring, role: applies, target: self, text: "(10-20)% chance to gain a Power Charge when you Cast a Curse Spell; curse limit = max power charges (FR seed, 10%). Works on a boss only when curses are cast during the fight (not verified how often; a Mark On Hit trigger counting as a cast is unverified)", source: "PoB Data/Uniques/ring.lua:646-647; FR XML line 487", pob: none}
  - {kind: support, name: "Power Charge On Critical", slot: any, role: applies, target: self, text: "54% (L20) chance per crit; 4% more damage per power charge; the only support that gives charges from a spell like Winter Orb", source: "PoB sup_int.lua:5593-5636, statMap 5604-5606", pob: partial}
  - {kind: mastery, name: "Caster Mastery effect 33089", slot: tree, role: applies, target: self, text: "Gain a Power Charge each second while Channelling a Spell (Worb node 14113)", source: "tree-ascendancy-analyst; TREE L31305", pob: none}
  - {kind: unique, name: "Ralakesh's Impatience (Power Current)", slot: boots, role: enables, target: self, text: "Count as having maximum number of Power Charges", source: "PoB Data/Uniques/boots.lua:935 (variant 5)", pob: full, variant: "Power Current"}
  - {kind: ascendancy, name: "Unstable Infusion 4242 (Assassin)", slot: tree, role: applies, target: self, text: "15% on crit, 30% on non-crit, on hit (wiki 3.27.0 values); +1 Maximum Power Charges. EK seed: works on a single boss, no kill needed; 8.921 Cyclone hits per s give 1.34 to 1.75 charges per s (model)", source: "poewiki Unstable Infusion rev 1580147; TREE L83536; headless pc_src_EK.json (Tree:4242 in PowerChargesMax)", pob: partial}
  - {kind: notable, name: "Forbidden Power 62504 (Occultist)", slot: tree, role: scales, target: self, text: "+1 Max, 6% inc Damage and AoE per charge, one charge per 200 mana spent, at most one charge per skill use (FR seed). FR Cyclone costs ES not mana in PoB (ESCost 6, ManaCost 0), so the mana trigger is probably idle - unverified", source: "poewiki Forbidden Power (Ascendancy passive skill) rev 1539109; TREE L44271; headless pc_cost_FR.json", pob: partial}
  - {kind: unique, name: "Malachai's Loop", slot: shield, role: scales, target: self, text: "+2 Max Power Charges; 20% chance on Hit; (12-16)% inc Spell Damage per charge", source: "PoB Data/Uniques/shield.lua:669-674 (variant 4)", pob: partial}
  - {kind: unique, name: "Voll's Protector", slot: body, role: applies, target: self, text: "Gain a Power Charge for each Enemy you hit with a Critical Strike; 50% reduced max mana", source: "PoB Data/Uniques/body.lua:1154-1155", pob: none}
  - {kind: unique, name: "Skyforth", slot: boots, role: applies, target: self, text: "25% chance to gain a Power Charge on Critical Strike; no Life Regeneration", source: "PoB Data/Uniques/boots.lua:608-610", pob: none}
  - {kind: unique, name: "Tulborn / Tulfall", slot: wand, role: applies, target: self, text: "Gain a Power Charge on Killing a Frozen Enemy (Foulborn Tulborn removes it)", source: "PoB Data/Uniques/wand.lua:392-395, 413; Foulborn jsonc:617", pob: none, payoff_of: [conditionEnemyFrozen]}
  - {kind: gem, name: "Assassin's Mark (quality and kill grant)", slot: any, role: applies, target: self, text: "marked enemy grants a power charge when it dies (100%, awarded to the killer, so useless on a boss) and, per 4% gem quality, 1% chance per hit on it (wiki 3.12.0). FR seed: quality 20 = 5% per hit, 7.524 Cyclone hits per s = 0.376 charges per s. EK seed: quality 0 = no per-hit chance. Mark itself is owned by the Assassin's Mark note", source: "PoB Data/Skills/act_int.lua:1013, 1017 (qualityStats 0.25 per 1%, constantStats 100); poewiki Assassin's Mark rev 1681632; build XML EK line 135 (level 30, quality 0), FR line 255 (level 21, quality 20)", pob: none}
  - {kind: notable, name: "Disciple of the Forbidden 9261", slot: tree, role: enables, target: self, text: "+1 Minimum Power Charges (counted: PowerChargesMin 1 in both seeds), 8% chance to gain a Power Charge on Kill (map clear only, not a boss), 8% inc Damage per charge", source: "poewiki Disciple of the Forbidden rev 1347313; headless pc_src_EK/FR.json (minsrc Tree:9261)", pob: partial}
  - {kind: notable, name: "Infused 25411 / Overcharge 34173 / Instability 20528", slot: tree, role: enables, target: self, text: "+1 Maximum Power Charges each; with the base 3 plus Unstable Infusion (EK) or Forbidden Power (FR) this is the 7 the tick assumes", source: "headless pc_src_EK/FR.json maxsrc (Tree:25411, 34173, 20528 plus 4242 or 62504)", pob: full}
  - {kind: notable, name: "Mage Hunter 65898", slot: tree, role: applies, target: self, text: "20% chance to gain a Power Charge when you Block (FR seed); boss attack and block rate not known", source: "headless pc_nodes_FR.json (node text); ModCache.lua:6361", pob: none}
  - {kind: keystone, name: "Inner Conviction", slot: tree, role: scales, target: self, text: "3% more Spell Damage per Power Charge (counted) and Gain Power Charges instead of Frenzy Charges (not parsed). Both seeds allocate it; it adds a damage term per charge that makes the charge count matter beyond crit", source: "headless pc_nodes_EK/FR.json; ModCache.lua:8049, 16163", pob: partial}
makes_redundant:
  - {provider: "kill-based power charge generation", when: "Ralakesh Power Current worn or Grand Spectrum minimum charges", why: "'counts as maximum' / minimum charges make the charges always present for DPS", source: "boots.lua:935; jewel.lua:226"}
  - {provider: "hit-based charge generation (Unstable Infusion, Assassin's Mark quality)", when: "the usePowerCharges tick is already assumed", why: "PoB already counts the maximum; these only decide whether the maximum is real on a boss", source: "CalcPerform.lua:1046-1048"}
conflicts:
  - {with: "Rashkaldor's Patience variant 1", effect: "'Cannot gain Power Charges' line exists in variant 1 only, not in Current", source: "item-analyst; PoB amulet.lua:939-943"}
conditions:
  - {text: "Anathema reads PowerChargesMax, not the current count, so it works without the config tick", source: "CalcPerform.lua:3216-3218"}
  - {text: "Power Charge On Critical charges still count only if usePowerCharges is ticked", source: "pob-coverage-auditor (ModParser.lua:2034)"}
  - {text: "Charge duration is 10 s base; gaining a charge (also at the maximum) resets the duration of ALL charges of that type; minimum charges stay. PoB: EK 21 s (Charge Mastery +100% and 12850 +15%), FR 11 s (6728 +15%), display only", source: "poewiki Charge rev 1700592, Power charge rev 1697266; CalcPerform.lua:988; CalcSetup.lua:31; headless pc_src_EK/FR.json"}
  - {text: "Most skills grant at most one charge of a type per skill use; channelling skills that hit while channelling (Cyclone), brands, orb skills are exceptions", source: "poewiki Charge rev 1700592"}
  - {text: "Zero charges cannot be tested: overridePowerCharges = 0 is ignored (the run returns the 7-charge numbers); the real floor is PowerChargesMin = 1", source: "ConfigTab.lua:1145; headless pc_whatif.py ov0 = base"}
  - {text: "Measured loss when the 7 charges are overstated (Mark kept, Pinnacle default): EK FullDPS 15.14M at 7, 14.35M at 6 (-5.2%), 13.59M at 5 (-10.2%), 11.35M at 4 (-25.0%), 9.20M at 3, 7.33M at 2, 5.73M at 1 (-62.2%); EK Cyclone crit 100 down to 93.0 at 4 and 69.2 at 1. FR FullDPS 57.00M at 7, 53.79M at 6 (-5.6%), 48.81M at 5 (-14.4%), 43.33M at 4 (-24.0%), 31.05M at 2, 26.00M at 1 (-54.4%); FR crit stays 100 at 5 so the FR loss at 5 charges is damage per charge, not crit", source: "headless b3b/pc_whatif.py, pc_whatif2.py (in-memory overridePowerCharges, nothing saved); crit-only view in mechanics-researcher-crit.md"}
uptime:
  Mapping:       {value: high, config: {usePowerCharges: true}, reasoning: "Kill sources (Disciple 8% on kill, marked-enemy kill 100%) and hit sources keep charges up in maps; the duration refresh at every gain keeps all 7 while enemies die or are hit more often than every 11 s (FR) or 21 s (EK)", source: "poewiki Charge rev 1700592; build-strategist table"}
  Pinnacle Boss: {value: model, config: {usePowerCharges: "true for crit/hit-based sources (EK Unstable Infusion: about 4 s to 7 charges), partial for FR (Mark quality only, about 16 s to 7, 10.6 s to 5), 'count as max', or Power Charge On Critical with high crit; kill-based = none"}, reasoning: "Labelled lower-bound ramp model (power_charge_ramp) from sourced inputs; the fight-average depends on fight length, which is not set here. PoB's tick reports the 7-charge value from the first hit", source: "headless pc_whatif.py + model block; poewiki Unstable Infusion rev 1580147, Assassin's Mark rev 1681632"}
seeds: [EK, FR, Worb]
sources:
  - {ref: "PoB ConfigOptions.lua:900-905, ConfigTab.lua:1144-1145, CalcPerform.lua:986-988, 1043-1057, 1117, CalcSections.lua:1860, CalcSetup.lua:31", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/Skills/sup_int.lua:5593, Data/Skills/act_int.lua:979-1018", kind: pob, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Charge (rev 1700592)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Power_charge (rev 1697266)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Assassin's_Mark (rev 1681632)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Unstable_Infusion (rev 1580147)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Forbidden_Power_(Ascendancy_passive_skill) (rev 1539109)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Disciple_of_the_Forbidden (rev 1347313)", kind: wiki, patch: "3.29"}
  - {ref: "tasks/reports/021-gate1.md N9", kind: discovery, patch: "3.29"}
not_verified:
  - "PoB EnableCharges config interplay (stat exists on the tree)"
  - "Whether Worb PCoC (Power Charge On Critical) charges are reflected: PoB counts them only through the config tick"
  - "Ramp model inputs not checked in game: that every Cyclone attack is exactly one hit that rolls Unstable Infusion / Mark quality separately (wiki Charge lists Cyclone as a multi-charge exception, PoB Speed is the attack rate); that hits of triggered spells (Ethereal Knives, Forbidden Rite) also roll them (the model leaves them out); that Unstable Infusion 'on hit' includes spell crits"
  - "Whether spending ES instead of mana (FR Cyclone ESCost 6, ManaCost 0 in PoB) counts toward Forbidden Power's 200 mana; whether a Mark On Hit-triggered or other automatic curse counts as 'Cast a Curse Spell' for Anathema; Mage Hunter block rate on a boss"
  - "Fight length of a Pinnacle boss and breaks in hitting (phases, untargetable) longer than the charge duration, which would drop the charges to the minimum"
  - "Charge duration of 21 s for EK / 11 s for FR is PoB display arithmetic (floor of 10 x (1 + INC)); not checked in game"
open_questions:
  - "Worb: is usePowerCharges to be assumed on in both scenarios because PCoC + Caster Mastery give charges on crit/channel? (suggested yes, derived from sources)"
  - "Generator: should a seed whose charges come only from kills (no hit/crit source) lower overridePowerCharges for the boss scenario? (FR is the example: only the Mark quality works on a boss)"
```
