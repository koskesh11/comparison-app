"""The report's own rules (app/present/report.py); its keys are M5 (test_golden_has_all_keys.py)."""

import math

import pytest

from comparison_app.app.present.report import key_paths, number


@pytest.mark.parametrize(
    ("value", "shown"),
    [(3, 3.0), (2.5, 2.5), (math.inf, None), (math.nan, None), (None, None), (True, None), ("7", None)],
)
def test_a_missing_or_infinite_number_is_null(value: object, shown: float | None) -> None:
    assert number(value) == shown


def test_key_paths_name_objects_and_list_items() -> None:
    value = {"a": {"b": 1}, "c": [{"d": 2}], "sources": [{"rows": [{"anything": 1}]}]}
    assert key_paths(value) == {"a", "a.b", "c", "c[].d", "sources", "sources[].rows"}
