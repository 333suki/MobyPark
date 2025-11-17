from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api.billing.schemas import BillingResponse
from app.db.database import SessionLocal
from app.db.models.parking_lot import ParkingLot
from app.db.models.parking_session import ParkingSession
from app.util.db_utils import DbUtils
from app.util.jwt_authenticator import JWTAuthenticator, TokenMissingError, TokenInvalidError, TokenExpiredError
from app.util.payment_utils import PaymentUtils

router = APIRouter(prefix="/billing", tags=["billing"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[BillingResponse])
async def get_user_billing(request: Request, db: Session = Depends(get_db)):
    """Get billing information for the authenticated user"""
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
    
    # Get username
    username = DbUtils.get_username(db, user_id)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Get all stopped sessions for this user
    sessions = db.query(ParkingSession).filter(
        ParkingSession.username == username,
        ParkingSession.stopped != None
    ).all()
    
    billing_data = []
    
    for session in sessions:
        # Get parking lot info
        parking_lot = db.query(ParkingLot).filter(
            ParkingLot.id == session.parking_lot_id
        ).first()
        
        if not parking_lot:
            continue
        
        # Calculate payment info
        transaction_hash = PaymentUtils.generate_payment_hash(session.id, session.license_plate)
        amount_paid = PaymentUtils.check_payment_amount(transaction_hash, db)
        
        # Calculate hours and days
        duration_minutes = session.duration_minutes or 0
        hours = duration_minutes / 60
        days = int(duration_minutes / (60 * 24))
        
        billing_data.append({
            "session": {
                "license_plate": session.license_plate,
                "started": session.started,
                "stopped": session.stopped,
                "hours": hours,
                "days": days
            },
            "parking": {
                "name": parking_lot.name,
                "location": parking_lot.location,
                "tariff": parking_lot.tariff,
                "daytariff": parking_lot.daytariff
            },
            "amount": session.cost or 0,
            "thash": transaction_hash,
            "payed": amount_paid,
            "balance": (session.cost or 0) - amount_paid
        })
    
    return billing_data


@router.get("/{username}", response_model=List[BillingResponse])
async def get_user_billing_by_username(
    username: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get billing information for a specific user (admin only)"""
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

    role: str = user_info.get("role")
    
    # Check if user is admin
    if role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get all stopped sessions for specified user
    sessions = db.query(ParkingSession).filter(
        ParkingSession.username == username,
        ParkingSession.stopped != None
    ).all()
    
    billing_data = []
    
    for session in sessions:
        # Get parking lot info
        parking_lot = db.query(ParkingLot).filter(
            ParkingLot.id == session.parking_lot_id
        ).first()
        
        if not parking_lot:
            continue
        
        # Calculate payment info
        transaction_hash = PaymentUtils.generate_payment_hash(session.id, session.license_plate)
        amount_paid = PaymentUtils.check_payment_amount(transaction_hash, db)
        
        # Calculate hours and days
        duration_minutes = session.duration_minutes or 0
        hours = duration_minutes / 60
        days = int(duration_minutes / (60 * 24))
        
        billing_data.append({
            "session": {
                "license_plate": session.license_plate,
                "started": session.started,
                "stopped": session.stopped,
                "hours": hours,
                "days": days
            },
            "parking": {
                "name": parking_lot.name,
                "location": parking_lot.location,
                "tariff": parking_lot.tariff,
                "daytariff": parking_lot.daytariff
            },
            "amount": session.cost or 0,
            "thash": transaction_hash,
            "payed": amount_paid,
            "balance": (session.cost or 0) - amount_paid
        })
    
    return billing_data