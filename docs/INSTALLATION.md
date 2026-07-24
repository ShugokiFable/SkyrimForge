# Installation

Extract the entire release, run `START-HERE.bat`, install Forge, configure core paths, then configure installed automation tools.

The installer creates a local virtual environment and a `.pth` pointer to the extracted source. No package-index download is required.

Replace the whole Forge directory when changing major versions. Do not copy isolated scripts between versions.

### Startup parser gate

`START-HERE.bat` invokes `PowerShell-Parse-Gate.ps1` without forwarding `%~dp0` as a separate argument. The gate resolves its repository root from `$PSScriptRoot`, avoiding Windows trailing-backslash quote ambiguity. `START-HERE.bat --validate-only` runs this exact startup gate noninteractively for CI and diagnostics.
