# Decisions

- Preserve 4.2.4 and install 4.2.5 beside it.
- Bootstrap only after the user selects installation or passes `-BootstrapPython`.
- Download only a pinned official Python installer, then verify SHA-256 and Authenticode before execution.
- Use one shared Forge `.venv` for all AI clients.
- Install a machine-readable `INSTALLATION.json` beside each provider skill so no provider needs a guessed path or `PYTHONPATH`.
- Register MCP only through a locally verified provider command surface. Kimi and Hermes remain full CLI/skill consumers when their installed clients do not expose MCP registration.
- Preserve PowerShell 5 compatibility for Grok registration by using an explicit process argument vector.
- Treat the configured tools root as read-only and import only unambiguous non-GUI adapters into the private tool vault.
- Pin configured third-party tools by exact executable hash; never launch a GUI merely to prove configuration.
