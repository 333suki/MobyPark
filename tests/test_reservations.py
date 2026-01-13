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

    def test_update_reservation_as_user(self):
        # Login
        login_response = client.post(
            "/auth/login",
            json={"username": "createreservationuser", "password": "Password123!"}
        )
        token = login_response.json()["token"]

        response = client.get("/reservations", headers={"Authorization": token})
        assert response.status_code == 200
        json_data = response.json()
        assert isinstance(json_data, list) # make suer the json object is a list
        assert len(json_data) > 0 # make sure if the list has more than 1 thang

        # get the id of the first reservation
        test_reservation_id = json_data[0]["id"]

        # update the license plate of said reservation
        response = client.put(f"/reservations/{test_reservation_id}", headers={"Authorization": token}, json={
            "license_plate": "33-XD-LO"
        })
        assert response.status_code == 200

        response = client.get(f"/reservations?reservation_id={test_reservation_id}", headers={"Authorization": token})
        assert response.status_code == 200
        json_data = response.json()
        assert isinstance(json_data, list)
        assert len(json_data) == 1
        # check if the license plate is actually updated to the new value
        assert json_data[0]["license_plate"] == "33-XD-LO"
        
    def test_delete_reservation_as_user(self):
        # Login
        login_response = client.post(
            "/auth/login",
            json={"username": "createreservationuser", "password": "Password123!"}
        )
        token = login_response.json()["token"]

        # first get the reservations
        response = client.get("/reservations", headers={"Authorization": token})
        assert response.status_code == 200
        json_data = response.json()
        assert isinstance(json_data, list)
        assert len(json_data) > 0 

        # get the id of the first reservation
        test_reservation_id = json_data[0]["id"]

        # delete the reservation on id
        response = client.delete(f"/reservations/{test_reservation_id}", headers={"Authorization": token})
        assert response.status_code == 200

        # check if the reservation is actually deleted
        response = client.get(f"/reservations?reservation_id={test_reservation_id}", headers={"Authorization": token})
        assert response.status_code == 200
        json_data = response.json()
        assert isinstance(json_data, list)
        assert len(json_data) == 0 


        

