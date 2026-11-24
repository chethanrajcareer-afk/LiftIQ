import random
from analytics.metrics import calculate_analytics
from core.models import Passenger, create_default_elevators
from core.models import Passenger
from core.simulation import Simulation

from algorithms.fcfs import FCFS
from algorithms.nearest import NearestElevator
from algorithms.demand_aware import DemandAware


def generate_workload(passenger_count=50, seed=42, duration=120):
    """
    Generate reproducible and physically valid
    passenger requests based on elevator availability.
    """

    if passenger_count < 0:
        raise ValueError("Passenger count cannot be negative.")

    if duration <= 0:
        raise ValueError("Duration must be positive.")

    rng = random.Random(seed)

    elevators = create_default_elevators()

    floors = list(range(-2, 11))

    # Generate only routes that at least one elevator can serve.
    valid_routes = [
        (origin, destination)
        for origin in floors
        for destination in floors
        if origin != destination
        and any(elevator.can_serve(origin, destination) for elevator in elevators)
    ]

    if not valid_routes and passenger_count > 0:
        raise ValueError("No valid elevator routes available.")

    arrival_times = sorted(rng.uniform(0, duration) for _ in range(passenger_count))

    requests = []

    for passenger_id, arrival_time in enumerate(arrival_times, start=1):

        origin, destination = rng.choice(valid_routes)

        requests.append(
            {
                "passenger_id": passenger_id,
                "origin": origin,
                "destination": destination,
                "arrival_time": round(arrival_time, 2),
            }
        )

    return requests


def run_experiment(requests):
    """
    Run identical passenger demand through
    three independent scheduling simulations.
    """

    algorithms = {
        "FCFS": FCFS(),
        "Nearest Elevator": NearestElevator(),
        "Demand Aware": DemandAware(),
    }

    results = {}

    for algorithm_name, scheduler in algorithms.items():

        simulation = Simulation(scheduler=scheduler)

        # Create fresh passenger objects for each simulation.
        for request in requests:

            passenger = Passenger(
                passenger_id=request["passenger_id"],
                origin=request["origin"],
                destination=request["destination"],
                arrival_time=request["arrival_time"],
            )

            simulation.add_passenger(passenger)

        summary = simulation.run()
        analytics = calculate_analytics(simulation)

        total = summary["total_passengers"]
        completed = summary["completed_passengers"]

        completion_rate = completed / total * 100 if total > 0 else 0.0

        results[algorithm_name] = {
            **summary,
            **analytics,
            "completion_rate": round(completion_rate, 2),
        }
    return results


def print_comparison(results):

    print("\n" + "=" * 90)
    print("LIFTIQ - ELEVATOR PERFORMANCE ANALYTICS")
    print("=" * 90)

    print(
        f"{'Algorithm':<22}"
        f"{'Avg Wait':>12}"
        f"{'P95 Wait':>12}"
        f"{'Avg Util %':>14}"
        f"{'Completed':>14}"
    )

    print("-" * 90)

    for name, metrics in results.items():

        print(
            f"{name:<22}"
            f"{metrics['average_waiting_time']:>12.2f}"
            f"{metrics['waiting_time_p95']:>12.2f}"
            f"{metrics['average_elevator_utilisation']:>14.2f}"
            f"{metrics['completed_passengers']:>14}"
        )

    print("=" * 90)

    print("\nINDIVIDUAL ELEVATOR UTILISATION")

    for name, metrics in results.items():

        print(f"\n{name}")

        for elevator_id, data in metrics["elevator_utilisation"].items():

            print(
                f"  {elevator_id}: "
                f"{data['utilisation_percentage']}% "
                f"(Busy: {data['busy_time']}s, "
                f"Idle: {data['idle_time']}s)"
            )


if __name__ == "__main__":

    print("\nGenerating passenger workload...")

    requests = generate_workload(passenger_count=50, seed=42, duration=120)

    print(f"Generated {len(requests)} passenger requests.")

    print("\nRunning algorithm comparison...")

    results = run_experiment(requests)

    print_comparison(results)

    print("\nExperiment completed successfully.")
