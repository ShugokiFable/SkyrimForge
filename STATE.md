# State

- Active version: 4.2.5
- Parent: v4.2.4 at 38cf10e
- Original symptom: `.venv\Scripts\python.exe` absent and no Python 3.11+ on `PATH`
- Secondary symptom: missing provider fallback configs and MCP automation limited to Codex/Claude
- Runtime status: installed runtime and MCP protocol are tool-validated
- Preserved rollback release: 4.2.4
- Active installed successor: 4.2.5
- Shared runtime: `.venv\Scripts\python.exe`
- AI integrations: Codex MCP ready; Grok MCP ready; Kimi and Hermes skill/CLI ready; Claude skill installed but client absent
- MCP smoke result: protocol `2025-11-25`, server 4.2.5, 52 tools
- Toolchain: supported discovered adapters are exact-path and SHA-256 pinned; GUI and runtime outcomes remain external gates
- Repository validation: PASS, 119 tests
- Deterministic archive comparison: PASS, 219 clean entries
- Negative install without Python or bootstrap approval: PASS; no `.venv` was created and the installer gave the exact recovery command
- Remaining runtime boundary: Skyrim gameplay and third-party GUI behavior are not proven by static/tool validation
