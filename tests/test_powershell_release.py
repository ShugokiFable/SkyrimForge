from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def owned_powershell_scripts(root: Path) -> list[Path]:
    scripts = [*root.glob('*.ps1')]
    workers = root / 'workers'
    if workers.is_dir():
        scripts.extend(workers.glob('*.ps1'))
    return sorted(set(scripts))


class PowerShellReleaseTests(unittest.TestCase):
    def test_no_expandable_string_has_ambiguous_variable_before_colon(self):
        bad = re.compile(r'(?<!`)\$(?!\{|\(|(?:env|global|script|local|private|using):)[A-Za-z_][A-Za-z0-9_]*:')
        # Scan only Forge-owned source scripts. Runtime-created environments such as
        # .venv contain upstream activation scripts with valid scoped variables like
        # $Env:PATH and are not part of the release source under test.
        findings = []
        for path in owned_powershell_scripts(ROOT):
            text = path.read_text(encoding='utf-8-sig')
            for line_number, line in enumerate(text.splitlines(), 1):
                for match in re.finditer(r'"(?:`.|[^"\r\n])*"', line):
                    invalid = bad.search(match.group(0))
                    if invalid:
                        findings.append(f'{path.relative_to(ROOT)}:{line_number}:{invalid.group(0)}')
        self.assertEqual(findings, [])

    def test_runtime_virtualenv_scripts_are_not_release_sources(self):
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'Top.ps1').write_text('Write-Host ok', encoding='utf-8')
            workers = root / 'workers'; workers.mkdir()
            (workers / 'Worker.ps1').write_text('Write-Host ok', encoding='utf-8')
            venv = root / '.venv' / 'Scripts'; venv.mkdir(parents=True)
            (venv / 'Activate.ps1').write_text('$Env:PATH', encoding='utf-8')
            relative = [path.relative_to(root).as_posix() for path in owned_powershell_scripts(root)]
            self.assertEqual(relative, ['Top.ps1', 'workers/Worker.ps1'])

    def test_skill_installer_is_transactional_and_uses_safe_formatting(self):
        text = (ROOT / 'Install-Forge-Skill.ps1').read_text(encoding='utf-8-sig')
        self.assertIn("Write-Host ('{0}: {1}' -f $Name, $Target)", text)
        self.assertIn('.skyrim-forge.stage-', text)
        self.assertIn('.skyrim-forge.backup-', text)
        self.assertIn('Staged Forge skill validation failed', text)
        self.assertNotIn('"$Name: $Target"', text)

    def test_batch_files_never_pass_quoted_dp0_as_a_standalone_external_argument(self):
        bad = re.compile(r'"%~dp0"(?=\s|$)', re.I)
        findings = []
        for path in sorted([*ROOT.glob('*.bat'), *ROOT.glob('*.cmd')]):
            for line_number, line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
                stripped = line.strip()
                if bad.search(line) and not re.match(r'(?i)^(?:cd|pushd)\b', stripped):
                    findings.append(f'{path.name}:{line_number}:{line}')
        self.assertEqual(findings, [])

    def test_start_menu_uses_gate_default_root_and_has_noninteractive_ci_probe(self):
        start = (ROOT / 'START-HERE.bat').read_text(encoding='utf-8-sig')
        tests = (ROOT / 'Run Tests.bat').read_text(encoding='utf-8-sig')
        self.assertIn('-File "%FORGE_PS_GATE%"', start)
        self.assertNotIn('-Root "%~dp0"', start)
        self.assertNotIn('-Root "%~dp0"', tests)
        self.assertIn('if /I "%~1"=="--validate-only" exit /b 0', start)
        self.assertIn('PowerShell-Parse-Gate.ps1', tests)

    def test_parser_gate_defaults_to_its_own_directory_and_sanitizes_legacy_quote(self):
        gate = (ROOT / 'PowerShell-Parse-Gate.ps1').read_text(encoding='utf-8-sig')
        self.assertIn("[string]$Root = ''", gate)
        self.assertIn('$PSScriptRoot', gate)
        self.assertIn("$Root.Trim().Trim([char]34)", gate)
        self.assertIn('Resolve-Path -LiteralPath $CandidateRoot', gate)


if __name__ == '__main__':
    unittest.main()
