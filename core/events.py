
import heapq
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EventType(Enum):
    PASSENGER_ARRIVAL = "passenger_arrival"
    ELEVATOR_ARRIVAL = "elevator_arrival"
    DOORS_OPEN = "doors_open"
    DOORS_CLOSE = "doors_close"
    PASSENGER_BOARDING = "passenger_boarding"
    PASSENGER_DROPOFF = "passenger_dropoff"


@dataclass(order=True)
class Event:
    time: float
    sequence: int

    event_type: EventType = field(compare=False)
    payload: Any = field(default=None, compare=False)


class EventQueue:

    def __init__(self):
        self._queue = []
        self._sequence = 0

    def schedule(self, time, event_type, payload=None):

        if time < 0:
            raise ValueError("Event time cannot be negative.")

        event = Event(
            time=time,
            sequence=self._sequence,
            event_type=event_type,
            payload=payload
        )

        heapq.heappush(self._queue, event)
        self._sequence += 1

        return event

    def pop_next(self):

        if not self._queue:
            raise IndexError("No events available.")

        return heapq.heappop(self._queue)

    def is_empty(self):
        return len(self._queue) == 0

    def __len__(self):
        return len(self._queue)
