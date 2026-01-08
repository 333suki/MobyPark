from app.db.database import SessionLocal
from app.db.models.parking_lot import ParkingLot
from datetime import datetime, date, timedelta
from app.util.parking_lot_utils import ParkingLotUtils

class TestGetFreeParkingSpots:
    """Unit tests for get_free_parking_spots"""
    def test_get_free_spots(self):
        """Test gets full capacity when there are no sessions and reservations"""
        db = SessionLocal()

        # Create test data
        parking_lot = ParkingLot(
            id=9285,
            name="TestParkingLot",
            location="Somewhere",
            address="Foo Street 1",
            capacity=200,
            reserved=0,
            tariff=5.0,
            daytariff=20,
            created_at=date.today(),
            coordinates_lat=50.0,
            coordinates_lng=50.0
        )
        db.add(parking_lot)
        db.commit()
        db.refresh(parking_lot)

        assert ParkingLotUtils.get_free_parking_spots(db, 9285, datetime.now(), datetime.now() + timedelta(hours=5)) == 200

        # Cleanup
        db.delete(parking_lot)
        db.commit()
        db.close()
