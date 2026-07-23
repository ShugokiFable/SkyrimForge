[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$env:PYTHONUTF8 = '1'

function Invoke-Checked {
    param([string]$Label, [string]$Command, [object[]]$Arguments = @())
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Label failed with exit code $LASTEXITCODE." }
}

function Find-Python {
    $Candidates = @()
    if (Get-Command py -ErrorAction SilentlyContinue) { $Candidates += [pscustomobject]@{Exe='py';Args=@('-3')} }
    if (Get-Command python -ErrorAction SilentlyContinue) { $Candidates += [pscustomobject]@{Exe='python';Args=@()} }
    if (Get-Command python3 -ErrorAction SilentlyContinue) { $Candidates += [pscustomobject]@{Exe='python3';Args=@()} }
    foreach ($Candidate in $Candidates) {
        try {
            $Value = & $Candidate.Exe @($Candidate.Args) -c "import sys; print(sys.version_info.major, sys.version_info.minor)"
            if ($LASTEXITCODE -eq 0) {
                $Parts = $Value.Trim() -split '\s+'
                if ([int]$Parts[0] -gt 3 -or ([int]$Parts[0] -eq 3 -and [int]$Parts[1] -ge 11)) { return $Candidate }
            }
        } catch {}
    }
    throw 'Python 3.11 or newer was not found.'
}

$Python = Find-Python
$env:SKYRIM_FORGE_BOOTSTRAP_ROOT = $Root
$ExpectedVersion = (& $Python.Exe @($Python.Args) -c "import os,sys; sys.path.insert(0, os.environ['SKYRIM_FORGE_BOOTSTRAP_ROOT']); from skyrim_forge.version import VERSION; print(VERSION)").Trim()
if (-not $ExpectedVersion) { throw 'Could not read the bundled Forge version.' }
$Native = Join-Path $Root 'writer\published\win-x64\SkyrimForge.Native.exe'
if (-not (Test-Path -LiteralPath $Native -PathType Leaf)) { throw "Bundled native helper is missing: $Native" }
$ExpectedNative = "SkyrimForge.Native $ExpectedVersion go"
$ActualNative = (& $Native version | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $ActualNative -cne $ExpectedNative) { throw "Native helper version check failed. Expected '$ExpectedNative'; got '$ActualNative'." }
Invoke-Checked 'Native helper self-test' $Native @('self-test')

$Venv = Join-Path $Root '.venv'
$VenvPython = Join-Path $Venv 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $VenvPython -PathType Leaf)) {
    Invoke-Checked 'Virtual environment creation' $Python.Exe (@($Python.Args) + @('-m','venv',$Venv))
}
& $VenvPython -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)"
if ($LASTEXITCODE -ne 0) { throw 'Forge virtual environment is not Python 3.11 or newer.' }
$SitePackages = (& $VenvPython -c "import sysconfig; print(sysconfig.get_paths()['purelib'])").Trim()
if (-not $SitePackages) { throw 'Could not resolve virtual-environment site-packages.' }
$Pth = Join-Path $SitePackages 'skyrim_forge_local.pth'
$Temp = "$Pth.stage-$([Guid]::NewGuid().ToString('N'))"
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
try {
    [IO.File]::WriteAllText($Temp, $Root + [Environment]::NewLine, $Utf8NoBom)
    Move-Item -LiteralPath $Temp -Destination $Pth -Force
} finally { Remove-Item -LiteralPath $Temp -Force -ErrorAction SilentlyContinue }

Invoke-Checked 'Forge version check' $VenvPython @('-m','skyrim_forge','version')
Invoke-Checked 'Forge regression self-test' $VenvPython @('-m','skyrim_forge','self-test')
Invoke-Checked 'Forge configuration migration' $VenvPython @('-m','skyrim_forge','config-show')
Invoke-Checked 'Forge doctor' $VenvPython @('-m','skyrim_forge','doctor')

Write-Host ''
Write-Host "Skyrim Forge $ExpectedVersion installed." -ForegroundColor Green
Write-Host "Config: $HOME\.skyrim-forge\config.toml"
Write-Host 'External tools and UI Automation remain disabled until explicitly configured.'
