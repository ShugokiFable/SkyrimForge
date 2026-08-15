# State

- Active version: 5.0.1
- Parent: v5.0.0 at 1c04f12
- Original symptom: FOMOD validation rejected installers that are legal per the
  published ModConfig5.0 schema, most importantly any option carrying a
  screenshot
- Secondary symptom: the published `MANIFEST.json` did not verify against a
  `git clone` of the repository it shipped in
- Tertiary symptom: every CodeQL run on a Dependabot branch failed with a
  configuration error, blocking four open pull requests
- Runtime status: repository validation and MCP protocol behaviour are
  tool-validated
- Preserved rollback release: 5.0.0
- Shared runtime: `.venv\Scripts\python.exe`
- MCP era support: dual-era. `server/discover`, per-request `_meta` version
  negotiation and `UnsupportedProtocolVersionError` for `2026-07-28`; the
  `initialize` handshake is retained unchanged for `2025-11-25`, `2025-06-18`
  and `2024-11-05`
- MCP smoke result: 52 tools identical across both eras; legacy results carry
  no modern-only fields
- Version sources: one source of truth in `skyrim_forge/version.py`; seven
  restatements are gated against it and CI derives the native version string
  instead of hardcoding it
- Repository validation: PASS, 135 tests
- Native helpers: rebuilt with pinned Go 1.23.2; two-build reproducibility PASS
  for Windows x64 and Linux x64; packaged and published copies hash-equal
- Remaining runtime boundary: Skyrim gameplay and third-party GUI behavior are
  not proven by static or tool validation
- Not exercised in this build: the Windows installer path, provider MCP
  re-registration, and any live AI client speaking the modern revision. The
  modern era is proven against the real stdio server, not against a shipped
  client, because no installed client speaks `2026-07-28` yet.
