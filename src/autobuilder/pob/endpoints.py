"""The names of the Lua functions src/ may call (docs/ARCHITECTURE.md, "Endpoints").

Each name is registered once in Lua with Rpc.register and listed in docs/ARCHITECTURE.md; tools/checks/lua_rules.py
checks the three agree, and tests/autobuilder/pob/test_every_endpoint_restores.py runs every endpoint that changes
state and checks the build is the same afterwards.
"""

from enum import StrEnum


class Endpoint(StrEnum):
    """Empty until milestone 1 adds the first endpoint."""


class ChangeKind(StrEnum):
    """Reversible changes to a build in memory (the "recalculate with the target's setting" button, decision 011).

    Empty until milestone 1 adds the first one; tests/autobuilder/compare/test_recalc_matches_apply.py runs each.
    """
