import pytest

from analytics.metrics import (
    calculate_percentile,
    calculate_analytics,
    calculate_elevator_utilisation,
)

from analytics.experiment import generate_workload
from core.models import Elevator, Passenger
from core.simulation import Simulation


def create_test_simulation():

    requests = generate_workload(passenger_count=20, seed=42, duration=60)

    simulation = Simulation()

    for request in requests:

        from core.models import Passenger

        passenger = Passenger(**request)

        simulation.add_passenger(passenger)

    simulation.run()

    return simulation


def test_percentile_calculation():

    values = [10, 20, 30, 40, 50]

    assert calculate_percentile(values, 50) == 30


def test_empty_percentile():

    assert calculate_percentile([], 95) == 0.0


def test_invalid_percentile():

    import pytest

    with pytest.raises(ValueError):
        calculate_percentile([10, 20], 110)


def test_all_six_elevators_are_measured():

    simulation = create_test_simulation()

    result = calculate_elevator_utilisation(simulation)

    assert len(result) == 6


def test_utilisation_is_within_valid_range():

    simulation = create_test_simulation()

    result = calculate_elevator_utilisation(simulation)

    for elevator in result.values():

        assert 0 <= elevator["utilisation_percentage"] <= 100


def test_analytics_contains_p95():

    simulation = create_test_simulation()

    result = calculate_analytics(simulation)

    assert "waiting_time_p95" in result


def test_busy_time_does_not_exceed_simulation_duration():

    simulation = create_test_simulation()

    result = calculate_elevator_utilisation(simulation)

    for elevator in result.values():

        assert elevator["busy_time"] <= simulation.current_time


def test_utilisation_accumulates_multiple_busy_intervals_and_idle_time():

    elevator = Elevator("E1", service_floors=(0, 2), current_floor=0)
    simulation = Simulation(elevators=[elevator])

    simulation.add_passenger(Passenger(1, 0, 2, 0))
    simulation.add_passenger(Passenger(2, 2, 0, 20))
    simulation.run()

    lifecycle_events = [
        event
        for event in simulation.event_log
        if event.get("elevator_id") == "E1"
        and event["event"] in {"elevator_dispatched", "elevator_became_idle"}
    ]

    assert [event["event"] for event in lifecycle_events] == [
        "elevator_dispatched",
        "elevator_became_idle",
        "elevator_dispatched",
        "elevator_became_idle",
    ]

    utilisation = calculate_elevator_utilisation(simulation)["E1"]

    assert utilisation["busy_time"] == pytest.approx(26.0)
    assert utilisation["idle_time"] == pytest.approx(7.0)
    assert utilisation["busy_time"] + utilisation["idle_time"] == pytest.approx(
        simulation.current_time
    )
