---
type: gap
status: draft
source: "PoB 2.67.2 Data/ModCache.lua lines cited below; per-line probe NodeAdditionOrReplacementFromString over the legion node lines (task 027 batch 4c, item-analyst); vault Interaction note Timeless jewels"
last_confirmed_patch: "3.29.x"
---

```gap
# Lines that timeless jewels put on conquered tree nodes (conqueror keystones, extra notable lines) and that PoB parses to nothing or only in part.
# They are node lines, not item text: the audit's item-text patterns never see them; read them from the allocated node list.
# The audit shows them as "can't measure - check yourself", never as wasted. The probe joins multi-line keystones, so a few may be mis-sorted.
patterns:
  - { match: "Gain Power Charges instead of Frenzy Charges", why: "Inner Conviction (Militant Faith, Dominus): PoB has no mods for this line; PoB keeps its Frenzy Charge count, the 3% more Spell Damage per Power Charge line is parsed" }
  - { match: "Nearby Allies and Enemies Share Charges with you", why: "Supreme Grandstanding (Elegant Hubris, Victario): no mods in ModCache" }
  - { match: "Enemies' Damage with Critical Strikes against you is Lucky", why: "Dance with Death (Brutal Restraint, Asenath): no mods in ModCache" }
  - { match: "Blind does not affect your Light Radius", why: "Second Sight (Brutal Restraint, Nasima): no mods in ModCache" }
  - { match: "Energy Shield starts at zero", why: "Immortal Ambition (Glorious Vanity, Ahuana): no mods in ModCache for this line (probe)" }
  - { match: "Does not delay Inherent Loss of Rage", why: "Chainbreaker (Lethal Pride, Akoya): partly parsed (probe)" }
  - { match: "chance to gain a Frenzy Charge on Hit", why: "Elegant Hubris notable: PoB has no mods for this line" }
  - { match: "chance to gain a Power Charge on Critical Strike", why: "Elegant Hubris notable: PoB has no mods for this line" }
  - { match: "Endurance Charge every second if you've been Hit Recently", why: "Elegant Hubris notable: PoB parses it to an empty mod list" }
  - { match: "chance to gain a Frenzy Charge on Kill", why: "Brutal Restraint addition: PoB has no mods for this line" }
  - { match: "chance to gain an Endurance Charge on Kill", why: "Lethal Pride addition: PoB has no mods for this line" }
  - { match: "chance to Intimidate Enemies for 4 seconds on Hit", why: "Lethal Pride addition: PoB parses it to an empty mod list; PoB takes Intimidate from config only" }
  - { match: "chance to Blind Enemies on Hit", why: "Glorious Vanity notable: PoB parses it to an empty mod list; PoB takes Blind from config only" }
```

**Evidence per pattern (PoB source lines, kept out of the player text; moved 2026-10-26, task 027 merge).**
- "Gain Power Charges instead of Frenzy Charges": Data/ModCache.lua:16163 mods nil; ModCache.lua:8049
- "chance to gain a Frenzy Charge on Hit": Data/ModCache.lua:3696 mods nil
- "chance to gain a Power Charge on Critical Strike": Data/ModCache.lua:5184 mods nil
- "Endurance Charge every second if you've been Hit Recently": Data/ModCache.lua:15646 mods empty
- "chance to gain a Frenzy Charge on Kill": Data/ModCache.lua:9875 mods nil
- "chance to gain an Endurance Charge on Kill": Data/ModCache.lua:9879 mods nil
- "chance to Intimidate Enemies for 4 seconds on Hit": Data/ModCache.lua:3635 mods empty
- "chance to Blind Enemies on Hit": Data/ModCache.lua:9848 mods empty

Interaction note: [[Timeless jewels]]. Counts of non-full lines per conqueror type (replacement nodes / additions, ranges at their minimum): eternal 6 of 56, kalguur 7 of 49, karui 1 of 12 / 2 of 27, maraketh 2 of 11 / 2 of 27, templar 1 of 22 / 0 of 2, vaal 2 of 119 / 0 of 38. PoB paths are relative to the PoB Community install folder.
