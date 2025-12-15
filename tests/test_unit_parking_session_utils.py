import pytest
from datetime import datetime, timedelta, date

from app.util.parking_session_utils import ParkingSessionService
from app.db.database import SessionLocal
from app.db.models.parking_session import ParkingSession
from app.db.models.parking_lot import ParkingLot
from app.db.models.user import User
from app.db.models.vehicle import Vehicle
from app.util.auth_utils import AuthUtils


class TestCheckActiveSession:
    """Unit tests for check_active_session"""
    
    def test_returns_true_when_active_session_exists(self):
        """Test returns True when active session exists"""
        db = SessionLocal()
        
        # Create test data
        user = User(
            username="test_active",
            email="test_active@test.com",
            password=AuthUtils.hash_password("test"),
            name="Test Active",
            phone="1234567890",
            role="user",
            created_at=date.today(),
            birth_year=1990,
            active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        vehicle = Vehicle(license_plate="ACTIVE123", user_id=user.id, make="Test", model="Car",
                         color="Blue", year="2020", created_at=date.today())
        db.add(vehicle)
        db.commit()
        
        parking_lot = ParkingLot(name="Test Lot", address="123 Test St", capacity=10, tariff=5.0, daytariff=25,
                                location="Downtown", reserved=0, created_at=date.today(),
                                coordinates_lat=52.52, coordinates_lng=13.405)
        db.add(parking_lot)
        db.commit()
        db.refresh(parking_lot)
        
        session = ParkingSession(
            license_plate="ACTIVE123",
            parking_lot_id=parking_lot.id,
            started=datetime.now(),
            username=user.username,
            payment_status="pending"
        )
        db.add(session)
        db.commit()
        
        result = ParkingSessionService.check_active_session(db, "ACTIVE123")
        
        assert result is True
        
        # Cleanup
        db.delete(session)
        db.delete(vehicle)
        db.delete(parking_lot)
        db.delete(user)
        db.commit()
        db.close()
    
    def test_returns_false_when_no_active_session(self):
        """Test returns False when no active session"""
        db = SessionLocal()
        
        result = ParkingSessionService.check_active_session(db, "NOACTIVE999")
        
        assert result is False
        db.close()


class TestGetUsername:
    """Unit tests for get_username"""
    
    def test_returns_username_when_user_exists(self):
        """Test returns username when user exists"""
        db = SessionLocal()
        
        user = User(
            username="test_getuser",
            email="test_getuser@test.com",
            password=AuthUtils.hash_password("test"),
            name="Test GetUser",
            phone="1234567890",
            role="user",
            created_at=date.today(),
            birth_year=1990,
            active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        result = ParkingSessionService.get_username(db, user.id)
        
        assert result == "test_getuser"
        
        # Cleanup
        db.delete(user)
        db.commit()
        db.close()
    
    def test_returns_none_when_user_not_exists(self):
        """Test returns None when user doesn't exist"""
        db = SessionLocal()
        
        result = ParkingSessionService.get_username(db, 999999)
        
        assert result is None
        db.close()


class TestCalculatePrice:
    """Unit tests for calculate_price"""
    
    def test_free_parking_under_3_minutes(self):
        """Test parking under 3 minutes is free"""
        parking_lot = ParkingLot(tariff=5.0, daytariff=25, location="Test", address="Test",
                                capacity=10, reserved=0, created_at=date.today(),
                                coordinates_lat=0.0, coordinates_lng=0.0, name="Test")
        session = ParkingSession(
            started=datetime(2023, 1, 1, 10, 0, 0),
            stopped=datetime(2023, 1, 1, 10, 2, 0),
            license_plate="TEST",
            parking_lot_id=1,
            username="test",
            payment_status="pending"
        )
        
        price = ParkingSessionService.calculate_price(parking_lot, session)
        
        assert price == 0
    
    def test_one_hour_parking(self):
        """Test one hour parking calculation"""
        parking_lot = ParkingLot(tariff=5.0, daytariff=25, location="Test", address="Test",
                                capacity=10, reserved=0, created_at=date.today(),
                                coordinates_lat=0.0, coordinates_lng=0.0, name="Test")
        session = ParkingSession(
            started=datetime(2023, 1, 1, 10, 0, 0),
            stopped=datetime(2023, 1, 1, 11, 0, 0),
            license_plate="TEST",
            parking_lot_id=1,
            username="test",
            payment_status="pending"
        )
        
        price = ParkingSessionService.calculate_price(parking_lot, session)
        
        assert price == 5.0
    
    def test_price_caps_at_day_tariff(self):
        """Test price caps at day tariff"""
        parking_lot = ParkingLot(tariff=5.0, daytariff=25, location="Test", address="Test",
                                capacity=10, reserved=0, created_at=date.today(),
                                coordinates_lat=0.0, coordinates_lng=0.0, name="Test")
        session = ParkingSession(
            started=datetime(2023, 1, 1, 10, 0, 0),
            stopped=datetime(2023, 1, 1, 22, 0, 0),
            license_plate="TEST",
            parking_lot_id=1,
            username="test",
            payment_status="pending"
        )
        
        price = ParkingSessionService.calculate_price(parking_lot, session)
        
        assert price == 25.0
    
    def test_multiple_day_parking(self):
        """Test multiple day parking calculation"""
        parking_lot = ParkingLot(tariff=5.0, daytariff=25, location="Test", address="Test",
                                capacity=10, reserved=0, created_at=date.today(),
                                coordinates_lat=0.0, coordinates_lng=0.0, name="Test")
        session = ParkingSession(
            started=datetime(2023, 1, 1, 10, 0, 0),
            stopped=datetime(2023, 1, 3, 10, 0, 0),
            license_plate="TEST",
            parking_lot_id=1,
            username="test",
            payment_status="pending"
        )
        
        price = ParkingSessionService.calculate_price(parking_lot, session)
        
        assert price == 75.0
