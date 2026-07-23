---
name: skyrim-forge
description: Use Skyrim Forge 3.0 as the primary typed automation broker for Skyrim mod development and validation.
---

# Skyrim Forge 3.0

Run `forge doctor` before major Skyrim work.

Use Forge inspection and typed jobs before inventing one-off scripts. Never launch xEdit, Creation Kit, LOOT, or Wrye Bash and leave the user to click. Use an Automation Fabric job or report that the required adapter is unavailable.

Hard rules:

- Never send arbitrary shell commands through Forge.
- Never write to live Skyrim Data, Vortex staging, MO2 mods, Overwrite, profiles, or saves.
- Treat `read_only_ready` as a healthy inspection state.
- Require `plugin_write_ready` for typed plugin output.
- Require `xedit_automation_ready` for xEdit jobs.
- Use `raw_form_id_hex`, `local_form_id_hex`, `origin_plugin`, and `form_key` exactly. Never label a raw file FormID as a runtime load-order FormID.
- Use `automation-validate` before `automation-run`.
- Set approval only after reviewing operation, inputs, output ownership, tool hash, and expected evidence.
- A missing completion marker is not success.
- Tool disagreement means stop and classify.
- xEdit evidence is not Skyrim runtime evidence.
- Creation Kit output is not visual validation.

For a release, prefer this chain:

```text
framework lint
plugin/header and record inspection
xEdit fixed-script check when configured
Papyrus freshness verification
asset/release-tree validation
semantic diff
package to a new version
report remaining in-game tests
```
