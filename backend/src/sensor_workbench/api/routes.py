"""Baseline HTTP metadata and a bounded WebSocket observation stream."""

import asyncio
from contextlib import suppress

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from sensor_workbench import __version__
from sensor_workbench.core.models import ClockDomain, Health, Source
from sensor_workbench.services.acquisition import Acquisition, Subscription


async def _send_stream(
    websocket: WebSocket, acquisition: Acquisition, subscription: Subscription,
) -> None:
    while True:
        message = await subscription.next_message(acquisition.source.run_id)
        await websocket.send_text(message.model_dump_json())


async def _wait_disconnect(websocket: WebSocket) -> None:
    while True:
        message = await websocket.receive()
        if message["type"] == "websocket.disconnect":
            return


def create_router(acquisition: Acquisition, host_clock: ClockDomain) -> APIRouter:
    """Expose one acquisition service; lifetime is controlled by the app lifespan.

    Args:
        acquisition: Running bounded simulation service.
        host_clock: Boot-specific Linux monotonic reception clock domain.

    Returns:
        Router with versioned health, source, clock, and WebSocket routes.
    """
    router = APIRouter(prefix="/api/v1")

    @router.get("/health", response_model=Health)
    async def health() -> Health:
        return Health(version=__version__, run_id=acquisition.source.run_id)

    @router.get("/sources", response_model=list[Source])
    async def sources() -> list[Source]:
        return [acquisition.source.source]

    @router.get("/clock-domains", response_model=list[ClockDomain])
    async def clock_domains() -> list[ClockDomain]:
        return [acquisition.source.clock_domain, host_clock]

    @router.websocket("/stream")
    async def stream(websocket: WebSocket) -> None:
        # Restrict browser origins as well as bind address: hostile websites can
        # otherwise connect to a user's unauthenticated localhost WebSocket.
        origin = websocket.headers.get("origin")
        host = websocket.headers.get("host")
        if origin and origin not in (f"http://{host}", f"https://{host}"):
            await websocket.close(code=1008)
            return
        await websocket.accept()
        try:
            subscription = acquisition.subscribe()
        except RuntimeError:
            await websocket.close(code=1013)
            return
        tasks = [
            asyncio.create_task(_send_stream(websocket, acquisition, subscription)),
            asyncio.create_task(_wait_disconnect(websocket)),
        ]
        try:
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                task.result()
        except (WebSocketDisconnect, RuntimeError):
            pass
        finally:
            for task in tasks:
                task.cancel()
            for task in tasks:
                with suppress(asyncio.CancelledError, WebSocketDisconnect, RuntimeError):
                    await task
            acquisition.unsubscribe(subscription)

    return router
