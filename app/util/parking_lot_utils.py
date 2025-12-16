from datetime import datetime
from sqlalchemy.orm import Session

from app.db.models.parking_lot import ParkingLot
from app.db.models.reservation import Reservation
from app.db.models.parking_session import ParkingSession

class ParkingLotUtils:
    @staticmethod
    def get_free_parking_spots(db: Session, parking_lot_id: int, start_time: datetime, end_time: datetime) -> int | None:
        if start_time < end_time:
            return None

        parking_lot: ParkingLot | None = db.query(ParkingLot).filter(ParkingLot.id == parking_lot_id).first()
        if parking_lot is None:
            return None

        capacity: int = parking_lot.capacity
        reservation_count: int = len(db.query(Reservation).filter(Reservation.start_time >= start_time).filter(Reservation.end_time <= end_time).all())
        session_count: int = len(db.query(ParkingSession).filter(ParkingSession.started >= start_time).filter(ParkingSession.stopped == None).all())
        session_count += len(db.query(ParkingSession).filter(ParkingSession.started >= start_time).filter(ParkingSession.stopped <= end_time).all())

        return capacity - reservation_count - session_count
