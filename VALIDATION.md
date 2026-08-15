# Validation

## Current results

- Source regression suite: PASS, 135 tests (1 skipped).
- Full repository validator, `--scope full`: PASS with zero errors.
- PowerShell parser gate: PASS for all Forge-owned scripts.
- Exact native build: PASS with pinned Go 1.23.2 for Windows x64 and Linux x64.
  Two-build reproducibility PASS; packaged and published helpers hash-equal;
  the rebuilt helper reports `SkyrimForge.Native 5.0.1 go` and self-tests PASS.
- Go format, vet, tests and race test: PASS.
- Wheel and source distribution builds: PASS and deterministic.
- MCP static surface: 52 tools, 19 resources, 7 prompts.
- MCP dual-era smoke against the real stdio server: PASS.
  - `server/discover` returns the supported version list, capabilities and
    `serverInfo`, with `resultType: "complete"` and caching hints.
  - A modern `tools/list` carries the mandatory caching hints.
  - An unknown version is refused with code `-32022` and the supported list.
  - The `initialize` handshake still negotiates `2025-11-25`.
  - A legacy result carries none of `resultType`, `ttlMs`, `cacheScope`.
  - Both eras return an identical 52-tool inventory.
- Version source gate: PASS. Seven restatements agree with
  `skyrim_forge/version.py`, and neither the workflow nor the archive builder
  hardcodes a version.
- Distributed integrity: PASS. All 214 manifest entries verify against the tree
  as checked out, and every file declared `eol=crlf` has CRLF endings on disk.
- Skyrim runtime test: UNTESTED. Static validation does not prove gameplay or
  third-party GUI behavior.

## Reproducing the release gate

Report files hash the tree they ship with, so a source change makes the shipped
manifest stale by definition. Run the validator twice: the first pass rewrites
the reports, the second pass is the gate that must return PASS.

```text
python scripts/validate_repository.py --scope full --write-reports
python scripts/validate_repository.py --scope full --write-reports
```

## FOMOD false positives (5.0.1)

Each case below is legal per the published `ModConfig5.0.xsd` and was rejected
before 5.0.1. Evidence: fixtures built directly from the schema, run against
`validate_fomod`, failing before the fix and passing after.

| Case | Before | After |
|---|---|---|
| Option carrying an `<image>` | FAIL "must contain files or conditionFlags in ModuleConfig 5.0 order" | PASS |
| `xsi:noNamespaceSchemaLocation` omitted | FAIL "must use the canonical schema-location token" | PASS + warning |
| Schema location spelled with `https` | FAIL | PASS, no comment |
| `foseDependency` | FAIL "Unsupported dependency element" | PASS + unverified warning |

The first is the significant one: the schema sequence is `description, image?,
(files, conditionFlags? | conditionFlags, files?), typeDescriptor`, and the
optional image was not allowed for, so any option with a screenshot was refused.

Verified not to be false positives, and left strict: unreferenced payload under
`strict_coverage`, missing source paths, ambiguous destination collisions,
undefined and temporally-unavailable condition flags, path traversal, and C#
scripted installers. Images referenced by `path=` outside `fomod/` were already
counted as covered.

## What this release fixed, and how it was proven

- **Modern MCP clients could not connect.** Proven by the server advertising
  only `2025-11-25`, `2025-06-18` and `2024-11-05`. Now proven fixed by a live
  stdio exchange covering discovery, negotiation, refusal and both eras.
- **`MANIFEST.json` did not verify in a clone.** Reproduced in a clean clone:
  five files (`Install-AI-Bridge.ps1`, `Install-Forge-Skill.ps1`,
  `Install-or-Update.ps1`, `Register-MCP.ps1`, `START-HERE.bat`) hashed
  differently because `.gitattributes` declares `eol=crlf` for them while the
  manifest recorded LF bytes. Now regenerated from the checked-out tree and
  gated by a regression that hashes every manifest entry.
- **CodeQL failed on every Dependabot branch.** Root cause was not permissions:
  `init` and `analyze` were bumped in separate pull requests, so they ran
  different releases and the scan died with "Loaded a configuration file for
  version '4.37.6', but running version '4.36.0'". Both are now pinned to one
  revision, Dependabot groups the pair, and a regression fails if they diverge.

## Evidence boundary

The release is tool-validated. Skyrim gameplay, save behavior, third-party GUI
automation, and visual results remain untested runtime gates.

The modern MCP era is validated against Forge's own stdio server and the
published specification, not against a shipped AI client, because no installed
client speaks `2026-07-28` yet. The legacy era remains the path every currently
registered client uses, and it is unchanged.

The Windows installer, provider MCP re-registration, and the packaged release
archive were not executed in this environment; GitHub CI performs those gates.
