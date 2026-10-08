"""Immutable version-one timing contracts with explicit clock identity and units."""

from enum import Enum
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
    WithJsonSchema,
    model_validator,
)


def _parse_integer(value: object) -> int:
    if type(value) is int:
        return value
    if isinstance(value, str) and value.lstrip("-").isascii():
        if value.isdecimal() or (value.startswith("-") and value[1:].isdecimal()):
            return int(value)
    raise ValueError("Timestamp must be an integer or a decimal integer string")


# Decimal strings on the wire avoid loss above JavaScript's 2**53 integer limit.
ExactInteger = Annotated[
    int,
    BeforeValidator(_parse_integer),
    PlainSerializer(str, return_type=str, when_used="json"),
    WithJsonSchema({"type": "string", "pattern": "^-?[0-9]+$"}, mode="serialization"),
]


class Contract(BaseModel):
    """Reject unknown fields and prevent mutation of validated raw evidence."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class Timescale(str, Enum):
    """Time scale names; their presence does not imply a clock conversion."""

    UTC = "UTC"
    TAI = "TAI"
    GPS = "GPS"
    PTP = "PTP"
    HOST_MONOTONIC = "HOST_MONOTONIC"
    DEVICE_LOCAL = "DEVICE_LOCAL"
    DEVICE_TICKS = "DEVICE_TICKS"
    UNKNOWN = "UNKNOWN"


class ClockDomain(Contract):
    """Identify a clock epoch, including boot identity for host monotonic clocks."""

    id: str = Field(min_length=1)
    owner: str = Field(min_length=1)
    timescale: Timescale
    epoch_description: str = Field(min_length=1)
    tick_rate_hz: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    resolution_ns: int | None = Field(default=None, gt=0, strict=True)
    boot_id: str | None = None

    @model_validator(mode="after")
    def require_boot_identity(self) -> "ClockDomain":
        """Reject host monotonic clock domains lacking an OS boot identity."""
        if self.timescale == Timescale.HOST_MONOTONIC and not self.boot_id:
            raise ValueError("Host monotonic clocks require boot_id")
        return self


class Timestamp(Contract):
    """Preserve an integer raw timestamp without converting units or epochs.

    JSON encodes value as a decimal string for lossless JavaScript transport.
    The declared unit and clock_domain_id must always accompany the value.
    """

    value: ExactInteger
    unit: Literal["ns", "us", "ms", "s", "ticks"]
    clock_domain_id: str = Field(min_length=1)
    semantics: Literal[
        "sample",
        "first_point",
        "last_point",
        "exposure_start",
        "exposure_end",
        "trigger",
        "transmit",
        "receive",
        "unknown",
    ]


class Metric(Contract):
    """A finite scalar with explicit units; simulation is indicated by its parent."""

    name: str = Field(min_length=1)
    value: float = Field(allow_inf_nan=False)
    unit: str = Field(min_length=1)


class Observation(Contract):
    """Raw observation; reception time is separate from the sample clock.

    host_receive_monotonic_ns uses the Linux monotonic clock and requires the
    boot ID. Missing sample timestamps remain missing. No derived time mapping
    is performed. Provenance and simulation labels travel with every event.
    """

    schema_version: Literal[1] = 1
    event_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    sequence: int | None = Field(default=None, ge=0, strict=True)
    kind: Literal["metric"] = "metric"
    raw_timestamp: Timestamp | None = None
    host_receive_monotonic_ns: ExactInteger | None = None
    host_boot_id: str | None = None
    kernel_receive_timestamp: Timestamp | None = None
    userspace_receive_timestamp: Timestamp | None = None
    metric: Metric
    quality_flags: tuple[str, ...] = ()
    simulated: bool
    provenance: str = Field(min_length=1)

    @model_validator(mode="after")
    def require_receive_boot_identity(self) -> "Observation":
        """Require a boot ID whenever host reception nanoseconds are provided."""
        if self.host_receive_monotonic_ns is not None and not self.host_boot_id:
            raise ValueError("Host reception time requires host_boot_id")
        return self


class Capability(Contract):
    """Separate support, availability, activity, and evidence verification.

    None means unknown, never false or a zero uncertainty estimate.
    """

    owner: str
    method_family: Literal["simulation"]
    prerequisites: tuple[str, ...] = ()
    evidence: str
    supported: bool | None
    available: bool | None
    active: bool | None
    verification: Literal["verified", "unverified"]


class Source(Contract):
    """Source identity and clock metadata independent of browser connections."""

    id: str
    name: str
    clock_domain_id: str
    simulated: bool
    rate_hz: float
    provenance: str
    capabilities: tuple[Capability, ...]


class StreamMessage(Contract):
    """One observation plus run identity and cumulative loss for this connection.

    Sequence gaps include missed production slots. dropped_total counts only
    observations evicted from this subscriber's bounded queue since connection.
    """

    schema_version: Literal[1] = 1
    run_id: str
    dropped_total: int = Field(ge=0, strict=True)
    observation: Observation


class Health(Contract):
    """Process health and stream schema, also defining its OpenAPI contract."""

    status: Literal["ok"] = "ok"
    version: str
    run_id: str
    stream_schema: StreamMessage | None = None
