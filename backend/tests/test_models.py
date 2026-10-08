import json

import pytest
from pydantic import ValidationError

from sensor_workbench.adapters.simulation import SimulatedSource
from sensor_workbench.core.models import ClockDomain, Observation, Timescale, Timestamp


def test_timestamp_roundtrip_keeps_epoch_nanoseconds_exact():
    value = 1_790_000_000_123_456_789
    timestamp = Timestamp(value=value, unit="ns", clock_domain_id="utc", semantics="sample")
    encoded = timestamp.model_dump_json()
    assert json.loads(encoded)["value"] == str(value)
    assert Timestamp.model_validate_json(encoded).value == value
    assert timestamp.value == value


@pytest.mark.parametrize("value", [1.5, True, "1.5", "1e9", "--12", "", "１２"])
def test_timestamp_rejects_noninteger_values(value):
    with pytest.raises(ValidationError):
        Timestamp(value=value, unit="ns", clock_domain_id="clock", semantics="sample")


def test_clock_domains_keep_identity_and_require_boot_id():
    first = ClockDomain(id="one", owner="a", timescale=Timescale.DEVICE_LOCAL, epoch_description="start")
    second = first.model_copy(update={"id": "two"})
    assert first != second
    with pytest.raises(ValidationError, match="boot_id"):
        ClockDomain(id="host", owner="host", timescale=Timescale.HOST_MONOTONIC, epoch_description="boot")


def test_raw_evidence_is_immutable_and_missing_sample_time_stays_missing():
    observation = SimulatedSource("test").observation(0)
    with pytest.raises(ValidationError):
        observation.simulated = False
    missing = observation.model_copy(update={"raw_timestamp": None})
    assert Observation.model_validate_json(missing.model_dump_json()).raw_timestamp is None
    invalid = observation.model_dump() | {"host_receive_monotonic_ns": 10}
    with pytest.raises(ValidationError, match="host_boot_id"):
        Observation.model_validate(invalid)


def test_reception_timestamp_and_boot_identity_roundtrip():
    observation = SimulatedSource("test").observation(4).model_copy(update={
        "host_receive_monotonic_ns": 9_007_199_254_740_993, "host_boot_id": "boot",
    })
    decoded = Observation.model_validate_json(observation.model_dump_json())
    assert decoded.host_receive_monotonic_ns == 9_007_199_254_740_993
    assert decoded.raw_timestamp.value == 400_000_000
    assert decoded.host_boot_id == "boot"
