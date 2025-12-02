import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)


class TestVehicles:

    # Test data
    valid_register_data = {
        "username": "testuser",
        "password": "Testpass123",
        "name": "Test User",
        "email": "testuser@example.com",
        "phone": "1234567890",
        "birth_year": 1990
    }

    valid_login_data = {
        "username": "testuser",
        "password": "Testpass123"
    }

    valid_vehicle_data = {
        "license_plate": "ABC123",
        "make": "Toyota",
        "model": "Camry",
        "color": "Blue",
        "year": "2020"
    }

    valid_vehicle_data_2 = {
        "license_plate": "XYZ789",
        "make": "Honda",
        "model": "Civic",
        "color": "Red",
        "year": "2019"
    }

    invalid_vehicle_data = {
        "license_plate": "",  # Invalid: empty
        "make": "Tesla",
        "model": "Model 3"
        # Missing required fields
    }

    update_vehicle_data = {
        "color": "Green",
        "year": "2021"
    }

    @staticmethod
    def setup_user_method(self):
        # Register user (ignore if already exists)
        client.post("/auth/register", json=self.valid_register_data)

        # Login and get token
        response = client.post("/auth/login", json=self.valid_login_data)
        token_data = response.json()
        self.token = token_data.get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @staticmethod
    def delete_vehicles_method(self):
        # Ensure test vehicles are removed after each test to avoid collisions.
        try:
            from app.db.database import SessionLocal
            from app.db.models.vehicle import Vehicle
            from app.db.models.user import User
            db = SessionLocal()
            user = db.query(User).filter(User.username == self.valid_register_data["username"]).first()
            if user:
                db.query(Vehicle).filter(Vehicle.user_id == user.id).delete()
                db.commit()
        except Exception:
            pass
    
    # Create vehicle
    def test_create_vehicle_success(self):
        self.setup_user_method(self)
        response = client.post("/vehicles/", 
                               json=self.valid_vehicle_data, 
                               headers=self.headers)
        assert response.status_code == 201
        data = response.json()
        assert data["license_plate"] == self.valid_vehicle_data["license_plate"]
        assert data["make"] == self.valid_vehicle_data["make"]
        assert data["model"] == self.valid_vehicle_data["model"]
        self.delete_vehicles_method(self)
    
    # Update vehicle
    def test_update_vehicle_success(self):
        self.setup_user_method(self)
        # First, create a vehicle to update
        client.post("/vehicles/", 
                    json=self.valid_vehicle_data, 
                    headers=self.headers)
        
        # Now, update the vehicle
        response = client.put(f"/vehicles/{self.valid_vehicle_data['license_plate']}",
                              json=self.update_vehicle_data,
                              headers=self.headers)
        data = response.json()
        print(data)
        assert data["color"] == self.update_vehicle_data["color"]
        assert data["year"] == self.update_vehicle_data["year"]
        self.delete_vehicles_method(self)
    
    # View vehicles
    
    # Delete vehicle