# Sensor Workbench

A local Linux sensor timing workbench. Stage 01 implements a FastAPI backend,
headless CLI, and React overview with live ECharts data from a deterministic
10 Hz simulated source. Every observation carries simulation provenance, units,
and a clock domain. Synthetic delay is not a hardware accuracy measurement.

See [STATUS](sensor-workbench-agent-plan-final/docs/agent/STATUS.md) and the
[Stage 01 handoff](sensor-workbench-agent-plan-final/docs/agent/handoffs/01.md)
for acceptance results and the next stage.

## Requirements and installation

Use Linux x86-64 or ARM64, Python 3.10+, uv, and Node 22.13+ with npm during
frontend development/build. Sensors, root, ROS 2, CUDA, and a GPU are unnecessary.
Node is unnecessary when running an installed Python wheel containing compiled
frontend assets. Run the service as an ordinary user.

Run commands from the repository root containing `Makefile`, `backend/`, and
`web/`. Agent and developer documents remain under
`sensor-workbench-agent-plan-final/docs/`. With uv and Node/npm on your PATH:

```bash
make bootstrap
make quality
make serve
```

For setup without development checks, run `make bootstrap`, `make build`, then
`make serve`. Bootstrap uses `uv sync --locked` and `npm ci`. Both lockfiles are
retained in source. Dependency downloads require access to PyPI and the npm
registry; later runs can reuse cached packages. Run `make lock` only when
intentionally updating dependencies, then rerun the quality checks.

To run the built wheel in a separate environment:

```bash
uv venv /tmp/sensor-workbench-run
uv pip install --python /tmp/sensor-workbench-run/bin/python dist/sensor_workbench-0.1.0-py3-none-any.whl
/tmp/sensor-workbench-run/bin/sensor-workbench serve
```

Open <http://127.0.0.1:8765>. The backend serves the compiled frontend. The overview
shows source metadata, synthetic delay in nanoseconds, raw sample time, sequence,
queue loss, and process run identity. It retains at most 300 observations and
marks data stale after two seconds without reception.

## Headless operation

```bash
uv run --project backend --locked sensor-workbench version
uv run --project backend --locked sensor-workbench serve --port 8765
curl http://127.0.0.1:8765/api/v1/health
curl http://127.0.0.1:8765/api/v1/sources
curl http://127.0.0.1:8765/api/v1/clock-domains
```

Where FastAPI, Pydantic v2, Uvicorn, and websockets are already available, the
source CLI can also run without installing the package:

```bash
PYTHONPATH=backend/src python3 -m sensor_workbench.cli version
PYTHONPATH=backend/src python3 -m sensor_workbench.cli serve
```

The API operates without compiled UI assets; `/` returns HTTP 503 with the build
command until assets exist. Stop with Ctrl+C or SIGTERM; shutdown awaits producer
cancellation and closes WebSocket tasks.

## Configuration and remote viewing

The optional JSON file is
`$XDG_CONFIG_HOME/sensor-workbench/config.json`, defaulting to
`~/.config/sensor-workbench/config.json`. No file or directory is automatically
created. Override with `SENSOR_WORKBENCH_CONFIG` or `serve --config PATH`.
CLI options `--host`, `--port`, and `--static-dir` override file settings.

```json
{
  "host": "127.0.0.1",
  "port": 8765,
  "state_dir": "/home/your-user/.local/state/sensor-workbench"
}
```

State defaults to `$XDG_STATE_HOME/sensor-workbench`, or
`~/.local/state/sensor-workbench`; Stage 01 writes no persistent state. `static_dir`
defaults to the package's compiled `static` directory. Unknown settings, malformed
JSON, unreadable explicit files, invalid ports, and non-loopback binds fail.

To view a workbench on another computer, keep its loopback listener and tunnel:

```bash
ssh -N -L 8765:127.0.0.1:8765 your-user@workbench-host
```

Then open <http://127.0.0.1:8765> on your computer. Direct LAN binds are unavailable
until authenticated remote access is implemented.

## Development and quality

```bash
make format-check
make lint
make typecheck
make test
make build
make quality
```

These targets execute Ruff formatter/linter, strict mypy, pytest, Prettier,
TypeScript ESLint, strict TypeScript, Vitest, markdownlint-cli2, and Vite plus a
Python distribution build. `make typecheck` also checks generated OpenAPI types.
Other language checks visibly skip only absent file types and run real tools
when applicable. `make -k quality` collects independent failures.

For development, start the backend on port 8765 and, in a second terminal, run:

```bash
cd web
npm run dev
```

Use the Vite loopback URL; its `/api` proxy supports WebSockets and preserves
same-origin browser headers. Production `make build` compiles assets into
`backend/src/sensor_workbench/static` and builds a wheel/sdist in `dist`.

Regenerate API types with `make generate-api`. The generator reads FastAPI's
OpenAPI serialization schemas, including the stream schema referenced by health,
and fails explicitly for unsupported schema constructs. Generated decimal-string
timestamp types preserve epoch nanoseconds in JavaScript. No implicit clock
conversion occurs. See [API contracts](sensor-workbench-agent-plan-final/docs/developer/stage-01-contracts.md).

To run the available system pytest without dependency installation:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=backend/src python3 -m pytest backend/tests -q
```

The quality targets require the locked tool environment. Disabling third-party pytest autoload keeps
unrelated installed ROS plugins out of the core test suite.

## Troubleshooting

- **UI HTTP 503:** run `make build`; for external assets use `serve --static-dir PATH`.
- **Dependency tools missing:** provision uv and Node/npm for your architecture;
  ensure their executables are on PATH, then run `make bootstrap`.
- **DNS/download failure:** restore permitted dependency access and rerun `make bootstrap`.
- **Port occupied:** choose another loopback port with `serve --port 9000`.
- **Reconnecting/stale:** inspect backend logs and API health. The browser reconnects
  with a bounded backoff; restart creates a new run/clock identity and clears the plot.
- **Queue loss:** `dropped_total` counts queue evictions for the current connection;
  sequence gaps can also indicate scheduler stalls. Acquisition continues without browsers.
- **Permission/configuration error:** check the explicitly selected JSON file;
  the service never replaces unreadable configuration with silent defaults.

## Agent documentation

- [AGENTS.md](AGENTS.md): one-stage execution procedure.
- [STATUS.md](sensor-workbench-agent-plan-final/docs/agent/STATUS.md): authoritative current stage.
- [SPEC.md](sensor-workbench-agent-plan-final/docs/agent/SPEC.md): product requirements and retained decisions.
- [RULES.md](sensor-workbench-agent-plan-final/docs/agent/RULES.md): engineering standards and safety.
- [ARCHITECTURE.md](sensor-workbench-agent-plan-final/docs/agent/ARCHITECTURE.md): shared contracts and boundaries.
- [Stages](sensor-workbench-agent-plan-final/docs/agent/stages/): sequential tasks.
- [Handoffs](sensor-workbench-agent-plan-final/docs/agent/handoffs/): factual results and next-agent instructions.
