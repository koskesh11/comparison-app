---
type: interaction
status: draft
pob_refs: [InstantLifeLeech, LifeLeechInstantProportion, LifeLeechInstant, LifeLeechRate, CannotRecoverLifeOutsideLeech, NoLifeRegen, LifeRegen, LifeRegenRecovery, EnergyShieldRegen, ZealotsOath, LifeOnKill, enemyIsBoss]
source: "poewiki Vaal Pact rev 1647702 (fetched 2026-10-26; rework 3.25.0, text equals tree.lua); PoB 2.67.2 CalcDefence.lua / CalcOffence.lua / CalcPerform.lua / ModParser.lua / Global.lua / Data/ModCache.lua / TreeData 3_29; headless runs on EK, FR and the Fireball seed (scratchpad b3c/F_run.py, evidence b3c/tree-ascendancy-analyst-F.md)"
last_confirmed_patch: "3.29.x"
---

Vaal Pact (keystone, node 10808, TreeData/3_29/tree.lua:60121-60125) since 3.25.0 says "Life Leech from Melee Damage is Instant" and "Cannot Recover Life other than from Leech" (the old doubled leech rate and doubled leech cap are gone). Melee attacks leech life at once, so the leech cannot be spread over time or capped by the leech rate; everything else that recovers life stops: regeneration, flasks, life on hit and kill, life on block and suppress. Non-melee leech (spells, projectiles) still works but stays non-instant. On the two CI seeds (EK, FR) it is a no-op for the pool - Life is 1 - and on the Fireball seed it only removes recovery. The one number that moves a real seed is PoB's loss of Zealot's Oath ES regeneration on FR (2250.6 -> 115 per second), which the wiki says the keystone does not remove. Related: [[Leech]] (leech mechanics), [[Defences]] (recovery and leech), [[Receiving damage]], [[Chaos Inoculation]], [[Energy shield recovery keystones]] (Zealot's Oath).

Pipeline: [[Receiving damage#Recovery]] - Vaal Pact acts on the recovery step, not on the incoming hit: it turns melee life leech into an instant gain (the part that is instant is added to the rate without the max-leech cap, CalcOffence.lua:4124-4125) and removes the other life recovery channels. PoB's TotalEHP ignores recovery (see that section), so the EHP and max-hit outputs do not move.

How PoB applies it: two lines. "Life Leech from Melee Damage is Instant" is InstantLifeLeech BASE 100 with mod flags 256 = ModFlag.Melee (Data/ModCache.lua:17369, Modules/ModParser.lua:3179, Data/Global.lua:110); CalcOffence.lua:3730 turns it into LifeLeechInstantProportion for skills whose cfg carries the Melee flag. "Cannot Recover Life other than from Leech" is two flags, CannotRecoverLifeOutsideLeech and NoLifeRegen (Data/ModCache.lua:14558, Modules/ModParser.lua:4790-4794). Consumers: LifeRecoveryRateMod stays 1 (CalcDefence.lua:1213), life on block and suppress are 0 (CalcDefence.lua:1564-1568), ES recharge no longer applies to life (CalcDefence.lua:1343), life on hit and on kill are 0 (CalcOffence.lua:3764, 3778), life flasks are not 'used' (CalcPerform.lua:1784, 1805), and NoLifeRegen sets LifeRegen to 0 in the first branch of the regeneration loop (CalcDefence.lua:1265-1266), BEFORE the Zealot's Oath branch (1267-1277), the legacy chain-breaker branch, Life Regen applies to ES (1286-1291; Kaom's Spirit style) and the Pious Path branch (1295-1301).

Measured (headless, in memory, nothing saved; keystone only - node 10808 force-allocated alone, path cost not included; same numbers at None (enemy level 85) and Pinnacle (84); TotalEHP, max hits and DPS keys unchanged on all three seeds):

| Seed | what changed | before -> after |
|---|---|---|
| EK (CI, Life 1) | LifeRegen / LifeRegenRecovery | 116 -> 0 (a flat regen on a 1-Life pool, see [[Chaos Inoculation]]); ComprehensiveNetLifeRegen -307.5 -> -423.5 at Pinnacle |
| FR (CI + Zealot's Oath, Life 1) | EnergyShieldRegen / EnergyShieldRegenRecovery | 2250.6 -> 115 per second (-94.9%); EnergyShieldRegenPercent 13.1 -> 0.7 |
| FR | LifeLeechInstantProportion (main skill Cyclone is melee) | 0 -> 1 |
| Fireball seed (NOT VIABLE, Life 2333, Mind Over Matter) | LifeRegen / LifeRegenRecovery, LifeOnKill | 189 -> 0, 10 -> 0 |

- Leech tests (custom line, not gear): FR with '1% of Physical Attack Damage Leeched as Life': LifeLeechRate 0.20 -> 0.75 per second, LifeLeechInstant 0 -> 0.10 per hit (Life is 1, so the size is meaningless; the proof is that Cyclone's leech becomes instant and bypasses the leech rate). Fireball seed with '2% of Fire Damage Leeched as Life' (a spell): LifeLeechRate 466.6, LifeLeech 233.3 per hit, LifeLeechInstantProportion 0 with and without the keystone (non-melee leech is unchanged); '1% of Physical Attack Damage Leeched as Life' on the Fireball seed does nothing (Fireball is not an attack).
- DPS keys are unchanged on all seeds. Zealot's Oath: PoB treats NoLifeRegen as higher priority; see below.

PoB vs the wiki (conflicts kept visible):
- Zealot's Oath, Pious Path and Kaom's Spirit: the wiki (Vaal Pact rev 1647702) says the modifier is checked when life is changed and "life recovery modifiers can still be used for other purposes through mechanics like Zealot's Oath, Pious Path, or Kaom's Spirit". PoB zeroes all three: FR ES regeneration 2250.6 -> 115. Until the game is tested the FR figure is a PoB reading, probably an understatement of the keystone's partner with Zealot's Oath.
- Brutal Fervour: the wiki says a hybrid melee plus non-melee skill (Molten Strike) gets both instant leech and overleech; PoB's melee flag is per skill cfg (not tested).

```interaction
id: vaal-pact
mechanic: "Life Leech from Melee Damage is Instant; Cannot Recover Life other than from Leech (leech and Temporal Rift only; regeneration, flasks, life on hit and kill stop); no effect on energy shield or mana leech; non-melee life leech stays non-instant"
family: resource
target: self
related: [leech, defences, receiving-damage, chaos-inoculation, es-recovery-keystones]
pipeline_step: ["Receiving damage#Recovery"]
pipeline_why: "Vaal Pact acts on recovery, not on incoming damage: melee life leech is added at once to the leech rate without the max-leech cap (CalcOffence.lua:3730, 4124-4125) while every other life recovery channel is switched off (CalcDefence.lua:1213, 1265-1266, 1343, 1564; CalcOffence.lua:3764, 3778; CalcPerform.lua:1784, 1805); PoB's TotalEHP and max hit contain no recovery, so they do not change."
pob:
  measured: full
  how: "Data/ModCache.lua:17369 (InstantLifeLeech BASE 100, flags 256 = ModFlag.Melee, Data/Global.lua:110) and 14558 (flags CannotRecoverLifeOutsideLeech + NoLifeRegen; Modules/ModParser.lua:4790-4794); CalcOffence.lua:3730 (instant proportion), 4124-4125 (instant rate added without cap), 3764 and 3778 (life on hit and kill); CalcDefence.lua:1213, 1343, 1564-1568, 1265-1266 (NoLifeRegen first, skipping Zealot's Oath 1267-1277, 1286-1291, 1295-1301); CalcPerform.lua:1784, 1805 (life flasks). Measured headless on EK, FR, Fireball seed (node 10808 alone, None and Pinnacle): EK LifeRegen 116 -> 0; FR EnergyShieldRegen 2250.6 -> 115 (Zealot's Oath conversion lost), LifeLeechInstantProportion 0 -> 1 (Cyclone is melee); Fireball LifeRegen 189 -> 0, LifeOnKill 10 -> 0, spell leech not instant; TotalEHP, max hits, DPS unchanged. Not modelled: wiki rule that Zealot's Oath, Pious Path and Kaom's Spirit keep working (PoB zeroes them), recoup and other recovery channels, Temporal Rift."
  config:
    - {var: enemyIsBoss, default: "Pinnacle (list index 3)", ref: "Modules/ConfigOptions.lua:2086 (enemy level only; the keystone's numbers are identical at None and Pinnacle)", class: b}
    - {var: conditionCritRecently, default: false, ref: "Atziri's Acuity condition 'dealt a Critical Strike Recently' (Data/ModCache.lua:22936); the config tick name was not looked up", class: c}
  unparsed: []
model: null
providers:
  - {kind: keystone, name: "Vaal Pact 10808", slot: tree, role: enables, target: self, text: "Life Leech from Melee Damage is Instant; Cannot Recover Life other than from Leech", source: "TreeData/3_29/tree.lua:60121-60125; Data/ModCache.lua:14558, 17369; Modules/ModParser.lua:3179, 4790-4794", pob: full}
  - {kind: tattoo, name: "Vaal Pact tattoo (keystone tattoo)", slot: tree, role: enables, target: self, text: "replaces a tree node with the Vaal Pact keystone (Limited to 1 Keystone Tattoo)", source: "Data/TattooPassives.lua:4720-4726", pob: full}
  - {kind: unique, name: "Atziri's Acuity", slot: Gloves, role: enables, target: self, text: "You have Vaal Pact if you've dealt a Critical Strike Recently (variants 2 and 3)", source: "Data/Uniques/gloves.lua:29; Data/ModCache.lua:22936; Modules/ModParser.lua:4674", pob: partial, variant: "variants 2, 3"}
  - {kind: unique, name: "Doomsower", slot: Sword, role: enables, target: self, text: "You have Vaal Pact while all Socketed Gems are Red (variants 4 and 5)", source: "Data/Uniques/sword.lua:815; Data/ModCache.lua:22937; Modules/ModParser.lua:3290", pob: partial, variant: "variants 4, 5"}
  - {kind: unique, name: "Mahuxotl's Machination", slot: Shield, role: enables, target: self, text: "grants Vaal Pact together with Corrupted Soul, Divine Flesh, Eternal Youth, Everlasting Sacrifice and Immortal Ambition (all six keystones as explicit lines)", source: "Data/Uniques/shield.lua:1018-1024; Data/ModCache.lua:22379", pob: full}
  - {kind: mod, name: "You have Vaal Pact while at maximum Endurance Charges", slot: any, role: enables, target: self, text: "keystone while Endurance Charges are at maximum (owning item not traced)", source: "Data/ModCache.lua:22938; Modules/ModParser.lua:4675", pob: partial}
  - {kind: mod, name: "Crucible weapon tree and Hellscape upside: Vaal Pact", slot: Weapon, role: enables, target: self, text: "weapon tree keystone and Scourge body armour upside", source: "Data/Crucible.lua:1348; Data/ModScourge.lua:838", pob: full}
  - {kind: mod, name: "Life Leech of Physical Attack Damage and other melee leech (nodes, gear, gems)", slot: any, role: scales, target: self, text: "the leech becomes instant; PoB adds the instant part at the full rate without the max leech rate; spells and projectiles keep non-instant leech", source: "Modules/CalcOffence.lua:3730, 4124-4125; headless FR custom-line test", pob: full}
  - {kind: keystone, name: "Zealot's Oath / Pious Path / Kaom's Spirit (life regeneration redirected)", slot: tree, role: blocks, target: self, text: "wiki: still work with Vaal Pact; PoB: NoLifeRegen is checked first so the redirected regeneration is lost (FR 2250.6 -> 115 ES per second)", source: "wiki Vaal Pact rev 1647702; Modules/CalcDefence.lua:1265-1301; headless FR", pob: partial}
  - {kind: mod, name: "Life regeneration, Life flasks, Life on Hit / on Kill / on Block / on Suppress", slot: any, role: blocks, target: self, text: "all stop under the keystone (wiki: 'sources that aren't leech or Temporal Rift'); PoB zeroes them in the places listed under How PoB applies it", source: "wiki Vaal Pact rev 1647702; Modules/CalcDefence.lua:1213, 1564; Modules/CalcOffence.lua:3764, 3778; Modules/CalcPerform.lua:1784, 1805", pob: full}
makes_redundant:
  - {provider: "Life regeneration, Life flasks, Life on Hit and on Kill, Life on Block (nodes, gear, jewels)", when: "Vaal Pact allocated", why: "they recover nothing under the keystone; PoB zeroes LifeRegen (EK 116 -> 0, Fireball seed 189 -> 0) and LifeOnKill (10 -> 0)", source: "headless EK and Fireball seed; wiki Vaal Pact rev 1647702"}
  - {provider: "Vaal Pact on Chaos Inoculation builds", when: "Life is 1 (CI)", why: "the pool is 1 Life, so instant melee leech and the loss of regeneration both change nothing real; EK and FR have no Life leech at all", source: "headless EK and FR; Chaos Inoculation note"}
conflicts:
  - {with: "Zealot's Oath on FR", effect: "PoB: ES regeneration 2250.6 -> 115 per second (-94.9%) because NoLifeRegen is applied first; wiki: Zealot's Oath still works with Vaal Pact", source: "headless FR; Modules/CalcDefence.lua:1265-1277; wiki Vaal Pact rev 1647702"}
  - {with: "spell and projectile builds relying on leech", effect: "no instant leech; their leech stays on the normal max-leech-rate rules", source: "headless Fireball seed custom-line test; wiki Vaal Pact rev 1647702"}
conditions:
  - {text: "instant leech applies to melee attacks only (PoB: ModFlag.Melee); it does not affect energy shield or mana leech, Ghost Reaver, leech from minions or from Totem Mastery", source: "wiki Vaal Pact rev 1647702; Data/ModCache.lua:17369"}
  - {text: "the recovery lock is checked when the player's life is modified; other life recovery stats stay on the character", source: "wiki Vaal Pact rev 1647702"}
uptime:
  Mapping:       {value: always, config: {enemyIsBoss: "None / map monsters (env.enemyLevel 85 in the headless run)"}, reasoning: "permanent while allocated; melee hits against map packs give instant leech on every hit; the cost (no regeneration or flasks) applies at once; seeds show only the cost because their pool is CI Life 1 or their skill is a spell", source: "headless EK/FR/Fireball seed; wiki Vaal Pact rev 1647702"}
  Pinnacle Boss: {value: pob, config: {enemyIsBoss: "Pinnacle (default; env.enemyLevel 84 in the headless run)"}, reasoning: "use PoB's LifeLeechInstant for the melee skill; no change to TotalEHP or max hit; boss fights that rely on regeneration lose it (Fireball seed 189 per second)", source: "headless EK/FR/Fireball seed"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Vaal_Pact (rev 1647702; version row 3.25.0)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcDefence.lua:1213, 1265-1301, 1343, 1564-1568; Modules/CalcOffence.lua:3730, 3764, 3778, 4124-4125; Modules/CalcPerform.lua:1784, 1805; Modules/ModParser.lua:3179, 3290, 4674-4675, 4790-4794; Data/Global.lua:110; Data/ModCache.lua:14558, 17369, 22379, 22936-22938; Data/TattooPassives.lua:4720-4726; Data/Uniques/gloves.lua:29; Data/Uniques/sword.lua:815; Data/Uniques/shield.lua:1018-1024; Data/Crucible.lua:1348; Data/ModScourge.lua:838; TreeData/3_29/tree.lua:60121-60125", kind: pob, patch: "3.29"}
  - {ref: "headless runs EK, FR, Fireball seed (scratchpad b3c/F_run.py, F_show.py; evidence b3c/tree-ascendancy-analyst-F.md)", kind: discovery, patch: "3.29"}
not_verified:
  - "whether Zealot's Oath, Pious Path and Kaom's Spirit really keep working with Vaal Pact in the game: the wiki says so, PoB zeroes them (FR 2250.6 -> 115 ES per second); no in-game test"
  - "the size of instant melee leech on a real melee seed: EK and FR are CI (Life 1) with no life leech, so only a custom-line test on FR was run (0.10 per hit on 1 Life)"
  - "Brutal Fervour hybrid skills (instant plus overleech) and minion or Totem Mastery leech exclusions from the wiki were not tested in PoB"
  - "other recovery channels under the keystone (life recoup, Temporal Rift, Vitality-type effects) were not checked in PoB; the wiki lists leech and Temporal Rift as the only allowed life recovery"
  - "the tick name behind Atziri's Acuity 'Critical Strike Recently' (CritRecently) was not looked up in ConfigOptions"
  - "the owner of 'You have Vaal Pact while at maximum Endurance Charges' (Data/ModCache.lua:22938) was not traced; Doomsower and Atziri's Acuity variants were read from PoB unique data only"
  - "enemy level 85 (None) and 84 (Pinnacle) are env.enemyLevel from the headless run; why None is one level higher was not traced"
open_questions:
  - "Should the generator treat Zealot's Oath + Vaal Pact as compatible (wiki) or as PoB shows it (ES regeneration lost) until the user tests it in the game?"
```
