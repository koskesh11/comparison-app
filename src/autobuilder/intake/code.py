"""A PoB build code to its XML (the first app's engine/pobbin.py:110-136, kept, plus the end-of-stream check).

Base64url and zlib, as PoB writes codes. Guards: at most 256 KB of code and 4 MB of XML (a zlib bomb stops at the
limit), no DOCTYPE or ENTITY, the root element PathOfBuilding. A cut-off stream is refused (task 102, area F finding
9: the first app let a truncated code through). PoB parses the XML; Python never does.
"""

import base64
import binascii
import re
import zlib

from autobuilder.errors import TooLarge, Unreadable
from autobuilder.intake.pobbin import MAX_CODE_BYTES

MAX_XML_BYTES = 4 * 1024 * 1024
ROOT_PATTERN = re.compile(r"^﻿?\s*(?:<\?xml[^>]*\?>\s*)?<PathOfBuilding[\s>/]")
FORBIDDEN_MARKUP = ("<!DOCTYPE", "<!ENTITY")
UNREADABLE = "Couldn't read that build."
TOO_LARGE = "That build is too large to import."


def decode(code: str) -> str:
    """The build's XML text; raises TooLarge or Unreadable."""
    code = code.strip()
    if len(code) > MAX_CODE_BYTES:
        raise TooLarge(TOO_LARGE)
    try:
        raw = base64.urlsafe_b64decode(code + "=" * (-len(code) % 4))
    except (binascii.Error, ValueError) as error:
        raise Unreadable(UNREADABLE) from error
    inflater = zlib.decompressobj()
    try:
        data = inflater.decompress(raw, MAX_XML_BYTES + 1)
    except zlib.error as error:
        raise Unreadable(UNREADABLE) from error
    if len(data) > MAX_XML_BYTES:
        raise TooLarge(TOO_LARGE)
    if not inflater.eof:
        raise Unreadable("That build code is cut off; copy it again.")
    return checked_xml(data)


def checked_xml(data: bytes) -> str:
    """UTF-8 text with a PathOfBuilding root and no DOCTYPE or ENTITY, or Unreadable."""
    try:
        xml = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise Unreadable(UNREADABLE) from error
    if any(marker in xml for marker in FORBIDDEN_MARKUP) or not ROOT_PATTERN.match(xml):
        raise Unreadable(UNREADABLE)
    return xml
