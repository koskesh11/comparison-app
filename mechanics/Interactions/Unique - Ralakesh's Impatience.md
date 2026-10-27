---
type: interaction
status: draft
pob_refs: [HaveMaximumFrenzyCharges, FrenzyCharges, FrenzyChargesMax, MovementSpeed, ElementalResist, ColdResist, ChaosResist, TotalDPS, TotalEHP, useFrenzyCharges]
source: "CoC EK Assa.xml item id 26 (boots, PoB 2.67.2, game 3.29), headless removal and per-line probes (tasks/reports/027-evidence/partial/b2c/item-analyst-ek.md); PoB Data/ModCache.lua:14797, CalcPerform.lua:1109-1111, Data/Uniques/boots.lua:921-933, Data/Vestigial.lua:888-896; poewiki Ralakesh's Impatience rev 1674049"
last_confirmed_patch: "3.29.x"
---

Ralakesh's Impatience (Frenzy variant) makes the game count the character as holding the maximum number of Frenzy charges. In the EK seed this is the item that makes the third charge type real: Power and Endurance are ticked in config and Frenzy cannot be gained (Inner Conviction turns Frenzy gains into Power), so the boots carry 35.2% of FullDPS (7 charges at 4% more each) plus movement speed and resistances.
In PoB the line equals ticking useFrenzyCharges, so PoB cannot tell the two apart; the 35.2% is a headless delta, the game fact comes from the item (corrupted boots, Frenzy variant line) and the wiki.

Pipeline: [[Damage calculation#More and less]] - the counted Frenzy charges feed the per-charge 4% more multiplier.

```interaction
id: unique-ralakeshs-impatience
mechanic: "Unique package: Ralakesh's Impatience (Frenzy variant) counts the character as having maximum Frenzy charges, which carries the per-charge more damage in the EK seed, plus movement speed, three resistance lines and Corrupted Blood immunity"
family: charge
target: self
pipeline_step: ["Damage calculation#More and less"]
pipeline_why: "the flag sets the Frenzy charge count to its maximum (CalcPerform.lua:1109-1111) and the count feeds the 4% more damage per charge multiplier"
related: [frenzy-charges, power-charges, endurance-charges, chaos-inoculation, bleed-poison-cb-immunity, max-resistances, unique-badge-of-the-brotherhood]
pob:
  measured: full
  how: "Flag HaveMaximumFrenzyCharges (ModCache.lua:14797, ModParser.lua:5267); CalcPerform.lua:1109-1111 sets output.FrenzyCharges = FrenzyChargesMax. Same effect as ticking useFrenzyCharges (ConfigOptions.lua:906). Seed measurement (headless, in memory): whole removal FullDPS -35.208% (9,807,398), main TotalDPS -21.936% (6,033,146 = 1/1.28), Frenzy current 7 -> 0 (max stays 7), MS x1.561 -> x1.393, Cold 75 -> 53, Chaos -43 -> -60, TotalEHP 145,259 -> 126,341 (-13.0%). Corrupted Blood immunity: PoB has no Corrupted Blood damage model, nothing measured"
  config:
    - {var: useFrenzyCharges, default: false, ref: "Modules/ConfigOptions.lua:906", class: c}
  unparsed: []
model: null
providers:
  - {kind: unique, name: "Ralakesh's Impatience", variant: "Frenzy Current (PoB variant 4 text)", slot: boots, role: enables, target: self, text: "Count as having maximum number of Frenzy Charges", source: "Data/ModCache.lua:14797; ModParser.lua:5267; CalcPerform.lua:1109-1111; Data/Uniques/boots.lua:921-933", pob: full}
  - {kind: unique, name: "Ralakesh's Impatience", variant: "Frenzy Current", slot: boots, role: sustains, target: self, text: "24% increased Movement Speed", source: "live parse MovementSpeed INC 24 (not in ModCache); removal of the whole item MS x1.561 -> x1.393", pob: full}
  - {kind: unique, name: "Ralakesh's Impatience", variant: "corruption implicit", slot: boots, role: sustains, target: self, text: "+14% to all Elemental Resistances", source: "Data/ModCache.lua:620; per-line probe: no change (Fire/Lightning over cap, Cold still capped)", pob: full}
  - {kind: unique, name: "Ralakesh's Impatience", variant: "Frenzy Current", slot: boots, role: sustains, target: self, text: "+24% to Cold Resistance", source: "Data/ModCache.lua:1160; per-line probe: Cold 75 -> 67, TotalEHP -4.8%", pob: full}
  - {kind: unique, name: "Ralakesh's Impatience", variant: "Frenzy Current", slot: boots, role: sustains, target: self, text: "+17% to Chaos Resistance (Chaos Inoculation: chaos hits cannot hurt, Life 1)", source: "Data/ModCache.lua:768; per-line probe: Chaos -43 -> -60, no EHP change", pob: full}
  - {kind: unique, name: "Ralakesh's Impatience", variant: "Frenzy Current", slot: boots, role: blocks, target: self, text: "Corrupted Blood cannot be inflicted on you", source: "Data/ModCache.lua:14790 (flag CorruptedBloodImmune); no PoB damage model", pob: partial}
package:
  seed: "CoC EK Assa.xml (PoB 2.67.2, game 3.29), item set 1"
  slot: Boots
  base: "NOT VERIFIED (sockets B-R-W-W, base Armour 71, ES 15, item level 85, requirement level 36 are in the evidence; the base name is not)"
  xml_item_id: 26
  variant: "Frenzy Current (PoB variant 4 text); corrupted (implicit +14% all elemental resistances); not Foulborn"
  removal: "FullDPS -35.208% (15,136,639 -> 9,807,398), main TotalDPS -21.936%, TotalEHP -13.0% - in-memory removal; PoB keeps the emptied slot's gems active, so the in-game loss is larger (4 sockets with 3 enabled gems)"
  lost_with_item:
    - "Frenzy current 7 -> 0 (the whole DPS value; equals unticking useFrenzyCharges)"
    - "Sockets B-R-W-W with Cast when Damage Taken 14, More Duration 18, Vulnerability 20 (Steelskin 18 is disabled in the seed): in game these gems lose their sockets, PoB keeps them active"
    - "Movement Speed x1.561 -> x1.393; Cold 75 -> 53; Chaos -43 -> -60; ES 5189 -> 5158; Armour 658 -> 556; conditions UsingBoots / UniqueItemInBoots; CorruptedItem count 2 -> 1"
  downsides_that_are_the_point: []
  foulborn: "none: no Ralakesh key in Data/ModFoulbornMap.jsonc and no Foulborn section in wiki rev 1674049. Related lead, not Foulborn: Data/Vestigial.lua:888-896 lists DivergentMinimumFrenzyChargesUnique__1 '+3 to Minimum Frenzy Charges' (Data/ModItemExclusive.lua:8525) as a vestigial implicit sourced from Ralakesh, selectable only on boots (Modules/AddImplicitPopup.lua:123-134); real minimum Frenzy charges would not be blocked by Inner Conviction. How a player gets a vestigial implicit: NOT VERIFIED"
  obtainability: "poewiki Ralakesh's Impatience rev 1674049 (patch 3.29): introduced 3.1.0; 3.26.0 version row: one of Endurance / Frenzy / Power 'Count as having maximum', 15-25% increased Movement Speed, Corrupted Blood immunity ('Existing versions unaffected'); legacy variants Pre 3.19 / Pre 3.26 differ (PoB Data/Uniques/boots.lua:921-933 variants 1-5). No drop restriction key in the wikitext (the Item acquisition template did not expand): drop source NOT VERIFIED. The seed copy is corrupted, so trade-only as a corrupted copy"
makes_redundant:
  - {provider: "Other Frenzy charge sources", when: "Ralakesh's Impatience is worn", why: "the flag already counts the maximum; the Badge is still needed to lift the maximum itself (the vault Frenzy charges note says the same)", source: "Frenzy charges note; item-analyst-ek.md"}
  - {provider: "Config box useFrenzyCharges", when: "Ralakesh's Impatience is worn", why: "in PoB the box and the flag give the same Frenzy count; the box stays unticked in the seed, which is consistent", source: "CalcPerform.lua:1109-1111; ConfigOptions.lua:906"}
conflicts:
  - {with: "Real charge gain and loss", effect: "Ralakesh does not stop real charge gain or loss, it only counts (wiki Ralakesh rev 1674049: 'Effects that rely on ... at maximum ... are always enabled')", source: "poewiki Ralakesh's Impatience rev 1674049"}
conditions:
  - {text: "The maximum itself comes from the tree and from the Badge of the Brotherhood (Frenzy maximum 3 -> 7); with Ralakesh but no Badge the count is the 3 maximum", source: "unique-badge-of-the-brotherhood matrix (eval3b): no Badge with Ralakesh 11.942M FullDPS"}
  - {text: "The Frenzy variant fits this build because the seed already assumes Power (usePowerCharges) and Endurance (useEnduranceCharges) at max by config, and Frenzy cannot be gained for real (Inner Conviction, node 12128); the Power or Endurance variants add 0 in PoB with those boxes ticked (but would be the real source of those charges)", source: "item-analyst-ek.md"}
uptime:
  Mapping:       {value: always, config: {}, reasoning: "the flag is permanent; no chance-based effect, no config box for it (the equivalent box useFrenzyCharges stays unticked)", source: "poewiki Ralakesh rev 1674049; CalcPerform.lua:1109-1111"}
  Pinnacle Boss: {value: always, config: {}, reasoning: "same as Mapping", source: "poewiki Ralakesh rev 1674049"}
seeds: [EK]
sources:
  - {ref: "https://www.poewiki.net/wiki/Ralakesh%27s_Impatience (rev 1674049)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Data/ModCache.lua:14797, Modules/CalcPerform.lua:1109-1111, Data/Uniques/boots.lua:921-933, Data/Vestigial.lua:888-896", kind: pob, patch: "3.29"}
  - {ref: "headless probes on CoC EK Assa.xml, PoB 2.67.2 (tasks/reports/027-evidence/partial/b2c/item-analyst-ek.md)", kind: pob, patch: "3.29"}
not_verified:
  - "NOT VERIFIED: drop source of Ralakesh's Impatience"
  - "NOT VERIFIED: whether any enemy in the intended content applies Corrupted Blood (PoB has no model for it)"
  - "NOT VERIFIED: how a player gets a vestigial implicit (the +3 minimum Frenzy charges lead)"
  - "NOT VERIFIED: the boots base name"
open_questions:
  - "Is the +3 minimum Frenzy charges vestigial implicit something the generator may use on other boots, or is the unique's Frenzy line the only accepted source?"
```
