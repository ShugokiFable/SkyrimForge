# Release process

1. Run the complete repository validator with `--write-reports`.
2. Run all required GitHub CI and CodeQL jobs.
3. Execute the Windows installer twice in CI.
4. Execute the bundled Windows native helper and its self-test.
5. Build the repository archive twice and require identical hashes.
6. Build the wheel and source distribution twice and require identical hashes.
7. Publish only from the validated tag commit.
8. State separately which installed tools and Skyrim runtime tests were actually exercised.
