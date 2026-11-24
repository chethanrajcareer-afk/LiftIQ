from analytics.experiment import generate_workload, run_experiment


def test_workload_generation():

    requests = generate_workload(passenger_count=20, seed=42)

    assert len(requests) == 20


def test_workload_is_reproducible():

    first = generate_workload(passenger_count=20, seed=42)

    second = generate_workload(passenger_count=20, seed=42)

    assert first == second


def test_three_algorithms_are_compared():

    requests = generate_workload(passenger_count=10, seed=10, duration=60)

    results = run_experiment(requests)

    assert len(results) == 3

    assert "FCFS" in results
    assert "Nearest Elevator" in results
    assert "Demand Aware" in results


def test_all_passengers_are_accounted_for():

    requests = generate_workload(passenger_count=10, seed=15, duration=60)

    results = run_experiment(requests)

    for metrics in results.values():

        assert metrics["total_passengers"] == 10

        assert metrics["completed_passengers"] + metrics["pending_passengers"] == 10


def test_completion_rate_is_valid():

    requests = generate_workload(passenger_count=10, seed=25)

    results = run_experiment(requests)

    for metrics in results.values():

        assert 0 <= metrics["completion_rate"] <= 100


def test_empty_workload():

    results = run_experiment([])

    for metrics in results.values():

        assert metrics["total_passengers"] == 0
        assert metrics["completed_passengers"] == 0
        assert metrics["completion_rate"] == 0
