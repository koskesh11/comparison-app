# 012 Builds are pasted; one request per link

- Date: 2026-10-26/27 (grilling rounds 4, 6, 8, 13, 22, 23)
- Decided by: owner; the terms reading by Claude (round 6)
- Status: accepted
- Scope: the importer and every external data source

## Context
poe.ninja's build and character endpoints return full PoB exports, but its API page calls them internal and "not
available for third-party use" (https://poe.ninja/docs/api, read 2026-10-26). PoB itself downloads pobb.in builds from
`pobb.in/pob/<id>` (Modules/BuildSiteTools.lua:29). pobb.in's robots.txt (fetched 2026-10-27) disallows `/pob/` and
`/*/raw$` for crawlers.

## Decision
- The owner pastes a PoB code (for example from poe.ninja's "Copy PoB" button) or a pobb.in link. No automatic
  fetching from poe.ninja.
- A pobb.in link is fetched through PoB's own address `pobb.in/pob/<id>`, one request per pasted link, never in bulk.
- Imported targets are saved to `Builds\AutoBuilder\imports` so the owner can open them in PoB.
- Many-build comparison (later) also works from pasted builds.
- Unique prices, when they come, use poe.ninja's documented economy data; rare prices matter little.

## Consequences
- The app writes only to `Builds\AutoBuilder\`; the PoB install and the owner's builds are read-only (enforced by the
  guard hook and the deny rules in .claude/settings.json).
