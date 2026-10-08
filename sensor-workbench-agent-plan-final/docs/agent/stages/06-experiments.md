# Stage 06 — Safe Automated Experiments

## Objective

Run repeatable timing experiments and produce defensible evidence, including carefully controlled PTP/gPTP operation when explicitly authorized.

## Deliverables

1. Define a small experiment contract: prerequisites, parameters, dry-run, authorization, execution, cancellation, cleanup, observations, and result.
2. Implement baseline timing observation, synchronization loss/recovery monitoring, and deterministic simulated offset/drift/packet-loss experiments.
3. Add optional supervised `ptp4l` launch/stop for a user-selected interface/profile. Show exact configuration and command in dry-run. Check for conflicting processes; never take ownership of an existing unrelated daemon.
4. Keep privileged operations separate from the unprivileged browser service, using a narrow allowlist and local authorization. Do not add a general shell-command API.
5. Do not change host system time, disable NTP, or inject physical clock shifts automatically. Process-local perturbation may remain a documented future experiment unless safely justified and separately authorized.
6. Record scenario version, environment, actions, readbacks, cleanup, observations, MCAP/PCAPNG evidence references, and limitations.
7. Calculate reproducible counts, medians, percentiles, spread, drift, freshness, and packet loss with clear units and definitions.
8. Distinguish clock offset, packet/sample arrival lag, motion-derived offset, and physical alignment residual.
9. Implement PASS, FAIL, INCONCLUSIVE, and UNVERIFIED outcomes with evidence-linked reasons.
10. Provide a simple browser experiment runner, progress view, results, and report export.
11. Test prerequisites, conflicts, cancellation, crashes, privilege failure, and cleanup.

## Scope boundary

No automatic disruptive tests, arbitrary browser commands, unsupported accuracy thresholds, or unrelated test frameworks.

## Acceptance

- A simulated experiment runs end-to-end and exports verifiable evidence.
- Pass, fail, and inconclusive outcomes are tested.
- Cancellation and cleanup work.
- Managed LinuxPTP control is available only with explicit authorization and supported permissions.
- Reports state what was measured and what cannot be inferred.
- Quality checks pass.

## Handoff

Write `docs/agent/handoffs/06.md`, update STATUS, and stop.
