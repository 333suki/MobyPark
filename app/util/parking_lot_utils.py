from datetime import datetime
from sqlalchemy.orm import Session

from app.db.models.parking_lot import ParkingLot
from app.db.models.reservation import Reservation
from app.db.models.parking_session import ParkingSession

class ParkingLotUtils:
    @staticmethod
    def get_free_parking_spots(db: Session, parking_lot_id: int, start_time: datetime, end_time: datetime) -> int | None:
        if start_time > end_time:
            return None

        parking_lot: ParkingLot | None = db.query(ParkingLot).filter(ParkingLot.id == parking_lot_id).first()
        if parking_lot is None:
            return None

        capacity: int = parking_lot.capacity
        reservation_count = db.query(Reservation).filter(
            Reservation.parking_lot_id == parking_lot_id,
            Reservation.start_time <= start_time,
            Reservation.end_time >= end_time
        ).count()

        session_count = db.query(ParkingSession).filter(
            ParkingSession.parking_lot_id == parking_lot_id,
            ParkingSession.started <= start_time,
            ParkingSession.stopped.is_(None)
        ).count()

        session_count += db.query(ParkingSession).filter(
            ParkingSession.parking_lot_id == parking_lot_id,
            ParkingSession.started <= start_time,
            ParkingSession.stopped >= end_time
        ).count()

        return capacity - reservation_count - session_count
