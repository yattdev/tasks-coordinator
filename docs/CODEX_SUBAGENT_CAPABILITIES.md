# Codex / Kandev bounded-worker capability assessment

Verified 2026-09-20 on the Coordinator task. This is an environment-specific
receipt, not an assertion that every Codex client exposes the same tool schema.

## Conclusion

The current PRIMARY can spawn named native workers with explicit model and
reasoning-effort requests. Concurrent Terra/high and Luna/medium requests were
accepted, completed bounded work and returned separately correlated results.
The Luna result passed independent source checks. No new persistent Kandev
session, task, primary, workflow change or heartbeat was created.

The remaining observability gap is independent proof of the child model/effort
actually used and its attributable tokens/cost. Current native lifecycle receipts
identify the Codex child thread but do not expose those fields. Successful
requested-model dispatch is verified; actual lower billed cost is not.

## Installed versions and evidence

- `codex --version`: `codex-cli 0.153.4`.
- npm `@agentclientprotocol/codex-acp`: `1.2.0`. Its installed adapter resolves
  `@openai/codex/bin/codex.js` to the same global `0.153.4` package. `CODEX_PATH`
  is unset in the inspected execution environment.
- Supported Kandev backend diagnostic manifest: `v0.94.0-310-g50d95d2ae`, commit
  `50d95d2ae`, build `2026-09-19T04:48:25Z`.
- Backend bundle: `.kandev/diagnostics/ad427fbcd30038e2fdd91ca3bfe940cf.zip`.
  Only its manifest was needed; backend log contents were not used.
- CLI-generated protocol schemas: task-root `codex-schema-TERRA6731/`, outside
  the repository. Generated schemas describe the app-server protocol, not
  necessarily the model-visible collaboration tool.
- Current model-visible host tool: `collaboration.spawn_agent`. That exact
  exposed interface is authoritative for calls from this PRIMARY.

## Capability matrix

| Question | Current result | Boundary |
| --- | --- | --- |
| PRIMARY creates native children | Verified by two completed probes | Native threads are not persistent Kandev task sessions. |
| Explicit model selection | Schema exposes `model`; Terra and Luna requests accepted and completed | Available overrides include `gpt-6-astra`, `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `gpt-5.5`. Sol was not re-probed this turn. Effective-child-model attestation is missing. |
| Explicit reasoning effort | Schema exposes `reasoning_effort`; high/medium requests accepted | Effective effort is not in the returned lifecycle receipt. Supported values depend on model. |
| Context selection | `fork_turns`: `none`, `all`, or positive integer string | Default/all inherits full history and parent model/effort; it does not accept overrides. Use `none` for compact workers. |
| Default cheaper child | Installed CLI strict parser accepts `agents.default_subagent_model` and `agents.default_subagent_reasoning_effort` | Not configured in inspected user/project files. Their effect on this host wrapper is not proven; explicit calls need no default. |
| Custom agent selection | No `agent_type`, `config_file`, cwd, or sandbox field in this host spawn schema | Custom-agent files documented for Codex are not automatically selectable through this wrapper; task names are identifiers, not profile selectors. |
| Temporary bounded work | Verified: child finished and returned a result | Completion ends active work, not necessarily retained transcript lifetime. No close/delete tool is exposed here; interruption and reuse are exposed. |
| Concurrent workers and correlation | Two workers overlapped; canonical paths and Codex thread IDs distinguish results | Runtime declares four active slots including PRIMARY, hence at most three active descendants in this team. No saturation test performed. |
| Kandev tool access | Luna could read own task's session census | It saw the parent's current session; this is inherited authority, not a separate Kandev approval principal. Board writes were not tested. |
| Heartbeat integration | Fits the existing event/wake-driven PRIMARY | Native children add no wake source or scheduler; queued-message transfer and restart recovery remain separate concerns. |

Exact schema fields are `task_name`, `message`, optional `fork_turns`, `model`,
and `reasoning_effort`. The live schema does expose the two override fields in
the user's caveat. Do not pass an undocumented `agent_type` or assume a future
client retains these fields. A full-history fork cannot be used to override a
model in this host. Reuse via `followup_task` has no model/effort override fields;
choose a new bounded child if a different model is required.

## Configuration verification and fallbacks

The app-server `ConfigReadResponse` typed `Config` omits `agents` but has
`additionalProperties: true`. Its omission is not evidence of no support.
We tested installed parsing without model inference or persistent config edits:

```sh
codex app-server --strict-config --listen stdio:// \
  -c 'agents.default_subagent_model="gpt-5.6-terra"' \
  -c 'agents.default_subagent_reasoning_effort="medium"' \
  -c 'agents.max_concurrent_threads_per_session=3' </dev/null
```

The baseline and these overrides exited 0. An invented top-level field exited
1 with `unknown configuration field`; an invented boolean under `agents`
failed because a custom `AgentRoleToml` was expected. However, an invalid effort
string also passed startup: parsing does not prove launch-time model/effort
validation. We did not claim a live worker launched from these defaults.

Optional fallback for a Codex client that is verified to load this config:

```toml
[agents]
default_subagent_model = "gpt-5.6-terra"
default_subagent_reasoning_effort = "medium"
max_concurrent_threads_per_session = 3
```

Do not change the top-level primary model to achieve child defaults. No config
change is necessary for today's explicit-override path. Custom `.codex/agents/`
files are another documented fallback only after the receiving tool exposes a
way to select them and a real launch verifies their configuration precedence.
The installed adapter supports merging `CODEX_CONFIG` for sessions, but this
assessment did not change adapter environment or workflow configuration.

Kandev's separate `spawn_session_kandev` accepts a profile ID and prompt, not
raw model/effort or context-fork fields. It creates a persistent session/tab.
Its schema explicitly permits the lane to override the requested profile;
prior actual-model receipts confirmed such overrides. Enabled profiles exist:

| Role | Profile ID | Configured model / effort |
| --- | --- | --- |
| Terra | `5d7135f9-8b98-4168-856d-1b495e19b481` | `gpt-5.6-terra` / medium |
| Luna | `40385329-6d98-4273-ab7c-aa29ff4353d1` | `gpt-5.6-luna` / medium |
| Sol | `24eff7cc-14c2-4147-b635-5be3df285af3` | `gpt-5.6-sol` / medium |

These profiles have `auto_fallback=false` and `require_exact_model=false`;
neither labels nor configuration prove a launch. Reuse a suitable existing idle
sidecar or an explicitly authorized Kandev session when task identity/lifecycle
is required, checking its actual agent-message `metadata.model`. The Kandev
spawn prompt is its only supplied task context. No persistent session was
created for this assessment.

## Proof of concept

The exact bounded native request shape used was:

```json
{
  "task_name": "cheap_worker_poc",
  "model": "gpt-5.6-luna",
  "reasoning_effort": "medium",
  "fork_turns": "none",
  "message": "request_id=spawn-poc-luna-20260920; nonce=LUNA-4829; read PROMPT.md, return its byte count/hash, charter role and git head; read only own task session census once; no writes; return structured observations, evidence gaps and blockers; stop."
}
```

The actual message also supplied absolute cwd and exact task/workspace/primary
identities. Result: 17,331 bytes; SHA256
`992f8195d4e14c7c67e98a03f4210e8f9b78b9a6c96c3f7d68374fbd259babfc`;
charter `2026-09-20a`; HEAD `96649e9b58bcd7f8775dd4ef2583d45985a01f92`;
three existing Kandev sessions and only PRIMARY
`2f61dda1-ac84-429d-a7b0-e3f91eed80fa`. Astra independently matched the hash,
bytes, head, session identities and live charter mirror. No source/board writes.

Kandev completion message `9dad86f8-93d4-49ef-9d1a-3f7c23af1281` at 00:24:00Z
correlates `/root/cheap_worker_poc` to Codex child thread
`01a0bc32-c936-7791-b78f-b8680e9d7cf5`. Terra/high audit ran under
`/root/codex_install_audit`, thread `01a0bc32-800c-7650-b9a8-697b6a65fb2c`,
with separate request ID `spawn-poc-terra-20260920` and nonce `TERRA-6731`.

The native thread ID is projected as `child_session_id` in a normalized tool
event but is not a Kandev persistent session ID: an exact conversation read
returned `NOT_FOUND: session not found`. The installed ACP adapter's
`createSubAgentActivityUpdate` carries thread/path/activity only. Its older
collaboration-event mapping has model/effort fields, but those were not present
in the observed native activity receipt. Do not mistake this projection gap
for failure to spawn, or a child's self-description for independent attestation.

PoC verdict: execution, result correlation, concurrent bounded work and inherited
read access PASS. Independent effective-model/effort and cost attribution remain
UNVERIFIED. This does not block the verified low-risk execution path.

## Recommended implementation and remaining limits

Use native explicit overrides with `fork_turns="none"` by default. Astra sends
the execution packet, verifies the result and owns the next decision. Include
request/strategy IDs, exact task/workspace/source, allowed actions, expected
outcome, deadline, stop/fallback and evidence format. Parent instructions and
tools still apply; `none` is a history choice, not a security sandbox. Filesystem
and tool authority are shared. Serialize board mutations and isolate source
writers using the existing task ownership rules.

No runtime code/config change is required for this basic flow. Keep engineering
implementation inside the persistent task's ownership rather than launching an
untracked Coordinator child into another card's worktree. A task's own authorized
worker can use bounded native assistance where its workflow permits it.

For production measurement, improve the existing native-activity projection to
include requested and effective model/effort, request ID, child status/error,
tokens and usage coverage. Persist accepted results/action IDs in the Coordinator
plan; do not rely on native in-memory state surviving a PRIMARY restart. This is
a proposed small observability enhancement, not implemented platform work.

On timeout or ambiguous outcome, reconcile the existing child before retrying;
stale generation/head stops action; permission or capacity failure returns an
exact blocker. Interruption is available but does not undo completed tool writes.
No per-child token budget, hard wall-clock deadline, isolated cwd or custom
sandbox is exposed in this spawn schema. Packet bounds are instructions, not
hard resource enforcement. Queue census still returns `UNKNOWN_ACTION` and
does not become available by using a native worker.

Retain the existing heartbeat: wake Astra, collect compact evidence cheaply,
decide, dispatch bounded work, verify, checkpoint. Helpers stop after a receipt;
they do not become autonomous coordinators or create timers. Measure whole-team
cost per verified outcome; startup, repeated bootstrap and reviews can outweigh
small delegations. No prices or savings were established by this test.

Official reference, checked against local evidence rather than used as proof:
[Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents).
