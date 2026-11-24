import math


def calculate_percentile(values, percentile):
    """
    Calculate percentile using the nearest-rank method.
    """

    if not values:
        return 0.0

    if not 0 <= percentile <= 100:
        raise ValueError("Percentile must be between 0 and 100.")

    ordered = sorted(values)

    index = max(0, math.ceil((percentile / 100) * len(ordered)) - 1)

    return ordered[index]


def calculate_elevator_utilisation(simulation):
    """
    Calculate busy time and utilisation for each elevator.

    Busy time includes dispatch, movement and door operations.
    """

    busy_times = {elevator.elevator_id: 0.0 for elevator in simulation.elevators}

    active_since = {}

    for event in simulation.event_log:

        elevator_id = event.get("elevator_id")
        event_name = event["event"]
        event_time = event["time"]

        if elevator_id not in busy_times:
            continue

        if event_name == "elevator_dispatched":

            active_since[elevator_id] = event_time

        elif event_name == "elevator_became_idle":

            start_time = active_since.pop(elevator_id, None)

            if start_time is not None:
                busy_times[elevator_id] += event_time - start_time

    # Account for any elevator still busy at simulation end.
    for elevator_id, start_time in active_since.items():

        busy_times[elevator_id] += max(0.0, simulation.current_time - start_time)

    simulation_duration = simulation.current_time

    utilisation = {}

    for elevator_id, busy_time in busy_times.items():

        percentage = (
            (busy_time / simulation_duration) * 100 if simulation_duration > 0 else 0.0
        )

        utilisation[elevator_id] = {
            "busy_time": round(busy_time, 2),
            "idle_time": round(max(0.0, simulation_duration - busy_time), 2),
            "utilisation_percentage": round(percentage, 2),
        }

    return utilisation


def calculate_analytics(simulation):
    """
    Generate performance analytics for a completed simulation.
    """

    completed = simulation.completed_passengers

    waiting_times = [passenger.waiting_time for passenger in completed]

    journey_times = [passenger.journey_time for passenger in completed]

    utilisation = calculate_elevator_utilisation(simulation)

    average_utilisation = (
        sum(item["utilisation_percentage"] for item in utilisation.values())
        / len(utilisation)
        if utilisation
        else 0.0
    )

    return {
        "waiting_time_p95": round(calculate_percentile(waiting_times, 95), 2),
        "waiting_time_median": round(calculate_percentile(waiting_times, 50), 2),
        "average_elevator_utilisation": round(average_utilisation, 2),
        "elevator_utilisation": utilisation,
        "total_busy_time": round(
            sum(item["busy_time"] for item in utilisation.values()), 2
        ),
    }
