import pytest

from sensor_workbench.adapters.simulation import PERIOD_NS, SimulatedSource


def test_simulation_is_deterministic_ten_hz_and_explicitly_labeled():
    first = SimulatedSource("fixed-run")
    second = SimulatedSource("fixed-run")
    observations = [first.observation(index) for index in range(30)]
    assert observations == [second.observation(index) for index in range(30)]
    assert observations[10].metric.value == 15_000
    assert observations[20].metric.value == 10_000
    for index, observation in enumerate(observations):
        assert observation.sequence == index
        assert observation.simulated is True
        assert observation.quality_flags == ("simulated",)
        assert observation.metric.unit == "ns"
        assert "no hardware" in observation.provenance
        assert observation.raw_timestamp.value == index * PERIOD_NS
        assert observation.raw_timestamp.clock_domain_id == first.clock_domain.id
    assert first.source.rate_hz == 10


def test_restart_creates_new_epoch_and_event_identity():
    old = SimulatedSource("old-run")
    new = SimulatedSource("new-run")
    assert old.source.id == new.source.id
    assert old.clock_domain.id != new.clock_domain.id
    assert old.observation(0).event_id != new.observation(0).event_id


@pytest.mark.parametrize("sequence", [-1, True, 1.1])
def test_invalid_sequence_is_rejected(sequence):
    with pytest.raises(ValueError):
        SimulatedSource("test").observation(sequence)
