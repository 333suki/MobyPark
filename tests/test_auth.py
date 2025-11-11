import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAuth:
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

    def test_register_user_success(self):
        """Test successful user registration"""
        response = client.post("/auth/register", json=self.valid_register_data)
        assert response.status_code == 201
        assert response.json() == {"message": "Registered successfully"}

    def test_register_user_duplicate_username(self):
        """Test registration with duplicate username"""
        # First registration
        client.post("/auth/register", json=self.valid_register_data)
        
        # Second registration with the same username
        duplicate_data = self.valid_register_data.copy()
        duplicate_data["email"] = "different@example.com"
        
        response = client.post("/auth/register", json=duplicate_data)
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]

    def test_register_user_duplicate_email(self):
        """Test registration with duplicate email"""
        # First registration
        client.post("/auth/register", json=self.valid_register_data)
        
        # Second registration with the same email
        duplicate_data = self.valid_register_data.copy()
        duplicate_data["username"] = "differentuser"
        
        response = client.post("/auth/register", json=duplicate_data)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_register_user_invalid_email_format(self):
        """Test registration with the invalid email format"""
        invalid_email_data = self.valid_register_data.copy()
        invalid_email_data["username"] = "newuser"
        invalid_email_data["email"] = "invalid-email"
        
        response = client.post("/auth/register", json=invalid_email_data)
        assert response.status_code == 400
        assert "validation_errors" in response.json()["detail"]

    def test_register_user_weak_password(self):
        """Test registration with a weak password"""
        weak_password_data = self.valid_register_data.copy()
        weak_password_data["username"] = "newuser"
        weak_password_data["password"] = "123"  # Too short
        
        response = client.post("/auth/register", json=weak_password_data)
        assert response.status_code == 400
        assert "validation_errors" in response.json()["detail"]

    def test_login_success(self):
        """Test successful login"""
        # First register a user
        client.post("/auth/register", json=self.valid_register_data)
        
        # Then try to log in
        response = client.post("/auth/login", json=self.valid_login_data)
        assert response.status_code == 200
        response_data = response.json()
        
        # Check all expected fields are present
        assert "token" in response_data
        assert response_data["username"] == self.valid_login_data["username"]

    def test_login_nonexistent_user(self):
        """Test login with a non-existent username"""
        login_data = {
            "username": "nonexistentuser",
            "password": "somepassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 400
        assert "Username doesn't exist" in response.json()["detail"]

    def test_login_wrong_password(self):
        """Test login with a wrong password"""
        # First register a user
        client.post("/auth/register", json=self.valid_register_data)
        
        # Then try to log in with a wrong password
        wrong_password_data = {
            "username": self.valid_login_data["username"],
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", json=wrong_password_data)
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

    def test_logout_success(self):
        """Test successful logout"""
        # Register and login
        client.post("/auth/register", json=self.valid_register_data)
        login_response = client.post("/auth/login", json=self.valid_login_data)
        token = login_response.json()["token"]
        
        # Logout
        logout_response = client.post("/auth/logout", json={"token": token})
        assert logout_response.status_code == 204

    def test_logout_invalid_token(self):
        """Test logout with an invalid token"""
        logout_response = client.post("/auth/logout", json={"token": "invalid-token"})
        assert logout_response.status_code == 400
        assert "Invalid session token" in logout_response.json()["detail"]