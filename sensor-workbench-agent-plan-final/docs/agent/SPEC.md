# Product Requirements and Decisions

This is the authoritative product specification. Stage files reference it rather than repeating it.

## Goal

Build a usable, portable Linux workbench for sensor integration, synchronization, timing diagnostics, recording, reproducible experiments, and cross-sensor physical measurement-time alignment.

It is **not** a PTP-only application. It must remain extensible without building unnecessary infrastructure.

## Required workflows

1. Open a browser and inspect the Linux host, interfaces, sources, and timing status.
2. Observe actual supported synchronization mechanisms and their evidence.
3. View live measurements and correctly labeled timing metrics.
4. Record timestamped observations and relevant packet/sensor evidence.
5. Replay and compare sessions without connected hardware.
6. Run safe, repeatable experiments with documented results.
7. Estimate and evaluate relative timing between sensors where the data makes this identifiable.
8. Export results with provenance, limitations, and uncertainty.

Core operation must also be available through a documented CLI/headless path.

## Synchronization families

The architecture and capability reporting must accommodate:

- IEEE 1588 PTP.
- IEEE 802.1AS gPTP, including automotive fixed-role operation.
- PPS.
- GNSS timing references.
- NTP/SNTP.
- Hardware trigger, SyncIn, and SyncOut.
- CANopen SYNC/TIME.
- EtherCAT Distributed Clocks.
- Software mapping between independent clocks.

These are different mechanisms: clock distribution, time reference, trigger coordination, and estimated clock mapping must not be conflated.

Implement real functionality through available, documented Linux interfaces and existing tools. For hardware-dependent methods that cannot be exercised, provide meaningful capability reporting and deterministic tests; do not pretend a full industrial protocol implementation exists.

## Confirmed requirements

- Local browser UI, optionally accessible from another LAN computer.
- Linux x86-64 and ARM64/Jetson portability.
- Independent from FieldEye; never modify `/home/correct-ai/fieldeye`.
- Live plots, recording, replay, diagnostics, automated experiments, and evidence.
- Relative sensor measurement timing is more important than UTC accuracy.
- No PPS hardware, timing cable, oscilloscope, or logic analyzer required for core operation.
- Future expansion for CAN IDs/payload interpretation, but no general CAN decoder in the initial project.
- Clear code, naming, documentation, real linting, tests, stage status, and agent handoffs.
- KISS and first principles: remove work that does not directly advance the goal.
- Nine sequential implementation stages.

## Provisional defaults

Earlier choices were recommended but not explicitly submitted as confirmed:

- First-class targets: Ubuntu 22.04/24.04 and compatible Jetson Linux.
- ROS 2 optional, not required by the core.
- Timing metadata always recorded; full raw sensor recording selectable.
- Private/internal repository initially; no public license assumed.
- Functional synchronization integrations where available; capability-aware interfaces and simulation where hardware is unavailable.

Agents may use these defaults unless a safe or irreversible decision requires confirmation. Do not silently change them.

## Known reference hardware and evidence

These are historical observations, **not** universal settings or guaranteed current capabilities.

- Jetson Linux Ethernet interface `enP8p1s0`, previously `192.168.1.115`, 100 Mbps, software timestamps only, no PTP hardware clock.
- Livox HAP previously `192.168.1.211`, firmware `15.05.01.08`, behind a custom PoE switch that cannot be bypassed.
- Automotive gPTP Sync/Follow_Up and peer-delay traffic passed through the switch.
- HAP point-cloud synchronization type may remain stale after master loss; freshness must be checked separately.
- An experimental +50 ms shift to the PTP master's perceived clock produced approximately +49.930 ms HAP cloud and +49.982 ms HAP IMU timestamp responses. This proves following behavior, **not** residual clock accuracy.
- HAP SDK clock offset/last-sync queries were unsupported.
- HBK MV7-AR CAN IMU currently has host reception timestamps; physical sample-time semantics are unverified.
- Xsens Sirius GNSS/INS time semantics and a previously reported approximately 9.9 ms quantity remain unverified.
- No PPS or independent timing instrument currently available.
- PoE switch per-port telemetry is unknown.

Never hardcode historical IP addresses or interface names into general defaults.

## Explicit exclusions

- A replacement LinuxPTP, chrony, or EtherCAT master.
- General DBC/J1939/CAN payload interpretation in the initial release.
- Full SLAM, EKF, navigation, or unrelated fusion software.
- Mandatory ROS 2, Docker, CUDA, cloud services, or GPU.
- Claims of microsecond accuracy without independent measurement.
- Speculative plugin frameworks and decorative/nonfunctional UI.
- Changes to unrelated repositories.

## Product success

A user can install the workbench, observe actual available timing capabilities, inspect and record evidence, replay sessions, run safe tests, and evaluate physical measurement-time relationships without confusing synchronization status with measurement alignment.
