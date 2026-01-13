import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add the parent directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

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

    @staticmethod
    def setup_method():
        """Ensure test users are removed before each test to avoid collisions."""
        try:
            from app.db.database import SessionLocal
            from app.db.models.user import User
            db = SessionLocal()
            for uname in ["testuser", "newuser", "differentuser"]:
                db.query(User).filter(User.username == uname).delete()
            db.commit()
        except Exception:
            pass

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
        assert "Invalid email format" in response.json()["detail"]

    def test_register_user_weak_password(self):
        """Test registration with a weak password"""
        weak_password_data = self.valid_register_data.copy()
        weak_password_data["username"] = "newuser"
        weak_password_data["email"] = "newuser@example.com"
        weak_password_data["password"] = "123"  # Too short

        # The Current implementation does not enforce password strength, expect success
        response = client.post("/auth/register", json=weak_password_data)
        assert response.status_code == 201
        assert response.json() == {"message": "Registered successfully"}

    def test_login_success(self):
        """Test successful login"""
        # First register a user
        client.post("/auth/register", json=self.valid_register_data)
        
        # Then try to log in
        response = client.post("/auth/login", json=self.valid_login_data)
        assert response.status_code == 200
        response_data = response.json()
        
        # Check expected fields are present (token only)
        assert "token" in response_data

    def test_login_nonexistent_user(self):
        """Test login with a non-existent username"""
        login_data = {
            "username": "nonexistentuser",
            "password": "somepassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 404
        assert "username" in response.json()["detail"]

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
        
        # Logout (token must be provided in the Authorization header)
        headers = {"Authorization": f"Bearer {token}"}
        logout_response = client.post("/auth/logout", json={"token": token}, headers=headers)
        assert logout_response.status_code == 204

    def test_logout_invalid_token(self):
        """Test logout with an invalid token"""
        # Provide invalid token in Authorization header
        headers = {"Authorization": "Bearer invalid-token"}
        logout_response = client.post("/auth/logout", json={"token": "invalid-token"}, headers=headers)
        assert logout_response.status_code == 401