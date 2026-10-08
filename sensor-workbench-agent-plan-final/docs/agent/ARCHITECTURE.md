# Minimal Architecture and Shared Contracts

This file defines technical boundaries. Do not add abstractions until required by implemented behavior.

## Stack

- Python 3.10+ with FastAPI and Pydantic v2.
- React, TypeScript, Vite, Apache ECharts.
- SQLite for metadata.
- MCAP for event/sensor recordings.
- PCAPNG for packet evidence where available.
- LinuxPTP for PTP/gPTP, SocketCAN for CAN.
- uv and npm with committed lockfiles.

Frontend assets are compiled and served by the backend. Node is not a runtime requirement on Jetson.

## Target layout

Create directories when working code requires them, not as empty scaffolding.
Application code and commands live at the repository root. Agent/developer
documents remain in `sensor-workbench-agent-plan-final/docs/`; the root
`AGENTS.md` points to the full execution procedure in the planning directory.

    backend/
      pyproject.toml
      uv.lock
      src/sensor_workbench/
        api/
        core/
        adapters/
        services/
        storage/
        app.py
        cli.py
      tests/
    web/
      package.json
      package-lock.json
      src/
        app/
        api/
        features/
        components/
      tests/
    deploy/
    sensor-workbench-agent-plan-final/
      AGENTS.md
      docs/
        agent/
        user/
        developer/
    Makefile
    AGENTS.md
    README.md

`core` owns timing and domain models, independent of FastAPI and hardware.
`adapters` translate real/simulated sources into core observations.
`services` own acquisition, recording, replay, experiments, and analysis.
`storage` owns durable formats.
`api` and `cli` expose services without duplicating business logic.
`web` uses typed backend contracts.

Do not create multiple backend services unless justified by a real requirement. A small separate privileged helper is permitted for narrowly authorized operations.

## Canonical contracts

Use typed, versioned Pydantic models. Extend compatibly; do not silently change existing field semantics.

**ClockDomain**
- `id`, `owner`, `timescale`, `epoch_description`.
- Optional `tick_rate_hz`, `resolution_ns`, `boot_id`.
- Timescales include UTC, TAI, GPS, PTP, HOST_MONOTONIC, DEVICE_LOCAL, DEVICE_TICKS, UNKNOWN.

**Timestamp**
- Integer `value`, `unit`, `clock_domain_id`, `semantics`.
- Semantics include sample, first_point, last_point, exposure_start, exposure_end, trigger, transmit, receive, unknown.
- No implicit clock conversion.

**Observation**
- `schema_version`, `event_id`, `source_id`, optional `sequence`, `kind`.
- Optional raw `Timestamp`.
- Optional `host_receive_monotonic_ns` with boot ID.
- Optional kernel and userspace receive timestamps with their clock domains.
- Typed metric or payload reference, quality flags, simulation flag, provenance.
- Derived common time and mapping version remain separate from raw time.

**Capability**
- Owner/source, method family, prerequisites, evidence, and distinct supported/available/active/unknown/unverified states.

**ClockMapping**
- Source and target domains; raw/common anchor pair; rate/drift; validity interval; method; uncertainty; immutable version.
- Apply anchored differences to avoid floating-point precision loss on epoch timestamps.
- Split mappings across clock discontinuities.

**Session**
- ID, sources, environment, clock domains, recording files, checksums, drop counts, completeness, provenance.

**ExperimentResult**
- Prerequisites, authorization, parameters, actions, cleanup, metrics, evidence, result and limitations.

Only implement contracts required by the current stage; reserve backward-compatible fields for later capabilities rather than implementing empty services.

## Extension boundaries

Use small typed interfaces when needed:
- Device source: identify, probe, observe.
- Synchronization source: detect, observe, optional authorized control.
- Acquisition source: start, stop, bounded observation stream.

Use an explicit internal registry, not dynamic untrusted plugin loading.

## API

Base path `/api/v1`. Stage 01 establishes:
- `GET /api/v1/health`
- `GET /api/v1/sources`
- `GET /api/v1/clock-domains`
- `WS /api/v1/stream`

Add later routes only when working. Backend OpenAPI schemas are authoritative; generate TypeScript API types and check them in CI or quality targets.

WebSocket messages must identify source, schema version, sequence/freshness, and loss where known. Use bounded buffers. Do not send full-rate LiDAR packets as chart JSON.

## Storage and deployment

Use XDG-compliant configuration and state paths with explicit overrides. Raw sessions are immutable and contain versioned manifests, MCAP, optional PCAPNG, and derived reports.

Default bind address is `127.0.0.1`; remote access is opt-in and authenticated. The web service must not run as root.

## Four distinct timing quantities

1. Device clock offset when independently measurable.
2. Measurement/packet-to-host arrival lag.
3. Motion-derived cross-sensor offset/drift.
4. Physical fusion/alignment residual.

Never substitute one for another without evidence.
