import pytest
from datetime import datetime

from app.util.payment_utils import PaymentUtils
from app.db.database import SessionLocal
from app.db.models.payment import Payment
from app.db.models.parking_session import ParkingSession
from app.db.models.parking_lot import ParkingLot
from app.db.models.user import User
from app.db.models.vehicle import Vehicle
from app.util.auth_utils import AuthUtils


class TestGeneratePaymentHash:
    """Unit tests for generate_payment_hash"""
    
    def test_generates_consistent_hash(self):
        """Test hash is consistent for same input"""
        hash1 = PaymentUtils.generate_payment_hash("123", "ABC123")
        hash2 = PaymentUtils.generate_payment_hash("123", "ABC123")
        
        assert hash1 == hash2
    
    def test_different_sessions_different_hash(self):
        """Test different session IDs produce different hashes"""
        hash1 = PaymentUtils.generate_payment_hash("123", "ABC123")
        hash2 = PaymentUtils.generate_payment_hash("456", "ABC123")
        
        assert hash1 != hash2
    
    def test_different_license_plates_different_hash(self):
        """Test different license plates produce different hashes"""
        hash1 = PaymentUtils.generate_payment_hash("123", "ABC123")
        hash2 = PaymentUtils.generate_payment_hash("123", "XYZ789")
        
        assert hash1 != hash2
    
    def test_hash_format(self):
        """Test hash is MD5 format (32 hex chars)"""
        hash_result = PaymentUtils.generate_payment_hash("123", "ABC123")
        
        assert len(hash_result) == 32
        assert all(c in '0123456789abcdef' for c in hash_result)


class TestCheckPaymentAmount:
    """Unit tests for check_payment_amount"""
    
    def test_returns_total_paid_for_transaction(self):
        """Test returns total amount paid for a transaction hash"""
        db = SessionLocal()
        
        # Create test data
        user = User(username="test_payment1", email="test_payment1@test.com", hashed_password=AuthUtils.hash_password("test"))
        db.add(user)
        db.commit()
        db.refresh(user)
        
        vehicle = Vehicle(license_plate="PAY123", user_id=user.id, make="Test", model="Car")
        db.add(vehicle)
        db.commit()
        
        parking_lot = ParkingLot(name="Test Lot", address="123 Test St", capacity=10, tariff=5.0, daytariff=25.0)
        db.add(parking_lot)
        db.commit()
        db.refresh(parking_lot)
        
        session = ParkingSession(
            license_plate="PAY123",
            parking_lot_id=parking_lot.id,
            started=datetime.now(),
            stopped=datetime.now(),
            username=user.username
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        transaction_hash = "test_transaction_123"
        payment1 = Payment(parking_session_id=session.id, amount=50.00, transaction=transaction_hash)
        payment2 = Payment(parking_session_id=session.id, amount=30.00, transaction=transaction_hash)
        db.add(payment1)
        db.add(payment2)
        db.commit()
        
        result = PaymentUtils.check_payment_amount(transaction_hash, db)
        
        assert result == 80.00
        
        # Cleanup
        db.delete(payment1)
        db.delete(payment2)
        db.delete(session)
        db.delete(vehicle)
        db.delete(parking_lot)
        db.delete(user)
        db.commit()
        db.close()
    
    def test_returns_zero_when_no_payment(self):
        """Test returns 0 when no payment exists"""
        db = SessionLocal()
        
        result = PaymentUtils.check_payment_amount("nonexistent_hash", db)
        
        assert result == 0.0
        db.close()
    
    def test_returns_correct_sum_with_multiple_payments(self):
        """Test returns correct sum with multiple payments"""
        db = SessionLocal()
        
        # Create test data
        user = User(username="test_payment2", email="test_payment2@test.com", hashed_password=AuthUtils.hash_password("test"))
        db.add(user)
        db.commit()
        db.refresh(user)
        
        vehicle = Vehicle(license_plate="PAY456", user_id=user.id, make="Test", model="Car")
        db.add(vehicle)
        db.commit()
        
        parking_lot = ParkingLot(name="Test Lot", address="123 Test St", capacity=10, tariff=5.0, daytariff=25.0)
        db.add(parking_lot)
        db.commit()
        db.refresh(parking_lot)
        
        session = ParkingSession(
            license_plate="PAY456",
            parking_lot_id=parking_lot.id,
            started=datetime.now(),
            stopped=datetime.now(),
            username=user.username
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        transaction_hash = "test_transaction_456"
        payments = [
            Payment(parking_session_id=session.id, amount=10.00, transaction=transaction_hash),
            Payment(parking_session_id=session.id, amount=20.00, transaction=transaction_hash),
            Payment(parking_session_id=session.id, amount=30.00, transaction=transaction_hash)
        ]
        for payment in payments:
            db.add(payment)
        db.commit()
        
        result = PaymentUtils.check_payment_amount(transaction_hash, db)
        
        assert result == 60.00
        
        # Cleanup
        for payment in payments:
            db.delete(payment)
        db.delete(session)
        db.delete(vehicle)
        db.delete(parking_lot)
        db.delete(user)
        db.commit()
        db.close()


class TestGenerateTransactionValidationHash:
    """Unit tests for generate_transaction_validation_hash"""
    
    def test_generates_unique_hash(self):
        """Test generates unique UUID for each call"""
        hash1 = PaymentUtils.generate_transaction_validation_hash()
        hash2 = PaymentUtils.generate_transaction_validation_hash()
        
        assert hash1 != hash2
    
    def test_hash_is_valid_uuid(self):
        """Test generated hash is a valid UUID string"""
        import uuid
        
        hash_result = PaymentUtils.generate_transaction_validation_hash()
        
        # Should be able to parse as UUID
        try:
            uuid.UUID(hash_result)
            assert True
        except ValueError:
            assert False, "Generated hash is not a valid UUID"
