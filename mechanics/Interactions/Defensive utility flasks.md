---
type: interaction
status: draft
pob_refs: [TotalEHP, Evasion, EvadeChance, Armour, PhysicalMaximumHitTaken, FireMaximumHitTaken, ColdMaximumHitTaken, SpellSuppressionChance, MovementSpeedMod, EffectiveMovementSpeedMod, CurseEffectOnSelf, IgniteAvoidChance, UsingFlask, conditionUsingFlask]
source: "PoB 2.67.2 Data/Bases/flask.lua, Data/Uniques/flask.lua, CalcPerform.lua, ItemsTab.lua; poewiki Granite_Flask rev 1488340, Jade_Flask rev 1648593, Quicksilver_Flask rev 1597918, Ruby_Flask rev 1451730, Sapphire_Flask rev 1488344, Taste_of_Hate rev 1677338 (fetched 2026-10-26); headless EK measurements (b1c-pob-flasks.md, b1c-item-flasks.md)"
last_confirmed_patch: "3.29.x"
---

Utility flasks that add defence while their buff runs: Granite (+1500 Armour), Jade (+1500 Evasion Rating), Quicksilver (40% increased Movement Speed), Quartz (+10% Suppress Spell Damage chance, Phasing), Stibnite (20% more Evasion), and the elemental flasks Ruby and Sapphire (+40% resistance and +5% maximum resistance of their element). Taste of Hate (current variant 5) shifts (20-30)% of Fire and Lightning Damage from Hits taken as Cold and sits on a Sapphire base; it no longer shifts Physical (that is a legacy variant, pre 3.25.0). EK values (TotalEHP 145,259 with all five flasks on, 123,672 with all off): FullDPS is unchanged by every flask; Jade is worth 15,190 EHP, Stibnite 5,115, Quartz 2,630, Quicksilver 0 EHP (movement speed 1.561 to 1.211 without it, curse effect on you 33% to 100%), Eternal Life 0 EHP (bleed immunity only, see [[Life and mana flasks]]). Same-base flasks do not stack (CalcPerform.lua:44-59). Related: [[Offensive utility flasks]], [[Flask uptime]], [[Elemental ailment immunity]], [[Armour and physical max hit]], [[Spell suppression]], [[Physical damage taken as elemental]].

Pipeline: [[Defences#Evasion]] and [[Defences#Armour formula]] - the flask adds to the pool before the formula; Taste of Hate acts first in [[Receiving damage#Damage taken as]], before resistance, armour and every damage-taken modifier.

```interaction
id: defensive-utility-flasks
mechanic: "A flask buff that raises defence while it runs: Granite +1500 Armour, Jade +1500 Evasion Rating, Quartz +10% Suppress Spell Damage chance and Phasing, Stibnite 20% more Evasion, Quicksilver 40% increased Movement Speed (6 s, 30 of 60 charges), Ruby and Sapphire +40% to their element's resistance and +5% to its maximum resistance (8 s, 20 of 50), Taste of Hate (20-30)% of Fire and Lightning Damage from Hits taken as Cold. Same-base flasks do not stack (highest per base name)"
family: defence
pipeline_step: ["Defences#Evasion", "Defences#Armour formula", "Defences#Spell suppression chance", "Defences#Resistance caps", "Receiving damage#Damage taken as", "Receiving damage#Resistances", "Defences#Ailment avoidance"]
pipeline_why: "armour, evasion, suppression and resistance lines add to the defence pool before its formula; taken-as is the first defender-side step and meets the new element's resistance"
target: self
related: [flask-uptime, offensive-utility-flasks, life-mana-flasks, armour-phys-max-hit, spell-suppression, max-resistances, physical-taken-as-elemental, elemental-ailment-immunity]
pob:
  measured: full
  how: "Every buff line is parsed and counted (live parse, 328 flask lines) while the slot's active box is ticked (CalcSetup.lua:1028-1031) and Condition UsingFlask is set (automatic for active flasks with instant recovery below 100%, CalcPerform.lua:1776-1778; or by conditionUsingFlask, ConfigOptions.lua:1098); item buff lines scale with flask effect and quality (CalcPerform.lua:1701-1720, 1727-1760). Same-base flasks: only the highest value of each modifier counts per base name (CalcPerform.lua:44-59, 1731-1732; measured: a plain Jade in Flask 5 next to EK's Jade changed nothing). PoB's own tooltip 'Deactivating this flask will give you' gives the same drops as the toggle (ItemsTab.lua after :4857, CalcSetup.lua:1368-1372). EK per-flask values (the build's 5 active flasks, Pinnacle Boss default): FullDPS 15,136,639 unchanged by every flask; TotalEHP 145,259 base, 123,672 all five off (-21,587); Jade off alone -15,190 (Evasion 14,082 to 7,738, EvadeChance 63 to 47); Stibnite off -5,115 (Evasion 11,735, EvadeChance 58); Quartz off -2,630 (SpellSuppressionChance 10 to 0); Quicksilver off 0 EHP (EffectiveMovementSpeedMod 1.561 to 1.211; all off 1.12; CurseEffectOnSelf 33 to 100); Eternal Life off 0 EHP (BleedAvoidChance 100 to 0). The single drops sum to 22,935 against 21,587 for all off (the evasion sources overlap multiplicatively). Hypothetical swaps into Flask 5 on EK, vs an empty slot (TotalEHP 145,259): Granite +16,387 (Armour 658 to 2,803, Physical max hit 7,538 to 8,089), plain Ruby or Sapphire +4,881 (Fire or Cold max hit 22,066 to 26,863, resistance 75 to 80), Taste of Hate current variant 5 at 20 / 25 / 30%: +6,711 / +7,028 / +7,583 (Fire max hit 22,887 / 23,099 / 23,317, Lightning 23,585 / 23,767 / 23,950, Cold 26,863, Physical 7,538 unchanged), of which the Sapphire base buff is +4,881 and the unique's lines the rest. PoB leaves out: Phasing (parses to Condition:Phasing, no output effect), Stibnite's Smoke Cloud (no mod), the wiki side effect that converted cold hits can chill or freeze you, and the real firing of 'Used when Charges reach full' flasks (EK flasks 1, 3 and 4 use it; PoB treats them as always on while ticked). The tooltip uptime reads 0% for these flasks (timed charge generation only, Surgeon's crit charges not counted)."
  config:
    - {var: conditionUsingFlask, default: false, ref: "Modules/ConfigOptions.lua:1098", class: b}
    - {var: "flask slot active checkbox (Items tab)", default: false, ref: "Modules/CalcSetup.lua:1028-1031", class: c}
  unparsed:
    - "Jade / Quartz / Stibnite (EK): Used when Charges reach full (unsupported, 'Not supported in PoB yet' Main.lua:120; no effect on numbers)"
    - "Stibnite (EK): Creates a Smoke Cloud on Use (parses to no mod, ignored)"
    - "flask suffix Corundum: Cannot be Stunned if you've been Stunned during Effect (unparsed)"
    - "flask suffix Iron: Restores Ward on use (unparsed)"
    - "flask suffix Basalt: Taunts nearby Enemies on use (unparsed)"
model: null
providers:
  - {kind: flask, name: "Granite Flask (base)", slot: flask, role: scales, target: self, text: "+1500 to Armour (3.15.0: previously 3000); 6 s, uses 30 of 60 charges. EK swap: Armour 658 to 2,803, TotalEHP +16,387", source: "Data/Bases/flask.lua:279-286; poewiki Granite_Flask rev 1488340", pob: full}
  - {kind: flask, name: "Jade Flask (base) with Examiner's affix", slot: flask, role: scales, target: self, text: "+1500 to Evasion Rating (3.15.0: previously 3000); 6 s, 30 of 60. EK Flask 1 also has 52% increased Evasion during Effect, 28% increased Duration (9.2 s): worth 15,190 TotalEHP in the build", source: "Data/Bases/flask.lua:311-318; poewiki Jade_Flask rev 1648593; b1c-pob-flasks.md (a)", pob: full}
  - {kind: flask, name: "Quicksilver Flask (base)", slot: flask, role: scales, target: self, text: "40% increased Movement Speed; 6 s, 30 of 60 (EK Flask 5: 5.5 s). EK: EffectiveMovementSpeedMod 1.561 to 1.211 without it; the same flask has 54% reduced Effect of Curses on you during Effect (CurseEffectOnSelf 33 to 100 without it); 0 EHP. 'Quicksilver Flasks you use also apply to nearby allies' reaches minions only", source: "Data/Bases/flask.lua:287-294; ModParser.lua:4158; poewiki Quicksilver_Flask rev 1597918", pob: full}
  - {kind: flask, name: "Quartz Flask (base) with Surgeon's affix", slot: flask, role: scales, target: self, text: "+10% Suppress Spell Damage chance and Phasing; 47% Avoid being Ignited during Effect (Catfish suffix); 7.2 s, 30 of 60 (EK Flask 3). Worth 2,630 TotalEHP on EK (SpellSuppressionChance 10 to 0, IgniteAvoidChance 47 to 0); Phasing has no output effect", source: "b1c-pob-flasks.md (a), (b); Data/Bases/flask.lua Quartz entry (line not recorded)", pob: partial}
  - {kind: flask, name: "Stibnite Flask (base) with Surgeon's affix", slot: flask, role: scales, target: self, text: "20% more Evasion; 13% increased Movement Speed during Effect; Creates a Smoke Cloud on Use (ignored by PoB); 9.6 s, 40 of 60 (EK Flask 4). Worth 5,115 TotalEHP on EK (Evasion 14,082 to 11,735, EvadeChance 63 to 58)", source: "b1c-pob-flasks.md (a), (b); Data/Bases/flask.lua Stibnite entry (line not recorded)", pob: partial}
  - {kind: flask, name: "Ruby Flask (base)", slot: flask, role: scales, target: self, text: "+5% to maximum Fire Resistance and +40% to Fire Resistance (3.24.0: from 50%); 8 s, 20 of 50. EK swap: Fire max hit 22,066 to 26,863, TotalEHP +4,881", source: "Data/Bases/flask.lua:255-262; poewiki Ruby_Flask rev 1451730", pob: full}
  - {kind: flask, name: "Sapphire Flask (base)", slot: flask, role: scales, target: self, text: "+5% to maximum Cold Resistance and +40% to Cold Resistance (3.24.0: from 50%); 8 s, 20 of 50. EK swap: Cold max hit 22,066 to 26,863, TotalEHP +4,881", source: "Data/Bases/flask.lua:263-270; poewiki Sapphire_Flask rev 1488344", pob: full}
  - {kind: unique, name: "Taste of Hate (taken as)", slot: flask, role: applies, target: self, text: "Current variant 5: (20-30)% of Fire and Lightning Damage from Hits taken as Cold Damage during Effect, 30% chance to Avoid being Chilled and Frozen during Effect (EK already 100% avoid: worth 0), Sapphire base buff. The shift only pays because the base buff raises maximum cold resistance (cold is then the best-mitigated element: 26,863 vs 22,066 fire). Hits only, not damage over time", source: "Data/Uniques/flask.lua:412-427 (variant 5 lines 419-425); poewiki Taste_of_Hate rev 1677338 (3.25.0, 3.25.1)", variant: "variant 5 (Current)", pob: full}
makes_redundant:
  - {provider: "a second flask of the same base (Granite, Jade, Quicksilver, Ruby, Sapphire)", when: "one flask of that base is active", why: "PoB merges buffs per base name and keeps the highest value per modifier; do not count a second one", source: "Modules/CalcPerform.lua:44-59, 1731-1732; b1c-item-flasks.md"}
  - {provider: "Taste of Hate's fire and lightning shift", when: "fire and lightning are not the weakest elemental max hits, or max cold resistance is not raised", why: "converting a hit into the better-mitigated element only helps if cold is stronger than its source; without the Sapphire base buff, moving 20% of lightning into cold lowered the lightning max hit (22,884 to 22,717)", source: "b1c-item-flasks.md (Taste of Hate readings)"}
conflicts:
  - {with: "Taste of Hate legacy variants 1-4 (pre 3.25.0)", effect: "the physical-taken-as-cold line (10-30%) and the +13,547 / +15,016 / +20,203 / +30,304 EHP figures belong to legacy variants; the current variant 5 leaves PhysicalMaximumHitTaken at 7,538", source: "Data/Uniques/flask.lua:412-427; poewiki Taste_of_Hate rev 1677338 (3.25.0); b1c-item-flasks.md"}
  - {with: "Chaos Inoculation (EK)", effect: "life-flask recovery is worth nothing with Life 1; only conditional immunities count", source: "b1c-pob-flasks.md (a)"}
conditions:
  - {text: "Flask buff lines apply only while the slot's active box is ticked, the combat or effective buff mode is on and Condition UsingFlask is set (automatic for active flasks with instant recovery below 100%)", source: "Modules/CalcSetup.lua:1028-1031; Modules/CalcPerform.lua:1776-1778, 1937; Modules/ConfigOptions.lua:1098"}
  - {text: "Same-base flasks do not stack: the highest value of each modifier per base name counts, so a second Jade, Granite, Quicksilver, Ruby or Sapphire adds nothing", source: "Modules/CalcPerform.lua:44-59, 1731-1732"}
  - {text: "Taste of Hate only shifts Hits taken (not damage over time); the wiki says it is not the same mechanic as damage conversion", source: "poewiki Taste_of_Hate rev 1677338"}
  - {text: "'Used when Charges reach full' (EK flasks 1, 3, 4) makes the game fire the flask as soon as it is full; PoB counts it as on whenever the box is ticked", source: "Main.lua:120; b1c-pob-flasks.md (b)"}
uptime:
  Mapping:
    value: pob
    config: {"flask slot active": true}
    reasoning: "use PoB's flask tooltip uptime as the floor (reads 0% for EK: no timed charge generation; Surgeon's crit charges are not counted) and the crit and kill charge model of [[Flask uptime]]; not re-modelled here"
    source: "Classes/ItemsTab.lua:4830-4857; vault Flask uptime"
  Pinnacle Boss:
    value: pob
    config: {"flask slot active": true}
    reasoning: "same floor; a defensive buff matters at the hit that would kill, and a 6-9.6 s window with 30-40 of 60 charges per use is bounded by charge gain, not duration; see Flask uptime for the model"
    source: "Classes/ItemsTab.lua:4830-4857; b1c-item-flasks.md; vault Flask uptime"
seeds: [EK]
sources:
  - {ref: "https://www.poewiki.net/wiki/Granite_Flask (rev 1488340); Jade_Flask (rev 1648593); Quicksilver_Flask (rev 1597918); Ruby_Flask (rev 1451730); Sapphire_Flask (rev 1488344); Taste_of_Hate (rev 1677338)", kind: wiki, patch: "3.29"}
  - {ref: "Data/Bases/flask.lua:255-294,311-318; Data/Uniques/flask.lua:412-427; Modules/CalcPerform.lua:44-59,1701-1760,1776-1778; Modules/CalcSetup.lua:1028-1031,1368-1372; Classes/ItemsTab.lua:4830-4857; Modules/ConfigOptions.lua:1098 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b1c-pob-flasks.md; b1c-item-flasks.md (EK measurements, in memory, restored == base)", kind: discovery, patch: "3.29"}
not_verified:
  - "Quartz and Stibnite: no wiki page read and no Data/Bases/flask.lua line recorded; base values are PoB tooltip and measurement only"
  - "real uptime of any of these flasks (PoB reads 0% for EK; the crit and kill charge model was not run)"
  - "how the game treats 'Used when Charges reach full' for uptime (wiki not read for that line)"
  - "whether converted cold hits can chill or freeze you under Taste of Hate and what is lost of the ignite and shock chance on those hits (no PoB output; EK freeze avoid is already 100)"
  - "Taste of Hate: burning and ignite damage taken is unchanged in PoB beyond the max-hit numbers (unverified)"
  - "item rolls set with {range:0|0.5|1}; all items normalised to quality 20 in the swaps; a real quality changes every duration"
  - "numbers are EK-specific (CI, resistances 75% before caps, Pinnacle Boss default hit mix); a build whose weak point is physical gets +0 physical from Taste of Hate's current variant"
open_questions: []
```
