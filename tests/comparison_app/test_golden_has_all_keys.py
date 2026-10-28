"""M5: every key the report sends to the browser is in the golden snapshot, so a new key cannot ship untested.

fixtures/golden_report.json holds the key paths of the reports of four comparisons of the reference builds
(decision 014), chosen so every part of the report is filled: Worb against itself (the table), Worb against CoC EK
Assa (a different main skill, config differences, a setting that looks wrong), Worb against Worb with a Custom
Modifier and a box it cannot use, CoC EK Assa against its Cyclone variant (the target's skill choices). The live
reports must have exactly those keys; record again with tools/record_golden_report.py after a deliberate change.
"""

import json
from pathlib import Path

import pytest

from comparison_app.analysis.scenarios import Scenario
from comparison_app.app.present.report import key_paths, report
from comparison_app.compare.service import compare
from comparison_app.pob.session import PobSession

GOLDEN = Path(__file__).parent / "fixtures" / "golden_report.json"
CHILLED = '<Input name="conditionEnemyChilled" boolean="true"/>'
CYCLONE = ('slot="Body Armour" mainActiveSkill="1"', 'slot="Body Armour" mainActiveSkill="2"')
EDITS = '<Input name="customMods" string="20% more Damage"/><Input name="channellingCycloneCheck" boolean="true"/>'


def cases(reference_xml: dict[str, str]) -> dict[str, tuple[tuple[str, str], tuple[str, str]]]:
    worb, assa = (reference_xml["Worb"], "Worb"), (reference_xml["CoC EK Assa"], "CoC EK Assa")
    edited = (reference_xml["Worb"].replace(CHILLED, CHILLED + EDITS), "Worb edited")
    cyclone = (assa[0].replace(*CYCLONE), "Cyclone")  # the conftest variant: group 1's second skill as main
    return {
        "Worb vs Worb": (worb, worb),
        "Worb vs CoC EK Assa": (worb, assa),
        "Worb vs Worb edited": (worb, edited),
        "CoC EK Assa vs Cyclone": (assa, cyclone),  # the target's skill choices
    }


def live_keys(session: PobSession, reference_xml: dict[str, str]) -> dict[str, list[str]]:
    return {
        name: sorted(key_paths(report(compare(session, yours, target, Scenario.PINNACLE_BOSS))))
        for name, (yours, target) in cases(reference_xml).items()
    }


@pytest.mark.pob
def test_golden_snapshot_has_every_report_key(pob_session: PobSession, reference_xml: dict[str, str]) -> None:
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]
    assert live_keys(pob_session, reference_xml) == golden
