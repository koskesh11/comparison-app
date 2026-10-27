---
type: interaction
status: draft
pob_refs: [TriggerRateCap, SkillTriggerRate, EffectiveSourceRate, CooldownRecovery, storedUses, ignoresTickRate, ServerTickRate, triggerRateCapOverride]
source: "poewiki Cooldown rev 1677532, Trigger rev 1702121 (fetched 2026-10-26); PoB 2.67.2 CalcTriggers.lua / CalcOffence.lua / Modules/Data.lua / Data/Skills/sup_dex.lua; headless runs on CoC EK Assa.xml and FR CoC Occu Three Dragons v4.xml (scratchpad b3/acc_run.py, acc_cdr.py, acc_whatif.py)"
last_confirmed_patch: "3.29.x"
---

Every trigger has two limits: the rate at which the source fires (here the attack rate x hit chance x crit chance) and a cap from the cooldown. The cooldown is divided by the cooldown recovery rate and then rounded UP to whole 33 ms server frames, so the cap moves in steps, not smoothly. A source faster than the cap loses procs; a source slower than the cap makes extra cooldown recovery worth nothing. The breakpoint table for Cast On Critical Strike is in [[CoC trigger]]; this note holds the mechanism PoB uses and the two seed measurements.

Pipeline: [[Damage calculation#Hit rate]] - the triggered spell's hits per second are SkillTriggerRate (the cap and the source rate decide it), so this acts on the rate, not on damage per hit; the source's crit and hit chance come from [[Damage calculation#Critical strike]] and [[Accuracy and hit chance]]

```interaction
id: trigger-rate-cap
mechanic: "Triggered skill rate = min(source rate x hit chance x crit chance, 1 / (cooldown / cooldown recovery rounded up to 33 ms frames)); skills that store more than one use skip the rounding; the triggered spell's cooldown, not the trigger gem's, is what counts"
family: trigger
pipeline_step: ["Damage calculation#Hit rate"]
pipeline_why: "the cap and the source rate set how many times per second the triggered spell lands (hit rate); more attack speed above the cap, or more cooldown recovery between breakpoints, adds nothing"
target: self
related: [coc-trigger, accuracy-hit-chance, channelling, cast-when-damage-taken, fight-length]
pob:
  measured: full
  how: "CalcTriggers.lua: cooldown per skill = (base + added) / calcLib.mod(CooldownRecovery) (580-581); rounding ceil(x * ServerTickRate) / ServerTickRate with ServerTickRate = 1/0.033 (582-583; Modules/Data.lua:237-238); action cooldown = max(trigger, triggered) (586); TriggerRateCap = 1 / that (588-591), or triggerRateCapOverride. EffectiveSourceRate = trigRate = HitSpeed or Speed of the fastest source skill in the group (75-87, 720), halved when dual wielding (446-450). SkillTriggerRate: (a) skills with storedUses > 1 or flagged ignoresTickRate use min(cap, source rate x overlaps), no tick rounding (456, 797-803); (b) globalTrigger skills use the source rate (811-812); (c) everything else, including CoC, goes through calcMultiSpellRotationImpact, a 1000-attack simulation with the cooldown started at the floor of the tick and ended at the next tick (91-134, 813-). The trigger chance fed to the simulation = source HitChance x source CritChance (736-782). A skill's own cooldown outside triggers: CalcOffence.lua:296-308 (storedUses > 1 skips the rounding too). PoB does not model: downtime of the source (movement, stray hits), boss immunity phases, rounding of the source attack time to server frames (unverified)."
  config: []
  unparsed: []
model: null
providers:
  - {kind: support, name: "Cast On Critical Strike", slot: any, role: enables, target: self, text: "cooldown 0.15 s, storedUses 1 (levels 1-20: 'cooldown = 0.15 ... storedUses = 1'); cast_linked_spells_on_attack_crit_% = 100", source: "Data/Skills/sup_dex.lua:537 (stat), 610-612 (level rows); CalcTriggers.lua:1156-1159", pob: full}
  - {kind: ascendancy, name: "Like Clockwork (Forbidden pair granted passive 51462)", slot: tree, role: scales, target: self, text: "+50% increased Cooldown Recovery Rate; measured on the EK Ethereal Knives modList as Tree:51462 = 50", source: "headless acc_cdr.py (EK); TreeData/3_29/tree.lua:84689-84698; detail in [[CoC trigger]]", pob: full}
  - {kind: jewel, name: "Hypnotic Eye abyss jewel (cooldown recovery roll)", slot: jewel, role: scales, target: self, text: "+3% increased Cooldown Recovery Rate each: EK Grim Iridescence (item 24); FR Foul Stare (item 29) and Enthralling Arbiter (item 30)", source: "headless acc_cdr.py: modList sources Item:24, Item:29, Item:30 value 3", pob: full}
  - {kind: mod, name: "Viper Road, Warlock Boots (cooldown recovery roll)", slot: boots, role: scales, target: self, text: "+9% increased Cooldown Recovery Rate on the FR boots (item 11)", source: "headless acc_cdr.py: modList source Item:11 value 9", pob: full}
  - {kind: gem, name: "Cyclone (trigger attack)", slot: gem, role: enables, target: self, text: "the source rate: EK Speed 8.9208/s, FR Speed 7.524/s; CritChance 100 and HitChance 100 in both", source: "headless acc_run.py; CalcTriggers.lua:75-87", pob: full}
makes_redundant:
  - {provider: "Cooldown recovery rate above the next breakpoint", when: "the source rate is already below the cap", why: "EK sits 13% below its cap (8.92 vs 10.10), so more cooldown recovery adds no damage; only more attack speed helps until the cap", source: "headless acc_run.py; CalcTriggers.lua:588-591"}
conflicts:
  - {with: "Skills storing more than one use (Doom Blast, Shockwave, ...)", effect: "no 33 ms breakpoints: they recover faster with each % of cooldown recovery; PoB sets ignoresTickRate", source: "wiki Cooldown rev 1677532 (Server frames); CalcTriggers.lua:456, CalcOffence.lua:300-303"}
  - {with: "Hit chance below 100%", effect: "the source's hit chance multiplies in once directly (HitChance) and once inside CritChance (crit chance x AccuracyHitChance), so a source hit chance h lowers the trigger factor to h x h (symbolic; no seed number is claimed); matches the wiki's second accuracy roll at the crit. DISPUTED (user, 2026-10-26): the earlier 46% -> 21% example came from a PoB in-memory removal of the crafted 'Hits can't be Evaded' (acc_whatif.py), not a game fact", source: "CalcTriggers.lua:739-781; CalcOffence.lua:3146; wiki Accuracy rev 1612031"}
conditions:
  - {text: "the cap uses the longest of trigger cooldown and triggered-skill cooldown, each divided by cooldown recovery BEFORE the tick rounding; identical triggered spells share one cooldown", source: "CalcTriggers.lua:580-586; wiki Trigger rev 1702121"}
  - {text: "wiki: cooldowns recover only at the start of a 33.0 ms server frame; 0.150 s is effectively 0.165 s (5 frames), 14% increased cooldown recovery reaches 4 frames", source: "wiki Cooldown rev 1677532 (Server frames)"}
  - {text: "wiki: cooldown applies per triggered skill, not per trigger gem (changed 2.4.0)", source: "wiki Trigger rev 1702121 (version history)"}
uptime:
  Mapping:       {value: pob, config: {}, reasoning: "use PoB's SkillTriggerRate; measured EK 8.9297/s of 8.9208 source rate (cap 10.10), FR 7.524 of 7.524 (cap 7.5758). Continuous attacking is assumed by PoB, mapping movement lowers it in game (no norm found for the fraction)", source: "headless acc_run.py; CalcTriggers.lua:797-822"}
  Pinnacle Boss: {value: pob, config: {}, reasoning: "same PoB number; the triggers stop while the boss is untargetable (no attack, no crit); fraction depends on the fight, see [[Fight length]]", source: "headless acc_run.py"}
seeds: [EK, FR]
sources:
  - {ref: "PoB Modules/CalcTriggers.lua, CalcOffence.lua, Modules/Data.lua, Data/Skills/sup_dex.lua (2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Cooldown (rev 1677532)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Trigger (rev 1702121)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Accuracy (rev 1612031)", kind: wiki, patch: "3.29"}
not_verified:
  - "EK: SkillTriggerRate 8.9297 is 0.10% above the source rate 8.9208 (ratio 1.0010); probable cause is a 1001st trigger inside the 1000-attack simulation (CalcTriggers.lua:99-123), not checked"
  - "FR: source 7.524/s is 0.69% below the cap 7.5758/s; what PoB shows just above the cap was not run (expected: the simulated rate falls toward the cap)"
  - "Accuracy and crit confirm: the vault takes the wiki Accuracy page for the second accuracy roll at the crit; the in-game order of the two rolls for triggers was not checked"
  - "Whether the 0.15 s cooldown is per triggered spell or per gem for CoC at 3.29 (wiki 2.4.0 history says per triggered skill; PoB reads it from the support row)"
  - "The 33 ms rounding of the source's own attack time is not in PoB (CalcOffence attack time is not tick-rounded in the lines read); whether the game rounds it was not checked"
open_questions:
  - "None for the user."
```
