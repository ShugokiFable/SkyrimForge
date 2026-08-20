from __future__ import annotations

import json
import subprocess
import sys
import unittest

from skyrim_forge.bundle_contract import evaluate_bundle_contract
from skyrim_forge.version import VERSION


class BundleContractTests(unittest.TestCase):
    def test_product_version_is_the_5_2_contract_series(self):
        # Pin the SERIES, not the patch. The contract range in
        # bundle_contract.py is what 5.2 promises a bundle; a patch bump does
        # not change it, and a test that hardcodes 5.2.0 just turns every
        # patch release into a test edit -- the same restated-literal drift
        # the version gate exists to catch.
        self.assertEqual(VERSION.split(".")[:2], ["5", "2"])

    def test_ultimate_bundle_7_8_0_is_compatible(self):
        report = evaluate_bundle_contract("7.8.0")
        self.assertEqual(report["result"], "PASS", report)
        self.assertEqual(report["contract_version"], 1)
        self.assertEqual(report["forge_version"], VERSION)
        self.assertEqual(report["bundle_version"], "7.8.0")
        self.assertTrue(report["capabilities"]["mcp_stdio"])
        self.assertTrue(report["capabilities"]["provider_registration"])

    def test_pre_7_8_bundle_is_rejected(self):
        report = evaluate_bundle_contract("7.7.15")
        self.assertEqual(report["result"], "FAIL")
        self.assertIn("requires Ultimate AI Starter Bundle >= 7.8.0", report["reason"])

    def test_next_bundle_major_requires_new_contract(self):
        report = evaluate_bundle_contract("8.0.0")
        self.assertEqual(report["result"], "FAIL")
        self.assertIn("< 8.0.0", report["reason"])

    def test_cli_contract_is_machine_readable_and_exit_code_tracks_result(self):
        ok = subprocess.run(
            [sys.executable, "-m", "skyrim_forge", "bundle-contract", "--bundle-version", "7.8.0"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
        self.assertEqual(json.loads(ok.stdout)["result"], "PASS")

        bad = subprocess.run(
            [sys.executable, "-m", "skyrim_forge", "bundle-contract", "--bundle-version", "7.7.15"],
            text=True,
            capture_output=True,
        )
        self.assertEqual(bad.returncode, 2, bad.stdout + bad.stderr)
        self.assertEqual(json.loads(bad.stdout)["result"], "FAIL")


if __name__ == "__main__":
    unittest.main()
