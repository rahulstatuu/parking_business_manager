"""
Represent a single parking space in the parking facility.

Each parking space has a unique number, belongs to one floor,
and has properties such as EV status, corner status, and pair
number.

The class also keeps track of whether the space is currently
occupied and which user is currently using it.
"""


class ParkingSpace:

    def __init__(
        self,
        space_number,
        floor,
        pair_number,
        is_ev=False,
        is_corner=False
    ):
        self.space_number = space_number
        self.floor = floor
        self.pair_number = pair_number
        self.is_ev = is_ev
        self.is_corner = is_corner

        # These values change when a vehicle enters or leaves.
        self.is_occupied = False
        self.current_user_id = None

    # Mark the space as occupied by a specific user.
    def occupy(self, user_id):
        self.is_occupied = True
        self.current_user_id = user_id

    # Make the space available after the current vehicle leaves.
    def release(self):
        self.is_occupied = False
        self.current_user_id = None

    # Provide a readable description of the parking space.
    def __str__(self):
        ev_status = (
            "EV"
            if self.is_ev
            else "Non-EV"
        )

        corner_status = (
            "Corner"
            if self.is_corner
            else "Standard"
        )

        availability = (
            "Occupied"
            if self.is_occupied
            else "Available"
        )

        return (
            f"{self.space_number} | "
            f"{self.floor} | "
            f"pair {self.pair_number} | "
            f"{ev_status} | "
            f"{corner_status} | "
            f"{availability}"
        )
