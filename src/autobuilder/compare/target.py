"""The target build, opened beside the owner's build in the same PoB as PoB's own CompareEntry (card 109, decision 009).

Rewrites the first app's guide.lua:1-46 handle: the target is loaded from its XML text by target.load and dropped by
target.release; a target PoB cannot open fails (TargetLoadFailed) and leaves none. The hash is of the exact text PoB
was given, as for the owner's build (analysis/session.py).
"""

import hashlib

from autobuilder.analysis.session import OpenedBuild
from autobuilder.pob.endpoints import Endpoint
from autobuilder.pob.session import BuildSummary, PobSession


def open_target(session: PobSession, xml: str, name: str) -> OpenedBuild:
    summary = BuildSummary.from_wire(session.call(Endpoint.TARGET_LOAD, {"xml": xml, "name": name}))
    return OpenedBuild(name, hashlib.sha256(xml.encode("utf-8")).hexdigest(), summary)


def release_target(session: PobSession) -> None:
    session.call(Endpoint.TARGET_RELEASE)
