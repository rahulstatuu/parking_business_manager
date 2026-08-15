import json


"""
Handle reading and writing data to the project's JSON files.

The class is responsible only for data storage. It does not
contain parking allocation, booking, or pricing logic.

User registration data is stored in users.json, while completed
parking transactions are stored in parking_history.json.
"""


class DataManager:

    def __init__(
        self,
        users_file="users.json",
        history_file="parking_history.json"
    ):
        self.users_file = users_file
        self.history_file = history_file

    # Load all registered users from users.json.
    def load_users(self):
        try:
            with open(self.users_file, "r", encoding="utf-8") as file:
                return json.load(file)

        except FileNotFoundError:
            return []

    # Save the current list of registered users to users.json.
    def save_users(self, users):
        with open(self.users_file, "w", encoding="utf-8") as file:
            json.dump(users, file, indent=4)

    # Load all completed parking records from parking_history.json.
    def load_history(self):
        try:
            with open(self.history_file, "r", encoding="utf-8") as file:
                return json.load(file)

        except FileNotFoundError:
            return []

    # Add a completed parking record to parking_history.json.
    def save_history(self, history_record):
        history = self.load_history()
        history.append(history_record)

        with open(self.history_file, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=4)
