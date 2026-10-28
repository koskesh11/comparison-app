"""One build opened in PoB as the owner saved it (decision 018): no network, no models, nothing left out.

Rewrites the first app's Auditor constructor (engine/audit.py:43-110): the build is validated by PoB itself
(build.load fails on a broken file) and the hash is taken of the exact bytes PoB was given, so a later change to the
file on disk can be noticed.
"""

import hashlib
from dataclasses import dataclass

from comparison_app.pob.session import BuildSummary, PobSession


@dataclass(frozen=True)
class OpenedBuild:
    name: str
    sha256: str  # of the XML text's UTF-8 bytes, exactly as PoB loaded them
    summary: BuildSummary


def open_build(session: PobSession, xml: str, name: str) -> OpenedBuild:
    summary = session.load_build(xml, name)
    return OpenedBuild(name, hashlib.sha256(xml.encode("utf-8")).hexdigest(), summary)
