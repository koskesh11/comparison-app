"""Records tests/comparison_app/fixtures/golden_report.json (M5): the key paths of the reports of the golden cases.

Run by hand after a deliberate change to the report's shape: PYTHONPATH="src;." python tools/record_golden_report.py
"""

import json
import tempfile
from pathlib import Path

from tests.comparison_app.conftest import REFERENCE_BUILDS, REFERENCE_FILES, pob_install
from tests.comparison_app.test_golden_has_all_keys import GOLDEN, live_keys

from comparison_app.pob.session import PobPaths, open_session


def main() -> None:
    out = GOLDEN.resolve()  # before the session moves into PoB's folder
    xml = {name: (REFERENCE_BUILDS / file).read_text(encoding="utf-8") for name, file in REFERENCE_FILES.items()}
    root = Path(tempfile.mkdtemp())
    (root / "AutoBuilder").mkdir()
    with open_session(PobPaths(pob_install(), root / "user", root / "AutoBuilder")) as session:
        recorded = live_keys(session, xml)
    about = "Key paths of the golden reports (tests/comparison_app/test_golden_has_all_keys.py, M5)."
    out.write_bytes((json.dumps({"about": about, "cases": recorded}, indent=1) + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
