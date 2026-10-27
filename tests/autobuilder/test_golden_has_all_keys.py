"""M5: every key the report sends to the browser is in the golden snapshot, so a new key cannot ship untested.

Skipped until autobuilder.app.present.report exists; then it fails until this test compares report.KEYS with the
keys of fixtures/golden_report.json (recorded from the reference builds, decision 014).
"""

import importlib.util

import pytest


def test_golden_snapshot_has_every_report_key() -> None:
    if importlib.util.find_spec("autobuilder.app.present.report") is None:
        pytest.skip("no report module yet (milestone 1)")
    pytest.fail("write the golden-keys test for the report module (module docstring)")
