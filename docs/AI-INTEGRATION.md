# AI integration

Forge 4.2.5 uses one installed runtime for every AI client:

```text
<FORGE_ROOT>\.venv\Scripts\python.exe -m skyrim_forge
```

`Install-AI-Bridge.ps1` performs four gates:

1. install or update the shared Forge runtime;
2. install the Forge skill into each selected provider home;
3. register the stdio MCP server where the installed provider exposes a verified registrar;
4. run Forge doctor and write `REPORTS\ai-integration.json`.

Each installed skill contains `INSTALLATION.json`. Its `cli` and `mcp` arrays
are the authoritative machine-local launch commands. This avoids relying on
`PATH`, a guessed drive, or a provider-specific `PYTHONPATH`.

| Provider | Skill | MCP registration |
|---|---:|---:|
| Codex | yes | `codex mcp` when installed |
| Claude | yes | `claude mcp` when installed |
| Grok | yes | `grok mcp` when installed |
| Kimi | yes | skill/CLI; no verified local MCP registrar |
| Hermes | yes | skill/CLI; no verified local MCP registrar |

An absent provider is reported as `NOT_INSTALLED`; it does not make Forge
unhealthy. A detected provider whose registration fails is reported as
`FAILED` and makes the integration command fail.

External Skyrim tools remain separately configured, hash-pinned, and disabled
until approved. Provider registration does not grant permission to write to
game `Data`, mod-manager staging, profiles, saves, or reference vaults.
