from fastapi.testclient import TestClient
from datetime import datetime
import time

from app.main import app

client = TestClient(app)


class TestGetPayments:
    """Tests for GET /payments/ endpoint"""

    def test_get_payments_without_token(self):
        """Test getting payments without authentication"""
        response = client.get("/payments/")
        
        assert response.status_code == 401

    def test_get_payments_empty(self):
        """Test getting payments when user has no payments"""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "username": "paymentuser1",
                "email": "payment1@example.com",
                "password": "Password123!"
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={"username": "paymentuser1", "password": "Password123!"}
        )
        token = login_response.json()["token"]
        
        response = client.get(
            "/payments/",
            headers={"Authorization": token}
        )
        
        assert response.status_code == 200
        assert response.json() == []

    def test_get_payments_with_payment(self):
        """Test getting payments after creating one"""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "username": "paymentuser2",
                "email": "payment2@example.com",
                "password": "Password123!"
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={"username": "paymentuser2", "password": "Password123!"}
        )
        token = login_response.json()["token"]
        
        # Create a payment
        client.post(
            "/payments/",
            headers={"Authorization": token},
            json={
                "transaction": "test-transaction-123",
                "amount": 25.0
            }
        )
        
        # Get payments
        response = client.get(
            "/payments/",
            headers={"Authorization": token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(p["transaction"] == "test-transaction-123" for p in data)


class TestGetPaymentsByUser:
    """Tests for GET /payments/{user_id} endpoint"""

    def test_get_payments_by_user_without_token(self):
        """Test getting user payments without authentication"""
        response = client.get("/payments/1")
        
        assert response.status_code == 401

    def test_get_payments_by_user_as_non_admin(self):
        """Test non-admin cannot access other user payments"""
        # Register regular user
        client.post(
            "/auth/register",
            json={
                "username": "regularuser3",
                "email": "regular3@example.com",
                "password": "Password123!"
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={"username": "regularuser3", "password": "Password123!"}
        )
        token = login_response.json()["token"]
        
        response = client.get(
            "/payments/1",
            headers={"Authorization": token}
        )
        
        assert response.status_code == 403
        assert "access denied" in response.json()["detail"].lower()


class TestCreatePayment:
    """Tests for POST /payments/ endpoint"""

    def test_create_payment_without_token(self):
        """Test creating payment without authentication"""
        response = client.post(
            "/payments/",
            json={
                "transaction": "test-transaction",
                "amount": 25.0
            }
        )
        
        assert response.status_code == 401

    def test_create_payment_success(self):
        """Test creating payment successfully"""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "username": "paymentuser4",
                "email": "payment4@example.com",
                "password": "Password123!"
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={"username": "paymentuser4", "password": "Password123!"}
        )
        token = login_response.json()["token"]
        
        # Create payment
        response = client.post(
            "/payments/",
            headers={"Authorization": token},
            json={
                "transaction": "test-transaction-456",
                "amount": 50.0
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "payment" in data
        assert data["payment"]["transaction"] == "test-transaction-456"
        assert data["payment"]["amount"] == 50.0
        assert data["payment"]["completed"] is None
        assert "hash" in data["payment"]

    def test_create_payment_missing_fields(self):
        """Test creating payment with missing fields"""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "username": "paymentuser5",
                "email": "payment5@example.com",
                "password": "Password123!"
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={"username": "paymentuser5", "password": "Password123!"}
        )
        token = login_response.json()["token"]
        
        # Try to create payment without amount
        response = client.post(
            "/payments/",
            headers={"Authorization": token},
            json={
                "transaction": "test-transaction"
            }
        )
        
        assert response.status_code == 422


class TestUpdatePayment:
    """Tests for PUT /payments/{transaction_id} endpoint"""

    def test_update_payment_not_found(self):
        """Test updating non-existent payment"""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "username": "paymentuser6",
                "email": "payment6@example.com",
                "password": "Password123!"
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={"username": "paymentuser6", "password": "Password123!"}
        )
        token = login_response.json()["token"]
        
        response = client.put(
            "/payments/nonexistenthash",
            headers={"Authorization": token},
            json={
                "id": 1,
                "amount": 25.0,
                "method": "credit_card",
                "issuer": "Visa",
                "bank": "Test Bank"
            }
        )
        
        assert response.status_code == 404

    def test_update_payment_success(self):
        """Test completing payment with transaction data"""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "username": "paymentuser7",
                "email": "payment7@example.com",
                "password": "Password123!"
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={"username": "paymentuser7", "password": "Password123!"}
        )
        token = login_response.json()["token"]
        
        # Create payment
        create_response = client.post(
            "/payments/",
            headers={"Authorization": token},
            json={
                "transaction": "test-transaction-789",
                "amount": 100.0
            }
        )
        
        payment_hash = create_response.json()["payment"]["hash"]
        
        # Complete payment
        response = client.put(
            f"/payments/{payment_hash}",
            headers={"Authorization": token},
            json={
                "id": 1,
                "amount": 100.0,
                "method": "credit_card",
                "issuer": "Mastercard",
                "bank": "Example Bank"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["payment"]["completed"] is not None
        assert "transaction" in data

    def test_update_payment_already_completed(self):
        """Test updating already completed payment"""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "username": "paymentuser8",
                "email": "payment8@example.com",
                "password": "Password123!"
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={"username": "paymentuser8", "password": "Password123!"}
        )
        token = login_response.json()["token"]
        
        # Create payment
        create_response = client.post(
            "/payments/",
            headers={"Authorization": token},
            json={
                "transaction": "test-transaction-completed",
                "amount": 75.0
            }
        )
        
        payment_hash = create_response.json()["payment"]["hash"]
        
        # Complete payment first time
        client.put(
            f"/payments/{payment_hash}",
            headers={"Authorization": token},
            json={
                "id": 1,
                "amount": 75.0,
                "method": "debit_card",
                "issuer": "Visa",
                "bank": "Test Bank"
            }
        )
        
        # Try to complete again
        response = client.put(
            f"/payments/{payment_hash}",
            headers={"Authorization": token},
            json={
                "id": 1,
                "amount": 75.0,
                "method": "debit_card",
                "issuer": "Visa",
                "bank": "Test Bank"
            }
        )
        
        assert response.status_code == 400
        assert "already completed" in response.json()["detail"].lower()


class TestRefundPayment:
    """Tests for POST /payments/refund/{payment_hash} endpoint"""

    def test_refund_payment_without_token(self):
        """Test refunding payment without authentication"""
        response = client.post("/payments/refund/somehash")
        
        assert response.status_code == 401

    def test_refund_payment_as_non_admin(self):
        """Test non-admin cannot refund payments"""
        # Register regular user
        client.post(
            "/auth/register",
            json={
                "username": "regularuser9",
                "email": "regular9@example.com",
                "password": "Password123!"
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={"username": "regularuser9", "password": "Password123!"}
        )
        token = login_response.json()["token"]
        
        response = client.post(
            "/payments/refund/somehash",
            headers={"Authorization": token}
        )
        
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()

class TestPaymentIntegration:
    """Integration tests for complete payment flow"""

    def test_complete_payment_flow(self):
        """Test full flow: create, complete payment"""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "username": "flowpayment",
                "email": "flowpayment@example.com",
                "password": "Password123!"
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={"username": "flowpayment", "password": "Password123!"}
        )
        token = login_response.json()["Authorization"]
        
        # Create payment
        create_response = client.post(
            "/payments/",
            headers={"Authorization": token},
            json={
                "transaction": "integration-test-payment",
                "amount": 150.0
            }
        )
        
        assert create_response.status_code == 200
        payment_hash = create_response.json()["payment"]["hash"]
        
        # Get payments
        get_response = client.get(
            "/payments/",
            headers={"Authorization": token}
        )
        
        assert get_response.status_code == 200
        payments = get_response.json()
        assert any(p["hash"] == payment_hash for p in payments)
        
        # Complete payment
        complete_response = client.put(
            f"/payments/{payment_hash}",
            headers={"Authorization": token},
            json={
                "id": 1,
                "amount": 150.0,
                "method": "credit_card",
                "issuer": "Amex",
                "bank": "Integration Bank"
            }
        )
        
        assert complete_response.status_code == 200
        assert complete_response.json()["payment"]["completed"] is not None

    def test_payment_for_parking_session(self):
        """Test creating payment for actual parking session"""
        # Register and login
        client.post(
            "/auth/register",
            json={
                "username": "parkingpayment",
                "email": "parkingpayment@example.com",
                "password": "Password123!"
            }
        )
        
        login_response = client.post(
            "/auth/login",
            json={"username": "parkingpayment", "password": "Password123!"}
        )
        token = login_response.json()["token"]
        
        # Start and stop parking
        client.post(
            f"/parking_sessions/start/{1}/PAYMENT999",
            headers={"Authorization": token}
        )
        
        time.sleep(1)
        
        client.post(
            "/parking_sessions/stop/PAYMENT999",
            headers={"Authorization": token}
        )
        
        # Get billing
        billing_response = client.get(
            "/billing/",
            headers={"Authorization": token}
        )
        
        data = billing_response.json()
        our_session = next((s for s in data if s["session"]["license_plate"] == "PAYMENT999"), None)
        
        if our_session:
            transaction_hash = our_session["thash"]
            amount = our_session["amount"]
            
            # Make payment
            payment_response = client.post(
                "/payments/",
                headers={"Authorization": token},
                json={
                    "transaction": transaction_hash,
                    "amount": amount
                }
            )
            
            assert payment_response.status_code == 200
            assert payment_response.json()["payment"]["amount"] == amount
