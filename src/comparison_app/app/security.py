"""What every request must show before the server reads it (the first app's engine/server.py:24-32, 108-142, kept).

The server answers only on 127.0.0.1; a request must name that host, come from the page's own origin (or none, as a
plain browser load does), and an API request must carry the token the page was given. Bodies are capped, a pasted PoB
code a little higher (interfaces.md 4.9). Every refusal is logged by the caller.
"""

import hmac
import secrets
from collections.abc import Mapping

from comparison_app.app.settings import HOST

MAX_BODY_BYTES = 64 * 1024
MAX_CODE_BODY_BYTES = 300 * 1024  # a request that carries a pasted PoB code (the code itself is limited in intake/)
TOKEN_HEADER = "X-Api-Token"  # noqa: S105 - the header's name, not a secret
COMMON_HEADERS = (  # anti-framing and no caching: the page carries the token
    ("X-Frame-Options", "DENY"),
    ("Content-Security-Policy", "frame-ancestors 'none'"),
    ("Cache-Control", "no-store"),
    ("X-Content-Type-Options", "nosniff"),
)


class Refused(Exception):  # the HTTP layer's own refusal, mapped in app/errors.py
    """A request the server will not read: `status` 401 or 403, `kind` the id the page switches on."""

    def __init__(self, status: int, kind: str, reason: str) -> None:
        super().__init__(reason)
        self.status, self.kind, self.reason = status, kind, reason


def new_token() -> str:
    return secrets.token_urlsafe(32)


def check_request(headers: Mapping[str, str], *, port: int, token: str, api: bool) -> None:
    hosts = {f"{HOST}:{port}", f"localhost:{port}"}
    origins = {f"http://{host}" for host in hosts}
    if headers.get("Host") not in hosts:
        raise Refused(403, "Forbidden", "bad_host")
    origin = headers.get("Origin")
    if origin is not None and origin not in origins:
        raise Refused(403, "Forbidden", "bad_origin")
    if api:
        supplied = headers.get(TOKEN_HEADER) or ""
        if not supplied:
            raise Refused(401, "Unauthorized", "missing_token")
        if not (token and hmac.compare_digest(supplied.encode("utf-8"), token.encode("utf-8"))):
            raise Refused(401, "Unauthorized", "bad_token")


def body_limit(carries_code: bool) -> int:
    return MAX_CODE_BODY_BYTES if carries_code else MAX_BODY_BYTES
