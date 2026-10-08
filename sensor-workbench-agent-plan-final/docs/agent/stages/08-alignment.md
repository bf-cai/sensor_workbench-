# Stage 08 — Cross-Sensor Temporal Alignment Evaluation

## Objective

Estimate and validate physical measurement-time relationships where recorded sensor signals contain enough information. Do not confuse clock synchronization with sample alignment.

## Deliverables

1. Define analysis inputs: source streams, timestamp semantics, reference domain, interval, optional extrinsics, and algorithm parameters.
2. Implement a documented robust cross-correlation or fitting method for fixed offset using comparable motion signals.
3. Estimate relative clock drift only when duration and signal excitation make it identifiable.
4. Distinguish fixed bias, drift, timestamp jitter, network/host arrival latency, and spatial calibration mismatch.
5. Use anchored time coordinates for numerical stability; do not regress floating-point epoch nanoseconds directly.
6. Handle missing samples, uneven sampling, gaps, outliers, clock resets, and insufficient motion.
7. Version derived clock/time mappings; never modify raw recorded timestamps.
8. Split fitting and held-out evaluation intervals. Report both results and uncertainty/identifiability limits.
9. Show before/after signals, estimated lag, residuals, uncertainty, and warnings in the browser.
10. Test synthetic known positive/negative offsets, 10 ms and 50 ms shifts, drift, jitter, missing samples, and unidentifiable cases.
11. Support real recorded motion signals when their timestamp and physical semantics are documented. If suitable real streams are absent, report physical fusion validation as unverified rather than fabricating a demonstration.

## Scope boundary

No SLAM, EKF, full point-cloud processing suite, or universal accuracy promises.

## Acceptance

- Synthetic offsets and drift are recovered within justified, documented tolerances.
- Held-out validation is demonstrated.
- Insufficient-information cases return inconclusive results.
- Raw evidence remains immutable.
- Analysis results clearly separate clock mapping from physical alignment.
- Quality checks pass.

## Handoff

Write `docs/agent/handoffs/08.md`, update STATUS, and stop.
