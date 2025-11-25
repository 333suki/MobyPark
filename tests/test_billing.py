from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import time

from app.main import app

client = TestClient(app)


class TestGetUserBilling:
    """Tests for GET /billing/ endpoint"""

    def test_get_billing_without_token(self):
        """Test getting billing without authentication"""
        response = client.get("/billing/")
        
        assert response.status_code == 401

    def test_get_billing_empty_sessions(self):
        """Test getting billing when user has no stopped sessions"""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "username": "billinguser1",
                "email": "billing1@example.com",
                "password": "Password123!",
                "name": "Billing User 1",
                "phone": "1234567890",
                "birth_year": 1990
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={"username": "billinguser1", "password": "Password123!"}
        )
        token = login_response.json()["token"]
        
        response = client.get(
            "/billing/",
            headers={"Authorization": token}
        )
        
        assert response.status_code == 200
        assert response.json() == []

    def test_get_billing_with_stopped_session(self):
        """Test getting billing with stopped session"""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "username": "billinguser2",
                "email": "billing2@example.com",
                "password": "Password123!",
                "name": "Billing User2",
                "phone": "1234567890",
                "birth_year": 1990
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={"username": "billinguser2", "password": "Password123!"}
        )
        token = login_response.json()["token"]
        
        # Start and stop a parking session
        client.post(
            f"/parking_sessions/start/{1}/BILLING123",
            headers={"Authorization": token}
        )
        
        time.sleep(1)
        
        client.post(
            "/parking_sessions/stop/BILLING123",
            headers={"Authorization": token}
        )
        
        # Check billing
        response = client.get(
            "/billing/",
            headers={"Authorization": token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        
        # Verify structure
        our_session = next((s for s in data if s["session"]["license_plate"] == "BILLING123"), None)
        assert our_session is not None
        assert "amount" in our_session
        assert "payed" in our_session
        assert "balance" in our_session
        assert our_session["payed"] == 0

    def test_get_billing_with_payment(self):
        """Test billing updates after payment"""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "username": "billinguser3",
                "email": "billing3@example.com",
                "name": "Billing User 3",
                "password": "Password123!",
                "phone": "1234567890",
                "birth_year": 1990
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={"username": "billinguser3", "password": "Password123!"}
        )
        token = login_response.json()["token"]
        
        # Start and stop a parking session
        client.post(
            f"/parking_sessions/start/{1}/PAID123",
            headers={"Authorization": token}
        )
        
        time.sleep(1)
        
        client.post(
            "/parking_sessions/stop/PAID123",
            headers={"Authorization": token}
        )
        
        # Get billing
        billing_response = client.get(
            "/billing/",
            headers={"Authorization": token}
        )
        
        data = billing_response.json()
        our_session = next((s for s in data if s["session"]["license_plate"] == "PAID123"), None)
        
        if our_session:
            transaction_hash = our_session["thash"]
            amount_due = our_session["amount"]
            
            # Make a payment
            client.post(
                "/payments/",
                headers={"Authorization": token},
                json={
                    "transaction": transaction_hash,
                    "amount": 10.0
                }
            )
            
            # Check billing again
            billing_response2 = client.get(
                "/billing/",
                headers={"Authorization": token}
            )
            
            data2 = billing_response2.json()
            our_session2 = next((s for s in data2 if s["session"]["license_plate"] == "PAID123"), None)
            
            assert our_session2["payed"] == 10.0
            assert our_session2["balance"] == amount_due - 10.0


class TestGetBillingByUsername:
    """Tests for GET /billing/{username} endpoint"""

    def test_get_billing_by_username_no_auth(self):
        """Test getting user billing without authentication"""
        response = client.get("/billing/testuser")
        
        assert response.status_code == 401

    def test_get_billing_by_username_as_non_admin(self):
        """Test non-admin cannot access other user billing"""
        # Register regular user
        client.post(
            "/auth/register",
            json={
                "username": "regularuser1",
                "email": "regular1@example.com",
                "password": "Password123!",
                "name": "Regular User1",
                "phone": "1234567890",
                "birth_year": 1990
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={"username": "regularuser1", "password": "Password123!"}
        )
        token = login_response.json()["token"]
        
        response = client.get(
            "/billing/someotheruser",
            headers={"Authorization": token}
        )
        
        assert response.status_code == 403
        assert "access denied" in response.json()["detail"].lower()


class TestBillingIntegration:
    """Integration tests for complete billing flow"""

    def test_complete_parking_and_billing_flow(self):
        """Test full flow: register, park, pay, check billing"""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "username": "flowuser",
                "email": "flow@example.com",
                "password": "Password123!",
                "name": "Flow User",
                "phone": "1234567890",
                "birth_year": 1990
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={"username": "flowuser", "password": "Password123!"}
        )
        token = login_response.json()["token"]
        
        # Start and stop parking
        client.post(
            f"/parking_sessions/start/{1}/FLOW123",
            headers={"Authorization": token}
        )
        
        time.sleep(1)
        
        client.post(
            "/parking_sessions/stop/FLOW123",
            headers={"Authorization": token}
        )
        
        # Check billing
        billing_response = client.get(
            "/billing/",
            headers={"Authorization": token}
        )
        
        assert billing_response.status_code == 200
        data = billing_response.json()
        our_session = next((s for s in data if s["session"]["license_plate"] == "FLOW123"), None)
        
        assert our_session is not None
        
        # Verify response structure
        assert "session" in our_session
        assert "parking" in our_session
        assert "amount" in our_session
        assert "thash" in our_session
        assert "payed" in our_session
        assert "balance" in our_session