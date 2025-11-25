import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

class TestParkingLots:
    valid_login_data = {
        "username": "testadmin",
        "password": "password"
    }
    def test_get_all_parking_lots_unauthorized(self):
        response = client.get("/parking_lots")
        assert response.status_code == 401

    def test_get_all_parking_lots(self):
        response = client.post("/auth/login", json=self.valid_login_data)
        assert response.status_code == 200
        data = response.json()
        token = data.get("token")
        assert token is not None

        response = client.get("/parking_lots", headers={"Authorization": token})
        assert response.status_code == 200
