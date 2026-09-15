# Standalone agentctl port-capacity diagnostic

- observed_at: 2026-09-15T00:11:12Z
- scope: current Coordinator session; read-only
- configured instance range: 41001-41100 inclusive (100 ports)
- supported diagnostic bundle: backend bundle requested twice with bounded waits; both calls remained pending and were terminated; no ZIP was materialized in the current execution workspace
- mutations: none (no teardown, kill, database write, host change, provider contact, or credential access)

## Evidence and cause

The emitted failure `failed to allocate port: no available ports in range [41001, 41100]` is produced by agentctl's in-memory `PortAllocator`. Allocation scans the inclusive range and rejects only when every entry is represented either in `allocated` or `unavailable`. `allocated` maps a port to an instance ID. A bind collision calls `MarkUnavailable`, which removes that port from `allocated` and permanently excludes it for the lifetime of the current agentctl control process. Therefore the exact failure proves logical capacity saturation of all 100 slots; it does not by itself prove that 100 live agent instances exist.

The manager registers a successfully created instance only after tracker startup and HTTP listener setup. It has cancellation cleanup for partially created instances. The current source also includes a one-hour idle reaper with a one-minute sweep, but any in-flight HTTP/WebSocket request prevents reaping. A failed teardown retains the instance and its port. These mechanisms make the main remaining explanations: still-owned/live instances; stopped or disconnected instances not yet idle/reapable; failed teardown; or ports marked unavailable after bind conflicts. The read-only instance census can distinguish registered instances from the remainder, but it cannot enumerate the allocator's private `unavailable` set.

## Supported authenticated census

Use the already-running backend's `ControlClient.ListInstances`, which performs authenticated `GET http://<configured-standalone-host>:<configured-control-port>/api/v1/instances`. The control API requires its internally held Bearer token; `/health` and the one-shot bootstrap handshake are the only exemptions. Do not retrieve, print, or pass the token outside the normal backend/operator integration. The response exposes instance ID, port, status, workspace path, agent command, and creation time; environment values must be omitted/redacted in any operator report.

For per-ID confirmation, the supported read-only operation is authenticated `GET /api/v1/instances/{id}`. Correlate only non-secret instance ID/status/port/created_at against authoritative session/execution ownership and generation before deciding anything is stale.

## Normal lifecycle teardown

The normal standalone teardown is the backend lifecycle path `StandaloneExecutor.StopInstance`, which calls `ControlClient.DeleteInstance`: authenticated `DELETE /api/v1/instances/{id}`. The agentctl handler uses a detached 15-second context and `Manager.StopInstance`, which serializes teardown, marks status `stopping`, closes process-start admission, quiesces/closes the instance HTTP server, calls `StopForTeardown`, then releases the port and deletes the instance only after successful cleanup. This is the supported operation; direct process kill or socket manipulation bypasses cleanup and must not be used.

## Reclaimability verdict

No individual instance is conclusively reclaimable from this diagnostic run. The supported bundle did not materialize, so there is no diagnostic instance ID/state/generation census to correlate. The current Coordinator instance is actively serving this session and is not a candidate. Zero terminal/unowned stale instance IDs are proven.

## Smallest safe operator action

1. Through the backend/operator integration that already owns agentctl authentication, run one read-only `ControlClient.ListInstances` census.
2. Compare returned non-secret IDs/status/created_at with authoritative session/execution ownership and current generation. Treat any uncertainty as owned.
3. If exactly one instance is proven terminal, unowned, and generation-stale, invoke the normal backend session teardown; for a true orphan with no session record, invoke one authenticated `DELETE /api/v1/instances/{id}` through the supported control client.
4. Re-run the read-only census and one session-start capacity probe before reclaiming another instance.

If the census returns fewer than 100 registered instances while allocation still reports exhaustion, do not delete additional instances speculatively: the deficit points to allocator `unavailable` slots (or an in-progress creation). Escalate for a coordinated agentctl restart or a product fix that exposes/reset-revalidates unavailable reservations. A restart is broader than per-instance teardown and needs an operator-controlled maintenance window.

## Local implementation evidence

- `/data/home/Code/kandev-source/apps/backend/internal/agentctl/server/instance/port_allocator.go`: allocator, release, permanent-in-process unavailable marking.
- `/data/home/Code/kandev-source/apps/backend/internal/agentctl/server/instance/manager.go`: create/abandon cleanup and ordered teardown/port release.
- `/data/home/Code/kandev-source/apps/backend/internal/agentctl/server/api/control_server.go`: authenticated GET/DELETE instance routes and bounded teardown.
- `/data/home/Code/kandev-source/apps/backend/internal/agent/runtime/agentctl/control.go`: supported control client census/delete calls.
- `/data/home/Code/kandev-source/apps/backend/internal/agent/runtime/lifecycle/executor_standalone.go`: normal lifecycle bridge to delete.
- `/data/home/Code/kandev-source/apps/backend/internal/agentctl/server/config/config.go`: defaults 41001-41100, idle timeout 1h, sweep 1m.
- installed `/usr/local/bin/agentctl` and `/app/apps/backend/bin/kandev` contain matching ListInstances/DeleteInstance/StandaloneExecutor symbols and route strings; installed backend identifies as Go 1.26.0, module `github.com/kandev/kandev (devel)` with no embedded VCS revision.
