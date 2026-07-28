# Validation

## Current results

- Source regression suite: PASS.
- PowerShell parser gate: PASS for all Forge-owned scripts.
- Exact native build: PASS with Go 1.23.2 for Windows x64 and Linux x64.
- Installed `version`, `self-test`, and `doctor`: PASS.
- Installed MCP protocol smoke: PASS; initialize and `tools/list` returned server 4.2.5 and 52 tools.
- Codex MCP registration: PASS with the exact shared `.venv` interpreter.
- Grok MCP registration: PASS with the exact shared `.venv` interpreter.
- Kimi and Hermes: PASS through installed skill/CLI descriptors; their installed clients expose no verified MCP registrar.
- Claude: client not installed; the provider skill and installation descriptor are present.
- Five provider skill descriptors: PASS; all match the root `INSTALLATION.json`.
- Hash-pinned capability resolution: PASS for BSArch, official Papyrus compilation, Champollion, DeadMesh, xEdit, texconv, DynDOLOD, and xLODGen.
- Skyrim runtime test: UNTESTED. Static validation does not prove gameplay or third-party GUI behavior.

## Final release gates

- Full repository validator: PASS, 119 tests, 214 source files.
- Python compilation and built-in self-test: PASS.
- Go format, vet, tests, race test, and two-build reproducibility: PASS.
- Wheel and source distribution builds: PASS.
- MCP static surface: PASS, 52 tools, 19 resources, and 7 prompts.
- Two-build deterministic release archive comparison: PASS.
- Release archive exclusions: PASS; no `.venv`, `INSTALLATION.json`, `REPORTS`, or `.go-cache` entries.
- Fresh extracted archive without Python or bootstrap approval: expected FAIL; no `.venv` was created and the error directed the user to `START-HERE.bat` or `-BootstrapPython`.
- PowerShell execution-policy-independent launch path: PASS through the shipped batch/explicit bypass entry point.

## Evidence boundary

The release is tool-validated. Skyrim gameplay, save behavior, third-party GUI
automation, and visual results remain untested runtime gates.
