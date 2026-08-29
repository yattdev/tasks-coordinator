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
