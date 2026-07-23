# Configuration

Forge stores user configuration at `%USERPROFILE%\.skyrim-forge\config.toml` by default.

Tool entries support:

- `executable`
- `worker`
- `sha256`
- `version`
- `timeout_seconds`

Use the menu configurators or `forge config-set`. Executable hashes are strongly recommended for xEdit workers and any internal Wrye Bash or Creation Kit worker.

## Legacy Papyrus migration

Forge 3.0.1 accepts Forge 2.x `[papyrus]` tables. It moves `compiler` into `[tools.papyrus_compiler]`, preserves `flags` and `imports`, writes a canonical configuration, and creates `config.toml.pre-3.0.1.bak` before replacing the legacy layout.
