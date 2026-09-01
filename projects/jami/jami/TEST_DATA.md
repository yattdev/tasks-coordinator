# Test-data manifest: jami

- Status: `READY`
- Workspace ID: `d918c5e2-903e-47ce-b372-8e62f9dbad9c`
- Repository: `905ab1f3-4992-4126-a2d8-070e2bf90136` (`/data/home/Code/jami`)
- Fixture ID/version: `jami-dev-ghost-v4-20251009-8143ec4c`
- Source class/time: owner-selected repository test dump
  `bootstrap/jami_mysqldump_dev-ghost-v4.sql`, mtime
  `2025-10-09 20:53:29Z`.
- Canonical private artifact:
  `/data/home/Code/coordinator/projects/jami/jami/artifacts/jami_mysqldump_dev-ghost-v4.sql`
  (ignored, mode 0600)
- Bytes / SHA-256: `1273958` /
  `8143ec4cb321cf40c55366083c8e17b98cf276faa0311b1cc66043c5aa1c9b6f`
- Engine/format: MySQL 5.7 logical SQL dump for `jamidb`. Current project
  Compose uses MySQL 8.0, so the first task restore must explicitly verify
  compatibility rather than assuming it.
- Load recipe: `how-to-load.sh`, derived from the repository's untracked
  `loadb.sh` without embedding its test password or fixed container name.
- Sanitization: owner-designated test data; independent secret/PII audit is not
  recorded. Keep same-workspace, private, uncommitted and short-lived after
  delivery.
- Required first restore assertions: empty task DB; importer exit 0 and
  unsuppressed stderr; Ghost schema/content counts; disposable login; Jami
  feature path; exact-head runtime. Record `TEST_DATA_RECEIPT`.
- Refresh rule: owner-selected replacement or proven incompatibility; version
  and hash every replacement.

Never add secrets or raw dump content to this manifest.
