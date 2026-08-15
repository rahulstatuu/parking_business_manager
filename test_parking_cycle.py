"""
Comprehensive regression tests for the parking facility system.

The tests verify parking booking, unbooked parking, pricing,
overtime, grace periods, EV fallback behavior, invalid input,
parking-space availability, parking-space release, and parking
ID generation.

The production classes are tested without changing their
business logic.
"""


from unittest.mock import patch
from datetime import datetime

from data_manager import DataManager
from parking_facility import ParkingFacility
from parking_manager import ParkingManager
from pricing import Pricing
from user import User


# ============================================================
# TEST SETUP
# ============================================================

data_manager = DataManager()
parking_facility = ParkingFacility()
pricing = Pricing()

parking_manager = ParkingManager(
    parking_facility,
    data_manager,
    pricing
)

user = User(
    user_id="u0001",
    car_model="Tesla Model Y",
    registration_no="TEST001",
    vehicle_type="ev",
    width=180,
    driver_cell="0701000001"
)


# ============================================================
# CONTROLLED DATETIME FOR TESTING
# ============================================================

class MockDateTime(datetime):

    current_time = None

    @classmethod
    def now(cls):
        return cls.current_time


def set_test_time(test_time):
    MockDateTime.current_time = test_time


def run_with_test_time(test_time, function):
    set_test_time(test_time)

    with patch(
        "parking_manager.datetime",
        MockDateTime
    ):
        return function()


# ============================================================
# TEST RESULT HELPER
# ============================================================

def print_test_result(
    description,
    passed,
    details=""
):
    print("\n## TEST RESULT")
    print("-" * 40)

    if passed:
        print("Test passed")
    else:
        print("Test failed")

    print(description)

    if details:
        print(details)


# ============================================================
# TEST 1
# BOOKED PARKING
# ============================================================

print("\n## TEST 1 - BOOKED PARKING")
print("-" * 40)

parking_manager.active_sessions.clear()

start_time = datetime(
    2026, 8, 13, 23, 0, 0
)


def start_booked_parking():
    with patch(
        "builtins.input",
        side_effect=[
            "1",
            "5"
        ]
    ):
        return parking_manager.start_parking(
            user
        )


session = run_with_test_time(
    start_time,
    start_booked_parking
)

passed = (
    session is not None
    and session.parking_type == "BOOKED"
    and session.booked_hours == 5
)

print_test_result(
    "5-hour booked parking was created.",
    passed
)


# ============================================================
# TEST 2
# EXIT EXACTLY AT BOOKING END
# ============================================================

print("\n## TEST 2 - EXIT EXACTLY AT BOOKING END")
print("-" * 40)

booking_end = datetime(
    2026, 8, 14, 4, 0, 0
)

completed = run_with_test_time(
    booking_end,
    lambda: parking_manager.exit_parking(
        session.parking_id
    )
)

passed = (
    completed is not None
    and completed.actual_duration == 300
    and completed.cost == 125
)

print_test_result(
    "Exit exactly at booking end produces no overtime.",
    passed,
    (
        f"Expected duration: 300 minutes\n"
        f"Actual duration:   "
        f"{completed.actual_duration} minutes\n"
        f"Expected cost: Kr 125.00\n"
        f"Actual cost:   Kr {completed.cost:.2f}"
    )
)


# ============================================================
# TEST 3
# EXIT WITHIN GRACE PERIOD
# ============================================================

print("\n## TEST 3 - EXIT WITHIN GRACE PERIOD")
print("-" * 40)

start_time = datetime(
    2026, 8, 13, 23, 0, 0
)

session = run_with_test_time(
    start_time,
    start_booked_parking
)

grace_exit = datetime(
    2026, 8, 14, 4, 2, 0
)

completed = run_with_test_time(
    grace_exit,
    lambda: parking_manager.exit_parking(
        session.parking_id
    )
)

passed = (
    completed is not None
    and completed.actual_duration == 302
    and completed.cost == 125
)

print_test_result(
    "Exit at the end of the two-minute grace period has no overtime charge.",
    passed,
    (
        f"Expected duration: 302 minutes\n"
        f"Actual duration:   "
        f"{completed.actual_duration} minutes\n"
        f"Expected cost: Kr 125.00\n"
        f"Actual cost:   Kr {completed.cost:.2f}"
    )
)


# ============================================================
# TEST 4
# BOOKED PARKING WITH OVERTIME
# ============================================================

print("\n## TEST 4 - BOOKED PARKING WITH OVERTIME")
print("-" * 40)

session = run_with_test_time(
    start_time,
    start_booked_parking
)

overtime_exit = datetime(
    2026, 8, 14, 4, 5, 0
)

completed = run_with_test_time(
    overtime_exit,
    lambda: parking_manager.exit_parking(
        session.parking_id
    )
)

pricing_breakdown = (
    completed.pricing_breakdown
)

actual_overtime = (
    pricing_breakdown.get(
        "overtime_minutes",
        0
    )
)

passed = (
    completed is not None
    and completed.actual_duration == 305
    and actual_overtime == 5
)

print_test_result(
    "Overtime is calculated from booking end, not from grace-period end.",
    passed,
    (
        f"Expected duration: 305 minutes\n"
        f"Actual duration:   "
        f"{completed.actual_duration} minutes\n"
        f"Expected overtime: 5 minutes\n"
        f"Actual overtime:   "
        f"{actual_overtime} minutes\n"
        f"Expected cost: Kr 145.00\n"
        f"Actual cost:   Kr {completed.cost:.2f}"
    )
)


# ============================================================
# TEST 5
# UNBOOKED PARKING
# ============================================================

print("\n## TEST 5 - UNBOOKED PARKING")
print("-" * 40)

start_time = datetime(
    2026, 8, 13, 23, 0, 0
)


def start_unbooked_parking():
    with patch(
        "builtins.input",
        side_effect=["2"]
    ):
        return parking_manager.start_parking(
            user
        )


session = run_with_test_time(
    start_time,
    start_unbooked_parking
)

exit_time = datetime(
    2026, 8, 14, 0, 10, 0
)

completed = run_with_test_time(
    exit_time,
    lambda: parking_manager.exit_parking(
        session.parking_id
    )
)

billable_duration = (
    completed.pricing_breakdown.get(
        "billable_duration_minutes"
    )
)

passed = (
    completed is not None
    and completed.actual_duration == 70
    and billable_duration == 68
    and completed.cost == 60
)

print_test_result(
    "70-minute unbooked parking charges correctly.",
    passed,
    (
        f"Expected duration: 70 minutes\n"
        f"Actual duration:   "
        f"{completed.actual_duration} minutes\n"
        f"Expected billable duration: 68 minutes\n"
        f"Actual billable duration:   "
        f"{billable_duration} minutes\n"
        f"Expected cost: Kr 60.00\n"
        f"Actual cost:   Kr {completed.cost:.2f}"
    )
)


# ============================================================
# TEST 6
# UNBOOKED PARKING WITHIN FIRST TWO MINUTES
# ============================================================

print("\n## TEST 6 - UNBOOKED PARKING WITHIN FIRST TWO MINUTES")
print("-" * 40)

session = run_with_test_time(
    start_time,
    start_unbooked_parking
)

exit_time = datetime(
    2026, 8, 13, 23, 1, 0
)

completed = run_with_test_time(
    exit_time,
    lambda: parking_manager.exit_parking(
        session.parking_id
    )
)

billable_duration = (
    completed.pricing_breakdown.get(
        "billable_duration_minutes"
    )
)

passed = (
    completed is not None
    and completed.actual_duration == 1
    and billable_duration == 0
    and completed.cost == 0
)

print_test_result(
    "One-minute unbooked parking is free.",
    passed,
    (
        f"Expected cost: Kr 0.00\n"
        f"Actual cost:   Kr {completed.cost:.2f}\n"
        f"Expected billable duration: 0 minutes\n"
        f"Actual billable duration:   "
        f"{billable_duration} minutes"
    )
)


# ============================================================
# TEST 7
# INVALID BOOKING INPUT
# ============================================================

print("\n## TEST 7 - INVALID BOOKING INPUT")
print("-" * 40)


def start_invalid_input_test():
    with patch(
        "builtins.input",
        side_effect=[
            "1",
            "abc",
            "0",
            "5"
        ]
    ):
        return parking_manager.start_parking(
            user
        )


session = run_with_test_time(
    start_time,
    start_invalid_input_test
)

passed = (
    session is not None
    and session.parking_type == "BOOKED"
    and session.booked_hours == 5
)

print_test_result(
    "Invalid booking inputs were rejected and valid input was accepted.",
    passed
)

if session is not None:
    run_with_test_time(
        start_time,
        lambda: parking_manager.exit_parking(
            session.parking_id
        )
    )


# ============================================================
# TEST 8
# INVALID BOOKING MENU CHOICE
# ============================================================

print("\n## TEST 8 - INVALID BOOKING MENU CHOICE")
print("-" * 40)

before = len(
    parking_manager.active_sessions
)


def start_invalid_menu_test():
    with patch(
        "builtins.input",
        side_effect=["9"]
    ):
        return parking_manager.start_parking(
            user
        )


session = run_with_test_time(
    start_time,
    start_invalid_menu_test
)

after = len(
    parking_manager.active_sessions
)

passed = (
    session is None
    and before == after
)

print_test_result(
    "Invalid menu choice was rejected.",
    passed,
    (
        "No parking session was created.\n"
        "No parking space was occupied."
    )
)


# ============================================================
# TEST 9
# EV ACCEPTS NON-EV FALLBACK
# ============================================================

print("\n## TEST 9 - EV ACCEPTS NON-EV FALLBACK")
print("-" * 40)

# Occupy every EV space so that the parking manager
# must offer a non-EV fallback space.
for space in parking_facility.get_all_spaces():
    if space.is_ev and not space.is_occupied:
        space.occupy("TEST_EV")


def start_ev_fallback_test():
    with patch(
        "builtins.input",
        side_effect=[
            "1",   # Accept non-EV fallback
            "1",   # Book parking
            "5"    # Book for 5 hours
        ]
    ):
        return parking_manager.start_parking(
            user
        )


session = run_with_test_time(
    start_time,
    start_ev_fallback_test
)

if session is None:

    print_test_result(
        "EV customer accepted the non-EV fallback space.",
        False,
        "No parking session was created."
    )

else:

    selected_space = next(
        space
        for space
        in parking_facility.get_all_spaces()
        if space.space_number
        == session.parking_space
    )

    passed = (
        selected_space.is_ev is False
        and session.parking_type == "BOOKED"
        and session.booked_hours == 5
    )

    print_test_result(
        "EV customer accepted the non-EV fallback space.",
        passed,
        (
            f"Selected space: "
            f"{selected_space.space_number}\n"
            f"Space EV status: "
            f"{selected_space.is_ev}\n"
            f"Parking type: "
            f"{session.parking_type}\n"
            f"Booked hours: "
            f"{session.booked_hours}"
        )
    )

    # Complete the parking session.
    run_with_test_time(
        start_time,
        lambda: parking_manager.exit_parking(
            session.parking_id
        )
    )


# Release only the EV spaces that were artificially
# occupied for this test.
for space in parking_facility.get_all_spaces():
    if space.current_user_id == "TEST_EV":
        space.release()


# ============================================================
# TEST 10
# EV REFUSAL
# ============================================================

print("\n## TEST 10 - EV REFUSAL")
print("-" * 40)

# Occupy every EV space again so that the
# non-EV fallback is offered.
for space in parking_facility.get_all_spaces():
    if space.is_ev and not space.is_occupied:
        space.occupy("TEST_EV")


before = len(
    parking_manager.active_sessions
)


def start_ev_refusal_test():
    with patch(
        "builtins.input",
        side_effect=[
            "2"   # Refuse non-EV fallback
        ]
    ):
        return parking_manager.start_parking(
            user
        )


session = run_with_test_time(
    start_time,
    start_ev_refusal_test
)

after = len(
    parking_manager.active_sessions
)

passed = (
    session is None
    and before == after
)

print_test_result(
    "EV customer refused the non-EV parking space.",
    passed,
    (
        "No parking session was created.\n"
        f"Active sessions: {after}"
    )
)


# ============================================================
# TEST 11
# PARKING SPACE RELEASE
# ============================================================

print("\n## TEST 11 - PARKING SPACE RELEASE")
print("-" * 40)

release_test_user = User(
    user_id="u0002",
    car_model="Volvo XC60",
    registration_no="TEST002",
    vehicle_type="non-ev",
    width=180,
    driver_cell="0701000002"
)


def start_release_test():
    with patch(
        "builtins.input",
        side_effect=[
            "2"   # Unbooked parking
        ]
    ):
        return parking_manager.start_parking(
            release_test_user
        )


session = run_with_test_time(
    start_time,
    start_release_test
)

if session is None:

    print_test_result(
        "Parking space is released after exit.",
        False,
        "No parking session was created."
    )

else:

    space_number = session.parking_space

    space = next(
        space
        for space
        in parking_facility.get_all_spaces()
        if space.space_number
        == space_number
    )

    occupied_before_exit = (
        space.is_occupied
    )

    run_with_test_time(
        start_time,
        lambda: parking_manager.exit_parking(
            session.parking_id
        )
    )

    occupied_after_exit = (
        space.is_occupied
    )

    passed = (
        occupied_before_exit is True
        and occupied_after_exit is False
    )

    print_test_result(
        "Parking space is released after exit.",
        passed,
        (
            f"Space: {space_number}\n"
            f"Occupied before exit: "
            f"{occupied_before_exit}\n"
            f"Occupied after exit:  "
            f"{occupied_after_exit}"
        )
    )


# ============================================================
# TEST 12
# NO PARKING SPACE AVAILABLE
# ============================================================

print("\n## TEST 12 - NO PARKING SPACE AVAILABLE")
print("-" * 40)

# Occupy every remaining available space.
for space in parking_facility.get_all_spaces():
    if not space.is_occupied:
        space.occupy("TEST_FULL")


before = len(
    parking_manager.active_sessions
)

session = run_with_test_time(
    start_time,
    start_unbooked_parking
)

after = len(
    parking_manager.active_sessions
)

passed = (
    session is None
    and before == after
)

print_test_result(
    "No parking session is created when all spaces are occupied.",
    passed,
    (
        "All parking spaces were occupied.\n"
        f"Active sessions: {after}"
    )
)


# ============================================================
# TEST 13
# PARKING ID FORMAT
# ============================================================

print("\n## TEST 13 - PARKING ID FORMAT")
print("-" * 40)

# This test checks the ID already generated in Test 1.
parking_id_parts = (
    parking_manager._generate_parking_id(
        "u0001",
        start_time
    )
)

parts = parking_id_parts.split("-")

passed = (
    len(parts) == 3
    and parts[0] == "u0001"
    and parts[1] == "20260813"
    and parts[2].isdigit()
)

print_test_result(
    "Parking ID follows the expected format.",
    passed,
    (
        f"Generated ID: {parking_id_parts}\n"
        "Expected format: u0001-YYYYMMDD-NN"
    )
)


# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("=" * 60)
print("COMPREHENSIVE PARKING REGRESSION TEST COMPLETE")
print("=" * 60)
