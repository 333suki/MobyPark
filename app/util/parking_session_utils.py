import math
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models.parking_lot import ParkingLot
from app.db.models.parking_session import ParkingSession
from app.db.models.user import User
from app.db.models.vehicle import Vehicle


class ParkingSessionService:
    
    @staticmethod
    def check_active_session(db: Session, license_plate: str) -> bool:
        """Check if there's an active session for the given license plate"""
        active_session = db.query(ParkingSession).filter(
            ParkingSession.license_plate == license_plate,
            ParkingSession.stopped == None
        ).first()
        return active_session is not None

    @staticmethod
    def get_user_by_license_plate(db: Session, license_plate: str) -> Optional[User]:
        """Get user by license plate if it's registered to their account"""
        vehicle = db.query(Vehicle).filter(Vehicle.license_plate == license_plate).first()
        if vehicle:
            return db.query(User).filter(User.id == vehicle.user_id).first()
        return None
    
    @staticmethod
    def calculate_price(parking_lot: ParkingLot, session: ParkingSession) -> float:
        """Calculate the price for a parking session based on duration and parking lot rates"""
        price = 0
        start = session.started

        if session.stopped:
            end = session.stopped
        else:
            end = datetime.now()

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
