# Coordinator bootstrap

This repository configures a long-lived Kandev board Coordinator.

Before taking any action on every turn—including human messages, task messages,
routine wakes, resumed sessions, and model switches—read `PROMPT.md` completely.
Then resolve the live Coordinator task/workspace/workflow identity and read the
current Kandev task plan section `Coordinator state & cycle logs`. Conversation
memory is not a substitute for either read.

`PROMPT.md` is the canonical policy. This file is only the cross-agent bootstrap;
do not duplicate the charter here. Read the relevant sections of
`docs/RUNBOOK.md`, `docs/DECISIONS.md`, and `docs/QA_INSTANCES.md` when the action
they govern arises.

Every full board monitoring cycle includes the complete Done column and enforces
the Done terminal-integrity gate in `PROMPT.md`. A merged PR or Done placement is
not sufficient evidence that local work was pushed and preserved.

System, developer, and current user instructions take precedence. Persist any
durable human override back into `PROMPT.md`, mirror it to the live task
description, commit it on this worktree's branch, and fast-forward the shared
`/data/home/Code/coordinator` main checkout as described in the charter.
