"""pobb.in import for the guide check: parse a link, fetch the build code, decode it. Stdlib only.

Limits (spec A1-A4, F1-F3): fixed host pobb.in, id ^[A-Za-z0-9_-]{4,32}$, 15 s timeout, code <= 256 KB, inflated
XML <= 4 MB (zlib bomb guard), no DOCTYPE/ENTITY, root tag PathOfBuilding. PoB parses the XML; Python never does.
Imported XML is saved only under <AutoBuilder dir>\imports\.
"""

import base64
import binascii
import re
import urllib.error
import urllib.request
import zlib
from pathlib import Path

from api_errors import ApiError, InvalidRequest

HOST = "pobb.in"
TIMEOUT_S = 15
MAX_CODE_BYTES = 256 * 1024
MAX_XML_BYTES = 4 * 1024 * 1024
ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{4,32}$")
LINK_PATTERN = re.compile(r"^(?:https?://)?(?:www\.)?pobb\.in/(?:pob/)?([^/?#\s]+)(?:/raw)?/?$", re.IGNORECASE)
ROOT_PATTERN = re.compile(r"^\ufeff?\s*(?:<\?xml[^>]*\?>\s*)?<PathOfBuilding[\s>/]")
FORBIDDEN_MARKUP = ("<!DOCTYPE", "<!ENTITY")


class BadLink(InvalidRequest):
    """F1: not a pobb.in build link."""


class Unreadable(InvalidRequest):
    """F1: the code is not a Path of Building build."""


class TooLarge(InvalidRequest):
    """F2: code or inflated XML over the limit."""


class FetchFailed(ApiError):
    """F3: pobb.in unreachable, slow, or answered with an error."""
    status = 502
    kind = "FetchFailed"


MSG_BAD_LINK = "That is not a pobb.in build link."
MSG_UNREADABLE = "Couldn\u2019t read that build."
MSG_TOO_LARGE = "That build is too large to import."


def parse_link(text) -> str:
    """Return the build id of a pobb.in link (pobb.in/ID, https://pobb.in/ID, /pob/ID, /ID/raw)."""
    match = LINK_PATTERN.match(text.strip()) if isinstance(text, str) else None
    if not match or not ID_PATTERN.match(match.group(1)) or match.group(1).lower() in ("pob", "raw"):
        raise BadLink(MSG_BAD_LINK)
    return match.group(1)


class _SameHostRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        host = urllib.request.urlparse(newurl).hostname or ""
        if host.lower() not in (HOST, "www." + HOST):
            raise urllib.error.URLError("redirect to another host refused")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _open(url: str, timeout: int):
    request = urllib.request.Request(url, headers={"User-Agent": "pob-autobuilder"})
    return urllib.request.build_opener(_SameHostRedirect).open(request, timeout=timeout)


def fetch(build_id: str) -> str:
    """Download the raw PoB code of a pobb.in build (at most MAX_CODE_BYTES)."""
    try:
        with _open(f"https://{HOST}/{build_id}/raw", timeout=TIMEOUT_S) as response:
            status = getattr(response, "status", 200)
            if status != 200:
                raise FetchFailed(f"Couldn\u2019t fetch the guide (pobb.in answered {status}). Try again later.")
            body = response.read(MAX_CODE_BYTES + 1)
    except urllib.error.HTTPError as error:
        raise FetchFailed(f"Couldn\u2019t fetch the guide (pobb.in answered {error.code}). Try again later.") from error
    except (urllib.error.URLError, OSError) as error:  # URLError, timeouts, resets
        raise FetchFailed("Couldn\u2019t fetch the guide (no connection). Try again later.") from error
    if len(body) > MAX_CODE_BYTES:
        raise TooLarge(MSG_TOO_LARGE)
    return body.decode("ascii", "replace").strip()


def decode(code: str) -> str:
    """Base64url + zlib to the PoB XML text, with size and markup guards. Raises TooLarge or Unreadable."""
    code = code.strip()
    if len(code) > MAX_CODE_BYTES:
        raise TooLarge(MSG_TOO_LARGE)
    try:
        raw = base64.urlsafe_b64decode(code + "=" * (-len(code) % 4))
    except (binascii.Error, ValueError) as error:
        raise Unreadable(MSG_UNREADABLE) from error
    inflater = zlib.decompressobj()
    try:
        data = inflater.decompress(raw, MAX_XML_BYTES + 1)
    except zlib.error as error:
        raise Unreadable(MSG_UNREADABLE) from error
    if len(data) > MAX_XML_BYTES:
        raise TooLarge(MSG_TOO_LARGE)
    return _checked_xml(data)


def _checked_xml(data: bytes) -> str:
    try:
        xml = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise Unreadable(MSG_UNREADABLE) from error
    if any(marker in xml for marker in FORBIDDEN_MARKUP) or not ROOT_PATTERN.match(xml):
        raise Unreadable(MSG_UNREADABLE)
    return xml


def save_import(xml: str, build_id: str, out_dir: Path) -> Path:
    """Write the XML to <out_dir>\imports\pobb-<id>.xml (the only write location, A4)."""
    target_dir = Path(out_dir) / "imports"
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"pobb-{build_id}.xml"
    temp = path.with_suffix(".xml.tmp")
    temp.write_bytes(xml.encode("utf-8"))
    temp.replace(path)
    return path


def import_link(text: str, out_dir: Path) -> dict:
    """Link to saved XML: {id, xml, path, codeBytes, xmlBytes}. No network when the link is bad."""
    build_id = parse_link(text)
    code = fetch(build_id)
    xml = decode(code)
    path = save_import(xml, build_id, out_dir)
    return {"id": build_id, "xml": xml, "path": str(path), "codeBytes": len(code), "xmlBytes": len(xml.encode("utf-8"))}
