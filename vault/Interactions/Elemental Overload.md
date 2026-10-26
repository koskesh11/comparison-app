---
type: interaction
status: draft
pob_refs: [CritChance, CritInPast8Sec, NoCritMultiplier, AilmentsAreNeverFromCrit, CritMultiplier, conditionHaveAugyre, conditionCritRecently]
source: "poewiki Elemental Overload rev 1482027 (fetched 2026-10-26); PoB 2.67.2 TreeData/3_29/tree.lua, Modules/ModParser.lua, CalcOffence.lua, ConfigOptions.lua; skill-gem-analyst own modLib.parseMod run; tree-ascendancy-analyst"
last_confirmed_patch: "3.29.x"
---

Elemental Overload is a keystone: skills that dealt a Critical Strike in the past 8 seconds deal 40% more Elemental Damage with Hits and Ailments, critical strikes deal no extra damage, and ailments never count as being from critical strikes. The bonus does not apply to the crit that starts the window, only to hits while it is already active. PoB parses all three lines but does not model the 8-second window: it sets the condition whenever crit chance is not 0, so it gives the full 40% even at 5% crit. Crit-mechanics content (crit multiplier, crit chance scaling versus this keystone) is batch 3 and is not written here.

Pipeline: [[Damage calculation#More and less]] - 40% more Elemental (Hit and Ailment keywords); [[Damage calculation#Critical strike]] - the crit multiplier is forced to 1 (the crit step is removed); [[Damage calculation#Ailments from hits]] - the ailment-from-crit link is switched off

Impact (a) EK: a hard no. EK's CritChance is 100% (CoC Assa run) and the build lives on crit multiplier plus impale (stored impale hit is 49% of FullDPS per the vault seed pins); Elemental Overload would set CritMultiplier to 1 and delete the ailments-from-crit link. Not a candidate, nothing to change. Impact (b) Fireball Elementalist: PoB over-credits the keystone at low crit chance because it assumes 100% uptime; with the model below, 5% crit gives 70% uptime at 1 hit per cast and 97% at 3 hits per cast (the latter needs the 0.6 hit norm). Fireball ignite is a 25% on-hit chance (act_int.lua:5816), not crit-dependent, so it is unaffected. The comparison of this keystone against crit scaling is batch 3; the generator must pick one side (crit pool or this keystone), not both.

```interaction
id: elemental-overload
mechanic: "Keystone: skills that have dealt a Critical Strike in the past 8 seconds deal 40% more Elemental Damage with Hits and Ailments; your Critical Strikes do not deal extra Damage; Ailments never count as being from Critical Strikes"
family: buff
pipeline_step: ["Damage calculation#More and less", "Damage calculation#Critical strike", "Damage calculation#Ailments from hits"]
pipeline_why: "parse result: ElementalDamage MORE 40 with Condition:CritInPast8Sec (more step), NoCritMultiplier FLAG forces the crit multiplier to 1 (crit step), AilmentsAreNeverFromCrit FLAG sets ailment chance on crit equal to on hit (ailments-from-hits step)"
target: self
related: [lucky-critical-strikes, coc-trigger, spell-projectile-supports]
pob:
  measured: partial
  how: "all three lines parse (analyst's modLib.parseMod run): line 1 -> ElementalDamage MORE 40, keywordFlags 786432 (Hit|Ailment), tag Condition:CritInPast8Sec; line 2 -> NoCritMultiplier FLAG; line 3 -> AilmentsAreNeverFromCrit FLAG; ModParser.lua:1308 (prefix 'skills that have dealt a critical strike in the past 8 seconds deal'), :993 ('with hits and ailments'), :2237, :3563. Uptime NOT modelled: `if output.CritChance ~= 0 then skillModList.conditions['CritInPast8Sec'] = true` (CalcOffence.lua:3273-3275), no config, no uptime math, the first crit is not excluded. NoCritMultiplier -> CritMultiplier = 1 (CalcOffence.lua:3204-3205); AilmentsAreNeverFromCrit sets ailment chance on crit = on hit (CalcOffence.lua:4296-4304) and zeroes crit-only DoT bonuses (CalcOffence.lua:4520, 4822, 5139, 5424)"
  config:
    - {var: conditionHaveAugyre, default: none, ref: "Modules/ConfigOptions.lua:1668-1671 (Augyre rotating buff, unique only)", class: a}
    - {var: conditionCritRecently, default: false, ref: "Modules/ConfigOptions.lua:1251 (a different condition: CritRecently, not CritInPast8Sec)", class: b}
  unparsed: []
model:
  proposed_kind: elemental_overload_uptime
  inputs: {from_pob: [CritChance], from_scenario: [hits_per_second]}
  params: {window_seconds: 8}
  formula: "P(up) = 1 - (1 - c)^(8 * hits/s), the first crit not boosted; example Fireball 5% crit, 2.98 casts/s (PoB Worb Speed): 1 - 0.95^23.8 = 70% at 1 hit per cast, 1 - 0.95^71 = 97% at 3 hits per cast (needs the 0.6 hit norm); PoB assumes 100%"
  calibration: "no norm found; derived by the analyst from the wiki rule 'an average of one critical strike every 8 seconds is achieved by performing 12.5/(Critical Strike Chance) hits per second'"
providers:
  - {kind: keystone, name: "Elemental Overload (node 22088)", slot: tree, role: applies, target: self, text: "the three lines above (wiki: near Witch/Templar)", source: "TreeData/3_29/tree.lua:39952-39958 (isKeystone); wiki Elemental Overload rev 1482027", pob: partial}
  - {kind: unique, name: "Augyre", slot: any, role: applies, target: self, text: "rotating buff chooses Elemental Overload or Resolute Technique; item text not read", source: "Modules/ConfigOptions.lua:1668-1671", pob: config}
  - {kind: keystone, name: "Resolute Technique (node 31961)", slot: tree, role: blocks, target: self, text: "never deal Critical Strikes, so the keystone window never opens", source: "TreeData/3_29/tree.lua:21817 (via tree-ascendancy-analyst)", pob: full}
  - {kind: keystone, name: "Precise Technique (node 63620)", slot: tree, role: blocks, target: self, text: "listed by the tree analyst as a conflicting crit keystone", source: "TreeData/3_29/tree.lua:68373 (via tree-ascendancy-analyst)", pob: partial}
  - {kind: keystone, name: "Perfect Agony (node 23407)", slot: tree, role: blocks, target: self, text: "with Elemental Overload you can no longer apply ailments with hits", source: "TreeData/3_29/tree.lua:80926 (via tree-ascendancy-analyst); wiki Elemental Overload rev 1482027", pob: partial}
  - {kind: mastery, name: "Critical Mastery (effect 9986)", slot: tree, role: blocks, target: enemy, text: "50% increased Effect of non-Damaging Ailments you inflict with Critical Strikes; worthless because ailments never count as from crit", source: "TreeData/3_29/tree.lua:23938 (via tree-ascendancy-analyst)", pob: full}
makes_redundant:
  - {provider: "Critical Strike Multiplier modifiers and every 'ailments from critical strikes' modifier", when: "Elemental Overload is allocated", why: "wiki: modifiers to critical strike multiplier no longer have any effect; the crit chance still matters because it keeps the 8-second window up", source: "wiki Elemental Overload rev 1482027; Modules/CalcOffence.lua:3204-3205,4296-4304"}
conflicts:
  - {with: "Resolute Technique, Precise Technique, Perfect Agony", effect: "Resolute Technique and Precise Technique are crit keystones that conflict (Resolute Technique never crits); Perfect Agony + Elemental Overload = no ailments from hits", source: "tree.lua:21817,68373,80926 (via tree-ascendancy-analyst); wiki Elemental Overload rev 1482027"}
conditions:
  - {text: "needs a crit within the last 8 s by that skill (per skill, not global, since 3.16.0); totems, traps and mines activate it for the player's skill; minions are unaffected", source: "wiki Elemental Overload rev 1482027 (version 3.16.0)"}
  - {text: "the bonus does not apply to the crit that activated the effect, only to hits while it is active", source: "wiki Elemental Overload rev 1482027"}
  - {text: "3.25.0: also 'Critical Strikes to not inherently inflict Ailments' (undocumented per the analyst's reading of the wiki)", source: "wiki Elemental Overload rev 1482027 version row 3.25.0"}
uptime:
  Mapping:
    value: high
    config: {}
    reasoning: "many hits per second, any crit chance of 5% or more keeps the window up; skills with many hits per second keep it up cheaply"
    source: "analyst reading of wiki Elemental Overload rev 1482027 (12.5/(crit chance) hits per second rule)"
  Pinnacle Boss:
    value: model
    config: {CritInPast8Sec: "model: P(up) = 1 - (1 - c)^(8 * hits/s)"}
    reasoning: "PoB gives the full 40% whenever CritChance is not 0 (CalcOffence.lua:3273-3275); the model corrects this for low crit chance"
    source: "Modules/CalcOffence.lua:3273-3275; analyst derivation (no calibration found)"
seeds: [Fireball]
sources:
  - {ref: "https://www.poewiki.net/wiki/Elemental_Overload (rev 1482027)", kind: wiki, patch: "3.29"}
  - {ref: "TreeData/3_29/tree.lua:39952-39958; Modules/ModParser.lua:993,1308,2237,3563; Modules/CalcOffence.lua:3204-3205,3273-3275,4296-4304; Modules/ConfigOptions.lua:1251,1668-1671 (PoB 2.67.2)", kind: pob, patch: "3.29"}
  - {ref: "wiki Elemental Overload version rows 3.16.0 (per skill, last 8 s) and 3.25.0", kind: patch_notes, patch: "3.29"}
not_verified:
  - "whether the 40% also multiplies ignite damage in PoB as the wiki says (keyword Ailment is set, but no ignite delta was run)"
  - "the keystone damage factor was not run in PoB as a build delta (custom-mod injection via input.customMods returned unchanged output); the figures use PoB's CritEffect formula (CalcOffence.lua:3262-3263) as arithmetic only"
  - "Augyre item text was not read; its role is taken from the config option only"
  - "uptime model has no calibration; it is the analyst's derivation from the wiki rule"
open_questions:
  - "Crit pool versus this keystone for the Fireball Elementalist is batch 3 (crit mechanics); the evidence gives arithmetic only (crit effect without the keystone = 1 + c(M-1), CalcOffence.lua:3262-3263), so no choice is recorded here."
  - "Should the generator override PoB's 100% uptime of the 8-second window with the model for low crit chance?"
```
