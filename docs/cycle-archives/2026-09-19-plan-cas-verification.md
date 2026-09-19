# Live plan CAS verification

At 2026-09-19T03:07Z, Coordinator task
`a68df3ae-aaf5-4591-a46d-9d73db62e46d` verified Support repair
`103af197-ff16-45a9-a9af-176244d588d3`. Support source commit:
`d41672428e2424b385ee9adff84ad033d266293f`.

- Read returned separate metadata and exact Markdown blocks.
- Exact preimage: [archive](2026-09-19T0301-plan-preimage.md), 204737 bytes,
  SHA256 `7a1d494ab898ca07fc6c4016d3b163ff772d3e52f675492a843f4c4b0df324dd`.
  Committed/pushed as `ffaec9e` before replacement; shared main fast-forwarded.
- Replacement used the read opaque version and intentional-truncation flag;
  exact body readback was 164516 bytes. Only one closed ledger record and 16
  cleared historical blocker records were archived; every other JSON value and
  trailing Markdown was preserved, with a current executable handoff prepended.
- A second write of that same body using the old token returned CONFLICT:
  `Plan was not changed because expected_version does not match the current plan.`
  Subsequent read proved both body and full metadata unchanged.

Pre/post canonical JSON SHA256 equality was checked for every retained field.
Key retained collections:

| Collection | Count | SHA256 before = after |
| --- | ---: | --- |
| open_ledger_task_ids | 68 | d1f6fe449910cfdb7bf89e22c412ebca431953dd43258c359d7e6f7ed88c702f |
| blocked_records | 26 | 96f2cc73e897dca2950b83a153a1f89cd52d75bfb11de75bea1342cdf5ee0393 |
| human_asks | 4 | 62cce2c2ac7bf969476937cd31d8c7d0a68421647f4c38a54a3e246843ba58f3 |
| active_flags | 5 | 79066efa1f3f66570164759cd702c9ba570d8e76f25ae7710ca8449a8fec548e |
| ledger | 68 | 36db3cdffcb5f86d89b4b2f42586b139a1dbfda9920394f791f8d2974b427b45 |
| handoff | 15 | 61c618d9047defbd7f5026b7ba4d41cbf18ca9f109fbeef1d6117b17e3139409 |

This verifies reusable plan-write CAS only. It does not prove worker fencing,
queue handoff, model switching, a complete monitoring cycle, or realized cost
savings. Queue census still returned UNKNOWN_ACTION. Primary remained Astra.
