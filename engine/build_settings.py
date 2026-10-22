"""Per-build settings remembered between runs (e.g. skills to leave out of the calculation)."""

import json
from pathlib import Path

SETTINGS_FILE = Path(__file__).resolve().parent / "userdata" / "build_settings.json"


def _load_all() -> dict:
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def get(build_key: str) -> dict:
    return _load_all().get(build_key, {})


def update(build_key: str, **values) -> dict:
    data = _load_all()
    merged = {**data.get(build_key, {}), **values}
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_FILE.write_text(json.dumps({**data, build_key: merged}, indent=2), encoding="utf-8")
    return merged
