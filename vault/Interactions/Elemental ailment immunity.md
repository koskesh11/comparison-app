---
type: interaction
status: draft
pob_refs: [FreezeAvoidChance, ChillAvoidChance, ShockAvoidChance, IgniteAvoidChance, FreezeImmune, ChillImmune, ShockImmune, IgniteImmune, ElementalAilmentImmune, AvoidFreeze, AvoidChill, AvoidShock, AvoidIgnite, AvoidElementalAilments, conditionChilled, conditionShocked, conditionFrozen]
source: "poewiki Ailment rev 1673310, Immunity rev 1674448, Freeze rev 1630938 (fetched 2026-10-26); PoB 2.67.2 CalcDefence.lua:1612-1625, ModParser.lua:4889-4917, Data/ModFlask.lua, Data/Uniques, TreeData/3_29/tree.lua, Data/Pantheons.lua; live parse of every quoted line (b1c-mechanics-immunity.md); EK sample probe (b1c-pob-flasks.md)"
last_confirmed_patch: "3.29.x"
---

How the player stops freeze, chill, shock and ignite from landing on them. There are three different things: Immune (new ones are stopped and existing stacks are removed), Cannot be X (new ones stopped, existing stay) and a chance to avoid (100% counts as Cannot be X, the reverse is not true). Immunity to freeze does not protect against chill; they are separate. The enemy-side notes are [[Freeze]], [[Chill]], [[Shock]] and [[Ignite]]; this note is about ailments on you, next to [[Defences]] and [[Flask uptime]].
Impact: PoB gives one number per ailment (FreezeAvoidChance etc., 0 to 100). It over-counts the reactive flasks ('if used while Frozen') as permanent immunity and drops the freeze half of Hrimnor's Resolve and the chill and freeze half of The Goddess Unleashed, so the generator should read the output and then correct for those sources. EK sample: ShockAvoidChance 100, FreezeAvoidChance 100 (not flask-sourced, source not traced), IgniteAvoidChance 47 (all from a utility flask; 0 with it off).
Pipeline: [[Defences#Ailment avoidance]] - a separate roll per ailment, multiplicative with the attacker's chance to inflict, 100% wins over 'always inflicts'.

```interaction
id: elemental-ailment-immunity
mechanic: "Freeze, chill, shock and ignite on you: Immune (stops new, removes existing), Cannot be X-ed (stops new, existing stay) or chance to avoid (100% equals Cannot be, not the reverse); 100% avoid or immunity beats 'always inflicts' sources; freeze immunity does not cover chill; 'Unaffected by X' applies the ailment but removes its effect"
family: defence
pipeline_step: ["Defences#Ailment avoidance"]
pipeline_why: "ailment avoidance is a roll of its own per ailment, separate from damage avoidance and from the ailment threshold; the wiki multiplies it with the attacker's inflict chance"
target: self
related: [freeze, chill, shock, ignite, flask-uptime, defences, bleed-poison-cb-immunity, stun]
pob:
  measured: partial
  how: "output.<Ailment>AvoidChance for Ignite, Chill, Freeze, Shock, Scorch, Brittle, Sap = 100 if <Ailment>Immune or ElementalAilmentImmune, else floor(min(100, Avoid<Ailment> + AvoidAilments + AvoidElementalAilments)) (+ AvoidShock when Stormshroud flag) (Modules/CalcDefence.lua:1612-1625; shown Modules/CalcSections.lua:1892-1898). When you are Chilled, Shocked or Scorched (config boxes) the effect is set to 0 at 100 avoid (Modules/CalcPerform.lua:862-896). Freeze on you has only Condition:Frozen for 'while Frozen' mods, no action speed or duration model (grep CalcPerform / CalcDefence). Enemy ignite and poison chance in the DoT model is multiplied by (1 - AvoidChance/100) (CalcDefence.lua:3536-3544). Avoid 100 and Immune are treated the same, so the wiki difference (removes existing or not) is not modelled; harmless for the output. Live parse (not ModCache): Immunity to Freeze and Chill during Effect lines parse to FreezeImmune / ChillImmune FLAG under Condition UsingFlask (ModParser.lua:4892-4893); ModCache.lua:16450-16454 holds only an unparsed joined two-line text, so ModCache alone is misleading here. Generator reads output.FreezeAvoidChance / ChillAvoidChance / ShockAvoidChance / IgniteAvoidChance (integer 0 to 100; flag-level immune cannot be told from 100 avoid in the output, read modDB flags if needed)."
  config:
    - {var: conditionChilled, default: false, ref: "Modules/ConfigOptions.lua:1198", class: b}
    - {var: conditionShocked, default: false, ref: "Modules/ConfigOptions.lua:1210", class: b}
    - {var: conditionFrozen, default: false, ref: "Modules/ConfigOptions.lua:1204", class: b}
    - {var: conditionBurning, default: false, ref: "Modules/ConfigOptions.lua:1189 (gates 'Cannot be Chilled while Burning')", class: b}
    - {var: conditionUsedFireSkillRecently, default: false, ref: "Modules/ConfigOptions.lua:1529 (gates Hrimnor's Resolve)", class: b}
    - {var: conditionHaveEnergyShield, default: false, ref: "Modules/ConfigOptions.lua:192 ('Do you always have Energy Shield?'; Condition:HaveEnergyShield is set nowhere else)", class: b}
    - {var: conditionFocused, default: false, ref: "Modules/ConfigOptions.lua:1003", class: b}
    - {var: conditionOnConsecratedGround, default: false, ref: "Modules/ConfigOptions.lua:1148", class: b}
    - {var: buffPhasing, default: false, ref: "Modules/ConfigOptions.lua:1036", class: b}
  unparsed:
    - "Hrimnor's Resolve (variant 3): 100% chance to Avoid being Chilled or Frozen if you have used a Fire Skill Recently - live parse gives only AvoidChill, the 'or Frozen' half is lost"
    - "The Goddess Unleashed: 100% chance to Avoid being Ignited, Chilled or Frozen with Her Blessing - live parse gives only AvoidIgnite; no config box for Her Blessing"
    - "Beacon of Madness: Immune to Elemental Ailments while affected by Glorious Madness - no config box for Glorious Madness"
    - "Hibernator, Fire Attunement, Capacitor: You cannot be Frozen / Ignited / Shocked if you've been X Recently - not parsed at all"
    - "Protection Mastery (tree effect 31331): Damaging / Non-Damaging Ailments Cannot Be inflicted on you while you already have one - not parsed"
    - "Shackles of the Wretched: cannot be Chilled / Frozen / Shocked / Ignited for 3 seconds after being X - not parsed"
model:
  proposed_kind: reactive_flask_immunity_window
  inputs: {from_pob: [flask duration and charge use from the flask tooltip, "FreezeAvoidChance / ChillAvoidChance / ShockAvoidChance / IgniteAvoidChance without UsingFlask-reactive sources"], from_scenario: [hit rate of the ailment source on you, scenario length]}
  params: {immunity_seconds_by_tier: "6-8 up to 15-17 s (reactive flask suffixes, Data/ModFlask.lua:220-231)", first_application: "always lands (the flask is used while already affected)"}
  formula: "reactive flask suffixes ('Grants Immunity to X if used while X') protect only against re-application inside the immunity window after one use; PoB instead counts 100% immunity whenever any flask is in use (Condition UsingFlask, CalcPerform.lua:1773-1778). Count them as 0 for the 'prevents the first ailment' question and as 'removes the ailment now plus window protection' only when the generator needs recovery time. 'During Effect' suffixes are correct in PoB and follow the flask uptime."
  calibration: "no norm found (derived from the flask mod text, wiki Modifier:FlaskChillFreezeImmunity1 rev 1566712)"
providers:
  - {kind: flask, name: "of the Deer / Walrus / Penguin (utility)", slot: flask, role: enables, target: self, text: "Immunity to Freeze and Chill during Effect + (45-49 / 40-44 / 35-39)% less Duration (lv 4 / 38 / 72); stat is flask-local", source: "Data/ModFlask.lua:242-244; wiki Modifier:FlaskFreezeAndChillImmunityDuringEffect(2)", pob: full}
  - {kind: flask, name: "of the Conger / Moray / Eel (shock) and Urchin / Mussel / Starfish (ignite, also removes Burning on use)", slot: flask, role: enables, target: self, text: "Immunity to Shock during Effect (lv 6 / 40 / 74); Immunity to Ignite during Effect, Removes Burning on use (lv 6 / 40 / 74)", source: "Data/ModFlask.lua:239-241, 245-247", pob: full}
  - {kind: flask, name: "reactive: Convection..Thawing, Earthing..the Dielectric, Damping..Quenching (life or mana flask)", slot: flask, role: enables, target: self, text: "Grants Immunity to Chill / Freeze, Shock or Ignite for (6-8 .. 15-17) seconds if used while Chilled / Frozen, Shocked or Ignited; ignite version removes all Burning (weight 750 on life flasks, 0 on utility flasks)", source: "Data/ModFlask.lua:220-231; ModParser.lua:4892-4893 (parsed as UsingFlask immunity)", pob: partial}
  - {kind: flask, name: "chance-based avoid flasks (Orca..Seal, Guppy..Sunfish, Tree Moss..Bog Moss; Taste of Hate)", slot: flask, role: scales, target: self, text: "(31-35 .. 51-55)% chance to Avoid being Chilled / Frozen, Ignited or Shocked during Effect (lv 4 to 80); Taste of Hate 30% Avoid Chilled / Frozen; EK carries a 47% Avoid Ignite flask (Catfish)", source: "Data/ModFlask.lua:183-197; Data/Uniques/flask.lua:426-427; b1c-pob-flasks.md (EK IgniteAvoidChance 47, 0 with the flask off)", pob: full}
  - {kind: unique, name: "Cannot be Frozen / Chilled / Ignited / Shocked uniques", slot: any, role: enables, target: self, text: "The Brine Crown, Alpha's Howl (also Shocked), Shiversting, Wanderlust, Dream Fragments, Vix Lunaris, Annihilation's Approach (Chilled + Frozen), Winterheart, Icetomb, Ashrend, The Goddess Scorned, Invictus Solaris, Fairgraves' Tricorne (Shocked); Kiara's Determination 'Immunity to Freeze, Chill, Curses and Stuns during Effect'", source: "Data/Uniques/helmet.lua:1088,207,248; sword.lua:1017,124; boots.lua:635,779-780; ring.lua:487-488; shield.lua:904,996; amulet.lua:1312; body.lua:1016,225; flask.lua:268", pob: full}
  - {kind: unique, name: "Hrimnor's Resolve (variant 3), The Goddess Unleashed", slot: helmet / body armour, role: enables, target: self, text: "100% chance to Avoid being Chilled or Frozen if you have used a Fire Skill Recently (wiki: Cannot be Chilled or Frozen if ...); Goddess Unleashed 100% Avoid Ignited, Chilled or Frozen with Her Blessing", variant: "Hrimnor's Resolve variant 3 (Data/Uniques/helmet.lua:131)", source: "Data/Uniques/helmet.lua:131; wiki Hrimnor's Resolve rev 1488070 (mod AvoidFreezeAndChillIfFireSkillUsedRecentlyUnique__1)", pob: partial}
  - {kind: gem, name: "Arctic Armour / Purity of Elements / Tempest Shield / Vaal Impurity of Ice, Fire, Lightning", slot: any, role: enables, target: self, text: "Arctic Armour: immune to being Frozen; Purity of Elements: immunity to all elemental ailments (ElementalAilmentImmune); Tempest Shield: shock immunity; Vaal Impurity: temporary immunity to its element. Purity of Ice / Fire / Lightning carry no immunity stat in PoB 3.29 data", source: "Data/Skills/act_dex.lua:613; act_int.lua:14585,20183-20184,14748; act_dex.lua:12345-12347; act_str.lua:9017; wiki Arctic Armour rev 1681716, Purity of Elements rev 1681679, Tempest Shield rev 1681667", pob: full}
  - {kind: ascendancy, name: "Occultist Frigid Wake, Saboteur Pyromaniac, Reliquarian Elevore, Juggernaut small node", slot: tree, role: enables, target: self, text: "Frigid Wake: Cannot be Chilled and Cannot be Frozen (node 47630); Pyromaniac: Immune to Ignite and Shock (node 16940); Elevore: 25% Avoid Elemental Ailments (node 48040); Ascendant carries the Juggernaut small node Cannot be Chilled (node 61072)", source: "TreeData/3_29/tree.lua (build.spec.tree.nodes scan, b1c-mechanics-immunity.md)", pob: full}
  - {kind: notable, name: "Antifreeze, Insulated, Non-Flammable, Crystal Skin, Elegant Form, Thick Skin and small avoidance nodes", slot: tree, role: scales, target: self, text: "30% Avoid being Frozen / Shocked / Ignited; Crystal Skin and Elegant Form 20% Avoid Elemental Ailments; Thick Skin 8%; small nodes 20% Freeze and Chill / Ignite / Shock Avoidance; Wrapped in Flame: Cannot be Chilled while Burning; Shield Mastery 20% Avoid Elemental Ailments while holding a Shield (effect 50228)", source: "TreeData/3_29/tree.lua (node ids 33676, 54798, 1581, 40743, 40181, 19069, 19508, 22002, 42530, 10952)", pob: full}
  - {kind: notable, name: "Hibernator, Capacitor, Fire Attunement; Protection Mastery", slot: tree, role: enables, target: self, text: "Cannot be Frozen / Shocked / Ignited if you've been X Recently; Protection Mastery: ailments cannot be inflicted on you while you already have one", source: "TreeData/3_29/tree.lua (live parse: not parsed, b1c-mechanics-immunity.md)", pob: none}
  - {kind: mod, name: "Pantheon: Brine King upgrade Captain Tanner Lightfoot, Shock and Horror, Abberath group", slot: pantheon, role: enables, target: self, text: "100% chance to Avoid being Frozen; 50% reduced Effect of Chill on you; 60% less Duration of Ignite on You (Abberath group)", source: "Data/Pantheons.lua:22-23,28-29,131; wiki cargo pantheon_souls TheBrineKing", pob: full}
  - {kind: jewel, name: "corrupted jewel, Stormshroud, Veiled Rin's prefix, Arohongui tattoo", slot: jewel / craft, role: scales, target: self, text: "(20-25)% chance to Avoid being Chilled / Frozen / Ignited / Shocked; Stormshroud: modifiers to Avoid Shocked apply to all elemental ailments; Rin's: (20-30)% Avoid Chilled and 100% Avoid being Frozen; tattoo 10% Avoid Chilled / Frozen", source: "Data/ModJewel.lua:36-38; Data/Uniques/jewel.lua:469; Data/ModVeiled.lua:184; Data/TattooPassives.lua:3105-3106", pob: full}
makes_redundant:
  - {provider: "Avoid-chance sources for one ailment", when: "that ailment is already at 100% avoid or Immune", why: "a second 100% adds nothing; PoB takes the immunity flag first and stops summing (CalcDefence.lua:1620-1624)", source: "Modules/CalcDefence.lua:1620-1624"}
  - {provider: "Reactive flask (Convection .. Quenching)", when: "a during-effect immunity or a permanent Cannot be X covers the same ailment", why: "the reactive flask only starts after the ailment landed", source: "Data/ModFlask.lua:220-231"}
conflicts:
  - {with: "Crystalised Fear (Elder super siphon)", effect: "immobilises the player; not a movement or action speed slow, cannot be prevented by immunity", source: "poewiki Crystalised Fear rev 1482829"}
  - {with: "Reactive flask counted as permanent in PoB", effect: "PoB shows 100 avoid for Condition UsingFlask even though the game grants the immunity only after the ailment landed", source: "Modules/ModParser.lua:4892-4893; Modules/CalcPerform.lua:1773-1778"}
  - {with: "Unaffected by X (Chieftain Tasalio, Cleansing Water)", effect: "the ailment is applied and shown but its debuff or damage has no effect; this is not immunity and does not reach AvoidChance", source: "poewiki Ailment rev 1673310; TreeData/3_29/tree.lua:16022-16028"}
conditions:
  - {text: "Sirus (Pinnacle Boss scenario): fire, cold and lightning Die Beam always ignite, freeze and shock; the wiki Recommendations say 'Immunity to corrupted blood and Shock greatly help' (a recommendation, not a hard requirement). Generator requirement: shock immunity or 100 ShockAvoidChance for a Sirus-ready build; freeze and ignite are not named", source: "poewiki Sirus rev 1702453"}
  - {text: "Maven Circle Slam and Ion Cannon always inflict Ignite, Shock or Freeze; Maven Recommendations name no ailment requirement. Generator requirement for Maven, Exarch, Eater, Shaper, Elder: no norm found", source: "poewiki The Maven rev 1700636; Exarch rev 1636125; Eater rev 1702329; Shaper rev 1700936; Elder rev 1700744 (b1c-mechanics-immunity.md)"}
  - {text: "Mapping: generator requirement: no norm found as a number (discovery only: Maxroll says avoiding elemental ailments 'has only gained importance over time'; that page still names Raider Avatar of the Veil, which is not in the 3.29 tree, so it does not count as a 3.29 authority)", source: "https://maxroll.gg/poe/resources/defenses-and-defensive-layering (discovery)"}
  - {text: "Several conditions need a config tick to count: UsingFlask is automatic, Focused, OnConsecratedGround, Phasing, Burning, UsedFireSkillRecently, Chilled and HaveEnergyShield are not", source: "Modules/ConfigOptions.lua:192,1003,1036,1148,1189,1198,1529"}
  - {text: "the reactive 'if used while Frozen/Chilled/Shocked/Ignited' suffixes are fired in the game by the Instilling flask enchants 'Used when you become Frozen / Chilled / Shocked / Ignited'; PoB has no parser line for 'Used when' (shown as 'Not supported in PoB yet'), so it counts the reactive suffix as always on while the slot is ticked", source: "Data/EnchantmentFlask.lua:20-23; Main.lua:120; b1c-item-flasks.md; poewiki Instilling_Orb rev 1683037"}
uptime:
  Mapping:
    value: pob
    config: {}
    reasoning: "permanent sources (equipment, tree, ascendancy, pantheon, skills) are always up and PoB's AvoidChance counts them; 'during Effect' flask sources follow the flask uptime (use the PoB flask tooltip number, see Flask uptime); reactive flask sources must not be counted as prevention"
    source: "Modules/CalcDefence.lua:1612-1625; Data/ModFlask.lua:183-197,220-231,242-247"
  Pinnacle Boss:
    value: model
    config: {conditionUsedFireSkillRecently: "model: only for the Hrimnor variant, true when the build casts a fire skill at least once per few seconds"}
    reasoning: "boss ailments come from fixed always-inflict beams, so a single failed 100% avoid is the whole question; permanent 100% avoid or Immune sources are binary and safe, flask windows and reactive flasks are decided by the reactive_flask_immunity_window model"
    source: "poewiki Sirus rev 1702453; The Maven rev 1700636; Ailment rev 1673310"
seeds: [EK]
sources:
  - {ref: "https://www.poewiki.net/wiki/Ailment (rev 1673310; 3.20.0 immunity no longer shown as 100% avoid, 3.28.0f multiplicative monster ailment effect fix); https://www.poewiki.net/wiki/Immunity (rev 1674448); https://www.poewiki.net/wiki/Freeze (rev 1630938)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Sirus (rev 1702453); https://www.poewiki.net/wiki/The_Maven (rev 1700636)", kind: wiki, patch: "3.29"}
  - {ref: "Modules/CalcDefence.lua:1612-1625; Modules/ModParser.lua:4889-4917; Data/ModFlask.lua:183-247; Data/Pantheons.lua; TreeData/3_29/tree.lua (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "tasks/reports/027-evidence/b1c-mechanics-immunity.md; tasks/reports/027-evidence/b1c-pob-flasks.md", kind: discovery, patch: "3.29"}
not_verified:
  - "config boxes are type check with no explicit default (read in ConfigOptions.lua on 2026-10-26), so default false is the check-box default, not a measured run"
  - "source of EK's ShockAvoidChance 100 and FreezeAvoidChance 100 (not flask-sourced; not traced)"
  - "live PoB parse of the ascendancy, tree notable, mastery and unique-equipment lines was not run line by line; they count as parsed because they are absent from the unparsed list in the evidence"
  - "Charge Mastery 'Cannot be Chilled at max Frenzy / Shocked at max Power / Ignited at max Endurance Charges' (tree effects 48661, 14100, 28720) was listed but its parse was not checked"
  - "utility versus life flask mod weights equal the live 3.29 drop tables (PoB and wiki agree, no third source)"
  - "wiki Immunity page still says Soul of the Brine King grants Cannot be Frozen; PoB and wiki cargo say 100% chance to Avoid being Frozen (same effect by the Ailment rule; wording only)"
  - "the exact PoB handling of the Stormshroud flag for ailments other than shock"
  - "further providers (Replica Allelopathy, The Hungry Loop, Replica Tasalio's Sign Immune to Chill; Tear of Purity, Astral Projector, Kiloava's Bluster; legacy flasks with weight 0) are listed in tasks/reports/027-evidence/b1c-mechanics-immunity.md only"
open_questions:
  - "The wiki Sirus text says 'greatly help' for shock immunity; should the generator treat shock immunity for Sirus as a hard requirement or a scored preference?"
  - "Should reactive flask suffixes be ignored by the generator or credited only after the first ailment (the model above)?"
```
