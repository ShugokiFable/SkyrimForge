# Changelog

## 4.2.0

- Added the Verified Toolchain Broker with recursive ZIP/directory discovery, including nested tools such as BSArch inside ESLifier.
- Added transactional local tool-vault import, runtime-closure preservation, receipts, provenance, and automatic SHA-256 pinning.
- Added exact capability resolution so GUI or similarly named executables cannot be substituted for a dedicated CLI.
- Added direct bounded adapters for BSArch, DeadMesh dmscan, Champollion, and Synthesis.Bethesda.CLI.
- Added BSArch BSA/BA2 routing, Skyrim SE/AE packing, extraction, and reopen verification.
- Added catalog coverage for core Skyrim engineering tools without redistributing third-party or Bethesda binaries.
- Added toolchain CLI, GUI, MCP, doctor, documentation, and regression coverage.
- Fixed the stale 3.0 START-HERE banner.

## 4.1.0

- Added the Nexus Mods publication gate for user requests that intend public or shareable distribution.
- Added file-level rights mapping so every bundled file must be assigned to an original-work, licence, permission, game-terms, or dependency record.
- Added strict enforcement that credit is not a substitute for permission.
- Added local permission-evidence hashing while excluding private permission messages and local paths from the public release.
- Added project and third-party licence records, collaborator credits, dependency notices, and public rights manifests.
- Added Donation Points compatibility checks for every bundled asset.
- Added original game/tool file blocking, executable inventory checks, nested-archive warnings, and internet-connected utility requirements.
- Added truthful-claim evidence gates, adult-content classification, AI-assistance disclosure and human-verification requirements.
- Added a current-policy review lock using official Nexus Mods policy URLs and a 90-day maximum review age.
- Added optional Nexus 25th Anniversary 2026 event checks, including the event-specific generative-AI prohibition.
- Added uploader attestation enforcement. AI agents are explicitly forbidden from signing or inventing permission.
- Added `nexus-policy-status`, `nexus-scaffold`, `nexus-plan-validate`, `nexus-audit`, `nexus-page-render`, and `nexus-build` across CLI, GUI, and MCP.
- Added `release-build --target nexus --publication-plan ...` so an ordinary private ZIP cannot be mislabeled as a Nexus-ready release.
- Added generated Nexus BBCode, credits, third-party notices, permissions, AI disclosure, public rights manifest, private audit, checklist, and deterministic ZIP.
- Added dedicated documentation, schema, policy source lock, AI skill rules, and publication regressions.
- The earlier 4.0 research branch was not published; 4.1.0 is the first packaged major-4 release tree.
- Changed unknown future SPID keys from hard failures to unverified warnings while retaining hard errors for demonstrated invalid aliases.

## 3.0.2

- Fixed Windows regression fixtures that disguised Python scripts as `.exe` files and triggered WinError 193/216 plus the Unsupported 16-Bit Application dialog.
- Added cross-platform Python worker launching through the active Forge interpreter.
- Added bounded PowerShell worker launching without `shell=True`.
- Added Windows PE header validation before invoking configured `.exe` tools.
- Wrapped process-start failures in structured Forge `ToolError` reports.
- Added Windows-specific regression tests proving invalid `.exe` fixtures are rejected before `CreateProcess`.
- Integrated the corrected CI validation scopes and exact Go 1.23.2 reproducibility toolchain.

## 3.0.1 CI hotfix

- Split cross-version Python validation from byte-for-byte native release validation.
- Pinned Go 1.23.2 in native, publication, and release jobs.
- Added an isolated Windows installer and legacy-config migration smoke test.
- Added explicit `SKYRIM_FORGE_PYTHON` support for deterministic automation environments.

## 3.0.1

- Fixed upgrades from Forge 2.x configurations containing a legacy `[papyrus]` table.
- Added automatic migration of the compiler path with a pre-migration configuration backup.
- Preserved Papyrus flags and import defaults in the canonical Forge 3 configuration.
- Made `version` and `self-test` independent of user configuration so updater bootstrap cannot be blocked by legacy settings.
- Added regression tests reproducing the exact upgrade failure.

## 3.0.0

- Added the typed Automation Fabric and transactional external-tool broker.
- Added unattended xEdit checks with fixed allowlisted scripts and completion markers.
- Added MO2 profile capture and profile-aware process launching.
- Added Vortex staging inventory without database mutation.
- Added LOOT plan, compare, backup, and approved apply stages.
- Added version-pinned external worker protocol for LOOT, Wrye Bash, and Creation Kit.
- Added coordinate-free Windows UI Automation fallback.
- Added direct Papyrus compilation with fresh-PEX verification.
- Added typed KYWD, GLOB, FLST, and OTFT plugin creation.
- Added plugin record querying with raw/local/origin identity fields.
- Added framework regressions for SPID special keys, KID type labels, BOS whitespace transforms, and CDF wildcard rejection.
- Added deterministic repository ZIP, wheel, source distribution, native helper binaries, validation reports, and SBOM.
