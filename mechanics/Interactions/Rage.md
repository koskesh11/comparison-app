---
type: interaction
status: draft
pob_refs: [multiplierRage, Condition:CanGainRage, Multiplier:RageStack, MaximumRage, MinimumRage, RageRegen, Rage, RageEffect, Multiplier:RageEffect, Condition:HaveMaximumRage, InherentRageLossDelay]
source: "user decision 2026-10-26 (task 027, decision 9); PoB 2.67.2 Modules/ConfigOptions.lua:1073, Modules/CalcPerform.lua:914-932; wiki Rage rev 1700756; lane 5a evidence tasks/reports/027-evidence/b5a-taa-jb.md:101"
last_confirmed_patch: "3.29.x"
---

Rage is a player resource (base maximum 30, PoB tooltip at ConfigOptions.lua:1073) that inherently grants 1% more Attack Damage per Rage and feeds every 'per Rage' line (Berserker's Crave the Slaughter and Rite of Ruin, Rage Mastery). PoB models no Rage gain and no Rage decay: the stack count is the hand-set config box 'Rage:' (var multiplierRage), capped at MaximumRage (CalcPerform.lua:915-918). The box is visible only with the flag Condition:CanGainRage (ifFlag at ConfigOptions.lua:1073), which Rage-on-Hit lines set.
Lane 5a finding (task 027, sample 3.26/VFoS Berserker.xml, single-enemy model): with multiplierRage unset (default 0) Rage and RageEffect are 0 and both Rage notables (Crave the Slaughter, Rite of Ruin) change TotalDPS by 0.00% in None and Pinnacle; the saved value 49 (capped at 47) is worth +83% of the main skill's TotalDPS over the unset box (b5a-taa-jb.md:101). So every Rage node is 0% until the box is set.
Rule, DECIDED by the user (2026-10-26): with a reliable Rage source, set PoB's Rage to half of maximum Rage, rounded down (example: Rage on Hit and 40 maximum Rage -> 20; the Berserker sample's 47 -> 23). Without a reliable source leave the box at 0. The half value replaces a Rage gain/decay model (none is built). Details per ascendancy: [[Berserker ascendancy]].

Pipeline: [[Damage calculation#More and less]] - Rage's inherent more Attack Damage per RageEffect (CalcPerform.lua:924-928); [[Damage calculation#Hit rate]] - attack speed per Rage (Crave the Slaughter); [[Receiving damage#Recovery]] - Rite of Ruin's life loss per Rage.

```interaction
id: rage
mechanic: "Rage: player resource (base maximum 30) granting 1% more Attack Damage per Rage (times Rage effect) and feeding 'per Rage' lines; PoB takes the stack count from the hand-set box multiplierRage, capped at MaximumRage, and models no gain or decay. User rule 2026-10-26: with a reliable Rage source set the box to half of maximum Rage, rounded down"
family: resource
target: self
related: [ascendancy-berserker, warcries, chance-on-hit-uptime, fight-length, damage-calculation, recovery]
pipeline_step: ["Damage calculation#More and less", "Damage calculation#Hit rate", "Receiving damage#Recovery"]
pipeline_why: "RageEffect becomes a Damage MORE mod on attacks (or spells with RageSpellDamage), attack speed per Rage is a hit-rate term, and Rite of Ruin's loss per Rage acts in recovery"
pob:
  measured: config
  how: "ConfigOptions.lua:1073 defines multiplierRage (type count, label 'Rage:', ifFlag Condition:CanGainRage) and applies Multiplier:RageStack BASE val. CalcPerform.lua:914-932 runs when Condition:CanGainRage is set or RageRegen is above 0: maxStacks = floor(MaximumRage BASE x MORE), stacks = max(min(config, maxStacks), MinimumRage), RageEffect = floor(stacks x RageEffect mod), Damage MORE RageEffect on attacks (spells with Condition:RageSpellDamage), Condition:HaveMaximumRage only when stacks == maxStacks. Lane 5a measured the gate on 3.26/VFoS Berserker.xml: box unset = Rage 0, RageEffect 0, Crave and Rite 0.00% (None and Pinnacle); box 49 capped at 47 = RageEffect 70 with Rite of Ruin (b5a-taa-jb.md:101). The half-of-maximum value (23 in that sample) was not run headless."
  config:
    - {var: multiplierRage, default: 0, ref: "Modules/ConfigOptions.lua:1073 (type count; visible only with ifFlag Condition:CanGainRage; user rule 2026-10-26: floor(MaximumRage / 2) with a reliable Rage source, else 0)", class: c}
  unparsed:
    - "Rage gain timing: 'Only one Hit every 0.5 seconds can cause you to gain Rage' (tree.lua reminder 14641) - no PoB model, only the hand-set count"
    - "Rage decay: inherent loss after the loss delay (PoB shows InherentRageLossDelay only as an output, CalcPerform.lua:932) - no PoB model"
model: null
providers:
  - {kind: node, name: "Rage on Attack Hit nodes (Berserker sample: 23038 Slaughter, 34590 and 48199 Rage on Hit, smalls 42861 and 63583)", slot: tree, role: enables, target: self, text: "'Gain 1 Rage on Attack Hit' (smalls); they set Condition:CanGainRage, which makes the Rage box visible and lets CalcPerform build Rage; the reliable source the user rule asks for when the main skill is an attack that keeps hitting", source: "tasks/reports/027-evidence/b5a-taa-jb.md:101 (bers2.json 'ragesrc'); Modules/ConfigOptions.lua:1073; Modules/CalcPerform.lua:914", pob: config}
  - {kind: node, name: "Battle Trance 24716 and Rage Mastery 9471 (Berserker sample)", slot: tree, role: scales, target: self, text: "raise maximum Rage: 30 base + 10 + 7 = 47 in the sample; the user rule then gives floor(47 / 2) = 23", source: "vault Berserker ascendancy (Rage gate paragraph); b5a-taa-jb.md section 3", pob: full}
  - {kind: ascendancy, name: "Crave the Slaughter 24528 / Rite of Ruin 57560 (Berserker)", slot: tree, role: scales, target: self, text: "1% increased Attack Speed per Rage; 50% increased Rage Effect and 0.1% of Life lost per second per Rage. 0.00% until multiplierRage is set (lane 5a)", source: "vault Berserker ascendancy; b5a-taa-jb.md:101", pob: config}
conflicts:
  - {with: "'at maximum Rage' lines", effect: "at half of maximum Condition:HaveMaximumRage is false (set only when stacks == maxStacks, CalcPerform.lua:929-931), so the rule turns every 'while at maximum Rage' line off; a build that relies on such a line needs the user's call", source: "Modules/CalcPerform.lua:929-931"}
  - {with: "MinimumRage sources", effect: "PoB uses max(config, MinimumRage), so a minimum above half of maximum overrides the rule's value", source: "Modules/CalcPerform.lua:916-918"}
conditions:
  - {text: "the rule applies only with a reliable Rage source; PoB shows the box only when Condition:CanGainRage is set (RageRegen alone also builds Rage in CalcPerform but does not show the box)", source: "Modules/ConfigOptions.lua:1073; Modules/CalcPerform.lua:914"}
  - {text: "half of maximum is rounded down, like PoE (user preference); example from the user: Rage on Hit with 40 maximum Rage gives 20", source: "user decision 2026-10-26 (027-overnight-summary.md, USER ANSWERS item 9)"}
uptime:
  Mapping:       {value: pob, config: {multiplierRage: "floor(MaximumRage / 2) with a reliable Rage source, else 0 (user rule 2026-10-26)"}, reasoning: "PoB has no Rage gain or decay; the user's half-of-maximum value stands in for the average stack count, so no uptime model is built", source: "user decision 2026-10-26; Modules/ConfigOptions.lua:1073"}
  Pinnacle Boss: {value: pob, config: {multiplierRage: "floor(MaximumRage / 2) with a reliable Rage source, else 0 (user rule 2026-10-26)"}, reasoning: "same value; untargetable phases (Rage decays after the loss delay) are covered by the half value, not modelled separately", source: "user decision 2026-10-26; wiki Rage rev 1700756"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Rage (rev 1700756)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/ConfigOptions.lua:1073; Modules/CalcPerform.lua:914-932", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b5a-taa-jb.md:101 and section 3 (lane 5a, Rage gate on 3.26/VFoS Berserker.xml)", kind: discovery, patch: "3.29"}
  - {ref: "tasks/reports/027-overnight-summary.md, USER ANSWERS (2026-10-26) item 9", kind: discovery, patch: "3.29"}
not_verified:
  - "the DPS at the half value (23 in the Berserker sample) was not run headless; only 0 and the saved 49 (capped 47) are measured"
  - "which Rage sources count as reliable beyond Rage on Attack Hit with an attack main skill that keeps hitting (warcry, kill or spell-based sources) is not decided"
  - "whether half of maximum matches the real average stack count in a fight (no gain/decay model; the user's rule replaces it)"
open_questions: []
```
