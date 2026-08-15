from data_manager import DataManager
from user_manager import UserManager


data_manager = DataManager()
user_manager = UserManager(data_manager)

# user_manager.add_user(
#     car_model="Volvo XC60",
#     registration_no="TEST666",
#     vehicle_type="non-ev",
#     width=180,
#     driver_cell="0701234567"
# )


# user_manager.delete_user("u0011-u0038")
