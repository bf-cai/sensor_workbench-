# Stage 04 — Linux Device and Transport Integration

## Objective

Make common Linux sensor interfaces observable while preserving a small, extensible architecture.

## Deliverables

1. Add read-only USB, serial, Ethernet endpoint, and SocketCAN discovery through supported Linux facilities.
2. Separate physical device identity from transport address, data source, clock domain, and synchronization method.
3. Report interface state, driver, permissions, and capabilities with explicit unknown/unavailable reasons.
4. Implement bounded, opt-in generic CAN frame observation with interface, CAN ID, raw payload reference, and kernel/host receive timestamp provenance where available.
5. Implement bounded, opt-in serial line observation for selected ports. Do not interpret undocumented payloads.
6. Handle hotplug, reconnect, permissions, malformed input, and source freshness.
7. Add a minimal internal adapter registry and a short developer guide demonstrating how a real source is added.
8. Prioritize documented Livox HAP timestamp extraction when an SDK, supported data stream, or recorded evidence makes it practical. Distinguish point-cloud and IMU timestamp semantics and synchronization-type freshness. If unavailable, document the missing prerequisite rather than inventing a driver.
9. Support Xsens and HBK capability profiles only for verified/documented fields; no invented sample-time interpretation.
10. Show discovered devices, sources, clock domains, and available observations in the browser and session manifests.
11. Test absent hardware, changing device paths, invalid frames, permissions, and disconnections.

## Scope boundary

No DBC/J1939 interpretation, general CAN payload decoding, firmware updates, unsupported vendor commands, or large device-driver framework.

## Acceptance

- Available Linux transport interfaces are discovered.
- CAN and serial observations work when their real interfaces are available, with correct timestamp provenance.
- Missing devices do not break startup or replay.
- HAP-specific functionality is either evidence-backed or explicitly unverified.
- No host receive timestamp is misrepresented as physical sensor sample time.
- Quality checks pass.

## Handoff

Write `docs/agent/handoffs/04.md`, update STATUS, and stop.
