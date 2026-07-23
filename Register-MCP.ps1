[CmdletBinding()]
param()
$ErrorActionPreference='Stop'
$Root=$PSScriptRoot
$Python=Join-Path $Root '.venv\Scripts\python.exe'
if(-not(Test-Path $Python)){throw 'Install Forge first.'}
function Ask([string]$Text){(Read-Host "$Text [y/N]") -match '^(?i:y|yes)$'}
if((Get-Command codex -ErrorAction SilentlyContinue) -and (Ask 'Register with Codex CLI?')){& codex mcp remove skyrim-forge 2>$null|Out-Null;& codex mcp add skyrim-forge -- $Python -m skyrim_forge mcp;if($LASTEXITCODE){Write-Warning 'Codex registration failed; use integrations/codex-config.toml.'}}
if((Get-Command claude -ErrorAction SilentlyContinue) -and (Ask 'Register with Claude Code?')){& claude mcp remove skyrim-forge -s user 2>$null|Out-Null;& claude mcp add --transport stdio --scope user skyrim-forge -- $Python -m skyrim_forge mcp;if($LASTEXITCODE){Write-Warning 'Claude registration failed; use integrations/claude-project.mcp.json.'}}
Write-Host 'Kimi, Grok, Hermes, and desktop examples are under integrations\.'
