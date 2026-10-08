# Agent Handoffs

After each stage, create a concise factual report named `01.md` through `09.md`.

Each report must include:

## Outcome

Completed, blocked, or failed, with actual date/time and worktree state.

## Implemented

Working behavior and important changed files.

## Contracts

New or changed API routes, schemas, configuration, storage, and migrations.

## Verification

Actual commands, exit codes, PASS/FAIL/NOT_RUN results, and relevant tool versions.

## Hardware

Real physical tests versus simulation, fixtures, and unavailable checks.

## Limitations

Known defects, incomplete requirements, safety concerns, and deferred work.

## Next agent

Commands to run, files to inspect, and facts needed to continue without prior chat context.

Update `docs/agent/STATUS.md` separately. Never rewrite previous evidence to conceal a failed test.
