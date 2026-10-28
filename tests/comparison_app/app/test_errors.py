"""The error table (app/errors.py, interfaces.md 4.9)."""

import pytest

from comparison_app.app.errors import reply_for
from comparison_app.app.security import Refused
from comparison_app.errors import (
    BadLink,
    FetchFailed,
    MixedStages,
    PobError,
    PobNotInstalled,
    SetupProblem,
)


@pytest.mark.parametrize(
    ("error", "status", "kind", "message"),
    [
        (BadLink("not a pobb.in link"), 400, "BadLink", "not a pobb.in link"),
        (MixedStages("Your build mixes stages"), 400, "MixedStages", "Your build mixes stages"),
        (FetchFailed("pobb.in did not answer"), 502, "FetchFailed", "pobb.in did not answer"),
        (PobNotInstalled("PoB not found"), 503, "Unavailable", "PoB not found"),
        (SetupProblem("no Builds folder"), 503, "Unavailable", "no Builds folder"),
        (Refused(401, "Unauthorized", "bad_token"), 401, "Unauthorized", "unauthorized"),
    ],
)
def test_known_errors_keep_their_own_message(error: Exception, status: int, kind: str, message: str) -> None:
    reply = reply_for(error)
    assert (reply.status, reply.kind, reply.message, reply.reference_id) == (status, kind, message, None)


def test_a_pob_failure_shows_its_first_line_with_a_reference() -> None:
    reply = reply_for(PobError("attempt to index a nil value\nstack traceback: ...", "tb"))
    assert (reply.status, reply.kind, reply.message) == (500, "EngineError", "attempt to index a nil value")
    assert reply.reference_id


def test_a_bug_is_never_shown_as_invalid_input() -> None:
    reply = reply_for(ValueError("bad"))
    assert (reply.status, reply.kind, reply.message) == (500, "EngineError", "internal error (ValueError)")
    assert reply.reference_id
