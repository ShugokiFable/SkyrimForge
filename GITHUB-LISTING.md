# GitHub listing — Skyrim Forge 3.0.1

> **Reminder (Grok, 2026-07-23):** This file is the only new file added for the GitHub listing.
> Existing project files were **not** edited. When you create the remote repo, fill in the URL below and push from this folder.

---

## Status

| Item | Value |
|------|--------|
| Local source root | `S:\Apps\Skyrim Tools\Skyrim-Forge-3.0.1` |
| Version | `3.0.1` |
| Tag to create after CI | `v3.0.1` |
| License | MIT |
| Git initialized here? | **No** (as of this listing) |
| Remote URL | `https://github.com/ShugokiFable/skyrim-forge.git` |
| Live page | https://github.com/ShugokiFable/skyrim-forge |
| Who prepared this listing | Grok (xAI) — published 2026-07-23 |
| Note | CI workflow files (`.github/workflows/*`) are local only until `gh auth` has `workflow` scope |

---

## GitHub “About” box (paste into Settings → General)

**Description (≤ 350 chars):**

```text
Safety-first Skyrim SE/AE mod engineering workbench + MCP server. Lets AI agents inspect plugins, write typed records, validate SPID/KID/BOS/SkyPatcher/CDF, compile Papyrus, and automate xEdit/MO2/CK/LOOT/Wrye via typed JSON jobs — not blind GUI clicking.
```

**Shorter alt (if you want a tighter one-liner):**

```text
Local Skyrim SE/AE workbench & MCP fabric so AI agents can build mods safely with typed tools, receipts, and bounded automation.
```

**Website:** leave blank, or your Nexus/docs URL later.

**Topics (comma-separated, paste one by one in Topics):**

```text
skyrim
skyrim-se
skyrim-ae
skyrim-modding
skse
mcp
mcp-server
ai-agents
modding-tools
esp
esl
papyrus
xedit
mod-organizer-2
loot
python
windows
automation
```

**Checklist toggles:**

- [x] Releases
- [x] Packages (optional)
- [x] Deployments (optional)
- [ ] Wiki (optional)
- [x] Issues
- [x] Discussions (optional, recommended once public)
- [x] Sponsorships (optional)

---

## Social preview / repo elevator pitch

**One paragraph for README header, releases, or Discord:**

Skyrim Forge is a **local, safety-first engineering workbench** for Skyrim Special Edition and Anniversary Edition. It gives AI agents a real tool surface—CLI, GUI, and MCP—so they can inspect plugins, create narrowly typed plugin content, validate distribution frameworks, compile Papyrus, package releases, and drive external tools (**xEdit, MO2, Creation Kit, LOOT, Wrye Bash**) through **typed JSON jobs** with snapshots, allowlists, and audit receipts. Live game Data, saves, and manager staging stay read-only; writes need explicit approval and land in the Forge workspace.

**Tagline options:**

1. *Typed tools for AI-built Skyrim mods.*
2. *Agents don’t click. They submit jobs.*
3. *Skyrim mod engineering with receipts, not vibes.*

---

## Features blurb (for Releases / Discussions intro)

### Core

- Plugin header inspection, master chains, flags, hashes
- Record traversal (including compressed) with signature / FormID / EditorID queries
- Transactional typed plugin creation: **KYWD, GLOB, FLST, OTFT**
- Framework validation: **SPID, KID, BOS, SkyPatcher, CDF**
- Papyrus compile via the official compiler with stale-PEX rejection
- Archive / release-tree inspection and deterministic packaging
- CLI · GUI · **MCP** for AI applications

### Automation Fabric (3.0)

- Typed JSON jobs → validate → snapshot → run adapter → logs/outputs → reopen/verify → **receipt**
- Allowlisted xEdit scripts with completion markers (no arbitrary generated Pascal)
- Version-pinned external workers for LOOT, Wrye Bash, Creation Kit
- Coordinate-free Windows UI Automation fallback (narrow, pre-calibrated only)
- MO2 profile capture; Vortex inventory without DB mutation
- External tools and UI automation **off by default**

### Safety model (sell this hard on GitHub)

- Live `Data`, saves, profiles, original archives, manager staging = **read-only inputs**
- Outputs only in the configured Forge workspace
- Writes require **explicit approval**
- Optional SHA-256 pins for external executables
- Subprocesses as argument arrays (`shell=False`)
- Honest evidence labels: static/tool checks ≠ in-game runtime proof

---

## Suggested GitHub repo name & visibility

| Field | Suggestion |
|--------|------------|
| Repo name | `skyrim-forge` (or `Skyrim-Forge`) |
| Visibility | Public if you want agents/community install; Private until first clean tag is fine |
| Default branch | `main` |
| Include | Existing `README.md`, `LICENSE`, `SECURITY.md`, `.github/` workflows (already in this tree) |

Do **not** wrap the push in an extra parent folder: repository root = contents of `Skyrim-Forge-3.0.1`.

---

## Where to push updates (copy/paste after remote exists)

From this exact directory:

```powershell
cd "S:\Apps\Skyrim Tools\Skyrim-Forge-3.0.1"

# first time only
git init
git add .
git commit -m "Release Skyrim Forge 3.0.1"
git branch -M main
git remote add origin https://github.com/<YOU>/<REPO>.git
git push -u origin main

# after CI + CodeQL are green
git tag -a v3.0.1 -m "Skyrim Forge 3.0.1"
git push origin v3.0.1
```

Later updates (routine):

```powershell
cd "S:\Apps\Skyrim Tools\Skyrim-Forge-3.0.1"
git add .
git commit -m "Describe the change"
git push origin main
# version release:
git tag -a vX.Y.Z -m "Skyrim Forge X.Y.Z"
git push origin vX.Y.Z
```

Release workflow (already under `.github/workflows/`) builds the deterministic ZIP, wheel, sdist, checksums, validation report, and SBOM when the tag is pushed.

Also see in-tree: `PUBLISH-TO-GITHUB.md`, `docs/GITHUB-RELEASE.md`, `RELEASING.md`.

---

## Create-repo checklist (human, ~5 minutes)

1. Create empty GitHub repo `skyrim-forge` (no auto README/license — this tree already has them).
2. Paste **About → Description** and **Topics** from above.
3. Set remote URL in the table at the top of this file.
4. Push `main`, wait for CI + CodeQL.
5. Push tag `v3.0.1`.
6. Confirm release assets appear; attach nothing that contains Bethesda game files (see `NOTICE.md`).

---

## What was intentionally not done

- No edits to `README.md`, configs, Python, or packaging.
- No `git init` / remote / push from the agent (needs your GitHub account and confirmation).
- No SSEEdit/CK launch.

When the remote exists, update the **Remote URL** row in this file so future sessions know exactly where updates go.
