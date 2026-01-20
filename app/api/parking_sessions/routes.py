from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Body
from sqlalchemy.orm import Session

from app.api.parking_sessions.schemas import ParkingSessionResponse, StopParkingSessionBody, CreateReservationBody
from app.db.database import SessionLocal
from app.db.models.discount_code import DiscountCode
from app.db.models.parking_lot import ParkingLot
from app.db.models.parking_session import ParkingSession
from app.util.db_utils import DbUtils
from app.util.jwt_authenticator import JWTAuthenticator, TokenMissingError, TokenInvalidError, TokenExpiredError
from app.util.parking_lot_utils import ParkingLotUtils
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
        body: Optional[CreateReservationBody] = Body(None),
        db: Session = Depends(get_db)
):
    # Try to validate token (optional for guest sessions)
    user_id = None
    role = None
    username = "guest"
    
    token = request.headers.get("Authorization")
    if token:
        try:
            user_info: dict = JWTAuthenticator.validate_token(token)
            user_id = user_info.get("sub")
            role = user_info.get("role")
            username = ParkingSessionService.get_username(db, user_id) or "guest"
        except (TokenMissingError, TokenInvalidError, TokenExpiredError):
            # If token is invalid, treat as guest
            pass

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

    # Check if there is a free parking spot
    free_parking_spots: int | None = ParkingLotUtils.get_free_parking_spots(db, parking_lot_id, datetime.now(), datetime.now() + timedelta(hours=1))
    if free_parking_spots is None or free_parking_spots == 0:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail=f"No free parking spot on parking lot with id {parking_lot_id}."
        )
    
    # Skip verification if user is admin or guest
    if role and role.lower() != "admin":
        # Check if license plate is registered to an account
        registered_user = ParkingSessionService.get_user_by_license_plate(db, license_plate)
        
        # If license plate is registered to a user, verify ownership
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
        started=body.start_time if body and body.start_time and role.lower() == "admin" else datetime.now(),
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
        body: Optional[StopParkingSessionBody] = Body(None),
        db: Session = Depends(get_db)):
    # Try to validate token (optional for guest sessions)
    user_id = None
    role = None
    username = None
    
    token = request.headers.get("Authorization")
    if token:
        try:
            user_info: dict = JWTAuthenticator.validate_token(token)
            user_id = user_info.get("sub")
            role = user_info.get("role")
            username = DbUtils.get_username(db, user_id)
        except (TokenMissingError, TokenInvalidError, TokenExpiredError):
            # If token is invalid, treat as guest
            pass
    
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

    # Verify permissions
    # Admin can stop any session
    if role and role.lower() == "admin":
        pass  # Admin can stop any session
    # Guest sessions can be stopped by anyone
    elif active_session.username == "guest":
        pass  # Anyone can stop guest sessions
    # User sessions require ownership verification
    elif username and username == active_session.username:
        pass  # User can stop their own session
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only stop your own parking sessions or guest sessions"
        )

    # Stop the session
    active_session.stopped = datetime.now()
    active_session.duration_minutes = int((active_session.stopped - active_session.started).total_seconds() / 60)
    
    # Discount logic
    if not body or not body.discount_code:
        discount_percentage = 0
    else:
        discount_code: DiscountCode | None = db.query(DiscountCode).filter(DiscountCode.code == body.discount_code).first()
        if discount_code is None:
            discount_percentage = 0
        elif discount_code.type == "one-time" and discount_code.used == True:
            discount_percentage = 0
        else:
            discount_percentage = discount_code.percentage
            if discount_code.type == "one-time":
                discount_code.used = True
                db.refresh(discount_code)

    # Calculate cost based on duration and parking lot rates
    parking_lot = DbUtils.get_parking_lot_by_id(db, active_session.parking_lot_id)
    active_session.cost = ParkingSessionService.calculate_price(parking_lot, active_session, discount_percentage)
    active_session.payment_status = "pending"
    
    db.commit()
    db.refresh(active_session)

    return active_session
