"""The names of the Lua functions src/ may call (docs/ARCHITECTURE.md, "Endpoints").

Each name is registered once in Lua with Rpc.register and listed in docs/ARCHITECTURE.md; tools/checks/lua_rules.py
checks the three agree, and tests/comparison_app/pob/test_every_endpoint_restores.py runs every endpoint and checks the
build is as it should be afterwards, by its effect.
"""

from collections.abc import Mapping
from enum import StrEnum


class Endpoint(StrEnum):
    BUILD_LOAD = "build.load"
    BUILD_SUMMARY = "build.summary"
    BUILD_STATE = "build.state"
    ANALYSIS_SUMMARY = "analysis.summary"
    ANALYSIS_CHAIN = "analysis.chain"
    TARGET_LOAD = "target.load"
    TARGET_RELEASE = "target.release"
    COMPARE_SNAPSHOT = "compare.snapshot"
    COMPARE_CHAIN_WITH = "compare.chain_with"
    BUILD_STAGES = "build.stages"
    BUILD_SET_STAGE = "build.set_stage"


class Effect(StrEnum):
    """What an endpoint does to the loaded build."""

    READ = "read"  # changes nothing
    TEMPORARY = "temporary"  # changes the build, reads, and undoes the change before it returns, also on error
    REPLACE = "replace"  # replaces the loaded build; after a failed load no build is loaded
    TARGET = "target"  # loads or releases the target build beside it; the loaded build is unchanged
    SWITCH = "switch"  # puts the loaded build on another stage; switching back to the saved stage gives the state back


EFFECTS: Mapping[Endpoint, Effect] = {
    Endpoint.BUILD_LOAD: Effect.REPLACE,
    Endpoint.BUILD_SUMMARY: Effect.READ,
    Endpoint.BUILD_STATE: Effect.READ,
    Endpoint.ANALYSIS_SUMMARY: Effect.TEMPORARY,
    Endpoint.ANALYSIS_CHAIN: Effect.TEMPORARY,
    Endpoint.TARGET_LOAD: Effect.TARGET,
    Endpoint.TARGET_RELEASE: Effect.TARGET,
    Endpoint.COMPARE_SNAPSHOT: Effect.READ,
    Endpoint.COMPARE_CHAIN_WITH: Effect.TEMPORARY,
    Endpoint.BUILD_STAGES: Effect.READ,
    Endpoint.BUILD_SET_STAGE: Effect.SWITCH,
}


class ChangeKind(StrEnum):
    """Reversible changes to a build in memory (the "recalculate with the target's setting" button, decision 011).

    Each is one field PoB saves and loads (SkillsTab.lua:447-513; pob/lua/compare/changes.lua);
    tests/comparison_app/compare/test_recalc_matches_apply.py runs each (M7).
    """

    SKILL_PART = "gem.skill_part"  # a gem's skill part (Winter Orb channelling or release)
    STAGE_COUNT = "gem.stage_count"
    MINE_COUNT = "gem.mine_count"
    MINION = "gem.minion"  # which minion a gem summons
    MINION_SKILL = "gem.minion_skill"
    GEM_COUNT = "gem.count"  # a gem's count in Full DPS
    GROUP_COUNT = "group.count"  # a group's count in Full DPS (Calcs.lua:119-120)
    MAIN_ACTIVE_SKILL = "group.main_active_skill"  # the group's active skill the sidebar shows
    MAIN_GROUP = "build.main_group"  # the sidebar's main skill group
    STAGE = "build.stage"  # a stage (PoB loadout): tree, items, skills and config switched together (decision 026)
