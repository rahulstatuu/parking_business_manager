import random
from datetime import datetime, timedelta

from parking_session import ParkingSession
from pricing import Pricing


"""
Manage parking allocation and active parking sessions.

Parking allocation follows these business priorities:

1. Keep ev and non-ev vehicles separated.
2. For vehicles wider than 175 cm, prefer corner spaces.
3. For wide vehicles booked for more than four hours,
   search eligible spaces from g3 to g1.
4. For normal-width vehicles booked for more than four hours,
   prefer g3.
5. When spaces have the same distance from the exit,
   treat them as a pair and select randomly.
6. An ev customer who is offered a non-ev space must
   accept that space before choosing booked or unbooked parking.
7. If the ev customer refuses the non-ev space,
   no parking session is created.
8. All parking types have a two-minute grace period.

The class also manages active parking sessions,
parking IDs, vehicle entry, vehicle exit, and pricing.
"""


class ParkingManager:

    EXIT_GRACE_MINUTES = 2

    def __init__(
        self,
        parking_facility,
        data_manager,
        pricing=None
    ):
        self.parking_facility = parking_facility
        self.data_manager = data_manager
        self.pricing = pricing or Pricing()
        self.active_sessions = {}

        # Restore active parking sessions
        # from the temporary parking file.
        self._restore_active_sessions()

    def _restore_active_sessions(self):
        saved_sessions = (
            ParkingSession.load_active_sessions()
        )

        for session_data in saved_sessions:

            session = ParkingSession(
                parking_id=session_data["parking_id"],
                user_id=session_data["user_id"],
                parking_type=session_data["parking_type"],
                parking_space=session_data["parking_space"],
                in_time=session_data["in_time"],
                booked_hours=session_data.get(
                    "booked_hours"
                ),
                booking_end=session_data.get(
                    "booking_end"
                )
            )

            self.active_sessions[
                session.parking_id
            ] = session

            # Restore the physical parking-space
            # occupancy as well.
            for space in (
                self.parking_facility.get_all_spaces()
            ):
                if (
                    space.space_number
                    == session.parking_space
                ):
                    space.occupy(
                        session.user_id
                    )
                    break

    # Return all parking spaces that are currently available.

    def _get_available_spaces(self):
        return [
            space
            for space in self.parking_facility.get_all_spaces()
            if not space.is_occupied
        ]

    # Keep ev and non-ev vehicles separated whenever possible.
    def _filter_by_vehicle_type(
        self,
        spaces,
        is_ev
    ):
        if is_ev:
            ev_spaces = [
                space
                for space in spaces
                if space.is_ev
            ]

            if ev_spaces:
                return ev_spaces

            return []

        return [
            space
            for space in spaces
            if not space.is_ev
        ]

    # Prefer corner spaces for vehicles wider than 175 cm.
    def _filter_by_width(
        self,
        spaces,
        vehicle_width
    ):
        if vehicle_width > 175:
            corner_spaces = [
                space
                for space in spaces
                if space.is_corner
            ]

            if corner_spaces:
                return corner_spaces

            return spaces

        normal_spaces = [
            space
            for space in spaces
            if not space.is_corner
        ]

        if normal_spaces:
            return normal_spaces

        return spaces

    # For a wide vehicle staying longer than four hours,
    # search eligible spaces from g3 to g1.
    def _find_wide_long_stay_space(
        self,
        spaces
    ):
        for floor in ("g3", "g2", "g1"):
            floor_spaces = [
                space
                for space in spaces
                if space.floor == floor
            ]

            if floor_spaces:
                return floor_spaces

        return []

    # For a normal-width vehicle staying longer than
    # four hours, prefer g3.
    def _filter_by_long_stay(
        self,
        spaces,
        expected_hours
    ):
        if expected_hours > 4:
            g3_spaces = [
                space
                for space in spaces
                if space.floor == "g3"
            ]

            if g3_spaces:
                return g3_spaces

        return spaces

    # Find the pair of spaces that is closest to the exit.
    def _find_nearest_pair(
        self,
        spaces
    ):
        if not spaces:
            return []

        nearest_pair = min(
            space.pair_number
            for space in spaces
        )

        return [
            space
            for space in spaces
            if space.pair_number == nearest_pair
        ]

    # Randomly select one space when the available
    # spaces have the same distance from the exit.
    def _select_from_pair(
        self,
        spaces
    ):
        if not spaces:
            return None

        return random.choice(spaces)

    # Find the nearest available ev space.
    def _find_available_ev_space(
        self,
        spaces
    ):
        ev_spaces = [
            space
            for space in spaces
            if space.is_ev
        ]

        if not ev_spaces:
            return None

        nearest_pair = self._find_nearest_pair(
            ev_spaces
        )

        return self._select_from_pair(
            nearest_pair
        )

    # Find a suitable non-ev fallback space for an ev
    # customer when no ev space is available.
    #
    # This space is shown to the customer before
    # the booking decision.
    def _find_ev_fallback_space(
        self,
        spaces,
        vehicle_width
    ):
        non_ev_spaces = [
            space
            for space in spaces
            if not space.is_ev
        ]

        if not non_ev_spaces:
            return None

        # Wide evs prefer non-ev corner spaces.
        if vehicle_width > 175:

            corner_spaces = [
                space
                for space in non_ev_spaces
                if space.is_corner
            ]

            if corner_spaces:
                non_ev_spaces = corner_spaces

        else:

            # Normal-width evs prefer non-corner spaces.
            normal_spaces = [
                space
                for space in non_ev_spaces
                if not space.is_corner
            ]

            if normal_spaces:
                non_ev_spaces = normal_spaces

        nearest_pair = self._find_nearest_pair(
            non_ev_spaces
        )

        return self._select_from_pair(
            nearest_pair
        )

    # Find the best parking space according to the
    # normal allocation rules.
    def find_parking_space(
        self,
        is_ev,
        vehicle_width,
        expected_hours
    ):
        available_spaces = (
            self._get_available_spaces()
        )

        if not available_spaces:
            return None

        # Priority 1:
        # ev and non-ev separation.
        spaces = self._filter_by_vehicle_type(
            available_spaces,
            is_ev
        )

        if not spaces:
            return None

        # Wide vehicle with a booking longer than
        # four hours.
        if (
            vehicle_width > 175
            and expected_hours > 4
        ):
            # Priority 2:
            # Corner spaces.
            spaces = self._filter_by_width(
                spaces,
                vehicle_width
            )

            # Priority 3:
            # g3, then g2, then g1.
            spaces = self._find_wide_long_stay_space(
                spaces
            )

        else:
            # Priority 2:
            # Corner preference for wide vehicles.
            spaces = self._filter_by_width(
                spaces,
                vehicle_width
            )

            # Priority 3:
            # g3 preference for long stays.
            spaces = self._filter_by_long_stay(
                spaces,
                expected_hours
            )

        if not spaces:
            return None

        # Final priority:
        # nearest pair.
        nearest_pair = self._find_nearest_pair(
            spaces
        )

        return self._select_from_pair(
            nearest_pair
        )

    # Generate a unique parking ID using the user's ID,
    # entry date, and the parking sequence for that date.
    #
    # Example:
    # u0001-20260812-01
    def _generate_parking_id(
        self,
        user_id,
        in_time
    ):
        date_part = in_time.strftime(
            "%Y%m%d"
        )

        prefix = (
            f"{user_id}-{date_part}-"
        )

        existing_records = (
            self.data_manager.load_history()
        )

        highest_sequence = 0

        for record in existing_records:

            parking_id = record.get(
                "parking_id",
                ""
            )

            if not parking_id.startswith(prefix):
                continue

            sequence_part = parking_id[
                len(prefix):
            ]

            try:
                sequence = int(
                    sequence_part
                )

            except ValueError:
                continue

            if sequence > highest_sequence:
                highest_sequence = sequence

        return (
            f"{prefix}"
            f"{highest_sequence + 1:02d}"
        )

    # Start a parking session when a registered
    # customer arrives.

    def start_parking(
        self,
        user
    ):
        # A user can have only one active
        # parking session at a time.
        existing_session = (
            self.get_session_by_user_id(
                user.user_id
            )
        )

        if existing_session is not None:

            print(
                "\nThis user is already"
                "in this parking facility"
            )

            print("-" * 40)

            print(
                f"User ID:       "
                f"{existing_session.user_id}"
            )

            print(
                f"Parking ID:    "
                f"{existing_session.parking_id}"
            )

            print(
                f"Parking space: "
                f"{existing_session.parking_space}"
            )

            print(
                f"Parking type:  "
                f"{existing_session.parking_type}"
            )

            print(
                f"In time:       "
                f"{existing_session.in_time}"
            )

            if existing_session.parking_type == "BOOKED":

                print(
                    f"Booked hours:  "
                    f"{existing_session.booked_hours:g}"
                )

                print(
                    f"Booking ends:  "
                    f"{existing_session.booking_end}"
                )

            print(
                "\nNo user can avail 2 parking sessions simultaneously"
            )

            return None

        # Record the exact time when the vehicle enters.
        in_time = datetime.now()

        available_spaces = (
            self._get_available_spaces()
        )

        if not available_spaces:
            print(
                "No parking space is currently available"
            )
            return None

        confirmed_space = None

        if user.is_ev():

            # First look for an ev space.
            confirmed_space = (
                self._find_available_ev_space(
                    available_spaces
                )
            )

            # No ev space is available.
            if confirmed_space is None:

                fallback_space = (
                    self._find_ev_fallback_space(
                        available_spaces,
                        user.width
                    )
                )

                if fallback_space is None:
                    print(
                        "No suitable parking space "
                        "is available"
                    )
                    return None

                print(
                    f"\nThe available suitable space "
                    f"{fallback_space.space_number} "
                    "is a non-ev parking space"
                )

                print(
                    "Would you like to park in "
                    "this space?"
                )
                print("1. Yes")
                print("2. No")

                ev_choice = input(
                    "Enter your choice: "
                ).strip()

                if ev_choice == "2":

                    print("\nParking refused")
                    print(
                        "Kindly exit within 2 minutes"
                    )
                    print(
                        "Total cost: Kr 0.00"
                    )

                    return None

                if ev_choice != "1":
                    print(
                        "Invalid choice"
                    )
                    print(
                        "Parking cancelled"
                    )
                    return None

                # The ev customer accepted the
                # non-ev space.
                confirmed_space = fallback_space

        print(
            "\nWould you like to book a parking time?"
        )
        print("1. Yes")
        print("2. No")

        choice = input(
            "Enter your choice: "
        ).strip()

        if choice == "1":

            parking_type = "BOOKED"

            while True:
                try:
                    booked_hours = float(
                        input(
                            "How many hours would "
                            "you like to book? "
                        )
                    )

                    if booked_hours <= 0:
                        print(
                            "Please enter a positive "
                            "number"
                        )
                        continue

                    break

                except ValueError:
                    print(
                        "Please enter a valid number"
                    )

            # Booking begins at exactly the same
            # time as vehicle entry.
            booking_end = (
                in_time
                + timedelta(
                    hours=booked_hours
                )
            )

        elif choice == "2":

            parking_type = "UNBOOKED"
            booked_hours = None
            booking_end = None

        else:
            print("Invalid choice")
            return None

        # If the ev customer already accepted a
        # non-ev fallback space, keep that space.
        #
        # Otherwise, apply the normal allocation rules.
        if confirmed_space is None:

            expected_hours = (
                booked_hours
                if booked_hours is not None
                else 0
            )

            confirmed_space = (
                self.find_parking_space(
                    is_ev=user.is_ev(),
                    vehicle_width=user.width,
                    expected_hours=expected_hours
                )
            )

            if confirmed_space is None:
                print(
                    "No suitable parking space "
                    "is available"
                )
                return None

        parking_id = (
            self._generate_parking_id(
                user.user_id,
                in_time
            )
        )

        in_time_string = in_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        booking_end_string = (
            booking_end.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            if booking_end
            else None
        )

        session = ParkingSession(
            parking_id=parking_id,
            user_id=user.user_id,
            parking_type=parking_type,
            parking_space=confirmed_space.space_number,
            in_time=in_time_string,
            booked_hours=booked_hours,
            booking_end=booking_end_string
        )

        # Occupy the confirmed physical space.
        confirmed_space.occupy(
            user.user_id
        )

        # Store the active session.
        self.active_sessions[
            parking_id
        ] = session

        # Save the current active sessions.
        ParkingSession.save_active_sessions(
            self.active_sessions.values()
        )

        print("\nParking confirmed")

        print(
            f"Parking ID:       {parking_id}"
        )

        print(
            f"Parking space:    "
            f"{confirmed_space.space_number}"
        )

        print(
            f"In time:          "
            f"{in_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if parking_type == "BOOKED":

            print(
                f"Booking starts:   "
                f"{in_time.strftime('%Y-%m-%d %H:%M:%S')}"
            )

            print(
                f"Booked hours:     "
                f"{booked_hours:g}"
            )

            print(
                f"Booking ends:     "
                f"{booking_end.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        return session

    # Return an active parking session using
    # its parking ID.
    def get_session(
        self,
        parking_id
    ):
        return self.active_sessions.get(
            parking_id
        )

    def get_session_by_user_id(self, user_id):
        user_id = user_id.strip().lower()

        for session in self.active_sessions.values():
            if session.user_id.lower() == user_id:
                return session

        return None

    # Complete a parking session and calculate
    # the final charge.

    def exit_parking(
        self,
        parking_id,
    ):
        session = self.get_session(
            parking_id
        )

        if session is None:
            print(
                "No active parking session found"
            )
            return None

        out_time = datetime.now()

        is_weekend = (
            out_time.weekday() >= 5
        )

        in_time = datetime.strptime(
            session.in_time,
            "%Y-%m-%d %H:%M:%S"
        )

        duration = (
            out_time - in_time
        )

        duration_minutes = max(
            0,
            int(
                duration.total_seconds()
                / 60
            )
        )

        grace_period = timedelta(
            minutes=self.EXIT_GRACE_MINUTES
        )

        if session.parking_type == "BOOKED":

            booking_end = datetime.strptime(
                session.booking_end,
                "%Y-%m-%d %H:%M:%S"
            )

            grace_end = (
                booking_end
                + grace_period
            )

            if out_time <= grace_end:

                # Customer leaves before or within
                # the courtesy period.
                #
                # No overtime is charged.
                cost, pricing_breakdown = (
                    self.pricing
                    .calculate_booked_charge(
                        session.booked_hours,
                        is_weekend
                    )
                )

                pricing_breakdown[
                    "early_departure"
                ] = (
                    out_time < booking_end
                )

                pricing_breakdown[
                    "actual_duration_minutes"
                ] = duration_minutes

                pricing_breakdown[
                    "overtime_minutes"
                ] = 0

                pricing_breakdown[
                    "exit_grace_minutes"
                ] = self.EXIT_GRACE_MINUTES

            else:

                # Customer has exceeded the courtesy
                # period.
                #
                # The grace period only determines
                # whether overtime is charged.
                #
                # Actual overtime is calculated from
                # the original booking end.
                overtime = (
                    out_time - booking_end
                )

                overtime_minutes = max(
                    1,
                    int(
                        overtime.total_seconds()
                        / 60
                    )
                )

                cost, pricing_breakdown = (
                    self.pricing
                    .calculate_booked_with_overtime(
                        session.booked_hours,
                        overtime_minutes,
                        is_weekend
                    )
                )

                pricing_breakdown[
                    "actual_duration_minutes"
                ] = duration_minutes

                pricing_breakdown[
                    "overtime_minutes"
                ] = overtime_minutes

                pricing_breakdown[
                    "exit_grace_minutes"
                ] = self.EXIT_GRACE_MINUTES

        else:

            # The first two minutes are free.
            #
            # The grace period is used operationally
            # but is kept only in the internal history.
            billable_minutes = max(
                0,
                duration_minutes
                - self.EXIT_GRACE_MINUTES
            )

            if billable_minutes == 0:

                cost = 0

                pricing_breakdown = {
                    "parking_type": "UNBOOKED",
                    "grace_period_minutes": (
                        self.EXIT_GRACE_MINUTES
                    ),
                    "actual_duration_minutes": (
                        duration_minutes
                    ),
                    "billable_duration_minutes": 0,
                    "charge_before_discount": 0,
                    "weekend": is_weekend,
                    "weekend_discount": (
                        self.pricing.weekend_discount
                        if is_weekend
                        else 0
                    ),
                    "total": 0
                }

            else:

                cost, pricing_breakdown = (
                    self.pricing
                    .calculate_unbooked_charge(
                        billable_minutes,
                        is_weekend
                    )
                )

                pricing_breakdown[
                    "grace_period_minutes"
                ] = self.EXIT_GRACE_MINUTES

                pricing_breakdown[
                    "actual_duration_minutes"
                ] = duration_minutes

                pricing_breakdown[
                    "billable_duration_minutes"
                ] = billable_minutes

        session.complete_session(
            out_time=out_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            actual_duration=duration_minutes,
            cost=cost,
            pricing_breakdown=pricing_breakdown
        )

        # Release the physical parking space.
        for space in (
            self.parking_facility
            .get_all_spaces()
        ):
            if (
                space.space_number
                == session.parking_space
            ):
                space.release()
                break

        # Save the completed parking incident.
        self.data_manager.save_history(
            session.to_dict()
        )

        # Remove the session from active parking.
        del self.active_sessions[
            parking_id
        ]

        # Update temporary active-session storage.
        if self.active_sessions:
            ParkingSession.save_active_sessions(
                self.active_sessions.values()
            )
        else:
            ParkingSession.clear_active_sessions()

        print("\nParking completed")
        print(
            f"Parking ID: {parking_id}"
        )
        print(
            f"Parking space: "
            f"{session.parking_space}"
        )
        print(
            f"In time: "
            f"{session.in_time}"
        )

        if session.parking_type == "BOOKED":
            print(
                f"Booking: "
                f"{session.booked_hours:g} hours"
            )
            print(
                f"Booking ends: "
                f"{session.booking_end}"
            )

        print(
            f"Out time: "
            f"{session.out_time}"
        )

        if duration_minutes == 1:
            duration_text = "1 minute"
        else:
            duration_text = (
                f"{duration_minutes} minutes"
            )

        print(
            f"Duration: {duration_text}"
        )

        print(
            f"Total cost: Kr {cost:.2f}"
        )

        return session
