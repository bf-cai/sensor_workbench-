# Coding Agent Entry Point

This repository is implemented through nine sequential stages. The instructions are designed to work without previous conversation context.

## When told "do the next stage"

1. Read `docs/agent/STATUS.md`.
2. Read `docs/agent/RULES.md`, `docs/agent/SPEC.md`, and `docs/agent/ARCHITECTURE.md`.
3. Inspect the actual repository, current Git changes, and the previous stage handoff.
4. If a stage is `in_progress`, `blocked`, or `failed`, resume or repair it. If state is `ready`, use the `next_stage` in STATUS. If `complete`, stop.
5. Read the entire matching `docs/agent/stages/NN-*.md` file.
6. Update STATUS to `in_progress` before substantive implementation.
7. Implement **only** that stage. Do not silently expand scope or start a later stage.
8. Run the actual applicable formatters, linters, type checkers, tests, and build checks.
9. Write `docs/agent/handoffs/NN.md` with factual results, commands, limitations, and next-stage information.
10. Update STATUS to `ready` for the next stage **only if acceptance passes**. Otherwise retain the current stage and mark `blocked` or `failed`.
11. Stop and report the result.

If another agent may still be editing the active stage, do not start concurrent work without coordination.

## Priority

1. User's explicit current instruction and safety requirements.
2. `docs/agent/SPEC.md` for product scope.
3. `docs/agent/RULES.md` for engineering standards.
4. `docs/agent/ARCHITECTURE.md` for shared technical contracts.
5. The selected stage file for stage-specific work.
6. Actual code and tests as evidence of implemented behavior.

If documents conflict, stop and resolve the contradiction rather than guessing. Do not invent user decisions.

## Hard boundaries

- Independent project. Never modify `/home/correct-ai/fieldeye`.
- Preserve unrelated files and uncommitted Git changes.
- Never claim unrun tests, simulated hardware results, or unmeasured accuracy as verified.
- Never make disruptive clock, network, CAN, or device changes without explicit authorization.
- Do not read binary files unless essential to the current task. Follow RULES for permitted targeted inspection.
- Do not commit, force-reset, delete user data, or install system packages without appropriate authorization.
- Finish with an accurate status and handoff, even if blocked.
