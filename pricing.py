"""
Manage the current parking prices and calculate parking charges.

Prices can be changed without changing previously completed
parking records.

Each completed parking record stores its own pricing breakdown,
so historical charges remain unchanged even when prices change.
"""


class Pricing:

    def __init__(
        self,
        unbooked_hourly_rate=40,
        booked_short_rate=30,
        booked_long_rate=25,
        booked_long_threshold=4,
        unbooked_pulse_minutes=30,
        weekend_discount=0.50
    ):
        self.unbooked_hourly_rate = unbooked_hourly_rate
        self.booked_short_rate = booked_short_rate
        self.booked_long_rate = booked_long_rate
        self.booked_long_threshold = booked_long_threshold
        self.unbooked_pulse_minutes = unbooked_pulse_minutes
        self.weekend_discount = weekend_discount

    # Calculate the charge for unbooked parking.
    def calculate_unbooked_charge(
        self,
        duration_minutes,
        is_weekend=False
    ):
        if duration_minutes <= 0:
            return 0, {
                "parking_type": "UNBOOKED",
                "rate": self.unbooked_hourly_rate,
                "pulse_minutes": self.unbooked_pulse_minutes,
                "pulses": 0,
                "weekend": is_weekend,
                "weekend_discount": (
                    self.weekend_discount if is_weekend else 0
                ),
                "charge_before_discount": 0,
                "total": 0
            }

        pulses = (
            duration_minutes + self.unbooked_pulse_minutes - 1
        ) // self.unbooked_pulse_minutes

        pulse_rate = (
            self.unbooked_hourly_rate
            * self.unbooked_pulse_minutes
            / 60
        )

        charge = pulses * pulse_rate

        discount = (
            self.weekend_discount
            if is_weekend
            else 0
        )

        final_charge = charge * (1 - discount)

        breakdown = {
            "parking_type": "UNBOOKED",
            "rate": self.unbooked_hourly_rate,
            "pulse_minutes": self.unbooked_pulse_minutes,
            "pulses": pulses,
            "weekend": is_weekend,
            "weekend_discount": discount,
            "charge_before_discount": charge,
            "total": final_charge
        }

        return final_charge, breakdown

    # Calculate the charge for booked parking.
    def calculate_booked_charge(
        self,
        booked_hours,
        is_weekend=False
    ):
        if booked_hours <= self.booked_long_threshold:
            rate = self.booked_short_rate
        else:
            rate = self.booked_long_rate

        charge = booked_hours * rate

        discount = (
            self.weekend_discount
            if is_weekend
            else 0
        )

        final_charge = charge * (1 - discount)

        breakdown = {
            "parking_type": "BOOKED",
            "booked_hours": booked_hours,
            "rate": rate,
            "charge_before_discount": charge,
            "weekend": is_weekend,
            "weekend_discount": discount,
            "total": final_charge
        }

        return final_charge, breakdown

    # Calculate the complete charge for a booked session,
    # including any time spent after the booking ends.
    def calculate_booked_with_overtime(
        self,
        booked_hours,
        overtime_minutes,
        is_weekend=False
    ):
        booked_charge, booked_breakdown = (
            self.calculate_booked_charge(
                booked_hours,
                is_weekend
            )
        )

        overtime_charge, overtime_breakdown = (
            self.calculate_unbooked_charge(
                overtime_minutes,
                is_weekend
            )
        )

        total = booked_charge + overtime_charge

        breakdown = {
            "parking_type": "BOOKED",
            "booked_hours": booked_hours,
            "booked_charge": booked_breakdown,
            "overtime_minutes": overtime_minutes,
            "overtime_charge": overtime_breakdown,
            "total": total
        }

        return total, breakdown
