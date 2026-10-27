---
type: interaction
status: draft
pob_refs: [SelfAurasOnlyAffectYou, ManaReserved, ManaReservedPercent, ManaUnreserved, AuraEffect, PhysicalDamageTaken, CombinedDPS, FullDPS, TotalEHP, EnergyShield, enemyIsBoss]
source: "poewiki Supreme Ego rev 1659207 (fetched 2026-10-26; version history ends 3.18.1c, text equals tree.lua); PoB 2.67.2 CalcPerform.lua / ModStore.lua / ModParser.lua / Data/ModCache.lua / TreeData 3_29; headless runs on EK, FR and the Fireball seed (scratchpad b3c/F_run.py, F_pride.py, evidence b3c/tree-ascendancy-analyst-F.md)"
last_confirmed_patch: "3.29.x"
---

Supreme Ego (keystone, node 49639, TreeData/3_29/tree.lua:67418-67422) has three lines: "Auras from your Skills can only affect you", "Aura Skills have 1% more Aura Effect per 2% of maximum Mana they Reserve" and "40% more Mana Reservation of Aura Skills". It is a single-big-aura keystone: it pays when one or two auras reserve a large share of your mana and nothing else needs the aura to hit enemies or allies. It costs 40% more mana on every aura and removes every aura effect that is aimed at enemies or allies. On the seeds it is a large loss on EK (-48.2% DPS, Pride and Flesh and Stone stop debuffing enemies, and the build is over-reserved), small on FR (+1.3% ES, over-reserved by 122 mana) and a gain on the Fireball seed (+8.2% DPS with a single Anger aura). Related: [[Defences]], [[Damage calculation]].

Pipeline: [[Damage calculation#Damage taken]] - PoB applies Pride's and Flesh and Stone's enemy effects as PhysicalDamageTaken MORE on the enemy; Supreme Ego sets those to 0, so the damage-taken step loses them and the hit damage multiplier of the build falls. The self-side aura effect (Clarity, Discipline, Anger) is multiplied by AuraEffect MORE in the aura buff step.

How PoB applies it: three lines are parsed separately - SelfAurasOnlyAffectYou flag (Data/ModCache.lua:14313), AuraEffect MORE 1 with PerStat ManaReservedPercent div 2 gated to Aura skills (ModCache.lua:14295) and ManaReserved MORE 40 gated to SkillType 39 = Aura (ModCache.lua:9427; Data/Global.lua:257). The per-skill percent is ModStore:GetStat('ManaReservedPercent') = floor(ManaReservedBase / Mana x 100) for the aura's own reservation, capped at 100 (Classes/ModStore.lua:317-330); the PerStat tag floors base/2 (ModStore.lua:481-505), so a 41% reservation gives 20% more effect. Enemy auras: CalcPerform.lua:2549, 2620, 2963 skip the debuff when SelfAurasOnlyAffectYou is set; minion and ally sharing is skipped at CalcPerform.lua:2478, 2855, 3233.

Measured (headless, in memory, nothing saved; keystone only - node 49639 force-allocated alone, path cost not included; enemy level from the headless run: 85 at None, 84 at Pinnacle; the numbers below are the same at both presets unless stated):

| Seed | aura reservation (mana) before -> after | aura effect | unreserved mana | main outputs |
|---|---|---|---|---|
| EK (Mana 1201) | Flesh and Stone 195 -> 272, Pride 355 -> 496, Clarity 156 -> 218 | +11%, +20%, +9% (Clarity); Pride and Flesh and Stone enemy effect 52 and 27 -> 0 | 107 -> -174 (needs 1375 of 1201) | CombinedDPS 14370752 -> 7445986 (-48.2%, None), 15084434 -> 7815769 (-48.2%, Pinnacle); TotalEHP unchanged |
| FR (Mana 523) | Precision 19 -> 26, Discipline 127 -> 177, Flesh and Stone 91 -> 127, Purity of Lightning 87 -> 121 | +2%, +16%, +12%, +11% | 6 -> -122 (needs 645 of 523) | ES 17116 -> 17339 (+1.3%), TotalEHP 102318 -> 103929 (+1.6%, None) and 273342 -> 277955 (+1.7%, Pinnacle), FullDPS +1.0%, CombinedDPS unchanged |
| Fireball seed (NOT VIABLE, Mana 1689) | Anger 783 -> 1095 (46.3% -> 64.8% of mana) | +32% | 906 -> 594 | CombinedDPS 390510 -> 422667 (+8.2%) and 285468 -> 309013 (+8.2%); TotalEHP 7806 -> 7280 (-6.7%) and 12065 -> 11252 (-6.7%) |

- EK: the enemy effects are PhysicalDamageTaken MORE 52 (Pride) and 27 (Flesh and Stone) on the enemy in the base build; with the keystone both entries read 0 (modDB dump, F_pride.py). 1 / (1.52 x 1.27) = 0.518 matches the -48.2%. Herald of Purity is not an Aura-tagged skill: its reservation (388 of the 1094) is not scaled. Clarity's mana regeneration rises 41.6 -> 45.3.
- Over-reservation: PoB still applies every aura when ManaUnreserved is negative (FR ES grew with unreserved -122); ManaReserved prints capped at the pool (EK 1201). In the game the last auras would not stay on; the number of auras that fit was not modelled. The keystone alone leaves both seeds unplayable until the reservation falls by 174 mana (EK, 12.7% of the 1375 needed) and 122 mana (FR, 18.9% of the 645 needed).
- Fireball seed: the unreserved mana is the Mind Over Matter pool (312 mana less: 906 -> 594), which is consistent with the -6.7% EHP; this attribution is an inference from the output.
- FR FullDPS +1.0% was not traced to a source (CombinedDPS unchanged).

```interaction
id: supreme-ego
mechanic: "Auras from your Skills can only affect you (no allies, minions, or enemies, so Pride, Flesh and Stone, curse auras and mine auras stop affecting enemies); Aura Skills have 1% more Aura Effect per 2% of maximum Mana they Reserve (per aura, own reservation); 40% more Mana Reservation of Aura Skills"
family: buff
target: self
related: [defences, damage-calculation, receiving-damage]
pipeline_step: ["Damage calculation#Damage taken", "Damage calculation#More and less"]
pipeline_why: "Enemy-aimed auras such as Pride and Flesh and Stone act on the enemy's damage taken (PoB: PhysicalDamageTaken MORE 52 and 27 on the enemy); Supreme Ego sets them to 0, which is a loss in the damage-taken step; the self-aimed auras get AuraEffect MORE (1% per 2% of the aura's own reservation) as a more multiplier on their buff values, at the price of ManaReserved MORE 40."
pob:
  measured: full
  how: "Data/ModCache.lua:14313 (SelfAurasOnlyAffectYou flag), 14295 (AuraEffect MORE 1 per 2% ManaReservedPercent, Aura skills), 9427 (ManaReserved MORE 40, SkillType 39 = Aura); Classes/ModStore.lua:317-330 (per-skill ManaReservedPercent, floored, capped 100), 481-505 (PerStat floor); Modules/CalcPerform.lua:2478, 2549, 2620, 2855, 2963, 3233 (SelfAurasOnlyAffectYou gates); Modules/CalcPerform.lua:2005-2008, 2040-2065 (reservation more/inc and ManaReservedBase). Measured headless on EK, FR, Fireball seed (node 49639 alone, None and Pinnacle): EK CombinedDPS -48.2% (Pride 52 and Flesh and Stone 27 PhysicalDamageTaken MORE on the enemy go to 0), unreserved -174; FR ES +1.3%, TotalEHP +1.6% / +1.7%, unreserved -122; Fireball Anger +32% effect, CombinedDPS +8.2%, EHP -6.7%. Not modelled: aura shut-off when over-reserved, Skitterbot and Blasphemy curse-aura behaviour, rounding of the 40% more (wiki: rounding down)."
  config:
    - {var: enemyIsBoss, default: "Pinnacle (list index 3)", ref: "Modules/ConfigOptions.lua:2086 (enemy level; the aura numbers are identical at None and Pinnacle)", class: b}
  unparsed: []
model: null
providers:
  - {kind: keystone, name: "Supreme Ego 49639", slot: tree, role: enables, target: self, text: "Auras from your Skills can only affect you; Aura Skills have 1% more Aura Effect per 2% of maximum Mana they Reserve; 40% more Mana Reservation of Aura Skills", source: "TreeData/3_29/tree.lua:67418-67422; Data/ModCache.lua:9427, 14295, 14313; Modules/ModParser.lua:4041", pob: full}
  - {kind: tattoo, name: "Supreme Ego tattoo (keystone tattoo)", slot: tree, role: enables, target: self, text: "replaces a tree node with the Supreme Ego keystone (Limited to 1 Keystone Tattoo)", source: "Data/TattooPassives.lua:3006-3010", pob: full}
  - {kind: jewel, name: "Elegant Hubris (legacy variant Chitus, Pre 3.11.0)", slot: jewel, role: enables, target: self, text: "Commissioned (2000-160000) coins to commemorate Chitus grants the keystone; wiki: the legacy jewel version equals the tree keystone", source: "Data/Uniques/jewel.lua:1852-1858; wiki Supreme Ego rev 1659207", pob: partial, variant: "Pre 3.11.0"}
  - {kind: mod, name: "Crucible weapon tree and Hellscape upside: Supreme Ego", slot: Weapon, role: enables, target: self, text: "weapon tree keystone and Scourge body armour upside", source: "Data/Crucible.lua:1359; Data/ModScourge.lua:849", pob: full}
  - {kind: mod, name: "Aura effect increases and mores (gems, tree, gear)", slot: any, role: scales, target: self, text: "multiply with the keystone's more term (Anger on the Fireball seed: auraMore 1.32)", source: "Modules/CalcPerform.lua:2462-2463, 2493-2494; headless Fireball seed", pob: full}
  - {kind: support, name: "Enlighten Support", slot: any, role: sustains, target: self, text: "reduces mana reservation of the supported skills; the offset to the 40% more (FR carries Enlighten L3 on Purity of Lightning and Arctic Armour)", source: "Data/Skills/sup_int.lua:2279-2280; FR headless skill listing", pob: full}
  - {kind: mod, name: "Enemy-aimed auras (Pride, Flesh and Stone, curse auras from Blasphemy, mine auras)", slot: any, role: blocks, target: enemy, text: "stop affecting enemies; wiki lists Pride, Flesh and Stone, mine auras and Blasphemy curse auras; measured: Pride and Flesh and Stone enemy PhysicalDamageTaken MORE go to 0", source: "wiki Supreme Ego rev 1659207; Modules/CalcPerform.lua:2549, 2620, 2963; headless EK F_pride.py", pob: full}
  - {kind: mod, name: "Aura sharing with minions, spectres and allies", slot: any, role: blocks, target: self, text: "auras no longer reach minions or allies (PoB skips the ally and minion branches when the flag is set)", source: "wiki Supreme Ego rev 1659207; Modules/CalcPerform.lua:2478, 2855, 3233", pob: partial}
makes_redundant:
  - {provider: "Several small auras (Clarity, Discipline, Purity of Lightning, Precision on FR) and enemy-debuffing auras (Pride, Flesh and Stone on EK)", when: "Supreme Ego allocated", why: "the 40% more reservation makes many auras unaffordable (EK needs 1375 of 1201 mana, FR 645 of 523) and the enemy-aimed ones lose their whole effect; the keystone favours one large aura", source: "headless EK and FR runs; wiki Supreme Ego rev 1659207"}
conflicts:
  - {with: "Pride and Flesh and Stone as damage sources (EK)", effect: "52% and 27% more physical damage taken by enemies both go to 0: -48.2% DPS on EK", source: "headless EK run (F_run.py, F_pride.py)"}
  - {with: "full mana reservation (EK 91.1%, FR 98.9% reserved before the keystone)", effect: "over-reserved by 174 (EK) and 122 (FR) mana; PoB keeps all auras on", source: "headless EK and FR runs; Modules/CalcPerform.lua:564-565"}
  - {with: "Mind Over Matter or any build that needs unreserved mana", effect: "the Fireball seed's unreserved mana falls 906 -> 594 (inferred link to the -6.7% EHP)", source: "headless Fireball seed"}
conditions:
  - {text: "the effect is read per aura: 1% more Aura Effect per 2% of maximum Mana THAT aura reserves, after the 40% more reservation (e.g. Anger 64.8% -> +32%); at most +50% at 100%", source: "Classes/ModStore.lua:317-330, 481-505; headless Fireball seed (getStat 64, auraMore 1.32)"}
  - {text: "40% more reservation applies to aura skills that reserve mana only (Herald skills are not Aura-tagged: Herald of Purity on EK stays at 388); wiki says it rounds down and includes mines", source: "Data/ModCache.lua:9427; headless EK run; wiki Supreme Ego rev 1659207"}
uptime:
  Mapping:       {value: always, config: {enemyIsBoss: "None / map monsters (env.enemyLevel 85 in the headless run)"}, reasoning: "permanent while allocated; the only question is whether the auras still fit in the mana pool; EK -48.2% DPS and over-reserved, FR +1.3% ES and over-reserved, Fireball seed +8.2% DPS", source: "headless EK/FR/Fireball seed"}
  Pinnacle Boss: {value: pob, config: {enemyIsBoss: "Pinnacle (default; env.enemyLevel 84 in the headless run)"}, reasoning: "same aura numbers as at None; EK -48.2% CombinedDPS (15084434 -> 7815769), FR TotalEHP +1.7%, Fireball seed +8.2% DPS and -6.7% EHP", source: "headless EK/FR/Fireball seed"}
seeds: []
sources:
  - {ref: "https://www.poewiki.net/wiki/Supreme_Ego (rev 1659207; last version row 3.18.1c)", kind: wiki, patch: "3.29"}
  - {ref: "PoB Classes/ModStore.lua:317-330, 481-505; Modules/CalcPerform.lua:564-565, 2005-2008, 2040-2065, 2462-2463, 2478, 2493-2494, 2549, 2620, 2855, 2963, 3233; Modules/ModParser.lua:4041; Data/ModCache.lua:9427, 14295, 14313; Data/Global.lua:257; Data/TattooPassives.lua:3006-3010; Data/Uniques/jewel.lua:1852-1858; Data/Crucible.lua:1359; Data/ModScourge.lua:849; Data/Skills/sup_int.lua:2279-2280; TreeData/3_29/tree.lua:67418-67422", kind: pob, patch: "3.29"}
  - {ref: "headless runs EK, FR, Fireball seed (scratchpad b3c/F_run.py, F_pride.py, F_show.py; evidence b3c/tree-ascendancy-analyst-F.md)", kind: discovery, patch: "3.29"}
not_verified:
  - "what the game does when auras no longer fit (which aura switches off); PoB keeps all auras on with a negative unreserved mana"
  - "Skitterbots, Profane Proxy, Blasphemy curse auras and mine auras under the keystone: the wiki describes them; PoB's branches were read, not measured"
  - "rounding of the 40% more reservation (wiki: rounds down); PoB's integer stages (CalcPerform.lua:2040-2065) were not compared line by line"
  - "why FR FullDPS rises 1.0% under the keystone (CombinedDPS unchanged): the contributing skill was not traced"
  - "attribution of the Fireball seed's -6.7% EHP to the smaller Mind Over Matter pool (inference from ManaUnreserved 906 -> 594)"
  - "the FR file ticks summonElementalRelicEnableAngerAura, ...HatredAura and ...WrathAura (headless config dump); whether those relic auras are Aura-tagged skills that reserve mana under the keystone was not checked"
  - "whether the Elegant Hubris legacy variant is still obtainable (wiki says same as the tree keystone)"
  - "enemy level 85 (None) and 84 (Pinnacle) are env.enemyLevel from the headless run; why None is one level higher was not traced"
open_questions:
  - "Should the generator ever take Supreme Ego with more than one aura, or only for a single large aura (Fireball seed style) where the over-reservation test passes?"
```
