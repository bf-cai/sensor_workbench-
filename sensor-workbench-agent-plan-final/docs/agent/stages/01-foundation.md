# Stage 01 — Minimal Working Platform

## Objective

Deliver a runnable Linux backend and browser UI with one real end-to-end simulated timing flow, plus enforceable engineering tooling.

## Deliverables

1. Create the Python package `sensor_workbench`, FastAPI app, CLI (`serve` and `version`), configuration, and graceful shutdown.
2. Create React/TypeScript/Vite frontend with a single working overview page and Apache ECharts plot.
3. Implement `ClockDomain`, `Timestamp`, `Observation`, and minimal source/capability models from ARCHITECTURE.
4. Implement one deterministic simulated source producing 10 observations/second. Label every simulated value as simulated. Use a bounded queue and explicit source clock domain.
5. Implement the four baseline API endpoints specified in ARCHITECTURE. Stream observations over WebSocket with reconnect-safe source identification.
6. Generate TypeScript API types from OpenAPI, with a documented reproducible regeneration command.
7. Configure uv, npm lockfiles, Ruff, mypy, pytest, ESLint, Prettier, strict TypeScript, Vitest, and applicable Markdown linting.
8. Implement the required root Makefile quality targets, using real tools.
9. Add tests for timestamp serialization, clock-domain identity, simulation determinism, API responses, WebSocket messages, and frontend rendering.
10. Write actual setup, run, test, and troubleshooting commands in README. Default to loopback; document SSH tunneling for remote viewing without opening an unauthenticated LAN listener.

## Scope boundary

No hardware integration, MCAP, database, general plugin framework, advanced authentication system, or unrelated screens.

## Acceptance

- A fresh install starts on Linux without sensors, root, ROS 2, or GPU.
- Browser displays live simulated timing data from the backend, not hardcoded UI values.
- Source provenance, units, and clock domain are visible.
- All quality commands run actual tools and pass.
- API contracts and README match the implementation.

## Handoff

Write `docs/agent/handoffs/01.md`, update STATUS, and stop.
