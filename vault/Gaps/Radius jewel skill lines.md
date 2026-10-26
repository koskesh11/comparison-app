---
type: gap
status: draft
source: "PoB 2.67.2 Data/Uniques/jewel.lua parsed through ModParser (task 027 batch 4c, a3_unparsed.py: 62 lines with leftover text on radius uniques); poewiki Ring of Blades rev 1553488"
last_confirmed_patch: "3.29.x"
---

Radius uniques whose second line changes a skill ("With at least 40 Dexterity in Radius, Barrage fires an additional 6 projectiles") or grants charges are only partly parsed: PoB reads the attribute threshold but leaves the skill text as leftover, so the audit would show them as wasted when they are not. They are listed in [[Radius jewels]] (unparsed). Ring of Blades (Ethereal Knives in a circle) was removed from the game in 3.20.0 and is not a provider.

```gap
# PoB leaves the skill text of these radius-jewel lines unparsed (substring match, case-insensitive).
# The audit shows them as "can't measure, check yourself", never as wasted.
patterns:
  - { match: "Strength in Radius,",             why: "radius jewel skill modifier (Rapid Expansion, Wildfire, The Vigil, Divine Inferno, Winter Burial, Shattered Chains): the skill text after the threshold is not parsed (PoB 2.67.2)" }
  - { match: "Dexterity in Radius,",            why: "radius jewel skill modifier (Volley Fire, Spirit Guards, Steel Spirit, Might and Influence, Growing Agony, Ring of Blades): the skill text is not parsed" }
  - { match: "Intelligence in Radius,",         why: "radius jewel skill modifier (Hazardous Research, Dead Reckoning, Frozen Trail, The Long Winter, Violent Dead, Winter's Bounty): the skill text is not parsed" }
  - { match: "total Dexterity and Strength in Radius", why: "Combat Focus: Prismatic Skills cannot choose an element; not parsed" }
  - { match: "total Intelligence and Dexterity in Radius", why: "Combat Focus: not parsed" }
  - { match: "total Strength and Intelligence in Radius", why: "Combat Focus: not parsed" }
  - { match: "Notables Allocated in Radius",    why: "Inspired Learning: gain a rare monster modifier on kill; not parsed" }
  - { match: "also grant an equal chance to gain", why: "The Blue/Red/Green Dream and Nightmare: the charge-on-kill half is not parsed (the resistance half is)" }
```
