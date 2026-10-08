"""Real loopback HTTP/WebSocket smoke test, with graceful process cleanup."""

import asyncio
import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from websockets.asyncio.client import connect


def test_real_cli_server_streams_and_shuts_down(tmp_path):
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    source_path = Path(__file__).resolve().parents[1] / "src"
    environment = os.environ | {"PYTHONPATH": str(source_path)}
    log_path = tmp_path / "server.log"
    with log_path.open("w") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "sensor_workbench.cli",
                "serve",
                "--port",
                str(port),
            ],
            env=environment,
            stdout=log,
            stderr=log,
        )
        try:
            health = None
            deadline = time.monotonic() + 10
            while time.monotonic() < deadline:
                try:
                    with urllib.request.urlopen(
                        f"http://127.0.0.1:{port}/api/v1/health", timeout=1
                    ) as response:
                        health = json.load(response)
                    break
                except urllib.error.URLError:
                    assert process.poll() is None, log_path.read_text()
                    time.sleep(0.05)
            assert health is not None, "Server did not become healthy"
            assert health["status"] == "ok"

            async def receive_stream():
                messages = []
                async with connect(f"ws://127.0.0.1:{port}/api/v1/stream") as websocket:
                    for _ in range(6):
                        messages.append(
                            json.loads(await asyncio.wait_for(websocket.recv(), 2))
                        )
                async with connect(f"ws://127.0.0.1:{port}/api/v1/stream") as websocket:
                    reconnect = json.loads(await asyncio.wait_for(websocket.recv(), 2))
                assert all(item["run_id"] == health["run_id"] for item in messages)
                assert all(item["observation"]["simulated"] for item in messages)
                first = messages[0]["observation"]
                last = messages[-1]["observation"]
                sequence_delta = last["sequence"] - first["sequence"]
                assert sequence_delta >= 5
                assert (
                    int(last["raw_timestamp"]["value"])
                    - int(first["raw_timestamp"]["value"])
                    == sequence_delta * 100_000_000
                )
                assert reconnect["observation"]["sequence"] > last["sequence"]
                assert reconnect["run_id"] == health["run_id"]
                assert reconnect["dropped_total"] == 0

            asyncio.run(receive_stream())
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
                raise AssertionError("Server did not shut down gracefully") from None
    # Uvicorn restores and re-raises SIGTERM after completing lifespan shutdown.
    assert process.returncode in (0, -signal.SIGTERM), log_path.read_text()
    assert "Application shutdown complete" in log_path.read_text()
