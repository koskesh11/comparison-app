---
type: gap
status: draft
source: "poewiki Version 3.28.0; PoB 2.67.2 Data/Gems.lua and changelog.txt; poe.ninja Allflame SkillGem cache (2026-10-21)"
last_confirmed_patch: "3.29.x"
---

```obtainable
# PoB Data/Gems.lua names. The engine reads only allow/deny (gem_key drops " Support", lowercases).
since: "3.28.0"
reason: "All Awakened Support Gems can no longer be obtained, except for Awakened Empower, Awakened Enlighten and Awakened Enhance (wiki Version 3.28.0)"
deny:
  - Awakened Added Fire Damage
  - Awakened Ancestral Call
  - Awakened Brutality
  - Awakened Burning Damage
  - Awakened Elemental Damage with Attacks
  - Awakened Fire Penetration
  - Awakened Generosity
  - Awakened Melee Physical Damage
  - Awakened Melee Splash
  - Awakened Multistrike
  - Awakened Added Cold Damage
  - Awakened Arrow Nova
  - Awakened Cast On Critical Strike
  - Awakened Chain
  - Awakened Cold Penetration
  - Awakened Deadly Ailments
  - Awakened Fork
  - Awakened Greater Multiple Projectiles
  - Awakened Swift Affliction
  - Awakened Void Manipulation
  - Awakened Vicious Projectiles
  - Awakened Added Chaos Damage
  - Awakened Added Lightning Damage
  - Awakened Blasphemy
  - Awakened Cast While Channelling
  - Awakened Controlled Destruction
  - Awakened Hextouch
  - Awakened Elemental Focus
  - Awakened Increased Area of Effect
  - Awakened Lightning Penetration
  - Awakened Minion Damage
  - Awakened Spell Cascade
  - Awakened Spell Echo
  - Awakened Unbound Ailments
  - Awakened Unleash
```

**What changed:** "All Awakened Support Gems can no longer be obtained, except for Awakened Empower, Awakened Enlighten and Awakened Enhance" (poewiki *Version 3.28.0*).

**PoB still has them:** `Data/Gems.lua:11061-11715` lists 38 Awakened gems; the 35 above plus Empower, Enlighten, Enhance (still obtainable, not denied). PoB only hides them from the dropdown: "Hide legacy awakened gems from dropdown" (`changelog.txt:456`, PoB 2.61.0). Paths relative to `%APPDATA%\Path of Building Community`.

**Effect today:** none for Allflame. The poe.ninja cache (`engine/cache/Allflame/SkillGem.json`, 2026-10-21) lists only Awakened Empower / Enhance / Enlighten. The list records why and guards against stale or wrong price data.

**Suggested replacement:** the same gem without "Awakened " (Awakened Greater Multiple Projectiles -> Greater Multiple Projectiles).

**Scope:** challenge league. Legacy copies may still trade in Standard: UNVERIFIED.

**Watch out (CoC):** Awakened Cast On Critical Strike also gives cooldown recovery (`Data/Skills/sup_dex.lua:727-732`). Swapping it for the normal gem can drop the trigger cap; see [[Trigger attack under the CoC cap]]. Cooldown Recovery Support (on the spell) is listed in Allflame: 3/20 uncorrupted, 31 listings, ~2,709 chaos (ninja cache, 2026-10-21).
