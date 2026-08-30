# Coordinator capability & situation registry

<!-- registry-version: 2026-08-30g -->

Canonical, actionable decision reference: **given this situation, what may a
Coordinator do, with which exact capability, under whose authority, and what
proves it worked.** Consult it before monitoring, acting, escalating, or ending a
turn.

This registry is a router, not a retelling. Each entry is deliberately short and
links to the deeper procedure; where an entry and a linked document disagree, the
linked document wins for *procedure* and `PROMPT.md` wins for *authority*. Report
the contradiction and fix it in the same change — see [Maintenance](#maintenance).

Entry fields: **Trigger** · **Action** · **Capability** · **Authority** ·
**Evidence** · **Escalate to** · **Never**.

Related: [PROMPT.md](../PROMPT.md) (binding authority) ·
[RUNBOOK](RUNBOOK.md) (procedures) · [DECISIONS](DECISIONS.md) (rationale) ·
[FILESYSTEM_DOCKER_CONTRACT](FILESYSTEM_DOCKER_CONTRACT.md) (access contract) ·
[CONTINUITY](CONTINUITY.md) · [QA_INSTANCES](QA_INSTANCES.md) ·
[LEARNING_LOG](LEARNING_LOG.md)

---

## A. Board monitoring and adaptive polling

### A1. Routine wake arrives (`WAKE:CYCLE` / `WAKE:STANDUP`)
- **Trigger** Any inbound message, not only routine wakes.
- **Action** Read `PROMPT.md` completely, resolve live task/workspace/workflow identity, read the state plan, then run the full cycle contract. A short marker never means a shallow pass.
- **Capability** `date -u`; tool discovery; `list_tasks_kandev`, `get_task_plan_kandev`, `get_task_conversation_kandev`, `list_task_sessions_kandev`.
- **Authority** Standing duty. Routine schedules are operator-owned.
- **Evidence** A cycle log appended to the state plan.
- **Escalate to** Human (visible ask) if a CRITICAL tool is missing.
- **Never** Create, heal, or modify any routine/cron/scheduler; never let a ping create a board task.

### A2. Choosing inspection depth
- **Trigger** Cycle with no material board change.
- **Action** Reduce DEPTH, never frequency: one-line log, skip deep reads. Deepest inspection goes to tasks recently unblocked, near completion, freshly dispatched, or FAILED.
- **Authority** Coordinator-decidable.
- **Evidence** Cycle log records the chosen depth and why.
- **Never** Manufacture extra wakeups, or skip processing a ping.

### A3. A task looks parked for more than one cycle
- **Trigger** Card appears stuck on the board.
- **Action** Either state in the cycle log why it is healthy and merely *looks* parked, or act on it. Those are the only two outcomes.
- **Evidence** Session state and `updated_at`, not the column — see [read session state, not the column](RUNBOOK.md#a-task-looks-active-but-is-idle--read-session-state-not-the-column).
- **Never** Let the Human have to ask "what is going on with this task".

### A4. Delegating bounded evidence gathering
- **Trigger** Every turn with at least two independent inbound messages or parallelizable evidence requests.
- **Action** Proactively start at most ~2 concurrent helpers from one ordered snapshot. Partition by full task UUID and dependency/PR family; give disjoint named slices and stop conditions; keep helpers read-only. The primary deduplicates receipts and serializes all mutations.
- **Authority** Coordinator-decidable; the primary keeps all accountability. High-risk, destructive, credential, integration/history, human-escalation, and Done cleanup decisions stay with the primary.
- **Evidence** Helper session IDs plus their evidence recorded in the cycle log.
- **Never** Wait for queue pressure before parallelizing independent work. Never assign one task/shared decision to two slices, leave helpers polling between wakes, let a helper produce human-facing reports, or allow parallel mutations.

### A5. Processing and draining the Coordinator message queue
- **Trigger** Every turn; act before the queue approaches its 15-entry limit.
- **Action** Census the queue, proactively parallelize independent entries under A4, then let the primary verify and act on every result. After durable state is updated, remove only exact reviewed entry IDs with authenticated `message.queue.remove`; use Kandev Support when the Coordinator has no direct authenticated queue surface.
- **Authority** Human-authorized queue triage; the primary retains all mutation and reporting responsibility.
- **Evidence** Before/after ordered IDs and counts, helper receipts, primary action receipts, and exact removal results. Verified 2026-08-30 by Support request `fad11a89-27bb-415b-8554-7097f225a09d`: 15/15 exact entries removed one-by-one, none missing, final count 0.
- **Never** Use SQL or broad cancellation; never remove an unreviewed, durable, or newly arrived row. Helper triage does not itself drain the product queue, and queue capacity is not the trigger for delegation.

---

## B. Task supervision, flags, blockers, workflow state, PRs, stale sessions

### B1. Classifying a task
- **Trigger** Every inspected task, every cycle.
- **Action** Exactly one of healthy / stalled / blocked / failed / waiting / anomalous / terminal, derived from evidence.
- **Evidence** Primary session state + `updated_at` + conversation. A column is never evidence of progress.
- **Never** Report "implementing"/"progressing" from the column alone.

### B2. Task is STALLED
- **Trigger** No state change and no new comment across two checks, or idle >~2h while its step expects activity.
- **Action** Post "Status? If blocked, state on what. If done with step, signal it." Silent after one nudge → treat as BLOCKED.
- **Capability** `message_task_kandev`.
- **Never** Nudge a task that correctly parked with its blocker captured.

### B3. Task cannot progress (physical Blocked)
- **Trigger** Any column except Backlogs / ToDeploy / Human-QA, where the task cannot move.
- **Action** Move it to physical Blocked **in the same cycle** and run it as HIGH-PRIORITY active recovery with an owner and a trigger.
- **Capability** `move_task_kandev`; [Blocked is an action queue](RUNBOOK.md#blocked-is-an-action-queue-not-a-parking-lot).
- **Authority** Coordinator-owned. A task-specific Human hands-off directive is a hard boundary — report the exact denial.
- **Never** Use Blocked as parking; never leave a Blocked card without owner and next trigger.

### B3a. Task moved or its next action changed
- **Trigger** Every requested/applied task move, or any owner/next-action change that makes the current agent tag stale.
- **Action** In the same cycle, verify the physical lane, read targeted tags, remove stale/incompatible agent applications, apply the tag matching the actual owner/next action with a concise hover note, then verify targeted tag readback. A queued move keeps a recorded pending tag reconciliation until the destination applies.
- **Capability** `move_task_kandev`; Tags plugin targeted `list_tags`, `add_tag`, and `remove_tag`; [reconcile the agent tag with every completed move](RUNBOOK.md#reconcile-the-agent-tag-with-every-completed-move).
- **Evidence** Physical workflow step plus exact task-scoped tag ID/name/note readback.
- **Never** Leave the prior lane's instruction on a moved card, infer a tag solely from the lane name, alter human tags, or violate the ToDeploy ownership boundary.

### B3b. A live armed pending move makes a task message-unsafe
- **Trigger** `pending_moves` contains a row whose target differs from the current lane and whose keyed task session is present and `WAITING_FOR_INPUT`.
- **Action** Do not message, wake, or move the task. Preserve the row and task, record every exact predicate, and use only an atomic exact-match cancellation capability that validates row ID, session ID, task ID, move ID, workflow, expected current step, and queued target in one transaction. Until that exists, keep the task message-unsafe and route the capability to platform task `7056a702-a3c3-4fe8-8535-c6b8d340ef6a`.
- **Capability** Read-only `pending_moves` census plus `list_task_sessions_kandev`; exact cancellation is **not currently available**. Support request `4571adf2-7d99-461b-835c-3a172cab8ef2` proved session-keyed `TakePendingMove` cannot fail closed across all predicates.
- **Evidence** Exact before/after row and lane readback, unchanged unrelated rows, unchanged task/session/tag state, and structured audit identity.
- **Never** Use raw SQL, broad queue cancellation, a separate preflight followed by `TakePendingMove`, or a no-op move on a dormant keyed session whose resume ordering is unproved.

### B4. Flagging / unflagging
- **Trigger** A genuine blocker, anomaly, or frozen loop.
- **Action** Comment whose first line is exactly `[COORDINATOR FLAG] <reason>` (or `[COORDINATOR UNFLAG] <resolution>`); `[COORDINATOR FLAG][URGENT]` on this task for urgent human escalation.
- **Capability** `message_task_kandev` (native flag tools do not exist; switch if discovery finds them).
- **Evidence** Active flags tracked in the state plan, not reconstructed by rescanning comments.
- **Escalate to** Human via `ask_user_question_kandev` whenever the flag needs a human ANSWER — the flag records, the ask surfaces.

### B5. Task blocked on a decision
- **Trigger** Blocked/flagged task reaches the decision ladder.
- **Action** DECIDE if the concrete action is neither destructive/irreversible nor security/trust-boundary; else RECOMMEND; else ESCALATE.
- **Capability** [Exercise full board approval authority](RUNBOOK.md#exercise-full-board-approval-authority-without-a-human-visit).
- **Authority** Coordinator is the board's approval principal for every same-workspace task.
- **Never** Relay a generic "Human approval required" to the Human; never escalate a question a competent lead would decide.

### B6. Open draft PR/MR in monitored scope
- **Trigger** Any open draft.
- **Action** Evaluate the readiness gate; direct the TASK AGENT to make it ready. Only a credential-blocked *mechanical* draft→ready is the Coordinator's to perform, after independently verifying the full receipt.
- **Capability** [Turn a draft PR/MR ready through its task agent](RUNBOOK.md#turn-a-draft-prmr-ready-through-its-task-agent).
- **Evidence** Canonical PR URL + exact clean pushed upstream-matched head; fresh exact-head CI census before and after the ready transition (including any newly triggered `pull_request` jobs); zero unresolved threads; visual evidence for visual changes.
- **Never** Notify from the draft-era check snapshot: marking ready can start new required workflows. Never merge, rebase, deploy, treat ready-for-review as acceptance, or become the implementer.

### B7. PR/MR identity
- **Trigger** Any use of checks, reviews, or mergeability as evidence.
- **Action** Resolve repository owner/name + number or canonical URL, exact head SHA, base, fork relationship first. Refresh after every head/base change.
- **Never** Treat a bare PR number as identity; never reuse evidence from a superseded SHA.

### B8. Stale, dead, or looping sessions
- **Trigger** Session RUNNING with no output; step never launched; step re-enters and loops; agent cannot edit files.
- **Action** Diagnose from session transcripts and `/data/logs/backend-logs.log` before acting. Unchanged tree across re-entries = platform routing defect → create one platform-bug task.
- **Capability** Runbook playbooks: [session RUNNING but no process](RUNBOOK.md#a-session-says-running-but-produces-no-process-output-or-timestamp) · [step never launched](RUNBOOK.md#step-agent-silently-never-launched-task-idle-in-a-step-for-hours) · [completed-session loop](RUNBOOK.md#step-re-enters-on-an-already-completed-session-and-loops) · [untrusted mise.toml](RUNBOOK.md#task-fails-to-start-worktree-misetoml-is-untrusted) · [stale worktree collision](RUNBOOK.md#task-failed-to-start-preparing-worktree-checking-out--fatal--already-exists).
- **Never** Create duplicate agents or destroy a valid reproduction.

### B9. Unanswered delegation
- **Trigger** A reply-bearing request produced no receipt.
- **Action** Diagnose task, all sessions, conversation, pending queue, workspace loading, backend error, then take exactly one matching action. RUNNING → leave alone. Terminal/unconsumed → one fresh session with the original handoff. Workspace-start failure → route to its repair owner.
- **Capability** [Follow up on delegated requests](RUNBOOK.md#follow-up-on-delegated-requests-and-rate-limited-sessions).
- **Never** Treat `sent`, `queued`, or `WAITING_FOR_INPUT` as completion; never resend because transport returned success.

### B10. Done-column integrity
- **Trigger** Every cycle; deeply for new/changed/unreceipted/suspicious Done tasks.
- **Action** Run the terminal-integrity gate before allowing cleanup; recover unsafe tasks out of Done to the narrowest safe active step.
- **Capability** [Audit every new or changed Done task](RUNBOOK.md#audit-every-new-or-changed-done-task-before-allowing-cleanup).
- **Authority** Done-integrity recovery is explicitly authorized and is not a backwards-move violation.
- **Never** Treat a merged PR or Done placement as proof work is durable.

---

## C. Coordinator filesystem and workspace capabilities

### C1. Reading and writing inside the workspace
- **Trigger** Any filesystem action.
- **Action** Confirm the path is in scope before touching it.
- **Capability** `rw` across **its own workspace only**: every active task root, every registered project checkout, the Git common dirs those checkouts need, and the canonical coordinator checkout. Full contract: [FILESYSTEM_DOCKER_CONTRACT §3](FILESYSTEM_DOCKER_CONTRACT.md#3-validated-coordinator--workspace-scoped-authority).
- **Authority** Workspace-scoped. Coordinators of other workspaces are peers with no standing over each other's resources.
- **Evidence** Every write **outside your own task root** is audited: principal, path, operation, timestamp.
- **Never** Other workspaces' resources; unregistered dirs under Code; **the Code root itself**; host paths outside the managed tree; privilege escalation. See [§4 absolute prohibitions](FILESYSTEM_DOCKER_CONTRACT.md#4-absolute-prohibitions--all-principals).

### C2. Destructive filesystem action on another task's resources
- **Trigger** Removing a task worktree or local branch.
- **Action** The filesystem permits it; the charter still governs. Run the full Done terminal-integrity gate first, bind to exact paths/refs, require a post-delete receipt.
- **Authority** Coordinator-approved ONLY for verified redundant task-local copies (merged canonical PR at accepted head, clean tree, nothing unpushed, no live dependant). Any unique state → Human.
- **Never** Force-remove on uncertain ownership or while a process holds the cwd.

### C3. A filesystem or broker denial
- **Trigger** Permission denied, path unavailable, guard refusal.
- **Action** Record the exact error and request registration or a reviewed operation.
- **Escalate to** Kandev Support (environment) — see [G1](#g1-an-environment-blocker-stops-a-task).
- **Never** Treat a denial as a puzzle to route around.

### C4. Shared coordinator repo (knowledge sync)
- **Trigger** Any edit to shared knowledge files.
- **Action** `git rebase main` before editing; commit small; `git -C /data/home/Code/coordinator merge --ff-only <your-branch>`; push. On conflict, hand-merge and preserve both sides.
- **Never** Force-push, `reset --hard`, rewrite published history, merge-commit onto main, or touch another worktree's branch. To rescue a stranded peer branch, cherry-pick onto YOUR branch.

### C5. Pruning redundant local worktree branches
- **Trigger** Local worktree-generated branches remain after their worktree registrations have been removed.
- **Action** Follow [Prune only fully integrated orphaned local worktree branches](RUNBOOK.md#prune-only-fully-integrated-orphaned-local-worktree-branches): enumerate exact local refs and live worktree branches, require every candidate to be absent from the live set and contained in the intended base, then use non-force deletion on each explicit ref.
- **Authority** Only a bounded, explicitly authorized repository-local cleanup. A branch with unique commits, ambiguous ownership/base, an active worktree, or a failed probe is preserved.
- **Evidence** Pre/post ref counts, candidate-list digest, zero unmerged candidates, every live branch still resolving, and unchanged base/remote/protected ref inventories.
- **Never** A destructive glob, `branch -D`, remote deletion, inference from a name alone, or generic automatic pruning that can break archive/unarchive recovery.

---

## D. Docker: task Compose vs Coordinator source broker

### D1. An ordinary task needs containers
- **Status** **VERIFIED WORKING — task-scoped Compose with fail-closed raw Docker.**
- **Action** Run Compose only from a disposable or task-owned directory inside the current task root. For an isolation acceptance test, prove one task-owned service can start and execute, then prove unrelated direct Docker operations are rejected before daemon access. Follow [Verify task-scoped Compose isolation](RUNBOOK.md#verify-task-scoped-compose-isolation-from-a-guarded-task-session).
- **Capability** Task-scoped `docker compose` only, inside its own task scope.
- **Authority** The task's own. The Coordinator directs; it does not run the task's runtime for it.
- **Evidence (verified 2026-08-29)** A disposable Alpine Compose service started and its in-volume ready marker was readable; `docker inspect`, `docker exec`, and `docker stop` against an unrelated name each exited 78 with `guarded Docker access supports 'docker compose' only`. The disposable container, network, volume, file, and directory were removed.
- **Never** Raw daemon or socket access, another Docker binary, bind mounts outside the task root, or an unrelated container. If a read-only direct probe unexpectedly succeeds, stop the negative test before issuing a mutating command and report the boundary regression.

### D2. The Coordinator needs workspace container data
- **Trigger** Diagnosis needs container metadata, logs, or task data.
- **Action** Progressive disclosure, least revealing first.
- **Capability** `docker kandev source list` (authoritative inventory; empty list ends the investigation) → `docker kandev source inspect <listed-container>` → `docker kandev source logs <listed-container> --tail N --since D` → `docker kandev source db-dump <listed-container> --target-task <full-uuid> --name <name>.sql`. Procedure: [source broker](RUNBOOK.md#retrieve-workspace-container-data-only-through-the-source-broker).
- **Authority** Standing autonomous authorization for broker-validated Coordinators, including production-like data requested by an active same-workspace task. No case-by-case Human approval; broker validation is authoritative.
- **Evidence** Run only from `/data/tasks/<coordinator-task-directory>/coordinator`, never the shared checkout. Delivery receipt = inbox path + byte count + SHA-256, plus the target's verification, isolated import, schema/data checks, and prompt deletion. A valid hash or a silent client alone is not a restore receipt.
- **Never** Guess a container name; repost suspected credentials from redacted logs; target or inspect a non-Coordinator-created ToDeploy task; use `docker exec`/`run`/`cp`, the Docker API/socket, a container shell, or cross-workspace access.

### D3. Discovering what the broker can do
- **Trigger** Unsure whether a broker capability exists.
- **Action** Run the subcommand bare — `docker kandev source`, `docker kandev support`. **`docker kandev` with no arguments under-reports**: it prints only `guarded Docker access supports 'docker compose' only` and never mentions `source` or `support`, both of which work.
- **Never** Conclude from top-level help that a documented capability is missing, or call `kandev-agent-docker-broker --help` (it blocks with no output).

---

## E. Android UI-QA / emulator

### E1. A task needs an Android emulator or on-device UI-QA
- **Status** **VERIFIED WORKING — guarded headless AVD UI-QA.** Physical USB/device UI-QA remains **NOT PROVISIONED**; USB/ADB host passthrough is intentionally absent.
- **Trigger** Mobile task requires emulator execution or on-device UI verification.
- **Action** Use the guarded wrappers directly: list available AVDs, open/check KVM, launch one disposable AVD headlessly, wait boundedly for `sys.boot_completed=1`, collect the task's API/model/UI evidence, and shut it down. The host SDK and AVD catalogue are read-only definitions; do not modify them. Follow the [Android wrapper runbook](RUNBOOK.md#android-ui-qa-through-the-guarded-emulatoradb-wrappers).
- **Capability** Guarded `emulator` and `adb` wrappers at `/usr/local/bin`; read-only host SDK and AVD catalogue; agent-local adb on port **5038**; `/dev/kvm` usable by the guarded execution path. There is no Coordinator-only entrypoint and no workspace-scoped KVM/ADB broker operation.
- **Evidence (verified 2026-08-29 in the resumed Coordinator session)** `os.open('/dev/kvm', O_RDWR)` succeeded; `emulator -accel-check` exited 0 with `KVM (version 12) is installed and usable`; `emulator -list-avds` returned the host catalogue; guarded `emulator -avd Pixel_3_API_29 ...` produced `emulator-5554`; bounded adb polling reached `sys.boot_completed=1`; the guest reported API 29 and model `Android SDK built for x86`; `adb exec-out screencap -p` produced a valid 1080x1920 PNG; `adb shell reboot -p` stopped it and final `pgrep` checks found no emulator, qemu, or adb process. SDK/AVD mounts remained `ro`, the protected Code parent remained non-writable, and no `codex-linux-sandbox` process wrapped tool commands.
- **Remediation (2026-08-29)** Two launch-path defects were fixed persistently: stored session `runtime_config.mode` could override the enforced full-access guard profile and re-enable the provider inner sandbox; and the `agentctl` user transition dropped the host KVM supplemental GID because the image lacked the matching group. Runtime mode fields are now migrated and protected against regression, and the rebuilt image creates/reuses the host KVM group and grants it to `kandev`. Earlier VERIFIED BLOCKED evidence came from a stale pre-recreate process and is superseded by the executed receipt above. Treat successful KVM open/acceleration as authoritative even if namespaced device ownership renders cosmetically as `nobody:nogroup`.
- **Never** Request `/dev/dri`, X11, Wayland, USB, raw Docker, a host adb server, or any privilege-escalation workaround — their absence is deliberate. Never claim physical-device capability. **Never substitute code-only evidence for an on-device acceptance criterion** — for genuinely code-only mobile work the ordinary `TEST_RUNTIME=NONE` path still applies ([Human-QA gate](RUNBOOK.md#human-qa-runtime-provisioning-is-an-acceptance-gate)), but that is not a stand-in for on-device QA.

## F. Description / prompt synchronization

### F1. `PROMPT.md` changed
- **Trigger** Any commit touching `PROMPT.md`.
- **Action** Mirror its **complete** current content into the live Coordinator task description, then **verify by comparing, not assuming**.
- **Capability** `docker kandev workspace description-update <file>` — the practical route for a 60 KB+ charter, verified present 2026-08-29 (`docker kandev workspace` lists it). `update_task_kandev` also accepts a description but requires sending the whole document inline. Bump the `<!-- version: ... -->` stamp in the same change.
- **Authority** Standing duty in the continuity checkpoint ([CONTINUITY](CONTINUITY.md)).
- **Evidence** A byte comparison of the live description against `PROMPT.md`.
- **Escalate to** Human — a failed mirror is a blocker, not a footnote, because running Coordinators are then on stale rules.
- **Never** Assume the mirror matched; never leave a partial/truncated description in place — a truncated charter is worse than a stale one.

### F2. This registry changed
- **Action** No charter mirror is required unless `PROMPT.md` itself changed. Bump `registry-version` and record the change in [LEARNING_LOG](LEARNING_LOG.md).

### F3. The state plan will not save
- **Trigger** Plan rewrite silently fails or exceeds the API limit.
- **Action** Archive history to `docs/archive/` and keep the live plan compact; the whole plan must be resent on every update.
- **Capability** [State-plan hygiene](RUNBOOK.md#state-plan-hygiene-keep-it-under-the-api-rewrite-limit).
- **Never** Send only a new section — that silently deletes everything else. Never invent an external actor to explain state you failed to persist.

---

## G. Contacting autonomous Kandev Support

### G1. An environment blocker stops a task
- **Trigger** Missing tool/dependency, permission or access failure, unavailable host capability, absent emulator/device support, or a similar host/container limit.
- **Action** Contact Support **yourself**, autonomously. Write a JSON request with four non-empty strings: `problem`, `evidence`, `expected_outcome`, `security_constraints`.
- **Capability**
  ```
  docker kandev support send <request.json>      # -> {"request_id": "...", "status": "queued"}
  docker kandev support status <request-id>      # -> queued | processing | complete (+ returncode)
  docker kandev support receive <request-id>     # -> full host-side Codex transcript
  ```
  Full procedure, schema, and gotchas: [Escalating an environment blocker](RUNBOOK.md#escalating-an-environment-blocker-to-kandev-support-host-codex-agent).
- **Authority** Standing. No Human relay for a routine request.
- **Evidence** `returncode: 0` plus a genuine assistant reply in `receive`.
- **Never** Use `codex exec resume` directly (it cannot work from a container); ask the Human to relay; target the support thread as a Kandev task/session; expose host `~/.codex`; or claim a delivery mechanism you have not exercised.

### G2. Composing the request
- **Action** Put the affected task/session ID inside `problem` or `evidence`. Pass the file path relative to the **coordinator task root** (e.g. `coordinator/support-request.json`) or absolute — a path relative to your shell cwd is the common failure.
- **Evidence** The broker attaches coordinator task ID, workspace/worktree, and request ID itself — do not duplicate them.
- **Never** Send secrets or raw credentials in any field.

### G3. Support returns a genuine terminal BLOCKED response
- **Trigger** `status` is `complete` with a non-zero return code and `receive` begins `KANDEV_SUPPORT_STATUS: BLOCKED`.
- **Action** Treat delivery as verified but the environment blocker as uncleared. Record the request ID, exact missing authority/capability, smallest next action, preservation receipt, and deterministic resume trigger; physically park the affected workflow task in Blocked. Do not resend the unchanged request.
- **Capability boundary** As verified 2026-08-29, the reviewed Support worker cannot directly edit persistent canonical workspace-repository inventory when no audited repair operation exists, and cannot provision/reuse GitLab credentials without a reviewed task-scoped credential broker. These are missing platform capabilities, not permission to edit backend state or mount host credentials.
- **Evidence** Full `receive` transcript, non-zero return code, no-mutation statement, and the named smallest next action.
- **Escalate to** Platform operator/Human only for the specifically named audited repair operation or scoped credential-broker capability; resume through Support or the task only after a non-secret acceptance receipt.
- **Never** Mark the request resolved because delivery completed; edit backend databases directly; mount host GitLab/Codex state; reveal or reuse host tokens; or create duplicate requests for the same unchanged blocker.

### G4. Support delivers results PROACTIVELY — do not poll, and do not relay through the Human
- **Trigger** A Support request has been sent and its `request_id` recorded.
- **Action** **Stop.** The final result arrives automatically as a new Coordinator message. Do not poll `status` in a loop and never ask the Human to relay. Verify the delivered claim independently before acting on it; if the result is incomplete or exposes a further defect, send a **fresh** request rather than resending the old one.
- **Evidence** Verified end-to-end 2026-08-29 (acceptance run below): results arrived as Coordinator messages with no status polling and no human relay.
- **Never** Poll continuously; treat a delivered claim as verified without checking it yourself; resend an unchanged request.

**A delivered `BLOCKED` result can still be a successful transport receipt but an
incomplete acceptance result.** If Support names a guarded-session assertion it cannot
execute and supplies a safe in-scope command, run that assertion in the named session.
Do not mark the underlying capability Blocked merely because Support lacks a cross-session
runner. If the assertion passes, send one fresh evidence-bearing Support request only when
the delivered result explicitly requires a follow-up; if it fails, send the exact output
as the new defect. Never duplicate the original request.

**B1/B2 acceptance (verified 2026-08-29).** Both host/mobile and scoped-Docker
requests arrived automatically as Coordinator messages without polling or Human relay.
Support correctly declared its inability to execute inside the live guarded session.
Coordinator-side execution then passed: the Android wrapper booted a KVM-backed
`Pixel_3_API_29`, collected API/model/PNG evidence, and shut down cleanly; task-scoped
Compose succeeded while unrelated `inspect`/`exec`/`stop` commands failed closed
with exit 78. Physical USB remains NOT PROVISIONED.

The evidence-bearing closure request `980ec435-5096-4dd6-af2e-6a50f5624c1e`
also arrived proactively, returned `KANDEV_SUPPORT_STATUS: RESOLVED`, accepted both
Coordinator-side receipts, and confirmed no platform change was required. This closes
the end-to-end acceptance; no `status` or `receive` command was used, so receive exit
codes are intentionally N/A for this proactive-delivery test.

### G5. The broker fails closed on bad input — exit 78, no request created
- **Trigger** Malformed JSON, or any of the four required strings missing/empty.
- **Evidence** Verified 2026-08-29 with two deliberate negatives, both **exit 78**, both creating **no** request:
  ```
  malformed JSON        -> kandev-agent-docker: support request is not valid UTF-8 JSON: Expecting value: line 1 column 31 (char 30)
  missing one field     -> kandev-agent-docker: support request requires non-empty problem, evidence,
                           expected_outcome, and security_constraints strings
  ```
- **Action** Treat exit 78 as a schema defect on your side. Fix the file and resend; do not retry unchanged and do not assume a partial request exists.

### G6. Acceptance run of the Support channel — 2026-08-29
Support-initiated end-to-end acceptance. Record kept because it establishes what is verified versus merely asserted.

| Case | Request ID | Sent | Routing |
|---|---|---|---|
| A2 host/deployment — Go module cache | `4a26bc2a-ef82-4711-9efe-3eb9644ae29e` | 16:39:07Z | host/deployment |
| A1 source/handoff — ACP guard prefix | `d6d8f689-7a70-4a8b-a2b0-627c7b9de0d3` | 16:39:32Z | source |

- **A2 finding, agent-side:** `/data/home/go/pkg/mod` is **writable** under the guarded session (`touch` succeeded; `GOMODCACHE=/data/home/go/pkg/mod`, `GOPATH=/data/home/go`). Asked Support to confirm the state is **persisted** rather than true only in the current runtime, and to say whether the D9/D14 stale-image degradation is resolved — a single runtime probe must not close it.
- **A1 finding, and the important one:** **the Coordinator has no surface to invoke summarize/handoff at all.** Enumerated: guarded Docker is `docker compose` only; `support` is send/status/receive; `workspace` is probe/description-update; `source` is list/inspect/logs/db-dump; the MCP tool space has no summarize verb. **So this fix is not verifiable by any Coordinator, before or after a regression.** The request therefore requires Support to prove the exact allowlist entry and regression result **and to return an agent-side acceptance probe**.
- **Standing rule this produced:** when a fix lands in a path you cannot reach, **require an acceptance probe you can run** as part of the fix. Otherwise the next regression is detected only by an operator noticing a failure in the UI.

**A2 result — `BLOCKED`, delivered proactively at ~16:40Z with no polling and no human relay.** Substantive and correctly scoped:
- Policy **is** persisted in deployment source: `main` at `7af25f5bad785aff7f2d1316d4cf170a9855be61` contains `aad8cd55`, binds **only** `/data/home/go` writable inside the guard, copies the guard into the image, and carries a regression probe. **No wider `/data/home` granted** — the security constraint was honoured.
- Support's own sandbox **refused** its `docker inspect` attempt ("directly uses raw Docker inspection, which the request explicitly forbids"), and it **did not route around it**. Constraint enforcement observed working on the Support side, not just asserted.
- **D9 partially resolved**: policy persistence and current guarded writability confirmed; **deployed-image / recreation-survival verification remains open** and cannot be closed by a runtime probe.
- D14 explicitly **not assessed** — correctly out of scope for a Go-cache-only request.

**The returned probe was defective, and this is why delivered results get verified rather than trusted.** Run verbatim it exits 2 with `GOMODCACHE: parameter not set`, because **`GOMODCACHE` is not exported in the guarded session** — `go env GOMODCACHE` knows it, the environment does not. It therefore fails *in the dangerous direction*: reporting failure while the cache is healthy. With the value sourced from `go env` the same body exits 0. Follow-up request `2cca45c8-59a5-48fd-be72-c5978c991870` sent 16:41:07Z asking for a corrected probe that derives the path, and asking whether the in-repo `tests/test-agent-guard.sh` probe shares the assumption.

**Separately observed:** `command -v lsof` -> `/usr/bin/lsof`, so **D14 looks resolved in the running environment** — but deliberately NOT closed on one runtime observation, having just been cautioned against exactly that for D9. Asked Support whether a persistence check is required.

**Rule this produced:** **a probe handed to you is a claim, not a fact.** Run it verbatim before recording it as the acceptance criterion; a probe that assumes an exported variable, a cwd, or a tool on PATH can fail in the direction that manufactures a false defect.

**A2b result — `RESOLVED`, delivered proactively at ~16:51Z.** Corrected probe supplied and **verified by me verbatim: exit 0, no residue left in the cache directory.** It derives the path with `go env GOMODCACHE`, keeps the narrow-path assertion, and removes its probe on interrupt via a trap. Support also answered both side questions: `tests/test-agent-guard.sh:84` never reads `$GOMODCACHE` (it probes `/data/home/go` directly, so the in-repo regression was never exposed to the false negative), and the guard's persisted allowlist contains only `/data/home/go` at `scripts/kandev-agent-guard:343`.

### Canonical Go-cache acceptance probe (verified 2026-08-29, exit 0)
```sh
sh -ceu '
  gomodcache="$(go env GOMODCACHE)"
  test "$gomodcache" = /data/home/go/pkg/mod
  test -d "$gomodcache"
  probe=""
  cleanup() { [ -z "$probe" ] || rm -f -- "$probe"; }
  trap cleanup EXIT HUP INT TERM
  probe="$(mktemp "$gomodcache"/.kandev-write-probe.XXXXXX)"
  test -f "$probe"; rm -f -- "$probe"; test ! -e "$probe"
  probe=""
'
```
**Run this after any container recreate.** Exit 0 is the acceptance criterion.

### Degradation status corrected on evidence, not inference
- **D9 (Go cache):** **partially resolved** — policy persisted in deployment source (`main` `7af25f5bad785aff7f2d1316d4cf170a9855be61` contains `aad8cd55`, binds only `/data/home/go`), current guarded writability verified. **Recreation-survival still unverified**; run the probe above after a recreate to close it.
- **D14 (`lsof`):** **runtime and deployment definition verified; recreation persistence pending.** `/usr/bin/lsof` exists now and `Dockerfile.local:21` installs it persistently. **Deliberately NOT closed** on a single runtime observation — Support explicitly set that bar and it is the right one. Close only when a recreated guarded session again passes `command -v lsof`.

**The wider rule both of these produced:** *a runtime observation proves the present, not the deployment.* Confirm the persisted definition **and** re-verify after recreation before closing an environment degradation.

**A1 outcome — `BLOCKED` twice, through an automatic second-pass escalation, and my diagnosis was refuted.** I had argued the guard was exiting early with `no agent command supplied`, reasoning from the script. Support disproved it: source builds `guard -- <ACP command>` and does not strip the executed argv; a guarded shell returned `guard-ready` and guarded `npx … codex-acp` stayed alive to a deliberate timeout, with neither emitting any `ERROR: kandev-agent-guard:` line. **The guard is not the failing component; the disconnect happens after launch.** Reading a script is not the same as observing the process — Correction #24.

**One thing I raised was confirmed and fixed:** the utility executor retains child stderr but omits it from the returned error, which is why this had to be diagnosed by reading source at all. Support wrote a narrowly filtered patch returning only `ERROR: kandev-agent-guard:` lines and never arbitrary provider stderr, honouring the constraint.

**That patch is uncommitted**, blocked by a mandatory hook failing on an *unrelated* typecheck (`service_pr_watch.go` undefined `taskID`/`status`). I checked: on `upstream/main` line 1024 sits inside `appendChangedField(changed []string, field string, isChanged bool)`, whose scope contains neither identifier, and three commits landed through the same hooks today from main-based worktrees. **So the blocker looks local to that checkout, not to main** — and Support's stated next action ("repair the unrelated undefined symbols") would mean editing a tree carrying substantial untracked human work (`slack/`, `voice/`, `debug/`, `system/logs/`, `logger/buffer/`, `loginpty/`, `process/`, `cli/src/`). Follow-up `bb2542e8-d356-488a-9a43-319f254fe1db` sent 17:02:15Z asking it to confirm that checkout's HEAD first and, if local, land the diagnostic from a **clean worktree based on main** instead of repairing anyone's work-in-progress.

**Rule: when a fix is blocked by an unrelated failure in a dirty shared checkout, move the fix to a clean tree — do not repair the dirt.** Unpushed human work is worth more than the convenience of committing in place.

### G7. A published plugin release is newer than the marketplace index
- **Trigger** A plugin release exists, but Settings/manual auto-update cannot discover it because the marketplace index still advertises the installed version.
- **Action** Verify the release artifact and version, then ask Kandev Support to use authenticated `POST /api/plugins/install` for that one published archive. Do not restart Kandev when the backend can refresh the live tool catalog.
- **Capability** [Update a live plugin when discovery is stale](RUNBOOK.md#update-a-live-plugin-when-the-marketplace-index-is-stale).
- **Evidence** HTTP install/readback status; exact live version, install path, status, auto-update, restart/error fields; and one real invocation of the newly registered schema from an existing session. Verified for Tags v0.14.0 by Support request `76d7e219-5e06-44f7-aae7-3ba8613f641e`: install 201, readback 200, active at `/data/plugins/kandev-plugin-tags/0.14.0`, and live `list_tags(task_id=...)` succeeded.
- **Never** Edit plugin YAML, database rows, or extracted installation files; never reload unrelated plugins or restart the whole application solely to refresh a compatible tool catalog.

### G8. Task-shell commands run but no output or completion arrives
- **Trigger** Even bounded `true`, `pwd`, or `git status` appears to start in a live task terminal but produces no output or completion.
- **Action** Preserve the task session and worktree, then ask Kandev Support for one disposable task-scoped terminal probe using the normal two-resize PTY protocol. The first resize starts the deferred shell; the subsequent resize establishes output wiring. This diagnoses the bridge only. Require Support to repair or expose the same sequence through the ordinary agent execution client, then verify an agent-issued non-TTY command and a distinctly agent-tool-allocated TTY before resuming the task. The TTY receipt must retain the tool's TTY/PTY selection and pass `test -t 0`, `test -t 1`, `stty`, `true`, `pwd`, and `git status`; a command merely labelled “TTY” or an inner `script`/`ssh -t` PTY is not evidence. If Support proves the ordinary model tool has no TTY selector, stop retrying Support and create a canonical platform capability task for a model-callable, guard-preserving TTY tool with durable `tty:true` dispatch evidence.
- **Capability** [Recover a task shell whose PTY output was never wired](RUNBOOK.md#recover-a-task-shell-whose-pty-output-was-never-wired).
- **Evidence** Support request `c0e1a9e7-bf39-49de-aa67-6d9a528aba2e` verified the disposable two-resize path, but the same task's ordinary agent path immediately hung again. Request `c97b3b47-febd-439b-a324-f29550413dd4` then deployed commit `6fcc88f689dae9797dd131229167a98d0e955d43` on the deployment-only `yattdev/kandev-service` `main` branch (not public `kdlbs/kandev` source), disabling Codex `unified_exec` only for `@agentclientprotocol/codex-acp`; independent session `c1ef931d-c98b-4af8-bd24-87352cf4da05` proved non-TTY output/completion with exit 0. Request `aaad659d-a9af-474e-bbb9-92a857665ab2` then proved the ordinary Codex ACP `commandExecution` event has no TTY field: App Server has client-side `command/exec tty:true`, but Support invoking it is not agent-issued and `process/spawn` is outside the Codex sandbox. Platform task `46945aff-382a-41a4-9f35-bd5c2806911e` owns the missing model-callable tool.
- **Never** Restart or replace the live task session, edit repository state, treat buffered-output absence as a command failure, leave the disposable Support terminal behind, or unblock from a Support-driven probe alone.

---

## H. Who owns a problem: Support vs project task vs Human

| The problem is… | Owner | Route |
|---|---|---|
| Host/container environment: missing tool or dependency, permission/access failure, unavailable host capability, emulator/device support | **Kandev Support** | [G1](#g1-an-environment-blocker-stops-a-task) |
| A defect in the kandev **product** (routing, env prep, scheduling, session lifecycle, API — anything in `kdlbs/kandev`) | **Board task** | Create a platform-bug task with symptom, evidence, where to look, and a regression-test acceptance criterion (PLATFORM BUG DUTY). No per-cycle cap — create one card per verified defect, however many that is |
| A defect in a task's own work | **That task's agent** | Direct it; do not implement for it |
| Destructive/irreversible on unique state, or security/trust-boundary | **Human** | `ask_user_question_kandev` with concrete options + recommendation |
| Human testing, physical access, or information only the Human has | **Human** | Visible ask — but never present ordinary task approval as the blocker |
| Anything else in this workspace | **Coordinator** | Decide, log vetoable, verify execution |

Support fixes the environment. Support does not decide product behaviour, approve
destructive actions, or substitute for the Human on trust-boundary calls.

---

## I. Hard boundaries

### I1. Reserved to the Human — preserve state and escalate visibly first
- Destructive or practically irreversible actions **that can remove unique or still-needed state**: deletion, reset/clean/discard, data/container removal, force-push, rebase/squash/amend of published history.
- Security or trust-boundary actions: secret/credential disclosure or scope expansion, authentication/authorization weakening, security-policy bypass, cross-workspace or trust-boundary access.

### I2. Explicitly NOT a second approval gate
Production, protected/release branch, cost, and external-communication **labels** do not by themselves create a second approval principal. Classify the concrete action by whether it is destructive/irreversible or security/trust-boundary, then decide or escalate. Verified redundant task-local worktree/branch cleanup is Coordinator-approved ([C2](#c2-destructive-filesystem-action-on-another-tasks-resources)) and must not be escalated.

### I3. Structural boundaries that never bend
- **Merging**: NEVER, by any agent, under any circumstance, until the human changes this (2026-08-29). Green/clean/approved = ready for a HUMAN decision, not authorization. No auto-merge, no directing an agent to merge; the full-approval grant does not reach merges.
- **Upstream `kdlbs/*` PR that is READY**: **Coordinator action, not a dead end** — post a mention of `@carlosflorencio` (maintainer, holds the merge) on the PR; add `@jcfs`/`@zeval` only when prior authorship on the touched paths shows they own that area. Readiness first (non-draft, green on current head, threads resolved). **Once per head**, recorded with PR number + head SHA; re-notify on a new push, never on an unchanged head. Agents are credential-blocked (D18), so the Coordinator posts it.
- **Merge asks**: resolve `base.repo.full_name` (not the head). `yattdev/*` or `ayattara-sfl/*` → human can merge, goes in NEEDS YOUR DECISION. `kdlbs/*` or third-party → human CANNOT merge, goes in WATCH as awaiting the upstream maintainer.
- **ToDeploy**: never move a task into it; never touch a task already in it unless this Coordinator created that task. A workflow-wide inventory may incidentally return its ID/title/column — issue no task-specific read or mutation.
- **Backlogs / ToDeploy** are Human-managed holding columns; **Human-QA** waits for Human review.
- **Cross-workspace**: no standing to move, message, flag, plan, or answer outside your workspace.
- **Own card**: never modify this Coordinator task's own step or state.
- **Wake sources**: Kandev routines only; never create or modify a routine, cron job, or scheduler.
- **Other tasks' descriptions**: never delete, close, or rewrite without separate explicit Human instruction; direction goes in comments.
- **Spend**: no action whose cost the Human has not authorized; cost alone is not an approval gate, but committing new spend is.
- **Production data**: sanitized, isolated, short-lived only; never mount, share, or mutate the main data store ([QA_INSTANCES](QA_INSTANCES.md)).
- **Task creation**: UNLIMITED per cycle, any in-scope repo (platform, plugin, project), any kind of work — bugs, features, capability, docs, fixes. No numeric cap, no approval gate (human-directed 2026-08-29). The gate is **viability**: verify the need against live evidence, check no existing card covers it, and be able to state problem / why it matters / acceptance criteria. Cannot justify it on evidence? Do not create it.
- **Other budget items**: uncertain whether a non-creation action is in budget? It is not — queue it.

---

## J. Failure and status semantics

### J1. Support request states
- `queued` — waiting its turn. `processing` — worker picked it up. `complete` — the run finished.
- **`complete` does not mean success.** Check `returncode`, then always read `receive`.
- Delivery is serialised, restart-safe, oldest-first. Latency is **seconds** on a clear queue and **minutes** while earlier requests drain. A long `queued` is the system working.
- **Action** Poll with adaptive backoff (seconds early, widening to ~30s). Never resend — a duplicate only adds another item to the same ordered queue.

### J2. Non-zero `returncode`
- **Action** Read `receive` for the real cause before concluding anything. Do not claim delivery succeeded.
- Ignore the host-side warning `failed to load models cache` / `missing field supports_parallel_tool_calls` — it appears on successful `returncode: 0` runs too. Diagnose from `returncode` and the assistant turn, never from the presence of an `ERROR` line.

### J3. Fresh request after a terminal failure
- **Trigger** An old request sits at `complete` / `returncode 1`.
- **Action** Terminal failures are **not** retroactively requeued. Check the old ID once, then send a **fresh** request.
- **Never** Reuse a terminal request ID or wait for it to self-heal.

### J4. Two Support failure modes that must not be conflated
- `no rollout found for thread id ... (-32600)` → **wrong route**; use the broker.
- `thread-store conflict: ... already has an active writer` → **right route**, host-side contention. Now handled as backpressure; if it resurfaces as a terminal failure, isolation has regressed — report it with the request ID rather than retrying in a loop.

### J5. Provider limits and credentials
- **Action** A rate-limit or credential hold is valid only for the cycle that observed it. Re-test every cycle; a stale hold silently freezes the board.
- **Evidence** Test the exact capability needed. `gh auth status` may report an invalid token while `gh api` REST succeeds. Prefer `gh api` REST and record which surface was tested.
- Persist a resource-keyed reset record in the state plan; the first routine at or after the buffered reset does one bounded retry. `401` is a credential blocker, not a rate limit.

### J6. Unexplained board state
- **Action** Suspect your own persistence failure FIRST. Compare your last successful state write against the board's change timestamps and read the actual move/handoff message — it carries the actor's tag.
- **Never** Invent an external actor to explain state you cannot account for, and never escalate that fiction.

---

## K. Visual QA image inspection

### K1. A task has local PNG screenshots that require visual acceptance
- **Status** **VERIFIED WORKING — approved local image inspection.** This is distinct from checking file type, dimensions, or hashes, which do not prove visual content.
- **Trigger** QA requires pixel/content inspection of screenshots already preserved in a task workspace or `/tmp`.
- **Action** Use the approved `view_image` capability on each decisive PNG, inspect the rendered content against the criterion, and record a per-file PASS/FAIL receipt. Follow [Inspecting QA screenshots](RUNBOOK.md#inspecting-qa-screenshots-with-view_image).
- **Capability** `view_image({path: <absolute-local-path>, detail: "original"})` for task-workspace or temporary images.
- **Evidence (verified 2026-08-29 after the Kandev runtime recreation)** Three valid PNGs — desktop web, responsive web, and native Android — decoded immediately in the consuming QA session. The agent visually confirmed the disabled historical participant and stored answer, with no task-related clipping, overlap, or error artifact, then advanced QA.
- **If it fails** One bounded retry after a known runtime/process recreation is enough. A fresh call that remains RUNNING without output is a Kandev product/tool defect: preserve the artifacts, record path/timestamp/duration and termination receipt, and route one platform board task under [H](#h-who-owns-a-problem-support-vs-project-task-vs-human). It is not a host-environment Support request and not a feature-code failure by itself.
- **Never** Substitute `file`, dimensions, checksums, DOM/XML hierarchy, responsive-web output, or console cleanliness for the required visual/native evidence. Never repeat unbounded hangs or delete the preserved images before the receiving QA/PR step has durable evidence.

---

## Maintenance

**Any verified new capability, limitation, workaround, or Support resolution updates
this registry and every affected runbook / decision / learning record in the SAME
change.** A capability proven in a session but not written down is lost at the next
session boundary, and a registry that lags the runbook is worse than none because it
is consulted first.

Rules:
1. Bump `registry-version` on every content change.
2. Route detail correctly: authority → `PROMPT.md`; procedure → `RUNBOOK.md`; rationale and supersessions → `DECISIONS.md`; the cycle receipt → `LEARNING_LOG.md`. This file holds the decision router only — link, do not copy long procedures.
3. A contradiction with a linked document is a defect. Fix both sides in one change; never leave two live rules disagreeing.
4. Record known gaps and conditional capabilities explicitly (see [E1](#e1-a-task-needs-an-android-emulator-or-on-device-ui-qa)) rather than omitting the situation — an absent entry reads as "no guidance", a recorded gap reads as "verified absent".
5. Verify every added link resolves before committing — and verify your checker first. A heading anchor is: lowercase; strip everything that is not a word character, whitespace, or ASCII hyphen (**underscores survive**, em-dashes and backticks do not); then replace **each** whitespace character with one hyphen (runs are **not** collapsed, so `IDLE — read` yields `idle--read`). A checker that strips underscores or collapses runs reports false breakage and invites "fixing" links that were already correct.
6. **A capability claim must name what was executed.** Record a status as working only after running the capability in the context that will actually use it, and state the command and its observable result. Neither absence of documentation nor presence of configuration is evidence: on 2026-08-29 an exhaustive knowledge-base search wrongly concluded Android was unsupported, and a configuration inspection then wrongly reported it verified end to end — only an actual emulator launch settled it. Use the four honest statuses: **VERIFIED WORKING** (executed here, with evidence), **VERIFIED BLOCKED** (executed here, failed, with the exact error), **UNVERIFIED** (not executed in this context), and **NOT PROVISIONED** (deliberately absent by design).
7. A verification does not transfer across execution contexts **or across process lifetimes**. Say which context was tested and when. A capability can be present, configured, and still unusable where it is needed; and a long-lived agent process keeps the device/group policy it was created with, so after an image rebuild or force-recreate an earlier negative result is stale until re-executed in a fresh process. Re-test before carrying any BLOCKED verdict forward, and never let a cosmetic display (e.g. namespaced ownership rendering as `nobody:nogroup`) stand in for an executed check — it reads identically whether access succeeds or fails.
