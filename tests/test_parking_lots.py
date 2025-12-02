import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

class TestParkingLots:
    admin_login_data = {
        "username": "testadmin",
        "password": "password"
    }

    user_login_data = {
        "username": "testuser",
        "password": "password"
    }

    def test_get_all_parking_lots_unauthorized(self):
        response = client.get("/parking_lots")
        assert response.status_code == 401

    def test_get_all_parking_lots(self):
        response = client.post("/auth/login", json=self.admin_login_data)
        assert response.status_code == 200
        data = response.json()
        token = data.get("token")
        assert token is not None

        response = client.get("/parking_lots", headers={"Authorization": token})
        assert response.status_code == 200

    def test_create_parking_lot_unauthorized(self):
        body = {
            "name": "Parking Lot",
            "location": "Netherlands",
            "address": "Foo Lane 3",
            "capacity": 200,
            "reserved": 50,
            "tariff": 5.1,
            "daytariff": 2,
            "coordinates_lat": 56.214,
            "coordinates_lng": 48.621
        }

        response = client.post("/parking_lots", json=body)
        assert response.status_code == 401

    def test_create_parking_lot(self):
        response = client.post("/auth/login", json=self.admin_login_data)
        assert response.status_code == 200
        data = response.json()
        token = data.get("token")
        assert token is not None

        body = {
            "name": "Parking Lot",
            "location": "Netherlands",
            "address": "Foo Lane 3",
            "capacity": 200,
            "reserved": 50,
            "tariff": 5.1,
            "daytariff": 2,
            "coordinates_lat": 56.214,
            "coordinates_lng": 48.621
        }

        response = client.post("/parking_lots", json=body, headers={"Authorization": token})
        assert response.status_code == 201
