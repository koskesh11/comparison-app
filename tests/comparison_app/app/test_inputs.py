"""What the page sends (app/inputs.py): read into typed records, everything else refused with words."""

import pytest

from comparison_app.analysis.scenarios import Scenario
from comparison_app.app.inputs import CompareRequest, compare_request
from comparison_app.errors import InvalidInput


def test_a_full_request_becomes_typed() -> None:
    body = {
        "build": "3.29/Worb.xml",
        "target": "https://pobb.in/v8XfQn1yFnAs",
        "scenario": "uber_pinnacle_boss",
        "yourStage": "",
        "targetStage": "Yellow Maps",
    }
    assert compare_request(body) == CompareRequest(
        "3.29/Worb.xml", "https://pobb.in/v8XfQn1yFnAs", None, Scenario.UBER_PINNACLE_BOSS, None, "Yellow Maps"
    )


def test_the_scenario_defaults_to_pinnacle() -> None:
    assert compare_request({"build": "a.xml", "targetImport": "pobb-abc"}).scenario is Scenario.PINNACLE_BOSS


@pytest.mark.parametrize(
    ("body", "message"),
    [
        ({"target": "x"}, "Missing build"),
        ({"build": "a.xml"}, "one of them"),
        ({"build": "a.xml", "target": "x", "targetImport": "pobb-abc"}, "one of them"),
        ({"build": "a.xml", "target": "x", "scenario": "sometimes"}, "Unknown scenario"),
        ({"build": 7, "target": "x"}, "build must be text"),
    ],
)
def test_a_wrong_request_is_refused_with_words(body: dict[str, object], message: str) -> None:
    with pytest.raises(InvalidInput, match=message):
        compare_request(body)
