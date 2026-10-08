UV ?= uv
NPM ?= npm

.PHONY: bootstrap lock format format-check format-python format-web lint lint-python lint-web lint-other typecheck typecheck-python typecheck-web check-api generate-api test test-python test-web build build-python build-web quality serve

bootstrap:
	$(UV) sync --project backend --locked
	cd web && $(NPM) ci

# Deliberately separate from bootstrap: normal installs must not rewrite locks.
lock:
	$(UV) lock --project backend
	cd web && $(NPM) install --package-lock-only

format:
	$(UV) run --project backend --locked ruff format backend
	$(UV) run --project backend --locked ruff check --fix backend
	cd web && $(NPM) run format

format-check: format-python format-web
format-python:
	$(UV) run --project backend --locked ruff format --check backend
format-web:
	cd web && $(NPM) run format-check

lint: lint-python lint-web lint-other
lint-python:
	$(UV) run --project backend --locked ruff check backend
lint-web:
	cd web && $(NPM) run lint
lint-other:
	$(UV) run --project backend --locked python backend/check_file_types.py

typecheck: typecheck-python typecheck-web check-api
typecheck-python:
	cd backend && $(UV) run --locked mypy src/sensor_workbench check_file_types.py
typecheck-web:
	cd web && $(NPM) run typecheck
check-api:
	$(UV) run --project backend --locked python -m sensor_workbench.api.generate_types --output web/src/api/generated.ts --check
generate-api:
	$(UV) run --project backend --locked python -m sensor_workbench.api.generate_types --output web/src/api/generated.ts

test: test-python test-web
test-python:
	cd backend && PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $(UV) run --locked pytest
test-web:
	cd web && $(NPM) run test

build: build-python
build-web:
	cd web && $(NPM) run build
build-python: build-web
	$(UV) build --project backend --out-dir dist

quality: format-check lint typecheck test build

serve:
	$(UV) run --project backend --locked sensor-workbench serve
