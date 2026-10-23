"""Record deterministic guide snapshot fixtures from real headless PoB runs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tests import guide_testlib as gl
from tests import golden_common as gc

from guide_lua import ensure_loaded, load_guide, release_guide, snapshot


OUTPUT = Path(__file__).resolve().parent / "fixtures" / "snapshots"


def write(name: str, value: dict) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, indent=1, sort_keys=True) + "\n"
    (OUTPUT / name).write_text(text, encoding="utf-8", newline="\n")


def player_fixture(key: str, filename: str) -> None:
    with gc.pob_cwd():
        engine = gl.make_engine(key)
        try:
            ensure_loaded(engine)
            write(filename, snapshot(engine, "player"))
        finally:
            gc.close_engine(engine)


def guide_fixture() -> None:
    with gc.pob_cwd():
        engine = gl.make_engine("EK")
        try:
            ensure_loaded(engine)
            result = load_guide(engine, gl.decode_guide(), "pobb guide")
            if not result["ok"]:
                raise RuntimeError(result["error"])
            write("pobb_guide.json", snapshot(engine, "guide"))
            release_guide(engine)
        finally:
            gc.close_engine(engine)


def main() -> None:
    player_fixture("EK", "ek_player.json")
    player_fixture("Worb", "worb_player.json")
    guide_fixture()


if __name__ == "__main__":
    main()
