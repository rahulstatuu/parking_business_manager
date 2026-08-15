import json
import os


"""
Represent one complete parking incident.

A parking session begins when a vehicle enters the parking
facility. At entry, the system records the user, parking type,
parking space, booking information, and entry time.

At exit, the session is completed with the exit time, actual
duration, pricing breakdown, and final cost.

The same parking ID is used throughout the entire parking
incident.
"""


class ParkingSession:

    def __init__(
        self,
        parking_id,
        user_id,
        parking_type,
        parking_space,
        in_time,
        booked_hours=None,
        booking_end=None
    ):
        self.parking_id = parking_id
        self.user_id = user_id
        self.parking_type = parking_type
        self.parking_space = parking_space

        self.in_time = in_time
        self.booked_hours = booked_hours
        self.booking_end = booking_end

        # These values are filled when the vehicle exits.
        self.out_time = None
        self.actual_duration = None
        self.pricing_breakdown = None
        self.cost = None

    # Complete the parking session when the vehicle leaves.
    def complete_session(
        self,
        out_time,
        actual_duration,
        cost,
        pricing_breakdown
    ):
        self.out_time = out_time
        self.actual_duration = actual_duration
        self.cost = cost
        self.pricing_breakdown = pricing_breakdown

    # Convert the parking session into a dictionary
    # for JSON storage.
    def to_dict(self):
        return {
            "parking_id": self.parking_id,
            "user_id": self.user_id,
            "parking_type": self.parking_type,
            "parking_space": self.parking_space,
            "booking_end": self.booking_end,
            "booked_hours": self.booked_hours,
            "in_time": self.in_time,
            "out_time": self.out_time,
            "actual_duration": self.actual_duration,
            "pricing": self.pricing_breakdown,
            "cost": self.cost
        }

    # Provide a simple description of the active
    # parking session.
    def __str__(self):
        return (
            f"{self.parking_id} | "
            f"{self.user_id} | "
            f"{self.parking_space} | "
            f"{self.parking_type}"
        )

    # Temporary persistence:
    # The current active parking sessions are temporarily saved in a JSON file.
    # This allows the system to restore the present parking data if the program
    # is closed normally or unexpectedly and then restarted.
    # The file contains only active parking sessions and is removed when no
    # parking sessions remain.

    TEMP_FILE = "temp_parking_data.json"

    # Save only currently active parking sessions
    @staticmethod
    def save_active_sessions(sessions):

        data = [
            session.to_dict()
            for session in sessions
        ]

        with open(
            ParkingSession.TEMP_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    # Load active parking sessions from the temporary file

    @staticmethod
    def load_active_sessions():

        if not os.path.exists(
            ParkingSession.TEMP_FILE
        ):
            return []

        with open(
            ParkingSession.TEMP_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            content = file.read().strip()

        if not content:
            return []

        return json.loads(content)

    # Delete the temporary parking-session file

    @staticmethod
    def clear_active_sessions():

        if os.path.exists(
            ParkingSession.TEMP_FILE
        ):
            os.remove(
                ParkingSession.TEMP_FILE
            )
