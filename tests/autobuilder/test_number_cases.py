"""M4: number formats shared by Python and the browser code (decision 020), including PoB's edge cases (S12).

fixtures/number_cases.json holds cases recorded from real PoB output: raw values with many decimals, negatives, -0,
inf, NaN and missing values, each with the rule (`pob` or `floor`), the precision and the text PoB or the game shows.
The browser test (tests/web, with the web code) reads the same file. While the list is empty nothing runs; the first
case needs autobuilder.app.present.numbers.
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


@pytest.mark.parametrize("case", cases())
def test_python_shows_the_case_as_pob_does(case: dict[str, Any]) -> None:
    numbers = importlib.import_module("autobuilder.app.present.numbers")
    assert numbers.show(case["value"], rule=case["rule"], precision=case["precision"]) == case["shown"]
