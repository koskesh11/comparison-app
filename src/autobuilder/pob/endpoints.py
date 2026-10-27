"""The names of the Lua functions src/ may call (docs/ARCHITECTURE.md, "Endpoints").

Each name is registered once in Lua with Rpc.register and listed in docs/ARCHITECTURE.md; tools/checks/lua_rules.py
checks the three agree, and tests/autobuilder/pob/test_every_endpoint_restores.py runs every endpoint and checks the
build is as it should be afterwards, by its effect.
"""

from collections.abc import Mapping
from enum import StrEnum


class Endpoint(StrEnum):
    BUILD_LOAD = "build.load"
    BUILD_SUMMARY = "build.summary"
    BUILD_STATE = "build.state"
    ANALYSIS_SUMMARY = "analysis.summary"


class Effect(StrEnum):
    """What an endpoint does to the loaded build."""

    READ = "read"  # changes nothing
    TEMPORARY = "temporary"  # changes the build, reads, and undoes the change before it returns, also on error
    REPLACE = "replace"  # replaces the loaded build; after a failed load no build is loaded


EFFECTS: Mapping[Endpoint, Effect] = {
    Endpoint.BUILD_LOAD: Effect.REPLACE,
    Endpoint.BUILD_SUMMARY: Effect.READ,
    Endpoint.BUILD_STATE: Effect.READ,
    Endpoint.ANALYSIS_SUMMARY: Effect.TEMPORARY,
}


class ChangeKind(StrEnum):
    """Reversible changes to a build in memory (the "recalculate with the target's setting" button, decision 011).

    Empty until milestone 1 adds the first one; tests/autobuilder/compare/test_recalc_matches_apply.py runs each.
    """
