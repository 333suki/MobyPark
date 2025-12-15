import math
from datetime import datetime

from app.db.models.parking_lot import ParkingLot


class ReservationUtils:

    @staticmethod
    def calculate_price(parking_lot: ParkingLot, start_time: datetime, end_time: datetime) -> float:
            """Calculate the price for a reservation based on duration and parking lot rates"""
            price = 0
            start = start_time

            end = end_time

            diff = end - start
            hours = math.ceil(diff.total_seconds() / 3600)

            if diff.total_seconds() < 180:
                price = 0
            elif end.date() > start.date():
                price = float(parking_lot.daytariff) * (diff.days + 1)
            else:
                price = float(parking_lot.tariff) * hours

                if price > float(parking_lot.daytariff):
                    price = float(parking_lot.daytariff)

            return price
