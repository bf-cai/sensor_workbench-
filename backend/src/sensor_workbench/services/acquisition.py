"""Browser-independent acquisition with bounded per-subscriber delivery."""

import asyncio
import time
from contextlib import suppress
from dataclasses import dataclass

from sensor_workbench.adapters.simulation import PERIOD_NS, SimulatedSource
from sensor_workbench.core.models import Observation, StreamMessage


@dataclass(eq=False)
class Subscription:
    """Bounded observation queue and cumulative evictions for one subscriber."""

    queue: asyncio.Queue[Observation]
    dropped_total: int = 0

    async def next_message(self, run_id: str) -> StreamMessage:
        """Wait for an observation; expose loss since this connection subscribed."""
        observation = await self.queue.get()
        return StreamMessage(
            run_id=run_id, dropped_total=self.dropped_total, observation=observation,
        )


class Acquisition:
    """Own one simulation task and at most sixteen bounded subscriber queues.

    Args:
        source: Deterministic synthetic observation generator.
        boot_id: Linux boot identity for reception monotonic timestamps.
        queue_size: Maximum queued observations per subscriber (default 32).
        max_subscribers: Maximum concurrent streams (default 16).
    """

    def __init__(
        self, source: SimulatedSource, boot_id: str,
        queue_size: int = 32, max_subscribers: int = 16,
    ) -> None:
        """Validate bounds and prepare acquisition without scheduling tasks."""
        if queue_size <= 0 or max_subscribers <= 0:
            raise ValueError("Queue and subscriber bounds must be positive")
        self.source = source
        self.boot_id = boot_id
        self.queue_size = queue_size
        self.max_subscribers = max_subscribers
        self.subscriptions: set[Subscription] = set()
        self.task: asyncio.Task[None] | None = None
        self.last_sequence: int | None = None

    def start(self) -> None:
        """Start acquisition on the current event loop, independently of clients."""
        if self.task is not None:
            raise RuntimeError("Acquisition is already started")
        self.task = asyncio.create_task(self._produce(), name="simulated-acquisition")

    async def stop(self) -> None:
        """Cancel and await the producer; discard remaining subscriber queues."""
        if self.task is not None:
            self.task.cancel()
            with suppress(asyncio.CancelledError):
                await self.task
            self.task = None
        self.subscriptions.clear()

    def subscribe(self) -> Subscription:
        """Create a bounded queue, raising RuntimeError if stream capacity is full."""
        if len(self.subscriptions) >= self.max_subscribers:
            raise RuntimeError("Stream connection limit reached")
        subscription = Subscription(asyncio.Queue(maxsize=self.queue_size))
        self.subscriptions.add(subscription)
        return subscription

    def unsubscribe(self, subscription: Subscription) -> None:
        """Release a subscriber when its browser disconnects or its sender fails."""
        self.subscriptions.discard(subscription)

    def publish(self, observation: Observation) -> None:
        """Offer an observation without blocking acquisition on slow subscribers."""
        self.last_sequence = observation.sequence
        for subscription in self.subscriptions:
            if subscription.queue.full():
                subscription.queue.get_nowait()
                subscription.dropped_total += 1
            subscription.queue.put_nowait(observation)

    async def _produce(self) -> None:
        epoch_ns = time.monotonic_ns()
        sequence = 0
        while True:
            deadline_ns = epoch_ns + sequence * PERIOD_NS
            await asyncio.sleep(max(0, deadline_ns - time.monotonic_ns()) / 1e9)
            receive_ns = time.monotonic_ns()
            # Skip missed sample slots instead of creating a catch-up burst.
            sequence = max(sequence, (receive_ns - epoch_ns) // PERIOD_NS)
            observation = self.source.observation(sequence).model_copy(update={
                "host_receive_monotonic_ns": receive_ns, "host_boot_id": self.boot_id,
            })
            self.publish(observation)
            sequence += 1
