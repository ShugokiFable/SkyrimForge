# Plan

1. [complete] Read the `2026-07-28` specification directly and record the exact
   wire contracts for `server/discover`, per-request `_meta` version
   negotiation, `UnsupportedProtocolVersionError`, mandatory caching hints, and
   the stdio backward-compatibility probe. No protocol behaviour written from
   memory.
2. [complete] Make the MCP server dual-era: serve the modern revision
   statelessly while `initialize` still selects legacy semantics, so already
   registered Codex, Claude and Grok clients keep working unchanged.
3. [complete] Prove the integrity evidence where users obtain it. Reproduce the
   `MANIFEST.json` verification failure in a clean clone, fix the cause, and add
   a regression that fails if the shipped manifest stops matching its tree.
4. [complete] Collapse the version restatements to one source of truth, gate the
   remaining copies against it, and stop CI hardcoding the native version string.
5. [complete] Fix the CodeQL configuration error, group the action pair in
   Dependabot so it cannot recur, and apply the four blocked action updates.
6. [complete] Rebuild native helpers with pinned Go 1.23.2, regenerate release
   evidence, and require a clean full validation at 5.0.0.
