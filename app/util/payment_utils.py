import uuid
from hashlib import md5

from sqlalchemy.orm import Session

from app.db.models.payment import Payment


class PaymentUtils:
    
    @staticmethod
    def generate_payment_hash(sessionid: str, license_plate: str) -> str:
        """
        Generate a payment transaction hash based on session ID and license plate
        """
        #return md5(str(sessionid + license_plate).encode("utf-8")).hexdigest()
        return md5((f"{sessionid}{license_plate}").encode("utf-8")).hexdigest()
    
    @staticmethod
    def check_payment_amount(transaction_hash: str, db: Session) -> float:
        """Check how much has been paid for a transaction"""
        payments = db.query(Payment).filter(
            Payment.transaction == transaction_hash
        ).all()
        
        total_paid = sum(payment.amount for payment in payments)
        return total_paid
    
    @staticmethod
    def generate_transaction_validation_hash() -> str:
        """
        Generate a unique validation hash for transaction security
        """
        return str(uuid.uuid4())
    


