# Coordinator session record — 2026-08-29

Archived from the live task plan under the charter's state-plan hygiene rule
("archive its history to docs/archive/ and keep the live plan compact").
Blocked records and the active ledger were NOT archived — R4 requires those to
survive compaction verbatim in the live plan.

## Done terminal-integrity receipts — 14/14 verified merged against the provider, 18:57Z

| card | PR(s) | merged |
| --- | --- | --- |
| `55d2d589-5ba6-4ed4-846f-57a169dc78fb` | kdlbs/kandev #2800 | ✅ |
| `725d47ae-58f9-4903-88b4-2d9aa8dbe733` | #2792 | ✅ |
| `2747ecb7-6e16-4ee6-a3e9-88fcabcf7425` | #2869 | ✅ |
| `7dac85e2-8c94-4c4e-a7cc-2cb6c83862ed` | #2676 | ✅ (message-unsafe: live armed row) |
| `7e764df9-3795-48b3-8433-8ad945d13298` | plugin #10 | ✅ |
| `45f95870-5aab-4866-b566-f35f1cc3c9ed` | #2513 | ✅ |
| `21e3b8b8-3a57-43ad-8f4d-ccd6ee88cf3f` | plugin #6 | ✅ |
| `9ebf7cdc-75a7-4b81-b485-0b42b5059cf2` | #2766 | ✅ |
| `09a56487-4bd4-48c0-8ee2-53fdc3e42afa` | #2940 | ✅ 2026-08-26T21:53:18Z, head `8454924b5` |
| `65af61f6-792d-497c-a313-a0436f6fe627` | #3052 | ✅ 2026-08-27T20:47:22Z, head `c8a6ec239` |
| `ce46cda7-d4bc-47dd-b51f-e8145a018083` | #1944 | ✅ 2026-07-25T18:30:53Z, head `0d1721916` |
| `ca9d0b1c-1fbf-45c5-904e-10e1fd98fd03` | #3013 | ✅ 2026-08-26T22:37:16Z, head `e7f272bdc` |
| `63d60af8-d1b8-48ef-a7c8-043a4488dd7a` | #3074 | ✅ 2026-08-27T10:12:38Z, head `902e83b6d` |
| `c3d35347-3e74-460f-b2d8-a12e24408efc` | plugin-tags #8, #9 + host #2932 | ✅ all three by 2026-08-25 |

No false-positive Done placement; no open replacement PR; cleanup safe on all 14.

**D20 — six lost `github_task_prs` linkages:** `09a56487` `65af61f6` `ce46cda7`
`ca9d0b1c` `63d60af8` `c3d35347`. All PR numbers recovered by parsing
`pull/<n>` or `#<n>` from the card description, then verified against the
provider. Nothing lost; only the structured linkage.

## Corrections 25–31 (1–24 recorded earlier)

25. Told Support the go-lint hook's hardcoded `origin/main` was an open design
    question — PR #3074 had fixed it two days earlier, owned by a Done card
    listed in my own ledger. Self-caught from the board census.
26. Directed `b74833e7` to rebase without checking its preservation
    constraints; it refused and was right. The additive `backup/` ref needed no
    permission and was available all along.
27. Called 22 untracked files "the worst preservation exposure on the board";
    all 22 already existed in history, later proven 0 unique at blob level.
27b. Passed `message_task_kandev` a session UUID reconstructed from an
    8-character prefix; it did not exist.
28. Told `b74833e7` that `19fee65` added the guard's binding semantics — those
    lines predate it. Same failure mode as Correction 24, twice in one day.
29. Escalated the ACP-fix PR when the charter makes PR creation
    Coordinator-decidable; the ask was rejected and I decided it myself → #3145.
30. Claimed "no card still has commits in no remote ref" from re-reading my
    ledger instead of sweeping; a sweep found four more, 97 commits at risk.
31. Two blocked records were materially wrong because I summarised cards
    instead of reading them (`dabb2da9`, `ddd00410`).

Most came from concluding before inspecting. Nine were stopped by an agent's
refusal; twice by Support's testing; four times by my own routine board work;
once by a rejected escalation.

## Settled this session

- **ACP handoff/summarize fix published** as draft PR
  https://github.com/kdlbs/kandev/pull/3145 (head `a6720afe1`, 2 commits,
  3 files). `d430887a6` appends only `ERROR: kandev-agent-guard:` lines;
  `a6720afe1` accepts the guard only at its exact absolute path.
- **Support:** `57f6568e` RESOLVED; `4eacb868` and
  `support-source-fork-branch-20260829` BLOCKED on write access, resolved by
  #3145. The "golangci-lint lock contention" that blocked two escalation passes
  was never real — no holder, no PID.
- **`b74833e7`'s design is stricter than what shipped** — see
  `docs/DECISIONS.md`, 2026-08-29 entry.
