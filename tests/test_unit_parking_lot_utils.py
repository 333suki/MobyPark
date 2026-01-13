from app.db.database import SessionLocal
from app.db.models.parking_lot import ParkingLot
from app.db.models.reservation import Reservation
from datetime import datetime, date, timedelta
from app.util.parking_lot_utils import ParkingLotUtils
from app.db.models.user import User
from app.util.auth_utils import AuthUtils

class TestGetFreeParkingSpots:
    """Unit tests for get_free_parking_spots"""
    def test_get_free_spots(self):
        """Test gets full capacity when there are no sessions and reservations"""
        db = SessionLocal()

        # Create test data
        parking_lot = ParkingLot(
            id=9999,
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

        assert ParkingLotUtils.get_free_parking_spots(db, 9999, datetime.now(), datetime.now() + timedelta(hours=5)) == 200

        # Cleanup
        db.delete(parking_lot)
        db.commit()
        db.close()

    def test_get_free_spots_reservation_active(self):
        """Test gets correct capacity when there is a reservation active"""
        db = SessionLocal()

        # Create test data
        parking_lot = ParkingLot(
            id=9999,
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

        user = User(
            id=9999,
            username="test_parking_lot_utils1",
            email="test_parking_lot_utils1@test.com",
            password=AuthUtils.hash_password("test"),
            name="Test Parking Lot Utils1",
            phone="1234567890",
            role="user",
            created_at=date.today(),
            birth_year=1990,
            active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        reservation = Reservation(
            user_id=9999,
            parking_lot_id=9999,
            license_plate="AA-11-BB",
            start_time=datetime.now() - timedelta(hours=1),
            end_time=datetime.now() + timedelta(hours=2),
            status = "pending",
            created_at=date.today(),
            cost=100.0
        )
        db.add(reservation)
        db.commit()
        db.refresh(reservation)

        assert ParkingLotUtils.get_free_parking_spots(db, 9999, datetime.now(),datetime.now() + timedelta(hours=1)) < 200

        db.delete(reservation)
        db.delete(user)
        db.delete(parking_lot)
        db.commit()
        db.close()
