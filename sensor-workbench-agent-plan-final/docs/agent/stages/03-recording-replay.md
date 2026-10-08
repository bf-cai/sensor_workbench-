# Stage 03 — Durable Recording and Replay

## Objective

Turn existing observations into reproducible evidence that survives application restarts and can be inspected offline.

## Deliverables

1. Add bounded acquisition-to-recorder queues with sequence and drop accounting. Recording must not depend on browser connections.
2. Implement SQLite metadata with simple versioned migrations and indexed session records.
3. Implement MCAP recording using a maintained MCAP library. Store versioned observation schemas and preserve original timestamps and clock domains.
4. Add a session manifest with sources, clock domains, software/environment versions, recording references, hashes, completeness, and loss counts.
5. Implement start/stop/flush/finalize, atomic manifest updates, and interrupted-session recovery.
6. Support optional PCAPNG evidence import/attachment. If a supported capture utility is available, allow an explicitly authorized, bounded capture; do not implement a custom packet-capture format.
7. Implement replay with pause, seek, speed, and an independent replay clock. Never rewrite raw timestamps.
8. Add minimal functional session controls and a replay timeline in the browser.
9. Add CLI commands for listing sessions and inspecting session metadata.
10. Test MCAP round trips, large timestamp values, incomplete sessions, storage exhaustion, malformed data, replay speed/seek, and drop counters.

## Scope boundary

No cloud storage, external database server, full sensor drivers, or advanced analysis.

## Acceptance

- A simulated or observed timing session records and replays offline.
- Raw timestamps, clock domains, and provenance survive round trips unchanged.
- Incomplete sessions are recoverable or clearly marked.
- Manifests, hashes, and drop counts are inspectable.
- Browser disconnects do not stop recording.
- Existing quality checks pass.

## Handoff

Write `docs/agent/handoffs/03.md`, update STATUS, and stop.
