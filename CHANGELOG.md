# Changelog

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
