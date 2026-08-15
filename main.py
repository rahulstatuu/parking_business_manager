from datetime import datetime, timedelta

from data_manager import DataManager
from parking_facility import ParkingFacility
from parking_manager import ParkingManager
from pricing import Pricing
from user_manager import UserManager


APP_TITLE = "PARKING BUSINESS MANAGEMENT"
LINE = "=" * 60


def print_header(title):
    print("\n" + LINE)
    print(title.center(60))
    print(LINE)


def create_system():
    data_manager = DataManager()
    parking_facility = ParkingFacility()
    pricing = Pricing()

    user_manager = UserManager(
        data_manager
    )

    parking_manager = ParkingManager(
        parking_facility=parking_facility,
        data_manager=data_manager,
        pricing=pricing
    )

    return (
        data_manager,
        parking_facility,
        user_manager,
        parking_manager
    )


# ============================================================
# USER MANAGEMENT
# ============================================================

def add_user(user_manager):
    print_header("ADD USER")

    car_model = input(
        "Car model: "
    ).strip()

    registration_no = input(
        "Registration number: "
    ).strip()

    vehicle_type = input(
        "Vehicle type (ev/non-ev): "
    ).strip().lower()

    while vehicle_type not in {"ev", "non-ev"}:
        print(
            "Please enter either 'ev' or 'non-ev'."
        )

        vehicle_type = input(
            "Vehicle type (ev/non-ev): "
        ).strip().lower()

    while True:
        try:
            width = float(
                input(
                    "Vehicle width (cm): "
                ).strip()
            )

            if width <= 0:
                print(
                    "Please enter a positive number."
                )
                continue

            break

        except ValueError:
            print(
                "Please enter a valid number."
            )

    driver_cell = input(
        "Driver cell: "
    ).strip()

    while True:

        print("\nUser information")
        print("-" * 40)

        print(
            f"Car model: {car_model}"
        )

        print(
            f"Registration: {registration_no}"
        )

        print(
            f"Vehicle type: {vehicle_type}"
        )

        print(
            f"Width: {width}"
        )

        print(
            f"Driver cell: {driver_cell}"
        )

        print("\nWhat would you like to do?")
        print("1. Add")
        print("2. Modify")
        print("3. Cancel")

        choice = input(
            "Enter your choice: "
        ).strip()

        # ----------------------------------------------------
        # ADD
        # ----------------------------------------------------
        if choice == "1":

            user_manager.add_user(
                car_model=car_model,
                registration_no=registration_no,
                vehicle_type=vehicle_type,
                width=width,
                driver_cell=driver_cell
            )

            return

        # ----------------------------------------------------
        # MODIFY
        # ----------------------------------------------------
        elif choice == "2":

            print(
                "\nWhich field would you like to modify?"
            )

            print("1. Car model")
            print("2. Registration number")
            print("3. Vehicle type")
            print("4. Vehicle width")
            print("5. Driver cell")

            field = input(
                "Enter your choice: "
            ).strip()

            if field == "1":

                car_model = input(
                    "New car model: "
                ).strip()

            elif field == "2":

                registration_no = input(
                    "New registration number: "
                ).strip()

            elif field == "3":

                while True:

                    vehicle_type = input(
                        "New vehicle type (ev/non-ev): "
                    ).strip().lower()

                    if vehicle_type in {
                        "ev",
                        "non-ev"
                    }:
                        break

                    print(
                        "Please enter either "
                        "'ev' or 'non-ev'."
                    )

            elif field == "4":

                while True:

                    try:

                        new_width = float(
                            input(
                                "New vehicle width (cm): "
                            ).strip()
                        )

                        if new_width <= 0:

                            print(
                                "Please enter a "
                                "positive number."
                            )

                            continue

                        width = new_width
                        break

                    except ValueError:

                        print(
                            "Please enter a valid number."
                        )

            elif field == "5":

                driver_cell = input(
                    "New driver cell: "
                ).strip()

            else:

                print(
                    "\nInvalid choice."
                )

        # ----------------------------------------------------
        # CANCEL
        # ----------------------------------------------------
        elif choice == "3":

            print(
                "\nUser addition cancelled."
            )

            return

        else:

            print(
                "\nInvalid choice."
            )


def find_user(user_manager):
    print_header("FIND USER")

    print("Search user by:")
    print("1. User ID")
    print("2. Car model")
    print("3. Registration number")
    print("4. Driver cell")

    choice = input(
        "\nEnter your choice: "
    ).strip()

    if choice == "1":
        search_field = "user_id"
        field_name = "user ID"

    elif choice == "2":
        search_field = "car_model"
        field_name = "car model"

    elif choice == "3":
        search_field = "registration_no"
        field_name = "registration number"

    elif choice == "4":
        search_field = "driver_cell"
        field_name = "driver cell"

    else:
        print(
            "\nInvalid choice."
        )
        return

    search_value = input(
        f"Enter {field_name}: "
    ).strip()

    if not search_value:
        print(
            "\nPlease enter a search value."
        )
        return

    users = user_manager.find_user(
        search_field,
        search_value
    )

    if not users:
        print(
            "\nNo matching user found."
        )
        return

    print(
        f"\nFound {len(users)} "
        f"matching user(s)"
    )

    for user in users:

        print("-" * 40)

        print(
            f"User ID:       {user.user_id}"
        )

        print(
            f"Car model:     {user.car_model}"
        )

        print(
            f"Registration:  "
            f"{user.registration_no}"
        )

        print(
            f"Vehicle type:  "
            f"{user.vehicle_type}"
        )

        print(
            f"Width:         "
            f"{user.width} cm"
        )

        print(
            f"Driver cell:   "
            f"{user.driver_cell}"
        )

    print("-" * 40)


def get_all_users(user_manager):
    print_header("VIEW USERS")

    users = user_manager.get_all_users()

    if not users:
        print(
            "No registered users found."
        )
        return

    for user in users:
        print("-" * 50)

        print(
            f"User ID:          {user.user_id}"
        )

        print(
            f"Car model:        {user.car_model}"
        )

        print(
            f"Registration:     {user.registration_no}"
        )

        print(
            f"Vehicle type:     {user.vehicle_type}"
        )

        print(
            f"Vehicle width:    {user.width} cm"
        )

        print(
            f"Driver cell:      {user.driver_cell}"
        )

    print("-" * 50)


def delete_user(
    user_manager,
    parking_manager
):
    print_header("DELETE USER")

    user_input = input(
        "Enter user ID: "
    ).strip()

    if not user_input:
        print(
            "\nPlease enter a user ID."
        )
        return

    # Check whether any requested user
    # currently has an active parking session.
    requested_ids = set()

    parts = user_input.lower().split(",")

    for part in parts:
        part = part.strip()

        if not part:
            continue

        if "-" in part:
            range_parts = part.split("-")

            if len(range_parts) != 2:
                continue

            start_id = range_parts[0].strip()
            end_id = range_parts[1].strip()

            if (
                not start_id.startswith("u")
                or not end_id.startswith("u")
            ):
                continue

            try:
                start_number = int(
                    start_id[1:]
                )

                end_number = int(
                    end_id[1:]
                )

            except ValueError:
                continue

            if start_number > end_number:
                continue

            for number in range(
                start_number,
                end_number + 1
            ):
                requested_ids.add(
                    f"u{number:04d}"
                )

        else:
            if not part.startswith("u"):
                continue

            try:
                number = int(part[1:])

                requested_ids.add(
                    f"u{number:04d}"
                )

            except ValueError:
                continue

    if not requested_ids:
        print(
            "\nNo valid user IDs entered."
        )
        return

    # Check active parking sessions.
    active_user_ids = {
        session.user_id.lower()
        for session
        in parking_manager.active_sessions.values()
    }

    parked_users = (
        requested_ids
        & active_user_ids
    )

    if parked_users:
        print(
            "\nThe following user(s) "
            "currently have an active "
            "parking session:"
        )

        print("-" * 40)

        for user_id in sorted(parked_users):
            print(user_id)

        print("-" * 40)

        print(
            "\nThis user(s) cannot be deleted "
            "until completing its parking session(s)"
        )

        return

    # No requested user is currently parked.
    user_manager.delete_user(
        user_input
    )


# ============================================================
# PARKING
# ============================================================

def start_parking(
    user_manager,
    parking_manager
):
    print_header("START PARKING")

    user_id = input(
        "Enter user ID: "
    ).strip()

    users = user_manager.find_user(
        "user_id",
        user_id
    )

    if not users:
        print(
            "\nNo user found with that ID."
        )
        return

    user = users[0]

    print("\nUser")
    print("-" * 40)
    print(user)

    parking_manager.start_parking(
        user
    )


def exit_parking(parking_manager):
    print_header("EXIT PARKING")

    if not parking_manager.active_sessions:
        print(
            "No parking session is currently going on."
        )
        return

    user_id = input(
        "Enter user ID: "
    ).strip()

    session = (
        parking_manager.get_session_by_user_id(
            user_id
        )
    )

    if session is None:
        print(
            "\nNo active parking session "
            "found for this user."
        )
        return

    print("\nActive parking session")
    print("-" * 40)

    print(
        f"User ID:       {session.user_id}"
    )

    print(
        f"Parking ID:    {session.parking_id}"
    )

    print(
        f"Parking space: {session.parking_space}"
    )

    print(
        f"Parking type:  {session.parking_type}"
    )

    print(
        f"In time:       {session.in_time}"
    )

    if session.parking_type == "BOOKED":
        print(
            f"Booked hours:  "
            f"{session.booked_hours:g}"
        )

        print(
            f"Booking ends:  "
            f"{session.booking_end}"
        )

    print("\nEnding parking...")

    parking_manager.exit_parking(
        session.parking_id
    )


# ============================================================
# FACILITY / SESSION INFORMATION
# ============================================================

def get_all_spaces(parking_facility):
    print_header("PARKING SPACES")

    spaces = parking_facility.get_all_spaces()

    if not spaces:
        print(
            "No parking spaces found."
        )
        return

    total_ev = sum(
        space.is_ev
        for space in spaces
    )

    occupied_ev = sum(
        space.is_ev
        and space.is_occupied
        for space in spaces
    )

    remaining_ev = (
        total_ev
        - occupied_ev
    )

    total_non_ev = sum(
        not space.is_ev
        for space in spaces
    )

    occupied_non_ev = sum(
        not space.is_ev
        and space.is_occupied
        for space in spaces
    )

    remaining_non_ev = (
        total_non_ev
        - occupied_non_ev
    )

    total_space = len(spaces)

    total_occupied = sum(
        space.is_occupied
        for space in spaces
    )

    total_remaining = (
        total_space
        - total_occupied
    )

    print(
        f"Total EV space:          {total_ev}"
    )

    print(
        f"Occupied EV space:       {occupied_ev}"
    )

    print(
        f"Remaining EV space:      {remaining_ev}"
    )

    print(
        f"\nTotal non-EV space:      {total_non_ev}"
    )

    print(
        f"Occupied non-EV space:   {occupied_non_ev}"
    )

    print(
        f"Remaining non-EV space:  {remaining_non_ev}"
    )

    print(
        f"\nTotal space:             {total_space}"
    )

    print(
        f"Total occupied space:    {total_occupied}"
    )

    print(
        f"Total remaining space:   {total_remaining}"
    )


def get_active_sessions(parking_manager):
    print_header("ACTIVE PARKING")

    sessions = parking_manager.active_sessions

    if not sessions:
        print("No active parking session")
        return

    for session in sessions.values():
        print("-" * 60)

        print(
            f"Parking ID:    {session.parking_id}"
        )

        print(
            f"User ID:       {session.user_id}"
        )

        print(
            f"Parking space: {session.parking_space}"
        )

        print(
            f"Parking type:  {session.parking_type}"
        )

        print(
            f"In time:       {session.in_time}"
        )

        if session.parking_type == "BOOKED":
            print(
                f"Booked hours:  {session.booked_hours:g}"
            )

            print(
                f"Booking ends:  {session.booking_end}"
            )


def get_parking_history(
    data_manager,
    user_manager
):
    print_header("PARKING HISTORY")

    print(
        "Whose parking history would "
        "you like to see?"
    )

    print("1. All users")
    print("2. Individual user")
    print("3. Cancel")

    choice = input(
        "\nEnter your choice: "
    ).strip()

    if choice == "3":
        return

    if choice not in {"1", "2"}:
        print(
            "\nInvalid choice."
        )
        return

    selected_user_id = None

    if choice == "2":

        user_id = input(
            "\nEnter user ID: "
        ).strip()

        users = user_manager.find_user(
            "user_id",
            user_id
        )

        if not users:
            print(
                "\nNo user found with "
                "that ID."
            )
            return

        user = users[0]
        selected_user_id = user.user_id

        print("\nUser")
        print("-" * 50)

        print(
            f"User ID:       {user.user_id}"
        )

        print(
            f"Car model:     {user.car_model}"
        )

        print(
            f"Registration:  "
            f"{user.registration_no}"
        )

        print(
            f"Driver cell:   "
            f"{user.driver_cell}"
        )

        print("-" * 50)

    print(
        "\nHow would you like to "
        "filter the time?"
    )

    print("1. All history")
    print("2. Today")
    print("3. Last 7 days")
    print("4. Last 30 days")
    print("5. Custom date range")
    print("6. Back")

    time_choice = input(
        "\nEnter your choice: "
    ).strip()

    if time_choice == "6":
        return

    if time_choice not in {
        "1",
        "2",
        "3",
        "4",
        "5"
    }:
        print(
            "\nInvalid choice."
        )
        return

    history = data_manager.load_history()

    if selected_user_id is not None:
        history = [
            record
            for record in history
            if record.get("user_id", "")
            .strip()
            .lower()
            == selected_user_id.strip().lower()
        ]

    start_date = None
    end_date = None

    today = datetime.now().date()

    if time_choice == "2":

        start_date = today
        end_date = today

    elif time_choice == "3":

        start_date = (
            today - timedelta(days=6)
        )
        end_date = today

    elif time_choice == "4":

        start_date = (
            today - timedelta(days=29)
        )
        end_date = today

    elif time_choice == "5":

        while True:
            start_input = input(
                "\nEnter start date "
                "(YYYY-MM-DD): "
            ).strip()

            try:
                start_date = (
                    datetime.strptime(
                        start_input,
                        "%Y-%m-%d"
                    ).date()
                )
                break

            except ValueError:
                print(
                    "Please enter a valid "
                    "date in YYYY-MM-DD format."
                )

        while True:
            end_input = input(
                "Enter end date "
                "(YYYY-MM-DD): "
            ).strip()

            try:
                end_date = (
                    datetime.strptime(
                        end_input,
                        "%Y-%m-%d"
                    ).date()
                )

                if end_date < start_date:
                    print(
                        "End date cannot be "
                        "before the start date."
                    )
                    continue

                break

            except ValueError:
                print(
                    "Please enter a valid "
                    "date in YYYY-MM-DD format."
                )

    if start_date is not None:

        filtered_history = []

        for record in history:

            in_time = record.get(
                "in_time",
                ""
            )

            try:
                record_date = (
                    datetime.strptime(
                        in_time,
                        "%Y-%m-%d %H:%M:%S"
                    ).date()
                )

            except ValueError:
                continue

            if (
                start_date
                <= record_date
                <= end_date
            ):
                filtered_history.append(
                    record
                )

        history = filtered_history

    print_header("PARKING HISTORY")

    if selected_user_id is None:
        print("ALL USERS")
    else:
        print(
            f"USER: {selected_user_id}"
        )

    if time_choice == "1":
        print("TIME RANGE: ALL HISTORY")

    elif time_choice == "2":
        print(
            "TIME RANGE: TODAY"
        )

    elif time_choice == "3":
        print(
            "TIME RANGE: LAST 7 DAYS"
        )

    elif time_choice == "4":
        print(
            "TIME RANGE: LAST 30 DAYS"
        )

    elif time_choice == "5":
        print(
            "TIME RANGE: "
            f"{start_date} TO {end_date}"
        )

    print()

    if not history:
        print(
            "No completed parking sessions "
            "found for the selected "
            "criteria."
        )
        return

    for record in history:

        print("-" * 60)

        print(
            f"Parking ID:    "
            f"{record.get('parking_id', '')}"
        )

        print(
            f"User ID:       "
            f"{record.get('user_id', '')}"
        )

        print(
            f"Parking space: "
            f"{record.get('parking_space', '')}"
        )

        print(
            f"Parking type:  "
            f"{record.get('parking_type', '')}"
        )

        print(
            f"In time:       "
            f"{record.get('in_time', '')}"
        )

        print(
            f"Out time:      "
            f"{record.get('out_time', '')}"
        )

        print(
            f"Duration:      "
            f"{record.get('actual_duration', '')} "
            f"minutes"
        )

        print(
            f"Total cost:    "
            f"Kr {record.get('cost', 0):.2f}"
        )

    print("-" * 60)


# ============================================================
# MENU
# ============================================================

def show_menu():
    print_header(APP_TITLE)

    print("1. Add user")
    print("2. Start parking")
    print("3. Exit parking")
    print("4. Find user")
    print("5. View all users")
    print("6. View space occupancy")
    print("7. View currently parked users")
    print("8. View parking history")
    print("9. Delete user")
    print("10. Exit")


def main():
    (
        data_manager,
        parking_facility,
        user_manager,
        parking_manager
    ) = create_system()

    while True:
        show_menu()

        choice = input(
            "\nEnter your choice: "
        ).strip()

        if choice == "1":
            add_user(user_manager)

        elif choice == "2":
            start_parking(
                user_manager,
                parking_manager
            )

        elif choice == "3":
            exit_parking(
                parking_manager
            )

        elif choice == "4":
            find_user(
                user_manager
            )

        elif choice == "5":
            get_all_users(
                user_manager
            )

        elif choice == "6":
            get_all_spaces(
                parking_facility
            )

        elif choice == "7":
            get_active_sessions(
                parking_manager
            )

        elif choice == "8":
            get_parking_history(
                data_manager,
                user_manager
            )

        elif choice == "9":
            delete_user(
                user_manager,
                parking_manager
            )

        elif choice == "10":
            print("\nExited")

            print("Thank you for using "
                  "PARKING BUSINESS MANAGER"
                  )

            break

        else:
            print(
                "\nInvalid choice. "
                "Please select a number from 1 to 10."
            )


if __name__ == "__main__":
    main()
