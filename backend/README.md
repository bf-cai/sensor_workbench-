# Sensor Workbench backend

The `sensor-workbench` wheel includes the compiled browser UI and serves it with
the local FastAPI API. Run `sensor-workbench serve` as an ordinary Linux user;
the default URL is <http://127.0.0.1:8765>. `sensor-workbench version` prints the
installed version. No sensors or GPU are required for the simulated source.

For development, run `make bootstrap`, `make quality`, and `make serve` from the
application repository root (the parent of this directory). See its README for
configuration, API contracts, SSH tunneling, and troubleshooting. Build the UI
before packaging the backend: `make build` performs both steps.
