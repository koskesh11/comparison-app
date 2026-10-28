"""M4: number formats shared by Python and the browser code (decision 020), including PoB's edge cases (S12).

fixtures/number_cases.json holds cases recorded from real PoB output: raw values with many decimals, negatives, -0,
inf, NaN and missing values, each with the rule (`pob` or `floor`), the precision and the text PoB or the game shows.
The browser test (tests/web, with the web code) reads the same file;
tests/comparison_app/pob/test_number_format.py checks every `pob` case against PoB's own formatter.
"""

import importlib
import json
from pathlib import Path
from typing import Any

import pytest

CASES = Path(__file__).parent / "fixtures" / "number_cases.json"
FIELDS = {"value", "rule", "precision", "shown", "source"}
RULES = {"pob", "floor"}


def cases() -> list[dict[str, Any]]:
    data: dict[str, list[dict[str, Any]]] = json.loads(CASES.read_text(encoding="utf-8"))
    return data["cases"]


def test_every_case_names_its_rule_and_source() -> None:
    assert [case for case in cases() if set(case) != FIELDS or case["rule"] not in RULES] == []


def number(value: object) -> float | None:
    """A case's value: a number, "inf", "-inf", "nan", or null for missing."""
    return None if value is None else float(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("case", cases(), ids=lambda case: f"{case['value']}-{case['rule']}{case['precision']}")
def test_python_shows_the_case_as_pob_does(case: dict[str, Any]) -> None:
    numbers = importlib.import_module("comparison_app.app.present.numbers")
    assert numbers.show(number(case["value"]), rule=case["rule"], precision=case["precision"]) == case["shown"]
