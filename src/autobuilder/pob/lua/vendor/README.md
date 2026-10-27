# Vendored from Path of Building

| File | Source | Why |
|---|---|---|
| `_SimpleGraphic.def.lua` | PoB Community, `src/_SimpleGraphic.def.lua`, byte for byte: git blob `6e159e4134eb23c509037380293fb6e3e5b68d64`, last changed upstream in commit `81dbae8465d1c5a17e7494333c2e2da3052cbcf9` (2026-08-23, "Use require for loading more modules (#10267)"); checked with the GitHub API on 2026-10-27, installed PoB 2.67.2 | PoB's runtime API (SimpleGraphic) with headless bodies; the install does not ship it. `boot.lua`, `filesearch.lua` and `sandbox.lua` replace some of its bodies. |

PoB updates itself, so after an update compare the blob with upstream
(`git hash-object _SimpleGraphic.def.lua` against
`https://api.github.com/repos/PathOfBuildingCommunity/PathOfBuilding/contents/src/_SimpleGraphic.def.lua`) and look for
new runtime functions. The upstream headless wrapper this boot follows is `src/HeadlessWrapper.lua` in the same repo.
