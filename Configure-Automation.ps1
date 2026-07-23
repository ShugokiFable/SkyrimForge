[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$Python = Join-Path $Root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) { throw 'Install Forge first.' }
$Tools = @(
    @{Name='xedit';Label='SSEEdit64.exe'},
    @{Name='mo2';Label='ModOrganizer.exe'},
    @{Name='loot';Label='LOOT.exe'},
    @{Name='wrye_bash';Label='Wrye Bash.exe'},
    @{Name='creation_kit';Label='CreationKit.exe'},
    @{Name='ckpe_loader';Label='ckpe_loader.exe'},
    @{Name='papyrus_compiler';Label='PapyrusCompiler.exe'},
    @{Name='archive';Label='Archive.exe / BSArch.exe / 7z.exe'}
)
Write-Host 'Configure only tools installed on this machine. Blank entries are preserved.' -ForegroundColor Cyan
foreach ($Tool in $Tools) {
    $Path = Read-Host "$($Tool.Label) path"
    if ($Path) {
        & $Python -m skyrim_forge config-set "tools.$($Tool.Name).executable" $Path
        if ($LASTEXITCODE) { throw "$($Tool.Name) configuration failed." }
        $Pin = Read-Host "Pin SHA-256 for $($Tool.Name)? [y/N]"
        if ($Pin -match '^(?i:y|yes)$') {
            $Hash = (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
            & $Python -m skyrim_forge config-set "tools.$($Tool.Name).sha256" $Hash
        }
    }
}
$UI = Read-Host 'Configure coordinate-free Windows UI Automation fallback? [y/N]'
if ($UI -match '^(?i:y|yes)$') {
    $PowerShellExe = Join-Path $PSHOME 'powershell.exe'
    & $Python -m skyrim_forge config-set tools.ui_worker.executable $PowerShellExe
    $WorkerScript = Join-Path $Root 'workers\SkyrimForge.UIWorker.ps1'
    & $Python -m skyrim_forge config-set tools.ui_worker.worker $WorkerScript
    $WorkerHash = (Get-FileHash -LiteralPath $WorkerScript -Algorithm SHA256).Hash.ToLowerInvariant()
    & $Python -m skyrim_forge config-set tools.ui_worker.worker_sha256 $WorkerHash
    & $Python -m skyrim_forge config-set allow_ui_automation true
}
& $Python -m skyrim_forge doctor
