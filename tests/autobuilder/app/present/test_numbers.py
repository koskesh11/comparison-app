"""The app's number formats (decision 020); the cases themselves are M4 (tests/autobuilder/test_number_cases.py)."""

import pytest

from autobuilder.app.present.numbers import MISSING, show


def test_an_unknown_rule_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown number rule"):
        show(1.0, rule="truncate", precision=0)


def test_missing_is_never_zero() -> None:
    assert show(None, rule="floor", precision=2) == MISSING != "0"
