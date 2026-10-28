"""One explicit table from an error to its HTTP status and the stable kind the page switches on (interfaces.md 4.9).

Domain errors carry no HTTP (comparison_app/errors.py). The message the page shows is the error's own (S8). A PoB
failure shows its first Lua line only; anything unexpected is a bug: 500 with a reference id the log also holds
(the first app's classify turned any ValueError into a 400, which could show a bug as "invalid request").
"""

import uuid
from dataclasses import dataclass

from comparison_app.app.security import Refused
from comparison_app.errors import FetchFailed, InvalidInput, PobError, PobNotInstalled, SetupProblem


@dataclass(frozen=True)
class ErrorReply:
    status: int
    kind: str
    message: str
    reference_id: str | None  # set for internal errors; the log record carries the same id


def reply_for(error: BaseException) -> ErrorReply:
    if isinstance(error, Refused):
        return ErrorReply(error.status, error.kind, error.kind.lower(), None)
    if isinstance(error, InvalidInput):  # BadLink, Unreadable, TooLarge, MixedStages, ...
        return ErrorReply(400, type(error).__name__, str(error), None)
    if isinstance(error, FetchFailed):
        return ErrorReply(502, "FetchFailed", str(error), None)
    if isinstance(error, PobNotInstalled | SetupProblem):
        return ErrorReply(503, "Unavailable", str(error), None)
    if isinstance(error, PobError):
        first_line = (error.message or "PoB failed").splitlines()[0]
        return ErrorReply(500, "EngineError", first_line, uuid.uuid4().hex[:12])
    return ErrorReply(500, "EngineError", f"internal error ({type(error).__name__})", uuid.uuid4().hex[:12])
