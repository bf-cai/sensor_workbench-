# Stage 05 — Additional Synchronization Methods

## Objective

Add practical synchronization observations beyond PTP, without building full industrial protocol stacks or pretending unavailable hardware was tested.

## Deliverables

1. **PPS:** discover Linux PPS devices and inspect pulse observations through supported tools/APIs when available.
2. **GNSS:** support documented time observations from available NMEA/gpsd sources. Distinguish GNSS fix quality, valid time, time scale, and missing leap-second information.
3. **NTP/SNTP:** inspect installed chrony or systemd-timesyncd status read-only. Label reported offset, delay, dispersion, and source correctly.
4. **Triggers:** model SyncIn/SyncOut relationships and observe supported GPIO/event timestamps when physical signals exist. Never infer timing from unobserved wiring.
5. **CANopen SYNC/TIME:** identify relevant synchronization frames through SocketCAN with configurable identifiers and explicit timestamp provenance. Do not build a CANopen stack.
6. **EtherCAT Distributed Clocks:** inspect supported installed industrial tooling when present; otherwise report unavailable. Do not implement an EtherCAT master.
7. **Software clock mapping:** implement anchored, versioned source-to-reference mappings with offset/rate, validity intervals, uncertainty, and clock-discontinuity handling.
8. Provide one common capability/status API and simple browser presentation for all specified families, distinguishing supported, available, active, unknown, and unverified states.
9. Add deterministic fixtures/tests for each family, including missing hardware, stale references, permission denial, time-scale mismatch, drift, and clock reset.
10. Document exactly which physical functions were verified and which remain dependent on external hardware or tools.

## Scope boundary

No full EtherCAT controller, general CAN decoder, automatic system-clock management, or vendor-specific undocumented timing commands.

## Acceptance

- Every required synchronization family has meaningful capability reporting.
- Available standard Linux timing sources produce actual observations.
- Missing facilities are reported honestly, not simulated as active.
- Clock mapping precision, drift, and discontinuity tests pass.
- PTP, recording, and device discovery remain functional.
- Quality checks pass.

## Handoff

Write `docs/agent/handoffs/05.md`, update STATUS, and stop.
