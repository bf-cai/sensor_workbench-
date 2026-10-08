# Stage 07 — Complete Browser Workbench

## Objective

Make the implemented diagnostic, recording, replay, and experiment workflows convenient and dependable through the browser.

## Deliverables

1. Organize functional screens for Overview, Devices, Synchronization, Sessions, Experiments, and Analysis.
2. Provide consistent navigation, responsive layout, accessible controls, loading/error states, and clear terminology.
3. Add live/historical timing charts with filtering, zoom, linked cursors, histograms, time-window selection, and annotations.
4. Show clock relationships, source freshness, actual synchronization status, unsupported capabilities, and uncertainty.
5. Complete session recording controls, replay timeline, comparisons, evidence links, and exports.
6. Use bounded client buffers and server-side aggregation/downsampling. Never push full LiDAR packets through chart JSON.
7. Handle device removal, WebSocket reconnection, stale data, insufficient permissions, and unavailable tools.
8. Implement optional authenticated LAN access, with a documented secure deployment path. Keep loopback the default; avoid exposing unauthenticated control endpoints.
9. Add Playwright end-to-end tests for the supported user workflows, plus frontend unit tests and production build verification.
10. Document routine user operations using actual commands and actual UI behavior.

## Scope boundary

No decorative dashboards, nonfunctional controls, duplicated frontend timing algorithms, or unrelated customization.

## Acceptance

- Routine supported workflows work through the browser.
- All visible controls are functional or clearly disabled with an explanation.
- Live and replay data are distinguishable.
- Plots show correct units, timestamp domains, and unknown states.
- Authenticated LAN behavior and localhost defaults are tested.
- Playwright, build, and quality checks pass.

## Handoff

Write `docs/agent/handoffs/07.md`, update STATUS, and stop.
