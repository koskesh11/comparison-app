---
type: interaction
status: draft
pob_refs: [buffFortification, overrideFortification, Condition:Fortified, FortificationStacks, MaximumFortification, MinimumFortification, FortifyDuration, DamageTakenWhenHit, NoFortificationMitigation]
source: "wiki Fortification rev 1698776 (Fortify redirects here), Fortify Support rev 1681881, Endurance charge rev 1697434; PoB 2.67.2 ConfigOptions.lua, CalcPerform.lua, CalcSetup.lua, ModParser.lua, Data.lua, Data/Misc.lua, Data/Skills/sup_str.lua, Data/SkillStatMap.lua, TreeData/3_29/tree.lua, Data/Uniques (task 027)"
last_confirmed_patch: "3.29.x"
---

Fortification is a stackable buff: every stack gives 1% less damage taken from hits (default maximum 20 stacks, 6 s per instance). Melee hits that Fortify give a number of stacks that depends on the hit's damage, the enemy's ailment threshold and its rarity; the formula is not on the wiki. PoB does not model the gaining at all: any Fortify line sets a flag and PoB then assumes the maximum stacks (or the override), and the Fortify Support gem alone does not set that flag. So the 1%-per-stack payoff is a config assumption, and the gem's melee damage is counted regardless.

Pipeline: [[Receiving damage#Damage taken modifiers]] - Fortification is a separate 'less damage taken from hits' multiplier applied after armour, resistances and endurance charges, so it multiplies on top of the whole mitigation chain and only against hits, not damage over time.

```interaction
id: fortify
mechanic: "Fortification: 1% less Damage taken from Hits per stack (maximum 20 by default, 6 s per instance, instances independent, one hit per 0.1 s can add stacks, stacks per hit depend on damage vs ailment threshold and rarity); PoB assumes the maximum stacks when any Fortify source or the config tick is present"
family: buff
target: self
related: [endurance-charges, onslaught, chance-on-hit-uptime]
pipeline_step: ["Receiving damage#Damage taken modifiers"]
pipeline_why: "Wiki Fortification rev 1698776: '#% less Damage taken modifiers are calculated after armour, resistances, and endurance charges'; PoB adds it as DamageTakenWhenHit MORE -stacks (CalcPerform.lua:675), a separate multiplier in the taken-modifier step; hits only"
pob:
  measured: config
  how: "CalcPerform.lua:645-678 (only in combat mode): the flag Fortified (any parsed 'Fortify' line, ModParser.lua:2592, or config buffFortification, ConfigOptions.lua:1039-1041) or MinimumFortification > 0 gives stacks = override or max (664, max = MaximumFortification BASE 20 from CalcSetup.lua:622 / Data/Misc.lua:145 plus +N lines), and adds DamageTakenWhenHit MORE -stacks (675) unless 'You do not inherently take less Damage for having Fortification' (Condition:NoFortificationMitigation, ModParser.lua:5627). Duration output 6 s x (1 + FortifyDuration inc) (CalcPerform.lua:671, Data.lua:253) is display only; gain per hit, the 0.1 s limit, the 100 instance tracking and stack decay are not modelled. The Fortify Support gem maps only the melee damage stats and FortifyEffectOnSelf (Data/Skills/sup_str.lua:2631-2647); 'chance_to_fortify_on_melee_hit_+%' has no SkillStatMap entry and no Modules file reads FortifyEffectOnSelf, so the gem does NOT set Condition:Fortified. Vigilant Strike only overrides the duration (SkillStatMap.lua:700-701)"
  config:
    - {var: buffFortification, default: false, ref: "Modules/ConfigOptions.lua:1039-1041", class: b}
    - {var: overrideFortification, default: max, ref: "Modules/ConfigOptions.lua:1042-1044", class: c}
  unparsed:
    - "Fortify Support: chance_to_fortify_on_melee_hit_+% 100 (constantStat) is not in SkillStatMap.lua: the gem does not switch Fortification on in PoB"
    - "Fortification Gain nodes: 'Fortifying Hits grant 40% increased Fortification' (TreeData/3_29/tree.lua:45173-45196) change the stacks per hit, which PoB does not model"
model:
  proposed_kind: fortification_stacks
  inputs: {from_pob: [MaximumFortification, FortifyDuration, HitSpeed], from_scenario: ["melee hit rate on a target that is hit H per second", "stacks per hit s (undocumented: wiki says it depends on damage, ailment threshold and rarity)"]}
  params: {duration_s_default: 6, max_default: 20, min_hit_gap_s: 0.1, instances_tracked: 100}
  formula: "stacks(t) = sum of the s-sized instances gained in the last d seconds, one hit per 0.1 s at most, capped at the maximum (instances still tracked at the cap, up to 100); expected steady stacks = min(max, s x min(H, 10) x d). s is unknown, so with no source for s the model can only give a bound: u(at least 1 stack) = 1-(1-p)^(H x d) for 'x% chance to Fortify'. Feed: stacks = PoB maximum only when the build hits with a Fortifying skill continuously; otherwise use the override (overrideFortification) with the modelled stacks"
  calibration: "no norm found; the wiki gives 6 s, 20 stacks and the 0.1 s limit, not the stack count per hit"
providers:
  - {kind: support, name: "Fortify Support", slot: any, role: applies, target: self, text: "Supports melee attack skills that are not triggered; 100% chance to Fortify on melee hit (constant stat), L1 10% more Melee Damage and 10% more Damage with ailments from melee hits; fortify_duration_+% as quality", source: "Data/Skills/sup_str.lua:2622-2653; wiki Fortify Support rev 1681881 (gem tags Attack, Support, Melee)", pob: partial}
  - {kind: gem, name: "Vigilant Strike", slot: any, role: applies, target: self, text: "Powerful melee strike that grants Fortification; gain_fortify_on_melee_hit_ms 8000 (duration override); cooldown can be bypassed by expending an Endurance Charge", source: "Data/Skills/act_str.lua:12482-12511; Data/SkillStatMap.lua:700-701", pob: partial}
  - {kind: unique, name: "Perseverance", slot: belt, role: applies, target: self, text: "Melee Hits which Stun Fortify (variant 2; (14-20)% chance in variant 1); You have Onslaught while Fortified", source: "Data/Uniques/belt.lua:652-663", pob: config}
  - {kind: unique, name: "The Celestial Brace", slot: gloves, role: applies, target: self, text: "Melee Hits from Strike Skills Fortify; +(1-10) to maximum Fortification; 1% increased Attack Speed per Fortification", source: "Data/Uniques/gloves.lua:54-61", pob: partial}
  - {kind: ascendancy, name: "Champion (Ascendant option) 39598", slot: tree, role: applies, target: self, text: "Melee Hits have 50% chance to Fortify; Taunt on Hit; 15% increased effect of Non-Curse Auras", source: "TreeData/3_29/tree.lua:18370-18379", pob: config}
  - {kind: mastery, name: "Fortify Mastery option 28469", slot: tree, role: applies, target: self, text: "Melee Hits Fortify, -3 to maximum Fortification (other options: 100 Life per Fortification lost, 20 Fortification on Melee Kill vs Rare/Unique, 10% reduced DoT taken at 20 Fortification)", source: "TreeData/3_29/tree.lua:32655-32711", pob: partial, variant: "option 28469: Melee Hits Fortify, -3 to maximum Fortification"}
  - {kind: notable, name: "Steadfast 13922 (cluster)", slot: tree, role: scales, target: self, text: "+3 to maximum Fortification; Regenerate 0.1% of Life per second per Fortification", source: "TreeData/3_29/tree.lua:32628-32641", pob: full}
  - {kind: notable, name: "Rampart 1340 (cluster)", slot: tree, role: scales, target: self, text: "30% increased Armour and Evasion Rating while Fortified; Fortifying Hits against Unique Enemies grant 100% increased Fortification", source: "TreeData/3_29/tree.lua:45211-45223", pob: partial}
  - {kind: unique, name: "Replica Badge of the Brotherhood", slot: amulet, role: scales, target: self, text: "+1 to maximum Fortification per Endurance Charge; (20-25)% chance to lose an Endurance Charge when you gain Fortification", source: "Data/Uniques/amulet.lua:232-235; ModCache.lua:251", pob: full}
  - {kind: unique, name: "Willowgift", slot: amulet, role: blocks, target: self, text: "You do not inherently take less Damage for having Fortification; +4% chance to Suppress Spell Damage per Fortification; (15-25)% increased Attack and Cast Speed while at maximum Fortification", source: "Data/Uniques/amulet.lua:1289-1300; Modules/ModParser.lua:5627", pob: full}
  - {kind: unique, name: "Rigwald's Hunt", slot: body, role: scales, target: self, text: "(30-40)% increased Fortification Duration; Minions have 1% chance to deal Double Damage per Fortification on you", source: "Data/Uniques/body.lua:912-918; Modules/ModParser.lua:4434", pob: full}
  - {kind: unique, name: "Bound By Destiny", slot: any, role: enables, target: self, text: "Melee Hits Fortify if 6 Warlord Items are Equipped; +1 to Maximum Endurance Charges if 6 Warlord Items are Equipped", source: "Data/Uniques/Special/BoundByDestiny.lua:50-52", pob: partial}
makes_redundant: []
conflicts:
  - {with: "Willowgift", effect: "removes the inherent 1% less damage taken per stack; Fortification then only feeds the item's suppression and speed lines", source: "Data/Uniques/amulet.lua:1298; Modules/ModParser.lua:5627"}
  - {with: "Replica Badge of the Brotherhood", effect: "(20-25)% chance to lose an Endurance Charge when you gain Fortification: more maximum Fortification costs charges", source: "Data/Uniques/amulet.lua:235"}
  - {with: "Fortify Mastery option 28469", effect: "-3 to maximum Fortification: 17 stacks instead of 20 unless other +maximum lines are present", source: "TreeData/3_29/tree.lua:32698-32699"}
conditions:
  - {text: "1% less Damage taken from Hits per stack; default maximum 20 stacks, 6 seconds per instance; the stacks gained per hit depend on the hit's damage, the enemy's ailment threshold and its rarity; no minimum, so a weak hit can give 0 stacks even with 100% chance to Fortify", source: "wiki Fortification rev 1698776 (page text, patch 3.29): 'Entities inherently have 1% less damage taken from hits per stack of Fortification. By default, it has a maximum of 20 stacks and lasts 6 seconds.' / 'There is no minimum number of stacks; insufficient damage can cause a hit to grant 0 stacks, even with 100% chance to Fortify.'"}
  - {text: "one hit per 0.1 s can add stacks; each instance lasts the default duration without refreshing others; instances are tracked even at the maximum, up to 100", source: "wiki Fortification rev 1698776: 'You can only gain Fortification stacks from one hit every 0.1 seconds, and each instance of stacks gained lasts for the default Fortification duration without refreshing any other instance.' / 'Up to 100 instances of Fortification can be tracked this way.'"}
  - {text: "Fortification reduces damage taken from Hits (the wiki text names hits only) and is not scaled by Buff Effect; the 'less damage taken' multiplier comes after armour, resistances and endurance charges", source: "wiki Fortification rev 1698776: '#% less Damage taken modifiers are calculated after armour, resistances, and endurance charges.' / 'increasing Buff Effect (with Ichimonji) has no effect on Fortification.'"}
  - {text: "version history: 3.16.0 rework (stacks from % of ailment threshold dealt, 1% per stack, 5 s, one hit per 0.1 s); 3.17.0 stack generation ignores the target's damage reduction; 3.19.0 roughly twice the stacks per hit and base duration 6 s", source: "wiki Fortification rev 1698776 version history (3.16.0, 3.17.0, 3.19.0)"}
  - {text: "Fortify Support requires a melee attack skill that is not triggered", source: "Data/Skills/sup_str.lua:2624-2629"}
uptime:
  Mapping:       {value: model, config: {buffFortification: "true for any melee Fortify source in the build (PoB then takes maximum stacks)", overrideFortification: "set to the modelled stacks when below maximum"}, reasoning: "packs give many hits, so a high-chance or 100% source reaches the cap quickly; the stacks per hit are undocumented, so PoB's maximum is an upper bound and the real value is not derivable from sources", source: "wiki Fortification rev 1698776; Modules/CalcPerform.lua:664, 675"}
  Pinnacle Boss: {value: model, config: {buffFortification: "true if melee hits land continuously; phases without melee hits drop to 0 after 6 s"}, reasoning: "wiki: Fortification generation against magic, rare and unique monsters is increased (a unique boss can give more stacks per hit than a normal monster), but only for melee hits that Fortify; spell and projectile builds get nothing", source: "wiki Fortification rev 1698776; TreeData/3_29/tree.lua:45222-45223"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Fortification (rev 1698776)", kind: wiki, patch: "3.29"}
  - {ref: "https://www.poewiki.net/wiki/Fortify_Support (rev 1681881)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Modules/CalcPerform.lua:645-678, 653-671, CalcSetup.lua:78-79, 622, ConfigOptions.lua:1039-1044, ModParser.lua:499-501, 2592-2595, 5627, Data.lua:253, Data/Misc.lua:145", kind: pob, patch: "3.29"}
  - {ref: "PoB Data/Skills/sup_str.lua:2622-2653, act_str.lua:12482-12511, Data/SkillStatMap.lua:697-702, TreeData/3_29/tree.lua:18370, 32628, 32655, 45173, 45211, Data/Uniques/{belt,gloves,amulet,body}.lua", kind: pob, patch: "3.29"}
not_verified:
  - "the stack-count formula per hit (wiki: depends on damage, ailment threshold and rarity; no numbers); the model above can only bound it"
  - "Fortify Support values (10% more melee damage at L1) come from PoB data only; the wiki gem page was fetched (rev 1681881) but its stat text was not read"
  - "whether the Fortify Support gem should set Condition:Fortified in PoB (observed: it does not; a config tick or another Fortify line is needed)"
  - "which seeds (EK, Worb, FR) have a melee Fortify source: none read; Cyclone-based EK would need the gem on a non-triggered Cyclone"
  - "The Celestial Brace: wiki lists +12 maximum Fortification when corrupted; PoB line is +(1-10) (corruption outcome not in PoB data)"
open_questions:
  - "Should the generator tick buffFortification for a melee build with a Fortify source and use the PoB maximum, or model stacks once a source for the per-hit formula exists? (suggested: tick, flag as an upper bound)"
```
