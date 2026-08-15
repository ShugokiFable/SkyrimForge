from __future__ import annotations

import importlib.util
import re
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


class WorkflowPinningTests(unittest.TestCase):
    """CodeQL's init and analyze actions must always run the same release.

    Dependabot raises one pull request per action unless they are grouped, so
    each request bumped half of the pair and every CodeQL run on those branches
    died with "Loaded a configuration file for version '4.37.6', but running
    version '4.36.0'". Four pull requests sat blocked behind it.
    """

    WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"

    def test_codeql_action_versions_are_pinned_together(self):
        pinned = set()
        for workflow in self.WORKFLOWS.glob("*.yml"):
            for match in re.finditer(r"github/codeql-action/\w+@(\S+)", workflow.read_text(encoding="utf-8")):
                pinned.add(match.group(1))
        if not pinned:
            self.skipTest("no CodeQL workflow present")
        self.assertEqual(len(pinned), 1, f"codeql-action steps are pinned to different revisions: {sorted(pinned)}")

    def test_dependabot_groups_the_codeql_pair(self):
        config = Path(__file__).resolve().parents[1] / ".github" / "dependabot.yml"
        if not config.exists():
            self.skipTest("no dependabot configuration present")
        self.assertIn("github/codeql-action", config.read_text(encoding="utf-8"),
                      "dependabot must group codeql-action so the pair cannot be split across pull requests")


if __name__ == "__main__":
    unittest.main()
