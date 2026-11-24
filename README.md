# LiftIQ

LiftIQ is a Python discrete-event simulation and decision-support prototype for university elevator operations. It compares elevator dispatch strategies against the same synthetic passenger workload and presents the results in a Streamlit dashboard.

## Current status

- Event-driven passenger lifecycle with deterministic event ordering.
- Three scheduling strategies: FCFS, Nearest Elevator, and Demand Aware.
- Reproducible synthetic workload generation and independent algorithm runs.
- Waiting-time, journey-time, completion, busy-time, idle-time, and utilisation metrics.
- Regression coverage for the elevator busy-to-idle lifecycle.
- 32 automated tests passing after the latest utilisation correction.

LiftIQ is a simulation platform. Its inputs and results are synthetic, so they must not be presented as live operational measurements or recommendations for CHRIST University.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Configure passenger count, arrival duration, and random seed in the sidebar, then select **Run Simulation**.

## Run tests

```powershell
python -m pytest -q
```

## Project structure

```text
app.py                  Streamlit dashboard
core/                   Models, event queue, and simulation engine
algorithms/             FCFS, nearest-elevator, and demand-aware policies
analytics/              Metrics and reproducible experiment runner
tests/                  Automated regression tests
assets/                 Dashboard assets
```

## Baseline experiment

Configuration: 50 passengers, 120 simulation-time units, seed 42.

| Algorithm | Average wait | P95 wait | Average utilisation |
| --- | ---: | ---: | ---: |
| FCFS | 82.95 | 198.38 | 58.63% |
| Nearest Elevator | 55.12 | 191.95 | 66.34% |
| Demand Aware | 57.01 | 178.85 | 65.44% |

All 50 requests completed in this synthetic baseline. The utilisation values were regenerated after correcting the `elevator_became_idle` event lifecycle. Waiting-time results are unchanged by that correction.

## Current limitations

- Passenger demand is synthetic.
- The engine dispatches one passenger journey per elevator at a time.
- Capacity, shared rides, intermediate stops, transfers, and breakdowns are not modelled.
- The real-world elevator labels and floor restrictions should be confirmed before using the model for operational analysis.
- Algorithm comparisons need multiple demand scenarios and random seeds.

## Next steps

1. Confirm the physical fleet configuration and encode it in tests.
2. Add scenario-based benchmarks across multiple seeds.
3. Model capacity, queue lengths, directional groups, and intermediate stops.
4. Add pinned dependencies, CI, architecture documentation, and deployment instructions.
