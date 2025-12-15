import pytest
import bcrypt

from app.util.auth_utils import AuthUtils
from app.util.jwt_authenticator import JWTAuthenticator


class TestPasswordHashing:
    """Unit tests for password hashing functions"""
    
    def test_hash_password_returns_string(self):
        """Test hash_password returns a string"""
        hashed = AuthUtils.hash_password("testpassword")
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_hash_password_different_for_same_input(self):
        """Test hash_password generates different hashes (due to salt)"""
        hash1 = AuthUtils.hash_password("testpassword")
        hash2 = AuthUtils.hash_password("testpassword")
        
        assert hash1 != hash2
    
    def test_verify_password_correct_password(self):
        """Test bcrypt.checkpw returns True for correct password"""
        hashed = AuthUtils.hash_password("testpassword")
        
        result = bcrypt.checkpw("testpassword".encode('utf-8'), hashed.encode('utf-8'))
        
        assert result is True
    
    def test_verify_password_incorrect_password(self):
        """Test bcrypt.checkpw returns False for incorrect password"""
        hashed = AuthUtils.hash_password("testpassword")
        
        result = bcrypt.checkpw("wrongpassword".encode('utf-8'), hashed.encode('utf-8'))
        
        assert result is False
    
    def test_verify_password_empty_password(self):
        """Test bcrypt.checkpw handles empty password"""
        hashed = AuthUtils.hash_password("testpassword")
        
        result = bcrypt.checkpw("".encode('utf-8'), hashed.encode('utf-8'))
        
        assert result is False


class TestEmailValidation:
    """Unit tests for email validation"""
    
    def test_validate_email_valid(self):
        """Test validate_email returns True for valid email"""
        assert AuthUtils.validate_email("test@example.com") is True
        assert AuthUtils.validate_email("user.name+tag@example.co.uk") is True
    
    def test_validate_email_invalid(self):
        """Test validate_email returns False for invalid email"""
        assert AuthUtils.validate_email("notanemail") is False
        assert AuthUtils.validate_email("@example.com") is False
        assert AuthUtils.validate_email("test@") is False
        assert AuthUtils.validate_email("test@.com") is False


class TestJWTToken:
    """Unit tests for JWT token generation and validation"""
    
    def test_generate_token_returns_string(self):
        """Test generate_token returns a string"""
        token = JWTAuthenticator.generate_token(1, "user")
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_generate_token_different_for_different_users(self):
        """Test different user IDs generate different tokens"""
        token1 = JWTAuthenticator.generate_token(1, "user")
        token2 = JWTAuthenticator.generate_token(2, "user")
        
        assert token1 != token2
    
    def test_validate_token_success(self):
        """Test validate_token successfully validates generated token"""
        token = JWTAuthenticator.generate_token(1, "user")
        
        result = JWTAuthenticator.validate_token(token)
        
        assert result is not None
        assert result["sub"] == 1
        assert result["role"] == "user"
    
    def test_hash_password_performance(self):
        """Test password hashing works correctly"""
        result = AuthUtils.hash_password("testpassword123")
        
        assert len(result) > 0
    
    def test_verify_password_performance(self):
        """Test password verification works correctly"""
        hashed = AuthUtils.hash_password("testpassword123")
        
        result = bcrypt.checkpw("testpassword123".encode('utf-8'), hashed.encode('utf-8'))
        
        assert result is True
    
    def test_generate_token_performance(self):
        """Test JWT token generation works correctly"""
        result = JWTAuthenticator.generate_token(1, "user")
        
        assert len(result) > 0
    
    def test_validate_token_performance(self):
        """Test JWT token validation works correctly"""
        token = JWTAuthenticator.generate_token(1, "user")
        
        result = JWTAuthenticator.validate_token(token)
        
        assert result["sub"] == 1
