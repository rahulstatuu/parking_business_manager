from parking_space import ParkingSpace

"""
Represent the complete underground parking facility.

The parking facility contains 60 spaces across three floors:
G1: P1-P20
G2: P21-P40
G3: P41-P60

The facility has 12 ev spaces and 12 corner spaces.

Parking spaces are grouped into 30 equal-distance pairs:
P1/P2, P3/P4, ..., P59/P60.

The class creates and manages all ParkingSpace objects.
"""


class ParkingFacility:

    def __init__(self):
        self.spaces = []
        self._create_spaces()

    # Create all 60 parking spaces and assign their properties.
    def _create_spaces(self):
        ev_spaces = {
            17, 18, 19, 20,
            37, 38, 39, 40,
            57, 58, 59, 60
        }

        corner_spaces = {
            1, 2, 19, 20,
            21, 22, 39, 40,
            41, 42, 59, 60
        }

        for number in range(1, 61):
            floor = self._get_floor(number)
            pair_number = self._get_pair_number(number)

            space = ParkingSpace(
                space_number=f"p{number}",
                floor=floor,
                pair_number=pair_number,
                is_ev=number in ev_spaces,
                is_corner=number in corner_spaces
            )

            self.spaces.append(space)

    # Determine which floor a parking-space number belongs to.
    def _get_floor(self, number):
        if number <= 20:
            return "g1"

        if number <= 40:
            return "g2"

        return "g3"

    # Determine the equal-distance pair to which a space belongs.
    def _get_pair_number(self, number):
        return (number + 1) // 2

    # Return all parking spaces in the facility.
    def get_all_spaces(self):
        return self.spaces
