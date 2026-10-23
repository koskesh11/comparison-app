"""Offline tests for cached gem obtainability."""

import sys
import unittest
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from obtainability import (  # noqa: E402
    GemVariant,
    Obtainability,
    cache_date_for,
    normal_version,
)


class ObtainabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obtainability = Obtainability.from_cache("Allflame")

    def test_denied_awakened_gems_include_source(self):
        expected_reason = "All Awakened Support Gems can no longer be obtained"
        for name in ("Awakened Cast On Critical Strike", "Awakened Void Manipulation"):
            with self.subTest(name=name):
                status = self.obtainability.status(name)
                self.assertEqual(status["state"], "denied")
                self.assertEqual(status["since"], "3.28.0")
                self.assertEqual(status["note"], "Unobtainable gems")
                self.assertTrue(status["reason"].startswith(expected_reason))

    def test_awakened_empower_is_not_denied(self):
        self.assertIsNone(self.obtainability.deny_reason("Awakened Empower"))
        self.assertNotEqual(self.obtainability.status("Awakened Empower")["state"], "denied")

    def test_deny_reason_returns_a_copy(self):
        reason = self.obtainability.deny_reason("Awakened Void Manipulation")
        reason["since"] = "changed"
        self.assertEqual(
            self.obtainability.deny_reason("Awakened Void Manipulation")["since"],
            "3.28.0",
        )

    def test_best_uncorrupted_variants(self):
        expected = {
            "Cast On Critical Strike": GemVariant(20, 20, False),
            "Void Manipulation": GemVariant(20, 20, False),
            "Cooldown Recovery": GemVariant(3, 20, False),
        }
        for name, variant in expected.items():
            with self.subTest(name=name):
                self.assertEqual(self.obtainability.best_uncorrupted(name), variant)

    def test_best_uncorrupted_unknown_gem_is_none(self):
        self.assertIsNone(self.obtainability.best_uncorrupted("Nonexistent Gem"))

    def test_status_for_unlisted_gem_includes_cache_metadata(self):
        status = self.obtainability.status("Definitely Made Up Gem")
        self.assertEqual(status["state"], "unlisted")
        self.assertEqual(status["league"], "Allflame")
        self.assertRegex(status["cacheDate"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(status["cacheDate"], cache_date_for("Allflame"))

    def test_status_for_listed_gem(self):
        self.assertEqual(self.obtainability.status("Empower"), {"state": "listed"})

    def test_status_prefers_allow_over_listed(self):
        obtainability = Obtainability("X", gems={"empower": []}, allow={"empower"})
        self.assertEqual(obtainability.status("Empower"), {"state": "allowed"})

    def test_status_prefers_deny_over_allow(self):
        obtainability = Obtainability("X", allow={"empower"}, deny={"empower"})
        self.assertEqual(
            obtainability.status("Empower"),
            {"state": "denied", "note": "", "since": "", "reason": ""},
        )

    def test_normal_version(self):
        self.assertEqual(normal_version("Awakened Cast On Critical Strike"), "Cast On Critical Strike")
        self.assertIsNone(normal_version("Empower"))
        self.assertIsNone(normal_version("Awakened "))
        self.assertEqual(
            self.obtainability.normal_version("Awakened Void Manipulation"),
            "Void Manipulation",
        )

    def test_direct_construction_has_no_cache_date(self):
        status = Obtainability("X").status("foo")
        self.assertIsNone(status["cacheDate"])


if __name__ == "__main__":
    unittest.main()
