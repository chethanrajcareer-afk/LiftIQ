
from collections import Counter

from algorithms.base import SchedulingAlgorithm


class DemandAware(SchedulingAlgorithm):

    def select_assignment(self, waiting_passengers, elevators):

        candidates = self.get_candidates(
            waiting_passengers,
            elevators
        )

        if not candidates:
            return None

        demand = Counter(
            passenger.origin
            for passenger in waiting_passengers
        )

        def calculate_score(pair):

            passenger, elevator = pair

            distance = elevator.distance_to(
                passenger.origin
            )

            floor_demand = demand[passenger.origin]

            score = distance / floor_demand

            return (
                score,
                passenger.arrival_time,
                passenger.passenger_id,
                elevator.elevator_id
            )

        return min(candidates, key=calculate_score)
