# Runbook

## No standup this morning
1. `crontab -l | grep kandev-coordinator` — entries present, exactly once each?
2. 2. `tail -50 ~/.local/state/kandev/coordinator-wake.log` — did cron fire? FATAL lines?
3. 3. Manual wake: `kandev-coordinator-wake.sh STANDUP` — watch the task in the UI.
4. 4. Script OK but task silent → check the task's session state in KanDev;
5.    test whether `message_task_kandev` relaunches idle sessions (see DECISIONS).
6. 
7. ## Wake script fails
8. - `FATAL: coordinator.env missing` → recreate from config/coordinator.env.example, chmod 600.
9. - `initialize failed HTTP ...` → MCP_URL/port wrong, endpoint down, or auth; try `tools/list` manually.
10. - `tools/call failed` / isError → check argument names (`task_id`, `message`) against `tools/list`.
11. 
12. ## Coordinator misbehaving (over-escalating / over-deciding / looping)
13. - Read its cycle logs on the task — decisions are one-line documented.
14. - Veto via comment; it calibrates from vetoes.
15. - Looping or runaway: flag the task with "STOP — wait for direction"; it must freeze.
16. 
17. ## Duplicate cron entries
18. Remove all marker-carrying entries, let the next session start re-provision
19. (idempotent check is on every session start).
20. 
21. ## Weekly hygiene
22. Cycle logs on the task grow; have the coordinator roll up old logs into a
23. weekly summary comment (or do it manually) to keep its context lean.
