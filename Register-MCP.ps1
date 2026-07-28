[CmdletBinding()]
param(
    [ValidateSet('All', 'Codex', 'Claude', 'Grok', 'Kimi', 'Hermes')]
    [string]$Provider = 'All',
    [switch]$Yes,
    [string]$ReportPath = ''
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$Python = Join-Path $Root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) { throw 'Install Forge first.' }

function Ask {
    param([string]$Text)
    if ($Yes) { return $true }
    return (Read-Host "$Text [y/N]") -match '^(?i:y|yes)$'
}

function Resolve-ProviderCommand {
    param([string]$Name)
    if ($Name -eq 'Codex') {
        $CodexBin = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'OpenAI\Codex\bin'
        if (Test-Path -LiteralPath $CodexBin) {
            $Direct = @(Get-ChildItem -LiteralPath $CodexBin -Recurse -Filter 'codex.exe' -File -ErrorAction SilentlyContinue |
                Sort-Object LastWriteTime -Descending |
                Select-Object -ExpandProperty FullName)
            if ($Direct.Count -gt 0) { return $Direct[0] }
        }
    }
    if ($Name -eq 'Grok') {
        $GrokDirect = Join-Path ([Environment]::GetFolderPath('UserProfile')) '.grok\bin\grok.exe'
        if (Test-Path -LiteralPath $GrokDirect -PathType Leaf) { return $GrokDirect }
    }
    $Command = Get-Command $Name.ToLowerInvariant() -ErrorAction SilentlyContinue
    if ($Command) { return $Command.Source }
    return $null
}

function Invoke-Registration {
    param([string]$Name)
    if ($Name -in @('Kimi', 'Hermes')) {
        return [ordered]@{
            provider = $Name
            mode = 'skill-cli'
            status = 'READY'
            command = $null
            detail = 'The supported local client has no verified MCP registrar. Forge remains available through the installed skill and exact CLI descriptor.'
        }
    }
    $Executable = Resolve-ProviderCommand -Name $Name
    if (-not $Executable) {
        return [ordered]@{
            provider = $Name
            mode = 'mcp'
            status = 'NOT_INSTALLED'
            command = $null
            detail = 'Provider command was not found. The installed skill still contains the exact Forge CLI and MCP launch descriptor.'
        }
    }
    if (-not (Ask -Text "Register Skyrim Forge MCP with ${Name}?")) {
        return [ordered]@{
            provider = $Name
            mode = 'mcp'
            status = 'SKIPPED'
            command = $Executable
            detail = 'Registration was not approved.'
        }
    }
    try {
        switch ($Name) {
            'Codex' {
                & $Executable mcp remove skyrim-forge 2>$null | Out-Null
                & $Executable mcp add skyrim-forge -- $Python -m skyrim_forge mcp | Out-Null
                if ($LASTEXITCODE -ne 0) { throw "Codex registration exited $LASTEXITCODE." }
                & $Executable mcp get skyrim-forge | Out-Null
                if ($LASTEXITCODE -ne 0) { throw "Codex verification exited $LASTEXITCODE." }
            }
            'Claude' {
                & $Executable mcp remove skyrim-forge -s user 2>$null | Out-Null
                & $Executable mcp add --transport stdio --scope user skyrim-forge -- $Python -m skyrim_forge mcp | Out-Null
                if ($LASTEXITCODE -ne 0) { throw "Claude registration exited $LASTEXITCODE." }
            }
            'Grok' {
                & $Executable mcp remove skyrim-forge 2>$null | Out-Null
                # Windows PowerShell 5 rewrites native `--` boundaries when the
                # executable is invoked through a variable. Start-Process keeps
                # Grok's documented separator and Python's `-m` as server args.
                $GrokArguments = @(
                    'mcp', 'add', '--scope', 'user', 'skyrim-forge', '--',
                    ('"' + $Python + '"'), '-m', 'skyrim_forge', 'mcp'
                )
                $GrokProcess = Start-Process -FilePath $Executable -ArgumentList $GrokArguments -NoNewWindow -Wait -PassThru
                if ($GrokProcess.ExitCode -ne 0) { throw "Grok registration exited $($GrokProcess.ExitCode)." }
                $GrokServers = @((& $Executable mcp list --json | ConvertFrom-Json))
                if ($LASTEXITCODE -ne 0) { throw "Grok MCP list exited $LASTEXITCODE." }
                $GrokForge = @($GrokServers | Where-Object {
                    $_.name -eq 'skyrim-forge' -and
                    $_.command -eq $Python -and
                    (@($_.args) -join ' ') -eq '-m skyrim_forge mcp' -and
                    $_.enabled
                })
                if ($GrokForge.Count -ne 1) { throw 'Grok MCP verification did not return the exact enabled Forge command.' }
            }
        }
        return [ordered]@{
            provider = $Name
            mode = 'mcp'
            status = 'READY'
            command = $Executable
            detail = 'MCP registration and provider verification passed.'
        }
    } catch {
        return [ordered]@{
            provider = $Name
            mode = 'mcp'
            status = 'FAILED'
            command = $Executable
            detail = $_.Exception.Message
        }
    }
}

$Selected = if ($Provider -eq 'All') {
    @('Codex', 'Claude', 'Grok', 'Kimi', 'Hermes')
} else {
    @($Provider)
}
$Results = @()
foreach ($Name in $Selected) {
    $Result = Invoke-Registration -Name $Name
    $Results += $Result
    $Color = if ($Result.status -eq 'READY') { 'Green' } elseif ($Result.status -eq 'FAILED') { 'Red' } else { 'Yellow' }
    Write-Host ('{0}: {1} ({2})' -f $Name, $Result.status, $Result.mode) -ForegroundColor $Color
    Write-Host ('  {0}' -f $Result.detail)
}

if (-not $ReportPath) { $ReportPath = Join-Path $Root 'REPORTS\ai-integration.json' }
$ReportPath = [IO.Path]::GetFullPath($ReportPath)
$ReportDirectory = Split-Path -Parent $ReportPath
New-Item -ItemType Directory -Force -Path $ReportDirectory | Out-Null
$Version = (& $Python -m skyrim_forge version | ConvertFrom-Json).version
$Report = [ordered]@{
    product = 'Skyrim Forge'
    version = $Version
    root = $Root
    python = $Python
    mcp_command = @($Python, '-m', 'skyrim_forge', 'mcp')
    providers = @($Results)
}
$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[IO.File]::WriteAllText($ReportPath, ($Report | ConvertTo-Json -Depth 8) + [Environment]::NewLine, $Utf8NoBom)
Write-Host "Integration report: $ReportPath"

if (@($Results | Where-Object { $_.status -eq 'FAILED' }).Count -gt 0) {
    throw 'One or more installed-provider MCP registrations failed. See the integration report.'
}
