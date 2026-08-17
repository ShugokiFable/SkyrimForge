# State

- Active version: 5.1.1 release candidate
- Parent: v5.1.0 at df5aba7
- Authoritative owner: `https://github.com/ShugokiFable/SkyrimForge`, branch
  `main`
- Preserved installed release: `Skyrim-Forge-5.1.0`
- Original MCP symptom: `forge_papyrus_compile` appeared in `tools/list` but
  had no dispatch case, so every call failed as an unknown tool
- Provider symptom: Kimi and Hermes were reported as skill-only even though
  both installed clients support MCP
- Provider-home symptom: Hermes skills defaulted to `%USERPROFILE%\.hermes`,
  but the installed application uses `%LOCALAPPDATA%\hermes`
- Shared runtime: `.venv\Scripts\python.exe`; no provider-specific environment
- Kimi approach: preserve all existing `mcpServers`, replace only
  `skyrim-forge`, then run `kimi doctor`
- Hermes approach: use `hermes mcp add` and require
  `hermes mcp test skyrim-forge`
- Targeted regressions: PASS, including byte-exact Kimi rollback on failure
- Full repository validation: PASS, 149 tests
- Native helpers: rebuilt reproducibly with pinned Go 1.23.2 for Windows x64
  and Linux x64
- Live client audit: Codex, Grok, and Kimi point to the exact installed 5.1.0
  MCP command; Hermes is installed but has no Forge MCP entry; Claude is absent
- Live client configuration was not changed and the 5.1.1 candidate is not
  installed or published
- Runtime boundary: Skyrim gameplay and third-party GUI behavior remain outside
  this bridge-only release
