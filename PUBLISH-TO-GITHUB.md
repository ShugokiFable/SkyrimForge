# Publish Skyrim Forge 3.0.1

Extract the GitHub-ready ZIP. Push the contents inside `Skyrim-Forge-3.0.1` to the repository root, not the outer ZIP.

```bash
git init
git add .
git commit -m "Release Skyrim Forge 3.0.1"
git branch -M main
git remote add origin <YOUR_REPOSITORY_URL>
git push -u origin main
```

Wait for CI and CodeQL. Then tag:

```bash
git tag -a v3.0.1 -m "Skyrim Forge 3.0.1"
git push origin v3.0.1
```

The release workflow validates the tagged source and publishes the repository ZIP, wheel, source distribution, checksums, validation report, build receipt, manifest, and SBOM.
