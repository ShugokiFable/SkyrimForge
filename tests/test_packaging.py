from __future__ import annotations

import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

import forge_build_backend


class PackagingTests(unittest.TestCase):
    def test_no_external_build_requirements(self):
        self.assertEqual(forge_build_backend.get_requires_for_build_wheel(), [])

    def test_wheel_determinism_and_native_files(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            wa=Path(a)/forge_build_backend.build_wheel(a); wb=Path(b)/forge_build_backend.build_wheel(b)
            self.assertEqual(hashlib.sha256(wa.read_bytes()).hexdigest(),hashlib.sha256(wb.read_bytes()).hexdigest())
            with zipfile.ZipFile(wa) as archive:
                self.assertIsNone(archive.testzip())
                self.assertIn("skyrim_forge/bin/win-x64/SkyrimForge.Native.exe",archive.namelist())

    def test_runtime_installation_artifacts_are_never_packaged(self):
        excluded = forge_build_backend.EXCLUDED
        self.assertIn("INSTALLATION.json", excluded)
        self.assertIn("REPORTS", excluded)
        self.assertIn(".venv", excluded)
        self.assertIn(".go-cache", excluded)


if __name__ == "__main__": unittest.main()
