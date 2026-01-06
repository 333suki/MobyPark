import pytest
from fastapi.testclient import TestClient
from app.db.models.parking_lot import ParkingLot

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

    def test_update_parking_lot_unauthorized(self):
        body = {
            "name": "Updated Parking Lot"
        }

        response = client.put("/parking_lots/1", json=body)
        assert response.status_code == 401

    def test_update_parking_lot(self):
        response = client.post("/auth/login", json=self.admin_login_data)
        assert response.status_code == 200
        data = response.json()
        token = data.get("token")
        assert token is not None

        body = {
            "name": "Updated Parking Lot"
        }

        response = client.get("/parking_lots", headers={"Authorization": token})
        json: list = response.json()
        parking_lot_count: int = len(json)

        response = client.put(f"/parking_lots/{parking_lot_count - 1}", json=body, headers={"Authorization": token})
        assert response.status_code == 200

        response = client.get(f"/parking_lots?parking_lot_id={parking_lot_count - 1}", headers={"Authorization": token})
        json: list = response.json()
        assert len(json) > 0
        assert json[0]["name"] == "Updated Parking Lot"

    def test_delete_parking_lot_unauthorized(self):
        response = client.delete("/parking_lots/1")
        assert response.status_code == 401

    def test_delete_parking_lot(self):
        response = client.post("/auth/login", json=self.admin_login_data)
        assert response.status_code == 200
        data = response.json()
        token = data.get("token")
        assert token is not None

        response = client.get("/parking_lots", headers={"Authorization": token})
        json: list = response.json()
        parking_lot_count: int = len(json)

        response = client.delete(f"/parking_lots/{parking_lot_count - 1}", headers={"Authorization": token})
        assert response.status_code == 200

    def test_get_free_parking_spots(self):
        response = client.post("/auth/login", json=self.user_login_data)
        assert response.status_code == 200
        data = response.json()
        token = data.get("token")
        assert token is not None

        response = client.get("/parking_lots/free_spots", headers={"Authorization": token})
        json: dict = response.json()
        assert json is not None
        assert json.get("free_parking_spots") is not None
