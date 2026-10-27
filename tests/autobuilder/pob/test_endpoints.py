"""The endpoint names: unique, written as `layer.name`; tools/checks/lua_rules.py checks Lua and the docs agree."""

import re
from enum import StrEnum

import pytest

from autobuilder.pob.endpoints import ChangeKind, Endpoint

NAME = re.compile(r"^[a-z]+\.[a-z_]+$")


@pytest.mark.parametrize("names", [Endpoint, ChangeKind], ids=["Endpoint", "ChangeKind"])
def test_names_are_unique_and_well_formed(names: type[StrEnum]) -> None:
    values = [member.value for member in names]
    assert len(values) == len(set(values))
    assert [value for value in values if not NAME.match(value)] == []
