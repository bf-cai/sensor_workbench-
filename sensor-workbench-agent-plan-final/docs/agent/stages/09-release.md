# Stage 09 — Integration, Portability, and Release

## Objective

Deliver an installable, maintainable Linux application with evidence-backed capabilities and no unfinished production paths.

## Deliverables

1. Audit the repository for broken contracts, duplicated logic, unused dependencies, dead code, and incomplete workflows.
2. Package the backend and compiled frontend for supported Linux x86-64 and ARM64 systems. Distinguish actual device testing from build-only or emulated verification.
3. Document reproducible installation, startup, upgrade, backup/recovery, and optional systemd operation.
4. Verify the core runtime does not require Node, Docker, ROS 2, CUDA, a GPU, or cloud access.
5. Test localhost defaults, authenticated LAN operation, permission boundaries, and privileged-helper allowlists.
6. Test database migrations, interrupted recordings, failed experiments, device disconnects, disk limits, and restart recovery.
7. Measure CPU, memory, recording throughput, queue drops, and chart performance with reproducible workloads.
8. Review dependency licenses and distribution obligations. Do not bundle GPL source or binaries without understanding the implications.
9. Run all actual formatters, linters, type checkers, unit/integration tests, Playwright workflows, and production builds.
10. Complete concise user and developer documentation and a verified platform/device capability matrix.
11. Resolve blocking defects. Label unverified physical hardware and future enhancements accurately rather than claiming they are implemented.

## Scope boundary

No new feature families, speculative refactoring, or unrelated product development.

## Acceptance

- Installation and main workflows work on the Linux targets actually tested.
- All mandatory quality checks pass.
- Security, recovery, and storage limits are tested.
- Documentation matches actual behavior.
- Supported hardware, synchronization, and performance claims have evidence.
- Unavailable hardware is explicitly marked unverified.

## Handoff

Write `docs/agent/handoffs/09.md`, set STATUS to `complete` with no next stage, and stop.
