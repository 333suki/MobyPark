import sys
import os

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.util.parking_session_utils import ParkingSessionService
from app.db.models.parking_session import ParkingSession
from app.db.models.parking_lot import ParkingLot

client = TestClient(app)


class TestStartParkingSession:
    
    def test_start_session_as_guest(self):
        """Test starting session without authentication"""
        response = client.post("/parking_sessions/start/1/GUEST123")
        
        assert response.status_code == 201
        data = response.json()
        assert data["license_plate"] == "GUEST123"
        assert data["username"] == "guest"
        assert data["payment_status"] == "ongoing"
    
    def test_start_session_duplicate(self):
        """Test cannot start duplicate session"""
        client.post("/parking_sessions/start/1/DUP123")
        response = client.post("/parking_sessions/start/1/DUP123")
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_start_session_different_parking_lots(self):
        """Test same plate in different parking lots"""
        response1 = client.post("/parking_sessions/start/1/PLATE123")
        client.post("/parking_sessions/stop/PLATE123")
        response2 = client.post("/parking_sessions/start/2/PLATE123")
        
        assert response1.status_code == 201
        assert response2.status_code == 201
    
    def test_start_session_invalid_parking_lot(self):
        """Test starting session with invalid parking lot"""
        response = client.post("/parking_sessions/start/9999/TEST123")
        
        # Should handle invalid parking lot
        assert response.status_code in [400, 404]


class TestStopParkingSession:
    
    def test_stop_guest_session(self):
        """Test stopping guest session"""
        client.post("/parking_sessions/start/1/STOP123")
        response = client.post("/parking_sessions/stop/STOP123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["stopped"] is not None
        assert data["payment_status"] == "pending"
    
    def test_stop_nonexistent_session(self):
        """Test stopping session that doesn't exist"""
        response = client.post("/parking_sessions/stop/NOTEXIST")
        
        assert response.status_code == 404
        assert "No active parking session" in response.json()["detail"]
    
    def test_stop_already_stopped_session(self):
        """Test stopping already stopped session"""
        client.post("/parking_sessions/start/1/STOP456")
        client.post("/parking_sessions/stop/STOP456")
        response = client.post("/parking_sessions/stop/STOP456")
        
        assert response.status_code == 404
    
    def test_stop_session_has_duration(self):
        """Test stopped session has duration"""
        client.post("/parking_sessions/start/1/DUR123")
        response = client.post("/parking_sessions/stop/DUR123")
        
        data = response.json()
        assert data["duration_minutes"] is not None
        assert data["duration_minutes"] >= 0


class TestGetParkingSessions:
    
    def test_get_sessions_no_auth(self):
        """Test getting sessions without authentication"""
        response = client.get("/parking_sessions/")
        
        assert response.status_code == 401
        assert "authorization token" in response.json()["detail"].lower()
    
    def test_get_sessions_with_invalid_token(self):
        """Test getting sessions with invalid token"""
        response = client.get(
            "/parking_sessions/",
            headers={"Authorization": "invalid_token"}
        )
        
        assert response.status_code == 401


class TestSessionFilters:
    
    def test_filter_by_license_plate(self):
        """Test filtering by license plate (requires auth)"""
        response = client.get(
            "/parking_sessions/?license_plate=ABC123",
            headers={"Authorization": "test_token"}
        )
        
        # Will fail auth but tests the endpoint structure
        assert response.status_code == 401
    
    def test_filter_with_limit(self):
        """Test using limit parameter"""
        response = client.get(
            "/parking_sessions/?limit=5",
            headers={"Authorization": "test_token"}
        )
        
        assert response.status_code == 401


class TestCalculatePrice:
    
    def test_price_under_3_minutes_is_free(self):
        """Test sessions under 3 minutes are free"""
        parking_lot = ParkingLot(tariff=5.0, daytariff=20.0)
        session = ParkingSession(
            started=datetime(2023, 1, 1, 10, 0, 0),
            stopped=datetime(2023, 1, 1, 10, 2, 0)
        )
        
        price = ParkingSessionService.calculate_price(parking_lot, session)
        
        assert price == 0
    
    def test_price_one_hour(self):
        """Test one hour costs 5.0"""
        parking_lot = ParkingLot(tariff=5.0, daytariff=20.0)
        session = ParkingSession(
            started=datetime(2023, 1, 1, 10, 0, 0),
            stopped=datetime(2023, 1, 1, 11, 0, 0)
        )
        
        price = ParkingSessionService.calculate_price(parking_lot, session)
        
        assert price == 5.0
    
    def test_price_caps_at_day_tariff(self):
        """Test price caps at day tariff"""
        parking_lot = ParkingLot(tariff=5.0, daytariff=20.0)
        session = ParkingSession(
            started=datetime(2023, 1, 1, 10, 0, 0),
            stopped=datetime(2023, 1, 1, 20, 0, 0)
        )
        
        price = ParkingSessionService.calculate_price(parking_lot, session)
        
        assert price == 20.0
    
    def test_price_multiple_days(self):
        """Test multiple days pricing"""
        parking_lot = ParkingLot(tariff=5.0, daytariff=20.0)
        session = ParkingSession(
            started=datetime(2023, 1, 1, 10, 0, 0),
            stopped=datetime(2023, 1, 3, 10, 0, 0)
        )
        
        price = ParkingSessionService.calculate_price(parking_lot, session)
        
        assert price == 60.0


class TestSessionLifecycle:
    
    def test_session_start_to_stop(self):
        """Test complete session lifecycle"""
        # Start session
        start_response = client.post("/parking_sessions/start/1/LIFECYCLE123")
        assert start_response.status_code == 201
        start_data = start_response.json()
        assert start_data["stopped"] is None
        
        # Stop session
        stop_response = client.post("/parking_sessions/stop/LIFECYCLE123")
        assert stop_response.status_code == 200
        stop_data = stop_response.json()
        assert stop_data["stopped"] is not None
        assert stop_data["duration_minutes"] >= 0
    
    def test_multiple_sessions_same_plate(self):
        """Test multiple sessions with same plate"""
        # First session
        client.post("/parking_sessions/start/1/MULTI123")
        client.post("/parking_sessions/stop/MULTI123")
        
        # Second session
        response = client.post("/parking_sessions/start/1/MULTI123")
        assert response.status_code == 201
    
    def test_session_has_correct_fields(self):
        """Test session has all required fields"""
        response = client.post("/parking_sessions/start/1/FIELDS123")
        
        data = response.json()
        assert "id" in data
        assert "parking_lot_id" in data
        assert "license_plate" in data
        assert "username" in data
        assert "started" in data
        assert "payment_status" in data