from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session

from app.api.parking_sessions.schemas import ParkingSessionResponse
from app.db.database import SessionLocal
from app.db.models.parking_lot import ParkingLot
from app.db.models.parking_session import ParkingSession
from app.util.db_utils import DbUtils
from app.util.jwt_authenticator import JWTAuthenticator, TokenMissingError, TokenInvalidError, TokenExpiredError
from app.util.parking_session_utils import ParkingSessionService

router = APIRouter(prefix="/parking_sessions", tags=["parking_sessions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[ParkingSessionResponse])
async def get_parking_sessions(
        request: Request,
        limit: Optional[int] = Query(None, description="Limit the amount of results", ge=1),
        parking_lot_id: Optional[int] = Query(None, description="Filter by parking lot ID"),
        license_plate: Optional[str] = Query(None, description="Filter by license plate"),
        date: Optional[datetime] = Query(None, description="Filter by date (YYYY-MM-DD)"),
        search_username: Optional[str] = Query(None, description="Filter by username"),
        db: Session = Depends(get_db)
):
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
    role: str = user_info.get("role")
    username = DbUtils.get_username(db, user_id)

    # Return sessions based on role
    if role.lower() == "admin":
        sessions = ParkingSessionService.get_all_sessions(
            db, limit, parking_lot_id, license_plate, date, search_username
        )
    else:
        sessions = ParkingSessionService.get_user_sessions(
            db, username, limit, parking_lot_id, license_plate, date, search_username
        )

    return sessions

@router.post("/start/{parking_lot_id}/{license_plate}", response_model=ParkingSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_parking_session(
        parking_lot_id: int,
        license_plate: str,
        request: Request,
        db: Session = Depends(get_db)
):
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
    role: str = user_info.get("role")


    # Check if parking lot exists
    parking_lot = db.query(ParkingLot).filter(ParkingLot.id == parking_lot_id).first()
    if not parking_lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parking lot with ID {parking_lot_id} not found"
        )
    
    # Check if there's already an active session for this license plate
    if ParkingSessionService.check_active_session(db, license_plate):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An active parking session already exists for this license plate"
        )

    username = ParkingSessionService.get_username(db, user_id) or "guest"
    
    # Skip verification if user is admin
    if not role.lower() == "admin":
        # Check if license plate is registered to an account
        registered_user = ParkingSessionService.get_user_by_license_plate(db, license_plate)
        
        # If license plate is registered to a user, verify
        if registered_user:
            if username != registered_user.username:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"This license plate is registered to another user. You cannot start a session for it."
                )

    # Create new parking session
    new_session = ParkingSession(
        parking_lot_id=parking_lot_id,
        license_plate=license_plate,
        username=username,
        started=datetime.now(),
        stopped=None,
        duration_minutes=None,
        cost=None,
        payment_status="ongoing"
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session

@router.post("/stop/{license_plate}", response_model=ParkingSessionResponse, status_code=status.HTTP_200_OK)
async def stop_parking_session(
        license_plate: str,
        request: Request,
        db: Session = Depends(get_db)):
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
    role: str = user_info.get("role")
    
    # Find active parking session
    active_session = db.query(ParkingSession).filter(
        ParkingSession.license_plate == license_plate,
        ParkingSession.stopped == None
    ).first()
    
    if not active_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active parking session found for this license plate"
        )

    # Try to get username and role from token (optional)
    # token = request.headers.get("Authorization")

    username = DbUtils.get_username(db, user_id) or None
    
    # Skip verification if user is admin
    if not role.lower() == "admin":
        # Guest sessions can be stopped by anyone
        if active_session.username != "guest":
            # User sessions require ownership verification
            if username != active_session.username:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only stop your own parking sessions"
                )

    # Stop the session
    active_session.stopped = datetime.now()
    active_session.duration_minutes = int((active_session.stopped - active_session.started).total_seconds() / 60)
    
    # Calculate cost based on duration and parking lot rates
    active_session.cost = ParkingSessionService.calculate_price(DbUtils.get_parking_lot_by_id(db, active_session.parking_lot_id), active_session)
    active_session.payment_status = "pending"
    
    db.commit()
    db.refresh(active_session)

    return active_session
