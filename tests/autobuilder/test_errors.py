"""The app's errors: every PoB failure is a PobError carrying its message and the traceback for the log."""

from autobuilder.errors import AutobuilderError, BuildLoadFailed, NoBuildLoaded, PobError, UnknownEndpoint


def test_a_pob_error_keeps_its_message_and_traceback() -> None:
    error = PobError("broken", traceback="stack traceback: ...")
    assert (str(error), error.message, error.traceback) == ("broken", "broken", "stack traceback: ...")
    assert PobError("x").traceback is None


def test_every_pob_failure_is_a_pob_error_and_an_app_error() -> None:
    for kind in (UnknownEndpoint, BuildLoadFailed, NoBuildLoaded):
        assert issubclass(kind, PobError) and issubclass(kind, AutobuilderError)
