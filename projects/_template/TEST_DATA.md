# Test-data manifest: PROJECT_NAME

- Status: `AWAITING_FIXTURE | READY | STALE | NOT_APPLICABLE`
- Workspace ID: `WORKSPACE_UUID`
- Project key: `PROJECT_KEY`
- Repository IDs/paths: `...`
- Fixture ID/version: `...`
- Source class: `sanitized-fixture | development-dump | static-backup | migrations-seeders | synthetic-overlay`
- Captured at: `...`
- Artifact: `artifacts/FILENAME` (ignored, mode 0600)
- Bytes / SHA-256: `...`
- Engine/version/format: `...`
- Sanitization and live-integration audit: `...`
- Load recipe: `how-to-load.sh` or documented command
- Start recipe: `how-to-start.sh` or project command
- Expected assertions: schema, representative counts, login and feature paths
- Refresh rule: `...`
- Known limitations: `...`
- Last accepted restore receipt: task UUID, destination identity, date, result

Never store passwords, tokens, master keys, private keys or raw dump content in
this manifest.
