---
type: interaction
status: draft
pob_refs: [CannotGainWarcryBuffs, Duration, WarcryPower, MinimumWarcryPower, multiplierWarcryPower, Condition:HaveCallToArms, NumAncestralExerts, UsedWarcryRecently]
source: "poewiki Call to Arms rev 1632488 (fetched 2026-10-26; 3.25.0 change); PoB 2.67.2 CalcPerform.lua, ModParser.lua, ConfigOptions.lua, Data/ModCache.lua, Data/Uniques, Data/SkillStatMap.lua, TreeData/3_29/tree.lua; headless measurements on EK, Worb, FR and the Fireball file, tasks 027 batch 3c (pob-coverage-auditor-E.md)"
last_confirmed_patch: "3.29.x"
---

Call to Arms (keystone) is the support-warcry keystone: it gives up your own warcry buff and charges for double duration so the warcries are for minions, allies and party. Tree text (TreeData/3_29/tree.lua:28882, node 23090): "Your Warcries do not grant Buffs or Charges to You / 100% more Warcry Duration". No seed has a warcry skill (checked: 0 warcry skills and 0 warcry gems on EK, Worb, FR and the Fireball file), so the measured effect is 0 everywhere. See [[Warcries]] for power, exerting and uptime; related: [[Bleed]], [[Ignite]], [[Poison]] and [[Damage over time multiplier]] do not interact.

Pipeline: [[Damage calculation#Increased and reduced]] - a warcry buff reaches the player as modDB mods through mergeBuff (CalcPerform.lua:2390-2402); the keystone skips exactly that merge, so the buff's increased/more terms never enter the damage pool; exerting, which is a separate More step ([[Warcries]]), is not touched.

Measured headless, in memory only (E_run.py, keystone force-allocated alone, 'keystone only, path cost not included'; enemy level from env.enemyLevel: 85 at None, 84 at Pinnacle): EK, Worb, FR and the Fireball file all give 0 changed output keys at both levels; the flag CannotGainWarcryBuffs is true after allocation, so the mod is active and simply has no warcry to act on.

```interaction
id: call-to-arms
mechanic: "Your warcries grant no buffs and no charges to you (allies, minions and party still get them); warcries have 100% more duration; exerting is not removed by the text"
family: buff
target: self
related: [warcries, bleed, ignite, poison, damage-over-time-multiplier]
pipeline_step: ["Damage calculation#Increased and reduced"]
pipeline_why: "PoB merges a warcry's buff into the player's modDB with mergeBuff only when CannotGainWarcryBuffs is not set (CalcPerform.lua:2390-2402), so the buff's increased/more terms and the 'AffectedBy<warcry>' conditions never exist; the buff for the minion (2404-2432) and the party export (2434-2441) is still built, scaled by uptime = min(full duration / cooldown, 1) where the 100% more Duration lifts the duration."
pob:
  measured: partial
  how: "Both lines parse: Data/ModCache.lua:23132 (CannotGainWarcryBuffs flag, ModParser.lua:4194) and 4239 (Duration MORE 100 with keyword Warcry = 4, Data/Global.lua:139); the keystone name entry is 14491 (Keystone LIST + Condition:HaveCallToArms). Consumer: CalcPerform.lua:2390 (the only reader of CannotGainWarcryBuffs). Exert counts (Num<warcry>Exerts, 2370-2376) are computed BEFORE the check, so exerting stays. Uptime = min(duration/cooldown, 1) or 1 with Condition:WarcryMaxHit (2385-2388). The 'or Charges' half has nothing to remove: Enduring Cry's endurance_charge_granted_per_X_monster_power_during_endurance_warcry has no entry in Data/SkillStatMap.lua or Modules (grep). Measured 0 changes on all four files because none has a warcry skill. NOT modelled: charges from warcries, ally buffs beyond the minion/party export, how many minions or allies stand in the area."
  config:
    - {var: multiplierWarcryPower, default: "unset; Boss, Pinnacle and Uber presets add 20", ref: "Modules/ConfigOptions.lua:743-744 (override, ifFlag UsesWarcryPower); presets 2123, 2158, 2192", class: b}
    - {var: conditionUsedWarcryRecently, default: false, ref: "Modules/ConfigOptions.lua:1569-1570 (ifFlag warcry; the keystone does not touch it)", class: c}
  unparsed: []
model: null
providers:
  - {kind: keystone, name: "Call to Arms", slot: tree, role: applies, target: self, text: "Your Warcries do not grant Buffs or Charges to You; 100% more Warcry Duration", source: "TreeData/3_29/tree.lua:28882 (node 23090); Data/ModCache.lua:14491, 23132, 4239", pob: full}
  - {kind: unique, name: "Mutewind Pennant", slot: Shield, role: applies, target: self, text: "Call to Arms (variant 4, Current); also 25% increased Warcry Buff Effect, which helps allies and minions only while Call to Arms is on", source: "Data/Uniques/shield.lua:394-412", pob: full, variant: "variant 4 (Current)"}
  - {kind: mod, name: "Warcry duration and cooldown sources", slot: any, role: scales, target: self, text: "uptime for minions and party = min(duration / cooldown, 1); the keystone's 100% more Duration doubles it", source: "Modules/CalcPerform.lua:2385-2388", pob: full}
  - {kind: mod, name: "Warcry Power (Boss presets 20, 'Warcries have a minimum of N power', 'Warcry Power' config)", slot: any, role: scales, target: self, text: "scales the minion/party buff only; the player's own buff is gone", source: "Modules/ConfigOptions.lua:743-744, 2123; Modules/ModParser.lua:5512-5513", pob: full}
  - {kind: gem, name: "any warcry skill (Rallying Cry, Seismic Cry, Ancestral Cry, General's Cry, ...)", slot: any, role: enables, target: self, text: "no seed carries one; without a warcry the keystone does nothing", source: "E_run.py (0 warcry skills on EK, Worb, FR, Fireball file)", pob: full}
makes_redundant:
  - {provider: "Warcry Buff Effect for your own buff (e.g. Mutewind Pennant 25%)", when: "Call to Arms allocated", why: "your own warcry buff is not granted, only minion/party buffs scale with it", source: "Modules/CalcPerform.lua:2390-2402"}
  - {provider: "conditional mods 'while affected by <warcry>'", when: "Call to Arms allocated", why: "PoB sets AffectedBy<warcry> on the player only inside the branch the keystone skips (CalcPerform.lua:2392-2393)", source: "Modules/CalcPerform.lua:2390-2393"}
conflicts:
  - {with: "exerting warcries (Ancestral, Seismic, Infernal, Intimidating, Rallying, Battlemage's)", effect: "wiki 3.25.0 and the tree text only remove buffs and charges, not exerting; PoB still counts Num<warcry>Exerts, so exert builds keep the exerted-attack bonus", source: "wiki Call to Arms rev 1632488; Modules/CalcPerform.lua:2370-2376"}
  - {with: "builds that rely on their own warcry buff or charges (Enduring Cry charges, Rallying Cry self buff)", effect: "they lose it, PoB shows that loss only for the buff, never for charges (not modelled)", source: "Modules/CalcPerform.lua:2390; Data/SkillStatMap.lua (no charge stat)"}
conditions:
  - {text: "version history: 3.11.0 introduced; 3.24.0 renamed Warlord's Call (no exert, buff to allies); 3.25.0 back to Call to Arms with 100% more Warcry Duration and no buffs or charges for you", source: "wiki Call to Arms rev 1632488"}
  - {text: "wiki: primarily for the supportive side of warcries toward minions, allies and party members", source: "wiki Call to Arms rev 1632488"}
uptime:
  Mapping:       {value: pob, config: {enemyIsBoss: "None / map monsters (enemy level 85 in the runs)", multiplierWarcryPower: "set by hand: no preset power for packs"}, reasoning: "permanent keystone; only matters with a warcry and minions or allies; PoB gives packs no warcry power unless set by hand", source: "Modules/ConfigOptions.lua:743-744, 2123"}
  Pinnacle Boss: {value: pob, config: {enemyIsBoss: "Pinnacle (default; enemy level 84 in the runs; warcry power 20 from the preset)"}, reasoning: "permanent keystone; the Pinnacle preset sets warcry power 20 for the minion buff", source: "Modules/ConfigOptions.lua:2158"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Call_to_Arms (rev 1632488)", kind: wiki, patch: "3.29"}
  - {ref: "PoB TreeData/3_29/tree.lua:28882; Data/ModCache.lua:4239,14491,23132; Modules/ModParser.lua:4194; Modules/CalcPerform.lua:2363-2445; Modules/ConfigOptions.lua:743-744,1569-1570,2123,2158,2192; Data/Global.lua:139; Data/Uniques/shield.lua:394-412", kind: pob, patch: "3.29"}
  - {ref: "tasks 027 batch 3c: scratchpad b3c/E/E_run.py, summary.txt (headless, nothing saved)", kind: discovery, patch: "3.29"}
not_verified:
  - "how big the keystone's effect is in PoB with a warcry and minions: no seed has a warcry skill and no warcry was added in the runs"
  - "whether the game's 'Charges' half also covers Enduring Cry charges for allies (wiki says only 'to the user')"
  - "whether exerting really stays in the game after 3.25.0 (the wiki change row lists only the removed buff/charges; the old Warlord's Call line 'no longer Exert' was removed)"
  - "Foulborn variants and the Impossible Escape jewel for this keystone: not checked"
open_questions:
  - "Does the generator ever start a build from a warcry-for-minions seed? No current seed does, so the keystone stays unmeasured"
```
