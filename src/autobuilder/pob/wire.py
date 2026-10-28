"""The wire between Python and Lua (S12): a request is a JSON object, a reply an `{ok, value, error}` envelope.

Lua writes inf, -inf and NaN as the JSON words Infinity, -Infinity and NaN (pob/lua/rpc.lua), which Python's json reads
as floats; dkjson alone writes them as null (dkjson.lua:293-295), which could not be told from a missing value. A
missing value is a missing key, and the typed records turn it into None.
"""

import json
from collections.abc import Mapping
from typing import Any

from autobuilder.errors import (
    BuildLoadFailed,
    BuildNotRestored,
    NoBuildLoaded,
    NoMainSkill,
    NoTargetLoaded,
    PobError,
    TargetLoadFailed,
    UnknownEndpoint,
)

ERRORS: dict[str, type[PobError]] = {
    "UnknownEndpoint": UnknownEndpoint,
    "BuildNotLoaded": BuildLoadFailed,
    "NoBuild": NoBuildLoaded,
    "NoMainSkill": NoMainSkill,
    "BuildNotRestored": BuildNotRestored,
    "TargetNotLoaded": TargetLoadFailed,
    "NoTarget": NoTargetLoaded,
}


def encode_request(payload: Mapping[str, Any] | None) -> bytes:
    """A request as UTF-8 JSON; a non-finite number in a request is a bug (ValueError)."""
    return json.dumps(dict(payload or {}), allow_nan=False, ensure_ascii=False, separators=(",", ":")).encode()


def decode_reply(raw: bytes) -> Any:
    """The value of an `ok` envelope; any other reply raises the PobError its `kind` names."""
    try:
        envelope = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PobError(f"PoB's reply is not JSON: {error}") from error
    if not isinstance(envelope, dict) or not isinstance(envelope.get("ok"), bool):
        raise PobError("PoB's reply is not an {ok, value, error} envelope")
    if envelope["ok"]:
        return envelope.get("value")
    raise _error(envelope.get("error"))


def _error(error: object) -> PobError:
    if not isinstance(error, dict):
        return PobError("PoB failed without saying why")
    kind, message, traceback = error.get("kind"), error.get("message"), error.get("traceback")
    text = message if isinstance(message, str) else f"PoB failed ({kind})"
    return ERRORS.get(str(kind), PobError)(text, traceback if isinstance(traceback, str) else None)


def number(value: object) -> float | None:
    """A PoB number as a float (inf and NaN included); None when it is missing."""
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise PobError(f"expected a number from PoB, got {type(value).__name__}")
    return float(value)


def text(value: object) -> str | None:
    """A PoB text value; None when it is missing."""
    if value is None or isinstance(value, str):
        return value
    raise PobError(f"expected text from PoB, got {type(value).__name__}")


def table(value: object) -> dict[str, Any]:
    """A PoB table with text keys; dkjson writes an empty table as []."""
    if value == []:
        return {}
    if not isinstance(value, dict):
        raise PobError(f"expected a table from PoB, got {type(value).__name__}")
    return value
