"""Stable, non-sensitive API error responses."""

import json

import optimize
import pobhost


class ApiError(Exception):
    status = 500
    kind = "ApiError"


class InvalidRequest(ApiError):
    status = 400
    kind = "InvalidRequest"


class Unauthorized(ApiError):
    status = 401
    kind = "Unauthorized"


class Forbidden(ApiError):
    status = 403
    kind = "Forbidden"


class Unavailable(ApiError):
    status = 503
    kind = "Unavailable"


class StaleAudit(ApiError):
    status = 409
    kind = "StaleAudit"


class EngineError(ApiError):
    status = 500
    kind = "EngineError"


def _invalid_message(error: Exception) -> str:
    if isinstance(error, KeyError):
        name = error.args[0] if error.args else "unknown"
        return f"missing field {name}"
    return str(error)


def _lua_message(error: Exception) -> str:
    first_line = next((line.strip() for line in str(error).splitlines() if line.strip()), "")
    return f"engine error: {first_line}"


def classify(error: Exception) -> tuple[int, dict]:
    """Map an exception to a stable HTTP status and safe JSON body."""
    if isinstance(error, ApiError):
        return error.status, {"error": str(error), "kind": error.kind}
    if isinstance(error, optimize.StaleAudit):
        return 409, {"error": str(error), "kind": "StaleAudit"}
    invalid = (ValueError, optimize.ChangeError, KeyError, json.JSONDecodeError)
    if isinstance(error, invalid):
        return 400, {"error": _invalid_message(error), "kind": "InvalidRequest"}
    if isinstance(error, pobhost.LuaError):
        return 500, {"error": _lua_message(error), "kind": "EngineError"}
    message = f"internal error ({type(error).__name__})"
    return 500, {"error": message, "kind": "EngineError"}
