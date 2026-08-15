PARKING BUSINESS MANAGER

A Python-based parking facility management system that models the operation of a 60-space underground parking facility.

The application handles user registration, parking allocation, booking, EV requirements, vehicle-size rules, active parking sessions, pricing, overtime, parking history, and persistent operational state.

The interface is simple by design. The business rules behind each parking decision are handled by separate Python classes.

Facility Overview

The parking facility contains 60 underground parking spaces across three floors:

G1: P1–P20

G2: P21–P40

G3: P41–P60

Total spaces: 60

EV spaces: 12

Non-EV spaces: 48

Larger corner spaces: 12

Equal-distance pairs: 30

Lowest floor: G3

Spaces are organized into equal-distance pairs:

P1 / P2

P3 / P4

P5 / P6

...

P59 / P60

When more than one eligible space belongs to the same distance pair, the system can randomly select between them.

Parking Allocation Rules

The system does not simply assign the first available space. It evaluates several conditions before confirming a parking space.

The allocation logic considers:

Vehicle type

EV vehicles are offered suitable EV spaces first.

If no suitable EV space is available, a suitable non-EV fallback can be offered.

The EV driver must accept the fallback space.

Refusing the fallback cancels the parking session.

Vehicle width

Vehicle width is checked before assigning a space.

Vehicles wider than 175 cm receive special allocation consideration.

Suitable corner spaces are considered for wider vehicles.

Booking duration

Longer bookings receive different allocation priority.

Long-stay bookings prioritize lower floors.

G3 is the lowest floor and therefore receives priority for applicable long bookings.

Distance pairs

Spaces are grouped into equal-distance pairs.

The system selects from eligible spaces rather than always taking the same space.

Availability

Occupied spaces are excluded.

If no suitable space exists, no parking session is created.

Business Rules and Validation

The system contains checks to prevent inconsistent parking and user data.

User-related checks

Registration numbers cannot be registered twice.

User IDs are generated automatically.

Users can be searched by:

User ID

Car model

Registration number

Driver cell

Searches support partial matching.

Searches are case-insensitive.

Invalid user IDs are rejected.

A currently parked user cannot be deleted.

Parking-related checks

A user cannot have two active parking sessions at the same time.

A parking session is not created without a suitable space.

An EV driver must accept a non-EV fallback space.

Refusing an EV fallback does not create an active session.

Invalid booking choices are rejected.

Invalid or non-positive booking durations are rejected.

Parking spaces are released after a vehicle exits.

A completed parking session is removed from active parking.

A user can exit parking using their user ID rather than remembering the parking ID.

Booking and Parking Sessions

A driver can choose between:

Book a parking time

Park without a booking

For booked parking, the system records:

In time

Booking start

Booked hours

Booking end

Out time

Actual duration

Overtime, if applicable

Final cost

Pricing breakdown

The booking starts at the same time as vehicle entry.

Example:

Parking confirmed
Parking ID:       u0001-20260813-57
Parking space:    p18
In time:          2026-08-13 23:00:00
Booking starts:   2026-08-13 23:00:00
Booked hours:     5
Booking ends:     2026-08-14 04:00:00

Exit and Grace Period Rules

The system distinguishes between booked and unbooked parking.

Booked parking

Exiting exactly at the booking end produces no overtime.

A two-minute grace period is allowed after the booking ends.

Exiting within the grace period produces no overtime charge.

Overtime is calculated from the original booking end time.

Overtime is charged separately from the booked parking charge.

Unbooked parking

The first two minutes are free.

Remaining billable time is calculated using the configured parking pulse.

Pricing

Pricing is isolated in the Pricing class.

Current pricing configuration:

Parking type

Rule

Unbooked

Kr 40/hour

Booked ≤ 4 hours

Kr 30/hour

Booked > 4 hours

Kr 25/hour

Unbooked billing pulse

30 minutes

Weekend discount

50%

The pricing system also produces a breakdown containing information such as:

Parking type

Applied rate

Number of pulses

Booked hours

Weekend status

Discount

Charge before discount

Overtime charge

Final total

Completed parking records retain their pricing breakdown so that historical charges do not depend on future price changes.

Persistent Active Parking

The system separates current parking state from completed parking history.

Three JSON files are used:

users.json
    ↓
Registered users

temp_parking_data.json
    ↓
Currently active parking sessions

parking_history.json
    ↓
Completed parking sessions

How active parking persistence works

When a vehicle enters:

ParkingSession created
        ↓
active_sessions updated
        ↓
temp_parking_data.json saved

If the application closes while a vehicle is still parked, the active session remains in temp_parking_data.json.

When the application starts again:

ParkingManager starts
        ↓
Load active sessions
        ↓
Recreate ParkingSession objects
        ↓
Restore active_sessions
        ↓
Restore occupied parking spaces

Restoring the physical space is important. Otherwise, the system could restore the parking session while incorrectly showing its parking space as available.

When the final active session ends:

active_sessions becomes empty
        ↓
temp_parking_data.json is removed

This allows the application to recover its current operational state after a program restart.

Parking History

Completed parking sessions are stored in:

parking_history.json

A completed record contains information such as:

Parking ID

User ID

Parking type

Parking space

In time

Out time

Booking information

Actual duration

Pricing breakdown

Final cost

The application can display history for:

All users

An individual user

All available records

Today

Last 7 days

Last 30 days

A custom date range

Application Menu

The application provides a command-line interface:

```text
============================================================
                PARKING BUSINESS MANAGER
============================================================
1. Add user
2. Start parking
3. Exit parking
4. Find user
5. View all users
6. View space occupancy
7. View active parking
8. View parking history
9. Delete user
10. Exit
```

The menu provides access to the main user and parking workflows while the underlying classes handle the business rules.

OOP Architecture

The project separates responsibilities across several classes.

                    main.py
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
    ▼                  ▼                  ▼

UserManager      ParkingManager       DataManager
│                  │                  │
▼                  ▼                  ▼
User          ParkingSession      JSON files
│
┌─────────┴─────────┐
▼                   ▼
ParkingFacility           Pricing
│
▼
ParkingSpace

User

Represents one registered parking user.

Handles:

User information

Vehicle information

EV identification

Dictionary conversion for storage

UserManager

Handles:

Adding users

Generating user IDs

Searching users

Retrieving all users

Deleting users

User-related validation

ParkingSpace

Represents one physical parking space.

Stores:

Space number

Floor

Pair number

EV status

Corner status

Occupancy state

Current user ID

ParkingFacility

Creates and manages the 60 physical parking spaces.

Handles:

Floor assignment

EV-space assignment

Corner-space assignment

Equal-distance pair assignment

ParkingSession

Represents one parking session.

Stores:

Parking ID

User ID

Parking type

Parking space

Entry information

Booking information

Exit information

Duration

Pricing information

It also manages temporary persistence of active parking sessions.

ParkingManager

Contains the main parking business logic.

Handles:

Space allocation

EV allocation

EV fallback

Vehicle-width rules

Booking

Active parking sessions

Parking IDs

Parking exit

Space occupation and release

Active-session persistence

Pricing

Handles:

Unbooked pricing

Booked pricing

Overtime pricing

Weekend discount

Pricing breakdowns

DataManager

Handles JSON storage for:

users.json

parking_history.json

Business logic remains outside the data-storage class.

Data Flow

A typical parking lifecycle looks like this:

```text

User
↓
Start parking
↓
Check existing active session
↓
Check available spaces
↓
Evaluate vehicle type
↓
Evaluate vehicle width
↓
Evaluate booking duration
↓
Apply parking allocation rules
↓
Create ParkingSession
↓
Occupy ParkingSpace
↓
Save active session
↓
Vehicle remains parked
↓
Exit using User ID
↓
Calculate duration and price
↓
Complete ParkingSession
↓
Save parking history
↓
Release ParkingSpace
↓
Remove active session

## Project Structure
```text
parking_business/
│
├── main.py
├── user.py
├── user_manager.py
├── parking_facility.py
├── parking_space.py
├── parking_session.py
├── parking_manager.py
├── pricing.py
├── data_manager.py
│
└── test_parking_cycle.py

Testing

The project includes a comprehensive parking regression test suite covering the main business rules.

The final regression suite contains 13 tests:

Booked parking

Exit exactly at booking end

Exit within the two-minute grace period

Booked parking with overtime

Unbooked parking

Unbooked parking within the first two minutes

Invalid booking input

Invalid booking menu choice

EV accepting a non-EV fallback

EV refusing a non-EV fallback

Parking-space release

No parking space available

Parking ID format

The final regression run passed all 13 tests.

Example:

TEST RESULT
----------------------------------------
Test passed
Overtime is calculated from booking end,
not from grace-period end.

Expected overtime: 5 minutes
Actual overtime:   5 minutes

Expected cost: Kr 145.00
Actual cost:   Kr 145.00

Technologies

Python

Object-Oriented Programming

JSON

File handling

Datetime

Exception handling

Input validation

State management

Regression testing

Running the Application

From the project directory:

python main.py

To run the regression tests:

python test_parking_cycle.py

Design Approach

The application keeps the command-line interface separate from the business logic.

main.py handles interaction with the user.

The managers and domain classes handle the actual operations.

For example:

main.py
↓
"Start parking"
↓
ParkingManager.start_parking()
↓
Parking allocation rules
↓

ParkingSession

↓

ParkingSpace

↓

Data persistence

This prevents the main menu from becoming responsible for parking allocation, pricing, data storage, and session management at the same time.

Key Implementation Areas

The project brings several Python concepts together in one application:

Classes and objects

Constructors

Instance methods

Static methods

Encapsulation of state

Composition between classes

Separation of responsibilities

List and dictionary operations

Set operations

File handling

JSON serialization

Exception handling

Date and time arithmetic

Conditional business rules

Searching and filtering

Persistent application state

Regression testing

Author

Rahul Rehman
Python / OOP Portfolio Project
