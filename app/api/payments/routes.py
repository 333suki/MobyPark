from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api.payments.schemas import PaymentCreate
from app.db.database import SessionLocal
from app.db.models.payment import Payment
from app.util.jwt_authenticator import JWTAuthenticator, TokenMissingError, TokenInvalidError, TokenExpiredError
from app.util.payment_utils import PaymentUtils

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
    # Validate token
    try:
        user_info: dict = JWTAuthenticator.validate_token(request.headers.get("Authorization"))
    except TokenMissingError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except TokenInvalidError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except TokenExpiredError as e:
        raise HTTPException(
            status_code=498,
            detail=str(e)
        )

    user_id: int = user_info.get("sub")
    
    # Get payments where user is the initiator
    payments = db.query(Payment).filter(
        Payment.initiator_id == user_id
    ).all()
    
    return payments

@router.get("/{user_id}")
async def get_payments_by_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all payments for a specific user (admin only)"""
    # Validate token
    try:
        user_info: dict = JWTAuthenticator.validate_token(request.headers.get("Authorization"))
    except TokenMissingError as e:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    except TokenInvalidError as e:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    except TokenExpiredError as e:
        raise HTTPException(
            status_code=498,
            detail=str(e)
        )

    user_role: str = user_info.get("role")
    
    # Check if user is admin
    if user_role.lower() != "admin":
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
    # Validate token
    try:
        user_info: dict = JWTAuthenticator.validate_token(request.headers.get("Authorization"))
    except TokenMissingError as e:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    except TokenInvalidError as e:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
    except TokenExpiredError as e:
        raise HTTPException(
            status_code=498,
            detail=str(e)
        )

    user_id: int = user_info.get("sub")

    payment = Payment(
        transaction=body.transaction,
        amount=body.amount,
        initiator_id=user_id,
        created_at=datetime.now(),
        completed=None,
        hash=PaymentUtils.generate_transaction_validation_hash()
    )
    
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    return {
        "payment": payment
    }

@router.post("/refund")
async def refund_payment():
    pass

@router.put("payments/{payment_id}")
async def update_payment(payment_id: int):
    pass
