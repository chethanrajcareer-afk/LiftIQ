from algorithms.fcfs import FCFS

from core.models import Passenger, ElevatorState, create_default_elevators

from core.events import EventQueue, EventType


class Simulation:

    def __init__(self, elevators=None, scheduler=None):

        # Initialize elevators
        self.elevators = (
            elevators if elevators is not None else create_default_elevators()
        )

        # Initialize scheduling algorithm
        self.scheduler = scheduler if scheduler is not None else FCFS()

        # Initialize event queue
        self.event_queue = EventQueue()

        # Passenger management
        self.passengers = {}
        self.pending_passengers = []
        self.completed_passengers = []

        # Simulation state
        self.current_time = 0.0
        self.event_log = []

    # --------------------------------------------------
    # PASSENGER MANAGEMENT
    # --------------------------------------------------

    def add_passenger(self, passenger):

        if passenger.passenger_id in self.passengers:
            raise ValueError("Passenger ID already exists.")

        eligible = any(
            elevator.can_serve(passenger.origin, passenger.destination)
            for elevator in self.elevators
        )

        if not eligible:
            raise ValueError("No elevator can serve this passenger's journey.")

        self.passengers[passenger.passenger_id] = passenger

        self.event_queue.schedule(
            passenger.arrival_time,
            EventType.PASSENGER_ARRIVAL,
            {"passenger_id": passenger.passenger_id},
        )

    # --------------------------------------------------
    # EVENT LOGGING
    # --------------------------------------------------

    def log_event(self, event_name, **details):

        self.event_log.append(
            {"time": self.current_time, "event": event_name, **details}
        )

    # --------------------------------------------------
    # ELEVATOR MANAGEMENT
    # --------------------------------------------------

    def get_elevator(self, elevator_id):

        for elevator in self.elevators:

            if elevator.elevator_id == elevator_id:
                return elevator

        raise ValueError("Elevator not found.")

    # --------------------------------------------------
    # SCHEDULING AND DISPATCH
    # --------------------------------------------------

    def _dispatch_waiting(self):

        while self.pending_passengers:

            waiting = [
                self.passengers[passenger_id]
                for passenger_id in self.pending_passengers
            ]

            assignment = self.scheduler.select_assignment(waiting, self.elevators)

            if assignment is None:
                return

            passenger, elevator = assignment

            self.pending_passengers.remove(passenger.passenger_id)

            self._start_pickup(elevator, passenger)

    # --------------------------------------------------
    # START ELEVATOR PICKUP
    # --------------------------------------------------

    def _start_pickup(self, elevator, passenger):

        distance = elevator.distance_to(passenger.origin)

        if passenger.origin > elevator.current_floor:

            elevator.state = ElevatorState.MOVING_UP

        elif passenger.origin < elevator.current_floor:

            elevator.state = ElevatorState.MOVING_DOWN

        else:

            elevator.state = ElevatorState.DOORS_OPEN

        travel_time = distance * elevator.travel_time_per_floor

        self.event_queue.schedule(
            self.current_time + travel_time,
            EventType.ELEVATOR_ARRIVAL,
            {
                "elevator_id": elevator.elevator_id,
                "passenger_id": passenger.passenger_id,
                "phase": "pickup",
                "target_floor": passenger.origin,
            },
        )

        self.log_event(
            "elevator_dispatched",
            elevator_id=elevator.elevator_id,
            passenger_id=passenger.passenger_id,
        )

    # --------------------------------------------------
    # EVENT PROCESSING ENGINE
    # --------------------------------------------------

    def _process_event(self, event):

        data = event.payload or {}
        event_type = event.event_type

        # PASSENGER ARRIVES
        if event_type == EventType.PASSENGER_ARRIVAL:

            passenger_id = data["passenger_id"]

            self.pending_passengers.append(passenger_id)

            self.log_event("passenger_arrived", passenger_id=passenger_id)

            self._dispatch_waiting()

        # ELEVATOR REACHES TARGET FLOOR
        elif event_type == EventType.ELEVATOR_ARRIVAL:

            elevator = self.get_elevator(data["elevator_id"])

            elevator.current_floor = data["target_floor"]

            elevator.state = ElevatorState.DOORS_OPEN

            self.event_queue.schedule(
                self.current_time + elevator.door_open_time, EventType.DOORS_OPEN, data
            )

            self.log_event(
                "elevator_arrived",
                elevator_id=elevator.elevator_id,
                floor=elevator.current_floor,
            )

        # ELEVATOR DOORS OPEN
        elif event_type == EventType.DOORS_OPEN:

            elevator = self.get_elevator(data["elevator_id"])

            if data["phase"] == "pickup":

                self.event_queue.schedule(
                    self.current_time + elevator.boarding_time_per_passenger,
                    EventType.PASSENGER_BOARDING,
                    data,
                )

            else:

                self.event_queue.schedule(
                    self.current_time, EventType.PASSENGER_DROPOFF, data
                )

        # PASSENGER BOARDS
        elif event_type == EventType.PASSENGER_BOARDING:

            elevator = self.get_elevator(data["elevator_id"])

            passenger = self.passengers[data["passenger_id"]]

            passenger.pickup_time = self.current_time

            elevator.passengers.append(passenger)

            self.log_event(
                "passenger_boarded",
                passenger_id=passenger.passenger_id,
                elevator_id=elevator.elevator_id,
            )

            self.event_queue.schedule(
                self.current_time + elevator.door_close_time,
                EventType.DOORS_CLOSE,
                data,
            )

        # PASSENGER REACHES DESTINATION
        elif event_type == EventType.PASSENGER_DROPOFF:

            elevator = self.get_elevator(data["elevator_id"])

            passenger = self.passengers[data["passenger_id"]]

            passenger.dropoff_time = self.current_time

            elevator.passengers.remove(passenger)

            self.completed_passengers.append(passenger)

            self.log_event(
                "passenger_dropped_off",
                passenger_id=passenger.passenger_id,
                elevator_id=elevator.elevator_id,
                floor=elevator.current_floor,
            )

            self.event_queue.schedule(
                self.current_time + elevator.door_close_time,
                EventType.DOORS_CLOSE,
                data,
            )

        # ELEVATOR DOORS CLOSE
        elif event_type == EventType.DOORS_CLOSE:

            elevator = self.get_elevator(data["elevator_id"])

            if data["phase"] == "pickup":

                passenger = self.passengers[data["passenger_id"]]

                destination = passenger.destination

                if destination > elevator.current_floor:

                    elevator.state = ElevatorState.MOVING_UP

                elif destination < elevator.current_floor:

                    elevator.state = ElevatorState.MOVING_DOWN

                else:

                    return

                travel_time = (
                    abs(destination - elevator.current_floor)
                    * elevator.travel_time_per_floor
                )

                self.event_queue.schedule(
                    self.current_time + travel_time,
                    EventType.ELEVATOR_ARRIVAL,
                    {
                        "elevator_id": elevator.elevator_id,
                        "passenger_id": passenger.passenger_id,
                        "phase": "dropoff",
                        "target_floor": destination,
                    },
                )

            else:

                elevator.state = ElevatorState.IDLE

                self.log_event(
                    "elevator_became_idle",
                    elevator_id=elevator.elevator_id,
                )

                self._dispatch_waiting()

    # --------------------------------------------------
    # RUN SIMULATION
    # --------------------------------------------------

    def run(self):

        while not self.event_queue.is_empty():

            event = self.event_queue.pop_next()

            self.current_time = event.time

            self._process_event(event)

        return self.get_summary()

    # --------------------------------------------------
    # PERFORMANCE SUMMARY
    # --------------------------------------------------

    def get_summary(self):

        completed = self.completed_passengers

        if not completed:

            average_wait = 0.0
            average_journey = 0.0
            maximum_wait = 0.0

        else:

            waiting_times = [passenger.waiting_time for passenger in completed]

            journey_times = [passenger.journey_time for passenger in completed]

            average_wait = sum(waiting_times) / len(waiting_times)

            average_journey = sum(journey_times) / len(journey_times)

            maximum_wait = max(waiting_times)

        return {
            "total_passengers": len(self.passengers),
            "completed_passengers": len(completed),
            "pending_passengers": len(self.pending_passengers),
            "average_waiting_time": average_wait,
            "maximum_waiting_time": maximum_wait,
            "average_journey_time": average_journey,
            "simulation_time": self.current_time,
        }
