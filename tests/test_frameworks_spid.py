from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skyrim_forge.frameworks import lint_paths


class SpidGrammarTests(unittest.TestCase):
    def test_actor_level_plus_skill_range_is_valid(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "ForHonor_DISTR.ini"
            path.write_text("Perk = 0x123~ForHonor.esp|||25/255,0(55/255)|||100\n", encoding="utf-8")
            report = lint_paths([path])
            self.assertEqual(report["result"], "PASS", report)
            self.assertEqual(report["errors"], 0)

    def test_single_value_skill_expression_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "Broken_DISTR.ini"
            path.write_text("Perk = 0x123~Broken.esp|||10/24,0(25)|||100\n", encoding="utf-8")
            report = lint_paths([path])
            self.assertEqual(report["result"], "FAIL")
            self.assertTrue(any("skill" in issue["message"].casefold() for item in report["reports"] for issue in item["issues"]))

    def test_skill_index_and_range_order_are_checked(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "Broken_DISTR.ini"
            path.write_text("Perk = 0x123~Broken.esp|||18(50/10)|||100\n", encoding="utf-8")
            report = lint_paths([path])
            self.assertEqual(report["result"], "FAIL")
            messages = [issue["message"] for item in report["reports"] for issue in item["issues"]]
            self.assertTrue(any("index" in message.casefold() for message in messages))

    def test_unknown_future_key_is_warning_not_false_failure(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "future_DISTR.ini"
            path.write_text("FutureDistribution = 0x1~A.esp||||||100\n", encoding="utf-8")
            report = lint_paths([path])
            self.assertEqual(report["result"], "PASS")
            self.assertEqual(report["errors"], 0)
            self.assertEqual(report["warnings"], 1)
            self.assertIn("outside Forge's pinned 7.3 profile", report["reports"][0]["issues"][0]["message"])

    def test_known_weapon_alias_remains_a_hard_error(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "bad_DISTR.ini"
            path.write_text("Weapon = 0x1~A.esp||||||100\n", encoding="utf-8")
            report = lint_paths([path])
            self.assertEqual(report["result"], "FAIL")
            self.assertEqual(report["errors"], 1)


if __name__ == "__main__":
    unittest.main()
