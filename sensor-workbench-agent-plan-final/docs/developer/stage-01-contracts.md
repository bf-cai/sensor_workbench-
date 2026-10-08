# Stage 01 API and timing contracts

`GET /api/v1/health` returns status, package version, process `run_id`, and a null
`stream_schema` field. Its referenced type publishes the WebSocket payload in
OpenAPI, since OpenAPI does not directly describe WebSocket routes.

`GET /api/v1/sources` returns the simulated source, 10 Hz rate, clock-domain ID,
provenance, and a capability with independent supported/available/active fields
and verification state. Null booleans mean unknown. Simulation verification
covers the software generator and carries no physical hardware claim.

`GET /api/v1/clock-domains` returns the process-specific synthetic device-local
sample clock and the Linux monotonic host reception clock with OS boot identity.
No mapping between these clocks is implemented or implied.

`WS /api/v1/stream` sends version-one `StreamMessage` JSON objects with `run_id`,
`dropped_total`, and `observation`. Each observation includes source/event IDs,
sequence, a raw sample timestamp, host reception monotonic nanoseconds and boot
ID, metric, simulation label, quality flags, and provenance. Optional kernel and
userspace receive timestamps remain null unless explicitly measured.

The generator computes sample time as `sequence * 100000000` ns. Its metric
`synthetic_delay` is a triangular deterministic value between 10000 and 15000 ns.
Neither value is derived from a physical sensor or an independent clock reference.
Production uses the Linux monotonic scheduler and skips missed slots rather than
bursting historical samples after a stall.

Python stores timestamp values as integers. JSON represents them as decimal
strings to avoid rounding above JavaScript's safe integer range. Units, clock
domain, and sample/transmit/receive semantics remain explicit; the frontend
plots scalar metric values and sample sequence without converting raw epochs.
Raw models are frozen and reject unknown fields. Missing raw timestamps remain
missing. Host monotonic values require a boot identity.

The source ID is stable across reconnects. A process restart changes `run_id`,
event identity, and synthetic clock domain so a reset is not mistaken for a
continuous clock. Browsers clear their retained values when run identity changes.
Host clock identity changes on reboot, independently of application restarts.

Acquisition starts once in the FastAPI lifespan, independently of WebSockets.
At most 16 subscribers each retain at most 32 pending observations. Slow clients
drop oldest queued observations without blocking acquisition. `dropped_total`
counts evictions since that client connected; it resets on reconnect. Sequence
gaps also expose producer slots missed during scheduling stalls. Browser chart
history retains at most 300 observations. UI freshness is time since browser
reception and does not claim sample clock freshness or synchronization quality.

Foreign browser origins are rejected. Headless clients without an Origin header
are allowed on loopback. Full stream capacity closes with code 1013. Disconnect
cancels sender/receiver tasks and removes the queue; app shutdown cancels and
awaits acquisition. Configuration rejects non-loopback binds in this stage.
