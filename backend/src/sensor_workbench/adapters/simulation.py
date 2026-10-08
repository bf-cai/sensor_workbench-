"""Deterministic 10 Hz synthetic sample and delay generator."""

from sensor_workbench.core.models import (
    Capability,
    ClockDomain,
    Metric,
    Observation,
    Source,
    Timescale,
    Timestamp,
)

SOURCE_ID = "simulated-timing"
PERIOD_NS = 100_000_000
PROVENANCE = "Deterministic triangular synthetic delay; no hardware measurement"


class SimulatedSource:
    """Generate values from sequence only, in a per-run device-local clock.

    Args:
        run_id: Process identity; distinguishes clock resets across restarts.
    """

    def __init__(self, run_id: str) -> None:
        """Set source and clock identity without starting acquisition."""
        self.run_id = run_id
        self.clock_domain = ClockDomain(
            id=f"simulation:{run_id}",
            owner=SOURCE_ID,
            timescale=Timescale.DEVICE_LOCAL,
            epoch_description="Synthetic sample zero at process acquisition start",
            resolution_ns=1,
        )
        self.source = Source(
            id=SOURCE_ID,
            name="Simulated timing source",
            clock_domain_id=self.clock_domain.id,
            simulated=True,
            rate_hz=10.0,
            provenance=PROVENANCE,
            capabilities=(
                Capability(
                    owner=SOURCE_ID,
                    method_family="simulation",
                    evidence=PROVENANCE,
                    supported=True,
                    available=True,
                    active=True,
                    verification="verified",
                ),
            ),
        )

    def observation(self, sequence: int) -> Observation:
        """Return deterministic raw sample time and synthetic delay in nanoseconds.

        Args:
            sequence: Nonnegative sample slot, spaced 100,000,000 ns apart.

        Returns:
            Simulated observation without host reception time or clock mapping.

        Raises:
            ValueError: If sequence is negative or not an integer.
        """
        if type(sequence) is not int or sequence < 0:
            raise ValueError("sequence must be a nonnegative integer")
        phase = sequence % 20
        delay_ns = 10_000 + 500 * (phase if phase <= 10 else 20 - phase)
        return Observation(
            event_id=f"{self.run_id}:{sequence}",
            source_id=SOURCE_ID,
            sequence=sequence,
            raw_timestamp=Timestamp(
                value=sequence * PERIOD_NS,
                unit="ns",
                clock_domain_id=self.clock_domain.id,
                semantics="sample",
            ),
            metric=Metric(name="synthetic_delay", value=float(delay_ns), unit="ns"),
            simulated=True,
            provenance=PROVENANCE,
            quality_flags=("simulated",),
        )
