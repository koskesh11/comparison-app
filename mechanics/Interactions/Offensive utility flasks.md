---
type: interaction
status: draft
pob_refs: [CritChance, ProjectileCount, FullDPS, PhysicalDamageGainAsCold, DealNoCold, UsingFlask, conditionUsingFlask, conditionOnConsecratedGround, conditionEnemyOnConsecratedGround, DamageTakenConsecratedGround]
source: "PoB 2.67.2 Data/Bases/flask.lua, Data/Uniques/flask.lua, CalcPerform.lua, ConfigOptions.lua; poewiki Diamond_Flask rev 1488339, Sulphur_Flask rev 1583803, Bottled_Faith rev 1485045, Dying_Sun rev 1597033, Taste_of_Hate rev 1677338 (fetched 2026-10-26); headless EK measurements (b1c-pob-flasks.md, b1c-item-flasks.md)"
last_confirmed_patch: "3.29.x"
---

Flasks that raise damage while their buff runs: Diamond (100% increased Global Critical Strike Chance, no lucky crit since 3.15.0), Sulphur (40% increased Damage), Bottled Faith (Sulphur base plus a damage-taken debuff on enemies standing on its Consecrated Ground), Dying Sun (2 additional Projectiles) and Taste of Hate's "Gain (10-15)% of Physical Damage as Extra Cold Damage". On EK (CoC Ethereal Knives, CI, Pinnacle Boss default) FullDPS is unchanged by every flask in the build; a swapped-in Sulphur adds 40% increased Damage (FullDPS 15,136,639 to 16,003,982, +5.73%), Bottled Faith adds more only if the user ticks the enemy-on-Consecrated-Ground config by hand (PoB does not tick it), and Diamond, Dying Sun and Taste of Hate's extra cold add 0 FullDPS on EK (crit already 100%, projectile count not in PoB's single-target DPS, Brutality zeroes the cold). Two flasks with the same base do not stack: PoB keeps the highest value per base name (CalcPerform.lua:44-59). Related: [[Defensive utility flasks]], [[Life and mana flasks]], [[Flask uptime]], [[Consecrated ground]], [[Conversion and gain as extra]].

Pipeline: [[Damage calculation#Increased and reduced]] - Sulphur and Diamond are additive increased lines inside the pool; Bottled Faith acts on the enemy in [[Damage calculation#Damage taken]]; Taste of Hate's extra cold is [[Damage calculation#Gain as extra]].

```interaction
id: offensive-utility-flasks
mechanic: "A flask buff that raises damage or crit while it runs: Diamond 100% increased Global Critical Strike Chance (6 s, 20 of 40 charges); Sulphur 40% increased Damage (8 s, 40 of 60) plus Consecrated Ground on use; Bottled Faith (Sulphur base) puts (7-10)% increased Damage taken on enemies standing on its ground; Dying Sun 2 additional Projectiles (and fire resistance); Taste of Hate gains (10-15)% of Physical as extra Cold. Same-base flasks do not stack (highest per base name)"
family: buff
pipeline_step: ["Damage calculation#Increased and reduced", "Damage calculation#Critical strike", "Damage calculation#Damage taken", "Damage calculation#Gain as extra"]
pipeline_why: "Sulphur and Diamond add to the increased pool and crit chance; Bottled Faith's ground adds increased damage taken on the enemy; gain-as-extra is an offensive conversion-like step on the damage type pool"
target: self
related: [flask-uptime, defensive-utility-flasks, life-mana-flasks, consecrated-ground, conversion-gain-as-extra, lucky-critical-strikes]
pob:
  measured: partial
  how: "All flask buff lines are parsed and counted while the slot's active box is ticked (CalcSetup.lua:1028-1031) and the Condition UsingFlask is set automatically for every active flask with instant recovery below 100% (CalcPerform.lua:1776-1778); item buff lines scale with flask effect (CalcPerform.lua:1701-1720, 1727-1760). Same-base flasks: mergeBuff keeps the highest value per base name (CalcPerform.lua:44-59, called with item.baseName at :1731-1732; a second Jade in another slot changed nothing). PoB leaves out: the Consecrated Ground a flask creates (the implicit parses to an EMPTY mod list, ModCache.lua:14819), so the ground config must be ticked by hand and the ground's uptime and position are not modelled; the extra projectiles reach only the projectile count (EK ProjectileCount 17 to 19) and not FullDPS, because dpsMultiplier is 1 for EK (CalcOffence.lua:805, 1096); Taste of Hate's gain-as-extra cold is parsed (PhysicalDamageGainAsCold, ModCache.lua:15776) but zeroed on EK by Brutality (DealNoCold = 1 from Skill:SupportBrutality). PoB's tooltip flask uptime is 0% for EK flasks: it counts timed charge generation only (ItemsTab.lua:4830-4857) and ignores Surgeon's crit charges (FlaskChargeOnCritChance 67 is read nowhere except breakdown output, CalcPerform.lua:1634). EK values: FullDPS 15,136,639 unchanged by every flask in the build; swapped into Flask 5 on EK: Sulphur 16,003,982 (+5.73%); Bottled Faith with the enemy ground config ticked 16,852,678 / 17,095,162 / 17,216,405 at 7 / 9 / 10% (+11.3% / +12.9% / +13.7% vs an empty slot), without the config only Sulphur's 16,003,982."
  config:
    - {var: conditionUsingFlask, default: false, ref: "Modules/ConfigOptions.lua:1098", class: b}
    - {var: "flask slot active checkbox (Items tab)", default: false, ref: "Modules/CalcSetup.lua:1028-1031", class: c}
    - {var: conditionOnConsecratedGround, default: false, ref: "Modules/ConfigOptions.lua:1148", class: b}
    - {var: conditionEnemyOnConsecratedGround, default: false, ref: "Modules/ConfigOptions.lua:2012-2013", class: b}
  unparsed:
    - "Bottled Faith: Consecrated Ground created by this Flask has Tripled Radius (unparsed, ModCache.lua:14759; no effect on numbers)"
    - "Sulphur / Bottled Faith: Creates Consecrated Ground on Use (parses to an empty mod list, silently ignored, ModCache.lua:14819)"
model: null
providers:
  - {kind: flask, name: "Diamond Flask (base)", slot: flask, role: scales, target: self, text: "100% increased Global Critical Strike Chance; 6 s, uses 20 of 40 charges (tooltip 7.2 s at quality 20). No lucky crit since 3.15.0 (wiki rev 1488339). EK: CritChance already 100, so +0 FullDPS", source: "Data/Bases/flask.lua:247-254 (CritChance INC 100, ModCache.lua:4186); poewiki Diamond_Flask rev 1488339 (3.15.0, 3.16.0)", pob: full}
  - {kind: flask, name: "Sulphur Flask (base)", slot: flask, role: scales, target: self, text: "40% increased Damage; 8 s, uses 40 of 60 charges (40 of 60 since 3.15.0, 8 s since 3.16.0); implicit Creates Consecrated Ground on Use (radius stat 18). EK swap: FullDPS +5.73%", source: "Data/Bases/flask.lua:349-358; poewiki Sulphur_Flask rev 1583803; Modifier:UtilityFlaskConsecrate rev 1557426", pob: partial}
  - {kind: unique, name: "Bottled Faith", slot: flask, role: applies, target: enemy, text: "Current variant 3 on a Sulphur base: (7-10)% increased Damage taken by enemies on the flask's Consecrated Ground during Effect, (100-150)% increased Critical Strike Chance against enemies on Consecrated Ground, (15-30)% reduced Duration (6.7-8.2 s, uses 40 of 60), Tripled Radius. Gated: the enemy config must be ticked (default off). Wiki: stacks additively with other consecrated-ground increased damage taken (such as Zealotry's Watcher's Eye)", source: "Data/Uniques/flask.lua:136-151 (ModParser.lua:4168; CalcPerform.lua:3662-3665); poewiki Bottled_Faith rev 1485045", variant: "variant 3 (Current)", pob: config}
  - {kind: unique, name: "Dying Sun", slot: flask, role: scales, target: self, text: "Current variant 4 on a Ruby base: Skills fire 2 additional Projectiles during Effect, (10-20)% increased Area of Effect during Effect, (125-150)% increased Charges per use, (40-60)% less Duration (uses 45 / 47 / 50 of 50 charges, lasts 5.8 / 4.8 / 3.8 s at range 0 / mid / max). EK: ProjectileCount 17 to 19, FullDPS +0 (PoB single-target DPS does not use the count); the shotgun gain needs the vault projectile model", source: "Data/Uniques/flask.lua:228-243 (ProjectileCount BASE 2 [UsingFlask], ModCache.lua:20425); poewiki Dying_Sun rev 1597033", variant: "variant 4 (Current)", pob: partial}
  - {kind: unique, name: "Taste of Hate (gain as extra)", slot: flask, role: scales, target: self, text: "Current variant 5: Gain (10-15)% of Physical Damage as Extra Cold Damage during effect (Sapphire base, 8 s, uses 20 of 50). EK: +0 FullDPS because the skill is supported by Brutality (DealNoCold = 1, so no cold damage is dealt). Its defensive half is in [[Defensive utility flasks]]", source: "Data/Uniques/flask.lua:412-427 (PhysicalDamageGainAsCold BASE [UsingFlask], ModCache.lua:15776); poewiki Taste_of_Hate rev 1677338", variant: "variant 5 (Current)", pob: full}
makes_redundant:
  - {provider: "a second flask of the same base (Diamond, Sulphur, Ruby, Sapphire)", when: "one flask of that base is already active", why: "PoB merges buffs per base name and keeps the highest value of each modifier; a plain Jade in Flask 5 next to EK's Jade changed nothing", source: "Modules/CalcPerform.lua:44-59, 1731-1732; b1c-item-flasks.md"}
conflicts:
  - {with: "Brutality (support)", effect: "supported skill deals no non-physical damage (DealNoCold / Fire / Lightning / Chaos), so Taste of Hate's Physical-as-extra-Cold is worth 0", source: "b1c-pob-flasks.md section b (probe_gain3.py, Skill:SupportBrutality)"}
  - {with: "crit chance already at the cap", effect: "Diamond's 100% increased crit chance adds nothing when CritChance is already 100 (EK); lucky crit is not granted any more", source: "b1c-pob-flasks.md section b; poewiki Diamond_Flask rev 1488339 (3.15.0)"}
conditions:
  - {text: "Flask buff lines apply only while the slot's active box is ticked, the combat or effective buff mode is on (env.mode_combat) and the Condition UsingFlask is set (automatic for active flasks with instant recovery below 100%, or by conditionUsingFlask)", source: "Modules/CalcSetup.lua:1028-1031; Modules/CalcPerform.lua:1776-1778, 1937; Modules/ConfigOptions.lua:1098"}
  - {text: "Bottled Faith's damage-taken line needs the enemy to stand on the ground: conditionEnemyOnConsecratedGround (default false) is NOT ticked by using the flask; PoB gives 0 from the line with the default config. Effect: enemyDB DamageTaken INC = sum x (1 + ConsecratedGroundEffect)", source: "Modules/ConfigOptions.lua:2012-2013; Modules/CalcPerform.lua:3662-3665; b1c-pob-flasks.md"}
  - {text: "Sulphur-based flasks give your own Consecrated Ground effects (5% life regeneration, -50% curse effect on you) only if conditionOnConsecratedGround (default false) is ticked; using the flask does not tick it", source: "Modules/ConfigOptions.lua:1148; Modules/CalcPerform.lua:804-806, 3145-3147"}
  - {text: "Dying Sun's current version needs a nearly full flask for every use (45-50 of 50 charges) and lasts 3.8-5.8 s: uptime is bounded by charge gain, not by duration", source: "b1c-item-flasks.md (PoB tooltip at quality 20); Data/Uniques/flask.lua:228-243"}
  - {text: "Wiki mechanics note: flask effect scales Dying Sun's projectile count (3 projectiles instead of 2 with enough increased flask effect); PoB scales item buff lines by flask effect", source: "poewiki Dying_Sun rev 1597033; Modules/CalcPerform.lua:1701-1720, 1727-1760"}
uptime:
  Mapping:
    value: pob
    config: {"flask slot active": true, conditionOnConsecratedGround: "only for the ground's own effects"}
    reasoning: "use PoB's flask tooltip uptime as the floor (it reads 0% for EK: no timed charge generation; Surgeon's crit charges and kill charges are not counted) and add the crit and kill charge model of [[Flask uptime]]; do not re-model it here. Bottled Faith additionally needs the ground under the enemy, which PoB does not model"
    source: "Classes/ItemsTab.lua:4830-4857; vault Flask uptime"
  Pinnacle Boss:
    value: pob
    config: {"flask slot active": true, conditionEnemyOnConsecratedGround: "ticked by hand for Bottled Faith"}
    reasoning: "same floor; a boss that leaves the ground gets no debuff, so Bottled Faith's gain is an upper bound; the uptime of the ground is not in PoB"
    source: "Classes/ItemsTab.lua:4830-4857; b1c-item-flasks.md; vault Flask uptime, Consecrated ground"
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Diamond_Flask (rev 1488339); Sulphur_Flask (rev 1583803); Bottled_Faith (rev 1485045); Dying_Sun (rev 1597033); Taste_of_Hate (rev 1677338)", kind: wiki, patch: "3.29"}
  - {ref: "Data/Bases/flask.lua:247-254,349-358; Data/Uniques/flask.lua:136-151,228-243,412-427; Modules/CalcPerform.lua:44-59,1701-1760,1776-1778,3662-3665; Modules/CalcSetup.lua:1028-1031; Modules/ConfigOptions.lua:1098,1148,2012-2013; Classes/ItemsTab.lua:4830-4857 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b1c-pob-flasks.md; b1c-item-flasks.md (EK measurements, in memory, restored == base)", kind: discovery, patch: "3.29"}
not_verified:
  - "real uptime of any of these flasks (PoB reads 0% for EK; the crit and kill charge model of Flask uptime was not run here)"
  - "Sulphur and Bottled Faith ground: duration, exact radius behaviour, and whether the damage-taken effect persists after the flask ends (wiki gives only the implicit radius stat 18)"
  - "Dying Sun with a flask-effect source (wiki says 3 projectiles): not measured; the projectile gain on a real boss needs the vault projectile model, not PoB's FullDPS"
  - "the roughly 32% other increased damage taken on the enemy before Bottled Faith is derived from two ratios, not read from an output"
  - "an earlier custom-mod reading of Bottled Faith's line at 8% without the Sulphur base gave FullDPS 16,054,011 (+6.1%); the item-based figures above include Sulphur's 40% and are the ones to use; the two were not reconciled further"
  - "item rolls: ranges were set with {range:0|0.5|1}; PoB's default midpoint prints 9 for the (7-10) line, not 8.5; all items were normalised to quality 20, a real quality changes every duration"
  - "numbers are EK-specific (CI, resistances capped, Pinnacle Boss default hit mix); other builds differ"
open_questions: []
```
