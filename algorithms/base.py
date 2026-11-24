
from abc import ABC, abstractmethod

from core.models import ElevatorState


class SchedulingAlgorithm(ABC):

    @abstractmethod
    def select_assignment(self, waiting_passengers, elevators):
        """
        Select and return (passenger, elevator).

        Return None if no assignment is possible.
        """
        pass

    def get_candidates(self, waiting_passengers, elevators):

        candidates = []

        for passenger in waiting_passengers:

            for elevator in elevators:

                if elevator.state != ElevatorState.IDLE:
                    continue

                if not elevator.can_serve(
                    passenger.origin,
                    passenger.destination
                ):
                    continue

                candidates.append((passenger, elevator))

        return candidates
