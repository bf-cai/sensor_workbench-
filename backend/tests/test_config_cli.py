import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from sensor_workbench import cli
from sensor_workbench.config import Settings, load_settings


def test_xdg_default_and_explicit_overrides(tmp_path, monkeypatch):
    monkeypatch.delenv("SENSOR_WORKBENCH_CONFIG", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    assert load_settings().host == "127.0.0.1"
    assert load_settings().state_dir == tmp_path / "state/sensor-workbench"
    path = tmp_path / "custom.json"
    path.write_text(json.dumps({"port": 9000, "state_dir": str(tmp_path / "custom-state")}))
    monkeypatch.setenv("SENSOR_WORKBENCH_CONFIG", str(path))
    assert load_settings().port == 9000
    assert load_settings().state_dir == tmp_path / "custom-state"
    assert not (tmp_path / "state").exists()


@pytest.mark.parametrize("host", ["0.0.0.0", "192.168.1.1", "::", "localhost"])
def test_configuration_rejects_unauthenticated_remote_bind(host):
    with pytest.raises(ValueError):
        Settings(host=host)
    assert Settings(host="::1").host == "::1"


def test_missing_and_malformed_configuration_fail_explicitly(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_settings(tmp_path / "missing.json")
    path = tmp_path / "malformed.json"
    path.write_text("not JSON")
    with pytest.raises(ValueError):
        load_settings(path)
    path.write_text('{"unused_setting": true}')
    with pytest.raises(ValidationError):
        load_settings(path)


def test_configuration_permission_error_is_not_silently_ignored(tmp_path, monkeypatch):
    path = tmp_path / "config.json"
    def denied(*args, **kwargs):
        raise PermissionError("permission denied")
    monkeypatch.setattr(Path, "read_text", denied)
    with pytest.raises(PermissionError):
        load_settings(path)


def test_cli_version(capsys):
    cli.main(["version"])
    assert capsys.readouterr().out.strip() == "0.1.0"


def test_cli_serve_uses_validated_loopback_settings(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(cli.os, "geteuid", lambda: 1000)
    monkeypatch.delenv("SENSOR_WORKBENCH_CONFIG", raising=False)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.setattr(cli.uvicorn, "run", lambda app, **kwargs: calls.append(kwargs))
    cli.main(["serve", "--port", "9001"])
    assert calls == [{"host": "127.0.0.1", "port": 9001}]
    with pytest.raises(SystemExit):
        cli.main(["serve", "--host", "0.0.0.0"])
    assert len(calls) == 1


def test_cli_refuses_root_server(monkeypatch):
    monkeypatch.setattr(cli.os, "geteuid", lambda: 0)
    with pytest.raises(SystemExit):
        cli.main(["serve"])
