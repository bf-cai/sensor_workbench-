# Stage 02 — First Real Linux/PTP/gPTP Diagnostic Workflow

## Objective

Prove the application can observe a real Linux interface and useful PTP/gPTP evidence. Keep this stage narrow: read-only diagnostics, not a full PTP controller or recording platform.

## Deliverables

1. Implement read-only Ethernet interface inspection using documented Linux facilities such as `ip` and `ethtool` with allowlisted arguments and subprocess timeouts.
2. Report interface identity, link state, driver, speed when available, software/hardware timestamp capability, and PHC availability. Unknown fields stay unknown.
3. Detect installed `ptp4l` and other LinuxPTP tools and versions without starting or modifying them.
4. Add offline PTP/gPTP packet decoding from a small, documented PCAP/PCAPNG fixture using a maintained packet-capture reader. Decode Ethernet PTP ethertype `0x88F7` and supported UDP PTP traffic.
5. Decode common PTP header information and the messages needed for automotive gPTP: Sync, Follow_Up, Pdelay_Req, Pdelay_Resp, Pdelay_Resp_Follow_Up. Track source, sequence, profile/domain, and observation freshness.
6. Support fixed master/follower automotive gPTP without requiring Announce or BMCA.
7. Add optional read-only live PTP packet observation on a selected interface through a Linux capture mechanism. Require explicit user permission when capture capabilities are missing; do not silently invoke sudo.
8. Expose interface and PTP event endpoints through existing API conventions. Display actual interface capabilities and a live/replayed packet timeline in the browser.
9. Include fixtures/tests for no-Announce automotive gPTP, missing Follow_Up, VLAN-tagged frames, stale observations, malformed packets, software-only timestamping, and no PHC.
10. Document a safe Jetson/HAP verification procedure. If the reference hardware is available, observe live gPTP packets and record exactly what was seen. If unavailable, mark physical verification unverified.
11. Do not claim HAP follower residual clock offset, lock accuracy, or measurement alignment from master-side traffic.

## Scope boundary

Do not implement MCAP, full recording/replay, LinuxPTP process control, clock perturbation, a complete Livox driver, or general network inspection. Those belong to later stages.

## Acceptance

- Real Linux interface inspection works on the development host.
- The offline fixture decoder correctly recognizes the specified PTP/gPTP messages.
- The browser displays actual inspection data and correctly labeled PTP events.
- Optional live capture works when permissions and traffic are available; otherwise the limitation is explicit.
- Automotive no-Announce behavior is handled.
- Existing Stage 01 functionality and quality checks pass.

## Handoff

Write `docs/agent/handoffs/02.md`, distinguishing actual Linux verification, live HAP evidence, and fixture-only tests. Update STATUS and stop.
