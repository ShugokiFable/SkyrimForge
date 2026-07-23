[CmdletBinding()]
param([ValidateSet('All','Codex','Claude','Grok','Kimi','Hermes')][string]$Provider='All')
$ErrorActionPreference='Stop'
$Root=$PSScriptRoot
$Source=Join-Path $Root 'integrations\skyrim-forge'
$Selected=if($Provider -eq 'All'){@('Codex','Claude','Grok','Kimi','Hermes')}else{@($Provider)}
function HomeFor([string]$Name){switch($Name){
 'Codex'{if($env:CODEX_HOME){$env:CODEX_HOME}else{Join-Path $HOME '.codex'}}
 'Claude'{if($env:CLAUDE_CONFIG_DIR){$env:CLAUDE_CONFIG_DIR}else{Join-Path $HOME '.claude'}}
 'Grok'{if($env:GROK_HOME){$env:GROK_HOME}else{Join-Path $HOME '.grok'}}
 'Kimi'{if($env:KIMI_CODE_HOME){$env:KIMI_CODE_HOME}else{Join-Path $HOME '.kimi-code'}}
 'Hermes'{if($env:HERMES_HOME){$env:HERMES_HOME}else{Join-Path $HOME '.hermes'}}
}}
foreach($Name in $Selected){
 $Skills=Join-Path (HomeFor $Name) 'skills'; $Target=Join-Path $Skills 'skyrim-forge'; New-Item -ItemType Directory -Force -Path $Skills|Out-Null
 $Stage=Join-Path $Skills ('.skyrim-forge.stage-'+[Guid]::NewGuid().ToString('N'))
 try{Copy-Item -LiteralPath $Source -Destination $Stage -Recurse; if(Test-Path $Target){Remove-Item $Target -Recurse -Force}; Move-Item $Stage $Target}
 finally{Remove-Item $Stage -Recurse -Force -ErrorAction SilentlyContinue}
 Write-Host "$Name: $Target" -ForegroundColor Green
}
