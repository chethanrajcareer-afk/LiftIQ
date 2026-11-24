
import pytest

from core.models import Passenger
from core.simulation import Simulation


def test_single_passenger_completes_journey():

    sim = Simulation()

    passenger = Passenger(
        passenger_id=1,
        origin=2,
        destination=4,
        arrival_time=0
    )

    sim.add_passenger(passenger)

    result = sim.run()

    assert result["completed_passengers"] == 1
    assert result["pending_passengers"] == 0


def test_waiting_time_calculation():

    sim = Simulation()

    passenger = Passenger(1, 2, 4, 0)

    sim.add_passenger(passenger)
    sim.run()

    assert passenger.pickup_time == 7.0
    assert passenger.waiting_time == 7.0


def test_passenger_reaches_destination():

    sim = Simulation()

    passenger = Passenger(1, 2, 4, 0)

    sim.add_passenger(passenger)
    sim.run()

    assert passenger.dropoff_time == 15.0
    assert passenger.journey_time == 8.0


def test_multiple_passengers_complete():

    sim = Simulation()

    sim.add_passenger(Passenger(1, 2, 4, 0))
    sim.add_passenger(Passenger(2, 0, 2, 0))

    result = sim.run()

    assert result["completed_passengers"] == 2


def test_invalid_elevator_route():

    sim = Simulation()

    passenger = Passenger(1, -2, 10, 0)

    with pytest.raises(ValueError):
        sim.add_passenger(passenger)


def test_duplicate_passenger_id():

    sim = Simulation()

    sim.add_passenger(Passenger(1, 2, 4, 0))

    with pytest.raises(ValueError):
        sim.add_passenger(Passenger(1, 2, 6, 5))


def test_event_log_is_generated():

    sim = Simulation()

    sim.add_passenger(Passenger(1, 2, 4, 0))
    sim.run()

    event_names = [
        event["event"] for event in sim.event_log
    ]

    assert "passenger_arrived" in event_names
    assert "elevator_dispatched" in event_names
    assert "passenger_boarded" in event_names
    assert "passenger_dropped_off" in event_names
