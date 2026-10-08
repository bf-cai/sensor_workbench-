# Sensor Workbench

A Linux workbench for sensor integration, synchronization diagnostics, recording, reproducible experiments, and cross-sensor measurement-time alignment.

**Current repository contents:** implementation plan only. Application development begins with Stage 01.

## Using a coding agent

Open the repository and instruct the agent:

> Do the next stage. Follow AGENTS.md, complete the stage acceptance criteria, run the real quality tools, update STATUS.md and the handoff, then stop.

The agent finds the next stage in `docs/agent/STATUS.md`.

## Where information lives

- `AGENTS.md`: execution procedure.
- `docs/agent/RULES.md`: coding standards, safety, testing, and completion requirements.
- `docs/agent/STATUS.md`: authoritative stage state.
- `docs/agent/SPEC.md`: product requirements and retained decisions.
- `docs/agent/ARCHITECTURE.md`: technical stack and shared contracts.
- `docs/agent/stages/`: the nine implementation tasks.
- `docs/agent/handoffs/`: results from previous agent sessions.

Stage 01 must replace this planning README with verified installation, development, testing, and operating instructions while retaining the navigation above.

## Engineering principle

Build the smallest complete, tested solution that advances the product goal. Prefer real working vertical slices to speculative architecture. Preserve correct timestamp semantics and evidence throughout.
