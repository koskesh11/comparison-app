---
type: interaction
status: draft
pob_refs: [triggeredBySpellSlinger, gainPercentBaseWandDamageToSpells, Condition:SupportedBySpellslinger, TriggerRateCap, SkillTriggerRate, EffectiveSourceRate, CooldownRecovery, ManaUnreserved]
source: "PoB 2.67.2 CalcTriggers.lua:1205-1218, 563-591, 91-134; CalcOffence.lua:913-930; CalcActiveSkill.lua:526-537; Data/Skills/act_int.lua:17052-17202; ModCache.lua:6564, 7473; poewiki Spellslinger rev 1682125; headless scratch variant of CoC EK Assa.xml with a wand (task 027 batch 3)"
last_confirmed_patch: "3.29.x"
---

Spellslinger is a hybrid gem: the active part reserves mana (20% per supported spell, 3.26.0), the support part makes the linked spell trigger when you fire a projectile with a wand attack and adds 60% (L1) to 174% (L20) of the wand's damage to it as spell damage. The trigger has a 0.6 s cooldown on the spell, lowered by the gem's own cooldown recovery (0% at L1, 38% at L20, 68% at L40); the cooldown rounds up to 33 ms frames, so a wand attack that is a little too fast loses up to half the triggers. Reservation mechanics (how the 20% is summed with auras) are in the batch 4 reservation note, not here.

Pipeline: [[Damage calculation#Hit rate]], [[Damage calculation#More and less]] - the wand attack rate, capped by the 0.6 s cooldown, is the hit rate of the triggered spell (Hit rate); the gem's 30% to 13% less damage is a MORE multiplier (More and less).

```interaction
id: spellslinger
mechanic: "Wand projectile attack triggers all linked spells; 0.6 s cooldown / (1 + gem cooldown recovery 0-38% at L1-L20 + other) in 33 ms frames; spell gets 60-174% of wand damage added; supported spell deals 30-20% less damage with hits and ailments; gem reserves 20% mana per supported spell"
family: trigger
pipeline_step: ["Damage calculation#Hit rate", "Damage calculation#More and less"]
pipeline_why: "the wand attack rate is the source rate of the trigger and is capped by the 0.6 s cooldown rounded to server frames (hit rate of the triggered spell); the less damage is a MORE multiplier and the wand damage is added before increased/more"
target: self
related: [coc-trigger, trigger-rate-cap, arcanist-brand, cast-on-melee-kill, cast-while-channelling, projectile-hits-single-target]
pob:
  measured: full
  how: "handler CalcTriggers.lua:1205-1218: triggerOnUse (no hit or crit chance factor on the wand attack, :737), source = any Attack AND Projectile skill with the Wand flag that is not itself Spellslinger-triggered, in ANY socket group (no slotMatch, :1209-1213); sourceRateIsFinal; cooldown = 0.6 / ICDR rounded to 33 ms (:563-591), rate through the rotation simulation (:91-134, :814). Wand damage: CalcOffence.lua:913-930 adds gainPercentBaseWandDamageToSpells % of the wand weaponData (average of both wands if two wands). Quality: +1% wand damage per 1% (act_int.lua:17145). Headless EK scratch variant (CoC removed, wand from the build's own Weapon 1 Swap item, Power Siphon L20 q20 as the wand attack, Spellslinger L20 q20, Ethereal Knives): EffectiveSourceRate 3.654 (Power Siphon rate), icdr 91 = 53 + 38 from the gem, TriggerRateCap 3.0303 (= 1 / 0.33 s), SkillTriggerRate 1.827 = exactly half of the attack rate (cooldown 0.33 s is longer than the 0.2737 s attack interval, so every second attack triggers). ManaUnreserved went from 107 (CoC variant) to -269 (reservation exceeds mana). Only the trigger fields are valid evidence: the variant swaps the weapon so Cyclone is disabled ('No usable weapon equipped')"
  config: []
  unparsed: []
model: null
providers:
  - {kind: gem, name: "Spellslinger (active part)", slot: any, role: enables, target: self, text: "Spell, Instant, HasReservation, Cooldown skill with castTime 0; mana reservation of the supported spells is shown but not an own PoB stat (spellslinger_mana_reservation is 'Display only'); cooldown 0.6, storedUses 1 on every level", source: "Data/Skills/act_int.lua:17052-17112 (statMap :17061-17063)", pob: full}
  - {kind: support, name: "Spellslinger (support part)", slot: any, role: scales, target: self, text: "requires Triggerable AND Spell; adds Triggered, HasReservation, Cooldown; excludes Trapped, RemoteMined, SummonsTotem, HasReservation, already Triggered, InbuiltTrigger; supportGemsOnly; levels: wand damage as added spell damage 60 / 174 / 264 %, cooldown recovery 0 / 38 / 68 %, less damage -30 / -20 / -13 % (L1 / L20 / L40); manaReservationPercent 20 on every level", source: "Data/Skills/act_int.lua:17114-17202 (L1 :17161, L20 :17180, L40 :17200)", pob: full}
  - {kind: support, name: "Spellslinger (reservation efficiency lines)", slot: any, role: scales, target: self, text: "'20% / 25% increased Mana Reservation Efficiency of Skills Supported by Spellslinger' parse to a ManaReservationEfficiency INC with Condition SupportedBySpellslinger", source: "Data/ModCache.lua:6564, 7473; Modules/ModParser.lua:1307, 1597", pob: full}
  - {kind: gem, name: "Power Siphon (wand projectile attack)", slot: gem, role: enables, target: self, text: "an Attack with Projectile that uses a wand: the usual Spellslinger source; any wand projectile attack counts", source: "PoB gem data; headless variant: 'Spellslinger's Trigger: Power Siphon'", pob: full}
makes_redundant: []
conflicts:
  - {with: "any other trigger support on the same spell (CoC, CoMK, CwC, CwDT, Arcanist Brand)", effect: "PoB disables the spell: 'This skill is supported by more than one trigger'", source: "Modules/CalcActiveSkill.lua:531-537"}
  - {with: "spells that reserve mana, totem, trap and mine spells, or spells already triggered", effect: "cannot be supported", source: "Data/Skills/act_int.lua:17119-17121 (requires / excludes)"}
  - {with: "a main hand that is not a wand (for example the dagger / sword of the EK and FR seeds)", effect: "no trigger source: the handler needs the Wand flag, and the wand attack must also be a projectile; the seeds' Cyclone is a melee attack", source: "CalcTriggers.lua:1209-1213; headless variant (Cyclone disabled without a usable weapon)"}
conditions:
  - {text: "trigger fires when a wand PROJECTILE attack is used, it does not need to hit, kill or crit; attacks triggered by other items do not count", source: "CalcTriggers.lua:1209-1213; wiki Spellslinger rev 1682125 'Non-Triggered Wand Attack'"}
  - {text: "all linked spells trigger on one wand shot; the 0.6 s cooldown is shared between instances of the same spell and is only added to spells that have a smaller cooldown", source: "wiki Spellslinger rev 1682125; PoB rotation :91-134"}
  - {text: "the cooldown breakpoints (33 ms frames) mean the wand attack should stay at or below the cap rate: with 91% total cooldown recovery the cap is 3.03/s and a 3.65/s wand attack gives 1.83/s", source: "headless variant; wiki Spellslinger rev 1682125 'Real Cooldown & Cooldown Threshold'"}
uptime:
  Mapping:       {value: pob, config: {}, reasoning: "Rate comes from the wand attack and the capped cooldown; use PoB's SkillTriggerRate. Real uptime is the share of time the wand attack is used (the wand attack is the main attack, so it is movement-limited, not kill-limited)", source: "CalcTriggers.lua:1205-1218, 814"}
  Pinnacle Boss: {value: pob, config: {}, reasoning: "Same: no kill or hit requirement, so only the boss phases (no attacking) reduce it. PoB's number", source: "CalcTriggers.lua:1205-1218"}
seeds: []
sources:
  - {ref: "PoB Modules/CalcTriggers.lua, CalcOffence.lua, CalcActiveSkill.lua, Data/Skills/act_int.lua, Data/ModCache.lua (2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Spellslinger (rev 1682125; 3.26.0 reservation 20%, 3.27.0 less damage 30-20%)", kind: wiki, patch: "3.29"}
not_verified:
  - "Reservation mechanics: how PoB sums the 20% per supported spell into the reserved mana (CalcActiveSkill.lua:526-528 sets skillData.manaReservationPercent) is left to the batch 4 reservation note"
  - "Whether the dual-wield /2 branch (CalcTriggers.lua:449-452) halves the Spellslinger rate with two wands (it needs sourceWeaponTrigger or an item-granted support; not run with two wands)"
  - "How much of the 3.65/s attack the real game loses at the 33 ms frame boundary beyond PoB's rotation simulation (the simulation agrees with the wiki 'up to almost half' text)"
  - "Wand base damage vs total weapon damage: PoB reads weaponData (local mods included); the wiki says 'Damage of Equipped Wand'"
open_questions:
  - "Is a wand/Spellslinger build wanted as a seed, or is it only a comparison against CoC on EK/FR (their weapons are not wands)?"
```
