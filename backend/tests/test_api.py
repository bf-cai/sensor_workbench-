"""Exercise the actual ASGI app without an external HTTP client dependency."""

import asyncio
import json
from pathlib import Path

from sensor_workbench.api.generate_types import generate_types
from sensor_workbench.app import create_app
from sensor_workbench.config import Settings
from sensor_workbench.core.models import StreamMessage


async def http_request(app, path):
    sent = []
    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}
    async def send(message):
        sent.append(message)
    await app({
        "type": "http", "asgi": {"version": "3.0", "spec_version": "2.4"}, "http_version": "1.1",
        "method": "GET", "scheme": "http", "path": path, "raw_path": path.encode(),
        "query_string": b"", "root_path": "", "headers": [(b"host", b"localhost")],
        "server": ("localhost", 8765), "client": ("localhost", 12345),
    }, receive, send)
    status = sent[0]["status"]
    body = b"".join(message.get("body", b"") for message in sent[1:])
    return status, body


async def websocket_session(app, origin=None):
    incoming = asyncio.Queue()
    outgoing = asyncio.Queue()
    await incoming.put({"type": "websocket.connect"})
    headers = [(b"host", b"localhost:8765")]
    if origin is not None:
        headers.append((b"origin", origin.encode()))
    scope = {
        "type": "websocket", "asgi": {"version": "3.0"}, "scheme": "ws",
        "path": "/api/v1/stream", "raw_path": b"/api/v1/stream", "root_path": "",
        "query_string": b"", "headers": headers, "subprotocols": [],
        "server": ("localhost", 8765), "client": ("localhost", 12345),
    }
    task = asyncio.create_task(app(scope, incoming.get, outgoing.put))
    return incoming, outgoing, task


def test_baseline_http_metadata_and_missing_assets(tmp_path):
    async def scenario():
        app = create_app(Settings(static_dir=tmp_path))
        async with app.router.lifespan_context(app):
            status, body = await http_request(app, "/api/v1/health")
            health = json.loads(body)
            assert status == 200 and health["status"] == "ok"
            assert health["version"] == "0.1.0"
            status, body = await http_request(app, "/api/v1/sources")
            sources = json.loads(body)
            assert status == 200 and len(sources) == 1
            assert sources[0]["simulated"] is True
            assert sources[0]["capabilities"][0]["active"] is True
            status, body = await http_request(app, "/api/v1/clock-domains")
            clocks = json.loads(body)
            assert status == 200
            assert sources[0]["clock_domain_id"] == clocks[0]["id"]
            assert clocks[1]["timescale"] == "HOST_MONOTONIC"
            assert clocks[1]["boot_id"]
            assert (await http_request(app, "/"))[0] == 503
            assert (await http_request(app, "/api/v1/nonexistent"))[0] == 404
        assert app.state.acquisition.task is None
    asyncio.run(scenario())


def test_websocket_messages_reconnect_identity_and_cleanup():
    async def scenario():
        app = create_app()
        async with app.router.lifespan_context(app):
            received = []
            for _ in range(2):
                incoming, outgoing, task = await websocket_session(app, "http://localhost:8765")
                assert (await asyncio.wait_for(outgoing.get(), 1))["type"] == "websocket.accept"
                payload = await asyncio.wait_for(outgoing.get(), 1)
                assert payload["type"] == "websocket.send"
                message = StreamMessage.model_validate_json(payload["text"])
                assert message.observation.simulated
                assert message.observation.raw_timestamp.unit == "ns"
                assert message.observation.host_receive_monotonic_ns is not None
                assert message.dropped_total == 0
                received.append(message)
                await incoming.put({"type": "websocket.disconnect", "code": 1000})
                await asyncio.wait_for(task, 1)
                assert not app.state.acquisition.subscriptions
            assert received[0].run_id == received[1].run_id
            assert received[0].observation.source_id == received[1].observation.source_id
            assert received[1].observation.sequence > received[0].observation.sequence
        assert app.state.acquisition.task is None
    asyncio.run(scenario())


def test_foreign_browser_origin_is_rejected():
    async def scenario():
        app = create_app()
        incoming, outgoing, task = await websocket_session(app, "https://untrusted.example")
        message = await asyncio.wait_for(outgoing.get(), 1)
        assert message == {"type": "websocket.close", "code": 1008, "reason": ""}
        await asyncio.wait_for(task, 1)
        assert not app.state.acquisition.subscriptions
    asyncio.run(scenario())


def test_stream_limit_returns_retryable_close():
    async def scenario():
        app = create_app()
        service = app.state.acquisition
        service.max_subscribers = 1
        held = service.subscribe()
        incoming, outgoing, task = await websocket_session(app)
        assert (await asyncio.wait_for(outgoing.get(), 1))["type"] == "websocket.accept"
        assert (await asyncio.wait_for(outgoing.get(), 1))["code"] == 1013
        await asyncio.wait_for(task, 1)
        service.unsubscribe(held)
    asyncio.run(scenario())


def test_built_index_and_assets_are_served(tmp_path):
    (tmp_path / "assets").mkdir()
    (tmp_path / "index.html").write_text("<html>fixture</html>")
    (tmp_path / "assets/test.js").write_text("console.log('fixture')")
    async def scenario():
        app = create_app(Settings(static_dir=tmp_path))
        async with app.router.lifespan_context(app):
            assert await http_request(app, "/") == (200, b"<html>fixture</html>")
            assert await http_request(app, "/assets/test.js") == (200, b"console.log('fixture')")
            assert (await http_request(app, "/assets/../../config.py"))[0] == 404
    asyncio.run(scenario())


def test_openapi_and_generated_contracts_are_current():
    schemas = create_app().openapi()["components"]["schemas"]
    assert schemas["Timestamp"]["properties"]["value"]["type"] == "string"
    assert "StreamMessage" in schemas
    root = Path(__file__).resolve().parents[2]
    assert (root / "web/src/api/generated.ts").read_text() == generate_types()
