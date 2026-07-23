# Skyrim Forge 3.0

Skyrim Forge is a local, safety-first engineering workbench and MCP server for Skyrim Special Edition and Anniversary Edition mod development.

Forge 3.0 introduces the **Automation Fabric**. An AI does not click around SSEEdit, Creation Kit, Wrye Bash, LOOT, or Mod Organizer 2. It submits a typed JSON job. Forge validates the job, snapshots inputs, runs only the configured adapter, captures logs and outputs, reopens what it can verify, and writes an audit receipt.

## Install

1. Extract the release into a permanent tools folder.
2. Run `START-HERE.bat`.
3. Choose **Install or update Forge**.
4. Configure core paths.
5. Configure only the external tools actually installed on the machine.
6. Register MCP and install the Forge skill for the AI applications you use.

External tool execution is disabled by default. UI Automation is separately disabled by default.

## What Forge can do directly

- Inspect plugin headers, masters, flags, and hashes.
- Traverse normal and compressed plugin records and query signatures, raw FormIDs, local FormIDs, origins, and EditorIDs.
- Create narrowly typed KYWD, GLOB, FLST, and OTFT plugins transactionally.
- Validate SPID, KID, BOS, SkyPatcher placement, and CDF configuration.
- Compile Papyrus through the official compiler and reject stale PEX output.
- Inspect archives and release trees.
- Build deterministic release archives.
- Snapshot MO2 profiles.
- Run fixed, allowlisted xEdit scripts unattended.
- Execute version-pinned JSON workers for LOOT, Wrye Bash, and Creation Kit.
- Run narrowly calibrated, coordinate-free Windows UI Automation jobs when no headless worker exists.
- Expose the workbench over CLI, GUI, and MCP.

## xEdit automation

Forge includes audited scripts under `resources/xedit` and installs them into the configured xEdit `Edit Scripts` directory only after approval.

A check job launches the installed xEdit executable with a selected plugin, its masters, automatic script execution, and automatic exit. Forge requires the completion marker produced by its own script. A process exit without the marker is classified as incomplete, not success.

Arbitrary generated Pascal is disabled. An additional script may run only when its exact SHA-256 is present in an explicit allowlist and the script already resides in xEdit's script directory.

## Creation Kit and Wrye Bash

Those applications do not provide one complete, stable public headless interface for all authoring and Bashed Patch operations. Forge supports two bounded mechanisms:

1. A version-pinned external worker implementing the Forge JSON worker contract.
2. A coordinate-free Windows UI Automation fallback for a narrow, pre-calibrated dialog sequence.

The fallback uses window titles, process IDs, Automation IDs, and accessible control names. Job files cannot contain coordinates, OCR instructions, or image matching.

## Safety model

- Live Skyrim `Data`, saves, profiles, original archives, and manager staging are read-only inputs.
- Outputs belong to the configured Forge workspace.
- Write operations require explicit approval.
- External executables may be pinned by SHA-256.
- Subprocesses are invoked with argument arrays and `shell=False`.
- Each automation job receives a transaction directory, input snapshots, logs, outputs, and a JSON receipt.
- Unexpected dialogs, missing completion markers, worker disagreement, missing outputs, hash mismatches, timeouts, and nonzero exits block the job.
- Forge does not silently apply a proposed load order.
- Forge does not claim that static checks replace Skyrim runtime testing.

## Fast commands

```text
forge doctor
forge discover-tools
forge config-show
forge lint <ModFolder>
forge plugin-info <Plugin.esp>
forge record-query <Plugin.esp> --signature SPEL --editor-id Bound
forge plugin-plan-validate examples/plugin-create.plan.json
forge automation-validate examples/automation-xedit-check.job.json
forge automation-run <job.json> --approve
```

## Readiness levels

`doctor` reports separate states:

- `read_only_ready`: inspection and static validation can run.
- `plugin_write_ready`: the typed writer can write inside the workspace.
- `xedit_automation_ready`: xEdit exists, hashes match when pinned, and external execution is enabled.
- `mo2_automation_ready`: MO2 is configured and external execution is enabled.

A missing external tool does not make the core installation broken.

## Evidence labels

Forge reports what each result actually proves:

- Plugin header inspection is not semantic validation.
- Forge record parsing is not independent xEdit evidence.
- xEdit scripted checks are not Skyrim runtime evidence.
- Release validation is packaging hygiene, not gameplay validation.
- Creation Kit output still needs visual and in-game testing where appearance, navmesh, lighting, scenes, or placement matter.

## Repository

The repository includes deterministic packaging, CI, CodeQL, issue templates, security policy, tests, schemas, native helper source, Windows and Linux native binaries, and GitHub release automation.
