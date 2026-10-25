---
type: interaction
status: draft
pob_refs: [FlaskChargeGen, FlaskChargeOnCritChance, FlaskChargesGenerated, LeftActiveMagicUtilityFlasks, conditionUsingFlask]
source: "wiki Flask rev 1697263; PoB 2.67.2 ItemsTab.lua:4784-4857, CalcPerform.lua:1578-1634, CalcSetup.lua:1028-1031, ModParser.lua; vault Gaps/Mageblood flasks; build-strategist, item-analyst, tree-ascendancy-analyst, skill-gem-analyst (task 027)"
last_confirmed_patch: "3.29.x"
---

How often a flask is actually on. PoB treats a flask as on or off (a checkbox); Mageblood forces the leftmost magic utility flasks on. PoB's own flask-tooltip uptime (ItemsTab.lua:4830-4857) counts timed charge generation only, so it is a floor: it ignores charges on critical strike and on kill. Use PoB's number as the floor; add crit and kill charges as a labelled model. Mageblood flasks need no model (always on); see [[Mageblood flasks]].

Pipeline: none - no damage/defence step: a flask only times effects whose own lines act in their usual step (increased, more, resistance, recovery); this note decides how long they are up, not where they act

```interaction
id: flask-uptime
mechanic: "Flask effect is up while charges cover use: charge sources are timed generation, chance on critical strike (one charge to one flask, shared 0.1 s cooldown = 0.132 s in server frames, about 7.5 charges/s cap), and kills (1 / 3.5 / 6 / 11 charges by rarity, fewer in maps)"
family: uptime
pipeline_step: []
pipeline_why: "no damage/defence step: a flask only times effects whose own lines act in their usual step (increased, more, resistance, recovery); this note decides how long they are up, not where they act"
target: self
related: [rampage, consecrated-ground]
pob:
  measured: partial
  how: "tooltip uptime = min(1, chargesGenerated_per_s * gainMod * duration / (chargesUsed * (1 - notConsume))) from timed generation only (ItemsTab.lua:4784-4857); FlaskChargeOnCritChance / FlaskChargeGen outputs exist only in breakdown mode (CalcPerform.lua:1615-1634); active flask = binary checkbox (CalcSetup.lua:1028-1031); no kill-based charge model; Mageblood marks the first N MAGIC non-life/mana/hybrid utility flasks active (CalcPerform.lua:1578-1600, ModParser.lua:5269-5270)"
  config:
    - {var: conditionUsingFlask, default: false, ref: "ConfigOptions.lua:1098", class: b}
    - {var: "flask slot active checkbox (Items tab)", default: false, ref: "CalcSetup.lua:1028-1031", class: c}
  unparsed:
    - "Mageblood: Magic Utility Flasks cannot be Used (harmless no-op)"
    - "Mageblood: Magic Utility Flask Effects cannot be removed (harmless no-op)"
model:
  proposed_kind: flask_uptime
  inputs:
    from_pob_item: [flaskData.duration, flaskData.chargesUsed, flaskData.gainMod, "FlaskDuration INC", "FlaskChargesUsed INC", "FlaskChargesGained INC", FlaskChanceNotConsumeCharges, "per-flask crit chance (Surgeon's) or global FlaskChargeOnCritChance"]
    from_pob_calcs: [FlaskChargeGen, UtilityFlaskChargeGen]
    from_pob: [CritChance, HitChance, "Speed or HitSpeed", "hits_per_cast from the projectile models"]
    from_scenario: [kills_per_s_by_rarity, map_charge_mult, n_crit_flasks]
  params: {crit_cd_s: 0.132, kill_charges: {normal: 1, magic: 3.5, rare: 6, unique: 11}, map_charge_mult: null}
  formula: "crit_events = Speed*hits_per_cast*CritChance*HitChance; crit_rate_total = 1/(crit_cd_s + 1/(crit_events*chance)); crit_rate_flask = crit_rate_total/n_crit_flasks (split UNVERIFIED); kill_rate = sum(kills_per_s[r]*kill_charges[r])*map_charge_mult; gen = (timed + crit_rate_flask + kill_rate)*gainMod; uptime = floor_pct(min(1, gen*duration/(chargesUsed*(1-notConsume)))); feed (user rule 2026-10-25: u >= 80% ticked, no notice; 50-80% ticked + user informed with u; < 50% unticked + warning with u) for the flask-on box; optional display: u*on + (1-u)*off, floored. Mageblood flasks: uptime 1, skip the model"
  calibration: "no norm found for map kill charges (wiki: monsters in maps generate even fewer, no number)"
providers:
  - {kind: unique, name: "Mageblood", slot: belt, role: sustains, target: self, text: "Leftmost (2-4) Magic Utility Flasks constantly apply their Flask Effects to you; Magic Utility Flasks cannot be Used; effects cannot be removed", source: "PoB Data/Uniques/belt.lua:546-552; CalcPerform.lua:1578-1604; vault Gaps/Mageblood flasks", pob: full}
  - {kind: foulborn, name: "Mageblood (Foulborn)", slot: belt, role: sustains, target: self, variant: "replaces 'Leftmost (2-4) Magic Utility Flasks...' with the Rightmost line", text: "Rightmost (2-4) Magic Utility Flasks constantly apply their Flask Effects to you", source: "PoB Data/ModFoulbornMap.jsonc:755 -> ModFoulborn.lua:344; CalcPerform.lua:1595-1599", pob: full}
  - {kind: flask, name: "Stormblood", slot: flask, role: sustains, target: self, text: "(20-40)% chance to gain a Flask Charge on Critical Strike", source: "PoB Data/Uniques/flask.lua:399", pob: partial}
  - {kind: flask, name: "Rotgut", slot: flask, role: sustains, target: self, text: "50% chance to gain a Flask Charge on Critical Strike (variant 4); consumes Frenzy Charges on use", source: "PoB Data/Uniques/flask.lua:293, 298-301", pob: partial}
  - {kind: mod, name: "Surgeon's (flask prefix FlaskChanceRechargeOnCrit5)", slot: flask, role: sustains, target: self, text: "(32-35)% chance to gain a Flask Charge on Critical Strike (EK sample runs 2 Surgeon's flasks)", source: "PoB Data/ModFlask.lua:95-99", pob: partial}
  - {kind: unique, name: "The Harvest", slot: axe, role: sustains, target: self, text: "Gain a Flask Charge when you deal a Critical Strike", source: "PoB Data/Uniques/axe.lua:252", pob: partial}
  - {kind: unique, name: "Watcher's Eye (Precision)", slot: jewel, role: sustains, target: self, text: "Gain a Flask Charge when you deal a Critical Strike while affected by Precision", source: "PoB Data/Uniques/Special/WatchersEye.lua:85; ModParser.lua:3585-3588", pob: partial}
  - {kind: mastery, name: "Flask mastery 40906", slot: tree, role: sustains, target: self, text: "25% chance to gain a Flask Charge when you deal a Critical Strike", source: "PoB TreeData/3_29/tree.lua:42256", pob: partial}
  - {kind: mastery, name: "Flask mastery 29214", slot: tree, role: sustains, target: self, text: "Life Flasks gain 1 Charge every 3 seconds / Mana Flasks gain 1 Charge every 3 seconds", source: "PoB TreeData/3_29/tree.lua:42234; ModParser.lua:5158-5170", pob: full}
  - {kind: notable, name: "Nature's Adrenaline 51101", slot: tree, role: sustains, target: self, text: "Flasks gain 3 Charges every 3 seconds", source: "PoB TreeData/3_29/tree.lua:83836", pob: full}
  - {kind: notable, name: "Replenishing Remedies 50690", slot: tree, role: sustains, target: self, text: "15% increased Flask Charges gained / Life and Mana Flasks gain 2 Charges every 3 s", source: "PoB TreeData/3_29/tree.lua:69122", pob: full}
  - {kind: unique, name: "The Tides of Time", slot: belt, role: sustains, target: self, text: "charges every 3 s, 100% increased recovery", source: "PoB Data/Uniques/belt.lua:968-970", pob: full}
  - {kind: gem, name: "Alchemist's Mark", slot: any, role: sustains, target: self, text: "attacker gets flask charges when hitting the marked enemy, 1 charge per 3 s (needs the mark slot)", source: "PoB Data/Skills/act_dex.lua:8", pob: none}
  - {kind: foulborn, name: "The Magnate (Foulborn)", slot: belt, role: scales, target: self, text: "Flasks applied to you have (10-15)% increased Effect (MagicUtilityFlaskEffect applies to magic utility flasks only)", source: "PoB Data/ModFoulbornMap.jsonc:826; ModParser.lua:5227", pob: full}
makes_redundant:
  - {provider: "timed-generation and crit-charge providers (Stormblood, Surgeon's, Nature's Adrenaline, Replenishing Remedies, Tides of Time)", when: "Mageblood (or Foulborn Mageblood) equipped", why: "the first N magic utility flasks are always on; still needed for non-magic, life, mana and hybrid flasks", source: "PoB CalcPerform.lua:1578-1600; build-strategist.md"}
conflicts:
  - {with: "Bisco's Leash", effect: "same belt slot as Mageblood (rampage belt vs flask belt)", source: "build-strategist.md"}
conditions:
  - {text: "display rule (user 2026-10-25): the app must always show each flask's uptime: PoB's tooltip number (ItemsTab.lua:4830-4857) + the scenario reasoning", source: "user 2026-10-25"}
  - {text: "Mageblood applies only to MAGIC utility flasks (rare/unique utility flasks, life, mana and hybrid flasks are not auto-activated)", source: "PoB CalcPerform.lua:1578-1600; pob-coverage-auditor.md"}
  - {text: "crit charge: one charge to one flask, a single cooldown shared by all effects (local and global), not affected by cooldown recovery", source: "wiki Flask rev 1697263 (3.13.0 0.2 -> 0.1 s)"}
uptime:
  Mapping:       {value: model, config: {"flask slot active": always}, reasoning: "user 2026-10-25: 100% uptime in mapping (assumption, not derived from kill charges)", source: "build-strategist.md; wiki Flask rev 1697263"}
  Pinnacle Boss: {value: pob, config: {"flask slot active": "PoB tooltip number (ItemsTab.lua:4830-4857) as the floor; crit charges added as a labelled model; Mageblood flasks always on"}, reasoning: "tooltip counts timed generation only; a unique boss kill (11 charges) comes only at the end of the fight; crit charge is not in PoB", source: "ItemsTab.lua:4830-4857; build-strategist.md"}
seeds: [FR, EK]
sources:
  - {ref: "https://www.poewiki.net/wiki/Flask (rev 1697263, 2026-07-28)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Classes/ItemsTab.lua:4784-4857; Modules/CalcPerform.lua:1578-1634; Modules/CalcSetup.lua:1028-1031; Modules/ModParser.lua:3585-3588, 5158-5170, 5269-5270", kind: pob, patch: "3.29"}
  - {ref: "vault/Gaps/Mageblood flasks.md", kind: pob, patch: "3.29"}
  - {ref: "user answers U1-U6, tasks/027-interaction-database.md log", kind: user, patch: "3.29"}
not_verified:
  - "map-monster kill-charge values and charges per second for a given clear speed"
  - "how crit charges are split across several flasks (random / first non-full / each Surgeon's to itself with the shared cooldown)"
  - "whether 'increased charges gained' multiplies crit charges"
  - "whether PoB parses Surgeon's as local flaskData or as a global modDB mod (not read)"
  - "the 70% crafted Flask Effect source of the FR seed (seed note)"
  - "Alchemist's Mark charges at level 20 (wiki not read)"
  - "Mageblood with non-magic flasks activates none (code reading only)"
open_questions: []
```
