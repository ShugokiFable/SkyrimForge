from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


class CIValidationScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        script = Path(__file__).resolve().parents[1] / "scripts" / "validate_repository.py"
        spec = importlib.util.spec_from_file_location("forge_validate_repository", script)
        assert spec and spec.loader
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_python_scope_never_rebuilds_native_binaries(self):
        checks = self.module.validation_checks("python")
        self.assertIn("python", checks)
        self.assertIn("packaging", checks)
        self.assertNotIn("native", checks)
        self.assertNotIn("go", checks)

    def test_full_scope_contains_reproducibility_checks(self):
        checks = self.module.validation_checks("full")
        self.assertIn("native", checks)
        self.assertIn("go", checks)

    def test_unknown_scope_is_rejected(self):
        with self.assertRaises(ValueError):
            self.module.validation_checks("unknown")


if __name__ == "__main__":
    unittest.main()
