import sys
import os

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.util.parking_session_utils import ParkingSessionService
from app.db.models.parking_session import ParkingSession
from app.db.models.parking_lot import ParkingLot

client = TestClient(app)

class TestDiscountCodes:
    admin_login_data = {
        "username": "testadmin",
        "password": "password"
    }

    def test_discount_code(self):
        """Test discount code logic"""

        # Login as admin
        response = client.post("/auth/login", json=self.admin_login_data)
        assert response.status_code == 200
        data = response.json()
        token = data.get("token")
        assert token is not None

        # Create discount code as admin
        response = client.post("/discount_codes", json={"code": "ABCDEF", "percentage": 10, "type": "multiple-use", "used": False}, headers={"Authorization": token})
        assert response.status_code == 201

        # Start session at a time in the past (admin-only)
        response = client.post("/parking_sessions/start/1/DISCOUNT123", json={"start_time": (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")}, headers={"Authorization": token})
        assert response.status_code == 201

        # Stop session without discount code
        response = client.post("/parking_sessions/stop/DISCOUNT123", headers={"Authorization": token})
        assert response.status_code == 200
        data = response.json()
        assert data["cost"] is not None
        normal_cost = data["cost"]


        # Start another session at a time in the past (admin-only)
        response = client.post("/parking_sessions/start/1/DISCOUNT456", json={"start_time": (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")}, headers={"Authorization": token})
        assert response.status_code == 201

        # Stop session with discount code
        response = client.post("/parking_sessions/stop/DISCOUNT456", json={"discount_code": "ABCDEF"}, headers={"Authorization": token})
        assert response.status_code == 200
        data = response.json()
        assert data["cost"] is not None
        discounted_cost = data["cost"]

        assert discounted_cost < normal_cost
