from user import User


"""
Manage registered parking users.

The UserManager handles adding, deleting, searching,
and retrieving registered users.

User IDs are generated and managed by UserManager
and user information is stored through DataManager
in users.json.
"""


class UserManager:

    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.users = self.data_manager.load_users()

    def _generate_user_id(self):
        used_numbers = set()

        for user in self.users:
            user_id = user["user_id"].lower()

            if user_id.startswith("u"):
                try:
                    number = int(user_id[1:])
                    used_numbers.add(number)

                except ValueError:
                    continue

        number = 1

        while number in used_numbers:
            number += 1

        return f"u{number:04d}"

    # Add new user and save it.
    def add_user(
        self,
        car_model,
        registration_no,
        vehicle_type,
        width,
        driver_cell
    ):
        car_model = car_model.strip().lower()
        registration_no = registration_no.strip().lower()
        vehicle_type = vehicle_type.strip().lower()
        driver_cell = driver_cell.strip()

        for user in self.users:

            existing_registration = (
                user["registration_no"]
                .strip()
                .lower()
            )

            if existing_registration == registration_no:

                print(
                    f"\nRegistration number "
                    f"{registration_no} is already registered"
                )

                print(
                    f"Existing user: "
                    f"{user['user_id']}"
                )

                return None

        user_id = self._generate_user_id()

        user = User(
            user_id=user_id,
            car_model=car_model,
            registration_no=registration_no,
            vehicle_type=vehicle_type,
            width=width,
            driver_cell=driver_cell
        )

        self.users.append(
            user.to_dict()
        )

        self.data_manager.save_users(
            self.users
        )

        print("\nUser added")
        print(
            f"User ID: {user.user_id}"
        )

        return user

    def find_user(
        self,
        search_field,
        search_value
    ):
        search_value = (
            search_value.strip().lower()
        )

        matches = []

        for user_data in self.users:

            if search_field == "user_id":
                value = user_data["user_id"]

            elif search_field == "car_model":
                value = user_data["car_model"]

            elif search_field == "registration_no":
                value = user_data["registration_no"]

            elif search_field == "driver_cell":
                value = user_data["driver_cell"]

            else:
                return []

            if search_value in value.strip().lower():
                matches.append(
                    User(**user_data)
                )

        return matches

    def get_all_users(self):
        return [
            User(**user_data)
            for user_data in self.users
        ]

    # Delete user and remove from the record.
    def delete_user(self, user_input):
        user_input = user_input.lower().strip()

        requested_ids = set()

        parts = user_input.split(",")

        for part in parts:
            part = part.strip()

            if not part:
                continue

            if "-" in part:
                range_parts = part.split("-")

                if len(range_parts) != 2:
                    print(f"Invalid range: {part}")
                    continue

                start_id = range_parts[0].strip()
                end_id = range_parts[1].strip()

                if (
                    not start_id.startswith("u")
                    or not end_id.startswith("u")
                ):
                    print(
                        f"Invalid user ID range: {part}"
                    )
                    continue

                try:
                    start_number = int(start_id[1:])
                    end_number = int(end_id[1:])

                except ValueError:
                    print(
                        f"Invalid user ID range: {part}"
                    )
                    continue

                if start_number > end_number:
                    print(
                        f"Invalid range: {part}"
                    )
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
                    print(
                        f"Invalid user ID: {part}"
                    )
                    continue

                try:
                    number = int(part[1:])

                    requested_ids.add(
                        f"u{number:04d}"
                    )

                except ValueError:
                    print(
                        f"Invalid user ID: {part}"
                    )

        if not requested_ids:
            print("No valid user IDs entered")
            return False

        users_to_delete = [
            user
            for user in self.users
            if user["user_id"].lower()
            in requested_ids
        ]

        missing_ids = (
            requested_ids
            - {
                user["user_id"].lower()
                for user in users_to_delete
            }
        )

        if not users_to_delete:
            print("No matching users found")
            return False

        print("\nUsers selected for deletion")
        print("-" * 40)

        for user in users_to_delete:
            print(
                f"User ID: {user['user_id']}"
            )
            print(
                f"Car model: {user['car_model']}"
            )
            print(
                f"Registration: "
                f"{user['registration_no']}"
            )
            print(
                f"Vehicle type: "
                f"{user['vehicle_type']}"
            )
            print()

        if missing_ids:
            print("User IDs not found:")
            print(
                ", ".join(
                    sorted(missing_ids)
                )
            )

        print(
            f"Are you sure you want to delete "
            f"{len(users_to_delete)} user(s)?"
        )

        print("1. Yes")
        print("2. No")

        choice = input(
            "Enter your choice: "
        ).strip()

        if choice != "1":
            print("\nDeletion cancelled")
            return False

        self.users = [
            user
            for user in self.users
            if user["user_id"].lower()
            not in requested_ids
        ]

        self.data_manager.save_users(
            self.users
        )

        print(
            f"\n{len(users_to_delete)} "
            f"user(s) deleted"
        )

        return True
