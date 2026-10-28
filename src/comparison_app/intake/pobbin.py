"""A pobb.in link to its PoB code (decision 012): one request per pasted link, to the address PoB itself uses.

PoB downloads pobb.in builds from `pobb.in/pob/<id>` (Modules/BuildSiteTools.lua:29, PoB 2.67.2); the first app used
`/<id>/raw` (engine/pobbin.py:96). Limits kept from the first app (engine/pobbin.py:20-107): https on port 443 to
pobb.in only, redirects only to the same host, 15 s per read and 30 s in all, at most 256 KB of code.
"""

import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from http.client import HTTPMessage
from typing import IO, Protocol

from comparison_app.errors import BadLink, FetchFailed, TooLarge

HOST = "pobb.in"
READ_SECONDS = 15
TOTAL_SECONDS = 30
CHUNK_BYTES = 16 * 1024
MAX_CODE_BYTES = 256 * 1024
HTTP_OK = 200
HTTPS_PORT = 443
ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{4,32}$")
LINK_PATTERN = re.compile(r"^(?:https?://)?(?:www\.)?pobb\.in/(?:pob/)?([^/?#\s]+)(?:/raw)?/?$", re.IGNORECASE)
NOT_IDS = ("pob", "raw")


class Response(Protocol):
    status: int

    def read1(self, size: int) -> bytes: ...
    def __enter__(self) -> "Response": ...
    def __exit__(self, *_: object) -> None: ...


Opener = Callable[[str, float], Response]


def looks_like_link(text: str) -> bool:
    """Pasted text that is meant as a link: PoB codes never hold a dot or a slash."""
    return "." in text or "/" in text


def parse_link(text: str) -> str:
    """The build id of a pobb.in link (pobb.in/ID, https://pobb.in/ID, /pob/ID, /ID/raw)."""
    match = LINK_PATTERN.match(text.strip())
    if not match or not ID_PATTERN.match(match.group(1)) or match.group(1).lower() in NOT_IDS:
        raise BadLink("That is not a pobb.in build link. For a build from another site, paste its PoB code.")
    return match.group(1)


class SameHostRedirect(urllib.request.HTTPRedirectHandler):
    """Follows a redirect only to pobb.in over https on port 443 without a login."""

    def redirect_request(  # noqa: PLR0913, PLR0917 - urllib's signature for this method
        self, req: urllib.request.Request, fp: IO[bytes], code: int, msg: str, headers: HTTPMessage, newurl: str
    ) -> urllib.request.Request | None:
        try:  # a malformed target (https://pobb.in:abc/, https://[bad) makes urlparse or .port raise ValueError
            target = urllib.parse.urlparse(newurl)
            host, port = (target.hostname or "").lower(), target.port
        except ValueError as error:
            raise urllib.error.URLError("redirect to a malformed address refused") from error
        if (
            host not in (HOST, "www." + HOST)
            or target.scheme != "https"
            or port not in (None, HTTPS_PORT)
            or target.username
            or target.password
        ):
            raise urllib.error.URLError("redirect to another host, scheme, port or login refused")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def open_https(url: str, timeout: float) -> Response:
    if not url.startswith(f"https://{HOST}/"):
        raise ValueError(f"only https://{HOST}/ is fetched, not {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "comparison-app"})  # noqa: S310 - https checked above
    response: Response = urllib.request.build_opener(SameHostRedirect).open(request, timeout=timeout)
    return response


def _read_limited(response: Response, clock: Callable[[], float]) -> bytes:
    """At most MAX_CODE_BYTES + 1 within TOTAL_SECONDS, so a slow server cannot hold a job open."""
    deadline, body = clock() + TOTAL_SECONDS, b""
    while len(body) <= MAX_CODE_BYTES:
        if clock() > deadline:
            raise FetchFailed("Couldn't fetch the build: pobb.in is too slow. Try again later.")
        chunk = response.read1(min(CHUNK_BYTES, MAX_CODE_BYTES + 1 - len(body)))
        if not chunk:
            break
        body += chunk
    return body


def fetch(build_id: str, opener: Opener = open_https, clock: Callable[[], float] = time.monotonic) -> str:
    """The PoB code of one pobb.in build: exactly one request."""
    try:
        with opener(f"https://{HOST}/pob/{build_id}", READ_SECONDS) as response:
            if response.status != HTTP_OK:
                raise FetchFailed(f"Couldn't fetch the build: pobb.in answered {response.status}. Try again later.")
            body = _read_limited(response, clock)
    except urllib.error.HTTPError as error:
        raise FetchFailed(f"Couldn't fetch the build: pobb.in answered {error.code}. Try again later.") from error
    except (urllib.error.URLError, OSError) as error:  # no connection, timeouts, resets, refused redirects
        raise FetchFailed("Couldn't fetch the build: no connection to pobb.in. Try again later.") from error
    if len(body) > MAX_CODE_BYTES:
        raise TooLarge("That build is too large to import.")
    return body.decode("ascii", "replace").strip()
