"""Opt-in end-to-end determinism checks."""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import golden_common as gc  # noqa: E402


@unittest.skipUnless(os.environ.get("AUTOBUILDER_SLOW") == "1",
                     "set AUTOBUILDER_SLOW=1 (slow: N full v4 audits)")
class DeterminismTests(unittest.TestCase):
    def test_v4_audit_deterministic(self):
        runs = int(os.environ.get("AUTOBUILDER_DET_RUNS", "10"))
        reports = []
        for _ in range(runs):
            with gc.pob_cwd():
                auditor = None
                try:
                    auditor = gc.offline_auditor(
                        gc.build_path(gc.RAW_BUILDS["v4"]),
                        {"includeDrafts": True, "disabledSkills": [], "scenario": "Pinnacle Boss"},
                    )
                    reports.append(gc.jsonable(auditor.run()))
                finally:
                    if auditor is not None:
                        gc.close_engine(auditor.engine)

        first = reports[0]
        for index, other in enumerate(reports[1:], start=2):
            differences = gc.diff(first, other)
            if differences:
                self.fail(f"run {index} differed:\n" + "\n".join(differences[:40]))


if __name__ == "__main__":
    unittest.main()
