import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAuth:
    # Test data
    valid_register_data = {
        "username": "testuser",
        "password": "testpassword123",
        "name": "Test User",
        "email": "testuser@example.com",
        "phone": "1234567890",
        "birth_year": 1990
    }
    
    valid_login_data = {
        "username": "testuser",
        "password": "testpassword123"
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
        
        # Second registration with same username
        duplicate_data = self.valid_register_data.copy()
        duplicate_data["email"] = "different@example.com"
        
        response = client.post("/auth/register", json=duplicate_data)
        
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]

    def test_register_user_duplicate_email(self):
        """Test registration with duplicate email"""
        # First registration
        client.post("/auth/register", json=self.valid_register_data)
        
        # Second registration with same email
        duplicate_data = self.valid_register_data.copy()
        duplicate_data["username"] = "differentuser"
        
        response = client.post("/auth/register", json=duplicate_data)
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_register_user_missing_required_fields(self):
        """Test registration with missing required fields"""
        incomplete_data = {
            "username": "incompleteuser",
            "password": "password123"
            # Missing name, email, phone, birth_year
        }
        
        response = client.post("/auth/register", json=incomplete_data)
        
        assert response.status_code == 400

    def test_register_user_invalid_email_format(self):
        """Test registration with invalid email format"""
        invalid_email_data = self.valid_register_data.copy()
        invalid_email_data["username"] = "newuser"
        invalid_email_data["email"] = "invalid-email"
        
        response = client.post("/auth/register", json=invalid_email_data)
        
        assert response.status_code == 400

    def test_login_success(self):
        """Test successful login"""
        # First register a user
        client.post("/auth/register", json=self.valid_register_data)
        
        # Then try to login
        response = client.post("/auth/login", json=self.valid_login_data)
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Check all expected fields are present
        assert "token" in response_data
        assert response_data["username"] == self.valid_login_data["username"]
        assert response_data["name"] == self.valid_register_data["name"]
        assert response_data["email"] == self.valid_register_data["email"]
        assert response_data["phone"] == self.valid_register_data["phone"]
        assert response_data["birth_year"] == self.valid_register_data["birth_year"]
        assert response_data["role"] == "user"  # Default role
        assert response_data["active"] == True  # Default active status

    def test_login_nonexistent_user(self):
        """Test login with non-existent username"""
        login_data = {
            "username": "nonexistentuser",
            "password": "somepassword"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 400
        assert "Username doesn't exist" in response.json()["detail"]

    def test_login_wrong_password(self):
        """Test login with wrong password"""
        # First register a user
        client.post("/auth/register", json=self.valid_register_data)
        
        # Then try to login with wrong password
        wrong_password_data = {
            "username": self.valid_login_data["username"],
            "password": "wrongpassword"
        }
        
        response = client.post("/auth/login", json=wrong_password_data)
        
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

    def test_login_missing_credentials(self):
        """Test login with missing credentials"""
        # Missing password
        incomplete_data = {
            "username": "testuser"
        }
        
        response = client.post("/auth/login", json=incomplete_data)
        
        assert response.status_code == 400  # Validation error

    def test_login_already_logged_in(self):
        """Test login when user is already logged in"""
        # Register and login once
        client.post("/auth/register", json=self.valid_register_data)
        first_login_response = client.post("/auth/login", json=self.valid_login_data)
        
        # Try to login again with same credentials
        second_login_response = client.post("/auth/login", json=self.valid_login_data)
        
        assert second_login_response.status_code == 400
        assert "User already logged in" in second_login_response.json()["detail"]

    def test_register_with_custom_role_and_active(self):
        """Test registration with custom role and active status"""
        custom_data = {
            "username": "adminuser",
            "password": "adminpass123",
            "name": "Admin User",
            "email": "admin@example.com",
            "phone": "0987654321",
            "birth_year": 1985,
            "role": "admin",
            "active": False
        }
        
        response = client.post("/auth/register", json=custom_data)
        
        assert response.status_code == 201
        assert response.json() == {"message": "Registered successfully"}

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
        """Test logout with invalid token"""
        logout_response = client.post("/auth/logout", json={"token": "invalid-token"})
        
        assert logout_response.status_code == 400
        assert "Invalid session token" in logout_response.json()["detail"]

    def test_password_hashing(self):
        """Verify that passwords are properly hashed"""
        # Register a user
        client.post("/auth/register", json=self.valid_register_data)
        
        # Login with correct password should work
        correct_login_response = client.post("/auth/login", json=self.valid_login_data)
        assert correct_login_response.status_code == 200
        
        # Login with wrong password should fail
        wrong_login_response = client.post("/auth/login", json={
            "username": self.valid_login_data["username"],
            "password": "wrongpassword"
        })
        assert wrong_login_response.status_code == 401

# Additional test for edge cases
def test_register_special_characters_in_username():
    """Test registration with special characters in username"""
    special_char_data = {
        "username": "user_name-123",
        "password": "password123",
        "name": "Special User",
        "email": "special@example.com",
        "phone": "1112223333",
        "birth_year": 1995
    }
    
    response = client.post("/auth/register", json=special_char_data)
    
    assert response.status_code == 201

def test_register_minimal_birth_year():
    """Test registration with very old birth year"""
    old_birth_year_data = {
        "username": "olduser",
        "password": "password123",
        "name": "Old User",
        "email": "old@example.com",
        "phone": "4445556666",
        "birth_year": 1900
    }
    
    response = client.post("/auth/register", json=old_birth_year_data)
    
    assert response.status_code == 201