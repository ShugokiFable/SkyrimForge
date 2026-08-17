# Plan

1. [complete] Resolve the authoritative source from the public repository and
   treat the supplied 5.1.0 folder as an installed, read-only comparison.
2. [complete] Compare the installed tree with the published 5.1.0 commit and
   reproduce the MCP/provider failures with focused regression tests.
3. [complete] Route Papyrus compilation through MCP, add native Kimi and Hermes
   MCP registration, and correct Hermes provider-home discovery.
4. [complete] Bump the versioned snapshot to 5.1.1, rebuild exact native
   helpers, run the full validator twice, and create a deterministic archive.
5. [pending] Publish to `main`, create the GitHub release, and install/repoint
   live provider clients only after the user explicitly approves those
   irreversible actions.
