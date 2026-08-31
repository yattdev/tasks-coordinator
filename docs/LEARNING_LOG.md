# Coordinator learning-cycle log

## 2026-08-21 — semantic merge-result and mixed-CI triage

- Added semantic merge-result triage: a current-main test that contradicts an
  accepted feature invariant is an integration-phase reconciliation problem,
  not permission for Human-QA to regress production behavior or rewrite the
  branch.
- Required fresh testing of the actual merge result after the upstream fixture
  or expectation is corrected under integration authority.
- Added per-job CI classification: runner/artifact/setup breakage remains
  infrastructure, while a deterministic product failure in another shard of
  the same red workflow remains task-owned and actionable.
- Files: `docs/RUNBOOK.md`, `docs/DECISIONS.md`, and this log. `PROMPT.md` was
  unchanged, so no live task-description mirror is required.
- Policy commit: `cc0f3ad` (`docs(coordinator): classify merge-result
  failures`). Shared `main` fast-forwarded successfully with no conflicts or
  unresolved items; this receipt commit was fast-forwarded separately.

## 2026-08-21 — exact-head runtimes and credential-scoped PR recovery

- Made QA-instance validity explicitly exact-head: any push or integration
  commit withdraws readiness until the task-owned LAN container is rebuilt and
  revalidated; stale instances are excluded from current inventories.
- Added a bounded fallback for authorized mechanical PR-thread work when a
  task-local credential broker fails but the Coordinator has its own valid
  repository-scoped identity. The fallback requires canonical repo/head proof,
  concrete code/test evidence, per-thread reply URLs, and a final unresolved
  count; it never transfers credentials or expands into implementation/merge.
- Recorded that provider rate limits make follow-up evidence unavailable, not
  green, and that successful external PR actions during a wedged Kandev session
  do not substitute for a monitoring cycle or board persistence.
- Reinforced that repeated routine wakes cannot recover a wedged task-control
  transport: one bounded probe, terminate, replace the caller session, and do
  not emit a standup or completed-cycle receipt from partial evidence.
- Files: `docs/RUNBOOK.md`, `docs/DECISIONS.md`, and this log. `PROMPT.md` was
  unchanged, so no live task-description mirror is required.
- Policy commit: `305cd10` (`docs(coordinator): tighten recovery evidence
  boundaries`). Shared `main` fast-forwarded successfully with no conflicts or
  unresolved items; this receipt commit was fast-forwarded separately.

## 2026-08-21 — stale sessions and gate ownership

- Captured physical workflow-gate ownership: ad-hoc Work-stage review evidence
  does not skip Review/QA, while a physical exact-head Review PASS must not wait
  on downstream CI.
- Added stale `RUNNING` diagnosis and recovery: verify process/output/timestamp,
  stop repeated queue writes, respect parent-scoped stop authority, and replace
  only a wedged caller session when necessary.
- Recorded that database writes, credential extraction, and shared-backend
  restarts are not task-control recovery mechanisms.
- Added containment guidance for an unauthorized history rewrite and a fresh
  LAN-instance/credential inventory procedure.
- Files: `docs/RUNBOOK.md`, `docs/DECISIONS.md`, `README.md`, and this log.
- Policy commit: `4d98343` (`docs(coordinator): harden stale session recovery`).
- Merge result: shared `main` fast-forwarded successfully to the policy commit;
  no conflicts. The log/link commit was then fast-forwarded separately.
- `PROMPT.md` was unchanged, so no live task-description mirror was required.

## 2026-08-22 — Human-QA instance provisioning cycle

Lessons captured, all incident-derived from a single Human-QA provisioning cycle
across 18 tasks and 16 containers:

- Fixture fit: copying the live database into QA instances is the wrong default.
  It produced a copied `master.key` in a LAN-published container, an instance
  serving the whole board unauthenticated, and several wasted rebuilds — and it
  could not exercise the features anyway. Tasks that refused the instruction were
  right; their refusals contained the incident faster than review did.
- Order of operations: "load real data, then verify isolation" creates the
  exposure before checking it. Features that ACT get synthetic data.
- Evidence discipline: report the primary SESSION state, not the board column. A
  task sat idle and blocked for 90 minutes while being reported as implementing.
- Inherited vs owned failures: bisect before assigning. A launcher panic on a
  73-file PR touched zero launcher files; `upstream/main` itself failed to compile
  and cascaded ~10 red checks onto unrelated clean PRs.
- Shared repairs land once. Narrow cherry-picks only for tasks physically blocked
  from committing locally.
- Provenance: layered images report the BASE OCI revision; plugin binaries carry
  no VCS stamp (`(devel)` + zero pseudo-version); compare payload digests, never
  the outer tarball SHA; a build timestamp is not provenance.
- Green CI is not universal evidence — env-dependent defects pass on runners and
  fail deterministically in agent containers, and the reverse.
- Enumerate-then-fix beats one-item-per-CI-round discovery.
- A host redirect may be deliberate: scope it (`-i <lan-if>` / `! -s 172.16.0.0/12`),
  do not remove it. Verify from a throwaway bridge container.
- An honest "not testable here" beats a display-only fixture, which converts an
  infrastructure gap into a false bug report against the feature.

Files changed: PROMPT.md (version stamp, Human-QA gate extension, triage evidence
rule), docs/QA_INSTANCES.md (new, linked from PROMPT/RUNBOOK/README),
docs/RUNBOOK.md (six playbooks), docs/DECISIONS.md (four decisions), README.md.

Not carried into shared policy: instance ports, container names, credentials,
task IDs, and per-task status — all transient.

## 2026-08-22b — infra fixes, base-branch breakage, task-startup recoveries

Lessons captured since 518382a:

- Task startup: an untrusted worktree `mise.toml` fails sessions at ACP init;
  `mise trust` + respawn is the fix. A subtask stranded in Backlogs must be moved
  to Work before a respawn does anything.
- Broken BASE: `upstream/main` failed to compile and cascaded red CI onto every
  mergeable PR; N tasks independently reporting the same failing line is evidence
  of a broken base, and the fix is landing ONE repair PR, not N cherry-picks.
- Verify operator infra fixes with the defect's own acceptance test — a NAT-rule
  "fixed" report was re-probed from a bridge container and still failed; the
  definitive Docker-egress test is a full `apt-get update`, not just a fetch.
- Deliberate host rules are scoped (inbound iface / exclude container sources),
  never removed.
- rolldown/rollup optional-binding misses after fresh pnpm install are a known
  install artifact, not an environment block; confirm via other worktrees, remedy
  with `pnpm install --force`.
- Ask-channel reaffirmed by the operator: use it for blocked tasks, not just own
  escalations; prose is not surfacing.
- QA: identify which component a UI control belongs to before filing a defect
  (adjacent enhance-prompt-button vs notes-enhance-button phantom defect).

Files: PROMPT.md (ask-channel reaffirmation, verify-operator-fix, version stamp),
docs/RUNBOOK.md (5 playbooks), docs/DECISIONS.md (3 decisions), docs/QA_INSTANCES.md
(phantom-control), docs/LEARNING_LOG.md.

Not carried into shared policy: PR numbers, ports, container names, credentials,
task IDs, per-task status — all transient.

## 2026-08-22c — base-repair recovery, zero-diff disposition

Lessons since a011058:

- Zero-diff platform fix → Done directly (skip PR/CI-Fixup): dd4f90b0's host NAT
  remediation had an empty diff; its regression gate is the disposable-bridge apt
  probe, not code. Reconciled the ACTION BUDGET Done rule to cover this.
- Broken-base dispatch hold: hold when upstream/main does not compile; lift by
  compiling the base, not by tracking the escalated PR (repair landed via #2916,
  not the escalated #2842).
- After a base repair, feature-complete branches flip CONFLICTING — classify as
  integration-pending (branch-green, review-ready, conflict resolved post-Human-QA);
  do not merge main in Human-QA to "fix" it; expect a wave, do not ping each.
- Degenerate test assertion (`expect(``).toContain(...)`, empty template literal)
  reads red regardless of the code — check the test before blaming the feature.
- Cross-task delegation edges belong on the DEPENDENT pointing at the prerequisite,
  never the reverse; a prose-only delegation is not mechanically enforced.

Files: PROMPT.md (ACTION BUDGET zero-diff Done + dispatch-hold, version stamp),
docs/RUNBOOK.md (4 playbooks), docs/DECISIONS.md (2 decisions), docs/LEARNING_LOG.md.
Not carried: PR numbers as policy, ports, credentials, task-specific status.

## 2026-08-22d — base-repair recovery confirmed; boundary-verify technique

Little NEW policy this cycle — the eventful lessons (zero-diff Done, dispatch hold,
integration-pending, mise-trust, fixture-fit) were captured in 2026-08-22a..c and
held true as the board recovered. Deliberately did not manufacture duplicate rules.

One durable addition: how to verify a resumed Human-QA task stayed within the phase
boundary — `git merge-base --is-ancestor upstream/main HEAD` false = boundary held;
distinguish an old history merge from a current-cycle merge. Confirmed in practice:
957da1cb resumed post-hold, fixed real E2E fixtures RED->GREEN, did NOT merge main
(boundary preserved); b6fb09ba #2842 went from thin/CONFLICTING to 52/52 green as
the base repair propagated (self-resolving, no ping).

Also reaffirmed: repeated zero-change monitoring cycles returning "no action" are
correct on a quiet board and must not manufacture pings (existing PROMPT rule).

Files: docs/RUNBOOK.md (1 playbook), docs/LEARNING_LOG.md. No PROMPT change → no
task-description mirror needed.

## 2026-08-22e — active board-management sweep (operator-directed)

Operator directed: "monitor board for CI issues, move tasks forward/backward, give
update." Ran a full monitored-steps sweep and acted. Durable lessons:

- A branch that MERGED a broken base carries the breakage; re-running CI never
  clears it. Fix = integrate the repaired base (a CI-Fixup action, not Human-QA).
  Distinct from integration-pending CONFLICTING. (c642d57a #2909 merged broken main
  at 999d60327 before #2916 repaired it.)
- A Spec/plan-mode task blocked on a KNOWN fix is unblocked by moving it to Work
  (edit capability), not by more discussion; decide the fork it raised rather than
  parking it. (6a5a2f73 stuck read-only 7h on the userns line-69 assertion fix.)
- CI-Fixup task with green CI and nothing left to fix advances forward, not idle.
  (55d2d589 #2800 sat 14h at 35/35 green → moved to Human-QA.)
- Under GitHub rate limiting, fall back to a task's own self-reported CI state and
  say so.

Files: docs/RUNBOOK.md (3 playbooks), docs/LEARNING_LOG.md. No PROMPT change.
Not carried: PR numbers/heads, task-specific status.

## 2026-08-24 — reproduction-preservation, credential push-wall, state-plan hygiene

- Do NOT apply a safe one-off workaround to a FAILED task that is the live
  reproduction for an in-flight platform fix. 375dcc90 (stale-worktree) had a
  verified-safe `git worktree remove` ready, but c0db9627's platform fix used
  375's worktree as its repro; preserving the failed state was correct. Added a
  PROMPT caveat to the blessed operational-fix power + RUNBOOK/DECISIONS entries.
- A shared credential/push wall (git_credential_lease_invalid across multiple
  tasks) is a platform defect; escalate the fix PR (#2940, Human-QA), relay
  reads/comments and push preserved fixes via coordinator creds best-effort, do
  not per-task-workaround. Parked tasks with preserved fix branches are correct.
- State-plan hygiene: the persisted plan can exceed the API rewrite limit and stop
  updating; keep it compact and archive history proactively.

Files: PROMPT.md (op-fix caveat, version stamp), docs/RUNBOOK.md (3 playbooks),
docs/DECISIONS.md (1 decision), docs/LEARNING_LOG.md.
## 2026-08-24 — Done-column durability incident

Task `9ededcef-07cd-45fa-97b1-6b899becef74` exposed the missing terminal audit:
the linked PR was merged and the task moved Human-QA → ToDeploy → Done, while a
later local commit appeared not to have been pushed. Follow-up archaeology proved
the landed implementation already covered the original scenario through later
work, but that recovery does not make the process safe: a merged PR cannot prove
that the final local head contains no unique work.

Policy change: every cycle now enumerates Done; new/changed entries get a
repository/session/resource terminal-integrity receipt, and unique local work is
preserved and returned to an active recovery step. Cross-agent boot shims now
force a full `PROMPT.md` and live-plan read on every turn. Files changed:
`PROMPT.md`, `AGENTS.md`, `AGENT.md`, `CLAUDE.md`,
`.github/copilot-instructions.md`, `README.md`, `docs/DECISIONS.md`,
`docs/RUNBOOK.md`, and this log.

## 2026-08-24f — explicit wake contract, fixture prerequisites, visual publication

- The short `WAKE:CYCLE` marker was too easy to interpret as a status sweep.
  Human direction expanded it into an explicit action contract covering live
  bootstrap, complete active+Done inventory, bounded helper delegation with
  primary accountability, evidence-based failure diagnosis, safe board action,
  exact-head draft readiness, visible escalation, and terminal reconciliation.
- A sessionless synthetic task produced no mobile panel DOM or storage request.
  Code-path inspection and an exact fixture query proved the handler correctly
  required an effective session ID. Durable rule: verify every entry-condition
  prerequisite before interpreting a no-op; invalid fixtures are not product
  defects, and named automated coverage may prove the valid path.
- Sanitized local screenshots can prove that QA was performed but do not satisfy
  reviewer-facing visual evidence until attached to the PR/MR. Provider auth or
  rate limits keep the PR draft; preserve paths/hashes and exact-head identity,
  avoid binary evidence commits or unapproved hosts, and publish after recovery.

Files: `PROMPT.md`, `README.md`, `docs/RUNBOOK.md`, `docs/DECISIONS.md`,
`docs/QA_INSTANCES.md`, and `docs/LEARNING_LOG.md`. Transient task IDs, ports,
container names, credentials, PR states, and provider reset times were excluded.

## 2026-08-24g — proactive follow-up for interrupted delegations

- A helper using a rate-limited model received new work but could only emit the
  provider limit message and never returned the requested receipt. A delivered
  message and `WAITING_FOR_INPUT` therefore cannot be treated as completion.
- Every reply-bearing delegation now gets a persisted follow-up ledger entry
  with expected evidence, next check, attempt count, observed failure/reset,
  owner, and fallback. Routine cycles reconcile due entries, retry once after a
  known reset, and route urgent or repeatedly unanswered work instead of
  silently abandoning it or spamming duplicate requests.
- The ledger is driven by existing routine wakes; it does not create a scheduler
  or polling helper.

Files: `PROMPT.md`, `docs/RUNBOOK.md`, `docs/DECISIONS.md`, and
`docs/LEARNING_LOG.md`.

## 2026-08-24h — model-independent continuity checkpoints

- The Coordinator's identity and capability must not depend on one model
  session remaining alive. Durable continuity now has three layers: binding
  policy, reusable versioned capability, and live operational state.
- Every new/resumed/switched session has an explicit load protocol; every turn
  has a save checkpoint. Replacement sessions receive executable obligations,
  evidence identities, follow-up triggers, fallbacks, and preserved-work paths.
- Hard interruptions are recovered from source evidence. The contract does not
  pretend to preserve private hidden reasoning; it preserves decisions,
  evidence, procedures, and unfinished work.

Files: `PROMPT.md`, all compatibility boot loaders, `README.md`,
`docs/CONTINUITY.md`, `docs/DECISIONS.md`, and `docs/LEARNING_LOG.md`.

## 2026-08-28 — missing linked-worktree administration recovery

- A readable linked-worktree `.git` pointer is insufficient validity evidence
  when its per-worktree admin directory disappeared during restoration.
- Native `git worktree repair` does not reconstruct that missing target, while
  automatic recreation can erase unique checkout content.
- Recovery is task-identity scoped: preserve and inventory content first,
  restore the exact validated admin entry when available, otherwise use an
  authorized snapshot/new-path rematerialization, then verify read-only Git
  metadata and one bounded agent start. A repair task must not inspect or mutate
  foreign task worktrees merely because it owns the platform defect.

Files: `docs/RUNBOOK.md` and `docs/LEARNING_LOG.md`.

## 2026-08-28b — linked-worktree backlink/marker mismatch

- A restored task can fail before consuming its handoff even when its `.git`
  metadata exists: the linked-worktree backlink may disagree with Kandev's
  task/workspace marker.
- Repeated session starts cannot repair an ownership mismatch. Preserve the
  checkout and validate the marker, pointer, reciprocal admin entry, task/repo
  ownership, branch, and HEAD under the owning task identity.
- Repair only the inconsistent metadata atomically, then prove read-only Git
  resolution and one bounded start. Ambiguous ownership stops recovery; it does
  not authorize speculative recreation or cleanup.

Files: `docs/RUNBOOK.md` and `docs/LEARNING_LOG.md`.

## 2026-08-28c — first-class Coordinator plugin principal

Window: no prior explicit `WAKE:LEARNING` timestamp existed, so this cycle used
the available Coordinator cycle logs and direct Human corrections through
2026-08-28T03:54:27Z.

- Captured one durable architectural decision: an ordinary task remains the
  bootstrap fallback, while the target Coordinator is a workspace-scoped plugin
  principal with isolated durable state and audited, mediated board/session
  operations rather than unrestricted cross-task filesystem access.
- Rejected as already covered: reset-aware GitHub retries versus invalid
  authentication; unanswered-session follow-up; verified redundant task-local
  cleanup; and missing/backlink-mismatched linked-worktree administration.
- Rejected as transient: current PR heads, provider states, task/session IDs,
  runtime ports, and the latest Redmine recovery receipt.

Files: `docs/DECISIONS.md` and `docs/LEARNING_LOG.md`.

## 2026-08-28d — task creation, briefing, and environment constraints

Window: 2026-08-28T15:00Z through 2026-08-29T00:15Z, derived from this session's
cycle logs. All four lessons are incident-derived from Coordinator errors or
confirmed environment behaviour, not speculation.

- **Pass `repository_id`, never `repository_url`, when creating a task in an
  existing workspace.** A URL can resolve to a *second* repository record whose
  materialization path the agent guard refuses, so the task cannot boot at all:
  `ERROR: kandev-agent-guard: Git common directory is outside an approved Code
  repository`. Census `repository_id` across the board first and reuse the
  dominant one — on this board 40 of 51 tasks shared a single record while the
  mistaken task got an outlier. Diagnose this as a Coordinator error; it is not
  an operator registration request and not a guard defect.
- **Create platform-bug tasks into Spec, not Work.** A detailed brief in the task
  description is NOT a plan artifact. A Work agent will correctly refuse
  (`WORK_INCOMPLETE`) because the Work step requires a current approved plan and
  forbids implementing from a guessed one — and the workflow may then
  auto-advance the empty card into Review, where there is no plan, diff, or PR to
  review. Route through Spec, let the Spec agent produce a real file map by
  inspecting the repository, then own the Todo → Work handoff.
- **Never cite a Coordinator-repository path as if it lived in the task's
  repository.** Briefing an agent to "read `docs/RUNBOOK.md`" sent a Spec agent
  hunting through `kdlbs/kandev` for a file that only exists in the Coordinator's
  own repo; it correctly reported the absence, refused to invent replacement
  prose, and carried a spurious risk entry into its plan. Quote the binding
  constraints inline in the brief instead of citing a path the agent cannot see.
- **A read-only default `GOMODCACHE` breaks Go commit hooks; task-local caches
  are the workaround.** Use `env GOMODCACHE=/tmp/<task-slug>-gomodcache
  GOCACHE=/tmp/<task-slug>-gocache` on every Go invocation, with a task-unique
  path to avoid cross-task collisions. Confirmed independently on two tasks. Part
  of a broader pattern: read-only mounts recur in this environment — the shared
  coordinator checkout at `/data/home/Code/coordinator` is mounted
  `ro,nosuid,nodev` as well — so suspect the mount before suspecting the code
  when an unexpected "read-only file system" error appears.
- **Stale `RUNNING` sessions settle on their own via orchestrator idle reclaim**
  (`idle reclaim: provider runtime released; row preserved for resume`). A
  cleanup-safety hold keyed on "a session is still RUNNING" therefore clears
  without the stale-session repair task landing, and must be re-verified from
  live session state every cycle rather than waited on.

Files: `docs/LEARNING_LOG.md`.

## 2026-08-29 — false history from silent persistence failure

Window: 2026-08-29T02:00Z–02:45Z, triggered by direct Human review corrections.

- **Silent persistence failure manufactures false history.** A Coordinator session moved 13
  cards Done→Blocked at 2026-08-28T02:05:52Z under its own
  `[COORDINATOR DONE-INTEGRITY RECOVERY]` tag, then failed to persist because the state plan
  had exceeded what `update_task_plan_kandev` can rewrite in one call. The next session found
  13 unexplained cards, inferred an "operator sweep", built an escalation on that premise, and
  asked the Human about it across several cycles. The Human corrected it: *"I did not move out
  13 cards from Done, you did it."*
  Rule: unexplained board state is FIRST a suspected persistence failure of your own. Compare
  your last successful write timestamp against the board's change timestamps, and read the
  move/handoff message on an affected card — it carries the actor's own tag — before
  attributing anything to a human.
- **A stale provider hold freezes the board.** A GitHub rate limit observed at 15:01Z was
  carried ~11 hours without retest; when finally re-tested it showed 5000/5000 remaining on
  both REST and GraphQL. Re-verify provider limits every cycle; a hold is valid only for the
  cycle that observed it.
- **Test the capability, not the summary command.** `gh auth status` reported `GH_TOKEN`
  invalid while `gh api` REST calls returned real data with full authenticated quota, and the
  `gh pr view` GraphQL path failed independently. Reporting "token invalid" from
  `gh auth status` alone was wrong and was repeated from another task's environment-specific
  claim without independent testing. Use `gh api` REST for provider verification and record
  which surface was actually exercised.
- **Do not relay a second-hand environment claim as verified fact.** The invalid-token report
  originated in one task's environment; repeating it board-wide without testing turned a local
  symptom into a false global degradation.

Files: `PROMPT.md`, `docs/LEARNING_LOG.md`.

## 2026-08-29b — CORRECTED: agent mount namespaces are private; never infer another agent's access

**This entry originally claimed a platform update had left every task worktree read-only.
That claim was WRONG and is retracted. Do not act on the earlier version.**

- **Each agent has a PRIVATE mount namespace.** The Coordinator's mount table shows only its
  own overrides. Another agent's task root can be `rw` inside that agent's namespace while
  appearing `ro` from the Coordinator's. `findmnt`, `/proc/mounts`, and a `touch` probe run
  from the Coordinator are therefore **not evidence about any other agent's access**.
- What actually happened: the Coordinator probed sibling task worktrees from its own namespace,
  saw `ro`, and escalated a board-wide read-only regression that did not exist. It then imposed
  a dispatch hold, withheld an approved UX direction, and declined to start a requested task —
  all on invalid evidence. An operator guard-rooted probe at
  `/data/tasks/recover-missing-link_596r7wik/kandev-source` showed task root, repository, and
  Git common directory all `rw`, `git add -A --dry-run` succeeding, and a real write
  succeeding; the owning agent then confirmed the same from inside its own namespace.
- **Rule: mount health is tested inside the target agent's namespace, never inferred from
  another.** To check whether a task can write, ask that task (or a guard-rooted probe) to run
  `git -C <worktree> add -A --dry-run` and report. Never conclude from the Coordinator's view.
- Correct reading of a Coordinator-side `ro` observation: it means *the Coordinator* lacks
  write access to that path — which may be a legitimate scope boundary — and says nothing about
  the owning task.
- Third instance in one day of the same failure mode: concluding a cause from evidence that
  could not support it (the others being a self-inflicted 13-card sweep misattributed to the
  operator, and a stale rate-limit hold). Before escalating an environment-wide claim, ask what
  observation would distinguish the hypothesis from its alternatives, and whether the evidence
  in hand actually does.
- Still true and unaffected by namespaces: intermittent GitHub 403 `rate limit exceeded` while
  `gh api rate_limit` reports full quota — a secondary rate limit, tracked separately.

Files: `docs/LEARNING_LOG.md`.

## 2026-08-29c — Filesystem & Docker contract independently validated PASS after the live-attestation fix

Rerun of the agreed contract (`docs/FILESYSTEM_DOCKER_CONTRACT.md`) from coordinator session
`2b3b715c-8dff-43b6-af81-5d0f1f94f246`, with real reversible write probes rather than the
read-only/audit inspection the previous attempt was limited to. All six requested checks pass.
Every §7 open implementation item is now delivered except the per-write audit (see below).

- **Guard-rooted per-task probe now exists** — `docker kandev workspace probe <task-uuid>`
  runs `kandev-agent-guard` fresh in the *target* task's namespace and returns task root, all
  relevant mount options, `task_write=ok`, and `git_add_dry_run=ok`. This is the mechanism
  §6 demanded; the Coordinator no longer has to ask the owning agent or guess from its own view.
  Cross-workspace target UUIDs are refused (`target task has no active task-scoped workspace`).
- **Coordinator elevation is attested, not asserted.** The guard matches the exported
  `KANDEV_TASK_ID`/`KANDEV_SESSION_ID` pair against `kandev.db` and derives the workspace from
  the matching row; when no IDs are exported it requires the sole active executor launch at the
  exact task root. A mismatched pair fails closed to ordinary task scope — observed directly:
  a guard invocation with cwd in another task's checkout, carrying this session's IDs, received
  ordinary scope with no workspace elevation. Eligibility is rechecked every 15s and revocation
  emits `scope_revoked` and SIGTERMs the child.
- **ACP stdin is preserved.** The recheck supervisor launches the guarded child as
  `"${run_guarded[@]}" <&0 &`, so the JSON-RPC channel survives. This session ran the entire
  validation without the stdin death that ended session `2a9451a6-eab5-4349-9adf-55a58f925086`.
- **Ordinary-task sibling isolation is real and verifiable from outside a namespace.**
  `pgrep -a bwrap` exposes every live guarded agent's full argv. A running task in another
  workspace showed exactly `--bind <repo>/.git`, `--ro-bind <repo>/.git/worktrees`,
  `--bind <repo>/.git/worktrees/<its own entry>` and **no** repo-parent bind. This is a
  legitimate way to verify another agent's scope without violating the namespace rule — read
  the argv the guard was launched with, not your own mount table.

**Finding — the Coordinator's repo grant shadows the sibling-admin overlay.** Coordinator scope
adds `--bind /data/home/Code/<repo>` for each registered checkout *after* the git-marker loop
has already applied the `--ro-bind …/.git/worktrees` overlay. bwrap mounts in order, so the
later parent bind hides it. Confirmed by mount ordering and by writing into a sibling admin dir.
Consequence: the Coordinator can corrupt the index/HEAD of all 118 sibling `coordinator`
worktrees and all 42 `kandev-source` worktrees — including the preserved unpushed-work
checkouts. This is within §3's grant, but §3's compensating control (condition 1: audit every
Coordinator write outside its own task root, with path and operation) is **not implemented**.
`/data/logs/coordinator-workspace-audit.jsonl` records scope *grants*, not writes. Either
implement per-write auditing or apply the coordinator repo binds before the worktree overlay so
the overlay survives.

**Finding — Go module cache is the one language cache the guard does not make writable.** The
support-path allowlist covers `.cargo`, `.gem`, `.npm`, `.local`, `.cache`, `.bundle`,
`.composer`, `.rustup` but not `/data/home/go`. Default `GOMODCACHE=/data/home/go/pkg/mod` is
read-only, so Go hooks fail unless a task sets a task-local cache. This is D9 and it persists.

**Finding — same-UID readability weakens two boundaries.** `/data/data/kandev.db` is readable
(mode 644 on a read-only mount): metadata for all 8 workspaces, 161 tasks outside this one, is
queryable without the broker. Separately, `KANDEV_AGENT_DOCKER_TOKEN` for every live agent —
including agents in other workspaces — is visible in `/proc/<pid>/cmdline`, and that token plus
a cwd inside the matching task root is the entire broker authorization. A cross-workspace
Compose-scope escalation is therefore plausible. **Not attempted** — exercising it is the
security/trust-boundary class the charter reserves for the Human. Pass tokens by fd or env, not
argv, and consider a per-workspace DB view.

Also cleared this cycle: D4 (shared knowledge base is `rw` again) and D5 (main checkout and
`feature/coordinator-long-liv-802` both at `98117b8`, zero divergence — nothing stranded).

Files: `docs/LEARNING_LOG.md`, `docs/FILESYSTEM_DOCKER_CONTRACT.md`.
## 2026-08-28 — workspace source authority and verified restore receipts

No precise prior learning-cycle timestamp was persisted, so this cycle used the
available activity since the final 2026-08-24 learning-log entry as its window.

Lessons captured:

- Broker-validated Coordinators have standing authority to use source list,
  curated inspect, bounded logs, and logical database dumps—including
  production-like data requested by active same-workspace tasks—without
  case-by-case human approval. Broker workspace/target validation is the
  authoritative boundary.
- Dump delivery, database import, and restore acceptance are separate gates. A
  valid hash and present table DDL do not prove a complete destination restore;
  use a known-clean task-owned database, preserve the client's real exit/error
  evidence, verify schema/data and task behavior, and delete artifacts promptly.

Rejected by the filter: exact task IDs, artifact paths, hashes, byte/table/row
counts, ports, and engine patch versions were transient incident evidence; the
local patch-tool degradation was environment-specific rather than shared
Coordinator policy.

Files changed: `PROMPT.md`, `README.md`, `docs/RUNBOOK.md`,
`docs/DECISIONS.md`, and this log. Policy commits are `a76caca` (standing broker
authority after rebase) and `ffb1128` (restore acceptance).

Merge/mirror status: rebase onto `main` succeeded without conflict, but shared
main could not fast-forward because `/data/home/Code/coordinator` is read-only
(`unable to unlink old` for the four policy files). Main remained unchanged;
the complete `PROMPT.md` mirror is intentionally pending the required
fast-forward. Operator action is required; no filesystem workaround was used.

## 2026-08-29d — One blocker label, three different faults: split it by the exact error string

Four Blocked cards all carried "Git metadata is read-only". Re-probing each with
`docker kandev workspace probe <full-task-uuid>` split them into three unrelated faults, and
the deciding evidence was the **exact error text**, not the symptom class.

| Error | Real fault | Right owner |
| --- | --- | --- |
| `missing Git worktree directory for <marker>` (guard, exit 78) | The repository's `.git/worktrees/` registry is absent | the worktree-admin recovery task |
| `Unable to create …/index.lock: File exists` | Stale 0-byte lock, no process holding it | the task that owns the checkout |
| `Unable to create …/index.lock: Read-only file system` | Genuinely unwritable mount | the filesystem-contract task |

The last one no longer occurs anywhere on this board. The middle one had been misread as the
last one for two days because both surface as "cannot create index.lock" and nobody compared
the second half of the sentence. Three other cards had been pinned to the wrong owner entirely.

- **Rule: when several cards share a blocker label, re-derive each one's blocker from a live
  probe before carrying any of them forward.** A shared label is a hypothesis, not a finding.
  Cards inherit each other's diagnosis silently, and a stale shared label freezes a whole class.
- **Rule: compare the error string, not the failing operation.** `git add` failing proves
  nothing about *why*. Two of these faults are one word apart in the same sentence.
- A repository can lose its `worktrees/` directory *entirely* while `.git` stays healthy
  (objects, refs, packed-refs, logs all intact). Recovery code that creates an entry inside
  `worktrees/` must create the directory when it is absent, or it fails on exactly the case
  that needs it. Task checkouts survive this — the content is intact, only the registration is
  gone, so preserve and re-register rather than re-materializing.
- A 0-byte `index.lock` with no holding process carries no content; removing it loses nothing
  and Git recreates it. Verify both properties first, bind the approval to exact paths, and
  require stop-and-report if either fails. A non-empty or held lock is a different situation.

Also confirmed again, from the other direction: `gh api rate_limit` reported `core: 5000/5000`
at the same instant real REST calls returned 403 "rate limit exceeded for user ID 79718216".
The 403 **identifies the user**, which means the credential authenticates — so a companion
"token is invalid" degradation, sourced only from `gh auth status`, was refuted and folded into
the rate-limit record. Test the capability you need and record which surface you exercised.

Files: `docs/LEARNING_LOG.md`.

## 2026-08-29e — Read the conversation, not the session row; inspect the tree before prescribing git

Three Coordinator errors in one cycle, all the same shape: acting on a proxy for evidence instead
of the evidence. Two were caught before harm, one was caught three minutes after issuing an
unsafe instruction.

- **A session row is not a report.** `WAITING_FOR_INPUT` with a freshly advanced `updated_at`
  means the agent *finished a turn*, not that it swallowed the message. I read the row, concluded
  the session was dead, recorded a platform degradation that did not exist, and spawned a second
  agent onto a task that already had a working one — putting two agents in one worktree for forty
  minutes, which is exactly the duplicate-agent hazard the charter forbids. The agent's reply had
  been sitting in the conversation the whole time. **Before concluding a session is stuck, read
  what it last said.**
- **Never prescribe a git operation without inspecting the working tree.** I told an agent to
  "integrate upstream/main with an ordinary merge". That worktree was already mid-merge:
  `MERGE_HEAD` set, **5,404 staged files**, one unresolved conflict, nothing committed — the most
  valuable uncommitted state on the board, present in no commit and no remote. A cleanup attempt
  before merging would have destroyed it. Corrected within three minutes with an explicit
  do-not-touch list (`merge --abort`, `reset`, `checkout -- .`, `stash`, `clean`), and the merge
  landed safely. **Check for `MERGE_HEAD`, staged count, and conflicts before advising anything.**
- **A "baseline compile error" claim must be checked against the base.** An agent reported
  `service_pr_watch.go:1024` as an unrelated baseline failure. Had I accepted the label I would
  have frozen board-wide dispatch. `upstream/main` was healthy; the file on disk was a half-merged
  blend belonging to neither side, and the error dissolved when the merge committed. The agent
  reported precisely enough for the check to be possible — that is what a good report buys.

**The counterpart duty: supply proof the sandboxed agent cannot obtain.** An agent correctly
refused to remove two approved stale `index.lock` files because it could not prove them unheld —
`lsof` and `fuser` absent, 1,275 unreadable `/proc` descriptors. That refusal was right and should
not be overridden. The Coordinator sees more of the host, so gathering the evidence is the
Coordinator's job: no `git` process existed anywhere, which settles it, because only git creates
an `index.lock`. That argument does not depend on descriptor readability, which is what had
stopped the agent. Both files were 0 bytes at 37 and 26 hours old — git writes the new index into
the lock before renaming, so a 0-byte lock that old means the writer died before writing anything
and there is no partial state to lose. Re-approved with the evidence attached and the size check
kept as the live gate; the agent removed it. **When an agent stops for want of proof, decide
whether the proof is obtainable from where you stand — then obtain it and own the judgment.**

**Provider note:** a GitHub secondary rate limit cleared *before* the reset timestamp its own 403
advertised. A primary reset time does not govern a secondary throttle, so a conservative fallback
must be an upper bound that a successful response can cut short. The root cause was ours: 122
periodic workflow-sync failures in under four hours, 84 of them the same 403, six workspaces
bursting in the same second with no backoff. The board spent two days treating a self-inflicted
throttle as an external provider outage.

Files: `docs/LEARNING_LOG.md`.

## 2026-08-29f — An agent's memory of intent is not evidence of repository state

Within thirty minutes, three task agents reported work as uncommitted or unresolved that their
own repository showed as committed or already gone. Each was reporting from its plan and notes
rather than reading `git log`, `git status`, or the filesystem.

| Task | Claimed | Actual |
| --- | --- | --- |
| `1f8d4dc8-83ac-44d6-9fbd-b34bd46e044e` | "executor admission in progress, no SHA yet" | `7aca62dbf` committed on merge `f59ecf081`; tree clean; 4 ahead / 0 behind |
| `b74833e7-a05f-4cdf-81cf-db5b4c02f368` | "both locks still exist and are zero bytes" | both absent; no `index.lock` anywhere under the registry; probe `git_add_dry_run=ok` |
| `23a62467-37e9-4113-b374-b44003abc0f3` | "validator uncommitted, ADR outstanding, no SHA" | `dc4149c1d` and `15adf4b1e` committed; tree completely clean |

Two of the three also contradicted their *own* earlier message. `b74833e7` had already written "the
dry-run now passes after its stale lock was removed" before reporting the locks as still present.

- **Verify a status claim against the repository before acting on it.** Every one of these would
  have cost something: re-implementing committed work, re-issuing an instruction already carried
  out, or — in `b74833e7`'s case — requesting a new host capability to solve a problem that no
  longer existed.
- **This is the same failure mode as reading a session row instead of the conversation** (entry
  2026-08-29e). It is not agent-specific; it is what happens when any actor treats its own notes
  as the source of truth. The Coordinator is not exempt — that entry records the Coordinator doing
  exactly this and spawning a duplicate agent as a result.
- **When two reports from the same agent disagree, neither is evidence.** Go to the filesystem.
- Correct the record with exact SHAs and paths rather than a general "please re-check". Naming
  `dc4149c1d` and `15adf4b1e` ends the ambiguity; "your work may already be committed" does not.

**Counterpart, and the reason this is not just an agent failing:** the same cycle produced a case
where an agent's refusal to trust its own incomplete evidence was exactly right. It would not
delete an approved stale lock because it could not prove zero holders — `lsof` and `fuser` absent,
1,275 unreadable `/proc` descriptors. Overriding that would have been wrong. The Coordinator could
see the whole host and establish that no `git` process existed anywhere, which settles it because
only git creates an `index.lock` — an argument that does not depend on descriptor readability.
**Distinguish an agent reporting stale notes from an agent correctly refusing to over-claim. The
first needs correcting; the second needs evidence it cannot obtain from where it stands.**

Files: `docs/LEARNING_LOG.md`.

## 2026-08-29b — Kandev Support escalation route; broker capability discovery

Window: 2026-08-28T04:01Z (last cycle receipt on this branch) to 2026-08-29T07:00Z.
Shared `main` advanced from `78a21c6` to `6f42c9a` during the window and already
absorbed both peer Coordinator branches, so this cycle's gathering was mostly
verification rather than rescue.

Lessons captured:

- Environment blockers (missing tools/dependencies, permission failures,
  unavailable host capabilities, absent emulator/device support) escalate to the
  host `Kandev Support — Codex` agent, and are a distinct class from kandev
  product defects, which remain board tasks under PLATFORM BUG DUTY. A peer
  Coordinator landed the binding `PROMPT.md` rule and decision concurrently
  (`fd65560`, `fa743df`) while this cycle was editing; the two versions were
  synthesized rather than duplicated — main's leaner charter line and fuller
  required-fields decision were kept, and only this cycle's genuinely additional
  findings were grafted on. The README entry point remains this cycle's.
- Agents cannot deliver a support request themselves. Independently reproduced the
  documented `codex exec resume` failing with `no rollout found for thread id ...
  (code -32600)` from a second Coordinator worktree/session — CLI installed and
  authenticated, host thread state deliberately unmounted. Recorded as SETTLED so
  later cycles stop re-probing it.
- A guarded broker can under-report its own capabilities. `docker kandev --help`
  says `guarded Docker access supports 'docker compose' only` and never mentions
  `source`, yet `docker kandev source list` succeeds. `docker kandev source` with
  no arguments is the authoritative capability list; establish capability by
  running the documented operation. Reading top-level help alone would misread a
  working authorized path as missing, producing a needless escalation or a
  forbidden workaround.

Rejected by the filter:

- Re-documenting the support identity/thread ID and the delivery failure —
  already covered by `6f42c9a`; sharpened in place with the reproduction and a
  do-not-re-test instruction instead of adding a near-duplicate section.
- The 2026-08-28 "shared main is read-only" claim — already retracted on main by
  `8d85b0c` (mount namespaces are private). Not re-litigated here.
- Transient and excluded: container names/IDs/images and workspace inventory from
  `source list`, peer branch SHAs, live board status, and this Coordinator's
  session ID.

Cross-worktree note: this cycle began by fast-forwarding a peer branch and
cherry-picking a second one, because both carried committed learning that shared
`main` did not yet have. Both landed independently mid-cycle, so the duplicates
were dropped on rebase — no learning was discarded, and the originals remain on
`main` under their authors' commits (`67d9e9e`, `6fc33f7`, `66dbfd6`, `c1446b5`).

Files: `PROMPT.md`, `README.md`, `docs/RUNBOOK.md`, `docs/DECISIONS.md`, and this log.

## 2026-08-29c — Kandev Support broker is the canonical autonomous route (corrective)

Window: 2026-08-29T07:00Z to 2026-08-29T07:25Z. Human-directed acceptance test of
the autonomous Support contact channel.

Corrective lesson — this **supersedes** `2026-08-29b` and the peer policy landed in
`fd65560`/`fa743df`, which recorded that agent containers cannot reach Support and
must leave a paste-ready request in the board trail:

- A reviewed broker route exists and works: `docker kandev support send|status|
  receive`. Acceptance test confirmed the full transport — `send` returned a
  request ID and `queued`, `status` reached `complete` in ~10-15s, `receive`
  returned genuine host-side stdout/stderr. Coordinators contact Support
  themselves; the board-trail handoff is now only the fallback when the broker is
  unavailable.
- The earlier "cannot deliver" finding was sound about `codex exec resume`
  specifically (`no rollout found`, host state unmounted, still true and still
  not worth re-probing) but wrong to generalise into "no route exists". A "cannot"
  claim must name the exact route tested.
- Two failure modes must not be conflated: `no rollout found` = wrong route, use
  the broker; `thread-store conflict: already has an active writer` = right route,
  host-side contention needing operator release.
- Reinforces the 2026-08-29b capability-discovery lesson from a second angle:
  `docker kandev` with no arguments advertises only compose and omits `support`
  entirely, while `docker kandev support` lists it. A guarded broker's advertised
  surface is not evidence of what it can do.
- Operational trap worth recording: `send` resolves a relative path against the
  task root (`/data/tasks/<task-dir>/`), not the shell cwd, so a request file
  written in the `coordinator/` subdirectory needs an absolute path.

Not resolved this cycle: three spaced attempts all returned
`already has an active writer` on the support thread, so no Support reply was
received. Transport is healthy; the thread lock is operator-side and is being
escalated with request IDs and exact stderr.

Rejected as transient: request IDs, session and token values, timestamps, and the
`supports_parallel_tool_calls` host warning that accompanied but did not cause the
fault.

Files: `PROMPT.md`, `README.md`, `docs/RUNBOOK.md`, `docs/DECISIONS.md`, this log.

## 2026-08-29d — Support channel verified end to end; queued means backpressure

Window: 2026-08-29T07:25Z to 2026-08-29T07:45Z. Human-directed retest after
writer-conflict retry handling was deployed.

- The autonomous Support channel now works end to end. All five acceptance
  criteria passed: `send` exit 0; a busy thread left the request `queued` rather
  than failing fast; status reached `complete` with `returncode: 0`; `receive`
  exit 0 returned a genuine Support reply echoing the coordinator task ID and
  broker request ID; and unknown IDs, out-of-root paths, missing fields, and
  malformed JSON all still fail closed with exit 78.
- Durable operational rule: a long `queued` is the system working, not a stall.
  Contention serialises on one writer; the broker retries with capped backoff and
  reports `complete` only after Codex processes the request. Observed ~15.5 minutes
  queued before success. Poll ~30s, never resend into the same queue, keep working.
- A slow queue and a broken queue are indistinguishable at a single poll. They are
  told apart only by whether a terminal state arrives, so the honest interim report
  is "queued, still retrying" — never "complete", never "stalled".
- Corrective detail: requests that failed under the old fail-fast behaviour were
  NOT retroactively requeued, contrary to expectation. They stay
  `complete`/`returncode 1` permanently. Check once, then send fresh.
- Corrected a documented error string: an out-of-root path returns
  `path is unavailable: ... No such file or directory` (paths are mapped into the
  task root), not `path is outside this agent task`.
- Recorded that `receive` returns the full Codex transcript — header, rendered
  request, reply, token count — and that the broker composes the prompt and
  attaches task/workspace/request identity itself, so those fields must not be
  duplicated into the request JSON.

Rejected as transient: request IDs, host session ID, model name, token counts, and
exact timestamps beyond the one duration that makes the polling budget concrete.

Files: `docs/RUNBOOK.md`, `docs/DECISIONS.md`, this log. `PROMPT.md` unchanged —
the binding rule already routes Support through the broker; polling cadence is
operational detail, so no charter mirror is triggered.

## 2026-08-29e — Support channel independently confirmed; three-state queue

Window: 2026-08-29T07:45Z to 2026-08-29T07:47Z. Independent Coordinator-side
confirmation after Kandev Support moved delivery to a dedicated worker-owned Codex
thread.

- CONFIRMED WORKING with a fresh request. `send` exit 0, status went
  `queued` -> `processing` -> `complete` with `returncode: 0`, `receive` exit 0 and
  returned a genuine Support reply echoing the coordinator task ID, workspace scope,
  and the new request ID. Total round trip about 8 seconds.
- Corrective: `status` has a **third** state, `processing`, previously undocumented
  because every earlier observation was either an instant failure or a long
  contended wait. The documented `queued|complete` pair was simply incomplete —
  a reminder that a state machine observed only at its extremes will be
  mis-specified.
- Sharpened the latency guidance rather than replacing it. Both observations are
  real and neither generalises alone: ~8 seconds on a clear queue, ~15.5 minutes
  while earlier requests drain. Delivery is serialised, restart-safe, and
  oldest-first, so poll with adaptive backoff and never resend into the same
  ordered queue.
- The root cause of the original conflict is now named in the runbook: delivery
  contended with the operator's interactive support chat. Isolation onto a
  worker-owned thread is what fixed it, so a reappearance of
  `already has an active writer` means that isolation regressed — a report, not a
  retry loop.
- Corrective: the host-side `supports_parallel_tool_calls` cache warning appears on
  the stderr of SUCCESSFUL runs too. It is noise, never the fault. Diagnose from
  `returncode` and the assistant turn, not from the presence of an ERROR line.

Rejected as transient: request IDs, host session ID, model name, token counts, and
exact wall-clock timestamps beyond the two durations that make the polling budget
concrete.

Files: `docs/RUNBOOK.md`, this log. `PROMPT.md` unchanged — the binding rule already
routes Support through the broker — so no charter mirror is triggered.

## 2026-08-29f — capability/situation registry

Window: 2026-08-29T07:50Z to 2026-08-29T08:10Z. Support-directed implementation of
a canonical capability/situation registry.

- Created `docs/CAPABILITY_REGISTRY.md` (registry-version 2026-08-29a): 10 situation
  families — board monitoring and adaptive polling; task supervision, flags,
  blockers, workflow state, PR readiness and stale sessions; Coordinator
  filesystem/workspace scope; task Compose versus the Coordinator source broker;
  Android UI-QA/emulator; description/prompt synchronization; contacting autonomous
  Kandev Support; owner routing across Support/board task/Human; hard boundaries;
  and failure/status semantics. Every entry carries trigger, action, exact
  capability, authority, evidence, escalation destination, and prohibitions.
- Referenced prominently from the `PROMPT.md` per-turn bootstrap and listed in
  README components. Deliberately built as a router with links, not a copy of the
  runbook, because a duplicated procedure drifts and a stale copy consulted first is
  worse than none.
- Recorded a known gap honestly rather than omitting it: Android emulator/device
  UI-QA has NO verified Coordinator capability, so the entry says so and routes to
  Support. An absent entry reads as "no guidance"; a recorded gap reads as
  "verified absent".
- Added a binding maintenance rule in both the registry and `PROMPT.md`: a verified
  capability, limitation, workaround, or Support resolution updates the registry and
  every affected runbook/decision/learning record in the SAME change, and a
  contradiction between them is a defect to fix immediately.
- Validation: a link checker resolves every markdown target and heading anchor in
  the registry, plus the inbound references from `PROMPT.md` and README, against the
  real files and their computed slugs.

Rejected as transient: live board contents, task/session IDs, and current request
IDs. No secrets, tokens, or LAN URLs entered shared knowledge.

Files: `docs/CAPABILITY_REGISTRY.md` (new), `PROMPT.md`, `README.md`,
`docs/DECISIONS.md`, this log. `PROMPT.md` changed, so the live-description charter
mirror is due.

## 2026-08-29g — Android UI-QA is conditionally available, not absent (corrective)

Window: 2026-08-29T08:03Z to 2026-08-29T08:10Z. Reported the registry's Android gap
to Kandev Support through the broker; Support answered and the gap entry was wrong.

- **Corrective:** registry entry E1 claimed "no verified Coordinator capability
  exists" for Android UI-QA. Support confirmed it is **available conditionally —
  headless AVD only**, through guarded `emulator`/`adb` wrappers, a read-only host
  SDK and AVD catalogue, agent-local adb on port 5038, and disposable AVD metadata
  under `/data/home/.android`. Verified locally: both wrappers exist on `PATH` and
  `emulator -list-avds` returns a populated catalogue.
- Physical-device UI-QA is genuinely not provisioned; USB/ADB host passthrough is
  deliberately absent. That half of the entry was right.
- Real blocker identified: `/dev/kvm` is `crw-rw---- nobody:nogroup` and unreadable
  by the agent user, so an x86_64 AVD cannot accelerate. Support classifies this as
  a host/container mapping issue to repair, not a permanent limitation — so the
  correct record is "conditionally available, pending KVM authorization repair",
  never "unsupported".
- The capability is a constrained wrapper plus filesystem guard, **not** a
  workspace-scoped broker RPC. Do not assume broker validation semantics apply to
  every guarded capability; the two shapes differ and a broker-only Android design
  would need separate review.
- Method lesson: **absence of documentation is not absence of capability.** The gap
  was recorded honestly from an exhaustive knowledge-base search, and the search was
  accurate — yet the conclusion was wrong, because the capability existed and had
  simply never been written down. A verified-absent claim should be tested against
  the environment (does the binary exist? does the inventory command answer?) before
  it is published, not derived from documentation alone. This is the same shape as
  the earlier `codex exec resume` error: a "cannot" claim must name the exact route
  tested.
- The maintenance rule worked as intended on its first exercise: Support's answer
  updated the registry, runbook, and this log in one change.

Rejected as transient: AVD names, request IDs, and device serials.

Files: `docs/CAPABILITY_REGISTRY.md` (E1 rewritten, registry-version 2026-08-29b),
`docs/RUNBOOK.md` (new procedure), this log. `PROMPT.md` unchanged — no charter
mirror triggered.

## 2026-08-29h — Android UI-QA is VERIFIED BLOCKED; a capability claim must name what was executed

Window: 2026-08-29T08:10Z to 2026-08-29T08:20Z. Support reported the KVM blocker
cleared and Android UI-QA verified end to end; independent execution contradicted
it, and Support then retracted.

- **Final status: VERIFIED BLOCKED.** `/dev/kvm` is present as
  `crw-rw---- nobody:nogroup`, but that is unmapped host ownership inside the
  container user namespace, so apparent `nogroup` membership grants nothing:
  `os.access` False for R_OK/W_OK, `os.open(O_RDWR)` raises `EPERM`, and
  `emulator -avd <avd> -no-window` dies at
  `ProbeKVM: This user doesn't have permissions to use KVM (/dev/kvm)` with no
  surviving `qemu-system` process and an empty `adb devices`. Group/`KVM_GID` fixes
  cannot repair an unmapped device ID. Physical-device QA remains unsupported.
  Unblocking needs an owning infrastructure change (a reviewed workspace-scoped KVM
  broker, or a safe device-identity mapping) — neither exists, so do not retry each
  cycle and do not seek a privilege workaround.
- **The durable lesson, now a registry maintenance rule: a capability claim must
  name what was executed.** Three claims about the same capability were made in one
  day and the first two were wrong in opposite directions. A knowledge-base search
  concluded "no capability exists" — accurate search, wrong conclusion, because the
  capability was undocumented. A configuration inspection then concluded "verified
  end to end" — accurate inspection, wrong conclusion, because configuration is not
  execution. Only launching the emulator settled it.
- Adopted four honest statuses so the distinction cannot collapse again: VERIFIED
  WORKING (executed here, with evidence), VERIFIED BLOCKED (executed here, failed,
  with the exact error), UNVERIFIED (not executed in this context), NOT PROVISIONED
  (deliberately absent by design).
- **A verification performed in a different execution context does not transfer.**
  Support's check and the Coordinator task session were different contexts; the
  capability was present and configured in both and usable in neither. Always state
  which context was tested.
- Process note: a peer report — even an authoritative one carrying an explicit
  "verified end to end" — is evidence to check, not a fact to publish. Recording
  Support's claim as instructed would have put a false VERIFIED WORKING into shared
  knowledge that every Coordinator would then have trusted.

Rejected as transient: request IDs, AVD names, emulator build number, and image paths.

Files: `docs/CAPABILITY_REGISTRY.md` (E1 rewritten, maintenance rules 6-7 added,
registry-version 2026-08-29c), `docs/RUNBOOK.md`, this log. `PROMPT.md` unchanged.

## 2026-08-29i — Android headless AVD UI-QA is VERIFIED WORKING (corrective supersession)

Window: 2026-08-29T08:20Z to 2026-08-29T08:41Z. Kandev Support repaired two
independent launch-path defects, force-recreated Kandev, and requested acceptance
from the actual resumed Coordinator session. This entry supersedes the current
capability conclusion in 2026-08-29h; the method lessons in that entry remain valid.

- **Final status: VERIFIED WORKING for guarded headless AVD UI-QA.** The resumed
  Coordinator session opened `/dev/kvm` O_RDWR; `emulator -accel-check` exited 0
  with KVM version 12 usable; the guarded AVD boot produced `emulator-5554` and
  reached `sys.boot_completed=1`; adb reported API 29 and model
  `Android SDK built for x86`; screencap produced a valid 1080x1920 PNG; and a clean
  guest poweroff plus adb shutdown left no emulator, qemu, or adb process. The SDK
  and AVD catalogue stayed read-only, the protected Code parent stayed
  non-writable, and no `codex-linux-sandbox` process wrapped tool commands.
- **Physical USB/device QA remains NOT PROVISIONED.** Headless AVD success does not
  imply USB passthrough, a host adb server, display access, or permission to request
  them.
- **Root causes:** persisted session `runtime_config.mode` could override the
  enforced full-access profile and re-enable the provider inner sandbox; separately,
  the `agentctl` user transition dropped host KVM supplemental GID 993 because the
  image lacked a matching group entry. Support migrated and guarded the runtime mode
  fields, rebuilt the image to create/reuse the host KVM group and add `kandev`, and
  force-recreated Kandev. The prior failure came from a stale pre-recreate process.
- **Method correction:** execution remains authoritative, but the execution context
  includes process lifetime. A failure from a process that predates an image/group
  recreation cannot validate the recreated environment. After such a repair, test
  from a resumed/fresh consuming session and record both the process context and the
  actual device-open/boot result. Namespaced device owner text is cosmetic when an
  O_RDWR open and accelerated boot succeed.

Rejected as transient: the emulator serial, screenshot path/hash, wrapper process
IDs, and exact boot duration. The AVD/API/model appear only as reproducible
acceptance evidence, not as a permanent catalogue promise.

Files: `PROMPT.md` (binding E1 reference/status), `docs/CAPABILITY_REGISTRY.md`
(E1 rewritten, registry-version 2026-08-29d), `docs/RUNBOOK.md`,
`docs/DECISIONS.md` (superseded gap rationale), this log.

## 2026-08-29j — approved local image inspection is VERIFIED WORKING (corrective)

Window: 2026-08-29T08:41Z to 2026-08-29T09:01Z. A QA task that had preserved all
feature evidence but repeatedly hung in `view_image` was resumed after the Kandev
runtime recreation and ran one bounded consuming-session retry.

- **Final status: VERIFIED WORKING.** Desktop-web, responsive-web, and native
  Android PNGs all decoded immediately through the approved image-inspection
  capability. The QA agent inspected the actual rendered content, confirmed the
  disabled historical participant and stored answer with no task-related clipping,
  overlap, or error artifact, recorded a visual PASS, and advanced the workflow.
- **Corrective:** the earlier hang was valid evidence for the pre-recreate process,
  but not for the repaired runtime. Capability status must include process lifetime;
  after a known runtime recreation, one fresh bounded execution supersedes a stale
  process result.
- **Evidence classes remain strict:** image metadata and DOM/XML hierarchy are
  useful preflight evidence but never pixel acceptance. Responsive web is not
  native UI. A platform-tool hang is not a feature-code failure.
- **Routing:** a fresh bounded `view_image` hang is a Kandev product/tool defect and
  belongs in one platform board task with preserved artifacts. It does not route to
  host-environment Support, and it does not justify unbounded retries.

Rejected as transient: task/session IDs, artifact paths, image hashes, and exact
tool-call timestamps. The three image classes are retained only as reproducible
acceptance evidence.

Files: `docs/CAPABILITY_REGISTRY.md` (new K1, registry-version 2026-08-29e),
`docs/RUNBOOK.md`, `docs/DECISIONS.md`, this log. `PROMPT.md` unchanged because the
existing binding registry-maintenance rule already covers the capability.

## 2026-08-29n — independent post-recreate confirmation; two rules sharpened

Window: 2026-08-29T08:16Z to 2026-08-29T11:05Z (from the previous entry's knowledge
commit to now). Support reported the KVM blocker cleared after a force-recreate and
asked for an independent re-test.

- **Independent confirmation, not a new claim.** Executed the full path in this
  post-recreate session: `os.open('/dev/kvm', O_RDWR)` succeeded, `emulator
  -list-avds` returned 10 AVDs, `Pixel_3_API_29` booted as `emulator-5554` with
  `sys.boot_completed=1`, API 29 / Android 10 / `Android SDK built for x86` / x86
  ABI, and `adb emu kill` left no `qemu-system` process. A peer Coordinator had
  already landed the corrected VERIFIED WORKING entry with a fuller receipt
  (`061a2e4`), so this cycle deliberately did NOT rewrite E1 — a second description
  of the same finding is the near-duplicate the filter exists to prevent.
- **Sharpened in place (registry maintenance rule 7):** a verification does not
  transfer across execution contexts **or across process lifetimes**. The peer
  captured the incident narrative; the binding general rule still said only
  "different execution context". A long-lived agent process keeps the device/group
  policy it was created with, so after an image rebuild or force-recreate an earlier
  negative result is stale until re-executed in a fresh process. The identical test
  failed at 08:13Z and passed at 11:01Z with no change to `id` output.
- **Also folded into rule 7:** a cosmetic display is never a substitute for an
  executed check. `/dev/kvm` renders as `crw-rw---- nobody:nogroup` both when
  `open()` fails and when it succeeds, so the earlier "unmapped ownership" reading
  was inference from a display that carries no signal either way.
- **New (runbook):** a cleanup receipt must not be built on a self-matching pattern.
  `pgrep -c -f qemu-system` counts the invoking shell's own command line — it
  reported four stray emulator processes when there were none, twice. Confirm with
  `ps -eo pid,comm | grep -i qemu` or `pgrep -c -x`. This matters because cleanup
  receipts are exactly where a false reading goes unchallenged.

Rejected by the filter:
- Re-describing the Android capability, evidence, or the pre-recreate remediation —
  already landed by a peer this window; sharpened the one under-general rule instead.
- The KVM group/GID remediation detail — platform-side, already recorded by its owner.
- Transient: request IDs, AVD names, emulator/qemu build strings, device serials.

Files: `docs/CAPABILITY_REGISTRY.md` (rule 7, registry-version 2026-08-29f),
`docs/RUNBOOK.md`. `PROMPT.md` unchanged — no charter mirror triggered.

## 2026-08-29k — verify the instrument before acting on it

Addendum to `2026-08-29n`, same window.

- A link check flagged a peer's registry link as broken. The link was correct; the
  **checker** was wrong — it stripped underscores from heading anchors, so
  `#...-with-view_image` never matched. Correcting that then produced four fresh
  false positives, because the second version collapsed whitespace runs while the
  anchor format does not.
- Canonical anchor rule, now recorded in registry maintenance rule 5: lowercase;
  strip everything that is not a word character, whitespace, or ASCII hyphen
  (underscores survive, em-dashes and backticks do not); replace **each** whitespace
  character with one hyphen, without collapsing runs — so `IDLE — read` yields
  `idle--read`.
- The general lesson: **a validator is itself unverified until tested against a case
  whose answer you already know.** Acting on the first result would have "fixed" a
  working link into a broken one — the validator would have caused the defect it
  claimed to find. Before trusting any checker, run it against one known-good and one
  known-bad input.
- This is the same shape as the day's other corrections, now at one more remove:
  documentation absence was not capability absence, configuration was not execution,
  and here a tool's verdict was not the property it claimed to measure.

Files: `docs/CAPABILITY_REGISTRY.md` (maintenance rule 5, registry-version
2026-08-29g), this log.

## 2026-08-29l — delivery is not the same as sending; and three concrete traps

Long Coordinator session on the Kandev workspace board. Recording what other
coordinator worktrees cannot discover for themselves.

### The charter mirror has a broker command — stop hand-copying

`docker kandev workspace description-update "$PWD/PROMPT.md"` updates the live task
description from a file, byte-exactly, with a returned SHA-256. Full procedure now in
`docs/RUNBOOK.md`. I had deferred the mirror across three cycles because the only
route I knew was retyping 64 KB through `update_task_kandev`, and a silently drifted
charter is worse than a visibly stale one. The command existed the whole time; I found
it by asking Kandev Support. **When a duty looks disproportionately expensive, ask
whether the expensive route is the only one before deferring it again.**

### A send receipt proves queue persistence, not delivery

Kandev's `queued_messages` table held **100 undelivered rows**, including twelve
addressed to my own coordinator session and one queued 07:16:54Z that never surfaced.
Kandev Support's verdict: *"a stuck or unserviced delivery path — not normal
short-lived backlog behavior."* Operating rules that follow:

- `sent` and `queued` from `message_task_kandev` mean the message was persisted. They
  do **not** mean the agent received it.
- Do not assume a `WAITING_FOR_INPUT` session is proactively woken; treat delivery as
  needing an external turn trigger until the dispatcher is verified.
- **This reframes "stale agents".** Four agents in one session reported state their own
  repositories contradicted, asked approval for work already committed, and requested
  actions already completed. I initially recorded that as agent carelessness. It is
  not: a platform that delivers instructions late will systematically produce agents
  that act, then report remembered state, then receive answers to questions they have
  already resolved. Verify against the repository, and do not attribute to the agent
  what the transport caused.

### Three traps worth knowing before you hit them

**1. `pgrep` substring matching against a Coordinator's own argv.** A validated
Coordinator's `bwrap` command line lists *every* task path in its workspace — 110 of
them here. So `pgrep -a bwrap | grep <task-dir>` matches the Coordinator itself and
reports a live agent in a worktree that has none. I hit this twice, once concluding I
had killed processes that were never signalled. Enumerate `--chdir` instead:
`for p in $(pgrep bwrap); do tr '\0' ' ' </proc/$p/cmdline | grep -o '\-\-chdir [^ ]*'; done`.
This is the same family as the `pgrep -c -f qemu-system` self-count in `2026-08-29j`.

**2. One comparison worktree is not evidence that untracked files are unique.** Auditing
a Done card, five untracked files appeared in its worktree and not in the one other
worktree I checked — which reads exactly like unpushed deliverable work, and nearly
made me recover a correctly-completed card. Widening the check: the same paths exist in
**43 worktrees**, share an identical bulk mtime, and are tracked in repository history.
They are materialization artifacts. Test across many worktrees, compare mtimes, and run
`git log --all -- <path>` before calling untracked content unique.

**3. Distinguishing a shared CI failure from a branch-owned one takes one query.** When a
check fails on a pull request, look at whether the *same named check* is failing on
other open pull requests from unrelated branches. Red on several → shared class, route
it to one owner. Red on one and green on another → branch-owned, hand it back. Applied
twice in one session: seven `parent directory cannot be accessed` failures turned out
shared across three tasks, while a `Run Backend Tests` failure was branch-owned because
the same check passed elsewhere.

### Worktree admin-directory collisions exist in the wild, and the obvious repair destroys work

Two independent cases where a task's `.git` marker resolved to a `worktrees/<id>` entry
whose `gitdir` backlink named **a different task's checkout**. Rewriting that backlink
to match the marker — the one-line fix it looks like — hands the administrative
directory, index and HEAD to the wrong task. In these two cases the rightful owners held
28 and 8 unpublished commits.

- Refuse when a marker resolves to an admin directory whose backlink names a different
  checkout. Report expected and actual, and resolve only by **allocating a new entry**,
  never by reassigning an existing one.
- The owning task is discoverable, but not from the filesystem:
  `task_environment_repos.worktree_path` maps a checkout to its task, `worktree_branch`
  and status. Use it to name the owner in the refusal rather than guessing.
- Related: a checkout can lose its branch refs **locally and on the remote**, with no
  dangling objects and no reflog. Then no faithful `HEAD` exists and reconstruction is
  impossible; content-only preservation is the honest outcome. Verify remote absence
  with a control branch that *does* resolve — a bare 404 can also mean a permissions
  problem.

### The pattern under all of it

Twelve corrections to my own conclusions in one session, every one traceable to
prescribing or concluding before inspecting: a `git merge` prescribed into a tree that
was already mid-merge with 5,404 staged files; a push approved onto a branch whose
histories had diverged, where the natural next step is a force-push over 286 commits; a
`read-tree` recommended against a branch with no commit behind it. **In three cases an
agent's refusal to follow my instruction is what prevented the harm.** An agent that
declines and reports the exact refusal is doing its job — treat that as signal, not
friction, and check your own instruction first.

Files: `docs/RUNBOOK.md`, `docs/LEARNING_LOG.md`.

## 2026-08-29m — Support delivery success is distinct from blocker resolution

Window: 2026-08-29T11:05Z to 2026-08-29T11:09Z.

- Two broker requests reached the autonomous Support worker and returned genuine
  terminal `KANDEV_SUPPORT_STATUS: BLOCKED` responses. This is a third broker
  outcome distinct from queue backpressure and resolved work: transport succeeded,
  but the requested environment repair exceeded the reviewed capability surface.
- Durable boundary: without an audited operation, Support must not repair
  persistent canonical workspace-repository inventory through direct backend
  edits. Without a reviewed task-scoped credential broker, it must not provision,
  reuse, expose, or mount host GitLab credentials.
- Coordinator action is therefore deterministic: preserve and physically park the
  affected task, record the exact missing capability and smallest operator action,
  and resume only on a non-secret acceptance receipt. Re-sending the unchanged
  request cannot create authority and only adds queue noise.
- This corrects a tempting but false inference that end-to-end broker delivery
  means every host/environment blocker is automatically actionable by Support.

Rejected as transient: task/session/request IDs, repository rows, MR numbers,
commit hashes, provider timestamps, and specific command timeouts.

Files: `docs/CAPABILITY_REGISTRY.md` (new G3, registry-version 2026-08-29h),
`docs/RUNBOOK.md`, this log. `PROMPT.md` unchanged because its existing binding
rule already requires autonomous broker routing and escalation of genuine terminal
faults.
## 2026-08-29p — the shared standup file collides across workspaces

Window: 2026-08-29T11:05Z to 2026-08-29T11:15Z, during a `WAKE:STANDUP` on the
Co-Up board.

- **New, corrective:** `standups/standup-YYYY-MM-DD.md` carries no workspace
  qualifier, while Coordinators are workspace-scoped peers each running their own
  standup routine into the same shared clone. Today's file already existed and
  described an entirely different board (52 cards, PRs #3048/#3136/#3143) — a peer's
  report, not a re-run of mine. Following the routine literally ("update today's
  file") would have destroyed it, and the five-file rotation could then have deleted
  the evidence.
- The existing rule anticipated only *same-workspace* duplicates and explicitly
  declared cross-workspace Coordinators independent peers — which is true for wake
  ownership and false for this one filename. The gap was in the seam between two
  correct rules, not inside either.
- Resolution: the dated file now carries one `## Workspace: <name> (<id>)` section
  per workspace, appended never overwritten, with a header explaining why. Bound in
  `PROMPT.md` and given a runbook procedure.
- **Capability recorded:** `docker kandev workspace description-update <file>` exists
  (verified via `docker kandev workspace`). This closes a gap I had been carrying for
  three cycles — the `PROMPT.md` charter mirror was deferred because sending a 60 KB+
  document inline risked a truncated description, which is worse than a stale one.
  Registry entry F1 now names it. Another instance of the day's recurring lesson:
  the capability existed and was simply undiscovered, and `docker kandev` with no
  arguments does not list `workspace` either.

Rejected as transient: board counts, the specific stalled task IDs, and the
session-start incident (escalated to Support, not yet a durable rule — if the ACP
start path proves to have a recurring failure mode it earns a playbook then).

Files: `PROMPT.md`, `docs/RUNBOOK.md`, `docs/CAPABILITY_REGISTRY.md`
(registry-version 2026-08-29h), this log.

## 2026-08-29q — a lane change is an agent's decision; I read half a schema and called it drift

I spent a cycle "fixing" a card that was never broken, and the agent working it had to
tell me so. Three separate errors, each one a layer under the last.

### What I claimed, and why it was wrong

`workflow_steps.events` carries `on_turn_complete` on six of the twelve lanes — Spec,
Work, Review, QA, PR, CI Fixup. I read that, saw those same six also carry
`on_enter: auto_start_agent`, and concluded the board walks cards forward unattended:
enter a lane, an agent starts, it finishes a turn, the card advances, repeat. I wrote
that up as a mechanism and acted on it.

**It is false.** The column immediately beside `events` is
`auto_advance_requires_signal`, and it is `1` on all six of those lanes. Advancement
fires **only when the agent explicitly signals step completion**. Nothing drifts. Every
lane change on this board is a decision somebody made.

So the "drift" I was chasing was the agent doing its job: `@codex-dw-pr` STEP 7 ends the
PR phase by routing to CI Fixup, and states outright *"Do not monitor CI here. CI
monitoring belongs to [CI FIXUP PHASE]."* Pending checks belong to CI Fixup **by
design**. I had inferred the opposite from the lane's name — that CI Fixup means a red
pipeline with a job to repair — and told the agent its correct routing was wrong, twice,
then queued a move parking it in Blocked, outside the lane that was supposed to be
watching its CI.

The agent pushed back with its phase contract quoted. It was right on every point.

### The three failures, named

1. **I read one column and stopped.** `events` without `auto_advance_requires_signal` is
   half a schema, and the missing half inverted the meaning. Same shape as recording
   `pending_moves.applied` — a column I never checked existed.
2. **I inferred lane semantics from lane names.** The authority is
   `workflow_steps.prompt`, which names the phase contract the agent is actually
   executing. It is one query. I never ran it until after being corrected.
3. **I attributed a system behaviour to an agent, then attributed an agent's decision to
   a system.** Both directions, same cycle, and I wrote a shared learning entry
   confidently asserting the second one.

### What is actually true and worth keeping

- **Read the phase prompt before judging a card's lane.**
  `SELECT prompt FROM workflow_steps WHERE id='<step-uuid>';` The lane name is a label;
  the prompt is the contract. Where they disagree, the prompt wins.
- **A card in a lane you did not expect is a decision, not a malfunction.** Ask the agent
  what phase it is executing before moving it. It has the contract; you are guessing.
- **The stable/advancing split still exists** — Backlogs, Todo, Blocked, Human-QA,
  ToDeploy and Done have no `on_turn_complete` at all — but on this board it never fires
  unattended, so it is not a hazard to route around.

### `move_task_kandev` returning 200 means *queued*, not *moved* (this part held up)

A move requested while the target's session is mid-turn is deferred to the turn
boundary. The call returns success and the returned task JSON echoes the **requested**
`workflow_step_id`, so the response looks like proof of a move that has not happened.
The real state:

- `tasks.workflow_step_id` is unchanged, and `updated_at` does not advance
- a row appears in `pending_moves` carrying the requested `workflow_step_id`

The row's **presence is the signal** — there is no `applied` flag, and the row is
removed once the move lands. `pending_moves.session_id` is `UNIQUE`, one pending move
per session, so a second request **supersedes** the first in place rather than stacking.
That property is what let me cancel the bad Blocked move: I issued a move to the lane
the card was already in, and the queued row retargeted itself, same row id.

Watch the column order when reading the raw row — `step_position` sits where an
`applied` flag would plausibly go, and I misread its `0` as exactly that before checking
`.schema`. Read the schema before naming a column you have only seen positionally.

### The pattern

Every correction I have logged today reduces to concluding before inspecting. This one
adds a sharper version: **when a conclusion makes an agent look wrong, that is the moment
to go back and check the schema, not the moment to send the instruction.** The agent's
refusal is what stopped this from becoming a card parked in the wrong lane with its CI
unwatched — the fourth time in this session that an agent declining my instruction
prevented the harm.

Files: `docs/RUNBOOK.md`, `docs/LEARNING_LOG.md`.

## 2026-08-29r — a queued move has no expiry, and messaging a task can fire one from nine days ago

Found while auditing `pending_moves` board-wide rather than for a single card — which I
had not done before, having only ever looked up the row for the task in front of me.

Seven rows existed. **Every one targeted a lane different from where its card actually
sat**, and the oldest had been queued nine days earlier. These are not residue; a queued
move waits indefinitely for its keyed session to reach a turn boundary.

| card | lane | queued target | keyed session | verdict |
|---|---|---|---|---|
| `7dac85e2` | **Done** | Blocked | `e4f06dea` `WAITING_FOR_INPUT` | **live** |
| `9e67c426` | Blocked | CI Fixup | `d3720d53` `WAITING_FOR_INPUT` | **live** |
| `9e67c426` | Blocked | Work | `3e60d669` `WAITING_FOR_INPUT` | **live** |
| `52892e8e` | Blocked | Human-QA | `dd25091c` — absent from the task's sessions | orphaned, inert |

### Why this matters more than it first looks

`WAITING_FOR_INPUT` is not dormant in the sense that matters. **Sending a message resumes
the session, and the resumed turn fires the queued move.** So an ordinary Coordinator
action — nudging a silent task, asking a question, issuing a handoff — silently relocates
the card, executing an instruction some other Coordinator queued days earlier. It will not
appear in your cycle log as a move you made, because you did not make it.

`7dac85e2` is the sharp case: a task I audited and deliberately left in Done, one message
away from leaving Done for Blocked. The DONE TERMINAL-INTEGRITY gate can be broken with no
agent at fault and no Coordinator intending it.

### What generalises

- **`session_id` is `UNIQUE`, not `task_id`.** A task accumulates one armed row per
  session that ever queued a move — `9e67c426` carries two, pointing at different lanes.
  Looking up "the" pending row for a task is the wrong mental model.
- **The row's keyed session decides whether it is a hazard.** Present and
  `WAITING_FOR_INPUT` → live. Absent from the task's session list → orphaned and inert.
  Both look identical in `pending_moves` alone; the classification only exists once you
  cross-reference `list_task_sessions_kandev`.
- **I did not act on it.** The supersession trick is verified for clearing a row on a card
  whose session is active, but whether issuing that move *first resumes* a dormant session
  and fires the old row is untested. On a verified-Done card that is not an experiment
  worth running blind — record and escalate instead. Given how much of today came from
  acting on an unverified mechanism, the restraint is the point.

Related: [[the board advances only on an explicit signal]] — that correction and this
finding are the same lesson from opposite sides. There I invented a system behaviour that
did not exist and blamed an agent for it; here a real system behaviour exists that would
have been blamed on nobody at all.

Files: `docs/RUNBOOK.md`, `docs/LEARNING_LOG.md`.

## 2026-08-29s — a task's PR can vanish from the board while staying open on the provider

`63b40206` sat in Human-QA with `task_repositories.metadata` = `{}`, where sibling cards
carry a full `comparison_target` naming PR number, head branch and target repo. I read
that as "either no PR was opened, or one exists and was never linked."

The task agent had the evidence that separates those: it had read a task relationship
record on 2026-08-28 showing **PR #6 already linked**. So the linkage existed and was
lost. That is a board regression, not an omission by the agent — and I could not have
distinguished the two from my side, because the current state looks identical either way.

**The lesson is about who holds which evidence.** Present board state cannot tell you
whether a field was never populated or was populated and reverted. The agent's own
history can. When a record looks merely incomplete, ask the owner whether it was ever
complete before concluding it was never done.

Consequences worth knowing:

- **A missing linkage makes a task's CI invisible to the Coordinator.** I had to resolve
  the branch to a provider repo by hand to discover #6 was open, Draft, head-matching and
  green. Anyone auditing the card saw a Human-QA task with no pull request attached.
- **Check the provider before recording "no PR exists."** `gh pr list --repo <owner/repo>
  --head <branch> --state all` answers it directly and cheaply.

### The same cycle, a sharper general point: green CI is not a clean review

With the rate limit cleared I could finally read review state across the board. **Every
PR had green CI. Not one was review-ready.** #3143 carried three unresolved automated
threads, #3137 two, #3136 one — while `63b40206`'s #6 had zero threads, zero comments,
and a 1,964-character body already ordering the reader through the diff.

So the two signals diverged on every card, in both directions: three cards looked ready
and were not; one looked unverified and was in better shape than any of them. Reading
only the check roll-up would have got all four wrong. **Fetch `reviewThreads` and the
body, not just `pr checks`, before calling anything ready** — this is the same failure as
[[calling a PR review-ready when its remote trailed]], one layer up.

Files: `docs/RUNBOOK.md`, `docs/LEARNING_LOG.md`.

## 2026-08-29t — DEFERRED FINDINGS REGISTER: two P1s with no board task to hold them

Recorded because they were **deliberately deferred, not dismissed**, and there is currently
no card to receive them. Deferred findings with nowhere to live are how real defects get
lost. If a Coordinator later gains permission to create board tasks, these are the scope.

**Source:** PR kdlbs/kandev#3143 (`Fix workflow-sync GitHub polling starving API quota`),
head `731ddc021c7be75a2798baaba08de5cd5305e759`, 2026-08-29. Both were confirmed real by
the task agent against the code, replied to on their threads with the risk stated, and
resolved as deferred follow-ups. Two contained fixes from the same review round **were**
landed on that PR: exempting `/rate_limit` probes from `ObserveSuccess`, and clamping the
oversized initial retry delay.

### [P1] Legacy admission state splits across two principals for one identity

`apps/backend/internal/github/service.go:297` — raised by `greptile-apps`.

`NewService` wires the service-level legacy client **before identity is known**, keying it
under the empty-login `workspace:legacy` fallback, while workspace-resolved legacy clients
coordinate by authenticated login. The same upstream credential therefore holds **two
independent admission slots**, so concurrent background requests bypass the serialization
and pacing the subsystem exists to impose.

**Cost of deferring:** principal-wide serialization is lost for the startup/global client
path. **Why it is not a patch:** a safe fix needs identity acquisition and rebinding
semantics — what happens to in-flight admissions when a client's identity resolves.

### [P1] Synchronous poller lets one throttled principal stall every other

`apps/backend/internal/workflowsync/service.go:248` — raised by `chatgpt-codex-connector`.

`SyncDueConfigs` calls `syncWorkspace` **serially**, and admission can wait **while holding
the workspace lock**. So when any due workspace shares a principal with an active retry
window or exhausted reserve, the first blocked workspace prevents every later one —
including unrelated GitHub **and GitLab** principals — from syncing for up to an hour.

**Cost of deferring:** no isolation between principals during a long throttle window.
**Why it is not a patch:** needs a nonblocking scheduled-admission contract or properly
owned per-workspace scheduling. A timeout or a goroutine around the blocking call is the
tempting shortcut and is not a fix.

### The rule this is here to enforce

**A deferral is only honest if the cost of deferring is written down somewhere that
outlives the pull request.** The agent stated both costs in its review replies, which is
correct — but review threads on a merged PR are not a register anyone consults. Escalating
"I need permission to create a task" without recording the content would have made the
finding contingent on that permission arriving. It is not contingent now.

Related: [[no silent caps]] — a bounded scope must be logged, not implied.

Files: `docs/LEARNING_LOG.md`.

## 2026-08-29u — nobody in the loop can re-run CI, so "flake or real defect?" is unanswerable

A PR reached a state where every question was resolved except one, and that one could not
be settled by anyone available.

**The situation.** #3143 failed `E2E Shard 13/14` after a previous run failed
`E2E Shard 9/14`. The agent had already proven the 9/14 failure was a **real** strict-mode
assertion defect — an unscoped locator matching two elements — and fixed it, so "assume
flake" was not open to us. For 13/14 it traced the root to `pr-status-badge.spec.ts:555`
and ran the exact test **10/10 clean** with `--repeat-each=10 --retries=0`.

**The decisive test is a re-run of the same job on the same commit.** Passes → flake.
Fails identically → deterministic, and the environment/artifact hypothesis takes over.

**Neither party can run it.**

- Task agents get **HTTP 401** from `gh` without the injected token (D18).
- The Coordinator gets `run <id> cannot be rerun; Must have admin rights to Repository`.

I offered the re-run before checking my own permissions, and an agent waited on a
capability I did not have. **Check that you can do a thing before offering it as the way
out of someone else's blocker.**

### What survives when the decisive test is unavailable

Substitute evidence is worth gathering, and worth labelling as substitute:

- **Sibling suites.** #3136 and #3137 ran the same E2E suite on the same repository with
  **zero** shard failures, while #3143 failed two different shards in consecutive runs. A
  general suite flake predicts the siblings would flake too.
- **Its limits, stated rather than buried.** Different times, different runner load — not
  a controlled comparison. And two *different* shards failing fits a single
  branch-specific defect badly, since that would hit the same spec twice. Neither
  hypothesis comes out clean.

The agent's final classification was the right shape: **"unresolved CI-only, likely
environment/load-dependent"**, explicitly noting it *cannot* prove a flake. That is a
finding. "Flaky" would have been a guess wearing a finding's clothes.

### The rule

**A local pass after `make build` does not separate "flaky" from "CI artifacts differ".**
Rebuilding before the local run confounds exactly the comparison you are making. Say so
when reporting it.

**And "retries reproduced the same failure" is evidence of determinism, not flakiness** —
if CI fails the same way every attempt, that is the opposite of jitter. Watch for a report
that contains both that sentence and a flakiness conclusion; they are in tension.

### The consequence for the board

The readiness gate requires green CI, so the PR cannot flip — **blocked on a capability
gap, not on the work**. Nine threads closed, three P1s fixed, `mergeable: true`, and it
sits behind one CI signal nobody present can interrogate. That distinction belongs in what
the Human reads, so the card is not mistaken for an agent that stalled.

Related: [[flipping draft to ready is itself a review trigger]].

## 2026-08-30b — draft-to-ready can create a new check gate

PR #3143 was fully green while draft. Immediately after the mechanical ready
transition, GitHub created a new `pull_request` review check on the unchanged head.
The Coordinator posted the maintainer notification before refreshing that
post-transition check set; the new job finished green shortly afterward, but the
ordering was still wrong.

The durable rule is: treat draft-to-ready as a provider state change that can create
new required work. Observe `isDraft=false`, refresh exact-head checks, threads, and
mergeability, wait for every newly triggered required job to become terminal green,
and only then notify the reviewer. A green draft-era census cannot prove the
post-ready PR is ready.

Files: `docs/LEARNING_LOG.md`.

## 2026-08-30c — parallel queue triage must begin before pressure

The first successful queue split used two read-only helpers only after the
Coordinator had reached 15/15 messages. The mechanism worked, but the timing was
reactive. The operator corrected it: on every turn, census the current session
queue and fill all safely available helper capacity whenever two or more independent
items exist.

Efficiency without conflicts comes from the assignment boundary: one immutable
snapshot, disjoint full task UUID/dependency families, read-only helpers, and one
primary that deduplicates evidence and serializes every task/provider/repository/
queue/plan mutation after a fresh live-state and `pending_moves` check. A new
arrival is not injected into a running slice. Capacity is not the delegation
trigger; it is the failure mode proactive triage prevents.

Files: `PROMPT.md`, `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`,
`docs/DECISIONS.md`, this log.

## 2026-08-31a — task-readable recovery files are not necessarily durable

A failed-session queue recovery produced valid mode-0600 pages under a task-owned
mode-0700 directory, but task-runtime cleanup removed the complete artifact before FIFO
reconciliation. Ownership, readability, and matching hashes proved the bytes at one
instant; they did not prove the storage lifetime covered the handoff.

The replacement recovery retained one Support-managed backing outside task-runtime
cleanup and exposed a byte-identical task mirror. The Coordinator verified all ten page
hashes, the manifest, the canonical 14-entry digest, and processed every entry FIFO while
leaving the source queue untouched. Future large recovery reads require that retained
boundary whenever task cleanup can race consumption; cleanup of the retained copy is a
separate exact authorization after dispositions are durable.

Files: `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`, `docs/DECISIONS.md`, this log.

## 2026-08-29v — proactive Support delivery plus guarded-session acceptance

Two environment acceptance requests produced an important split in evidence ownership.
The broker delivered both results automatically to the Coordinator without polling or a
Human relay, so transport and routing were proven. Support nevertheless returned
`BLOCKED`: it could inspect the deployment policy but had no reviewed operation for
executing inside the named guarded task session.

That did **not** mean the capabilities were blocked. Running the supplied checks in the
actual session proved both:

- guarded Android/KVM wrappers booted a listed headless AVD to
  `sys.boot_completed=1`, returned API/model data, captured a valid screenshot, and
  shut down without residual emulator/qemu/adb processes; physical USB remains
  intentionally unprovisioned;
- task-owned `docker compose` started and executed a disposable service, while direct
  unrelated `docker inspect`, `docker exec`, and `docker stop` each failed closed
  with exit 78 before daemon access.

Durable lesson: a Support-side runner gap and an unavailable task capability are
different claims. A proactive `BLOCKED` response proves delivery but must be interpreted
at the exact boundary it names. When Support supplies safe in-scope acceptance commands,
execute them in the owning guarded session, preserve the boundary, and send one fresh
evidence-bearing follow-up only if the delivered result remains incomplete.

The evidence-bearing follow-up later arrived proactively as `RESOLVED`, accepted both
guarded-session receipts, and required no platform change. That final message closes the
loop: once Support's closure agrees with the independently captured evidence, persist the
receipt and stop—an acknowledgement-only Support request would be a duplicate.

Files: `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`, this log.

## 2026-08-30a — a pruned worktree does not imply a disposable branch

The Coordinator repository accumulated 431 local branches matching its exact
`main-[0-9a-z][0-9a-z][0-9a-z]` worktree naming rule. Comparing that set with
`git worktree list --porcelain` found 168 refs with no live worktree; all 168
were ancestors of `main`. After a fresh per-ref worktree and ancestry check,
non-force deletion removed exactly those 168 and left 263/263 live branches,
zero missing live refs, and unchanged base, remote, feature, and backup refs.

The recurrence is not Git corruption or local deployment customization. On
canonical `kdlbs/kandev` upstream/main `4d8763e4de852701f22345c7ac115ffdfac30664`,
several terminal/handoff/automation paths intentionally call worktree removal
with `removeBranch=false`. That protects local-only unpublished commits, but Git
worktree removal then leaves the branch indefinitely. The platform comment that
operators use branch-cleanup tooling does not itself bound the accumulation.

The safe lesson is two-sided: absent from `git worktree list` is necessary but
not sufficient for deletion, while retaining every absent ref forever is not a
cleanup policy. A bounded repository-local cleanup needs an exact name allow
list, live-worktree set subtraction, containment in a verified base, explicit
non-force deletion, and post-delete ref/worktree invariants. A generic platform
fix must additionally preserve archive/unarchive recovery: current recreation
treats a branch missing locally and remotely as unrecoverable even if its commits
remain reachable through the base. That upstream design is tracked by task
`37eca47b-cf05-47ee-b143-39408edbeed1`.

Files: `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`, this log.

## 2026-08-30d — a command labelled TTY is not TTY evidence

Support repaired real Codex ACP command-result delivery with deployment-only
`yattdev/kandev-service` `main` commit `6fcc88f689dae9797dd131229167a98d0e955d43`
(not a public `kdlbs/kandev` source commit): the guard now preserves existing
`CODEX_CONFIG` while setting `features.unified_exec=false` only for
`@agentclientprotocol/codex-acp`. Fresh agent session
`c1ef931d-c98b-4af8-bd24-87352cf4da05` independently proved the important half:
non-TTY output and completion arrived immediately with empty stderr and exit 0 from
the exact protected worktree/head.

The same receipt called a second command “TTY”, but durable metadata stored both calls
as the same normalized `shell_exec` kind. The command did not run `test -t` or `stty`,
and no retained tool input showed a TTY/PTY selection. The label described intent, not
transport. Exact TTY acceptance therefore stayed open instead of being inferred from
ordinary output.

The reusable test is three-part: retain evidence that the agent tool itself requested
a TTY, assert `test -t 0` and `test -t 1`, and run `stty` before the functional command.
Do not accept an inner `script`, `ssh -t`, or similar self-allocated PTY because that
bypasses the layer under test. One evidence-bearing Support follow-up owns the check;
the task and its preserved work remain parked meanwhile.

Files: `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`, `docs/DECISIONS.md`, this log.

## 2026-08-30l — direct-to-Work creation must publish the plan before launch

Two replacement repair tasks were created directly in Work with detailed
implementation briefs, but their first sessions correctly reported that no saved
approved plan existed. The Coordinator then had to persist plans and resume them;
earlier zero-work launch attempts in the same failure family had already become
terminal duplicates.

The reusable invariant is ordering, not briefing length. For a direct Work task,
create without starting the agent, save and read back the approved plan, then launch
and verify the Work session. If that ordering is unavailable, start the task in Spec.
Never use `start_agent=true` for direct Work and rely on a later plan backfill: the
first Work turn is entitled to refuse before the plan write wins the race.

Files: `PROMPT.md`, `docs/RUNBOOK.md`, `docs/DECISIONS.md`, this log.

## 2026-08-30j — delayed task reports are receipts, not live state

Several task messages accurately described the session census at the time they were
written but arrived after the Coordinator had already started a newer exact-head gate
session. Acting on the delayed claim would have launched duplicate Review/QA work or
misreported the board as stalled.

The reusable correction is to bind every inbound report to its creation time, lane,
canonical PR/MR head, and session IDs, then compare those claims with live task,
provider, and complete-session readback before acting. A newer live receipt supersedes
the delayed report without invalidating its historical value. Conversation arrival
order alone is not a source of truth.

Files: `PROMPT.md`, `docs/RUNBOOK.md`, `docs/DECISIONS.md`, this log.

## 2026-08-30k — screenshot evidence must render inline on the review surface

A board-wide visual-evidence audit found UI-visible PRs whose captures existed locally
or were linked as ordinary Markdown URLs but did not render as screenshots where the
reviewer inspects the change. The Human explicitly required screenshots on PRs whenever
UI changes are present.

The durable gate now requires still images to render inline in the PR/MR body from a
stable reviewer-accessible URL, with descriptive labeling and a final image-content
check. This does not authorize an evidence-only code commit: when approved provider
publication is unavailable, preserve the sanitized local capture and keep the PR draft
until it can be attached correctly.

Files: `docs/RUNBOOK.md`, `docs/DECISIONS.md`, this log.

## 2026-08-30i — a reviewed root helper still needs an explicit first-install handoff

Capability-repair request `35011026-3fb4-4daa-bb2b-12a1facc2d5b` did not merely restate
the missing authority. It produced deployment commit
`5f4fabf1618b0316b7aec2bbea63e76d48bb227f`: a fail-closed host helper, audited installer,
and three predicate tests. Support correctly stopped at the remaining boundary because
the first install writes root-owned executable, configuration, audit, and sudoers state.

The reusable sequence is now precise: verify the commit and installer locally; rerun its
non-root syntax and predicate tests; re-read every authorized process/group and excluded
agent; confirm lane, sessions, pending rows, clean head, and artifacts; then make one
operator ask with the exact install command. Installation is not cleanup and does not
prove resolution. Once installed, send one fresh predicate-complete Support request and
independently verify the structured before/after receipt. Do not expose the helper as raw
agent authority, repeatedly ask Support to install it, or silently treat a committed
artifact as deployed capability.

Evidence: task `04802c8a-aad9-4d18-bdca-fa593c2e0b9a`, merged PR
`https://github.com/kdlbs/kandev/pull/3151`, and the deployment commit above.

Files: `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`, `docs/DECISIONS.md`, this log.

## 2026-08-30g — an orphan process is a resource leak, not evidence to reopen Done

Two ACP/Bubblewrap trees remained alive after their terminal task worktrees had already
been safely removed. Both tasks had zero active sessions and no lifecycle-tracked
execution, so waking them would not have supplied a legitimate stop target and could
have fired unrelated queued task state.

Support request `9f8dd8b8-2969-4499-9d02-eb9c63aff5cf` proved the narrow fallback:
bind every PID and process group to the exact deleted task-worktree CWD, attempt the
supported lifecycle stop first, then use bounded group-scoped `SIGTERM` only when no
tracked execution exists. Root-only termination was ignored; the four exact isolated
groups exited after `SIGTERM`, with no `SIGKILL` and no unrelated mutation.

The reusable acceptance gate includes more than process absence: task sessions remain
non-active, worktrees/registrations and intended local branches retain their prior
disposition, and accepted/merge commit objects remain durable. A terminal orphan is a
resource-disposition defect, not proof of lost work or a reason to recover the card out
of Done.

Files: `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`, `docs/DECISIONS.md`, this log.

## 2026-08-30h — stronger process signals need atomic host-side ownership proof

Five residual backend/Vite service groups survived repeated exact `SIGTERM` attempts
after QA, while the enclosing guarded agent and Human-QA card correctly remained live.
The guarded worker could enumerate stable PID, parent, PGID, SID, and membership data,
but could not read the host CWD links; reviewed Support also lacked non-interactive host
authority. Two escalated requests correctly sent no `SIGKILL`.

The reusable correction is that visible process topology is necessary but insufficient
for a stronger destructive signal. Task-root CWD ownership, complete group membership,
and excluded-agent identity must be revalidated atomically by the same least-privilege
host operation that signals the exact groups, and every mismatch must fail closed.

An unchanged kill request is not the next escalation. Send one distinct capability-repair
request for that audited host primitive and await its proactive result without polling.
If the capability itself is terminally blocked, preserve the processes and make one
operator/Human escalation with exact predicates; never expose transferable host authority
or broaden the target. The task lane, sessions, repository, and QA artifacts remain
independent invariants throughout this cleanup.

Evidence: Support requests `c6997ee9-0130-4567-9e79-6988c157cd05` and
`fd3c8c3f-cf63-4d59-a1d8-b63b24a07644`; capability-repair request
`35011026-3fb4-4daa-bb2b-12a1facc2d5b`; task
`04802c8a-aad9-4d18-bdca-fa593c2e0b9a`.

Files: `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`, `docs/DECISIONS.md`, this log.

## 2026-08-30e — exact cancellation cannot be built from preflight plus consume

Support request `4571adf2-7d99-461b-835c-3a172cab8ef2` audited the only supplied service
primitive for a fresh armed `pending_moves` row: `TakePendingMove(sessionID)`. It cannot
accept or atomically verify the inspected row ID, task, move, current lane, and queued
target. Reading those first does not help; another writer can replace the session-unique
row between the read and consume, and the consumer then deletes the replacement.

The lesson is broader than this table: a race-sensitive destructive operation is not
made fail-closed by adding a careful preflight. Every identity and state predicate that
defines the authorized target must participate in the same transaction as the mutation.
For pending moves that means row, keyed session, task, move, workflow, current step, and
target step, plus one-success concurrency and unchanged state on every mismatch.

The existing TTL/orphan repair prevents old replay but cannot safely clear a fresh row.
Platform Spec `7056a702-a3c3-4fe8-8535-c6b8d340ef6a` owns the exact operation. Until it
lands, a dormant-session armed row makes the task message-unsafe: do not nudge it, retarget
it experimentally, use raw SQL, or broaden cancellation merely to make progress.

Files: `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`, `docs/DECISIONS.md`, this log.

## 2026-08-30f — ordinary Codex ACP cannot currently request a TTY

Support request `aaad659d-a9af-474e-bbb9-92a857665ab2` separated an absent capability
from a broken transport. App Server has a client-side `command/exec` request with
`tty:true`, but the ordinary model-facing Codex ACP `commandExecution` event carries no
TTY field. Having Support call App Server directly would prove a Support-issued command,
not an agent-issued one, while `process/spawn` is unavailable inside the Codex sandbox.

Once this boundary is established, repeating the same Support diagnostic cannot produce
valid acceptance. The next action is a single canonical platform capability task, not
another resume or a wrapper that allocates its own inner PTY. Task
`46945aff-382a-41a4-9f35-bd5c2806911e` owns a model-callable, guard-preserving TTY tool.
Its acceptance must retain durable evidence that the model requested `tty:true`, then
pass `test -t 0`, `test -t 1`, `stty`, and the bounded functional commands through the
ordinary agent path.

Files: `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`, `docs/DECISIONS.md`, this log.

## 2026-08-30m — Support delivery is proactive, not poll-driven

Multiple Support results arrived directly as Coordinator messages while older shared
instructions still told every session to poll `status` and `receive`. That contradiction
could duplicate work and hold an orchestration cycle open for a result the platform was
already going to push.

The durable rule is now one-way: send once, persist the request ID, continue other work,
and await the proactive result. Active-writer contention is internal broker backpressure.
The diagnostic surfaces remain only for an explicitly requested bounded test of them.

## 2026-08-30n — authenticated operations need explicit credential-bootstrap authority

An authenticated product action and the credential used to reach it are separate grants.
Requests that authorized exact queue removal or one plugin install but prohibited every
SQL mutation also prohibited Support's only available temporary-token bootstrap, so
BLOCKED was the correct outcome.

Do not write mutually impossible constraints. Use a temporary token only when the
Human/user expressly authorizes that exact mint/revoke lifecycle; bind it to the named
operations, expose no token, and require a non-secret `0 → 1 → 0` receipt. Otherwise
require a preissued credential and stop after the precise BLOCKED response.

## 2026-08-30o — failed-session queues recover through one exact read

A failed Coordinator session retained unread messages that ordinary conversation reads
could not recover. One exact authenticated queue read succeeded, but its response exceeded
the transport budget; complete bodies were therefore paginated into restricted,
task-readable files with per-page hashes and a canonical manifest digest.

The replacement primary verified ownership, modes, byte counts, hashes, one-read and
token-lifecycle receipts, then reconciled all entries FIFO against newer live state. No
source queue mutation occurred. After every disposition was durable, only the temporary
recovery pages were deleted. This makes continuity robust without replaying stale work or
turning a read request into queue-removal authority.

Files: `PROMPT.md`, `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`,
`docs/DECISIONS.md`, this log.

## 2026-08-31p — draft is routine metadata, not a confirmation gate

The Human corrected a recurring workflow framing error: agents were treating draft
status itself as an issue or asking for confirmation before making a qualified PR ready.
Draft is only provider metadata. Before routing to Review, evaluate the exact-head
readiness gate; if it passes, make the PR ready through the supported action, refresh
all post-ready workflows and review state, then notify the reviewer once for that head.

Files: `PROMPT.md`, `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`,
`docs/DECISIONS.md`, this log.

## 2026-08-31q — a zero pending-move preflight expires after target activity

A workflow-scoped Support census correctly returned zero rows, but the target task's
primary session ran afterward. Reusing the earlier result for a later corrective message
would have treated a timestamped observation as durable permission even though the
session turn could have consumed, replaced, or created pending-transition state.

The durable gate now binds a zero result to exact task/workflow identity, physical lane,
complete session IDs/states/`updated_at`, and read time. Any relevant lane/session
change before contact requires a fresh exact-scope census. Null pending-action projection
fields never replace the authoritative row read.

Files: `PROMPT.md`, `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`,
`docs/DECISIONS.md`, this log.

## 2026-08-31r — Support is one request per unresolved platform incident

The Human identified that Support traffic had become excessive. The Coordinator was
opening a new read-only `pending_moves` request before many routine task contacts because
the direct capability was unavailable and earlier point-in-time results expired after
session activity. Those requests were safe individually but not operationally relevant
as separate escalations.

Support is now incident-based and deduplicated: exhaust normal tools, one bounded retry,
and documented fallbacks; then send one request for a genuine unresolved platform/host
root cause, batching exact tasks where useful. Routine messages, moves, wake replies,
CI/review work, and metadata reads do not qualify. Without direct pending-move access,
stable same-lane coordination uses a complete live session census and immediate
verification. Concrete risk may justify one request to add or restore a reusable
guarded platform capability, never a one-off Support lookup.

Files: `PROMPT.md`, `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`,
`docs/DECISIONS.md`, this log.

## 2026-08-31s — Support repairs capabilities; it never relays operations

The Human sharpened the Support boundary after the first frequency correction. Support
is for platform repairs and external capabilities unavailable to task agents: dead or
unresumable sessions, damaged task environments, host/container failures, missing
packages, Android emulators, and comparable guarded platform provisioning.

It is not a message relay, registry/database reader, metadata lookup service, provider
poller, or routine operator. If a missing direct capability matters, ask once for the
platform to provide a reusable guarded capability; never ask Support to execute each
instance of the missing operation. The prior high-risk one-off lookup exception is
removed.

Files: `PROMPT.md`, `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`,
`docs/DECISIONS.md`, this log.

## 2026-08-31t — QA the runtime plane, not the deployment label

A Dockerized Kandev deployment exposed an ambiguity: the published Kandev image is the
control plane, while some features change only the Local Docker executor task containers
that it creates. Treating “Kandev runs in Docker” as a single runtime either makes a
relevant executor feature look irrelevant or produces a second control-plane instance
that cannot exercise the changed path.

The durable procedure now traces the changed code to its target plane before provisioning
QA. Test that plane directly. Use `TEST_RUNTIME=NONE` when there is no persistent
Human-operated surface and named exact-head automation already exercises the target
plane; state both the plane and evidence in the handoff.

Files: `docs/RUNBOOK.md`, `docs/QA_INSTANCES.md`, `docs/DECISIONS.md`, this log.

## 2026-08-31u — Compose overrides need a narrow deployment-owned transport

A task's tracked Compose file already accepted isolated database and web ports, but the
guarded client discarded the command-scoped values before Compose interpolation. The
mandatory pre-push hook consequently used shared defaults and collided with an occupied
host port. Ownership mattered: the installed client/broker belonged to the deployment
repository, so patching upstream product source would have changed the wrong plane.

The persistent repair forwards only `COMPOSE_PROJECT_NAME`, `DB_PORT`, and `WEB_PORT`,
validates names and port ranges, and keeps every unrelated environment value excluded.
Independent guarded acceptance must cover valid rendering, sentinel non-disclosure,
invalid-value rejection, raw-Docker denial, and cleanup before a blocked task resumes.

Files: `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`, `docs/DECISIONS.md`, this log.

## 2026-08-31v — a gate agent cannot certify its own fix

A QA turn found a real in-scope defect, added a regression, pushed the correction, and
reported `QA_RESULT = PASSED` while also routing back to Review. The fix and local tests
were valid, but the verdict was not: the successor head had been authored by the gate
turn and had not received independent Review or QA.

The durable rule binds every gate receipt to an immutable head and an independent turn.
A gate-owned change is implementation evidence. It withdraws PASS/readiness for the new
head, routes through fresh Review, and reruns QA when QA still applies. Changed-tree
backward routing is expected and must not be bypassed as a workflow replay.

Files: `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`, `docs/DECISIONS.md`, this log.

## 2026-08-31w — a proposal cannot approve itself

A detailed linked architecture issue contained a recommendation, rationale, boundary
mapping, and decision record, but every word was authored by the contributor and no
maintainer had responded. Treating the link as “architecture discussion complete” would
have converted self-documentation into external approval.

The general rule is principal-bound: when repository policy requires maintainer or
architecture approval, require a substantive response from that named authority and
record its author, URL, timestamp, and answered scope. Board-level Coordinator authority
does not impersonate an upstream maintainer or waive the repository's policy gate.

Files: `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`, `docs/DECISIONS.md`, this log.

## 2026-08-31x — dependency relation fields are viewpoint-relative

An edge-correction receipt appeared to disagree with `list_related_tasks_kandev`
because the read projection's `blocked_by` field was mistaken for the queried task's
prerequisites. Source verification showed the inverse: `blockers` are prerequisites of
the queried task, while `blocked_by` are its downstream dependents. The mutation receipt
and both read projections were therefore consistent, and an idempotent removal retry was
unnecessary but harmless.

Read both task projections and interpret each field from the queried task's viewpoint
before changing an edge. This prevents a correctly oriented dependency from being
misclassified as a persistence defect or removed in the wrong direction.

Files: `docs/RUNBOOK.md`, this log.

## 2026-08-31y — replacement and parallel evidence need readback barriers

A successful full-content plan update once concealed a truncated replacement until a
prior read receipt restored it. The durable rule is transactional in practice: retain
the exact full pre-write plan, read the result back immediately, verify identity,
anchors, and completeness, and restore the exact prior content on any mismatch. Never
reconstruct lost normative state from memory.

The same audit found several operational documents lagging behind binding policy. Queue
helpers now feed a fresh live task/session/provider read before any action or human-facing
result; missing queue-removal capability leaves rows intact instead of delegating one-off
removal to Support; guarded same-workspace recovery may replace a proven stale,
non-consuming session without creating concurrent writers; and Support normally delivers
results proactively after one `send`. Dependency reads are also registered explicitly as
viewpoint-relative so edge changes verify both endpoints.

Files: `README.md`, `docs/CAPABILITY_REGISTRY.md`, `docs/RUNBOOK.md`, this log.
