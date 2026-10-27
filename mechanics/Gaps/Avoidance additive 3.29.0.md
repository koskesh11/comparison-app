---
type: gap
status: draft
source: "official 3.29.0 patch notes https://www.pathofexile.com/forum/view-thread/3985332 (mechanics-researcher, 027-debuff-uptime.md section 1); poewiki Avoidance rev 1675590 (not re-fetched); PoB 2.67.2 CalcDefence.lua / Data.lua / ModParser.lua (pob-coverage-auditor); mechanics-researcher-receiving-defences.md (Surprises 2)"
last_confirmed_patch: "3.29.x"
---

# Avoid-all damage from hits: wiki says additive since 3.29.0, PoB multiplies (gap, prose only, no mod pattern)

Verdict (task 027, 2026-10-25): the claim HELD but is narrower than first written. Official 3.29.0 notes (https://www.pathofexile.com/forum/view-thread/3985332, "Content Update 3.29.0 - Path of Exile: Curse of the Allflame", HTTP 200 via curl with a browser UA):

> Player Changes: "Sources of chance to Avoid all Damage from Hits are now additive with sources of Avoiding Damage of a specific Type from Hits. Some Damage Avoidance stat descriptions have been adjusted to better communicate these chances are additive with each other."
> Bug Fixes: "Fixed a bug where some sources of chance to Avoid Damage from Hits were not capped at 75%."

The cap line is a separate bug fix for "some sources", not part of the additive change (the old wording "the 75% cap bug was fixed" was too broad). The official text names no damage types and no sources. Wiki Avoidance rev 1675590 was not re-fetched.

PoB 2.67.2 side (pob-coverage-auditor; lines 1689-1693 re-read by interactions-lead): not-hit chance multiplies avoid-all as its own factor in every category (CalcDefence.lua:1689-1693); the per-type damage path is additive min(Avoid<Type> + Projectile, 75) and never reads avoid-all (CalcDefence.lua:2831-2855); each stat is capped at 75 separately (Data.lua:252; CalcDefence.lua:1578, 1583, 1585); projectile avoidance is a not-hit factor only when no per-type avoidance exists (CalcDefence.lua:1576-1581, 1690, 1692); no ModParser line adds avoid-all into the per-type stats (ModParser.lua:386-397). Unverified: how the not-hit chance and the damage path combine into EHP, and the wiki page and 3.29.x hotfix notes.

- A build stacking both kinds may be understated in PoB if the official additive wording applies to avoid-all and the per-type stats it names; PoB may simply lag the 3.29.0 change. This is a conflict, not a proven PoB bug.
- Both readings stay visible; do not pick one silently. Needs an in-game or patch-note check (user).

Linked from: [[Receiving damage#Immunity and avoidance]], [[Defences#Damage avoidance]].

This note has no gap code block on purpose: engine/vault.py loads gap patterns live and this gap has no mod pattern.
