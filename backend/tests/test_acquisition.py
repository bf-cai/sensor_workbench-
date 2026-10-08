import asyncio

import pytest

from sensor_workbench.adapters.simulation import SimulatedSource
from sensor_workbench.services.acquisition import Acquisition


def test_slow_subscriber_drops_oldest_without_blocking_others():
    async def scenario():
        service = Acquisition(SimulatedSource("test"), "boot", queue_size=2)
        slow = service.subscribe()
        fast = service.subscribe()
        for sequence in range(5):
            service.publish(service.source.observation(sequence))
            assert (await fast.next_message("test")).observation.sequence == sequence
        assert slow.queue.qsize() == 2
        message = await slow.next_message("test")
        assert message.observation.sequence == 3
        assert message.dropped_total == 3
        assert fast.dropped_total == 0
        service.unsubscribe(slow)
        assert slow not in service.subscriptions

    asyncio.run(scenario())


def test_acquisition_runs_without_clients_and_cancels_cleanly():
    async def scenario():
        service = Acquisition(SimulatedSource("test"), "boot")
        service.start()
        task = service.task
        await asyncio.sleep(0.23)
        assert service.last_sequence is not None and service.last_sequence >= 2
        assert service.subscriptions == set()
        subscription = service.subscribe()
        message = await asyncio.wait_for(subscription.next_message("test"), 0.3)
        assert message.observation.sequence >= 3
        assert message.observation.host_boot_id == "boot"
        assert isinstance(message.observation.host_receive_monotonic_ns, int)
        with pytest.raises(RuntimeError, match="already started"):
            service.start()
        await service.stop()
        assert task.cancelled()
        assert service.task is None
        assert not service.subscriptions

    asyncio.run(scenario())


def test_connection_capacity_is_enforced():
    service = Acquisition(SimulatedSource("test"), "boot", max_subscribers=1)
    subscription = service.subscribe()
    with pytest.raises(RuntimeError, match="limit"):
        service.subscribe()
    service.unsubscribe(subscription)
    assert service.subscribe() is not subscription


def test_stalled_event_loop_skips_slots_without_catchup_burst():
    async def scenario():
        import time

        service = Acquisition(SimulatedSource("test"), "boot", queue_size=10)
        subscription = service.subscribe()
        service.start()
        first = await asyncio.wait_for(subscription.next_message("test"), 0.3)
        assert first.observation.sequence == 0
        time.sleep(0.35)
        after_stall = await asyncio.wait_for(subscription.next_message("test"), 0.2)
        assert after_stall.observation.sequence >= 3
        assert subscription.queue.empty()
        await service.stop()

    asyncio.run(scenario())
