# Workspace ownership

- Product: Skyrim Forge
- Authoritative repository: `https://github.com/ShugokiFable/SkyrimForge`
- Branch: `main`
- Parent: tag `v5.1.2`, commit `6f25163`
- Active version: `5.1.3` validated release
- Previous installed release: `Skyrim-Forge-5.1.2`

The Git repository owns the project. Versioned release folders extracted beside
it are installed outputs, not sources; edits belong in a clone of the repository
above. Skyrim `Data`, mod-manager staging, profiles, saves, and reference vaults
remain read-only.

A prior local path was recorded here as authoritative and no longer exists. When
a recorded owner root is absent, resolve authority from the published repository
and the version pointers inside the candidate trees rather than editing an
installed output in place.
