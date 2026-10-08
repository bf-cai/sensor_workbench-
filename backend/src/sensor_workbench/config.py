"""Read-only XDG configuration; loopback is the only allowed stage-one bind."""

import ipaddress
import json
import os
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Settings(BaseModel):
    """Server configuration from an explicit or XDG JSON file.

    Loading does not create directories or overwrite configuration. state_dir
    reserves an XDG state location but Stage 01 writes no recordings or database.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)
    host: str = "127.0.0.1"
    port: int = Field(default=8765, ge=1, le=65535, strict=True)
    state_dir: Path = Field(
        default_factory=lambda: (
            Path(
                os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state")),
            )
            / "sensor-workbench"
        )
    )
    static_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "static")

    @field_validator("host")
    @classmethod
    def require_loopback(cls, value: str) -> str:
        """Reject non-loopback binds until authenticated remote access exists."""
        if not ipaddress.ip_address(value).is_loopback:
            raise ValueError("Only a loopback IP is permitted; use an SSH tunnel")
        return value


def load_settings(config_path: Path | None = None) -> Settings:
    """Read settings from explicit path, environment override, or optional XDG file.

    Args:
        config_path: Explicit JSON file; it must exist when provided.

    Returns:
        Validated configuration without filesystem writes.

    Raises:
        OSError: Explicit file is missing, unreadable, or inaccessible.
        ValueError: JSON or settings are invalid.
    """
    override = os.environ.get("SENSOR_WORKBENCH_CONFIG")
    explicit = config_path is not None or override is not None
    path = config_path or (
        Path(override)
        if override
        else Path(
            os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")),
        )
        / "sensor-workbench/config.json"
    )
    if not explicit and not path.exists():
        return Settings()
    return Settings.model_validate(json.loads(path.read_text(encoding="utf-8")))
