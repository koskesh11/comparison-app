"""What the page sends, read once into typed records; anything else is InvalidInput with words the page can show.

A compare request names your build (a path inside the Builds folder, intake/library.py), the target (a pasted
pobb.in link or PoB code, or an import saved before, intake/store.py), the scenario (decision 010) and, for each build,
the stage picked or none for the saved one (decision 026). Keys are camelCase, as the wire is (interfaces.md 4.9).
"""

from collections.abc import Mapping
from dataclasses import dataclass

from comparison_app.analysis.scenarios import DEFAULT, Scenario
from comparison_app.errors import InvalidInput

MAX_TEXT = 300 * 1024  # a pasted code; the body cap (app/security.py) holds the same


@dataclass(frozen=True)
class CompareRequest:
    build: str  # relative to the Builds folder
    target: str | None  # a pasted pobb.in link or PoB code
    target_import: str | None  # or an import id saved before ("pobb-...", "code-...")
    scenario: Scenario
    your_stage: str | None
    target_stage: str | None


def _text(body: Mapping[str, object], key: str, *, required: bool = False) -> str | None:
    value = body.get(key)
    if value is None or value == "":
        if required:
            raise InvalidInput(f"Missing {key}.")
        return None
    if not isinstance(value, str) or len(value) > MAX_TEXT:
        raise InvalidInput(f"{key} must be text.")
    return value


def compare_request(body: Mapping[str, object]) -> CompareRequest:
    build = _text(body, "build", required=True)
    target, target_import = _text(body, "target"), _text(body, "targetImport")
    if (target is None) == (target_import is None):
        raise InvalidInput("Paste a pobb.in link or a PoB code, or pick a saved target - one of them.")
    scenario_name = _text(body, "scenario") or DEFAULT.value
    try:
        scenario = Scenario(scenario_name)
    except ValueError as error:
        raise InvalidInput(f"Unknown scenario {scenario_name!r}.") from error
    return CompareRequest(
        str(build), target, target_import, scenario, _text(body, "yourStage"), _text(body, "targetStage")
    )
