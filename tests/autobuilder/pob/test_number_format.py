"""M4 against PoB itself: every `pob` case in fixtures/number_cases.json is what PoB's own formatter writes today
(formatCalcVal, CalcFormat.lua:12-14), run in the shared session (lua/format_values.lua). A PoB update that changes its
formatting fails here first."""

import json
from pathlib import Path

import pytest

from autobuilder.pob.session import PobSession

pytestmark = pytest.mark.pob

PROBES = Path(__file__).parent / "lua"
CASES = Path(__file__).parents[1] / "fixtures" / "number_cases.json"


def test_every_pob_case_is_what_pob_writes(pob_session: PobSession) -> None:
    cases = [
        case
        for case in json.loads(CASES.read_text(encoding="utf-8"))["cases"]
        if case["rule"] == "pob" and case["value"] is not None
    ]
    probe = [{"value": case["value"], "precision": case["precision"]} for case in cases]
    answer = pob_session._host.run_file(PROBES / "format_values.lua", json.dumps(probe))  # the probe needs the state
    assert answer is not None
    assert json.loads(answer) == [case["shown"] for case in cases]
