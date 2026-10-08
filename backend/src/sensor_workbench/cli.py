"""Headless version and loopback server entry points."""

import argparse
import os
from pathlib import Path

import uvicorn

from sensor_workbench import __version__
from sensor_workbench.app import create_app
from sensor_workbench.config import load_settings


def main(argv: list[str] | None = None) -> None:
    """Parse CLI arguments and run the server or print the package version.

    Args:
        argv: Explicit argument list for tests; None reads process arguments.

    Raises:
        SystemExit: Invalid configuration, missing command, or root server use.
    """
    parser = argparse.ArgumentParser(prog="sensor-workbench")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("version", help="Print package version")
    serve = commands.add_parser("serve", help="Serve the local UI and API")
    serve.add_argument("--config", type=Path, help="Explicit JSON configuration file")
    serve.add_argument("--host", help="Loopback IP address (default 127.0.0.1)")
    serve.add_argument("--port", type=int, help="Port (default 8765)")
    serve.add_argument("--static-dir", type=Path, help="Compiled Vite assets directory")
    arguments = parser.parse_args(argv)
    if arguments.command == "version":
        print(__version__)
        return
    if os.geteuid() == 0:
        parser.error("Run the workbench as an unprivileged user")
    try:
        settings = load_settings(arguments.config)
        overrides = {
            name: getattr(arguments, name)
            for name in (
                "host",
                "port",
                "static_dir",
            )
            if getattr(arguments, name) is not None
        }
        settings = type(settings).model_validate(settings.model_dump() | overrides)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    uvicorn.run(create_app(settings), host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
