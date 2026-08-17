from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POWERSHELL = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"


@unittest.skipUnless(os.name == "nt", "Windows provider bridge")
class WindowsProviderBridgeTests(unittest.TestCase):
    def run_script(self, script: Path, *arguments: str, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(POWERSHELL), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), *arguments],
            text=True,
            capture_output=True,
            env=env,
            timeout=60,
            check=False,
        )

    def test_hermes_skill_defaults_to_local_app_data(self):
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            fixture = temp / "forge"
            source = fixture / "integrations" / "skyrim-forge"
            source.mkdir(parents=True)
            shutil.copy2(ROOT / "Install-Forge-Skill.ps1", fixture / "Install-Forge-Skill.ps1")
            (source / "SKILL.md").write_text("---\nname: skyrim-forge\n---\n", encoding="utf-8")
            (fixture / "INSTALLATION.json").write_text(
                json.dumps({"root": str(fixture), "python": sys.executable}), encoding="utf-8"
            )
            profile = temp / "profile"
            local = temp / "local"
            profile.mkdir()
            local.mkdir()
            env = os.environ.copy()
            env.update({"USERPROFILE": str(profile), "LOCALAPPDATA": str(local), "HERMES_HOME": ""})
            result = self.run_script(fixture / "Install-Forge-Skill.ps1", "-Provider", "Hermes", env=env)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((local / "hermes" / "skills" / "skyrim-forge" / "INSTALLATION.json").is_file())
            self.assertFalse((profile / ".hermes" / "skills" / "skyrim-forge").exists())

    def require_installed_test_runtime(self) -> Path:
        python = ROOT / ".venv" / "Scripts" / "python.exe"
        if not python.is_file():
            self.skipTest("Register-MCP integration requires the installed Forge test runtime")
        return python

    def test_kimi_registration_preserves_other_servers_and_writes_forge(self):
        python = self.require_installed_test_runtime()
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            kimi_home = temp / "kimi"
            kimi_home.mkdir()
            config = kimi_home / "mcp.json"
            config.write_text(json.dumps({"mcpServers": {"keep": {"command": "keep.exe", "args": []}}}), encoding="utf-8")
            fake_bin = temp / "bin"
            fake_bin.mkdir()
            (fake_bin / "kimi.cmd").write_text("@exit /b 0\n", encoding="ascii")
            report = temp / "report.json"
            env = os.environ.copy()
            env.update({"KIMI_CODE_HOME": str(kimi_home), "PATH": str(fake_bin) + os.pathsep + env["PATH"]})
            result = self.run_script(
                ROOT / "Register-MCP.ps1", "-Provider", "Kimi", "-Yes", "-ReportPath", str(report), env=env
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            written = json.loads(config.read_text(encoding="utf-8-sig"))["mcpServers"]
            self.assertEqual(written["keep"], {"command": "keep.exe", "args": []})
            self.assertEqual(written["skyrim-forge"]["command"], str(python))
            self.assertEqual(written["skyrim-forge"]["args"], ["-m", "skyrim_forge", "mcp"])
            provider = json.loads(report.read_text(encoding="utf-8-sig"))["providers"][0]
            self.assertEqual((provider["mode"], provider["status"]), ("mcp", "READY"))

    def test_kimi_doctor_failure_restores_original_configuration(self):
        self.require_installed_test_runtime()
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            kimi_home = temp / "kimi"
            kimi_home.mkdir()
            config = kimi_home / "mcp.json"
            original = '{"mcpServers":{"keep":{"command":"keep.exe","args":[]}}}\n'
            config.write_text(original, encoding="utf-8")
            fake_bin = temp / "bin"
            fake_bin.mkdir()
            (fake_bin / "kimi.cmd").write_text("@exit /b 7\n", encoding="ascii")
            report = temp / "report.json"
            env = os.environ.copy()
            env.update({"KIMI_CODE_HOME": str(kimi_home), "PATH": str(fake_bin) + os.pathsep + env["PATH"]})
            result = self.run_script(
                ROOT / "Register-MCP.ps1", "-Provider", "Kimi", "-Yes", "-ReportPath", str(report), env=env
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(config.read_text(encoding="utf-8"), original)
            provider = json.loads(report.read_text(encoding="utf-8-sig"))["providers"][0]
            self.assertEqual((provider["mode"], provider["status"]), ("mcp", "FAILED"))

    def test_kimi_rejects_array_shaped_server_map_without_overwriting(self):
        self.require_installed_test_runtime()
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            kimi_home = temp / "kimi"
            kimi_home.mkdir()
            config = kimi_home / "mcp.json"
            original = '{"mcpServers":[{"keep":{"command":"keep.exe","args":[]}}]}\n'
            config.write_text(original, encoding="utf-8")
            fake_bin = temp / "bin"
            fake_bin.mkdir()
            (fake_bin / "kimi.cmd").write_text("@exit /b 0\n", encoding="ascii")
            report = temp / "report.json"
            env = os.environ.copy()
            env.update({"KIMI_CODE_HOME": str(kimi_home), "PATH": str(fake_bin) + os.pathsep + env["PATH"]})
            result = self.run_script(
                ROOT / "Register-MCP.ps1", "-Provider", "Kimi", "-Yes", "-ReportPath", str(report), env=env
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(config.read_text(encoding="utf-8"), original)
            provider = json.loads(report.read_text(encoding="utf-8-sig"))["providers"][0]
            self.assertEqual((provider["mode"], provider["status"]), ("mcp", "FAILED"))

    def test_hermes_registration_uses_supported_cli_and_tests_connection(self):
        python = self.require_installed_test_runtime()
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            fake_bin = temp / "bin"
            fake_bin.mkdir()
            call_log = temp / "hermes-calls.txt"
            (fake_bin / "hermes.cmd").write_text('@echo %*>>"%FAKE_HERMES_LOG%"\n@exit /b 0\n', encoding="ascii")
            report = temp / "report.json"
            env = os.environ.copy()
            env.update({
                "HERMES_HOME": str(temp / "hermes-home"),
                "FAKE_HERMES_LOG": str(call_log),
                "PATH": str(fake_bin) + os.pathsep + env["PATH"],
            })
            result = self.run_script(
                ROOT / "Register-MCP.ps1", "-Provider", "Hermes", "-Yes", "-ReportPath", str(report), env=env
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            calls = call_log.read_text(encoding="utf-8").splitlines()
            self.assertIn(f"mcp add skyrim-forge --command {python} --args -m skyrim_forge mcp", calls)
            self.assertIn("mcp test skyrim-forge", calls)
            provider = json.loads(report.read_text(encoding="utf-8-sig"))["providers"][0]
            self.assertEqual((provider["mode"], provider["status"]), ("mcp", "READY"))

    def test_hermes_test_failure_restores_original_configuration(self):
        self.require_installed_test_runtime()
        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            hermes_home = temp / "hermes-home"
            hermes_home.mkdir()
            config = hermes_home / "config.yaml"
            original = "mcp_servers:\n  keep:\n    command: keep.exe\n"
            config.write_text(original, encoding="utf-8")
            fake_bin = temp / "bin"
            fake_bin.mkdir()
            (fake_bin / "hermes.cmd").write_text(
                '@if "%1 %2"=="mcp add" echo modified>"%HERMES_HOME%\\config.yaml"\n'
                '@if "%1 %2"=="mcp test" exit /b 9\n'
                '@exit /b 0\n',
                encoding="ascii",
            )
            report = temp / "report.json"
            env = os.environ.copy()
            env.update({"HERMES_HOME": str(hermes_home), "PATH": str(fake_bin) + os.pathsep + env["PATH"]})
            result = self.run_script(
                ROOT / "Register-MCP.ps1", "-Provider", "Hermes", "-Yes", "-ReportPath", str(report), env=env
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(config.read_text(encoding="utf-8"), original)
            provider = json.loads(report.read_text(encoding="utf-8-sig"))["providers"][0]
            self.assertEqual((provider["mode"], provider["status"]), ("mcp", "FAILED"))


if __name__ == "__main__":
    unittest.main()
