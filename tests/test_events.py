
import pytest

from core.events import EventQueue, EventType


def test_events_are_processed_chronologically():

    queue = EventQueue()

    queue.schedule(10, EventType.PASSENGER_ARRIVAL)
    queue.schedule(5, EventType.ELEVATOR_ARRIVAL)
    queue.schedule(8, EventType.DOORS_OPEN)

    assert queue.pop_next().time == 5
    assert queue.pop_next().time == 8
    assert queue.pop_next().time == 10


def test_same_time_events_preserve_order():

    queue = EventQueue()

    first = queue.schedule(
        5, EventType.PASSENGER_ARRIVAL
    )

    second = queue.schedule(
        5, EventType.ELEVATOR_ARRIVAL
    )

    assert queue.pop_next() == first
    assert queue.pop_next() == second


def test_event_payload():

    queue = EventQueue()

    queue.schedule(
        5,
        EventType.PASSENGER_ARRIVAL,
        {"passenger_id": 101}
    )

    event = queue.pop_next()

    assert event.payload["passenger_id"] == 101


def test_negative_event_time():

    queue = EventQueue()

    with pytest.raises(ValueError):
        queue.schedule(-1, EventType.PASSENGER_ARRIVAL)


def test_empty_queue():

    queue = EventQueue()

    assert queue.is_empty()
    assert len(queue) == 0

    with pytest.raises(IndexError):
        queue.pop_next()
