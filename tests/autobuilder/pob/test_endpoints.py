"""The endpoint names: unique, written as `layer.name`, each with its effect. tools/checks/lua_rules.py checks that
Lua and the docs agree."""

import re
from enum import StrEnum

import pytest

from autobuilder.pob.endpoints import EFFECTS, ChangeKind, Endpoint

NAME = re.compile(r"^[a-z]+\.[a-z_]+$")


@pytest.mark.parametrize("names", [Endpoint, ChangeKind], ids=["Endpoint", "ChangeKind"])
def test_names_are_unique_and_well_formed(names: type[StrEnum]) -> None:
    values = [member.value for member in names]
    assert len(values) == len(set(values))
    assert [value for value in values if not NAME.match(value)] == []


def test_every_endpoint_has_exactly_one_effect() -> None:
    assert set(EFFECTS) == set(Endpoint)
