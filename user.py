"""
Represent a registered parking user.

Each user has a unique user ID, vehicle information, and
contact information.
"""


class User:

    def __init__(
        self,
        user_id,
        car_model,
        registration_no,
        vehicle_type,
        width,
        driver_cell
    ):
        self.user_id = user_id
        self.car_model = car_model
        self.registration_no = registration_no
        self.vehicle_type = vehicle_type
        self.width = width
        self.driver_cell = driver_cell

    # Convert the User object into a dictionary for JSON storage.
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "car_model": self.car_model,
            "registration_no": self.registration_no,
            "vehicle_type": self.vehicle_type,
            "width": self.width,
            "driver_cell": self.driver_cell
        }

    # Check whether this user owns an EV.
    def is_ev(self):
        return self.vehicle_type == "ev"

    # Provide a simple description of the registered user.
    def __str__(self):
        return (
            f"{self.user_id} | "
            f"{self.car_model} | "
            f"{self.registration_no}"
        )
