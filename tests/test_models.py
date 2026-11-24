
from core.models import (
    Passenger,
    ElevatorState,
    create_default_elevators
)


def test_elevator_count():
    elevators = create_default_elevators()
    assert len(elevators) == 6


def test_odd_elevator():
    elevators = create_default_elevators()
    elevator = elevators[0]

    assert elevator.can_serve(1, 9)
    assert not elevator.can_serve(2, 8)


def test_even_elevator():
    elevators = create_default_elevators()
    elevator = elevators[1]

    assert elevator.can_serve(2, 8)
    assert not elevator.can_serve(1, 9)


def test_all_floor_elevator():
    elevators = create_default_elevators()
    elevator = elevators[4]

    assert elevator.can_serve(0, 10)


def test_passenger_waiting_time():
    passenger = Passenger(1, 2, 8, 10.0)

    passenger.pickup_time = 15.0

    assert passenger.waiting_time == 5.0


def test_initial_state():
    elevators = create_default_elevators()

    assert all(
        elevator.state == ElevatorState.IDLE
        for elevator in elevators
    )
