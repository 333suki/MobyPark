from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import desc
from datetime import datetime
import hashlib
import uuid

from app.db.database import SessionLocal
from app.db.models.payment import Payment
from app.db.models.user import User
from app.api.login_sessions.session_manager import LoginSessionManager
from app.util.db_utils import DbUtils
from app.util.payment_utils import PaymentUtils
from app.api.payments.schemas import PaymentCreate, PaymentRefund, PaymentComplete

router = APIRouter(prefix="/payments", tags=["payments"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def get_payments(request: Request, db: Session = Depends(get_db)):
    """Get all payments for the current user"""
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing session token"
        )
    
    user_id = LoginSessionManager.get_user_id(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing session token"
        )
    
    # Get payments where user is the initiator
    payments = db.query(Payment).filter(
        Payment.initiator_id == user_id
    ).all()
    
    return payments

@router.get("/{username}")
async def get_payments_by_user(
    username: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all payments for a specific user (admin only)"""
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing session token"
        )
    
    user_id = LoginSessionManager.get_user_id(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing session token"
        )
    
    # Check if user is admin
    user_role = DbUtils.get_user_role(db, user_id)
    if user_role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get payments for specified user
    payments = db.query(Payment).filter(
        Payment.initiator_id == user_id
    ).all()
    
    return payments


@router.post("/")
async def post_payment(
    body: PaymentCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new payment transaction"""
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing session token"
        )
    
    user_id = LoginSessionManager.get_user_id(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing session token"
        )

    payment = Payment(
        transaction=body.transaction,
        amount=body.amount,
        initiator_id=user_id,
        created_at=datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        completed=False,
        hash=PaymentUtils.generate_transaction_validation_hash()
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    return {
        "status": "Success",
        "payment": payment
    }

@router.post("/refund")
async def refund_payment():
    pass

@router.put("payments/{payment_id}")
async def update_payment(payment_id: int):
    pass