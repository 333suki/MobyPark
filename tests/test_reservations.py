import pytest
from fastapi.testclient import TestClient
from app.db.models.reservation import Reservation

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
        assert isinstance(json_data, list) # this should return a list of the reservations

    def test_create_reservation_as_user(self):
        # Register and login
        client.post(
            "/auth/register",
            json={
                "username": "createreservationuser",
                "email": "reservationuser@example.com",
                "password": "Password123!",
                "name": "Reservation User1",
                "phone": "1234567890",
                "birth_year": 1600
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={"username": "createreservationuser", "password": "Password123!"}
        )
        token = login_response.json()["token"]

        # Create a reservation
        response = client.post(
            "/reservations", 
            json={
                "parking_lot_id": 1,
                "license_plate": "36-DX-PL",
                "start_time": "2026-01-13T11:15:01",
                "end_time": "2026-01-14T08:10:05"
            }, headers={"Authorization": token}
        )

        assert response.status_code == 201

        # Get the reservations (this should only show the users own reservation)
        response = client.get("/reservations", headers={"Authorization": token})
        assert response.status_code == 200
        json_data = response.json()
        assert isinstance(json_data, list) # this should return a list of the reservations
        assert len(json_data) > 0 # check if the list has more than 1 thang

        
        

