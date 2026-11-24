
from algorithms.base import SchedulingAlgorithm


class FCFS(SchedulingAlgorithm):

    def select_assignment(self, waiting_passengers, elevators):

        candidates = self.get_candidates(
            waiting_passengers,
            elevators
        )

        if not candidates:
            return None

        return min(
            candidates,
            key=lambda pair: (
                pair[0].arrival_time,
                pair[0].passenger_id,
                pair[1].elevator_id
            )
        )
