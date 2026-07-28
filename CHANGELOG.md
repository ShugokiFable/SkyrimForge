# Changelog

## 4.2.5

- Fixed fresh Windows installations failing when Python 3.11+ was not already on `PATH`.
- Added an explicit, user-approved bootstrap for the pinned Python 3.13.14 installer from python.org with SHA-256 and Authenticode verification.
- Added registry and standard-location Python discovery so a newly installed interpreter is usable without restarting the shell.
- Added `SKYRIM_FORGE_ROOT` registration and a generated `INSTALLATION.json` beside every installed Forge AI skill, removing per-provider `PYTHONPATH` workarounds.
- Made explicit `SKYRIM_FORGE_CONFIG` and `--config` locations self-contained so sandboxed AI clients do not fall back to an unwritable user Documents folder.
- Added one-command all-AI setup covering runtime installation, provider skills, MCP registration, and a machine-readable integration report.
- Added current Codex, Claude, and Grok MCP registration; Kimi and Hermes are reported accurately as skill/CLI consumers when no supported MCP registrar is available.
- Fixed Grok registration under Windows PowerShell 5 and verify its exact enabled command rather than trusting process exit alone.
- Fixed configured 7-Zip paths being omitted from Forge's read allowlist.
- Fixed the Windows CI native-version assertion that was stale at 4.2.3.
- Added `SKYRIM_FORGE_GO` so sandboxed and deterministic builds can select the exact Go 1.23.2 executable without relying on inherited `PATH`.
- Made updates repin the Forge-owned UI worker to the active installation while preserving all user-selected Skyrim and third-party tool paths.
- Fixed strict-mode provider prompts parsing `$Name?` as a variable and permanently excluded machine-local installation descriptors, reports, virtual environments, and Go caches from release artifacts.

## 4.2.4

- Fixed GitHub release validation failing because Go embedded Git revision and commit-time metadata only when building inside the Actions checkout.
- Added `-buildvcs=false` to the canonical native-helper build and reproducibility validator.
- Added a canonical native-helper rebuild script that updates both published and packaged copies.
- Added a regression that creates a real temporary Git repository and requires its deterministic build to match the bundled helper byte-for-byte.
- Added build-metadata diagnostics to native reproducibility reports.

## 4.2.3

- Fixed the installed regression suite scanning `.venv\Scripts\Activate.ps1` as if it were Forge-owned release source.
- Fixed the Papyrus case-collision fixture on Windows by placing case-equivalent filenames in separate source roots.
- Added regressions proving runtime-created virtual environments are excluded while Forge-owned PowerShell scripts remain audited.
- Preserved the real PowerShell parser gate over top-level and worker scripts.
- Synchronized packaged native helpers with the published binaries and added a hash-equality release gate.

## 4.2.2

- Fixed `START-HERE.bat` and `Run Tests.bat` passing a quoted `%~dp0` directory token to PowerShell. Because `%~dp0` ends with a backslash, Windows command-line parsing could preserve the closing quote as part of the path.
- The startup and test launchers now let `PowerShell-Parse-Gate.ps1` use its own `$PSScriptRoot` instead of serializing the repository directory through `cmd.exe`.
- Hardened the parser gate to normalize an accidentally quoted legacy root argument instead of crashing with `Illegal characters in path`.
- Added a noninteractive `START-HERE.bat --validate-only` mode and execute that exact path in Windows CI.
- Added release-time checks that reject standalone quoted `%~dp0` arguments in external-command lines.
- Added permanent regressions for the exact user-reported failure.

## 4.2.1

- Fixed the PowerShell parser failure in `Install-Forge-Skill.ps1` caused by an ambiguous variable immediately followed by a colon.
- Replaced the unsafe interpolation with PowerShell's format operator.
- Made AI skill installation transactional, idempotent, rollback-safe, and reparse-point aware.
- Added an all-script PowerShell parser gate that runs before the menu and before regression tests.
- Added static detection for ambiguous colon-adjacent variable references in expandable PowerShell strings.
- Added Windows CI execution for all five AI provider skill targets, including a second idempotence pass and content-hash verification.
- Added release regressions covering the exact reported parser failure.

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
