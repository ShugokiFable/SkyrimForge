# Publish Skyrim Forge 4.2.5

Extract the GitHub-ready ZIP. Push the contents inside `Skyrim-Forge-4.2.5` to the repository root, not the outer ZIP.

```bash
git init
git add .
git commit -m "Release Skyrim Forge 4.2.5"
git branch -M main
git remote add origin <YOUR_REPOSITORY_URL>
git push -u origin main
```

Wait for CI and CodeQL. Then tag:

```bash
git tag -a v4.2.5 -m "Skyrim Forge 4.2.5"
git push origin v4.2.5
```

The release workflow validates the tagged source and publishes the repository ZIP, wheel, source distribution, checksums, validation report, build receipt, manifest, and SBOM.

## FOMOD release gate

Any repository release fixture containing `fomod/ModuleConfig.xml` is checked for XML order, source coverage, flags, dependencies, branches, and destination collisions.
