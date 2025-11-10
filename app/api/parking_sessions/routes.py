from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import desc
from datetime import datetime

from app.db.database import SessionLocal
from app.db.models.parking_session import ParkingSession
from app.db.models.user import User
from app.db.models.parking_lot import ParkingLot
from app.api.login_sessions.session_manager import LoginSessionManager
from app.util.db_utils import DbUtils
from app.util.parking_session_utils import ParkingSessionService
from app.api.parking_sessions.schemas import ParkingSessionResponse

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
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token"
        )

    # Get user info
    user_id = LoginSessionManager.get_user_id(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # Get role and username
    role = DbUtils.get_user_role(db, user_id)
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

    # Try to get username and role from token (optional)
    username = "guest"
    is_admin = False
    token = request.headers.get("Authorization")
    
    if token:
        user_id = LoginSessionManager.get_user_id(token)
        if user_id:
            username = ParkingSessionService.get_username(db, user_id) or "guest"
            role = DbUtils.get_user_role(db, user_id)
            is_admin = role.lower() == "admin"
    
    # Skip verification if user is admin
    if not is_admin:
        # Check if license plate is registered to an account
        registered_user = ParkingSessionService.get_user_by_license_plate(db, license_plate)
        
        # If license plate is registered to a user, verify authorization
        if registered_user:
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"This license plate is registered to another user. You cannot start a session for it."
                )
            
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
    username = None
    is_admin = False
    token = request.headers.get("Authorization")
    
    if token:
        user_id = LoginSessionManager.get_user_id(token)
        if user_id:
            username = ParkingSessionService.get_username(db, user_id)
            role = DbUtils.get_user_role(db, user_id)
            is_admin = role.lower() == "admin"
    
    # Skip verification if user is admin
    if not is_admin:
        # Guest sessions can be stopped by anyone
        if active_session.username != "guest":
            # User sessions require authentication and ownership verification
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authorization required to stop a user's parking session"
                )
            
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