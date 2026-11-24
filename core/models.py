
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ElevatorState(Enum):
    IDLE = "idle"
    MOVING_UP = "moving_up"
    MOVING_DOWN = "moving_down"
    DOORS_OPEN = "doors_open"
    OUT_OF_SERVICE = "out_of_service"


@dataclass
class Passenger:
    passenger_id: int
    origin: int
    destination: int
    arrival_time: float

    pickup_time: Optional[float] = None
    dropoff_time: Optional[float] = None

    def __post_init__(self):
        if self.origin == self.destination:
            raise ValueError("Origin and destination cannot be equal.")

        if self.arrival_time < 0:
            raise ValueError("Arrival time cannot be negative.")

    @property
    def waiting_time(self):
        if self.pickup_time is None:
            return None

        return self.pickup_time - self.arrival_time

    @property
    def journey_time(self):
        if self.dropoff_time is None:
            return None

        return self.dropoff_time - self.pickup_time


@dataclass
class Elevator:
    elevator_id: str
    service_floors: tuple

    current_floor: int = 0
    capacity: int = 12

    travel_time_per_floor: float = 2.0
    door_open_time: float = 2.0
    door_close_time: float = 2.0
    boarding_time_per_passenger: float = 1.0

    state: ElevatorState = ElevatorState.IDLE

    passengers: list = field(default_factory=list)

    def can_serve(self, origin: int, destination: int) -> bool:
        return (
            origin in self.service_floors
            and destination in self.service_floors
        )

    def is_full(self) -> bool:
        return len(self.passengers) >= self.capacity

    def distance_to(self, floor: int) -> int:
        return abs(self.current_floor - floor)


def create_default_elevators():

    floors = range(-2, 10)

    odd_floors = tuple(
        floor for floor in floors if floor % 2 != 0
    )

    even_floors = tuple(
        floor for floor in floors if floor % 2 == 0
    )

    all_floors = tuple(range(0, 11))

    elevators = [
    Elevator("A1", odd_floors, current_floor=1),
    Elevator("A2", even_floors, current_floor=0),
    Elevator("B1", odd_floors, current_floor=1),
    Elevator("B2", even_floors, current_floor=0),
    Elevator("C1", all_floors, current_floor=0),
    Elevator("C2", all_floors, current_floor=0),
    ]

    return elevators
