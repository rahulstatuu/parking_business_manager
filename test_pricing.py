from pricing import Pricing


pricing = Pricing()


print("TEST 1: Unbooked - 30 minutes")
cost, breakdown = pricing.calculate_unbooked_charge(
    duration_minutes=30,
    is_weekend=False
)
print(f"Cost: {cost:.2f} kr")
print(breakdown)
print()


print("TEST 2: Unbooked - 60 minutes")
cost, breakdown = pricing.calculate_unbooked_charge(
    duration_minutes=60,
    is_weekend=False
)
print(f"Cost: {cost:.2f} kr")
print(breakdown)
print()


print("TEST 3: Unbooked - 70 minutes")
cost, breakdown = pricing.calculate_unbooked_charge(
    duration_minutes=70,
    is_weekend=False
)
print(f"Cost: {cost:.2f} kr")
print(breakdown)
print()


print("TEST 4: Booked - 3 hours")
cost, breakdown = pricing.calculate_booked_charge(
    booked_hours=3,
    is_weekend=False
)
print(f"Cost: {cost:.2f} kr")
print(breakdown)
print()


print("TEST 5: Booked - 5 hours")
cost, breakdown = pricing.calculate_booked_charge(
    booked_hours=5,
    is_weekend=False
)
print(f"Cost: {cost:.2f} kr")
print(breakdown)
print()


print("TEST 6: Booked 5 hours + 45 minutes overtime")

cost, breakdown = pricing.calculate_booked_with_overtime(
    booked_hours=5,
    overtime_minutes=45,
    is_weekend=False
)

print(f"Cost: {cost:.2f} kr")
print(breakdown)
print()


print("TEST 7: Weekend - booked 5 hours")

cost, breakdown = pricing.calculate_booked_charge(
    booked_hours=5,
    is_weekend=True
)

print(f"Cost: {cost:.2f} kr")
print(breakdown)
print()


print("TEST 8: Weekend - unbooked 60 minutes")

cost, breakdown = pricing.calculate_unbooked_charge(
    duration_minutes=60,
    is_weekend=True
)

print(f"Cost: {cost:.2f} kr")
print(breakdown)
print()
