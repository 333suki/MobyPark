import pytest
from fastapi.testclient import TestClient
from app.db.models.reservation import reservation

from app.main import app

client = TestClient(app)


class TestGetReservations:
    admin_test_data = {
        "username": "testadmin",
        "password": "password"
    }

    user_test_data = {
        "username": "testuser",
        "password": "password"
    }

    # Tests for GET /reservations/ endpoint
    def test_get_reservations_without_token(self):
        # Test getting reservations without authentication
        response = client.get("/reservations/")
        
        assert response.status_code == 401

    def test_get_reservation_as_admin(self):
        # Login as admin
        response = client.post("/auth/login", json=self.admin_test_data)
        assert response.status_code == 200
        data = response.json()
        token = data.get("token")
        assert token is not None

        # Get all the reservations (admin can see them all)
        response = client.get("/reservations", headers={"Authorization": token})
        assert response.status_code == 200
        json_data = response.json()
        assert isInstance(json_data, list) # this should return a list of the reservations

        
