"""FastAPI application factory with acquisition lifespan and compiled UI assets."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from sensor_workbench import __version__
from sensor_workbench.adapters.simulation import SimulatedSource
from sensor_workbench.api.routes import create_router
from sensor_workbench.config import Settings, load_settings
from sensor_workbench.core.models import ClockDomain, Timescale
from sensor_workbench.services.acquisition import Acquisition


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the Linux app without starting background tasks or altering devices.

    Args:
        settings: Validated settings; otherwise read the optional XDG config.

    Returns:
        ASGI application. Its lifespan starts and cleanly cancels acquisition.

    Raises:
        OSError: Linux boot identity cannot be read.
        ValueError: Configuration is invalid.
    """
    settings = settings or load_settings()
    boot_id = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    source = SimulatedSource(str(uuid4()))
    acquisition = Acquisition(source, boot_id)
    host_clock = ClockDomain(
        id=f"host-monotonic:{boot_id}", owner="host",
        timescale=Timescale.HOST_MONOTONIC,
        epoch_description="Linux CLOCK_MONOTONIC epoch for this boot",
        boot_id=boot_id,
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        acquisition.start()
        try:
            yield
        finally:
            await acquisition.stop()

    app = FastAPI(title="Sensor Workbench", version=__version__, lifespan=lifespan)
    app.state.acquisition = acquisition
    app.include_router(create_router(acquisition, host_clock))
    static_dir = settings.static_dir.resolve()
    if (static_dir / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")

    @app.get("/", include_in_schema=False)
    async def overview() -> FileResponse:
        index = static_dir / "index.html"
        if not index.is_file():
            raise HTTPException(503, "UI assets are missing; run make build")
        return FileResponse(index)

    return app
