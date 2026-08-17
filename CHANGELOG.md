# Changelog

## 5.1.1

AI bridge reliability release.

- Routed the advertised `forge_papyrus_compile` MCP tool to the service. Calls
  no longer fall through to an unknown-tool error.
- Registered Kimi through its preserving `mcp.json` configuration and verified
  the result with `kimi doctor`; a failed doctor restores the original bytes.
- Registered Hermes through its supported MCP CLI and required a successful
  `hermes mcp test skyrim-forge` connection probe; failed replacement attempts
  restore the original Hermes configuration bytes.
- Corrected Hermes skill installation from the unused `%USERPROFILE%\.hermes`
  path to `%LOCALAPPDATA%\hermes`, while preserving `HERMES_HOME` overrides.
- Added Windows regression coverage for Kimi configuration preservation,
  Hermes registration/testing, Hermes home resolution, and Papyrus MCP routing.

## 5.1.0

Framework linting, validated against a real reference corpus for the first time.

Forge's SPID/KID/BOS/FLM/SkyPatcher profiles were written from documentation
with no installed mods to check them against. Run over 1,195 framework configs
from a live 3,000-mod load order, the linter reported **13,554 errors and 11,762
warnings across 16% of files**. Triaged against the frameworks' own SKSE runtime
logs, essentially all of it was false. After these fixes the same corpus reports
**11 errors and 71 warnings across 5% of files**, and the 11 are genuine
third-party defects.

- Fixed SkyPatcher clause values being split on commas. A value is routinely a
  comma-separated form list (`removeFromLLs=A.esp|001DBD, A.esp|001DC8`), and
  every form after the first was reported as unmodeled syntax. 11,730 warnings
  from one parsing error; rules are now validated per `key=value` clause.
- Fixed a single-value SPID skill filter being an error. The corpus installs
  13,427 of them across skill indices 12-16 with **zero** parse failures in
  `po3_SpellPerkItemDistributor.log`, and one was traced end to end: Abyss's
  `14(20)` distributed as `SPEL:FE059810`. Five rows using index 0 were rejected
  at runtime, so the observation is kept as an advisory - failing 13,427 working
  rows to catch 5 is the worse error. Runtime evidence outranks a static profile.
- Fixed the advisory burying everything else: a repeated note is now collapsed to
  one entry per file naming the count and first line, not one per line.
- Added the SkyPatcher categories `outfit`, `ingestible`, `misc`, `ingredient`
  and `projectile`. All five are installed and working; none were in the profile.
- Fixed KID keys being matched case-sensitively. Shipping mods write
  `keyword =`, and `BoobiesArmorPouch [KYWD:FF001DA3]` distributes from one.
- Fixed a two-field KID line being rejected as an unsupported type label. Field 2
  is a name filter there, and `BoobiesArmorScarf [KYWD:FF001DA5]` applied at
  runtime. Now an advisory naming the unrecognised token.
- Fixed surviving byte-order marks inventing findings. `utf-8-sig` strips one;
  corpus files carry three stacked at the top and one mid-file where two sources
  were concatenated. A surviving U+FEFF stopped a comment from being a comment
  and turned a valid key into an unknown one.
- Added `InstalledCorpusRegressionTests`, built from the real installed lines.

## 5.0.2

- Fixed the installed AI skill advertising "Skyrim Forge 4.2" from inside a 5.0
  installation. That line is the skill's `description`, which is the only thing
  an agent reads when deciding whether to load Forge at all, and it was wrong in
  every provider home the bridge installs to.
- Extended the version gate to cover the skill descriptor. It checks the series
  (`major.minor`) rather than the patch, because that is what the skill states.
  Eight restatements of the version are now gated against `version.py`.

## 5.0.1

FOMOD false positives. Forge is meant to be the last gate a mod passes before it
ships, which makes a wrong rejection more expensive than a missed nicety: it
teaches the author to stop trusting the gate. Each of these refused an installer
that is legal per the official `ModConfig5.0.xsd` and that Vortex and MO2 install
without complaint.

- Fixed a plugin containing the optional `<image>` element being rejected with
  "must contain files or conditionFlags in ModuleConfig 5.0 order". The schema
  sequence is `description, image?, (files, conditionFlags? | conditionFlags,
  files?), typeDescriptor`; the optional image was not allowed for, so **every
  option carrying a screenshot was refused** — which is most real installers.
- Fixed `xsi:noNamespaceSchemaLocation` being enforced as mandatory. It is an
  optional XML hint, nothing in the schema requires it, and no mod manager reads
  it. Omitting it, or spelling the URL with `https`, failed the whole installer.
  It is now reported as a warning and the structure is validated regardless.
  `http`/`https` for both the `fo3` and `gemm` documents, and a bare
  `ModConfig5.0.xsd`, are all accepted without comment.
- Fixed game-specific version dependencies being refused as unsupported
  elements. The `fo3` schema that Forge itself names as canonical exists
  precisely to add `foseDependency`, so the validator demanded a schema and then
  rejected what that schema defines. `foseDependency`, `nvseDependency`, and
  `skseDependency` are now recorded as unverified, consistent with how Forge
  already treats version-specific framework syntax.
- Made the unreferenced-payload error name the files it rejects instead of
  reporting only a count. Coverage remains strict; the message became usable.
- Added `ThirdPartyFomodFalsePositiveTests`, which builds installers that are
  legal per the published XSD and requires Forge to accept them.

The C# scripted-installer refusal is unchanged and deliberate: those permit
arbitrary code execution.

## 5.0.0

Protocol release. Forge now speaks the current MCP revision without giving up
the one every installed client still uses.

- Added MCP `2026-07-28` support. That revision removes the `initialize`
  handshake and carries the protocol version, client identity, and capabilities
  as per-request `_meta` instead. Forge is now a **dual-era server**: a request
  declaring the modern version is served statelessly under it, and an
  `initialize` request still selects legacy semantics.
- Added `server/discover`, which the revision requires servers to implement. It
  returns the supported version list, capabilities, and `serverInfo` in one
  request, and answers even when the request carries no `_meta`, because it is
  the documented stdio probe a client sends before it knows what the server
  speaks.
- Added `UnsupportedProtocolVersionError` (`-32022`) carrying the supported
  version list, so a client that asks for an unknown revision is corrected
  rather than silently downgraded.
- Added the caching hints the revision makes mandatory on complete results.
  Static tool, prompt, and resource inventories are `public`; sanitized local
  configuration is `private` with a zero TTL, because it reflects machine state
  that `forge_config_set` can change.
- Legacy responses are byte-identical to 4.2.5. `resultType`, `ttlMs`, and
  `cacheScope` appear only when the client asked for the modern revision, so
  already registered Codex, Claude, and Grok installations are unaffected.
- Fixed `MANIFEST.json` failing to verify against a `git clone`. Five files
  (`Install-AI-Bridge.ps1`, `Install-Forge-Skill.ps1`, `Install-or-Update.ps1`,
  `Register-MCP.ps1`, `START-HERE.bat`) are declared `eol=crlf` in
  `.gitattributes`, but the manifest recorded LF bytes, so anyone who cloned the
  repository and checked the shipped integrity evidence got five mismatches.
- Added a regression that hashes every manifest entry against the delivered
  tree, and one that requires files declared `eol=crlf` to actually have CRLF
  endings. Integrity evidence that only verifies on the author's machine is
  worse than none, because it fails for the honest verifier and no one else.
- Fixed CodeQL failing on every Dependabot branch with "Loaded a configuration
  file for version '4.37.6', but running version '4.36.0'". The cause was not
  permissions: `codeql-action/init` and `codeql-action/analyze` were bumped in
  separate pull requests, so each branch ran a mismatched pair. Both are pinned
  to one revision, Dependabot now groups them, and a regression fails if they
  diverge. This unblocked four stalled pull requests.
- Collapsed the product version to a single source of truth in
  `skyrim_forge/version.py`. It was restated in the validator, the release
  archive builder, the wheel generator string, a Go constant, packaging
  metadata, plain-text pointers, and a batch-file title, and 4.2.4 shipped with
  Windows CI still asserting 4.2.3. Every restatement is now gated against the
  source, and CI derives the expected native version instead of hardcoding it.
- Applied the blocked action updates: `actions/checkout` 7.0.1,
  `actions/setup-python` 7.0.0, and `github/codeql-action` 4.37.6.
- Rebuilt Windows and Linux native helpers reproducibly as 5.0.0 with pinned
  Go 1.23.2.

Every 4.x safety boundary is unchanged: no GUI launching, no arbitrary shell
commands, no writes to live Skyrim `Data`, external processes disabled by
default, and third-party tools hash-pinned rather than bundled.

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
