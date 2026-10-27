---
type: gap
status: draft
source: "poewiki Chaos Inoculation rev 1634768, Low life rev 1596639 (re-fetched 2026-10-26); PoB 2.67.2 Modules/CalcPerform.lua:560-571; vault Interactions Chaos Inoculation, Pain Attunement (task 027 batch 3)"
last_confirmed_patch: "3.29.x"
---

# CI plus Life reservation: PoB sets Low Life, the game does not (gap, prose only, no mod pattern)

**What PoB does.** The reservation block sets `Low<pool>` from the unreserved share: `if (max - reserved) / max <= (lowPerc > 0 and lowPerc or data.misc.LowPoolThreshold) then condList["Low"..pool] = true` (`CalcPerform.lua:570-571`). With Chaos Inoculation Life is 1 (`CalcPerform.lua:82-86`), and `reserved = ... m_ceil(max * percent / 100)` (`CalcPerform.lua:562`) rounds any Life reservation up to at least 1, so `(1 - 1) / 1 = 0 <= threshold` and PoB sets `Condition:LowLife` while `Condition:FullLife` stays true. Measured on the Fireball seed with CI plus the custom line 'Reserves 1% of Life': Pain Attunement then adds +26.5% (CombinedDPS 285468 -> 361063) ([[Chaos Inoculation]]).

**What the wiki says.** "Low life conditions will never take effect while CI is enabled. Effects such as Pain Attunement and On Low Life mods on gear will not activate" (Chaos Inoculation rev 1634768), "The only way to achieve Low Life while Chaos Inoculation is allocated is with Coward's Legacy, as a maximum life of 1 counts as being on full life" (Low life rev 1596639). The same page says skills linked to Lifetap or Arrogance, or taken with Blood Magic, "cannot be cast", so a CI build cannot reserve Life in the first place.

**Consequence.** Any "on Low Life" bonus (Pain Attunement, 'while on Low Life' item and jewel lines) that PoB credits to a CI build through a Life reservation is a phantom. The only real Low Life with CI is Coward's Legacy (PoB models it as `Condition:LowLife` only while `AffectedByVulnerability`, see [[Chaos Inoculation]]).

**Rule for the generator and the audit:** with Chaos Inoculation allocated, treat any DPS or defence gain that depends on `Condition:LowLife` as unreal unless Coward's Legacy is equipped, and never let the search add a Life reservation to unlock one. Unverified in the game (the wiki is the only source; PoB's number is a code-reading plus one headless run).

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap sits in the build state (CI plus a reservation), not in a mod line.
