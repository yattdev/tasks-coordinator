# PR #3158 transport delta — 2026-09-15T02:15Z

- Task `37eca47b-cf05-47ee-b143-39408edbeed1` again attempted the HTTPS-configured `fork` push at clean local successor `0da05686deaca3201c2969bfca51e4f1f58b0b33`; it failed with the unchanged credential-lease-scope denial. Fork/PR remains `90e076db266cc601f599b244afc007e21116cb1e`; no source changed.
- Coordinator decision: the verified credential lease is SSH-scoped. Instructed the task to make at most one normal non-force push through explicit `git@github.com:yattdev/kandev.git`, with exact source SHA and destination branch, then verify remote/PR head. This is the supported transport for this denial, not a credential bypass.
- The task-message call did not return within the bounded 15-second window, so delivery is uncertain. Do not resend or issue a competing push until task conversation/provider readback proves whether the instruction was consumed.
- On success, require fresh exact-head CI, independent Review, and distinct QA. On SSH denial, preserve the local successor and record the exact error; no further retry, remote rewrite, HTTPS prompt, force push, or alternate bypass.
- Live Coordinator task-plan reads remain degraded and timed out again; this delta is committed to shared Coordinator state for continuity.
